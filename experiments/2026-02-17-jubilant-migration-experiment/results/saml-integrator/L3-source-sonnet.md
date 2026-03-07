# 🤖 Copilot CLI Session

> **Session ID:** `9c36f39c-3ff5-4bf8-affd-d36b8241750f`
> **Duration:** 5m 19s

<sub>⏱️ 4s</sub>

### 👤 User

Migrate this charm's integration tests from pytest-operator (python-libjuju) to jubilant and pytest-jubilant. Update all test files, conftest.py, and dependencies.

Before starting, install jubilant and pytest-jubilant from PyPI (pip install jubilant pytest-jubilant) and read the source code to understand the API. The key modules are the Juju class, wait helpers (all_active, all_blocked, any_error), and the pytest-jubilant fixtures (pack, get_resources, juju fixture, temp_model_factory).

---

<sub>⏱️ 12s</sub>

### 📦 task (Completed)

### 💬 Copilot

I'll explore the repository systematically. Let me start by viewing the directory structure and then reading all the requested files in parallel.

### ✅ `view`

**/tmp/saml-integrator-L3-sonnet**

/tmp/saml-integrator-L3-sonnet

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


### ✅ `bash`

**Find all Python test files**

$ find /tmp/saml-integrator-L3-sonnet/tests -type f -name "*.py" | sort

<details>
<summary>14 lines</summary>

```
/tmp/saml-integrator-L3-sonnet/tests/__init__.py
/tmp/saml-integrator-L3-sonnet/tests/conftest.py
/tmp/saml-integrator-L3-sonnet/tests/integration/__init__.py
/tmp/saml-integrator-L3-sonnet/tests/integration/any_charm.py
/tmp/saml-integrator-L3-sonnet/tests/integration/conftest.py
/tmp/saml-integrator-L3-sonnet/tests/integration/test_charm.py
/tmp/saml-integrator-L3-sonnet/tests/interface/conftest.py
/tmp/saml-integrator-L3-sonnet/tests/interface/test_saml.py
/tmp/saml-integrator-L3-sonnet/tests/unit/__init__.py
/tmp/saml-integrator-L3-sonnet/tests/unit/test_charm.py
/tmp/saml-integrator-L3-sonnet/tests/unit/test_charm_state.py
/tmp/saml-integrator-L3-sonnet/tests/unit/test_library_saml.py
/tmp/saml-integrator-L3-sonnet/tests/unit/test_saml.py
<exited with exit code 0>
```

</details>


### ✅ `bash`

**Find configuration and requirements files at root**

$ find /tmp/saml-integrator-L3-sonnet -maxdepth 1 -type f \( -name "*requirements*.txt" -o -name "*.toml" -o -name "*.yaml" -o -name "*.yml" \) | sort

<details>
<summary>8 lines</summary>

```
/tmp/saml-integrator-L3-sonnet/.licenserc.yaml
/tmp/saml-integrator-L3-sonnet/.woke.yaml
/tmp/saml-integrator-L3-sonnet/charmcraft.yaml
/tmp/saml-integrator-L3-sonnet/config.yaml
/tmp/saml-integrator-L3-sonnet/metadata.yaml
/tmp/saml-integrator-L3-sonnet/pyproject.toml
/tmp/saml-integrator-L3-sonnet/tox.toml
<exited with exit code 0>
```

</details>


### 💬 Copilot

Now let me get the complete directory structure of tests and read all the requested files:

### ✅ `bash`

**Get complete directory structure of tests**

$ tree /tmp/saml-integrator-L3-sonnet/tests -L 3

```
bash: tree: command not found
<exited with exit code 127>
```


### ✅ `view`

**/tmp/saml-integrator-L3-sonnet/tests/conftest.py**

/tmp/saml-integrator-L3-sonnet/tests/conftest.py

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


### ✅ `view`

**/tmp/saml-integrator-L3-sonnet/tests/integration/test_charm.py**

/tmp/saml-integrator-L3-sonnet/tests/integration/test_charm.py

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

**/tmp/saml-integrator-L3-sonnet/tests/integration/any_charm.py**

/tmp/saml-integrator-L3-sonnet/tests/integration/any_charm.py

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

**/tmp/saml-integrator-L3-sonnet/pyproject.toml**

/tmp/saml-integrator-L3-sonnet/pyproject.toml

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


### ✅ `view`

**/tmp/saml-integrator-L3-sonnet/tox.toml**

/tmp/saml-integrator-L3-sonnet/tox.toml

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


### ✅ `view`

**/tmp/saml-integrator-L3-sonnet/charmcraft.yaml**

/tmp/saml-integrator-L3-sonnet/charmcraft.yaml

<details>
<summary>20 lines</summary>

```
1. # Copyright 2025 Canonical Ltd.
2. # See LICENSE file for licensing details.
3. 
4. # Learn more about charmcraft.yaml configuration at:
5. # https://juju.is/docs/sdk/charmcraft-config
6. type: "charm"
7. bases:
8.   - build-on:
9.       - name: "ubuntu"
10.         channel: "22.04"
11.     run-on:
12.       - name: "ubuntu"
13.         channel: "22.04"
14. parts:
15.   charm:
16.     source: .
17.     plugin: uv
18.     build-snaps:
19.     - astral-uv
20.
```

</details>


### 💬 Copilot

Now let me get the directory structure and the remaining test files:

### ✅ `bash`

**Find all files in tests directory**

$ find /tmp/saml-integrator-L3-sonnet/tests -type f | sort

<details>
<summary>19 lines</summary>

```
/tmp/saml-integrator-L3-sonnet/tests/__init__.py
/tmp/saml-integrator-L3-sonnet/tests/conftest.py
/tmp/saml-integrator-L3-sonnet/tests/integration/__init__.py
/tmp/saml-integrator-L3-sonnet/tests/integration/any_charm.py
/tmp/saml-integrator-L3-sonnet/tests/integration/conftest.py
/tmp/saml-integrator-L3-sonnet/tests/integration/test_charm.py
/tmp/saml-integrator-L3-sonnet/tests/interface/conftest.py
/tmp/saml-integrator-L3-sonnet/tests/interface/test_saml.py
/tmp/saml-integrator-L3-sonnet/tests/unit/__init__.py
/tmp/saml-integrator-L3-sonnet/tests/unit/files/metadata_default_namespaces.xml
/tmp/saml-integrator-L3-sonnet/tests/unit/files/metadata_signed.xml
/tmp/saml-integrator-L3-sonnet/tests/unit/files/metadata_signed_tampered.xml
/tmp/saml-integrator-L3-sonnet/tests/unit/files/metadata_unsigned.xml
/tmp/saml-integrator-L3-sonnet/tests/unit/files/non_utf8_metadata_unsigned.xml
/tmp/saml-integrator-L3-sonnet/tests/unit/test_charm.py
/tmp/saml-integrator-L3-sonnet/tests/unit/test_charm_state.py
/tmp/saml-integrator-L3-sonnet/tests/unit/test_library_saml.py
/tmp/saml-integrator-L3-sonnet/tests/unit/test_saml.py
<exited with exit code 0>
```

</details>


### ✅ `view`

**/tmp/saml-integrator-L3-sonnet/tests/integration/conftest.py**

/tmp/saml-integrator-L3-sonnet/tests/integration/conftest.py

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

**/tmp/saml-integrator-L3-sonnet/tests/unit/test_charm.py**

/tmp/saml-integrator-L3-sonnet/tests/unit/test_charm.py

<details>
<summary>160 lines</summary>

```
1. # Copyright 2025 Canonical Ltd.
2. # See LICENSE file for licensing details.
3. 
4. """SAML Integrator Charm unit tests."""
5. 
6. # pylint: disable=protected-access
7. from pathlib import Path
8. from unittest.mock import patch
9. 
10. import ops
11. from ops.testing import Harness
12. 
13. from charm import SamlIntegratorOperatorCharm
14. 
15. 
16. def test_misconfigured_charm_reaches_blocked_status():
17.     """
18.     arrange: set up a charm.
19.     act: trigger a configuration change missing required configs.
20.     assert: the charm reaches BlockedStatus.
21.     """
22.     harness = Harness(SamlIntegratorOperatorCharm)
23.     harness.begin()
24.     assert harness.model.unit.status.name == ops.BlockedStatus().name
25. 
26. 
27. def test_update_status():
28.     """
29.     arrange: set up a charm.
30.     act: trigger an update status with the required configs.
31.     assert: the charm executes _update_relations.
32.     """
33.     metadata = Path("tests/unit/files/metadata_unsigned.xml").read_text(encoding="utf-8")
34.     harness = Harness(SamlIntegratorOperatorCharm)
35.     entity_id = "https://login.staging.ubuntu.com"
36.     harness.update_config(
37.         {
38.             "entity_id": entity_id,
39.             "metadata": metadata,
40.         }
41.     )
42.     harness.begin()
43.     with patch("charm.SamlIntegratorOperatorCharm._update_relations") as update_relations_mock:
44.         harness.charm.on.update_status.emit()
45.         update_relations_mock.assert_called_once()
46. 
47. 
48. def test_charm_reaches_active_status():
49.     """
50.     arrange: set up a charm.
51.     act: trigger a configuration change with the required configs.
52.     assert: the charm reaches ActiveStatus.
53.     """
54.     metadata = Path("tests/unit/files/metadata_unsigned.xml").read_text(encoding="utf-8")
55.     harness = Harness(SamlIntegratorOperatorCharm)
56.     entity_id = "https://login.staging.ubuntu.com"
57.     harness.update_config(
58.         {
59.             "entity_id": entity_id,
60.             "metadata": metadata,
61.         }
62.     )
63.     harness.begin()
64.     harness.charm.on.config_changed.emit()
65.     assert harness.model.unit.status == ops.ActiveStatus()
66. 
67. 
68. def test_relation_joined_when_leader():
69.     """
70.     arrange: set up a configured charm and set leadership for the unit.
71.     act: add a relation.
72.     assert: the relation get populated with the SAML data.
73.     """
74.     metadata = Path("tests/unit/files/metadata_unsigned.xml").read_text(encoding="utf-8")
75. 
76.     harness = Harness(SamlIntegratorOperatorCharm)
77.     harness.set_leader(True)
78.     entity_id = "https://login.staging.ubuntu.com"
79.     harness.update_config(
80.         {
81.             "entity_id": entity_id,
82.             "metadata": metadata,
83.         }
84.     )
85.     harness.begin()
86.     harness.charm.on.config_changed.emit()
87.     assert harness.model.unit.status == ops.ActiveStatus()
88.     harness.add_relation("saml", "indico")
89.     data = harness.model.get_relation("saml").data[harness.model.app]
90.     assert data["entity_id"] == harness.charm._charm_state.entity_id
91.     assert data["x509certs"] == ",".join(harness.charm._saml_integrator.certificates)
92.     endpoints = harness.charm._saml_integrator.endpoints
93.     sl_re = [
94.         ep
95.         for ep in endpoints
96.         if ep.name == "SingleLogoutService"
97.         and ep.binding == "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"
98.     ]
99.     if sl_re:
100.         assert data["single_logout_service_redirect_url"] == str(sl_re[0].url)
101.         assert data["single_logout_service_redirect_binding"] == sl_re[0].binding
102.         if sl_re[0].response_url:
103.             assert data["single_logout_service_redirect_response_url"] == str(
104.                 sl_re[0].response_url
105.             )
106.     sl_post = [
107.         ep
108.         for ep in endpoints
109.         if ep.name == "SingleLogoutService"
110.         and ep.binding == "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Post"
111.     ]
112.     if sl_post:
113.         assert data["single_logout_service_post_url"] == str(sl_post[0].url)
114.         assert data["single_logout_service_post_binding"] == sl_post[0].binding
115.         if sl_post[0].response_url:
116.             assert data["single_logout_service_post_response_url"] == str(sl_post[0].response_url)
117.     sso_re = [
118.         ep
119.         for ep in endpoints
120.         if ep.name == "SingleSignOnService"
121.         and ep.binding == "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"
122.     ]
123.     if sso_re:
124.         assert data["single_sign_on_service_redirect_url"] == str(sso_re[0].url)
125.         assert data["single_sign_on_service_redirect_binding"] == sso_re[0].binding
126.     sso_post = [
127.         ep
128.         for ep in endpoints
129.         if ep.name == "SingleSignOnService"
130.         and ep.binding == "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Post"
131.     ]
132.     if sso_post:
133.         assert data["single_sign_on_service_post_url"] == str(sso_post[0].url)
134.         assert data["single_sign_on_service_post_binding"] == sso_post[0].binding
135. 
136. 
137. def test_relation_joined_when_not_leader():
138.     """
139.     arrange: set up a charm and unset leadership for the unit.
140.     act: add a relation.
141.     assert: the relation get populated with the SAML data.
142.     """
143.     metadata = Path("tests/unit/files/metadata_unsigned.xml").read_text(encoding="utf-8")
144. 
145.     harness = Harness(SamlIntegratorOperatorCharm)
146.     harness.set_leader(False)
147.     entity_id = "https://login.staging.ubuntu.com"
148.     harness.update_config(
149.         {
150.             "entity_id": entity_id,
151.             "metadata": metadata,
152.         }
153.     )
154.     harness.begin()
155.     harness.charm.on.config_changed.emit()
156.     assert harness.model.unit.status == ops.ActiveStatus()
157.     harness.add_relation("saml", "indico")
158.     data = harness.model.get_relation("saml").data[harness.model.app]
159.     assert data == {}
160.
```

</details>


### ✅ `view`

**/tmp/saml-integrator-L3-sonnet/tests/unit/test_charm_state.py**

/tmp/saml-integrator-L3-sonnet/tests/unit/test_charm_state.py

<details>
<summary>94 lines</summary>

```
1. # Copyright 2025 Canonical Ltd.
2. # See LICENSE file for licensing details.
3. 
4. """CharmState unit tests."""
5. 
6. import urllib
7. from pathlib import Path
8. from unittest.mock import MagicMock, patch
9. 
10. import pytest
11. 
12. from charm_state import CharmConfigInvalidError, CharmState
13. 
14. 
15. @patch("urllib.request.urlopen")
16. def test_charm_state_from_charm_with_metadata_url(urlopen_mock):
17.     """
18.     arrange: set up a configured charm
19.     act: access the status properties
20.     assert: the configuration is accessible from the state properties.
21.     """
22.     metadata = Path("tests/unit/files/metadata_unsigned.xml").read_bytes()
23.     urlopen_result_mock = MagicMock()
24.     urlopen_result_mock.getcode.return_value = 200
25.     urlopen_result_mock.read.return_value = metadata
26.     urlopen_result_mock.__enter__.return_value = urlopen_result_mock
27.     urlopen_mock.return_value = urlopen_result_mock
28. 
29.     entity_id = "https://login.staging.ubuntu.com"
30.     metadata_url = "https://login.staging.ubuntu.com/saml/metadata"
31.     charm = MagicMock(
32.         config={
33.             "entity_id": entity_id,
34.             "metadata_url": metadata_url,
35.         }
36.     )
37.     state = CharmState.from_charm(charm)
38.     assert state.entity_id == entity_id
39.     assert str(state.metadata_url) == metadata_url
40.     assert state.metadata == metadata
41. 
42. 
43. def test_charm_state_from_charm_with_metadata():
44.     """
45.     arrange: set up a configured charm
46.     act: access the status properties
47.     assert: the configuration is accessible from the state properties.
48.     """
49.     metadata = Path("tests/unit/files/metadata_unsigned.xml").read_text(encoding="utf-8")
50. 
51.     entity_id = "https://login.staging.ubuntu.com"
52.     charm = MagicMock(
53.         config={
54.             "entity_id": entity_id,
55.             "metadata": metadata,
56.         }
57.     )
58.     state = CharmState.from_charm(charm)
59.     assert state.entity_id == entity_id
60.     assert state.metadata_url is None
61.     assert state.metadata == metadata
62. 
63. 
64. def test_charm_state_from_charm_with_invalid_config():
65.     """
66.     arrange: set up an unconfigured charm
67.     act: access the status properties
68.     assert: a CharmConfigInvalidError is raised.
69.     """
70.     entity_id = "https://login.staging.ubuntu.com"
71.     charm = MagicMock(config={"entity_id": entity_id})
72.     with pytest.raises(CharmConfigInvalidError):
73.         CharmState.from_charm(charm)
74. 
75. 
76. @patch.object(urllib.request, "urlopen", side_effect=urllib.error.URLError("Error"))
77. def test_charm_state_from_charm_with_metadata_url_invalid(_):
78.     """
79.     arrange: set up a configured charm with a metadata_url returning a 404
80.     act: access the status properties
81.     assert: a CharmConfigInvalidError is raised.
82.     """
83.     entity_id = "https://login.staging.ubuntu.com"
84.     metadata_url = "https://login.staging.ubuntu.com/saml/metadata"
85.     charm = MagicMock(
86.         config={
87.             "entity_id": entity_id,
88.             "metadata_url": metadata_url,
89.         }
90.     )
91.     state = CharmState.from_charm(charm)
92.     with pytest.raises(CharmConfigInvalidError):
93.         state.metadata  # noqa: B018
94.
```

</details>


### ✅ `view`

**/tmp/saml-integrator-L3-sonnet/tests/unit/test_library_saml.py**

/tmp/saml-integrator-L3-sonnet/tests/unit/test_library_saml.py

<details>
<summary>182 lines</summary>

```
1. # Copyright 2025 Canonical Ltd.
2. # See LICENSE file for licensing details.
3. 
4. """SAML library unit tests"""
5. 
6. import ops
7. import pytest
8. from charms.saml_integrator.v0 import saml
9. from ops.testing import Harness
10. 
11. REQUIRER_METADATA = """
12. name: saml-consumer
13. requires:
14.   saml:
15.     interface: saml
16. """
17. 
18. PROVIDER_METADATA = """
19. name: saml-producer
20. provides:
21.   saml:
22.     interface: saml
23. """
24. 
25. 
26. class SamlRequirerCharm(ops.CharmBase):
27.     """Class for requirer charm testing."""
28. 
29.     def __init__(self, *args):
30.         """Init method for the class.
31. 
32.         Args:
33.             args: Variable list of positional arguments passed to the parent constructor.
34.         """
35.         super().__init__(*args)
36.         self.saml = saml.SamlRequires(self)
37.         self.events = []
38.         self.framework.observe(self.saml.on.saml_data_available, self._record_event)
39. 
40.     def _record_event(self, event: ops.EventBase) -> None:
41.         """Rececord emitted event in the event list.
42. 
43.         Args:
44.             event: event.
45.         """
46.         self.events.append(event)
47. 
48. 
49. class SamlProviderCharm(ops.CharmBase):
50.     """Class for provider charm testing."""
51. 
52.     def __init__(self, *args):
53.         """Init method for the class.
54. 
55.         Args:
56.             args: Variable list of positional arguments passed to the parent constructor.
57.         """
58.         super().__init__(*args)
59.         self.saml = saml.SamlProvides(self)
60.         self.events = []
61.         self.framework.observe(self.on.saml_relation_changed, self._record_event)
62. 
63.     def _record_event(self, event: ops.EventBase) -> None:
64.         """Record emitted event in the event list.
65. 
66.         Args:
67.             event: event.
68.         """
69.         self.events.append(event)
70. 
71. 
72. def test_saml_relation_data_to_relation_data():
73.     """
74.     arrange: instantiate a SamlRelationData object.
75.     act: obtain the relation representation.
76.     assert: the relation representation is correct.
77.     """
78.     sso_endpoint = saml.SamlEndpoint(
79.         name="SingleSignOnService",
80.         url="https://login.staging.ubuntu.com/saml/",
81.         binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect",
82.     )
83.     slo_endpoint = saml.SamlEndpoint(
84.         name="SingleLogoutService",
85.         url="https://login.staging.ubuntu.com/+logout",
86.         binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect",
87.         response_url="https://login.staging.ubuntu.com/+logout2",
88.     )
89.     saml_data = saml.SamlRelationData(
90.         entity_id="https://login.staging.ubuntu.com",
91.         metadata_url="https://login.staging.ubuntu.com/saml/metadata",
92.         certificates=["cert1", "cert2"],
93.         endpoints=[sso_endpoint, slo_endpoint],
94.     )
95.     relation_data = saml_data.to_relation_data()
96.     expected_relation_data = {
97.         "entity_id": "https://login.staging.ubuntu.com",
98.         "metadata_url": "https://login.staging.ubuntu.com/saml/metadata",
99.         "x509certs": "cert1,cert2",
100.         "single_sign_on_service_redirect_url": "https://login.staging.ubuntu.com/saml/",
101.         "single_sign_on_service_redirect_binding": (
102.             "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"
103.         ),
104.         "single_logout_service_redirect_url": "https://login.staging.ubuntu.com/+logout",
105.         "single_logout_service_redirect_binding": (
106.             "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"
107.         ),
108.         "single_logout_service_redirect_response_url": "https://login.staging.ubuntu.com/+logout2",
109.     }
110.     assert relation_data == expected_relation_data
111. 
112. 
113. def test_requirer_charm_does_not_emit_event_id_no_data():
114.     """
115.     arrange: set up a charm with no relation data to be populated.
116.     act: trigger a relation changed event.
117.     assert: no events are emitted.
118.     """
119.     harness = Harness(SamlRequirerCharm, meta=REQUIRER_METADATA)
120.     harness.begin()
121.     harness.set_leader(True)
122.     relation_id = harness.add_relation("saml", "saml-provider")
123.     harness.add_relation_unit(relation_id, "saml-provider/0")
124.     relation = harness.charm.framework.model.get_relation("saml", 0)
125.     harness.charm.on.saml_relation_changed.emit(relation)
126.     assert len(harness.charm.events) == 0
127. 
128. 
129. @pytest.mark.parametrize("is_leader", [True, False])
130. def test_requirer_charm_emits_event(is_leader):
131.     """
132.     arrange: set up a charm.
133.     act: trigger a relation changed event.
134.     assert: a event containing the relation data is emitted.
135.     """
136.     relation_data = {
137.         "entity_id": "https://login.staging.ubuntu.com",
138.         "metadata_url": "https://login.staging.ubuntu.com/saml/metadata",
139.         "x509certs": "cert1,cert2",
140.         "single_sign_on_service_redirect_url": "https://login.staging.ubuntu.com/saml/",
141.         "single_sign_on_service_redirect_binding": (
142.             "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"
143.         ),
144.         "single_logout_service_redirect_url": "https://login.staging.ubuntu.com/+logout",
145.         "single_logout_service_redirect_binding": (
146.             "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"
147.         ),
148.     }
149. 
150.     harness = Harness(SamlRequirerCharm, meta=REQUIRER_METADATA)
151.     harness.begin()
152.     harness.set_leader(is_leader)
153.     relation_id = harness.add_relation("saml", "saml-provider")
154.     harness.add_relation_unit(relation_id, "saml-provider/0")
155.     harness.update_relation_data(
156.         relation_id,
157.         "saml-provider",
158.         relation_data,
159.     )
160. 
161.     slo_endpoint = saml.SamlEndpoint(
162.         name="SingleLogoutService",
163.         url="https://login.staging.ubuntu.com/+logout",
164.         binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect",
165.     )
166.     sso_endpoint = saml.SamlEndpoint(
167.         name="SingleSignOnService",
168.         url="https://login.staging.ubuntu.com/saml/",
169.         binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect",
170.     )
171.     assert len(harness.charm.events) == 1
172.     assert harness.charm.events[0].entity_id == relation_data["entity_id"]
173.     assert harness.charm.events[0].metadata_url == relation_data["metadata_url"]
174.     assert harness.charm.events[0].certificates == tuple(relation_data["x509certs"].split(","))
175.     assert harness.charm.events[0].endpoints == (slo_endpoint, sso_endpoint)
176. 
177.     retrieved_relation_data = harness.charm.saml.get_relation_data()
178.     assert retrieved_relation_data.entity_id == relation_data["entity_id"]
179.     assert str(retrieved_relation_data.metadata_url) == relation_data["metadata_url"]
180.     assert retrieved_relation_data.certificates == tuple(relation_data["x509certs"].split(","))
181.     assert retrieved_relation_data.endpoints == (slo_endpoint, sso_endpoint)
182.
```

</details>


### ✅ `view`

**/tmp/saml-integrator-L3-sonnet/tests/unit/test_saml.py**

/tmp/saml-integrator-L3-sonnet/tests/unit/test_saml.py

<details>
<summary>253 lines</summary>

```
1. # Copyright 2025 Canonical Ltd.
2. # See LICENSE file for licensing details.
3. 
4. """SAML Integrator unit tests."""
5. 
6. # pylint: disable=pointless-statement
7. from pathlib import Path
8. from unittest.mock import MagicMock
9. 
10. import pytest  # type: ignore[reportMissingImports]
11. 
12. from charm_state import CharmConfigInvalidError
13. from saml import SamlIntegrator
14. 
15. 
16. def get_urlopen_result_mock(code: int, result: bytes) -> MagicMock:
17.     """Get a MagicMock for the urlopen response.
18. 
19.     Args:
20.         code: response code.
21.         result: response content.
22. 
23.     Returns:
24.         Mock for the response.
25.     """
26.     urlopen_result_mock = MagicMock()
27.     urlopen_result_mock.getcode.return_value = code
28.     urlopen_result_mock.read.return_value = result
29.     return urlopen_result_mock
30. 
31. 
32. def test_saml_with_invalid_metadata():
33.     """
34.     arrange: mock the metadata contents so that they are invalid.
35.     act: access the metadata properties.
36.     assert: a CharmConfigInvalidError exception is raised when attempting to access the
37.         properties read from the metadata.
38.     """
39.     charm_state = MagicMock(
40.         entity_id="https://login.staging.ubuntu.com",
41.         metadata="invalid",
42.     )
43.     saml_integrator = SamlIntegrator(charm_state=charm_state)
44.     with pytest.raises(CharmConfigInvalidError):
45.         saml_integrator.certificates  # noqa: B018
46.     with pytest.raises(CharmConfigInvalidError):
47.         saml_integrator.endpoints  # noqa: B018
48. 
49. 
50. def test_saml_with_valid_signed_metadata():
51.     """
52.     arrange: mock the metadata contents so that they valid.
53.     act: access the metadata properties.
54.     assert: the properties are populated as defined in the metadata.
55.     """
56.     metadata = Path("tests/unit/files/metadata_signed.xml").read_text(encoding="utf-8")
57.     entity_id = "https://login.staging.ubuntu.com"
58.     charm_state = MagicMock(
59.         entity_id=entity_id,
60.         fingerprint=(
61.             "1C:73:51:f2:23:55:f8:3d:25:7e:65:56:dd:f1:a9:17:fe:d4:af"
62.             ":dc:70:d2:a8:11:b3:2f:d2:ea:c4:6d:91:e7"
63.         ),
64.         metadata=metadata,
65.     )
66.     saml_integrator = SamlIntegrator(charm_state=charm_state)
67.     signing_cert = (
68.         "MIIFazCCA1OgAwIBAgIUWPY90f+xbkCWHVJXtwm2+9mZiIcwDQYJKoZIhvcNAQEL"
69.         "BQAwRTELMAkGA1UEBhMCQVUxEzARBgNVBAgMClNvbWUtU3RhdGUxITAfBgNVBAoM"
70.         "GEludGVybmV0IFdpZGdpdHMgUHR5IEx0ZDAeFw0yMzA4MDkxNDI1NDVaFw0yNDA4"
71.         "MDgxNDI1NDVaMEUxCzAJBgNVBAYTAkFVMRMwEQYDVQQIDApTb21lLVN0YXRlMSEw"
72.         "HwYDVQQKDBhJbnRlcm5ldCBXaWRnaXRzIFB0eSBMdGQwggIiMA0GCSqGSIb3DQEB"
73.         "AQUAA4ICDwAwggIKAoICAQDDaJTOlLBVePVvenKbtq6B6vHNnvxLEA1NMmhZ9yvH"
74.         "N/h0/FTph0iBf+VWyCY9M2CeMKggTIAhrVAXEALG7ImGl/lFKdfC/8eEXFtEMe4V"
75.         "WAOC9qnb3dAViMAq5xMd6e5gwrcPSaDtOE8Up2OUfsHuf7GfocWtWh3beqW1FLE7"
76.         "JBPcVKNZ6T8ap5fUHVCprfCk0yrPQ3ocJOWE0JHatqfahU34fWFTHWD1qfplL/Xf"
77.         "mr9ayk+eey2FwsoloEtdpOMgitkeYpKNTh4btkQ4TEyKlG07+87l1b7niBeuEj1T"
78.         "yqq87Kz6eHIarAlLmPHhBuM1/BQunyaVEfM0AXv2u/A8Uvz9njRoaWlZKHdlsEMq"
79.         "hBzVCn+T7WnkxE3dGQDwgXbeDIOx1x/utR40UZeYUd6HUer4WtORNg1pBp2GeKp8"
80.         "3gej/SjAhzqsB3ZdhPA47bDw21sp4ytTPCEvc2IsdErq7zIe5pUxkQKOe0R00qyd"
81.         "69THdTqjvpo6oVQdEXauCisooWwxRAksUazqtaZUAwNB/pLqmE+kSFnsxEpn6BDH"
82.         "6GVUFfMpzXUTsqBqK3j5QvHexVzLp3CyYicq1VjKghu5ICsIp+CGhLEEIBLJksJ8"
83.         "IH6j9mHJ4W4qoLefBHNZDlxg2ZGDwEqs66gJVao5zQyEDjScUjVTrvfIZM3WY08L"
84.         "5QIDAQABo1MwUTAdBgNVHQ4EFgQUW/f6Ya3dlETc60m8JFhZsZo4XLYwHwYDVR0j"
85.         "BBgwFoAUW/f6Ya3dlETc60m8JFhZsZo4XLYwDwYDVR0TAQH/BAUwAwEB/zANBgkq"
86.         "hkiG9w0BAQsFAAOCAgEAocRH2K+CWQFxMpJQvayEq7uU6dkdH2xE12Vg4wUm4/h+"
87.         "hmngK6TlXqBHISpitlQlbqx1CsO3E9FeZGVA7erySh+lyoO9Hndhm7Fsj2U1P0MW"
88.         "tkz81NOT975f0zTQ1KsdzTHkocV5dx869jD3ssUCkpxdTRF6EJmRLQoRfGEmxnuG"
89.         "bynFcOUMZ7fxd79IsDy4tWcUjoV4jeWDiyi/LuuhVDr+AhI62Gl2MTdFLHTTRzak"
90.         "IzIWmFVEdrfuDgg/RR4YYBoXrGSA0RLrpKpexb4kZd8/hvTtCcPghUuK6Q1iMT4q"
91.         "hV2dKVFut/6IKLnD35Ol/fLLoy2CtnioUqx6v3MefxAptKpQM3ebgpv2UzIsIXdU"
92.         "RQ9pfDlsyo1wdJ1wZNh6A5eerROsX3MKjLqUAiJh4v+ydeR3IyN3YckdadU6Wq+m"
93.         "wnrVPI0nxrgLW/5srJ4cR4idEgmV8cRNJSqoaFPLyBoLk/cjq/yQAXcz23eWD6aD"
94.         "qsOrRlyuKXQ6KEi/z6aIsiKNH5PPg9Fr3aH+cSnbTU7UNmJH/eOaYzaYMI1NiweU"
95.         "Z5C+jLxosbIwfv4IqNCX8EZfvAMTAFpsDrwi0uO5W0pJMMcOKD0eT4smNbb+9eM2"
96.         "6EPjd7nh5uMPiktm3JXXXPjfTacdieE8WsO+ddsV93dR5wT54mFG1myHAOBnAf4="
97.     )
98.     assert saml_integrator.signing_certificate == signing_cert
99.     assert saml_integrator.certificates == [signing_cert, "cert1_content"]
100.     endpoints = saml_integrator.endpoints
101.     assert len(endpoints) == 2
102.     assert endpoints[0].name == "SingleLogoutService"
103.     assert endpoints[0].binding == "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"
104.     assert str(endpoints[0].url) == "https://login.staging.ubuntu.com/+logout"
105.     assert str(endpoints[0].response_url) == "https://login.staging.ubuntu.com/example/"
106.     assert endpoints[1].name == "SingleSignOnService"
107.     assert endpoints[1].binding == "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"
108.     assert str(endpoints[1].url) == "https://login.staging.ubuntu.com/saml/"
109.     assert endpoints[1].response_url is None
110. 
111. 
112. def test_saml_with_valid_tampered_signed_metadata():
113.     """
114.     arrange: mock the metadata contents so that they invalid.
115.     act: access the metadata properties.
116.     assert: an exception is raised.
117.     """
118.     metadata = Path("tests/unit/files/metadata_signed_tampered.xml").read_text(encoding="utf-8")
119. 
120.     entity_id = "https://login.staging.ubuntu.com"
121.     charm_state = MagicMock(
122.         entity_id=entity_id,
123.         fingerprint=(
124.             "1c:73:51:f2:23:55:f8:3d:25:7e:65:56:dd:f1:a9:17:fe:d4:af"
125.             ":dc:70:d2:a8:11:b3:2f:d2:ea:c4:6d:91:e7"
126.         ),
127.         metadata=metadata,
128.     )
129.     saml_integrator = SamlIntegrator(charm_state=charm_state)
130.     with pytest.raises(CharmConfigInvalidError):
131.         saml_integrator.tree  # noqa: B018
132. 
133. 
134. def test_saml_with_valid_signed_metadata_not_matching_fingerprint():
135.     """
136.     arrange: mock the metadata contents so that they invalid and set an invalid fingerprint.
137.     act: access the metadata properties.
138.     assert: the properties are po
139.     pulated as defined in the metadata.
140.     """
141.     metadata = Path("tests/unit/files/metadata_signed.xml").read_text(encoding="utf-8")
142. 
143.     entity_id = "https://login.staging.ubuntu.com"
144.     charm_state = MagicMock(
145.         entity_id=entity_id,
146.         fingerprint="invalid_fingerprint",
147.         metadata=metadata,
148.     )
149.     saml_integrator = SamlIntegrator(charm_state=charm_state)
150.     with pytest.raises(CharmConfigInvalidError):
151.         saml_integrator.tree  # noqa: B018
152. 
153. 
154. def test_saml_with_valid_unsigned_metadata():
155.     """
156.     arrange: mock the metadata contents so that they invalid.
157.     act: access the metadata properties.
158.     assert: the properties are populated as defined in the metadata.
159.     """
160.     metadata = Path("tests/unit/files/metadata_unsigned.xml").read_text(encoding="utf-8")
161. 
162.     entity_id = "https://login.staging.ubuntu.com"
163.     charm_state = MagicMock(
164.         entity_id=entity_id,
165.         fingerprint="",
166.         metadata=metadata,
167.     )
168.     saml_integrator = SamlIntegrator(charm_state=charm_state)
169.     assert saml_integrator.certificates == ["cert1_content"]
170.     endpoints = saml_integrator.endpoints
171.     assert len(endpoints) == 2
172.     assert endpoints[0].name == "SingleLogoutService"
173.     assert endpoints[0].binding == "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Post"
174.     assert str(endpoints[0].url) == "https://login.staging.ubuntu.com/+logout"
175.     assert str(endpoints[0].response_url) == "https://login.staging.ubuntu.com/example/"
176.     assert endpoints[1].name == "SingleSignOnService"
177.     assert endpoints[1].binding == "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Post"
178.     assert str(endpoints[1].url) == "https://login.staging.ubuntu.com/saml/"
179.     assert endpoints[1].response_url is None
180. 
181. 
182. def test_saml_with_valid_unsigned_metadata_non_utf8():
183.     """
184.     arrange: mock the metadata contents so that they invalid.
185.     act: access the metadata properties.
186.     assert: the properties are populated as defined in the metadata.
187.     """
188.     metadata = Path("tests/unit/files/non_utf8_metadata_unsigned.xml").read_text(encoding="utf-8")
189. 
190.     entity_id = "https://accounts.google.com/o/saml2?idpid=C03oypjtr"
191.     charm_state = MagicMock(
192.         entity_id=entity_id,
193.         fingerprint="",
194.         metadata=metadata,
195.     )
196.     saml_integrator = SamlIntegrator(charm_state=charm_state)
197.     certificate = (
198.         "MIIDdDCCAlygAwIBAgIGAYdLBPyWMA0GCSqGSIb3DQEBCwUAMHsxFDASBgNVBAoTC0dvb2dsZSBJ"
199.         "bmMuMRYwFAYDVQQHEw1Nb3VudGFpbiBWaWV3MQ8wDQYDVQQDEwZHb29nbGUxGDAWBgNVBAsTD0dv"
200.         "b2dsZSBGb3IgV29yazELMAkGA1UEBhMCVVMxEzARBgNVBAgTCkNhbGlmb3JuaWEwHhcNMjMwNDA0"
201.         "MDY0NzA5WhcNMjgwNDAyMDY0NzA5WjB7MRQwEgYDVQQKEwtHb29nbGUgSW5jLjEWMBQGA1UEBxMN"
202.         "TW91bnRhaW4gVmlldzEPMA0GA1UEAxMGR29vZ2xlMRgwFgYDVQQLEw9Hb29nbGUgRm9yIFdvcmsx"
203.         "CzAJBgNVBAYTAlVTMRMwEQYDVQQIEwpDYWxpZm9ybmlhMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8A"
204.         "MIIBCgKCAQEApl6vmP6rt86m6I3dojHeT7bodIlDU3UnE2y1Hpqc6xlq0Kxv3ZcVrZX1dX/UC4NY"
205.         "CTlumUrEoVzERKRU1aGqBuk9QqvMpkf25jiWEetDly7IVJAq8behjq+801KzU3Kn1s830+czzQuH"
206.         "oVA9KlWwL6FSbCjmNKlAQ8qqcyQ3C1HlVF0x489/kfgZFw6sSX1sTZHgG0vw2E8xGdjRdtVVEgQG"
207.         "uWzLvcpWAPAK6IqzY5e9xETXN8au04SqnVWfUi19f4w8kCh3T8LIakmvm09lxYajndKCQvYrPnq+"
208.         "YpVwHiufnHxkVMb4claFFgX+gNDyEWbGDIi8yOQnKeUHnpCKGQIDAQABMA0GCSqGSIb3DQEBCwUA"
209.         "A4IBAQBZJnZzQilSlH3N2UCoJ1G9Me47NdZIs1HyQZNMtzbXwS+Z5Ek05loKFj75D3R094dtn4RC"
210.         "1pM5BQjBProMG5UbtQKVKbM8SjQgj23UWuuc6YXDok9lqtWuGwpOSNYUU75K/7vdVCFdG2urtms2"
211.         "ueZ2D8bA3nDhsgHAhc6YJM3TqatcFHRGTNlwkKl71GYMWYM3JKNEZAfU7zhjicXYhW7t3+Hj6TJC"
212.         "ChYw2B+hfOv0W324BZyyZW8X3m5CWVlCWxBKfIo3NJ+gg/dGbkuPIbzdV197LSuxkArm/7rMbxwe"
213.         "KNL8a7w5HN3iCi27GlKpmj4n5uMnDpRDk81hrvyew2Rp"
214.     )
215.     assert saml_integrator.certificates == [certificate]
216.     endpoints = saml_integrator.endpoints
217.     assert len(endpoints) == 2
218.     assert endpoints[0].name == "SingleSignOnService"
219.     assert endpoints[0].binding == "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"
220.     assert str(endpoints[0].url) == "https://accounts.google.com/o/saml2/idp?idpid=C03oypjtr"
221.     assert endpoints[0].response_url is None
222.     assert endpoints[1].name == "SingleSignOnService"
223.     assert endpoints[1].binding == "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"
224.     assert str(endpoints[1].url) == "https://accounts.google.com/o/saml2/idp?idpid=C03oypjtr"
225.     assert endpoints[1].response_url is None
226. 
227. 
228. def test_saml_with_metadata_with_default_namespaces():
229.     """
230.     arrange: mock the metadata with XML default namespaces.
231.     act: access the metadata properties.
232.     assert: the properties are populated as defined in the metadata.
233.     """
234.     metadata = Path("tests/unit/files/metadata_default_namespaces.xml").read_text(encoding="utf-8")
235. 
236.     entity_id = "https://saml.canonical.test/metadata"
237.     charm_state = MagicMock(
238.         entity_id=entity_id,
239.         fingerprint="",
240.         metadata=metadata,
241.     )
242.     saml_integrator = SamlIntegrator(charm_state=charm_state)
243.     endpoints = saml_integrator.endpoints
244.     assert len(endpoints) == 2
245.     assert endpoints[0].name == "SingleSignOnService"
246.     assert endpoints[0].binding == "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"
247.     assert str(endpoints[0].url) == "https://saml.canonical.test/sso"
248.     assert endpoints[0].response_url is None
249.     assert endpoints[1].name == "SingleSignOnService"
250.     assert endpoints[1].binding == "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"
251.     assert str(endpoints[1].url) == "https://saml.canonical.test/sso"
252.     assert endpoints[1].response_url is None
253.
```

</details>


### 💬 Copilot

Now let me get the interface test files and any remaining configuration files:

### ✅ `view`

**/tmp/saml-integrator-L3-sonnet/tests/interface/conftest.py**

/tmp/saml-integrator-L3-sonnet/tests/interface/conftest.py

<details>
<summary>83 lines</summary>

```
1. # Copyright 2025 Canonical Ltd.
2. # See LICENSE file for licensing details.
3. 
4. """Fixtures for charm-relation-interfaces tests."""
5. 
6. from typing import Dict
7. from unittest import mock
8. 
9. import pytest
10. from charms.saml_integrator.v0.saml import SamlEndpoint, SamlRelationData
11. from interface_tester.plugin import InterfaceTester
12. from scenario import State
13. 
14. import saml
15. from charm import SamlIntegratorOperatorCharm
16. 
17. 
18. # Interface tests are centrally hosted at https://github.com/canonical/charm-relation-interfaces.
19. # this fixture is used by the test runner of charm-relation-interfaces to test saml's compliance
20. # with the interface specifications.
21. # DO NOT MOVE OR RENAME THIS FIXTURE! If you need to, you'll need to open a PR on
22. # https://github.com/canonical/charm-relation-interfaces and change saml's test configuration
23. # to include the new identifier/location.
24. @pytest.fixture
25. def interface_tester(interface_tester: InterfaceTester, monkeypatch: pytest.MonkeyPatch):
26.     sso_redirect_endpoint = SamlEndpoint(
27.         name="SingleSignOnService",
28.         url="https://login.staging.ubuntu.com/saml/",
29.         binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect",
30.     )
31.     sso_post_endpoint = SamlEndpoint(
32.         name="SingleSignOnService",
33.         url="https://login.staging.ubuntu.com/saml/",
34.         binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST",
35.     )
36.     slo_redirect_endpoint = SamlEndpoint(
37.         name="SingleLogoutService",
38.         url="https://login.staging.ubuntu.com/saml/logout",
39.         binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect",
40.         response_url="https://login.staging.ubuntu.com/saml/logout/response",
41.     )
42.     slo_post_endpoint = SamlEndpoint(
43.         name="SingleLogoutService",
44.         url="https://login.staging.ubuntu.com/saml/logout",
45.         binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST",
46.         response_url="https://login.staging.ubuntu.com/saml/logout/response",
47.     )
48. 
49.     # Store the original method
50.     original_to_relation_data = SamlRelationData.to_relation_data
51. 
52.     # Create a wrapper that adds the missing single_logout_service_url field
53.     # This is a workaround for a mismatch between the library naming convention
54.     # and the interface schema expectations
55.     def patched_to_relation_data(self) -> Dict[str, str]:
56.         result = original_to_relation_data(self)
57.         # Add single_logout_service_url if we have logout endpoints
58.         # The schema expects this field but the library generates method-specific URLs
59.         if "single_logout_service_redirect_url" in result:
60.             result["single_logout_service_url"] = result["single_logout_service_redirect_url"]
61.         return result
62. 
63.     with (
64.         mock.patch.object(saml.SamlIntegrator, "certificates", ["cert_content"]),
65.         mock.patch.object(
66.             saml.SamlIntegrator,
67.             "endpoints",
68.             [sso_redirect_endpoint, sso_post_endpoint, slo_redirect_endpoint, slo_post_endpoint],
69.         ),
70.         mock.patch.object(SamlRelationData, "to_relation_data", patched_to_relation_data),
71.     ):
72.         interface_tester.configure(
73.             charm_type=SamlIntegratorOperatorCharm,
74.             state_template=State(
75.                 leader=True,
76.                 config={
77.                     "entity_id": "https://login.staging.ubuntu.com",
78.                     "metadata_url": "https://login.staging.ubuntu.com/saml/metadata",
79.                 },
80.             ),
81.         )
82.         yield interface_tester
83.
```

</details>


### ✅ `view`

**/tmp/saml-integrator-L3-sonnet/tests/interface/test_saml.py**

/tmp/saml-integrator-L3-sonnet/tests/interface/test_saml.py

<details>
<summary>18 lines</summary>

```
1. # Copyright 2025 Canonical Ltd.
2. # See LICENSE file for licensing details.
3. from interface_tester import InterfaceTester
4. 
5. 
6. # Interface tests are centrally hosted at https://github.com/canonical/charm-relation-interfaces.
7. # this fixture is used by the test runner of charm-relation-interfaces to test saml's compliance
8. # with the interface specifications.
9. # DO NOT MOVE OR RENAME THIS FIXTURE! If you need to, you'll need to open a PR on
10. # https://github.com/canonical/charm-relation-interfaces and change saml's test configuration
11. # to include the new identifier/location.
12. def test_saml_v0_interface(interface_tester: InterfaceTester):
13.     interface_tester.configure(
14.         interface_name="saml",
15.         interface_version=0,
16.     )
17.     interface_tester.run()
18.
```

</details>


### ✅ `view`

**/tmp/saml-integrator-L3-sonnet/tests/__init__.py**

/tmp/saml-integrator-L3-sonnet/tests/__init__.py

```
1. # Copyright 2025 Canonical Ltd.
2. # See LICENSE file for licensing details.
3. 
4. """Tests module."""
5. 
```


### ✅ `view`

**/tmp/saml-integrator-L3-sonnet/tests/unit/__init__.py**

/tmp/saml-integrator-L3-sonnet/tests/unit/__init__.py

```
1. # Copyright 2025 Canonical Ltd.
2. # See LICENSE file for licensing details.
3. 
```


### ✅ `view`

**/tmp/saml-integrator-L3-sonnet/tests/integration/__init__.py**

/tmp/saml-integrator-L3-sonnet/tests/integration/__init__.py

```
1. # Copyright 2025 Canonical Ltd.
2. # See LICENSE file for licensing details.
3. 
```


### ✅ `bash`

**Check for any requirements files**

$ find /tmp/saml-integrator-L3-sonnet -maxdepth 1 -name "*requirements*.txt" -o -name "*.lock"

```
/tmp/saml-integrator-L3-sonnet/uv.lock
<exited with exit code 0>
```


### 💬 Copilot

Perfect! Now let me create a comprehensive summary with proper directory structure visualization:

### ✅ `bash`

**Show complete tests directory structure**

$ find /tmp/saml-integrator-L3-sonnet/tests -type f -o -type d | sort | sed 's|/tmp/saml-integrator-L3-sonnet/||' | head -30

<details>
<summary>24 lines</summary>

```
tests
tests/__init__.py
tests/conftest.py
tests/integration
tests/integration/__init__.py
tests/integration/any_charm.py
tests/integration/conftest.py
tests/integration/test_charm.py
tests/interface
tests/interface/conftest.py
tests/interface/test_saml.py
tests/unit
tests/unit/__init__.py
tests/unit/files
tests/unit/files/metadata_default_namespaces.xml
tests/unit/files/metadata_signed.xml
tests/unit/files/metadata_signed_tampered.xml
tests/unit/files/metadata_unsigned.xml
tests/unit/files/non_utf8_metadata_unsigned.xml
tests/unit/test_charm.py
tests/unit/test_charm_state.py
tests/unit/test_library_saml.py
tests/unit/test_saml.py
<exited with exit code 0>
```

</details>


### 💬 Copilot

Now I'll compile the comprehensive overview:

## Comprehensive Repository Overview: SAML Integrator

### 1. Complete Directory Structure of `tests/` Directory

```
tests/
├── __init__.py                          # Tests module init
├── conftest.py                          # Root test configuration
├── integration/
│   ├── __init__.py
│   ├── any_charm.py                     # Test charm implementation for integration tests
│   ├── conftest.py                      # Integration test fixtures
│   └── test_charm.py                    # Integration test cases
├── interface/
│   ├── conftest.py                      # Interface test fixtures
│   └── test_saml.py                     # Interface compliance tests
└── unit/
    ├── __init__.py
    ├── files/
    │   ├── metadata_default_namespaces.xml
    │   ├── metadata_signed.xml
    │   ├── metadata_signed_tampered.xml
    │   ├── metadata_unsigned.xml
    │   └── non_utf8_metadata_unsigned.xml
    ├── test_charm.py                    # Unit tests for charm
    ├── test_charm_state.py              # Unit tests for charm state
    ├── test_library_saml.py             # Unit tests for SAML library
    └── test_saml.py                     # Unit tests for SAML integrator
```

---

### 2. Full Content of `tests/conftest.py`

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

---

### 3. Full Content of All Test Files in `tests/integration/`

#### **tests/integration/test_charm.py**

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

#### **tests/integration/any_charm.py**

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

#### **tests/integration/conftest.py**

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

---

### 4. Full Content of `pyproject.toml`

```toml
# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

[project]
name = "saml-integrator-operator"
version = "0.0.0"
description = "SAML Integrator to abstract SAML IdP details."
readme = "README.md"
requires-python = "\>=3.10"
classifiers = [
  "Programming Language :: Python :: 3 :: Only",
  "Programming Language :: Python :: 3.10",
  "Programming Language :: Python :: 3.11",
  "Programming Language :: Python :: 3.12",
  "Programming Language :: Python :: 3.13",
  "Programming Language :: Python :: 3.14",
]
dependencies = [
  "lxml==6.0.2",
  "ops==3.6.0",
  "pydantic==2.12.5",
  "signxml==4.3.0",
]

[dependency-groups]
fmt = [
  "ruff",
]
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
unit = [
  "coverage[toml]",
  "pytest",
]
coverage-report = [
  "coverage[toml]",
  "pytest",
]
static = [
  "bandit[toml]",
]
interface = [
  "ops-scenario",
  "pytest",
  "pytest-interface-tester",
]
integration = [
  "allure-pytest\>=2.8.18",
  "allure-pytest-collection-report @ git+https://github.com/canonical/data-platform-workflows@v24.0.0#subdirectory=python/pytest_plugins/allure_pytest_collection_report",
  "juju",
  "pytest",
  "pytest-asyncio",
  "pytest-operator",
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
markers = [ "requires_secrets: mark tests that require external secrets" ]
pythonpath = [
  "lib",
  "src"
]

[tool.coverage.run]
branch = true

[tool.coverage.report]
fail_under = 99
show_missing = true

[tool.mypy]
ignore_missing_imports = true
explicit_package_bases = true
namespace_packages = true

[tool.bandit]
exclude_dirs = [ "/venv/" ]

[tool.bandit.assert_used]
skips = [ "*/*test.py", "*/test_*.py", "*tests/*.py" ]
```

---

### 5. Full Content of `tox.toml`

```toml
# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

skipsdist = true
skip_missing_interpreters = true
envlist = [ "lint", "unit", "static", "interface", "coverage-report" ]
requires = [ "tox\>=4.21" ]
no_package = true

[env_run_base]
passenv = [ "PYTHONPATH", "CHARM_BUILD_DIR", "MODEL_SETTINGS" ]
runner = "uv-venv-lock-runner"

[env_run_base.setenv]
PYTHONPATH = "{toxinidir}:{toxinidir}/lib:{[vars]src_path}"
PYTHONBREAKPOINT = "ipdb.set_trace"
PY_COLORS = "1"

[env.fmt]
description = "Apply coding style standards to code"
commands = [
  [
    "ruff",
    "check",
    "--fix",
    "--select",
    "I",
    { replace = "ref", of = [
      "vars",
      "all_path",
    ], extend = true },
  ],
  [
    "ruff",
    "format",
    { replace = "ref", of = [
      "vars",
      "all_path",
    ], extend = true },
  ],
]
dependency_groups = [ "fmt" ]

[env.lint]
description = "Check code against coding style standards"
commands = [
  [
    "codespell",
    "{toxinidir}",
  ],
  [
    "ruff",
    "format",
    "--check",
    "--diff",
    { replace = "ref", of = [
      "vars",
      "all_path",
    ], extend = true },
  ],
  [
    "ruff",
    "check",
    { replace = "ref", of = [
      "vars",
      "all_path",
    ], extend = true },
  ],
  [
    "mypy",
    { replace = "ref", of = [
      "vars",
      "all_path",
    ], extend = true },
  ],
]
dependency_groups = [ "lint" ]

[env.unit]
description = "Run unit tests"
commands = [
  [
    "coverage",
    "run",
    "--source={[vars]src_path},{[vars]lib_path}",
    "-m",
    "pytest",
    "--ignore={[vars]tst_path}integration",
    "--ignore={[vars]tst_path}interface",
    "-v",
    "--tb",
    "native",
    "-s",
    { replace = "posargs", extend = "true" },
  ],
  [
    "coverage",
    "report",
  ],
]
dependency_groups = [ "unit" ]

[env.coverage-report]
description = "Create test coverage report"
commands = [ [ "coverage", "report" ] ]
dependency_groups = [ "coverage-report" ]

[env.static]
description = "Run static analysis tests"
commands = [ [ "bandit", "-c", "{toxinidir}/pyproject.toml", "-r", "{[vars]src_path}", "{[vars]tst_path}" ] ]
dependency_groups = [ "static" ]

[env.interface]
description = "Run unit tests"
commands = [
  [
    "pytest",
    "-v",
    "--tb",
    "native",
    "{[vars]tst_path}/interface",
    "--log-cli-level=INFO",
    "-s",
    { replace = "posargs", extend = "true" },
  ],
]
dependency_groups = [ "interface" ]

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

[env.lint-fix]
description = "Apply coding style standards to code"
commands = [
  [
    "ruff",
    "check",
    "--fix",
    "--fix-only",
    { replace = "ref", of = [
      "vars",
      "all_path",
    ], extend = true },
  ],
]
dependency_groups = [ "lint" ]

[vars]
src_path = "{toxinidir}/src/"
tst_path = "{toxinidir}/tests/"
lib_path = "{toxinidir}/lib/charms/saml_integrator"
all_path = [ "{toxinidir}/src/", "{toxinidir}/tests/", "{toxinidir}/lib/charms/saml_integrator" ]
```

---

### 6. Full Content of `charmcraft.yaml`

```yaml
# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

# Learn more about charmcraft.yaml configuration at:
# https://juju.is/docs/sdk/charmcraft-config
type: "charm"
bases:
  - build-on:
      - name: "ubuntu"
        channel: "22.04"
    run-on:
      - name: "ubuntu"
        channel: "22.04"
parts:
  charm:
    source: .
    plugin: uv
    build-snaps:
    - astral-uv
```

---

### 7. Dependency Specifications Summary

**Primary Dependencies (runtime):**
- `lxml==6.0.2` - XML processing
- `ops==3.6.0` - Juju Charm library
- `pydantic==2.12.5` - Data validation
- `signxml==4.3.0` - XML signing/verification

**Development Dependency Groups:**
- **fmt**: ruff (code formatting)
- **lint**: codespell, mypy, ops-scenario, pep8-naming, pytest, pytest-asyncio, pytest-operator, requests, ruff, type stubs
- **unit**: coverage, pytest
- **coverage-report**: coverage, pytest
- **static**: bandit (security analysis)
- **interface**: ops-scenario, pytest, pytest-interface-tester
- **integration**: allure-pytest, allure-pytest-collection-report, juju, pytest, pytest-asyncio, pytest-operator

**Dependency Management:**
- Uses `uv` (Astral Python package manager) for both building (charmcraft.yaml) and dependency resolution
- Lock file: `uv.lock` (in repository root)
- Python Version Support: 3.10, 3.11, 3.12, 3.13, 3.14

**Testing Configuration:**
- pytest min version: 6.0
- Coverage fail threshold: 99%
- tox environments: lint, unit, static, interface, coverage-report, fmt, lint-fix, integration

This repository is a Juju charm operator for SAML integration with comprehensive test coverage including unit, integration, and interface compliance tests.


---

<sub>⏱️ 1m 10s</sub>

### ✅ `bash`

**Install jubilant and pytest-jubilant**

$ pip install jubilant pytest-jubilant 2>&1 | tail -5

```
bash: pip: command not found
<exited with exit code 0>
```


---

<sub>⏱️ 1m 13s</sub>

### ✅ `bash`

**Install jubilant and pytest-jubilant with pip3**

$ pip3 install jubilant pytest-jubilant 2>&1 | tail -10

```
bash: pip3: command not found
<exited with exit code 0>
```


---

<sub>⏱️ 1m 17s</sub>

### ✅ `bash`

**Install using python3 -m pip**

$ python3 -m pip install jubilant pytest-jubilant 2>&1 | tail -10

```
/usr/bin/python3: No module named pip
<exited with exit code 0>
```


---

<sub>⏱️ 1m 21s</sub>

### ✅ `bash`

**Find available Python package managers**

$ which python3 uv pip pip3 2>/dev/null; ls /usr/local/bin/pip* /usr/local/bin/uv 2>/dev/null; apt list --installed 2>/dev/null | grep -E 'python|pip|uv'

<details>
<summary>95 lines</summary>

```
/usr/bin/python3
/snap/bin/uv
libpipeline1/noble,now 1.5.7-2 amd64 [installed,automatic]
libpython3-stdlib/noble-updates,noble-security,now 3.12.3-0ubuntu2.1 amd64 [installed,automatic]
libpython3.12-minimal/noble-updates,noble-security,now 3.12.3-1ubuntu0.11 amd64 [installed,automatic]
libpython3.12-stdlib/noble-updates,noble-security,now 3.12.3-1ubuntu0.11 amd64 [installed,automatic]
libpython3.12t64/noble-updates,noble-security,now 3.12.3-1ubuntu0.11 amd64 [installed,automatic]
libsharpyuv0/noble,now 1.3.2-0.4build3 amd64 [installed,automatic]
libuv1t64/noble,now 1.48.0-1.1build1 amd64 [installed,automatic]
python-apt-common/noble-updates,now 2.7.7ubuntu5.2 all [installed,automatic]
python-babel-localedata/noble,now 2.10.3-3build1 all [installed]
python3-apport/noble-updates,noble-security,now 2.28.1-0ubuntu3.8 all [installed,automatic]
python3-apt/noble-updates,now 2.7.7ubuntu5.2 amd64 [installed,automatic]
python3-attr/noble,now 23.2.0-2 all [installed,automatic]
python3-automat/noble,now 22.10.0-2 all [installed,automatic]
python3-babel/noble,now 2.10.3-3build1 all [installed]
python3-bcrypt/noble,now 3.2.2-1build1 amd64 [installed,automatic]
python3-blinker/noble,now 1.7.0-1 all [installed,automatic]
python3-boto3/noble,now 1.34.46+dfsg-1ubuntu1 all [installed,automatic]
python3-botocore/noble,now 1.34.46+repack-1ubuntu1 all [installed,automatic]
python3-bpfcc/noble,now 0.29.1+ds-1ubuntu7 all [installed,automatic]
python3-certifi/noble,now 2023.11.17-1 all [installed,automatic]
python3-cffi-backend/noble,now 1.16.0-2build1 amd64 [installed,automatic]
python3-chardet/noble,now 5.2.0+dfsg-1 all [installed,automatic]
python3-click/noble,now 8.1.6-2 all [installed,automatic]
python3-colorama/noble,now 0.4.6-4 all [installed,automatic]
python3-commandnotfound/noble,now 23.04.0 all [installed,automatic]
python3-configobj/noble,now 5.0.8-3 all [installed,automatic]
python3-constantly/noble,now 23.10.4-1 all [installed,automatic]
python3-cryptography/noble-updates,noble-security,now 41.0.7-4ubuntu0.1 amd64 [installed,automatic]
python3-dateutil/noble,now 2.8.2-3ubuntu1 all [installed,automatic]
python3-dbus/noble,now 1.3.2-5build3 amd64 [installed,automatic]
python3-debconf/noble,now 1.5.86ubuntu1 all [installed,automatic]
python3-debian/noble,now 0.1.49ubuntu2 all [installed,automatic]
python3-distro-info/noble,now 1.7build1 all [installed,automatic]
python3-distro/noble,now 1.9.0-1 all [installed,automatic]
python3-distupgrade/noble-updates,now 1:24.04.28 all [installed,automatic]
python3-gdbm/noble,now 3.12.3-0ubuntu1 amd64 [installed,automatic]
python3-gi/noble,now 3.48.2-1 amd64 [installed,automatic]
python3-hamcrest/noble,now 2.1.0-1 all [installed,automatic]
python3-httplib2/noble,now 0.20.4-3 all [installed,automatic]
python3-hyperlink/noble,now 21.0.0-5 all [installed,automatic]
python3-idna/noble-updates,noble-security,now 3.6-2ubuntu0.1 all [installed,automatic]
python3-incremental/noble,now 22.10.0-1 all [installed,automatic]
python3-jinja2/noble-updates,noble-security,now 3.1.2-1ubuntu1.3 all [installed]
python3-jmespath/noble,now 1.0.1-1 all [installed,automatic]
python3-json-pointer/noble,now 2.0-0ubuntu1 all [installed]
python3-jsonpatch/noble,now 1.32-3 all [installed]
python3-jsonschema/noble,now 4.10.3-2ubuntu1 all [installed]
python3-jwt/noble,now 2.7.0-1 all [installed,automatic]
python3-launchpadlib/noble,now 1.11.0-6 all [installed,automatic]
python3-lazr.restfulclient/noble,now 0.14.6-1 all [installed,automatic]
python3-lazr.uri/noble,now 1.0.6-3 all [installed,automatic]
python3-magic/noble,now 2:0.4.27-3 all [installed,automatic]
python3-markdown-it/noble,now 3.0.0-2 all [installed,automatic]
python3-markupsafe/noble,now 2.1.5-1build2 amd64 [installed]
python3-mdurl/noble,now 0.1.2-1 all [installed,automatic]
python3-minimal/noble-updates,noble-security,now 3.12.3-0ubuntu2.1 amd64 [installed,automatic]
python3-netaddr/noble,now 0.8.0-2ubuntu1 all [installed,automatic]
python3-netifaces/noble,now 0.11.0-2build3 amd64 [installed,automatic]
python3-netplan/noble-updates,now 1.1.2-8ubuntu1~24.04.1 amd64 [installed,automatic]
python3-newt/noble,now 0.52.24-2ubuntu2 amd64 [installed,automatic]
python3-oauthlib/noble,now 3.2.2-1 all [installed,automatic]
python3-openssl/noble,now 23.2.0-1 all [installed,automatic]
python3-packaging/noble,now 24.0-1 all [installed,automatic]
python3-pexpect/noble,now 4.9-2 all [installed,automatic]
python3-pkg-resources/noble-updates,noble-security,now 68.1.2-2ubuntu1.2 all [installed,automatic]
python3-problem-report/noble-updates,noble-security,now 2.28.1-0ubuntu3.8 all [installed,automatic]
python3-ptyprocess/noble,now 0.7.0-5 all [installed,automatic]
python3-pyasn1-modules/noble,now 0.2.8-1 all [installed,automatic]
python3-pyasn1/noble-updates,noble-security,now 0.4.8-4ubuntu0.1 all [installed,automatic]
python3-pygments/noble,now 2.17.2+dfsg-1 all [installed,automatic]
python3-pyparsing/noble,now 3.1.1-1 all [installed,automatic]
python3-pyrsistent/noble,now 0.20.0-1build2 amd64 [installed]
python3-requests/noble-updates,noble-security,now 2.31.0+dfsg-1ubuntu1.1 all [installed,automatic]
python3-rich/noble,now 13.7.1-1 all [installed,automatic]
python3-s3transfer/noble,now 0.10.1-1ubuntu2 all [installed,automatic]
python3-serial/noble,now 3.5-2 all [installed]
python3-service-identity/noble,now 24.1.0-1 all [installed,automatic]
python3-setuptools/noble-updates,noble-security,now 68.1.2-2ubuntu1.2 all [installed,automatic]
python3-six/noble,now 1.16.0-4 all [installed,automatic]
python3-software-properties/noble-updates,now 0.99.49.3 all [installed,automatic]
python3-systemd/noble,now 235-1build4 amd64 [installed,automatic]
python3-twisted/noble-updates,noble-security,now 24.3.0-1ubuntu0.1 all [installed,automatic]
python3-typing-extensions/noble,now 4.10.0-1 all [installed,automatic]
python3-tz/noble,now 2024.1-2 all [installed]
python3-update-manager/noble-updates,now 1:24.04.12 all [installed,automatic]
python3-urllib3/noble-updates,noble-security,now 2.0.7-1ubuntu0.6 all [installed,automatic]
python3-wadllib/noble,now 1.3.6-5 all [installed,automatic]
python3-yaml/noble,now 6.0.1-2build2 amd64 [installed,automatic]
python3-zope.interface/noble,now 6.1-1build1 amd64 [installed,automatic]
python3.12-minimal/noble-updates,noble-security,now 3.12.3-1ubuntu0.11 amd64 [installed,automatic]
python3.12/noble-updates,noble-security,now 3.12.3-1ubuntu0.11 amd64 [installed,automatic]
python3/noble-updates,noble-security,now 3.12.3-0ubuntu2.1 amd64 [installed,automatic]
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 1m 25s</sub>

### ✅ `bash`

**Install jubilant and pytest-jubilant with uv**

$ cd /tmp/saml-integrator-L3-sonnet && uv pip install jubilant pytest-jubilant --system 2>&1 | tail -15

<details>
<summary>12 lines</summary>

```
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

hint: Virtual environments were not considered due to the `--system` flag
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 1m 29s</sub>

### ✅ `bash`

**Create venv and install jubilant packages**

$ uv venv /tmp/jubilant-env && /tmp/jubilant-env/bin/pip install jubilant pytest-jubilant 2>&1 | tail -10

```
Using CPython 3.12.3 interpreter at: /usr/bin/python3
Creating virtual environment at: /tmp/jubilant-env
Activate with: source /tmp/jubilant-env/bin/activate
bash: /tmp/jubilant-env/bin/pip: No such file or directory
<exited with exit code 0>
```


---

<sub>⏱️ 1m 34s</sub>

### ✅ `bash`

**Install jubilant in venv using uv pip**

$ source /tmp/jubilant-env/bin/activate && uv pip install jubilant pytest-jubilant 2>&1 | tail -10

<details>
<summary>11 lines</summary>

```
Prepared 2 packages in 133ms
Installed 8 packages in 3ms
 + iniconfig==2.3.0
 + jubilant==1.7.0
 + packaging==26.0
 + pluggy==1.6.0
 + pygments==2.19.2
 + pytest==9.0.2
 + pytest-jubilant==1.1
 + pyyaml==6.0.3
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 1m 39s</sub>

### ✅ `bash`

**Read jubilant API documentation**

$ source /tmp/jubilant-env/bin/activate && python3 -c "import jubilant; help(jubilant)" 2>&1 | head -150

<details>
<summary>146 lines</summary>

```
Help on package jubilant:

NAME
    jubilant - Jubilant is a Pythonic wrapper around the Juju CLI.

PACKAGE CONTENTS
    _all_any
    _juju
    _pretty
    _task
    _test_helpers
    _version
    _yaml
    modeltypes
    secrettypes
    statustypes

CLASSES
    builtins.Exception(builtins.BaseException)
        jubilant._juju.WaitError
        jubilant._task.TaskError
    builtins.object
        jubilant._juju.Juju
        jubilant._task.Task
        jubilant._version.Version
        jubilant.modeltypes.ModelInfo
        jubilant.secrettypes.Secret
            jubilant.secrettypes.RevealedSecret
        jubilant.statustypes.Status
    builtins.str(builtins.object)
        jubilant.secrettypes.SecretURI
    subprocess.CalledProcessError(subprocess.SubprocessError)
        jubilant._juju.CLIError

    class CLIError(subprocess.CalledProcessError)
     |  CLIError(returncode, cmd, output=None, stderr=None)
     |
     |  Subclass of ``CalledProcessError`` that includes stdout and stderr in the ``__str__``.
     |
     |  Method resolution order:
     |      CLIError
     |      subprocess.CalledProcessError
     |      subprocess.SubprocessError
     |      builtins.Exception
     |      builtins.BaseException
     |      builtins.object
     |
     |  Methods defined here:
     |
     |  __str__(self) -> 'str'
     |      Return str(self).
     |
     |  ----------------------------------------------------------------------
     |  Methods inherited from subprocess.CalledProcessError:
     |
     |  __init__(self, returncode, cmd, output=None, stderr=None)
     |      Initialize self.  See help(type(self)) for accurate signature.
     |
     |  ----------------------------------------------------------------------
     |  Data descriptors inherited from subprocess.CalledProcessError:
     |
     |  stdout
     |      Alias for output attribute, to match stderr
     |
     |  ----------------------------------------------------------------------
     |  Data descriptors inherited from subprocess.SubprocessError:
     |
     |  __weakref__
     |      list of weak references to the object
     |
     |  ----------------------------------------------------------------------
     |  Static methods inherited from builtins.Exception:
     |
     |  __new__(*args, **kwargs) class method of builtins.Exception
     |      Create and return a new object.  See help(type) for accurate signature.
     |
     |  ----------------------------------------------------------------------
     |  Methods inherited from builtins.BaseException:
     |
     |  __delattr__(self, name, /)
     |      Implement delattr(self, name).
     |
     |  __getattribute__(self, name, /)
     |      Return getattr(self, name).
     |
     |  __reduce__(...)
     |      Helper for pickle.
     |
     |  __repr__(self, /)
     |      Return repr(self).
     |
     |  __setattr__(self, name, value, /)
     |      Implement setattr(self, name, value).
     |
     |  __setstate__(...)
     |
     |  add_note(...)
     |      Exception.add_note(note) --
     |      add a note to the exception
     |
     |  with_traceback(...)
     |      Exception.with_traceback(tb) --
     |      set self.__traceback__ to tb and return self.
     |
     |  ----------------------------------------------------------------------
     |  Data descriptors inherited from builtins.BaseException:
     |
     |  __cause__
     |      exception cause
     |
     |  __context__
     |      exception context
     |
     |  __dict__
     |
     |  __suppress_context__
     |
     |  __traceback__
     |
     |  args

    class Juju(builtins.object)
     |  Juju(*, model: 'str | None' = None, wait_timeout: 'float' = 180.0, cli_binary: 'str | pathlib.Path | None' = None)
     |
     |  Instantiate this class to run Juju commands.
     |
     |  Most methods directly call a single Juju CLI command. If a CLI command doesn't yet exist as a
     |  method, use :meth:`cli`.
     |
     |  Example::
     |
     |      juju = jubilant.Juju()
     |      juju.deploy('snappass-test')
     |
     |  Args:
     |      model: If specified, operate on this Juju model, otherwise use the current Juju model.
     |          If the model is in another controller, prefix the model name with ``<controller>:``.
     |      wait_timeout: The default timeout for :meth:`wait` (in seconds) if that method's *timeout*
     |          parameter is not specified.
     |      cli_binary: Path to the Juju CLI binary. If not specified, uses ``juju`` and assumes it is
     |          in the PATH.
     |
     |  Methods defined here:
     |
     |  __init__(self, *, model: 'str | None' = None, wait_timeout: 'float' = 180.0, cli_binary: 'str | pathlib.Path | None' = None)
     |      Initialize self.  See help(type(self)) for accurate signature.
     |
     |  __repr__(self) -> 'str'
     |      Return repr(self).
     |
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 1m 43s</sub>

### ✅ `bash`

**Read Juju class API**

$ source /tmp/jubilant-env/bin/activate && python3 -c "import jubilant; help(jubilant.Juju)" 2>&1 | head -250

<details>
<summary>250 lines</summary>

```
Help on class Juju in module jubilant._juju:

class Juju(builtins.object)
 |  Juju(*, model: 'str | None' = None, wait_timeout: 'float' = 180.0, cli_binary: 'str | pathlib.Path | None' = None)
 |
 |  Instantiate this class to run Juju commands.
 |
 |  Most methods directly call a single Juju CLI command. If a CLI command doesn't yet exist as a
 |  method, use :meth:`cli`.
 |
 |  Example::
 |
 |      juju = jubilant.Juju()
 |      juju.deploy('snappass-test')
 |
 |  Args:
 |      model: If specified, operate on this Juju model, otherwise use the current Juju model.
 |          If the model is in another controller, prefix the model name with ``<controller>:``.
 |      wait_timeout: The default timeout for :meth:`wait` (in seconds) if that method's *timeout*
 |          parameter is not specified.
 |      cli_binary: Path to the Juju CLI binary. If not specified, uses ``juju`` and assumes it is
 |          in the PATH.
 |
 |  Methods defined here:
 |
 |  __init__(self, *, model: 'str | None' = None, wait_timeout: 'float' = 180.0, cli_binary: 'str | pathlib.Path | None' = None)
 |      Initialize self.  See help(type(self)) for accurate signature.
 |
 |  __repr__(self) -> 'str'
 |      Return repr(self).
 |
 |  add_credential(self, cloud: 'str', credential: 'str | pathlib.Path | Mapping[str, Any]', *, client: 'bool' = False, controller: 'str | None' = None, region: 'str | None' = None) -> 'None'
 |      Add a credential for a cloud.
 |
 |      Args:
 |          cloud: Name of the cloud to add credentials for.
 |          credential: Path to a YAML file containing credential to add, or a mapping
 |              representing the parsed credential YAML (``{'credentials': ...}``).
 |          client: Set to True to save credentials on the client, meaning controllers
 |              created later will have access to them. You must specify ``client=True``
 |              or provide *controller* (or both).
 |          controller: If specified, save credentials to the named controller.
 |          region: Cloud region that the credential is valid for.
 |
 |  add_model(self, model: 'str', cloud: 'str | None' = None, *, controller: 'str | None' = None, config: 'Mapping[str, ConfigValue] | None' = None, credential: 'str | None' = None) -> 'None'
 |      Add a named model and set this instance's model to it.
 |
 |      To avoid interfering with CLI users, this won't switch the Juju CLI to the
 |      newly-created model. However, because :attr:`model` is set to the name of the new
 |      model, all subsequent operations on this instance will use the new model.
 |
 |      Args:
 |          model: Name of model to add.
 |          cloud: Name of cloud or region (or cloud/region) to use for the model.
 |          controller: Name of controller to operate in. If not specified, use the current
 |              controller.
 |          config: Model configuration as key-value pairs, for example,
 |              ``{'image-stream': 'daily'}``.
 |          credential: Name of cloud credential to use for the model.
 |
 |  add_secret(self, name: 'str', content: 'Mapping[str, str]', *, info: 'str | None' = None) -> 'SecretURI'
 |      Add a new named secret and return its secret URI.
 |
 |      Args:
 |          name: Name for the secret.
 |          content: Key-value pairs that represent the secret content, for example
 |              ``{'password': 'hunter2'}``.
 |          info: Description for the secret.
 |
 |  add_ssh_key(self, *keys: 'str') -> 'None'
 |      Add one or more SSH keys to the model.
 |
 |      The SSH keys are added to all current and future machines in the model.
 |
 |      Args:
 |          keys: SSH public key or keys to add. Each key should be the full
 |              SSH public key string (for example, ``ssh-rsa AAAAB3... user@host``).
 |
 |  add_unit(self, app: 'str', *, attach_storage: 'str | Iterable[str] | None' = None, num_units: 'int' = 1, to: 'str | Iterable[str] | None' = None)
 |      Add one or more units to a deployed application.
 |
 |      Args:
 |          app: Name of application to add units to.
 |          attach_storage: Existing storage(s) to attach to the deployed unit, for example,
 |              ``foo/0`` or ``mydisk/1``. Not available for Kubernetes models.
 |          num_units: Number of units to add.
 |          to: Machine or container to deploy the unit in (bypasses constraints). For example,
 |              to deploy to a new LXD container on machine 25, use ``lxd:25``.
 |
 |  bootstrap(self, cloud: 'str', controller: 'str', *, bootstrap_base: 'str | None' = None, bootstrap_constraints: 'Mapping[str, str] | None' = None, config: 'Mapping[str, ConfigValue] | None' = None, constraints: 'Mapping[str, str] | None' = None, credential: 'str | None' = None, force: 'bool' = False, model_defaults: 'Mapping[str, ConfigValue] | None' = None, storage_pool: 'Mapping[str, str] | None' = None, to: 'str | Iterable[str] | None' = None) -> 'None'
 |      Bootstrap a controller on a cloud environment.
 |
 |      To avoid interfering with CLI users, this does not switch the Juju CLI
 |      to the newly-created controller. In addition, ``self.model`` is not updated.
 |
 |      If you want to create a new controller with a model, use :meth:`add_model`
 |      after calling this method, which will set ``self.model`` for future commands::
 |
 |          juju = jubilant.Juju()
 |          juju.bootstrap('lxd', 'myctrl')
 |          juju.add_model('mymodel', controller='myctrl')
 |          # self.model will be 'myctrl.mymodel' here
 |
 |      Args:
 |          cloud: Name of cloud to bootstrap on. Initialization consists of creating a
 |              "controller" model and provisioning a machine to act as controller.
 |          controller: Name for the controller.
 |          bootstrap_base: Specify the base of the bootstrap machine, for example
 |              ``"24.04"``.
 |          bootstrap_constraints: Specify bootstrap machine constraints, for example,
 |              ``{'mem': '8G'}``. If used, its values will also apply to any future
 |              controllers provisioned for high availability (HA).
 |          config: Controller configuration options. Model config keys only affect the
 |              controller model.
 |          constraints: Set model constraints, for example, ``{'mem': '8G', 'cores': '4'}``.
 |              If used, its values will be set as the default constraints for all future
 |              workload machines in the model, exactly as if the constraints were set with
 |              ``juju set-model-constraints``.
 |          credential: Name of cloud credential to use when bootstrapping.
 |          force: If True, allow bypassing of checks such as supported bases.
 |          model_defaults: Configuration options to set for all models.
 |          storage_pool: Options for an initial storage pool as key-value pairs. ``name``
 |              and ``type`` are required, plus any additional attributes.
 |          to: Placement directive indicating an instance to bootstrap.
 |
 |  cli(self, *args: 'str', include_model: 'bool' = True, stdin: 'str | None' = None) -> 'str'
 |      Run a Juju CLI command and return its standard output.
 |
 |      Args:
 |          args: Command-line arguments (excluding ``juju``).
 |          include_model: If true and :attr:`model` is set, insert the ``--model`` argument
 |              after the first argument in *args*.
 |          stdin: Standard input to send to the process, if any.
 |
 |  config(self, app: 'str', values: 'Mapping[str, ConfigValue] | None' = None, *, app_config: 'bool' = False, reset: 'str | Iterable[str]' = ()) -> 'Mapping[str, ConfigValue] | None'
 |      Get or set the configuration of a deployed application.
 |
 |      If called with only the *app* argument, get the config and return it.
 |
 |      If called with the *values* or *reset* arguments, set the config values and return None,
 |      and reset any keys in *reset* to their defaults.
 |
 |      Args:
 |          app: Application name to get or set config for.
 |          values: Mapping of config names to values to set.
 |          app_config: When getting config, set this to True to get the
 |              (poorly-named) "application-config" values instead of charm config.
 |          reset: Key or list of keys to reset to their defaults.
 |
 |  consume(self, model_and_app: 'str', alias: 'str | None' = None, *, controller: 'str | None' = None, owner: 'str | None' = None) -> 'None'
 |      Add a remote offer to the model.
 |
 |      Examples::
 |
 |          juju.consume('othermodel.mysql', 'sql')
 |          juju.consume('othermodel.mysql', controller='ctrl2', owner='admin')
 |
 |      Args:
 |          model_and_app: Dotted application and model name to offer endpoints for, for example
 |              ``othermodel.mysql``.
 |          alias: A local alias for the offer, for use with :meth:`integrate`. Defaults to the
 |              application name.
 |          controller: Remote offer's controller. Defaults to the current controller.
 |          owner: Remote model's owner. Defaults to the user that is currently logged in to the
 |              controller providing the offer.
 |
 |  debug_log(self, *, limit: 'int' = 0) -> 'str'
 |      Return debug log messages from a model.
 |
 |      For example, to create a pytest fixture which shows the last 1000 log lines if any tests
 |      fail::
 |
 |          @pytest.fixture(scope='module')
 |          def juju(request: pytest.FixtureRequest):
 |              with jubilant.temp_model() as juju:
 |                  yield juju  # run the test
 |                  if request.session.testsfailed:
 |                      log = juju.debug_log(limit=1000)
 |                      print(log, end='')
 |
 |      Args:
 |          limit: Limit the result to the most recent *limit* lines. Defaults to 0, meaning
 |              return all lines in the log.
 |
 |  deploy(self, charm: 'str | pathlib.Path', app: 'str | None' = None, *, attach_storage: 'str | Iterable[str] | None' = None, base: 'str | None' = None, bind: 'Mapping[str, str] | str | None' = None, channel: 'str | None' = None, config: 'Mapping[str, ConfigValue] | None' = None, constraints: 'Mapping[str, str] | None' = None, force: 'bool' = False, num_units: 'int' = 1, overlays: 'Iterable[str | pathlib.Path]' = (), resources: 'Mapping[str, str] | None' = None, revision: 'int | None' = None, storage: 'Mapping[str, str] | None' = None, to: 'str | Iterable[str] | None' = None, trust: 'bool' = False) -> 'None'
 |      Deploy an application or bundle.
 |
 |      Args:
 |          charm: Name of charm or bundle to deploy, or path to a local file (must start with
 |              ``/`` or ``.``).
 |          app: Custom application name within the model. Defaults to the charm name.
 |          attach_storage: Existing storage(s) to attach to the deployed unit, for example,
 |              ``foo/0`` or ``mydisk/1``. Not available for Kubernetes models.
 |          base: The base on which to deploy, for example, ``ubuntu@22.04``.
 |          bind: Either a mapping of endpoint-to-space bindings, for example
 |              ``{'database-peers': 'internal-space'}``, or a single space name, which is
 |              equivalent to binding all endpoints to that space.
 |          channel: Channel to use when deploying from Charmhub, for example, ``latest/edge``.
 |          config: Application configuration as key-value pairs, for example,
 |              ``{'name': 'My Wiki'}``.
 |          constraints: Hardware constraints for new machines, for example, ``{'mem': '8G'}``.
 |          force: If true, bypass checks such as supported bases.
 |          num_units: Number of units to deploy for principal charms.
 |          overlays: File paths of bundles to overlay on the primary bundle, applied in order.
 |          resources: Specify named resources to use for deployment, for example:
 |              ``{'bin': '/path/to/some/binary'}``.
 |          revision: Charmhub revision number to deploy.
 |          storage: Constraints for named storage(s), for example, ``{'data': 'tmpfs,1G'}``.
 |          to: Machine or container to deploy the unit in (bypasses constraints). For example,
 |              to deploy to a new LXD container on machine 25, use ``lxd:25``.
 |          trust: If true, allows charm to run hooks that require access to cloud credentials.
 |
 |  destroy_model(self, model: 'str', *, destroy_storage: 'bool' = False, force: 'bool' = False, no_wait: 'bool' = False, release_storage: 'bool' = False, timeout: 'float | None' = None) -> 'None'
 |      Terminate all machines (or containers) and resources for a model.
 |
 |      If the given model is this instance's model, also sets this instance's
 |      :attr:`model` to None.
 |
 |      Args:
 |          model: Name of model to destroy.
 |          destroy_storage: If True, destroy all storage instances in the model.
 |          force: If True, force model destruction and ignore any errors.
 |          no_wait: If True, rush through model destruction without waiting for each step
 |              to complete.
 |          release_storage: If True, release all storage instances in the model.
 |              This is mutually exclusive with *destroy_storage*.
 |          timeout: Maximum time (in seconds) to wait for each step in the model destruction.
 |              This option can only be used with *force*.
 |
 |  exec(self, command: 'str', *args: 'str', machine: 'int | str | None' = None, unit: 'str | None' = None, wait: 'float | None' = None) -> 'Task'
 |      Run the command on the remote target specified.
 |
 |      You must specify either *machine* or *unit*, but not both.
 |
 |      Note: this method does not support running a command on multiple units
 |      at once. If you need that, let us know, and we'll consider adding it
 |      with a new ``exec_multiple`` method or similar.
 |
 |      Args:
 |          command: Command to run. Because the command is executed using the shell,
 |              arguments may also be included here as a single string, for example
 |              ``juju.exec('echo foo', ...)``.
 |          args: Arguments of the command.
 |          machine: ID of machine to run the command on, for example ``0``, ``"0"``,
 |              or ``"0/lxd/0"``.
 |          unit: Name of unit to run the command on, for example ``mysql/0`` or ``mysql/leader``.
 |          wait: Maximum time to wait for command to finish; :class:`TimeoutError` is raised if
 |              this is reached. Juju's default is to wait 5 minutes.
 |
 |      Returns:
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 1m 52s</sub>

### ✅ `bash`

**Read key Juju methods**

$ source /tmp/jubilant-env/bin/activate && python3 -c "import jubilant; help(jubilant.Juju)" 2>&1 | grep -A 5 "def integrate\|def wait\|def status\|def relate"

```

<exited with exit code 1>
```


---

<sub>⏱️ 2m 21s</sub>

### ✅ `bash`

**Read wait helper functions**

$ source /tmp/jubilant-env/bin/activate && python3 -c "import jubilant; help(jubilant.all_active); help(jubilant.all_blocked); help(jubilant.any_error)" 2>&1

<details>
<summary>14 lines</summary>

```
Help on function all_active in module jubilant._all_any:

all_active(status: 'Status', *apps: 'str') -> 'bool'
    Report whether all apps and units in *status* (or in *apps* if provided) are "active".

    Examples::

        # Use the callable directly to wait for all apps in status to be active.
        juju.wait(jubilant.all_active)

        # Use a lambda to wait for all apps specified (blog, mysql) to be active.
        juju.wait(lambda status: jubilant.all_active(status, 'blog', 'mysql'))

    Args:
        status: The status object being tested.
        apps: If provided, only these applications (and their units) are tested. If an app is not
            present in ``status.apps``, returns False.
(END)
<command with shellId: 16 is still running after 30 seconds. The command is still running. Check the output above - if it looks like the command is waiting for input, use write_bash to provide it. Otherwise, use read_bash to continue waiting for output, or stop_bash to stop it.>
```

</details>


---

<sub>⏱️ 2m 21s</sub>

### ✅ `bash`

**Read pytest_jubilant API**

$ source /tmp/jubilant-env/bin/activate && python3 -c "import pytest_jubilant; help(pytest_jubilant)" 2>&1

<details>
<summary>17 lines</summary>

```
Help on package pytest_jubilant:

NAME
    pytest_jubilant - Welcome to pytest-jubilant!

PACKAGE CONTENTS
    main
    version

FUNCTIONS
    get_resources(root: Union[pathlib.Path, str] = './') -> Optional[Dict[str, str]]
        Obtain the charm resources from metadata.yaml's upstream-source fields.

    pack(root: Union[pathlib.Path, str] = './', platform: Optional[str] = None) -> pathlib.Path
        Pack a local charm and return it.

DATA
    __all__ = ['pack', 'get_resources']

FILE
    /tmp/jubilant-env/lib/python3.12/site-packages/pytest_jubilant/__init__.py

(END)
<command with shellId: 17 is still running after 30 seconds. The command is still running. Check the output above - if it looks like the command is waiting for input, use write_bash to provide it. Otherwise, use read_bash to continue waiting for output, or stop_bash to stop it.>
```

</details>


---

<sub>⏱️ 2m 25s</sub>

### ✅ `stop_bash`

<details>
<summary>Arguments</summary>

```json
{
  "shellId": "16"
}
```

</details>

```
<command with id: 16 stopped>
```


---

<sub>⏱️ 2m 25s</sub>

### ✅ `stop_bash`

<details>
<summary>Arguments</summary>

```json
{
  "shellId": "17"
}
```

</details>

```
<command with id: 17 stopped>
```


---

<sub>⏱️ 2m 28s</sub>

### ✅ `bash`

**Find jubilant source files**

$ find /tmp/jubilant-env/lib -name "*.py" | xargs grep -l "def " | head -20

<details>
<summary>22 lines</summary>

```
/tmp/jubilant-env/lib/python3.12/site-packages/iniconfig/exceptions.py
/tmp/jubilant-env/lib/python3.12/site-packages/iniconfig/_parse.py
/tmp/jubilant-env/lib/python3.12/site-packages/iniconfig/__init__.py
/tmp/jubilant-env/lib/python3.12/site-packages/packaging/metadata.py
/tmp/jubilant-env/lib/python3.12/site-packages/packaging/requirements.py
/tmp/jubilant-env/lib/python3.12/site-packages/packaging/_structures.py
/tmp/jubilant-env/lib/python3.12/site-packages/packaging/_tokenizer.py
/tmp/jubilant-env/lib/python3.12/site-packages/packaging/licenses/__init__.py
/tmp/jubilant-env/lib/python3.12/site-packages/packaging/tags.py
/tmp/jubilant-env/lib/python3.12/site-packages/packaging/_manylinux.py
/tmp/jubilant-env/lib/python3.12/site-packages/packaging/version.py
/tmp/jubilant-env/lib/python3.12/site-packages/packaging/specifiers.py
/tmp/jubilant-env/lib/python3.12/site-packages/packaging/_parser.py
/tmp/jubilant-env/lib/python3.12/site-packages/packaging/utils.py
/tmp/jubilant-env/lib/python3.12/site-packages/packaging/pylock.py
/tmp/jubilant-env/lib/python3.12/site-packages/packaging/_elffile.py
/tmp/jubilant-env/lib/python3.12/site-packages/packaging/_musllinux.py
/tmp/jubilant-env/lib/python3.12/site-packages/packaging/markers.py
/tmp/jubilant-env/lib/python3.12/site-packages/jubilant/secrettypes.py
/tmp/jubilant-env/lib/python3.12/site-packages/jubilant/statustypes.py
xargs: grep: terminated by signal 13
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 2m 33s</sub>

### ✅ `bash`

**Read key Juju methods from source**

$ cat /tmp/jubilant-env/lib/python3.12/site-packages/jubilant/_juju.py | grep -A 20 "def wait\|def integrate\|def config\|def deploy" | head -150

<details>
<summary>89 lines</summary>

```
def config(self, app: str, *, app_config: bool = False) -> Mapping[str, ConfigValue]: ...

    @overload
    def config(
        self,
        app: str,
        values: Mapping[str, ConfigValue],
        *,
        reset: str | Iterable[str] = (),
    ) -> None: ...

    @overload
    def config(self, app: str, *, reset: str | Iterable[str]) -> None: ...

    def config(
        self,
        app: str,
        values: Mapping[str, ConfigValue] | None = None,
        *,
        app_config: bool = False,
        reset: str | Iterable[str] = (),
    ) -> Mapping[str, ConfigValue] | None:
        """Get or set the configuration of a deployed application.

        If called with only the *app* argument, get the config and return it.

        If called with the *values* or *reset* arguments, set the config values and return None,
        and reset any keys in *reset* to their defaults.

        Args:
            app: Application name to get or set config for.
            values: Mapping of config names to values to set.
            app_config: When getting config, set this to True to get the
                (poorly-named) "application-config" values instead of charm config.
            reset: Key or list of keys to reset to their defaults.
--
    def deploy(
        self,
        charm: str | pathlib.Path,
        app: str | None = None,
        *,
        attach_storage: str | Iterable[str] | None = None,
        base: str | None = None,
        bind: Mapping[str, str] | str | None = None,
        channel: str | None = None,
        config: Mapping[str, ConfigValue] | None = None,
        constraints: Mapping[str, str] | None = None,
        force: bool = False,
        num_units: int = 1,
        overlays: Iterable[str | pathlib.Path] = (),
        resources: Mapping[str, str] | None = None,
        revision: int | None = None,
        storage: Mapping[str, str] | None = None,
        to: str | Iterable[str] | None = None,
        trust: bool = False,
    ) -> None:
        """Deploy an application or bundle.
--
    def integrate(self, app1: str, app2: str, *, via: str | Iterable[str] | None = None) -> None:
        """Integrate two applications, creating a relation between them.

        The order of *app1* and *app2* is not significant. Each of them should
        be in the format ``<application>[:<endpoint>]``. The endpoint is only
        required if there's more than one possible integration between the two
        applications.

        To integrate an application in the current model with an application in
        another model (cross-model), prefix *app1* or *app2* with ``<model>.``.
        To integrate with an application on another controller, *app1* or *app2* must
        be an offer endpoint. See ``juju integrate --help`` for details.

        Args:
            app1: One of the applications (and endpoints) to integrate.
            app2: The other of the applications (and endpoints) to integrate.
            via: Inform the offering side (the remote application) of the
                source of traffic, to enable network ports to be opened. This
                is in CIDR notation, for example ``192.0.2.0/24``.
        """
        args = ['integrate', app1, app2]
--
    def wait(
        self,
        ready: Callable[[Status], bool],
        *,
        error: Callable[[Status], bool] | None = None,
        delay: float = 1.0,
        timeout: float | None = None,
        successes: int = 3,
    ) -> Status:
        """Wait until ``ready(status)`` returns true.

        This fetches the Juju status repeatedly (waiting *delay* seconds between each call),
        and returns the last status after the *ready* callable returns true for *successes*
        times in a row.

        Example::

            juju = jubilant.Juju()
            juju.deploy('snappass-test')
            juju.wait(jubilant.all_active)
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 2m 33s</sub>

### ✅ `bash`

**Read pytest_jubilant main module**

$ cat /tmp/jubilant-env/lib/python3.12/site-packages/pytest_jubilant/main.py

<details>
<summary>237 lines</summary>

```
#!/usr/bin/env python3
# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

"""Main plugin module."""
import dataclasses
import logging
import os
import secrets
import shlex
import subprocess
from pathlib import Path
from typing import Union, Optional, Dict
from unittest.mock import MagicMock, patch

import jubilant
import pytest
import yaml

JDL_LOGFILE_EXTENSION = "-jdl.txt"
DEFAULT_JDL_DUMP_PATH = "./.logs"


def pytest_addoption(parser):
    group = parser.getgroup("jubilant")
    group.addoption(
        "--model",
        action="store",
        default=None,
        help="Juju model name to target.",
    )
    group.addoption(
        "--keep-models",
        action="store_true",
        default=False,
        help="Skip model teardown.",
    )
    group.addoption(
        "--no-setup",
        action="store_true",
        default=False,
        help='Skip tests marked with "setup".',
    )
    group.addoption(
        "--no-teardown",
        action="store_true",
        default=False,
        help='Skip tests marked with "teardown".',
    )
    group.addoption(
        "--switch",
        action="store_true",
        default=False,
        help="Switch to the temporary model that is currently being worked on.",
    )
    group.addoption(
        "--dump-logs",
        action="store",
        default=DEFAULT_JDL_DUMP_PATH,
        help="Directory in which to dump any juju debug-log for any model prior to tearing it down. "
        "Set to empty string to disable the behaviour.",
    )


_cli_mock: Optional[MagicMock] = None


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "setup: tests that setup some parts of the environment."
    )
    config.addinivalue_line(
        "markers", "teardown: tests that tear down some parts of the environment."
    )

    # horrible to do it this way, but it's easy
    if os.getenv("PYTESTING_PYTEST_JUBILANT"):
        mm = MagicMock()
        mm.return_value = MagicMock(stdout="output", stderr="error")
        ctx = patch("subprocess.run", new=mm)
        ctx.__enter__()
        global _cli_mock
        _cli_mock = mm


def pytest_collection_modifyitems(config: pytest.Config, items):
    def _set_keep_models(val: bool = True):
        # TODO: less hacky way to do this?
        optname = config._opt2dest.get("--keep-models", "--keep-models")  # noqa
        config.option.__setattr__(optname, val)

    if config.getoption("--no-teardown"):
        skipper = pytest.mark.skip(reason="--no-teardown provided.")
        for item in items:
            if "teardown" in item.keywords:
                item.add_marker(skipper)

        if config.getoption("--keep-models"):
            logging.warning("--no-teardown implies --keep-models")
        else:
            _set_keep_models(True)

    if config.getoption("--no-setup"):
        skipper = pytest.mark.skip(reason="--no-setup provided.")
        for item in items:
            if "setup" in item.keywords:
                item.add_marker(skipper)


class TempModelFactory:
    """Manages temporary models for testing."""

    def __init__(
        self,
        prefix: str,
        randbits: Optional[str] = None,
        check_models_unique: bool = True,
    ):
        self.prefix = prefix
        self.randbits = randbits
        self._models: Dict[str, jubilant.Juju] = {}
        self._check_models_unique = check_models_unique

    def get_juju(self, suffix: str) -> jubilant.Juju:
        model_name = "-".join(filter(None, (self.prefix, self.randbits, suffix)))
        if model_name in self._models:
            raise ValueError(
                f"model {model_name} already registered on this temp_model factory. "
                "choose a different prefix."
            )

        juju = jubilant.Juju(model=model_name)
        try:
            juju.add_model(model_name)
        except jubilant.CLIError as e:
            # If --model is set (_check_models_unique is False), then the user wants collisions.
            # If the name is randomly generated, the chance of colliding with another
            # randomly generated model that wasn't torn down is tiny, but still present.
            if (
                "already exists on this k8s cluster" in e.args[1]
                and self._check_models_unique
            ):
                raise

        self._models[model_name] = juju
        return juju

    def dump_all_logs(self, path: Path = Path(DEFAULT_JDL_DUMP_PATH)):
        path.mkdir(parents=True, exist_ok=True)
        for model, juju in self._models.items():
            jdl_path = path / (model + JDL_LOGFILE_EXTENSION)
            jdl = juju.cli("debug-log", "--replay")
            jdl_path.write_text(jdl)
            logging.info(f"dropping jdl for model {model} to {jdl_path}")

    def teardown(self, force: bool = False):
        for model, juju in self._models.items():
            juju.destroy_model(model, destroy_storage=True, force=force)


@pytest.fixture(scope="module")
def cli_mock(request):
    yield _cli_mock


@pytest.fixture(scope="module")
def temp_model_factory(request):
    user_model = request.config.getoption("--model")
    if user_model:
        prefix = user_model
        randbits = None
    else:
        prefix = (request.module.__name__.rpartition(".")[-1]).replace("_", "-")
        randbits = (
            "testing"
            if os.getenv("PYTESTING_PYTEST_JUBILANT")
            else secrets.token_hex(4)
        )
    factory = TempModelFactory(
        prefix=prefix, randbits=randbits, check_models_unique=not user_model
    )

    yield factory

    # BEFORE tearing down the models, dump any and all juju debug-logs
    if dump_logs := request.config.getoption("--dump-logs"):
        factory.dump_all_logs(Path(dump_logs))

    if not request.config.getoption("--keep-models"):
        # TODO: jubilant defaults to --force, but is that a good idea?
        factory.teardown(force=True)

    if _cli_mock:
        _cli_mock.reset_mock()


@pytest.fixture(scope="module")
def juju(request, temp_model_factory):
    juju = temp_model_factory.get_juju("")
    if request.config.getoption("--switch"):
        juju.cli("switch", juju.model, include_model=False)
    return juju


@dataclasses.dataclass
class _Result:
    charm: Path
    resources: Optional[Dict[str, str]]


def _pack(root: Union[Path, str], platform: Optional[str] = None):
    _platform = f" --platform {platform}" if platform else ""
    cmd = f"charmcraft pack -p {root}{_platform}"
    proc = subprocess.run(
        shlex.split(cmd),
        check=True,
        capture_output=True,
        text=True,
    )

    # The output looks like:
    # ❯ charmcraft pack
    # Packed tempo-coordinator-k8s_ubuntu@24.04-amd64.charm
    # Packed tempo-coordinator-k8s_ubuntu@22.04-amd64.charm

    # Don't ask me why this goes to stderr.
    output = proc.stderr

    # we parse it and collect all the built charms.
    packed_charms = []
    for line in output.strip().splitlines():
        if line.startswith("Packed"):
            packed_charms.append(line.split()[1])

    if not packed_charms:
        raise ValueError(
            f"unable to get packed charm(s) ({cmd!r} completed with {proc.returncode=}, {proc.stdout=}, {proc.stderr=})"
        )

    return packed_charms


def pack(root: Union[Path, str] = "./", platform: Optional[str] = None) -> Path:
    """Pack a local charm and return it."""
    packed_charms = _pack(root, platform)

    if len(packed_charms) > 1:
        raise ValueError(
            "This charm supports multiple platforms. "
            "Pass a `platform` argument to control which charm you're getting instead."
        )

    return Path(packed_charms[0]).resolve()


def get_resources(root: Union[Path, str] = "./") -> Optional[Dict[str, str]]:
    """Obtain the charm resources from metadata.yaml's upstream-source fields."""
    for meta_name in ("metadata.yaml", "charmcraft.yaml"):
        if (meta_yaml := Path(root) / meta_name).exists():
            logging.debug(f"found metadata file: {meta_yaml}")
            meta = yaml.safe_load(meta_yaml.read_text())
            if meta_resources := meta.get("resources"):
                try:
                    resources = {
                        resource: res_meta["upstream-source"]
                        for resource, res_meta in meta_resources.items()
                    }
                except KeyError:
                    logging.exception(
                        "The `upstream-source` key wasn't found in the resource. If your charm follows a different convention of pointing at an OCI image, you need to pack it manually."
                    )
                    raise
            else:
                resources = None
                logging.info(
                    f"resources not found in {meta_name}; proceeding without resources"
                )
            break
    else:
        resources = None
        logging.error(
            f"metadata/charmcraft.yaml not found at {root}; unable to load resources"
        )

    return resources
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 3m 39s</sub>

### 💬 Copilot

Now I have a clear picture. Let me implement the migration.

---

<sub>⏱️ 3m 39s</sub>

### ✅ `sql`

**Create migration todos**

<details>
<summary>Arguments</summary>

```json
{
  "description": "Create migration todos",
  "query": "INSERT INTO todos (id, title, description, status) VALUES\n  ('update-integration-conftest', 'Update tests/integration/conftest.py', 'Remove pytest_asyncio/OpsTest, replace with jubilant.Juju fixture. app and any_charm fixtures become sync, return str app names, use juju.deploy(). Keep --charm-file option support.', 'pending'),\n  ('update-integration-tests', 'Update tests/integration/test_charm.py', 'Remove async/await, @pytest.mark.asyncio, @pytest.mark.abort_on_fail, ops imports. Replace app.set_config() with juju.config(), model.wait_for_idle with juju.wait(jubilant.all_active), add_relation with juju.integrate().', 'pending'),\n  ('update-root-conftest', 'Update tests/conftest.py', 'Keep --charm-file option for compatibility with jubilant-based conftest.', 'pending'),\n  ('update-pyproject', 'Update pyproject.toml dependencies', 'In integration group: remove juju, pytest-asyncio, pytest-operator; add jubilant, pytest-jubilant. In lint group: remove pytest-asyncio, pytest-operator; add jubilant, pytest-jubilant.', 'pending'),\n  ('update-lockfile', 'Update uv.lock', 'Run uv lock to regenerate lock file after pyproject.toml changes.', 'pending');"
}
```

</details>

```
5 row(s) inserted. Last inserted row ID: 5.
```


---

<sub>⏱️ 3m 43s</sub>

### ✅ `view`

**/tmp/saml-integrator-L3-sonnet/tests/integration/conftest.py**

/tmp/saml-integrator-L3-sonnet/tests/integration/conftest.py

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

<sub>⏱️ 3m 43s</sub>

### ✅ `view`

**/tmp/saml-integrator-L3-sonnet/tests/integration/test_charm.py**

/tmp/saml-integrator-L3-sonnet/tests/integration/test_charm.py

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

<sub>⏱️ 3m 43s</sub>

### ✅ `view`

**/tmp/saml-integrator-L3-sonnet/tests/conftest.py**

/tmp/saml-integrator-L3-sonnet/tests/conftest.py

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

<sub>⏱️ 3m 48s</sub>

### 💬 Copilot

Now I'll update all the files:

---

<sub>⏱️ 3m 48s</sub>

### ✅ `sql`

**Mark todos in progress**

<details>
<summary>Arguments</summary>

```json
{
  "description": "Mark todos in progress",
  "query": "UPDATE todos SET status = 'in_progress' WHERE id IN ('update-integration-conftest', 'update-integration-tests', 'update-root-conftest', 'update-pyproject');"
}
```

</details>

```
4 row(s) updated.
```


---

<sub>⏱️ 3m 59s</sub>

### ✅ `edit`

**/tmp/saml-integrator-L3-sonnet/tests/integration/conftest.py**

/tmp/saml-integrator-L3-sonnet/tests/integration/conftest.py

```
File /tmp/saml-integrator-L3-sonnet/tests/integration/conftest.py updated with changes.
```


---

<sub>⏱️ 4m 9s</sub>

### ✅ `edit`

**/tmp/saml-integrator-L3-sonnet/tests/integration/test_charm.py**

/tmp/saml-integrator-L3-sonnet/tests/integration/test_charm.py

```
File /tmp/saml-integrator-L3-sonnet/tests/integration/test_charm.py updated with changes.
```


---

<sub>⏱️ 4m 14s</sub>

### 💬 Copilot

Now update `pyproject.toml` — replace `pytest-operator`, `pytest-asyncio`, and `juju` in both `lint` and `integration` groups with `jubilant` and `pytest-jubilant`:

---

<sub>⏱️ 4m 14s</sub>

### ✅ `view`

**/tmp/saml-integrator-L3-sonnet/pyproject.toml**

/tmp/saml-integrator-L3-sonnet/pyproject.toml (lines 28-60)

<details>
<summary>33 lines</summary>

```
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
```

</details>


---

<sub>⏱️ 4m 18s</sub>

### ✅ `view`

**/tmp/saml-integrator-L3-sonnet/pyproject.toml**

/tmp/saml-integrator-L3-sonnet/pyproject.toml (lines 59-70)

<details>
<summary>12 lines</summary>

```
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
```

</details>


---

<sub>⏱️ 4m 25s</sub>

### ✅ `edit`

**/tmp/saml-integrator-L3-sonnet/pyproject.toml**

/tmp/saml-integrator-L3-sonnet/pyproject.toml

```
File /tmp/saml-integrator-L3-sonnet/pyproject.toml updated with changes.
```


---

<sub>⏱️ 4m 31s</sub>

### ✅ `edit`

**/tmp/saml-integrator-L3-sonnet/pyproject.toml**

/tmp/saml-integrator-L3-sonnet/pyproject.toml

```
File /tmp/saml-integrator-L3-sonnet/pyproject.toml updated with changes.
```


---

<sub>⏱️ 4m 37s</sub>

### 💬 Copilot

Now update the lock file:

---

<sub>⏱️ 4m 37s</sub>

### ✅ `sql`

**Mark lockfile todo in progress**

<details>
<summary>Arguments</summary>

```json
{
  "description": "Mark lockfile todo in progress",
  "query": "UPDATE todos SET status = 'in_progress' WHERE id = 'update-lockfile';"
}
```

</details>

```
1 row(s) updated.
```


---

<sub>⏱️ 4m 38s</sub>

### ✅ `bash`

**Regenerate uv.lock**

$ cd /tmp/saml-integrator-L3-sonnet && uv lock 2>&1 | tail -20

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

<sub>⏱️ 4m 44s</sub>

### 💬 Copilot

The lock file was regenerated successfully, removing `pytest-asyncio`, `pytest-operator` and many of their transitive dependencies, and adding `pytest-jubilant`. Now let me mark all todos done and verify the final state:

---

<sub>⏱️ 4m 44s</sub>

### ✅ `sql`

**Mark all todos done**

<details>
<summary>Arguments</summary>

```json
{
  "description": "Mark all todos done",
  "query": "UPDATE todos SET status = 'done' WHERE status = 'in_progress';"
}
```

</details>

```
5 row(s) updated.
```


---

<sub>⏱️ 4m 44s</sub>

### ✅ `bash`

**Show changed files**

$ cd /tmp/saml-integrator-L3-sonnet && git --no-pager diff --stat HEAD

<details>
<summary>6 lines</summary>

```
pyproject.toml                  |   9 +-
 tests/integration/conftest.py   |  39 ++--
 tests/integration/test_charm.py |  39 ++--
 uv.lock                         | 825 ++------------------------------------------------------------------------------
 4 files changed, 51 insertions(+), 861 deletions(-)
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 4m 49s</sub>

### ✅ `bash`

**Show final diff**

$ cd /tmp/saml-integrator-L3-sonnet && git --no-pager diff HEAD -- pyproject.toml tests/integration/conftest.py tests/integration/test_charm.py

<details>
<summary>156 lines</summary>

```diff
diff --git a/pyproject.toml b/pyproject.toml
index 59170c2..92dce70 100644
--- a/pyproject.toml
+++ b/pyproject.toml
@@ -28,12 +28,12 @@ fmt = [
 ]
 lint = [
   "codespell",
+  "jubilant",
   "mypy",
   "ops-scenario",
   "pep8-naming",
   "pytest",
-  "pytest-asyncio",
-  "pytest-operator",
+  "pytest-jubilant",
   "requests",
   "ruff",
   "types-mock",
@@ -59,10 +59,9 @@ interface = [
 integration = [
   "allure-pytest>=2.8.18",
   "allure-pytest-collection-report @ git+https://github.com/canonical/data-platform-workflows@v24.0.0#subdirectory=python/pytest_plugins/allure_pytest_collection_report",
-  "juju",
+  "jubilant",
   "pytest",
-  "pytest-asyncio",
-  "pytest-operator",
+  "pytest-jubilant",
 ]
 
 [tool.uv]
diff --git a/tests/integration/conftest.py b/tests/integration/conftest.py
index e933368..6043eab 100644
--- a/tests/integration/conftest.py
+++ b/tests/integration/conftest.py
@@ -6,40 +6,34 @@
 import json
 from pathlib import Path
 
-import pytest_asyncio
+import jubilant
+import pytest_jubilant
 import yaml
 from pytest import Config, fixture
-from pytest_operator.plugin import OpsTest
 
 
 @fixture(scope="module", name="app_name")
 def app_name_fixture():
     """Provide app name from the metadata."""
     metadata = yaml.safe_load(Path("./metadata.yaml").read_text("utf-8"))
-    yield metadata["name"]
+    return metadata["name"]
 
 
-@pytest_asyncio.fixture(scope="module")
-async def app(ops_test: OpsTest, pytestconfig: Config, app_name: str):
-    """SAML Integrator charm used for integration testing.
+@fixture(scope="module")
+def app(juju: jubilant.Juju, pytestconfig: Config, app_name: str) -> str:
+    """Deploy the SAML Integrator charm for integration testing.
 
-    Build the charm and deploy it along with Anycharm.
+    Uses the charm file passed via --charm-file, or packs the charm automatically.
     """
     charm = pytestconfig.getoption("--charm-file")
-    assert ops_test.model
-    application = await ops_test.model.deploy(
-        f"./{charm}",
-        application_name=app_name,
-    )
-    yield application
-
+    charm_path = Path(charm) if charm else pytest_jubilant.pack()
+    juju.deploy(charm_path, app_name)
+    return app_name
 
-@pytest_asyncio.fixture(scope="module")
-async def any_charm(ops_test: OpsTest):
-    """SAML Integrator charm used for integration testing.
 
-    Build the charm and deploy it along with Anycharm.
-    """
+@fixture(scope="module")
+def any_charm(juju: jubilant.Juju) -> str:
+    """Deploy any-charm for integration testing of the SAML relation."""
     path_lib = "lib/charms/saml_integrator/v0/saml.py"
     saml_lib = Path(path_lib).read_text(encoding="utf8")
     any_charm_script = Path("tests/integration/any_charm.py").read_text(encoding="utf8")
@@ -47,11 +41,10 @@ async def any_charm(ops_test: OpsTest):
         "saml.py": saml_lib,
         "any_charm.py": any_charm_script,
     }
-    assert ops_test.model
-    application = await ops_test.model.deploy(
+    juju.deploy(
         "any-charm",
-        application_name="any",
+        "any",
         channel="beta",
         config={"python-packages": "pydantic>=2.12.5", "src-overwrite": json.dumps(src_overwrite)},
     )
-    yield application
+    return "any"
diff --git a/tests/integration/test_charm.py b/tests/integration/test_charm.py
index de64441..421b842 100644
--- a/tests/integration/test_charm.py
+++ b/tests/integration/test_charm.py
@@ -4,48 +4,37 @@
 
 """SAML Integrator charm integration tests."""
 
-import ops
-import pytest
-from pytest_operator.plugin import OpsTest
+import jubilant
 
 
-@pytest.mark.asyncio
-@pytest.mark.abort_on_fail
-async def test_active(ops_test: OpsTest, app: ops.Application):
+def test_active(juju: jubilant.Juju, app: str):
     """Check that the charm is active.
 
-    Assume that the charm has already been built and is running.
+    Assume that the charm has already been deployed and is running.
     """
-    await app.set_config(  # type: ignore[attr-defined]
+    juju.config(
+        app,
         {
             "entity_id": "https://login.staging.ubuntu.com",
             "fingerprint": "",
             "metadata_url": "https://login.staging.ubuntu.com/saml/metadata",
-        }
+        },
     )
-    status_name = ops.ActiveStatus.name  # type: ignore[has-type]
-    assert ops_test.model
-    await ops_test.model.wait_for_idle(status=status_name, raise_on_error=True)
-    assert app.units[0].workload_status == status_name  # type: ignore
+    juju.wait(jubilant.all_active)
 
 
-@pytest.mark.asyncio
-@pytest.mark.abort_on_fail
-async def test_relation(ops_test: OpsTest, app: ops.Application, any_charm: ops.Application):
+def test_relation(juju: jubilant.Juju, app: str, any_charm: str):
     """Check that the charm is active once related to another charm.
 
-    Assume that the charm has already been built and is running.
+    Assume that the charm has already been deployed and is running.
     """
-    relation_name = f"{app.name}:saml"
-    assert ops_test.model
-    await ops_test.model.add_relation(f"{any_charm.name}:require-saml", relation_name)
-    await app.set_config(  # type: ignore[attr-defined]
+    juju.integrate(f"{any_charm}:require-saml", f"{app}:saml")
+    juju.config(
+        app,
         {
             "entity_id": "https://login.staging.ubuntu.com",
             "fingerprint": "",
             "metadata_url": "https://login.staging.ubuntu.com/saml/metadata",
-        }
+        },
     )
-    status_name = ops.ActiveStatus.name  # type: ignore[has-type]
-    await ops_test.model.wait_for_idle(status=status_name, raise_on_error=True)
-    assert app.units[0].workload_status == status_name  # type: ignore
+    juju.wait(jubilant.all_active)
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 5m 0s</sub>

### 💬 Copilot

Now let's commit:

---

<sub>⏱️ 5m 1s</sub>

### ✅ `bash`

**Commit the migration**

$ cd /tmp/saml-integrator-L3-sonnet && git add pyproject.toml tests/integration/conftest.py tests/integration/test_charm.py uv.lock && git commit -m "Migrate integration tests from pytest-operator to jubilant

Replace python-libjuju/pytest-operator async tests with synchronous
jubilant/pytest-jubilant equivalents:

- tests/integration/conftest.py: Remove pytest_asyncio/OpsTest; use
  jubilant.Juju fixture from pytest-jubilant. Fixtures app and any_charm
  are now sync, return app name strings, and call juju.deploy(). The app
  fixture auto-packs the charm via pytest_jubilant.pack() when no
  --charm-file is provided.

- tests/integration/test_charm.py: Remove async/await,
  @pytest.mark.asyncio, @pytest.mark.abort_on_fail, and ops/OpsTest
  imports. Replace app.set_config() with juju.config(), model.wait_for_idle
  with juju.wait(jubilant.all_active), and model.add_relation with
  juju.integrate().

- pyproject.toml: In both lint and integration dependency groups, replace
  juju, pytest-asyncio, pytest-operator with jubilant and pytest-jubilant.

- uv.lock: Regenerated to reflect dependency changes.

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

<sub>⏱️ 5m 10s</sub>

### ✅ `bash`

**Commit with git config**

$ cd /tmp/saml-integrator-L3-sonnet && git config user.email "copilot@github.com" && git config user.name "Copilot" && git commit -m "Migrate integration tests from pytest-operator to jubilant

Replace python-libjuju/pytest-operator async tests with synchronous
jubilant/pytest-jubilant equivalents:

- tests/integration/conftest.py: Remove pytest_asyncio/OpsTest; use
  jubilant.Juju fixture from pytest-jubilant. Fixtures app and any_charm
  are now sync, return app name strings, and call juju.deploy(). The app
  fixture auto-packs the charm via pytest_jubilant.pack() when no
  --charm-file is provided.

- tests/integration/test_charm.py: Remove async/await,
  @pytest.mark.asyncio, @pytest.mark.abort_on_fail, and ops/OpsTest
  imports. Replace app.set_config() with juju.config(), model.wait_for_idle
  with juju.wait(jubilant.all_active), and model.add_relation with
  juju.integrate().

- pyproject.toml: In both lint and integration dependency groups, replace
  juju, pytest-asyncio, pytest-operator with jubilant and pytest-jubilant.

- uv.lock: Regenerated to reflect dependency changes.

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"

```
[main 1c038e2] Migrate integration tests from pytest-operator to jubilant
 4 files changed, 51 insertions(+), 861 deletions(-)
<exited with exit code 0>
```


---

<sub>⏱️ 5m 19s</sub>

### 💬 Copilot

Migration complete. Here's a summary of all changes:

**`tests/integration/test_charm.py`** — Removed `async`/`await`, `@pytest.mark.asyncio`, `@pytest.mark.abort_on_fail`, and `ops`/`OpsTest` imports. Replaced `app.set_config()` → `juju.config(app, {...})`, `model.wait_for_idle()` → `juju.wait(jubilant.all_active)`, and `model.add_relation()` → `juju.integrate()`. App args are now `str` (app names) instead of `ops.Application` objects.

**`tests/integration/conftest.py`** — Removed `pytest_asyncio` and `OpsTest`. The `app` and `any_charm` fixtures are now sync, accept the `juju: jubilant.Juju` fixture from pytest-jubilant, call `juju.deploy()`, and return app name strings. The `app` fixture auto-packs via `pytest_jubilant.pack()` when `--charm-file` isn't provided.

**`pyproject.toml`** — In both `lint` and `integration` dependency groups: removed `juju` (python-libjuju), `pytest-asyncio`, `pytest-operator`; added `jubilant` and `pytest-jubilant`.

**`uv.lock`** — Regenerated, dropping ~50 transitive dependencies from the old async stack (websockets, macaroons, pyasn1, traitlets, etc.).

---

<sub>Generated by [GitHub Copilot CLI](https://github.com/features/copilot/cli)</sub>
