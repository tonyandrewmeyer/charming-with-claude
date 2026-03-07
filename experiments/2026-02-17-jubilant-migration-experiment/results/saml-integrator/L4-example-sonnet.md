# 🤖 Copilot CLI Session

> **Session ID:** `57f832b4-e476-4fb0-a0d3-321f9931aef9`
> **Started:** 3/7/2026, 12:10:55 PM
> **Duration:** 10m 8s
> **Exported:** 3/7/2026, 12:21:03 PM

<sub>⏱️ 5s</sub>

### 👤 User

Migrate this charm's integration tests from pytest-operator (python-libjuju) to jubilant and pytest-jubilant. Update all test files, conftest.py, and dependencies.

For a working example of what jubilant integration tests look like, clone https://github.com/canonical/wordpress-k8s-operator and study its tests/integration/ directory. Pay attention to how conftest.py sets up the juju fixture, how tests use juju.deploy(), juju.wait(), juju.integrate(), and how pytest-jubilant's pack() and get_resources() are used.

---

<sub>⏱️ 14s</sub>

### 📦 task (Completed)

### ✅ `glob`

**/tmp/saml-integrator-L4-sonnet**

"**/tests/integration/**/*.py" in /tmp/saml-integrator-L4-sonnet

```
/tmp/saml-integrator-L4-sonnet/tests/integration/__init__.py
/tmp/saml-integrator-L4-sonnet/tests/integration/any_charm.py
/tmp/saml-integrator-L4-sonnet/tests/integration/test_charm.py
/tmp/saml-integrator-L4-sonnet/tests/integration/conftest.py
```


### ✅ `glob`

**/tmp/saml-integrator-L4-sonnet**

"**/pyproject.toml" in /tmp/saml-integrator-L4-sonnet

```
/tmp/saml-integrator-L4-sonnet/pyproject.toml
```


### ✅ `glob`

**/tmp/saml-integrator-L4-sonnet**

"**/tox.ini" in /tmp/saml-integrator-L4-sonnet

```
No files matched the pattern.
```


### ✅ `glob`

**/tmp/saml-integrator-L4-sonnet**

"**/Makefile" in /tmp/saml-integrator-L4-sonnet

```
/tmp/saml-integrator-L4-sonnet/Makefile
```


### ✅ `glob`

**/tmp/saml-integrator-L4-sonnet**

"**/metadata.yaml" in /tmp/saml-integrator-L4-sonnet

```
/tmp/saml-integrator-L4-sonnet/metadata.yaml
```


### ✅ `glob`

**/tmp/saml-integrator-L4-sonnet**

"**/charmcraft.yaml" in /tmp/saml-integrator-L4-sonnet

```
/tmp/saml-integrator-L4-sonnet/charmcraft.yaml
```


### ✅ `view`

**/tmp/saml-integrator-L4-sonnet/tests/integration**

/tmp/saml-integrator-L4-sonnet/tests/integration

```
__init__.py
any_charm.py
conftest.py
test_charm.py
```


### 💬 Copilot

Now let me view all the test files and related configuration files in parallel:

### ✅ `view`

**/tmp/saml-integrator-L4-sonnet/tests/integration/conftest.py**

/tmp/saml-integrator-L4-sonnet/tests/integration/conftest.py

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

**/tmp/saml-integrator-L4-sonnet/tests/integration/test_charm.py**

/tmp/saml-integrator-L4-sonnet/tests/integration/test_charm.py

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

**/tmp/saml-integrator-L4-sonnet/tests/integration/any_charm.py**

/tmp/saml-integrator-L4-sonnet/tests/integration/any_charm.py

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

**/tmp/saml-integrator-L4-sonnet/tests/integration/__init__.py**

/tmp/saml-integrator-L4-sonnet/tests/integration/__init__.py

```
1. # Copyright 2025 Canonical Ltd.
2. # See LICENSE file for licensing details.
3. 
```


### ✅ `view`

**/tmp/saml-integrator-L4-sonnet/pyproject.toml**

/tmp/saml-integrator-L4-sonnet/pyproject.toml

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

**/tmp/saml-integrator-L4-sonnet/Makefile**

/tmp/saml-integrator-L4-sonnet/Makefile

<details>
<summary>42 lines</summary>

```
1. # Copyright 2025 Canonical Ltd.
2. # See LICENSE file for licensing details.
3. 
4. # Top-level Makefile
5. # Delegates targets to Makefile.docs
6. 
7. # ==============================================================================
8. # Macros
9. # ==============================================================================
10. 
11. # Colors
12. NO_COLOR=\033[0m
13. CYAN_COLOR=\033[0;36m
14. YELLOW_COLOR=\033[0;93m
15. RED_COLOR=\033[0;91m
16. 
17. msg = @printf '$(CYAN_COLOR)$(1)$(NO_COLOR)\n'
18. errmsg = @printf '$(RED_COLOR)Error: $(1)$(NO_COLOR)\n' && exit 1
19. 
20. # ==============================================================================
21. # Core
22. # ==============================================================================
23. 
24. include Makefile.docs
25. 
26. .PHONY: help 
27. help: _list-targets ## Prints all available targets
28. 
29. .PHONY: _list-targets
30. _list-targets: ## This collects and prints all targets, ignore internal commands
31. 	$(call msg,Available targets:)
32. 	@awk -F'[:#]' '                                               \
33. 		/^[a-zA-Z0-9._-]+:([^=]|$$)/ {                            \
34. 			target = $$1;                                         \
35. 			comment = "";                                         \
36. 			if (match($$0, /## .*/))                              \
37. 				comment = substr($$0, RSTART + 3);                \
38. 			if (target != ".PHONY" && target !~ /^_/ && !seen[target]++) \
39. 				printf "  make %-20s $(YELLOW_COLOR)# %s$(NO_COLOR)\n", target, comment;    \
40. 		}' $(MAKEFILE_LIST) | sort
41. 
42.
```

</details>


### ✅ `view`

**/tmp/saml-integrator-L4-sonnet/metadata.yaml**

/tmp/saml-integrator-L4-sonnet/metadata.yaml

<details>
<summary>32 lines</summary>

```
1. # Copyright 2025 Canonical Ltd.
2. # See LICENSE file for licensing details.
3. 
4. name: saml-integrator
5. display-name: SAML Integrator
6. summary: SAML Integrator to abstract SAML IdP details.
7. description: |
8.   A [Juju](https://juju.is/) [charm](https://juju.is/docs/olm/charmed-operators)
9.   deploying and managing a SAML Integrator on Kubernetes and bare metal. SAML is an XML-based
10.   open-standard for transferring identity data between two parties: an identity
11.   provider (IdP) and a service provider (SP).
12. 
13.   This charm simplifies configuration of SAML SPs by providing a single point
14.   of configuration for all the requirers using the same SAML entity. It can be
15.   deployed on many different Kubernetes platforms, from [MicroK8s](https://microk8s.io)
16.   to [Charmed Kubernetes](https://ubuntu.com/kubernetes) and public cloud Kubernetes
17.   offerings.
18. 
19.   As such, the charm makes it easy to manage and propagate SAML configuration, while
20.   giving the freedom to deploy on the Kubernetes platform of their choice.
21. 
22.   For DevOps or SRE teams this charm will make operating any charm leveraging SAML
23.   authentication simple and straightforward through Juju's clean interface.
24. docs: https://discourse.charmhub.io/t/saml-integrator-documentation-overview/11293
25. issues: https://github.com/canonical/saml-integrator-operator/issues
26. maintainers:
27.   - https://launchpad.net/~canonical-is-devops
28. source: https://github.com/canonical/saml-integrator-operator
29. provides:
30.   saml:
31.     interface: saml
32.
```

</details>


### ✅ `view`

**/tmp/saml-integrator-L4-sonnet/charmcraft.yaml**

/tmp/saml-integrator-L4-sonnet/charmcraft.yaml

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

Now let me check if there's a Makefile.docs since it's included in the main Makefile:

### ✅ `glob`

**/tmp/saml-integrator-L4-sonnet**

"**/Makefile.docs" in /tmp/saml-integrator-L4-sonnet

```
/tmp/saml-integrator-L4-sonnet/Makefile.docs
```


### ✅ `view`

**/tmp/saml-integrator-L4-sonnet/Makefile.docs**

/tmp/saml-integrator-L4-sonnet/Makefile.docs

<details>
<summary>76 lines</summary>

```
1. # Copyright 2025 Canonical Ltd.
2. # See LICENSE file for licensing details.
3. 
4. # Minimal makefile for documentation
5. #
6. 
7. # Vale settings
8. VALE_DIR ?= .vale
9. PRAECEPTA_CONFIG 	?= .vale.ini
10. DOCS_FILES 	?= docs/ README.md CONTRIBUTING.md
11. 
12. HAS_VALE			:= $(shell command -v vale;)
13. HAS_LYCHEE			:= $(shell command -v lychee;)
14. 
15. # ==============================================================================
16. # Docs Targets
17. # ==============================================================================
18. 
19. .PHONY: docs-check
20. docs-check: vale lychee ## Run all Docs checks
21. 
22. .PHONY: docs-clean
23. docs-clean: vale-clean
24. 
25. # ==============================================================================
26. # Dependency Check Targets
27. # ==============================================================================
28. 
29. .PHONY: .check-vale
30. .check-vale:
31. ifndef HAS_VALE
32. 	$(call errmsg,'vale' is not installed. Please install it first) \
33. 	exit 1;
34. endif
35. 
36. .PHONY: .check-lychee
37. .check-lychee:
38. ifndef HAS_LYCHEE
39. 	$(call errmsg,'lychee' is not installed. Please install it first) \
40. 	exit 1;
41. endif
42. 
43. 
44. # ==============================================================================
45. # Main Vale Targets
46. # ==============================================================================
47. 
48. .PHONY: vale-sync
49. vale-sync: ## Download and install external Vale configuration sources
50. 	$(call msg,--- Syncing Vale styles... ---)
51. 	@vale sync
52. 
53. .PHONY: vale
54. vale: .check-vale vale-sync ## Run Vale checks on docs
55. 	$(call msg,--- Running Vale checks on "$(DOCS_FILES)"... ---)
56. 	@vale --config=$(PRAECEPTA_CONFIG) $(DOCS_FILES)
57. 
58. # ==============================================================================
59. # Main Lychee Targets
60. # ==============================================================================
61. 
62. .PHONY: lychee
63. lychee: .check-lychee ## Run Lychee checks on docs
64. 	$(call msg,--- Running lychee checks on "$(LYCHEE_DOCS_FILES)"... ---)
65. 	@lychee $(DOCS_FILES)
66. 
67. # ==============================================================================
68. # Helper Targets
69. # ==============================================================================
70. 
71. .PHONY: vale-clean
72. vale-clean:
73. 	$(call msg,--- Cleaning downloaded packages and ignored files from "$(VALE_DIR)"... ---)
74. 	@git clean -dfX $(VALE_DIR)
75. 
76.
```

</details>


### 💬 Copilot

Perfect! Now I have all the information. Let me compile this into a comprehensive response. Let me also check if there are any other test-related Makefiles:

### ✅ `bash`

**Find all Makefiles**

$ find /tmp/saml-integrator-L4-sonnet -name "Makefile*" -type f

```
/tmp/saml-integrator-L4-sonnet/Makefile
/tmp/saml-integrator-L4-sonnet/Makefile.docs
<exited with exit code 0>
```


### 💬 Copilot

Let me check if there's a Makefile.test or any other build-related files in the repo:

### ✅ `bash`

**List all regular files in root**

$ ls -la /tmp/saml-integrator-L4-sonnet/ | grep -E "^-" | head -30

<details>
<summary>21 lines</summary>

```
-rw-rw-r--  1 ubuntu ubuntu    362 Mar  7 11:58 .gitignore
-rw-rw-r--  1 ubuntu ubuntu     33 Mar  7 11:58 .jujuignore
-rw-rw-r--  1 ubuntu ubuntu    696 Mar  7 11:58 .licenserc.yaml
-rw-rw-r--  1 ubuntu ubuntu    260 Mar  7 11:58 .vale.ini
-rw-rw-r--  1 ubuntu ubuntu    320 Mar  7 11:58 .woke.yaml
-rw-rw-r--  1 ubuntu ubuntu    221 Mar  7 11:58 CHANGELOG.md
-rw-rw-r--  1 ubuntu ubuntu     40 Mar  7 11:58 CODEOWNERS
-rw-rw-r--  1 ubuntu ubuntu   6744 Mar  7 11:58 CONTRIBUTING.md
-rw-rw-r--  1 ubuntu ubuntu  11357 Mar  7 11:58 LICENSE
-rw-rw-r--  1 ubuntu ubuntu   1447 Mar  7 11:58 Makefile
-rw-rw-r--  1 ubuntu ubuntu   2253 Mar  7 11:58 Makefile.docs
-rw-rw-r--  1 ubuntu ubuntu   1904 Mar  7 11:58 README.md
-rw-rw-r--  1 ubuntu ubuntu   1089 Mar  7 11:58 SECURITY.md
-rw-rw-r--  1 ubuntu ubuntu    394 Mar  7 11:58 charmcraft.yaml
-rw-rw-r--  1 ubuntu ubuntu    613 Mar  7 11:58 config.yaml
-rw-rw-r--  1 ubuntu ubuntu   1475 Mar  7 11:58 metadata.yaml
-rw-rw-r--  1 ubuntu ubuntu   3042 Mar  7 11:58 pyproject.toml
-rw-rw-r--  1 ubuntu ubuntu    976 Mar  7 11:58 renovate.json
-rw-rw-r--  1 ubuntu ubuntu   3271 Mar  7 11:58 tox.toml
-rw-rw-r--  1 ubuntu ubuntu 374104 Mar  7 11:58 uv.lock
<exited with exit code 0>
```

</details>


### 💬 Copilot

Great! I found `tox.toml`. Let me view it:

### ✅ `view`

**/tmp/saml-integrator-L4-sonnet/tox.toml**

/tmp/saml-integrator-L4-sonnet/tox.toml

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

Perfect! Now I have all the information. Let me provide a comprehensive summary:

---

## Integration Tests Exploration

### 1. **Integration Test Files**

#### `/tmp/saml-integrator-L4-sonnet/tests/integration/conftest.py`
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

#### `/tmp/saml-integrator-L4-sonnet/tests/integration/test_charm.py`
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

#### `/tmp/saml-integrator-L4-sonnet/tests/integration/any_charm.py`
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

#### `/tmp/saml-integrator-L4-sonnet/tests/integration/__init__.py`
```python
# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.
```

---

### 2. **Testing Dependencies in `pyproject.toml`**

```toml
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
```

---

### 3. **`tox.toml` - Complete File**

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

### 4. **Makefile Content**

#### `/tmp/saml-integrator-L4-sonnet/Makefile`
```makefile
# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

# Top-level Makefile
# Delegates targets to Makefile.docs

# ==============================================================================
# Macros
# ==============================================================================

# Colors
NO_COLOR=\033[0m
CYAN_COLOR=\033[0;36m
YELLOW_COLOR=\033[0;93m
RED_COLOR=\033[0;91m

msg = @printf '$(CYAN_COLOR)$(1)$(NO_COLOR)\n'
errmsg = @printf '$(RED_COLOR)Error: $(1)$(NO_COLOR)\n' && exit 1

# ==============================================================================
# Core
# ==============================================================================

include Makefile.docs

.PHONY: help 
help: _list-targets ## Prints all available targets

.PHONY: _list-targets
_list-targets: ## This collects and prints all targets, ignore internal commands
	$(call msg,Available targets:)
	@awk -F'[:#]' '                                               \
		/^[a-zA-Z0-9._-]+:([^=]|$$)/ {                            \
			target = $$1;                                         \
			comment = "";                                         \
			if (match($$0, /## .*/))                              \
				comment = substr($$0, RSTART + 3);                \
			if (target != ".PHONY" && target !~ /^_/ && !seen[target]++) \
				printf "  make %-20s $(YELLOW_COLOR)# %s$(NO_COLOR)\n", target, comment;    \
		}' $(MAKEFILE_LIST) | sort
```

#### `/tmp/saml-integrator-L4-sonnet/Makefile.docs`
```makefile
# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

# Minimal makefile for documentation
#

# Vale settings
VALE_DIR ?= .vale
PRAECEPTA_CONFIG 	?= .vale.ini
DOCS_FILES 	?= docs/ README.md CONTRIBUTING.md

HAS_VALE			:= $(shell command -v vale;)
HAS_LYCHEE			:= $(shell command -v lychee;)

# ==============================================================================
# Docs Targets
# ==============================================================================

.PHONY: docs-check
docs-check: vale lychee ## Run all Docs checks

.PHONY: docs-clean
docs-clean: vale-clean

# ==============================================================================
# Dependency Check Targets
# ==============================================================================

.PHONY: .check-vale
.check-vale:
ifndef HAS_VALE
	$(call errmsg,'vale' is not installed. Please install it first) \
	exit 1;
endif

.PHONY: .check-lychee
.check-lychee:
ifndef HAS_LYCHEE
	$(call errmsg,'lychee' is not installed. Please install it first) \
	exit 1;
endif


# ==============================================================================
# Main Vale Targets
# ==============================================================================

.PHONY: vale-sync
vale-sync: ## Download and install external Vale configuration sources
	$(call msg,--- Syncing Vale styles... ---)
	@vale sync

.PHONY: vale
vale: .check-vale vale-sync ## Run Vale checks on docs
	$(call msg,--- Running Vale checks on "$(DOCS_FILES)"... ---)
	@vale --config=$(PRAECEPTA_CONFIG) $(DOCS_FILES)

# ==============================================================================
# Main Lychee Targets
# ==============================================================================

.PHONY: lychee
lychee: .check-lychee ## Run Lychee checks on docs
	$(call msg,--- Running lychee checks on "$(LYCHEE_DOCS_FILES)"... ---)
	@lychee $(DOCS_FILES)

# ==============================================================================
# Helper Targets
# ==============================================================================

.PHONY: vale-clean
vale-clean:
	$(call msg,--- Cleaning downloaded packages and ignored files from "$(VALE_DIR)"... ---)
	@git clean -dfX $(VALE_DIR)
```

---

### 5. **Charm Metadata**

#### `/tmp/saml-integrator-L4-sonnet/metadata.yaml`
```yaml
# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

name: saml-integrator
display-name: SAML Integrator
summary: SAML Integrator to abstract SAML IdP details.
description: |
  A [Juju](https://juju.is/) [charm](https://juju.is/docs/olm/charmed-operators)
  deploying and managing a SAML Integrator on Kubernetes and bare metal. SAML is an XML-based
  open-standard for transferring identity data between two parties: an identity
  provider (IdP) and a service provider (SP).

  This charm simplifies configuration of SAML SPs by providing a single point
  of configuration for all the requirers using the same SAML entity. It can be
  deployed on many different Kubernetes platforms, from [MicroK8s](https://microk8s.io)
  to [Charmed Kubernetes](https://ubuntu.com/kubernetes) and public cloud Kubernetes
  offerings.

  As such, the charm makes it easy to manage and propagate SAML configuration, while
  giving the freedom to deploy on the Kubernetes platform of their choice.

  For DevOps or SRE teams this charm will make operating any charm leveraging SAML
  authentication simple and straightforward through Juju's clean interface.
docs: https://discourse.charmhub.io/t/saml-integrator-documentation-overview/11293
issues: https://github.com/canonical/saml-integrator-operator/issues
maintainers:
  - https://launchpad.net/~canonical-is-devops
source: https://github.com/canonical/saml-integrator-operator
provides:
  saml:
    interface: saml
```

#### `/tmp/saml-integrator-L4-sonnet/charmcraft.yaml`
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

## Summary

**What this charm does:**
- The SAML Integrator is a Juju charm that manages SAML (Security Assertion Markup Language) configuration for identity providers and service providers
- Provides a centralized point of configuration for multiple charms that require SAML authentication
- Works on Kubernetes (MicroK8s, Charmed Kubernetes, public cloud) and bare metal

**Integration Tests:**
- **2 test functions**: `test_active` and `test_relation`
- **Fixtures**: `app` (SAML Integrator charm), `any_charm` (test charm with SAML requires relation), `app_name` (from metadata)
- **Test approach**: Uses pytest-operator for async testing with Juju models
- Tests deployment, configuration, and relation functionality

**Key test dependencies** (from pyproject.toml):
- `pytest`, `pytest-asyncio`, `pytest-operator` 
- `allure-pytest`, `juju`
- `pydantic\>=2.12.5` for validation

**Running tests** (from tox.toml):
- `tox -e integration` - Runs integration tests excluding unit and interface tests
- Uses pytest with verbose output and native tracebacks


---

<sub>⏱️ 16s</sub>

### ✅ `bash`

**Clone WordPress operator for reference**

$ cd /tmp/saml-integrator-L4-sonnet && git clone https://github.com/canonical/wordpress-k8s-operator /tmp/wordpress-k8s-operator --depth=1 2>&1 | tail -5

```
Cloning into '/tmp/wordpress-k8s-operator'...
<exited with exit code 0>
```


---

<sub>⏱️ 1m 20s</sub>

### 📦 task (Completed)

### 💬 Copilot

I'll explore the integration tests directory and gather all the relevant files for you. Let me start by examining the directory structure and then read all the relevant files in parallel.

### ✅ `view`

**/tmp/wordpress-k8s-operator/tests/integration**

/tmp/wordpress-k8s-operator/tests/integration

<details>
<summary>12 lines</summary>

```
conftest.py
helper.py
pre_run_script.sh
pre_run_script_juju3.sh
test_addon.py
test_core.py
test_cos_grafana.py
test_cos_loki.py
test_cos_prometheus.py
test_external.py
test_ingress.py
test_machine.py
```

</details>


### 💬 Copilot

Now let me read all the test files and conftest in parallel:

### ✅ `view`

**/tmp/wordpress-k8s-operator/tests/integration/conftest.py**

/tmp/wordpress-k8s-operator/tests/integration/conftest.py

<details>
<summary>241 lines</summary>

```
1. # Copyright 2024 Canonical Ltd.
2. # See LICENSE file for licensing details.
3. 
4. """Fixtures for the wordpress integration tests."""
5. 
6. import configparser
7. import json
8. import re
9. import secrets
10. from pathlib import Path
11. from typing import AsyncGenerator, Dict, Optional
12. 
13. import pytest
14. import pytest_asyncio
15. import swiftclient
16. import swiftclient.exceptions
17. import swiftclient.service
18. from juju.controller import Controller
19. from juju.model import Model
20. from pytest import Config
21. from pytest_operator.plugin import OpsTest
22. 
23. from tests.integration.helper import WordpressApp
24. 
25. 
26. @pytest.fixture(scope="module")
27. def model(ops_test: OpsTest) -> Model:
28.     """Return the juju model object created by pytest-operator."""
29.     model = ops_test.model
30.     assert model
31.     return model
32. 
33. 
34. @pytest.fixture(scope="module", name="kube_config")
35. def kube_config_fixture(pytestconfig: Config):
36.     """The Kubernetes cluster configuration file."""
37.     kube_config = pytestconfig.getoption("--kube-config")
38.     assert kube_config, (
39.         "The Kubernetes config file path should not be empty, "
40.         "please include it in the --kube-config parameter"
41.     )
42.     return kube_config
43. 
44. 
45. @pytest_asyncio.fixture(scope="module", name="machine_controller")
46. async def machine_controller_fixture() -> AsyncGenerator[Controller, None]:
47.     """The lxd controller."""
48.     controller = Controller()
49.     await controller.connect_controller("localhost")
50. 
51.     yield controller
52. 
53.     await controller.disconnect()
54. 
55. 
56. @pytest_asyncio.fixture(scope="module", name="machine_model")
57. async def machine_model_fixture(machine_controller: Controller) -> AsyncGenerator[Model, None]:
58.     """The machine model for jenkins agent machine charm."""
59.     machine_model_name = f"mysql-machine-{secrets.token_hex(2)}"
60.     model = await machine_controller.add_model(machine_model_name)
61. 
62.     yield model
63. 
64.     await model.disconnect()
65. 
66. 
67. @pytest_asyncio.fixture(scope="module", name="wordpress")
68. async def wordpress_fixture(
69.     pytestconfig: Config, ops_test: OpsTest, model: Model, kube_config: str
70. ) -> WordpressApp:
71.     """Prepare the wordpress charm for integration tests."""
72.     exit_code, _, _ = await ops_test.juju("model-config", "logging-config=<root>=INFO;unit=DEBUG")
73.     assert exit_code == 0
74.     charm = pytestconfig.getoption("--charm-file")
75.     charm_dir = Path(__file__).parent.parent.parent
76.     if not charm:
77.         charm = await ops_test.build_charm(charm_dir)
78.     else:
79.         charm = Path(charm).absolute()
80.     wordpress_image = pytestconfig.getoption("--wordpress-image")
81.     if not wordpress_image:
82.         raise ValueError("--wordpress-image is required to run integration test")
83.     app = await model.deploy(
84.         charm,
85.         resources={
86.             "wordpress-image": wordpress_image,
87.         },
88.         num_units=1,
89.         series="jammy",
90.     )
91.     await model.wait_for_idle(status="blocked", apps=[app.name], timeout=30 * 60)
92.     return WordpressApp(app, ops_test=ops_test, kube_config=kube_config)
93. 
94. 
95. @pytest_asyncio.fixture(scope="module")
96. async def prepare_mysql(ops_test: OpsTest, wordpress: WordpressApp, model: Model):
97.     """Deploy and relate the mysql-k8s charm for integration tests."""
98.     app = await model.deploy("mysql-k8s", channel="8.0/stable", trust=True)
99.     await model.wait_for_idle(status="active", apps=[app.name], timeout=30 * 60)
100.     await model.relate(f"{wordpress.name}:database", f"{app.name}:database")
101.     await model.wait_for_idle(
102.         status="active", apps=[app.name, wordpress.name], timeout=40 * 60, idle_period=30
103.     )
104. 
105. 
106. @pytest_asyncio.fixture(scope="module")
107. async def prepare_machine_mysql(
108.     wordpress: WordpressApp, machine_controller: Controller, machine_model: Model, model: Model
109. ):
110.     """Deploy and relate the mysql-k8s charm for integration tests."""
111.     await machine_model.deploy("mysql", channel="8.0/edge", trust=True)
112.     await machine_model.create_offer("mysql:database")
113.     await machine_model.wait_for_idle(status="active", apps=["mysql"], timeout=30 * 60)
114.     await model.relate(
115.         f"{wordpress.name}:database",
116.         f"{machine_controller.controller_name}:admin/{machine_model.name}.mysql",
117.     )
118. 
119. 
120. @pytest.fixture(scope="module", name="openstack_environment")
121. def openstack_environment_fixture(pytestconfig: Config):
122.     """Parse the openstack rc style configuration file from the --openstack-rc argument.
123. 
124.     Returns: a dictionary of environment variables and values, or None if --openstack-rc isn't
125.         provided.
126.     """
127.     rc_file = pytestconfig.getoption("--openstack-rc")
128.     if not rc_file:
129.         raise ValueError("--openstack-rc is required to run this test")
130.     with open(rc_file, encoding="utf-8") as rc_fo:
131.         rc_file = rc_fo.read()
132.     rc_file = re.sub("^export ", "", rc_file, flags=re.MULTILINE)
133.     openstack_conf = configparser.ConfigParser()
134.     openstack_conf.read_string("[DEFAULT]\n" + rc_file)
135.     return {k.upper(): v for k, v in openstack_conf["DEFAULT"].items()}
136. 
137. 
138. @pytest.fixture(scope="module", name="swift_conn")
139. def swift_conn_fixture(openstack_environment) -> Optional[swiftclient.Connection]:
140.     """Create a swift connection client."""
141.     return swiftclient.Connection(
142.         authurl=openstack_environment["OS_AUTH_URL"],
143.         auth_version="3",
144.         user=openstack_environment["OS_USERNAME"],
145.         key=openstack_environment["OS_PASSWORD"],
146.         os_options={
147.             "user_domain_name": openstack_environment["OS_USER_DOMAIN_ID"],
148.             "project_domain_name": openstack_environment["OS_PROJECT_DOMAIN_ID"],
149.             "project_name": openstack_environment["OS_PROJECT_NAME"],
150.         },
151.     )
152. 
153. 
154. @pytest.fixture(scope="module", name="swift_config")
155. def swift_config_fixture(
156.     ops_test: OpsTest,
157.     swift_conn: swiftclient.Connection,
158.     openstack_environment: Dict[str, str],
159. ) -> Dict[str, str]:
160.     """Create a swift config dict that can be used for wp_plugin_openstack-objectstorage_config."""
161.     swift_service = swiftclient.service.SwiftService(
162.         options={
163.             "auth_version": "3",
164.             "os_auth_url": openstack_environment["OS_AUTH_URL"],
165.             "os_username": openstack_environment["OS_USERNAME"],
166.             "os_password": openstack_environment["OS_PASSWORD"],
167.             "os_project_name": openstack_environment["OS_PROJECT_NAME"],
168.             "os_project_domain_name": openstack_environment["OS_PROJECT_DOMAIN_ID"],
169.         }
170.     )
171.     container = f"wordpress_{ops_test.model_name}"
172.     # if the container exists, remove the container
173.     swift_service.delete(container=container)
174.     # create a swift container for our test
175.     swift_conn.put_container(container)
176.     # change container ACL to allow us getting an object by HTTP request without any authentication
177.     # the swift server will act as a static HTTP server after this
178.     swift_service.post(container=container, options={"read_acl": ".r:*,.rlistings"})
179. 
180.     return {
181.         "auth-url": openstack_environment["OS_AUTH_URL"] + "/v3",
182.         "bucket": container,
183.         "password": openstack_environment["OS_PASSWORD"],
184.         "object-prefix": "wp-content/uploads/",
185.         "region": openstack_environment["OS_REGION_NAME"],
186.         "tenant": openstack_environment["OS_PROJECT_NAME"],
187.         "domain": openstack_environment["OS_PROJECT_DOMAIN_ID"],
188.         "swift-url": swift_conn.url,
189.         "username": openstack_environment["OS_USERNAME"],
190.         "copy-to-swift": "1",
191.         "serve-from-swift": "1",
192.         "remove-local-file": "0",
193.     }
194. 
195. 
196. @pytest_asyncio.fixture(scope="module")
197. async def prepare_swift(wordpress: WordpressApp, swift_config: Dict[str, str]):
198.     """Configure the wordpress charm to use openstack swift object storage."""
199.     await wordpress.set_config(
200.         {"wp_plugin_openstack-objectstorage_config": json.dumps(swift_config)}
201.     )
202.     await wordpress.model.wait_for_idle(status="active", apps=[wordpress.name], timeout=30 * 60)
203. 
204. 
205. @pytest_asyncio.fixture(scope="module")
206. async def prepare_nginx_ingress(wordpress: WordpressApp, prepare_mysql):
207.     """Deploy and relate nginx-ingress-integrator charm for integration tests."""
208.     await wordpress.model.deploy(
209.         "nginx-ingress-integrator", channel="latest/edge", series="focal", revision=133, trust=True
210.     )
211.     await wordpress.model.wait_for_idle(apps=["nginx-ingress-integrator"], timeout=30 * 60)
212.     await wordpress.model.relate(f"{wordpress.name}:nginx-route", "nginx-ingress-integrator")
213.     await wordpress.model.wait_for_idle(status="active")
214. 
215. 
216. @pytest_asyncio.fixture(scope="module")
217. async def prepare_prometheus(wordpress: WordpressApp, prepare_mysql):
218.     """Deploy and relate prometheus-k8s charm for integration tests."""
219.     prometheus = await wordpress.model.deploy("prometheus-k8s", channel="1/stable", trust=True)
220.     await wordpress.model.wait_for_idle(
221.         status="active", apps=[prometheus.name], raise_on_error=False, timeout=30 * 60
222.     )
223.     await wordpress.model.relate(f"{wordpress.name}:metrics-endpoint", prometheus.name)
224.     await wordpress.model.wait_for_idle(
225.         status="active",
226.         apps=[prometheus.name, wordpress.name],
227.         timeout=20 * 60,
228.         raise_on_error=False,
229.     )
230. 
231. 
232. @pytest_asyncio.fixture(scope="module")
233. async def prepare_loki(wordpress: WordpressApp, prepare_mysql):
234.     """Deploy and relate loki-k8s charm for integration tests."""
235.     loki = await wordpress.model.deploy("loki-k8s", channel="1/stable", trust=True)
236.     await wordpress.model.wait_for_idle(apps=[loki.name], status="active", timeout=20 * 60)
237.     await wordpress.model.relate(f"{wordpress.name}:logging", loki.name)
238.     await wordpress.model.wait_for_idle(
239.         apps=[loki.name, wordpress.name], status="active", timeout=40 * 60
240.     )
241.
```

</details>


### ✅ `view`

**/tmp/wordpress-k8s-operator/tests/integration/test_addon.py**

/tmp/wordpress-k8s-operator/tests/integration/test_addon.py

<details>
<summary>115 lines</summary>

```
1. # Copyright 2024 Canonical Ltd.
2. # See LICENSE file for licensing details.
3. 
4. """Integration tests for WordPress charm COS addon management."""
5. 
6. from typing import List, Set
7. 
8. import pytest
9. 
10. from charm import WordpressCharm
11. from tests.integration.helper import WordpressApp
12. 
13. 
14. @pytest.mark.usefixtures("prepare_mysql", "prepare_swift")
15. async def test_wordpress_install_uninstall_themes(wordpress: WordpressApp):
16.     """
17.     arrange: after WordPress charm has been deployed and db relation established.
18.     act: change themes setting in config.
19.     assert: themes should be installed and uninstalled accordingly.
20.     """
21.     theme_change_list: List[Set[str]] = [
22.         {"twentyfifteen", "classic"},
23.         {"tt1-blocks", "twentyfifteen"},
24.         {"tt1-blocks"},
25.         {"twentyeleven"},
26.         set(),
27.     ]
28.     for themes in theme_change_list:
29.         await wordpress.set_config({"themes": ",".join(themes)})
30.         await wordpress.model.wait_for_idle(status="active", apps=[wordpress.name])
31. 
32.         for wordpress_client in await wordpress.client_for_units():
33.             expected_themes = themes
34.             expected_themes.update(WordpressCharm._WORDPRESS_DEFAULT_THEMES)
35.             actual_themes = set(wordpress_client.list_themes())
36.             assert expected_themes == actual_themes, (
37.                 f"theme installed {themes} should match themes setting in config"
38.             )
39. 
40. 
41. @pytest.mark.usefixtures("prepare_mysql", "prepare_swift")
42. async def test_wordpress_theme_installation_error(wordpress: WordpressApp):
43.     """
44.     arrange: after WordPress charm has been deployed and db relation established.
45.     act: install a nonexistent theme.
46.     assert: charm should switch to blocked state and the reason should be included in the status
47.         message.
48.     """
49.     invalid_theme = "invalid-theme-sgkeahrgalejr"
50.     await wordpress.set_config({"themes": invalid_theme})
51.     await wordpress.wait_for_wordpress_idle()
52. 
53.     for unit in wordpress.get_units():
54.         assert unit.workload_status == "blocked", (
55.             "status should be 'blocked' since the theme in themes config does not exist"
56.         )
57. 
58.         assert invalid_theme in unit.workload_status_message, (
59.             "status message should contain the reason why it's blocked"
60.         )
61. 
62.     await wordpress.set_config({"themes": ""})
63.     await wordpress.wait_for_wordpress_idle(status="active")
64. 
65. 
66. @pytest.mark.usefixtures("prepare_mysql", "prepare_swift")
67. async def test_wordpress_install_uninstall_plugins(wordpress: WordpressApp):
68.     """
69.     arrange: after WordPress charm has been deployed and db relation established.
70.     act: change plugins setting in config.
71.     assert: plugins should be installed and uninstalled accordingly.
72.     """
73.     plugin_change_list: List[Set[str]] = [
74.         {"classic-editor", "classic-widgets"},
75.         {"classic-editor"},
76.         {"classic-widgets"},
77.         set(),
78.     ]
79.     for plugins in plugin_change_list:
80.         await wordpress.set_config({"plugins": ",".join(plugins)})
81.         await wordpress.wait_for_wordpress_idle(status="active")
82. 
83.         for wordpress_client in await wordpress.client_for_units():
84.             expected_plugins = plugins
85.             expected_plugins.update(WordpressCharm._WORDPRESS_DEFAULT_PLUGINS)
86.             actual_plugins = set(wordpress_client.list_plugins())
87.             assert expected_plugins == actual_plugins, (
88.                 f"plugin installed {plugins} should match plugins setting in config"
89.             )
90. 
91. 
92. @pytest.mark.usefixtures("prepare_mysql", "prepare_swift")
93. async def test_wordpress_plugin_installation_error(wordpress: WordpressApp):
94.     """
95.     arrange: after WordPress charm has been deployed and db relation established.
96.     act: install a nonexistent plugin.
97.     assert: charm should switch to blocked state and the reason should be included in the status
98.         message.
99.     """
100.     invalid_plugin = "invalid-plugin-sgkeahrgalejr"
101.     await wordpress.set_config({"plugins": invalid_plugin})
102.     await wordpress.wait_for_wordpress_idle()
103. 
104.     for unit in wordpress.get_units():
105.         assert unit.workload_status == "blocked", (
106.             "status should be 'blocked' since the plugin in plugins config does not exist"
107.         )
108. 
109.         assert invalid_plugin in unit.workload_status_message, (
110.             "status message should contain the reason why it's blocked"
111.         )
112. 
113.     await wordpress.set_config({"plugins": ""})
114.     await wordpress.wait_for_wordpress_idle(status="active")
115.
```

</details>


### ✅ `view`

**/tmp/wordpress-k8s-operator/tests/integration/test_core.py**

/tmp/wordpress-k8s-operator/tests/integration/test_core.py

<details>
<summary>164 lines</summary>

```
1. # Copyright 2024 Canonical Ltd.
2. # See LICENSE file for licensing details.
3. 
4. """Integration tests for WordPress charm core functionality."""
5. 
6. import io
7. import json
8. import secrets
9. import urllib.parse
10. 
11. import PIL.Image
12. import pytest
13. import requests
14. from pytest_operator.plugin import OpsTest
15. 
16. from tests.integration.helper import WordpressApp, WordpressClient
17. 
18. 
19. @pytest.mark.usefixtures("prepare_mysql")
20. @pytest.mark.abort_on_fail
21. async def test_wordpress_up(wordpress: WordpressApp, ops_test: OpsTest):
22.     """
23.     arrange: after WordPress charm has been deployed and db relation established.
24.     act: test wordpress server is up.
25.     assert: wordpress service is up.
26.     """
27.     await wordpress.model.wait_for_idle(status="active")
28.     for unit_ip in await wordpress.get_unit_ips():
29.         assert requests.get(f"http://{unit_ip}", timeout=10).status_code == 200
30. 
31. 
32. @pytest.mark.usefixtures("prepare_mysql", "prepare_swift")
33. async def test_wordpress_functionality(wordpress: WordpressApp):
34.     """
35.     arrange: after WordPress charm has been deployed and db relation established.
36.     act: test WordPress basic functionality (login, post, comment).
37.     assert: WordPress works normally as a blog site.
38.     """
39.     for unit_ip in await wordpress.get_unit_ips():
40.         WordpressClient.run_wordpress_functionality_test(
41.             host=unit_ip,
42.             admin_username="admin",
43.             admin_password=await wordpress.get_default_admin_password(),
44.         )
45. 
46. 
47. @pytest.mark.usefixtures("prepare_mysql")
48. async def test_change_upload_limit(wordpress: WordpressApp):
49.     """
50.     arrange: after WordPress charm has been deployed and db relation established.
51.     act: change upload limit related settings.
52.     assert: upload limit change should be reflected in the upload page.
53.     """
54.     await wordpress.set_config({"upload_max_filesize": "16M"})
55.     await wordpress.model.wait_for_idle(status="active")
56.     password = await wordpress.get_default_admin_password()
57.     for unit_ip in await wordpress.get_unit_ips():
58.         wordpress_client = WordpressClient(
59.             host=unit_ip,
60.             username="admin",
61.             password=password,
62.             is_admin=True,
63.         )
64.         text = wordpress_client.get_post(f"http://{unit_ip}/wp-admin/upload.php")
65.         # upload limit = min(upload_max_filesize, post_max_size)
66.         assert "Maximum upload file size: 8 MB" in text
67.     await wordpress.set_config({"post_max_size": "16M"})
68.     await wordpress.model.wait_for_idle(status="active")
69.     for unit_ip in await wordpress.get_unit_ips():
70.         wordpress_client = WordpressClient(
71.             host=unit_ip,
72.             username="admin",
73.             password=password,
74.             is_admin=True,
75.         )
76.         text = wordpress_client.get_post(f"http://{unit_ip}/wp-admin/upload.php")
77.         assert "Maximum upload file size: 16 MB" in text
78. 
79. 
80. @pytest.mark.usefixtures("prepare_mysql", "prepare_swift")
81. async def test_openstack_object_storage_plugin(
82.     wordpress: WordpressApp,
83.     swift_conn,
84. ):
85.     """
86.     arrange: after charm deployed, db relation established and openstack swift server ready.
87.     act: update charm configuration for openstack object storage plugin.
88.     assert: openstack object storage plugin should be installed after the config update and
89.         WordPress openstack swift object storage integration should be set up properly.
90.         After openstack swift plugin activated, an image file uploaded to one unit through
91.         WordPress media uploader should be accessible from all units.
92.     """
93.     container = await wordpress.get_swift_bucket()
94.     for idx, unit_ip in enumerate(await wordpress.get_unit_ips()):
95.         image = PIL.Image.new("RGB", (500, 500), color=(idx, 0, 0))
96.         nonce = secrets.token_hex(8)
97.         filename = f"{nonce}.{unit_ip}.{idx}.jpg"
98.         image_buf = io.BytesIO()
99.         image.save(image_buf, format="jpeg")
100.         image = image_buf.getvalue()
101.         wordpress_client = WordpressClient(
102.             host=unit_ip,
103.             username="admin",
104.             password=await wordpress.get_default_admin_password(),
105.             is_admin=True,
106.         )
107.         image_urls = wordpress_client.upload_media(filename=filename, content=image)["urls"]
108.         swift_object_list = [
109.             o["name"] for o in swift_conn.get_container(container, full_listing=True)[1]
110.         ]
111.         assert any(nonce in f for f in swift_object_list), (
112.             "media files uploaded should be stored in swift object storage"
113.         )
114.         source_url = min(image_urls, key=len)
115.         for image_url in image_urls:
116.             assert requests.get(image_url, timeout=10).status_code == 200, (
117.                 "the original image and resized images should be accessible from the WordPress site"
118.             )
119.         for host in await wordpress.get_unit_ips():
120.             url_components = list(urllib.parse.urlsplit(source_url))
121.             url_components[1] = host
122.             url = urllib.parse.urlunsplit(url_components)
123.             assert requests.get(url, timeout=10).content == image, (
124.                 "image downloaded from WordPress should match the image uploaded"
125.             )
126. 
127. 
128. @pytest.mark.usefixtures("prepare_mysql", "prepare_swift")
129. async def test_apache_config(wordpress: WordpressApp, ops_test: OpsTest):
130.     """
131.     arrange: after WordPress charm has been deployed and db relation established.
132.     act: update the config to trigger a new reconciliation.
133.     assert: apache config test works properly and prevents the restart of the server.
134.     """
135.     await wordpress.set_config(
136.         {"initial_settings": json.dumps({"user_name": "foo", "admin_email": "bar@example.com"})}
137.     )
138.     await wordpress.wait_for_wordpress_idle()
139.     exit_code, stdout, _ = await ops_test.juju("debug-log", "--replay")
140.     assert exit_code == 0
141.     assert "Apache config docker-php-swift-proxy is enabled" in stdout
142.     assert "Conf docker-php-swift-proxy already enabled" not in stdout
143. 
144. 
145. @pytest.mark.usefixtures("prepare_mysql")
146. async def test_uploads_owner(wordpress: WordpressApp, ops_test: OpsTest):
147.     """
148.     arrange: after WordPress charm has been deployed and db relation established.
149.     act: get uploads directory owner
150.     assert: uploads belongs to wordpress user.
151.     """
152.     cmd = [
153.         "juju",
154.         "ssh",
155.         f"{wordpress.app.name}/0",
156.         "stat",
157.         '--printf="%u"',
158.         "/var/www/html/wp-content/uploads",
159.     ]
160. 
161.     retcode, stdout, _ = await ops_test.run(*cmd)
162.     assert retcode == 0
163.     assert stdout.strip() == "584792"
164.
```

</details>


### ✅ `view`

**/tmp/wordpress-k8s-operator/tests/integration/test_cos_grafana.py**

/tmp/wordpress-k8s-operator/tests/integration/test_cos_grafana.py

<details>
<summary>67 lines</summary>

```
1. # Copyright 2024 Canonical Ltd.
2. # See LICENSE file for licensing details.
3. 
4. """Integration tests for WordPress charm COS integration."""
5. 
6. import functools
7. 
8. import pytest
9. import requests
10. from juju.action import Action
11. from juju.client._definitions import FullStatus
12. 
13. from tests.integration.helper import WordpressApp, wait_for
14. 
15. 
16. def dashboard_exist(loggedin_session: requests.Session, unit_address: str):
17.     """Checks if the WordPress dashboard is registered in Grafana.
18. 
19.     Args:
20.         loggedin_session: Requests session that's authorized to make API calls.
21.         unit_address: Grafana unit address.
22. 
23.     Returns:
24.         True if all dashboard is found. False otherwise.
25.     """
26.     dashboards = loggedin_session.get(
27.         f"http://{unit_address}:3000/api/search",
28.         timeout=10,
29.         params={"query": "Wordpress Operator Overview"},
30.     ).json()
31.     return len(dashboards)
32. 
33. 
34. @pytest.mark.usefixtures("prepare_mysql")
35. async def test_grafana_integration(
36.     wordpress: WordpressApp,
37. ):
38.     """
39.     arrange: after WordPress charm has been deployed and relations established among cos.
40.     act: grafana charm joins relation
41.     assert: grafana wordpress dashboard can be found
42.     """
43.     grafana = await wordpress.model.deploy("grafana-k8s", channel="1/stable", trust=True)
44.     await wordpress.model.wait_for_idle(status="active", apps=["grafana-k8s"], timeout=20 * 60)
45.     await wordpress.model.add_relation("wordpress-k8s:grafana-dashboard", "grafana-k8s")
46.     await wordpress.model.wait_for_idle(
47.         status="active", apps=["grafana-k8s", "wordpress-k8s"], timeout=30 * 60
48.     )
49.     action: Action = await grafana.units[0].run_action("get-admin-password")
50.     await action.wait()
51.     password = action.results["admin-password"]
52. 
53.     status: FullStatus = await wordpress.model.get_status(filters=[grafana.name])
54.     for unit in status.applications[grafana.name].units.values():
55.         sess = requests.session()
56.         sess.post(
57.             f"http://{unit.address}:3000/login",
58.             json={
59.                 "user": "admin",
60.                 "password": password,
61.             },
62.         ).raise_for_status()
63.         await wait_for(
64.             functools.partial(dashboard_exist, loggedin_session=sess, unit_address=unit.address),
65.             timeout=60 * 20,
66.         )
67.
```

</details>


### ✅ `view`

**/tmp/wordpress-k8s-operator/tests/integration/test_cos_loki.py**

/tmp/wordpress-k8s-operator/tests/integration/test_cos_loki.py

<details>
<summary>69 lines</summary>

```
1. # Copyright 2024 Canonical Ltd.
2. # See LICENSE file for licensing details.
3. 
4. """Integration tests for WordPress charm COS integration."""
5. 
6. import functools
7. from typing import Iterable
8. 
9. import kubernetes
10. import pytest
11. import requests
12. from juju.client._definitions import FullStatus
13. 
14. from tests.integration.helper import WordpressApp, wait_for
15. 
16. 
17. def log_files_exist(unit_address: str, application_name: str, filenames: Iterable[str]) -> bool:
18.     """Returns whether log filenames exist in Loki logs query.
19. 
20.     Args:
21.         unit_address: Loki unit ip address.
22.         application_name: Application name to query logs for.
23.         filenames: Expected filenames to be present in logs collected by Loki.
24. 
25.     Returns:
26.         True if log files with logs exists. False otherwise.
27.     """
28.     series = requests.get(f"http://{unit_address}:3100/loki/api/v1/series", timeout=10).text
29.     assert application_name in series
30.     log_query = requests.get(
31.         f"http://{unit_address}:3100/loki/api/v1/query",
32.         timeout=10,
33.         params={"query": f'{{juju_application="{application_name}"}}'},
34.     ).json()
35. 
36.     return len(log_query["data"]["result"]) != 0
37. 
38. 
39. @pytest.mark.abort_on_fail
40. @pytest.mark.usefixtures("prepare_mysql", "prepare_loki")
41. async def test_loki_integration(
42.     wordpress: WordpressApp,
43.     kube_config: str,
44. ):
45.     """
46.     arrange: after WordPress charm has been deployed and relations established.
47.     act: loki charm joins relation
48.     assert: loki joins relation successfully, logs are being output to container and to files for
49.         loki to scrape.
50.     """
51.     status: FullStatus = await wordpress.model.get_status(filters=["loki-k8s"])
52.     for unit in status.applications["loki-k8s"].units.values():
53.         await wait_for(
54.             functools.partial(
55.                 log_files_exist,
56.                 unit.address,
57.                 wordpress.name,
58.                 ("/var/log/apache2/error.*.log", "/var/log/apache2/access.*.log"),
59.             ),
60.             timeout=10 * 60,
61.         )
62.     kubernetes.config.load_kube_config(config_file=kube_config)
63.     kube_core_client = kubernetes.client.CoreV1Api()
64. 
65.     kube_log = kube_core_client.read_namespaced_pod_log(
66.         name=f"{wordpress.name}-0", namespace=wordpress.model.name, container="wordpress"
67.     )
68.     assert kube_log
69.
```

</details>


### ✅ `view`

**/tmp/wordpress-k8s-operator/tests/integration/test_cos_prometheus.py**

/tmp/wordpress-k8s-operator/tests/integration/test_cos_prometheus.py

<details>
<summary>34 lines</summary>

```
1. # Copyright 2024 Canonical Ltd.
2. # See LICENSE file for licensing details.
3. 
4. """Integration tests for WordPress charm COS integration."""
5. 
6. import pytest
7. import requests
8. from juju.client._definitions import FullStatus
9. 
10. from cos import APACHE_PROMETHEUS_SCRAPE_PORT
11. from tests.integration.helper import WordpressApp
12. 
13. 
14. @pytest.mark.abort_on_fail
15. @pytest.mark.usefixtures("prepare_mysql", "prepare_prometheus")
16. async def test_prometheus_integration(
17.     wordpress: WordpressApp,
18. ):
19.     """
20.     arrange: none.
21.     act: deploy the WordPress charm and relations established with prometheus.
22.     assert: prometheus metrics endpoint for prometheus is active and prometheus has active scrape
23.         targets.
24.     """
25.     for unit_ip in await wordpress.get_unit_ips():
26.         res = requests.get(f"http://{unit_ip}:{APACHE_PROMETHEUS_SCRAPE_PORT}", timeout=10)
27.         assert res.status_code == 200
28.     status: FullStatus = await wordpress.model.get_status(filters=["prometheus-k8s"])
29.     for unit in status.applications["prometheus-k8s"].units.values():
30.         query_targets = requests.get(
31.             f"http://{unit.address}:9090/api/v1/targets", timeout=10
32.         ).json()
33.         assert len(query_targets["data"]["activeTargets"])
34.
```

</details>


### ✅ `view`

**/tmp/wordpress-k8s-operator/tests/integration/test_external.py**

/tmp/wordpress-k8s-operator/tests/integration/test_external.py

<details>
<summary>91 lines</summary>

```
1. # Copyright 2024 Canonical Ltd.
2. # See LICENSE file for licensing details.
3. 
4. """Integration tests for WordPress charm external service integration."""
5. 
6. import secrets
7. 
8. import pytest
9. from pytest import Config
10. 
11. from tests.integration.helper import WordpressApp, WordpressClient
12. 
13. 
14. @pytest.mark.requires_secret
15. @pytest.mark.usefixtures("prepare_mysql", "prepare_swift")
16. async def test_akismet_plugin(
17.     wordpress: WordpressApp,
18.     pytestconfig: Config,
19. ):
20.     """
21.     arrange: after WordPress charm has been deployed, db relation established.
22.     act: update charm configuration for Akismet plugin.
23.     assert: Akismet plugin should be activated and spam detection function should be working.
24.     """
25.     akismet_api_key = pytestconfig.getoption("--akismet-api-key")
26.     if not akismet_api_key:
27.         raise ValueError("--akismet-api-key is required for running this test")
28. 
29.     await wordpress.set_config({"wp_plugin_akismet_key": akismet_api_key})
30.     await wordpress.wait_for_wordpress_idle(status="active")
31. 
32.     for wordpress_client in await wordpress.client_for_units():
33.         post = wordpress_client.create_post(secrets.token_hex(8), secrets.token_hex(8))
34.         wordpress_client.create_comment(
35.             post_id=post["id"], post_link=post["link"], content="akismet-guaranteed-spam"
36.         )
37.         wordpress_client.create_comment(
38.             post_id=post["id"], post_link=post["link"], content="test comment"
39.         )
40.         assert len(wordpress_client.list_comments(status="spam", post_id=post["id"])) == 1, (
41.             "Akismet plugin should move the triggered spam comment to the spam section"
42.         )
43.         assert len(wordpress_client.list_comments(post_id=post["id"])) == 1, (
44.             "Akismet plugin should keep the normal comment"
45.         )
46. 
47. 
48. @pytest.mark.requires_secret
49. @pytest.mark.usefixtures("prepare_mysql")
50. async def test_openid_plugin(
51.     wordpress: WordpressApp,
52.     pytestconfig: Config,
53. ):
54.     """
55.     arrange: after WordPress charm has been deployed, db relation established.
56.     act: update charm configuration for OpenID plugin.
57.     assert: A WordPress user should be created with correct roles according to the config.
58.     """
59.     openid_username = pytestconfig.getoption("--openid-username")
60.     if not openid_username:
61.         raise ValueError("--openid-username is required for running this test")
62.     openid_password = pytestconfig.getoption("--openid-password")
63.     if not openid_password:
64.         raise ValueError("--openid-password is required for running this test")
65.     launchpad_team = pytestconfig.getoption("--launchpad-team")
66.     if not launchpad_team:
67.         raise ValueError("--launchpad-team is required for running this test")
68.     await wordpress.set_config({"wp_plugin_openid_team_map": f"{launchpad_team}=administrator"})
69.     await wordpress.wait_for_wordpress_idle(status="active")
70. 
71.     for idx, unit_ip in enumerate(await wordpress.get_unit_ips()):
72.         # wordpress-teams-integration has a bug causing desired roles not to be assigned to
73.         # the user when first-time login. Login twice by creating the WordPressClient client twice
74.         # for the very first time.
75.         for attempt in range(2 if idx == 0 else 1):
76.             try:
77.                 wordpress_client = WordpressClient(
78.                     host=unit_ip,
79.                     username=openid_username,
80.                     password=openid_password,
81.                     is_admin=True,
82.                     use_launchpad_login=True,
83.                 )
84.             except AssertionError:
85.                 if attempt == 0:
86.                     continue
87.                 raise
88.         assert "administrator" in wordpress_client.list_roles(), (
89.             "An launchpad OpenID account should be associated with the WordPress admin user"
90.         )
91.
```

</details>


### ✅ `view`

**/tmp/wordpress-k8s-operator/tests/integration/test_ingress.py**

/tmp/wordpress-k8s-operator/tests/integration/test_ingress.py

<details>
<summary>72 lines</summary>

```
1. # Copyright 2024 Canonical Ltd.
2. # See LICENSE file for licensing details.
3. 
4. """Integration tests for WordPress charm ingress integration."""
5. 
6. import kubernetes
7. import pytest
8. import requests
9. 
10. from tests.integration.helper import WordpressApp
11. 
12. 
13. @pytest.mark.usefixtures("prepare_mysql", "prepare_nginx_ingress", "prepare_swift")
14. async def test_ingress(wordpress: WordpressApp):
15.     """
16.     arrange: after WordPress charm has been deployed and db relation established.
17.     act: deploy the nginx-ingress-integrator charm and create the relation between ingress charm
18.         and WordPress charm.
19.     assert: A Kubernetes ingress should be created and the ingress should accept HTTPS connections.
20.     """
21.     response = requests.get("http://127.0.0.1", headers={"Host": wordpress.name}, timeout=5)
22.     assert response.status_code == 200 and "wordpress" in response.text.lower(), (
23.         "Ingress should accept requests to WordPress and return correct contents"
24.     )
25. 
26.     new_hostname = "wordpress.test"
27.     await wordpress.set_config({"blog_hostname": new_hostname})
28.     await wordpress.model.wait_for_idle(status="active")
29.     response = requests.get(
30.         "https://127.0.0.1", headers={"Host": new_hostname}, timeout=5, verify=False
31.     )  # nosec
32.     assert response.status_code == 200 and "wordpress" in response.text.lower(), (
33.         "Ingress should update the server name indication based routing after blog_hostname updated"
34.     )
35. 
36. 
37. @pytest.mark.usefixtures("prepare_mysql", "prepare_nginx_ingress", "prepare_swift")
38. async def test_ingress_modsecurity(
39.     wordpress: WordpressApp,
40.     kube_config: str,
41. ):
42.     """
43.     arrange: WordPress charm is running and Nginx ingress integrator deployed and related to it.
44.     act: update the use_nginx_ingress_modsec WordPress charm config.
45.     assert: A Kubernetes ingress modsecurity should be enabled and proper rules should be set up
46.         for WordPress.
47.     """
48.     await wordpress.set_config({"use_nginx_ingress_modsec": "true"})
49.     await wordpress.model.wait_for_idle(status="active")
50. 
51.     kubernetes.config.load_kube_config(config_file=kube_config)
52.     kube = kubernetes.client.NetworkingV1Api()
53. 
54.     def get_ingress_annotation():
55.         """Get ingress annotations from kubernetes.
56. 
57.         Returns:
58.             Nginx ingress annotations.
59.         """
60.         ingress_list = kube.list_namespaced_ingress(namespace=wordpress.model.name).items
61.         return ingress_list[0].metadata.annotations
62. 
63.     ingress_annotations = get_ingress_annotation()
64.     assert ingress_annotations["nginx.ingress.kubernetes.io/enable-modsecurity"] == "true"
65.     assert (
66.         ingress_annotations["nginx.ingress.kubernetes.io/enable-owasp-modsecurity-crs"] == "true"
67.     )
68.     assert (
69.         'SecAction "id:900130,phase:1,nolog,pass,t:none,setvar:tx.crs_exclusions_wordpress=1"\n'
70.         in ingress_annotations["nginx.ingress.kubernetes.io/modsecurity-snippet"]
71.     )
72.
```

</details>


### ✅ `view`

**/tmp/wordpress-k8s-operator/tests/integration/test_machine.py**

/tmp/wordpress-k8s-operator/tests/integration/test_machine.py

<details>
<summary>40 lines</summary>

```
1. # Copyright 2024 Canonical Ltd.
2. # See LICENSE file for licensing details.
3. 
4. """Integration tests for WordPress charm core functionality with mysql machine charm."""
5. 
6. import functools
7. 
8. import pytest
9. from helper import get_mysql_primary_unit, wait_for
10. from juju.application import Application
11. from juju.model import Model
12. 
13. from tests.integration.helper import WordpressApp
14. 
15. 
16. @pytest.mark.usefixtures("prepare_machine_mysql")
17. async def test_database_endpoints_changed(machine_model: Model, wordpress: WordpressApp):
18.     """
19.     arrange: given related mysql charm with 3 units.
20.     act: when the leader mysql unit is removed and hence the endpoints changed event fired.
21.     assert: the WordPress correctly connects to the newly elected leader endpoint.
22.     """
23.     model: Model = wordpress.model
24.     mysql: Application = machine_model.applications["mysql"]
25.     await mysql.add_unit(2)
26.     await machine_model.wait_for_idle(["mysql"], timeout=30 * 60)
27.     await model.wait_for_idle(["wordpress-k8s"])
28. 
29.     leader = await get_mysql_primary_unit(mysql.units)
30.     assert leader, "No leader unit found."
31.     await mysql.destroy_unit(leader.name)
32.     await machine_model.wait_for_idle(["mysql"], timeout=30 * 60, idle_period=30)
33.     await model.wait_for_idle(["wordpress-k8s"])
34. 
35.     leader = await wait_for(functools.partial(get_mysql_primary_unit, mysql.units))
36. 
37.     assert await leader.get_public_address() in await wordpress.get_wordpress_config(), (
38.         "MySQL leader unit IP not found."
39.     )
40.
```

</details>


### ✅ `view`

**/tmp/wordpress-k8s-operator/tests/integration/helper.py**

/tmp/wordpress-k8s-operator/tests/integration/helper.py

```
File too large to read at once (24.2 KB). Consider using tools like grep (for searching), head/tail (for viewing start/end), view with view_range (for specific sections), or jq (for JSON) to examine portions of the file.
```


### 💬 Copilot

Now let me read the helper.py file in chunks and get the configuration files:

### ✅ `view`

**/tmp/wordpress-k8s-operator/tests/integration/helper.py**

/tmp/wordpress-k8s-operator/tests/integration/helper.py (lines 1-150)

<details>
<summary>150 lines</summary>

```
1. # Copyright 2024 Canonical Ltd.
2. # See LICENSE file for licensing details.
3. 
4. """Helper classes and functions for integration tests."""
5. 
6. import asyncio
7. import html
8. import inspect
9. import json
10. import logging
11. import mimetypes
12. import re
13. import secrets
14. import time
15. from typing import (
16.     Any,
17.     Awaitable,
18.     Callable,
19.     Dict,
20.     Iterable,
21.     List,
22.     Optional,
23.     Tuple,
24.     Type,
25.     TypedDict,
26.     Union,
27. )
28. 
29. import kubernetes
30. import requests
31. import yaml
32. from juju.application import Application
33. from juju.model import Model
34. from juju.unit import Unit
35. from pytest_operator.plugin import OpsTest
36. 
37. logger = logging.getLogger(__name__)
38. 
39. 
40. def retry(times: int, exceptions: Tuple[Type[Exception]], interval=5):
41.     """Retry decorator to catch exceptions and retry.
42. 
43.     Args:
44.         times: Number of times to retry.
45.         exceptions: Types of exceptions to catch to retry.
46.         interval: Interval between retries.
47.     """
48. 
49.     def decorator(func: Callable):
50.         """The decorating wrapper function.
51. 
52.         Args:
53.             func: Function to retry.
54.         """
55. 
56.         async def newfn(*args: Any, **kwargs: Any):
57.             """Newly wrapped function with retry.
58. 
59.             Returns:
60.                 The newly decorated function with retry capability.
61.             """
62.             attempt = 0
63.             while attempt < times:
64.                 try:
65.                     if asyncio.iscoroutinefunction(func):
66.                         return await func(*args, **kwargs)
67.                     return func(*args, **kwargs)
68.                 except exceptions as exc:
69.                     logger.warning(
70.                         "Function failed with exception %s, retrying %s/%s times.",
71.                         exc,
72.                         attempt,
73.                         times,
74.                     )
75.                     attempt += 1
76.                 time.sleep(interval)
77.             if asyncio.iscoroutinefunction(func):
78.                 return await func(*args, **kwargs)
79.             return func(*args, **kwargs)
80. 
81.         return newfn
82. 
83.     return decorator
84. 
85. 
86. class WordPressPost(TypedDict):
87.     """Typing for a WordPress post object.
88. 
89.     Attrs:
90.         id: A numeric identifier of a given post.
91.         link: A url path to given post.
92.     """
93. 
94.     id: int
95.     link: str
96. 
97. 
98. class WordpressClient:
99.     """A very simple WordPress client for test purpose only."""
100. 
101.     @classmethod
102.     def run_wordpress_functionality_test(cls, host: str, admin_username: str, admin_password: str):
103.         """Run standard WordPress functionality test suite.
104. 
105.         Args:
106.             host: ip address or hostname of the WordPress instance.
107.             admin_username: WordPress admin user username.
108.             admin_password: WordPress admin user password.
109.         """
110.         wp_client = cls(host=host, username=admin_username, password=admin_password, is_admin=True)
111.         post_title = secrets.token_hex(16)
112.         post_content = secrets.token_hex(16)
113.         post = wp_client.create_post(
114.             title=post_title,
115.             content=post_content,
116.         )
117.         homepage = wp_client.get_homepage()
118.         assert post_title in homepage, "admin user should be able to create a new post"
119.         comment = secrets.token_hex(16)
120.         post_link = post["link"]
121.         comment_link = wp_client.create_comment(
122.             post_id=post["id"],
123.             post_link=post_link,
124.             content=comment,
125.         )
126.         assert comment_link.startswith(post_link) and comment in wp_client.get_post(post_link), (
127.             "admin user should be able to create a comment"
128.         )
129. 
130.     def __init__(
131.         self,
132.         host: str,
133.         username: str,
134.         password: str,
135.         is_admin: bool,
136.         use_launchpad_login: bool = False,
137.     ):
138.         """Initialize the WordPress JSON API client.
139. 
140.         Args:
141.             host: ip address or hostname of the WordPress instance.
142.             username: WordPress user username.
143.             password: WordPress user password.
144.             is_admin: if this user is a WordPress admin.
145.             use_launchpad_login: Use Launchpad OpenID to login instead of WordPress userpass.
146. 
147.         Raises:
148.             RuntimeError: if invalid credentials were used to login to WordPress.
149.             ValueError: if non-admin account was used to access /wp-json/ endpoint or the /wp-json/
150.                 endpoint was not set through permalink.
```

</details>


### ✅ `view`

**/tmp/wordpress-k8s-operator/pyproject.toml**

/tmp/wordpress-k8s-operator/pyproject.toml

<details>
<summary>169 lines</summary>

```
1. # Copyright 2025 Canonical Ltd.
2. # See LICENSE file for licensing details.
3. 
4. [project]
5. name = "wordpress-k8s-operator"
6. version = "0.0.0"
7. description = "WordPress is an OSS to create a beautiful website."
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
19.   "cosl==1.4.0",
20.   "mysql-connector-python==9.5.0",
21.   "ops==3.5.1",
22.   "pydantic==2.12.5",
23.   "requests==2.32.5",
24. ]
25. 
26. [dependency-groups]
27. fmt = [
28.   "ruff",
29. ]
30. lint = [
31.   "codespell",
32.   "juju>=3.6,<4",
33.   "kubernetes",
34.   "mypy",
35.   "pep8-naming",
36.   "pillow",
37.   "pytest==9.0.2",
38.   "pytest-cov",
39.   "pytest-operator",
40.   "python-keystoneclient",
41.   "python-swiftclient",
42.   "ruff",
43.   "types-pyyaml",
44.   "types-requests",
45.   "websockets<17",
46. ]
47. static = [
48.   "bandit[toml]",
49.   "toml",
50. ]
51. unit = [
52.   "coverage[toml]",
53.   "pytest",
54. ]
55. coverage-report = [
56.   "coverage[toml]",
57.   "pytest",
58. ]
59. integration = [
60.   "allure-pytest>=2.8.18",
61.   "allure-pytest-collection-report @ git+https://github.com/canonical/data-platform-workflows@v24.0.0#subdirectory=python/pytest_plugins/allure_pytest_collection_report",
62.   "juju>=2.9,<3",
63.   "kubernetes",
64.   "pillow",
65.   "pytest==9.0.2",
66.   "pytest-cov",
67.   "pytest-operator",
68.   "python-keystoneclient",
69.   "python-swiftclient",
70.   "types-pyyaml",
71.   "types-requests",
72.   "websockets<17",
73. ]
74. integration-juju3 = [
75.   "juju==3.6.1.3",
76.   "kubernetes",
77.   "macaroonbakery==1.3.4",
78.   "pillow",
79.   "pytest==9.0.2",
80.   "pytest-cov",
81.   "pytest-operator",
82.   "python-keystoneclient",
83.   "python-swiftclient",
84.   "types-pyyaml",
85.   "types-requests",
86. ]
87. 
88. [tool.uv]
89. package = false
90. conflicts = [ [ { group = "integration" }, { group = "integration-juju3" }, { group = "lint" } ] ]
91. 
92. [tool.ruff]
93. target-version = "py310"
94. line-length = 99
95. 
96. # enable ruff linters:
97. #   A flake8-builtins
98. #   B flake8-bugbear
99. # CPY flake8-copyright
100. #   D pydocstyle
101. # E/W pycodestyle
102. #   F Pyflakes
103. #   I isort
104. #   N pep8-naming
105. # RUF Ruff-specific rules
106. #   S flake8-bandit
107. # SIM flake8-simplify
108. #  TC flake8-type-checking
109. #  UP pyupgrade
110. lint.select = [ "A", "B", "C", "CPY", "D", "E", "F", "I", "N", "RUF", "S", "SIM", "TC", "UP", "W" ]
111. lint.ignore = [
112.   "B904",
113.   "D107",
114.   "D203",
115.   "D204",
116.   "D205",
117.   "D213",
118.   "D215",
119.   "D400",
120.   "D404",
121.   "D406",
122.   "D407",
123.   "D408",
124.   "D409",
125.   "D413",
126.   "E501",
127.   "S105",
128.   "S603",
129.   "TC002",
130.   "TC006",
131.   "UP006",
132.   "UP007",
133.   "UP035",
134.   "UP045",
135. ]
136. lint.per-file-ignores."tests/*" = [ "B011", "D100", "D101", "D102", "D103", "D104", "D212", "D415", "D417", "S" ]
137. lint.flake8-copyright.author = "Canonical Ltd."
138. lint.flake8-copyright.min-file-size = 1
139. lint.flake8-copyright.notice-rgx = "Copyright\\s\\d{4}([-,]\\d{4})*\\s+"
140. lint.mccabe.max-complexity = 10
141. lint.pydocstyle.convention = "google"
142. 
143. [tool.codespell]
144. skip = "build,lib,venv,icon.svg,.tox,.git,.mypy_cache,.ruff_cache,.coverage,htmlcov,uv.lock,grafana_dashboards"
145. 
146. [tool.pytest.ini_options]
147. markers = [
148.   "slow: marks slow and not very important tests",
149.   "requires_secret: mark tests that require external secrets",
150. ]
151. 
152. [tool.coverage.run]
153. branch = true
154. 
155. [tool.coverage.report]
156. fail_under = 90
157. show_missing = true
158. 
159. [tool.mypy]
160. ignore_missing_imports = true
161. allow_redefinition = true
162. plugins = [ "pydantic.mypy" ]
163. 
164. [tool.bandit]
165. exclude_dirs = [ "/venv/" ]
166. 
167. [tool.bandit.assert_used]
168. skips = [ "*/integration/helper.py", "*/*test*" ]
169.
```

</details>


### ✅ `bash`

**Find tox configuration files**

$ find /tmp/wordpress-k8s-operator -maxdepth 2 -name "tox.ini" -o -name "tox.toml" | head -5

```
/tmp/wordpress-k8s-operator/tox.toml
<exited with exit code 0>
```


### 💬 Copilot

Now let me read the rest of helper.py and the tox.toml file:

### ✅ `view`

**/tmp/wordpress-k8s-operator/tests/integration/helper.py**

/tmp/wordpress-k8s-operator/tests/integration/helper.py (lines 150-350)

<details>
<summary>201 lines</summary>

```
150.                 endpoint was not set through permalink.
151.         """
152.         self.host = host
153.         self.username = username
154.         self.password = password
155.         self._session = requests.session()
156.         self.timeout = 10
157.         if use_launchpad_login:
158.             self.login_using_launchpad(username, password)
159.         else:
160.             if not self._login():
161.                 raise RuntimeError(f"login failed with username {username}")
162.         # By default, WordPress does not expose the /wp-json/ endpoint test if /wp-json
163.         # is exposed, and expose that with a permalink setting if not
164.         try:
165.             self._get(f"http://{self.host}/wp-json/").json()
166.         except requests.exceptions.JSONDecodeError as exc:
167.             if not is_admin:
168.                 raise ValueError(
169.                     "set options-permalink manually or login with an admin account"
170.                 ) from exc
171.             self._set_options_permalink()
172. 
173.     def _get(
174.         self,
175.         url: str,
176.         headers: Optional[Dict[str, str]] = None,
177.         except_status_code: Optional[int] = None,
178.     ) -> requests.Response:
179.         """HTTP GET using the instance session.
180. 
181.         The instance session contains user's login session cookies, so this method can assess
182.         restricted resources on WordPress.
183. 
184.         Args:
185.             url: Same as the ``url`` argument in :meth:`requests.Session.get`.
186.             headers: Same as ``url``  in :meth:`requests.Session.get`.
187.             except_status_code: Except the response http status code,
188.                 raise :exc:`requests.HTTPError` if not match.
189. 
190.         Raises:
191.             HTTPError: if unexpected status code was returned.
192. 
193.         Returns:
194.             An instance of :class:`requests.Response`.
195.         """
196.         request = requests.Request("GET", url, headers=headers)
197.         prepped = self._session.prepare_request(request)
198.         response = self._session.send(prepped, timeout=self.timeout)
199.         if except_status_code is not None and response.status_code != except_status_code:
200.             raise requests.HTTPError(request=request, response=response)
201.         return response
202. 
203.     def _post(
204.         self,
205.         url: str,
206.         json_: Optional[dict] = None,
207.         data: Optional[Union[bytes, Dict[str, Any]]] = None,
208.         headers: Optional[Dict[str, str]] = None,
209.         except_status_code: Optional[int] = None,
210.     ) -> requests.Response:
211.         """HTTP GET using the instance session.
212. 
213.         The instance session contains user's login session cookies, so this method can assess
214.         restricted resources on WordPress.
215. 
216.         Args:
217.             url: Same as the ``url`` argument in :meth:`requests.Session.post`.
218.             json_: Same as the ``json`` argument in :meth:`requests.Session.post`.
219.             data: Same as the ``data`` argument in :meth:`requests.Session.post`.
220.             headers: Same as the ``url``  in :meth:`requests.Session.post`.
221.             except_status_code: Except the response http status code,
222.                 raise :exc:`requests.HTTPError` if not match.
223. 
224.         Raises:
225.             HTTPError: if unexpected status code was returned.
226. 
227.         Returns:
228.             An instance of :class:`requests.Response`.
229.         """
230.         request = requests.Request("POST", url, json=json_, data=data, headers=headers)
231.         prepped = self._session.prepare_request(request)
232.         response = self._session.send(prepped, timeout=self.timeout)
233.         if except_status_code is not None and response.status_code != except_status_code:
234.             raise requests.HTTPError(request=request, response=response)
235.         return response
236. 
237.     def _login(self) -> bool:
238.         """Login WordPress with current username and password, set session cookies.
239. 
240.         Returns:
241.             True if login successfully.
242.         """
243.         self._get(f"http://{self.host}/wp-login.php")
244.         response = self._post(
245.             f"http://{self.host}/wp-login.php",
246.             data={
247.                 "log": self.username,
248.                 "pwd": self.password,
249.                 "wp-submit": "Log In",
250.                 "redirect_to": f"http://{self.host}/wp-admin/",
251.                 "testcookie": 1,
252.             },
253.             except_status_code=200,
254.         )
255.         return response.url == f"http://{self.host}/wp-admin/"
256. 
257.     def _set_options_permalink(self) -> None:
258.         """Set WordPress permalink option to /%postname%/."""
259.         options_permalink_page = self._get(
260.             f"http://{self.host}/wp-admin/options-permalink.php"
261.         ).text
262.         wp_nonce_matches = re.findall(
263.             'name="_wpnonce" value="([a-zA-Z0-9]+)"', options_permalink_page
264.         )
265.         assert wp_nonce_matches, f"wpnonce not found in {options_permalink_page}"
266.         wp_nonce = wp_nonce_matches[0]
267.         self._post(
268.             f"http://{self.host}/wp-admin/options-permalink.php",
269.             data={
270.                 "_wpnonce": wp_nonce,
271.                 "_wp_http_referer": "/wp-admin/options-permalink.php",
272.                 "selection": "/%postname%/",
273.                 "permalink_structure": "/%postname%/",
274.                 "submit": "Save Changes",
275.             },
276.             except_status_code=200,
277.         )
278. 
279.     def _gen_wp_rest_nonce(self) -> str:
280.         """Generate a nonce for WordPress REST API.
281. 
282.         Returns:
283.             (str) A WordPress nonce for WordPress JSON REST API.
284.         """
285.         new_post_page = self._get(f"http://{self.host}/wp-admin/post-new.php").text
286.         nonce: str = json.loads(re.findall("var wpApiSettings = ([^;]+);", new_post_page)[0])[
287.             "nonce"
288.         ]
289.         return nonce
290. 
291.     def create_post(
292.         self, title: str, content: str, featured_media: Optional[int] = None
293.     ) -> WordPressPost:
294.         """Create a WordPress post using wp-json API, return post object.
295. 
296.         Args:
297.             title (str): Title of the post.
298.             content (str): Content of the post.
299.             featured_media (Optional[int]): Media ID for the featured media of the post.
300. 
301.         Returns:
302.             Post object returned from WordPress REST API.
303.         """
304.         body: Dict[str, Union[str, int]] = {
305.             "status": "publish",
306.             "title": title,
307.             "content": content,
308.         }
309.         if featured_media is not None:
310.             body["featured_media"] = featured_media
311.         response = self._post(
312.             f"http://{self.host}/wp-json/wp/v2/posts/",
313.             json_=body,
314.             headers={"X-WP-Nonce": self._gen_wp_rest_nonce()},
315.             except_status_code=201,
316.         )
317.         return response.json()
318. 
319.     def create_comment(self, post_id: int, post_link: str, content: str) -> str:
320.         """Add a comment to a WordPress post using HTML form, return url link of the new comment.
321. 
322.         Args:
323.             post_id: ID of the post that the new comment will be attached to.
324.             post_link: URL of the post that the new comment will be attached to.
325.             content: Content of the new comment.
326. 
327.         Raises:
328.             ValueError: if same comment already exists.
329. 
330.         Returns:
331.             (str) URL pointed to the comment created.
332.         """
333.         post_page = self._get(post_link)
334.         nonce = re.findall(
335.             'name="_wp_unfiltered_html_comment_disabled" value="([a-zA-Z0-9]+)"', post_page.text
336.         )[0]
337. 
338.         response = self._post(
339.             f"http://{self.host}/wp-comments-post.php",
340.             data={
341.                 "comment": content,
342.                 "submit": "Post Comment",
343.                 "comment_post_ID": post_id,
344.                 "comment_parent": "0",
345.                 "_wp_unfiltered_html_comment": nonce,
346.             },
347.             except_status_code=200,
348.         )
349.         if "Duplicate comment detected" in response.text:
350.             raise ValueError(f"Duplicate comment detected: {content!r}")
```

</details>


### ✅ `view`

**/tmp/wordpress-k8s-operator/tests/integration/helper.py**

/tmp/wordpress-k8s-operator/tests/integration/helper.py (lines 350--1)

<details>
<summary>341 lines</summary>

```
350.             raise ValueError(f"Duplicate comment detected: {content!r}")
351.         return response.url
352. 
353.     def get_homepage(self) -> str:
354.         """Get the WordPress homepage source (HTML).
355. 
356.         Returns:
357.             (str) The WordPress homepage content, HTML.
358.         """
359.         return self._get(f"http://{self.host}").text
360. 
361.     def get_post(self, post_link: str) -> str:
362.         """Get the WordPress blog post page source (HTML).
363. 
364.         Args:
365.             post_link: URL to the WordPress post.
366. 
367.         Returns:
368.             (str) The WordPress homepage content, HTML.
369.         """
370.         return self._get(post_link).text
371. 
372.     def list_themes(self) -> List[str]:
373.         """List all installed WordPress theme slugs.
374. 
375.         Return:
376.             (List[str]) WordPress themes Installed.
377.         """
378.         response = self._get(
379.             f"http://{self.host}/wp-json/wp/v2/themes?per_page=100",
380.             headers={"X-WP-Nonce": self._gen_wp_rest_nonce()},
381.             except_status_code=200,
382.         )
383.         return [t["stylesheet"] for t in response.json()]
384. 
385.     def list_plugins(self) -> List[str]:
386.         """List all installed WordPress plugin slugs.
387. 
388.         Return:
389.             (List[str]) WordPress plugins Installed.
390.         """
391.         response = self._get(
392.             f"http://{self.host}/wp-json/wp/v2/plugins?per_page=100",
393.             headers={"X-WP-Nonce": self._gen_wp_rest_nonce()},
394.             except_status_code=200,
395.         )
396.         return [p["plugin"].split("/")[0] for p in response.json()]
397. 
398.     def list_comments(self, status: str = "approve", post_id: Optional[int] = None) -> List[dict]:
399.         """List all comments in the WordPress site.
400. 
401.         Args:
402.             status: WordPress comment status, can be 'hold', 'approve', 'spam', or 'trash'.
403.             post_id: List all comments attached to the post, None to query the entire site.
404. 
405.         Returns:
406.             (List[dict]) A list of comment objects returned by WordPress REST API.
407.         """
408.         url = f"http://{self.host}/wp-json/wp/v2/comments?status={status}"
409.         if post_id:
410.             url += f"&post={post_id}"
411.         response = self._get(url, headers={"X-WP-Nonce": self._gen_wp_rest_nonce()})
412.         return response.json()
413. 
414.     def upload_media(self, filename: str, content: bytes, mimetype: Optional[str] = None) -> dict:
415.         """Upload a media file (image/video).
416. 
417.         Args:
418.             filename: Filename of the media file.
419.             content: Content of the media file, bytes.
420.             mimetype: Mimetype of the media file, will infer from the filename if not provided.
421. 
422.         Raises:
423.             ValueError: if filename has invalid mimetype that cannot be automatically deduced.
424. 
425.         Returns:
426.              A dict with two keys: id and urls. Id is the WordPress media id and urls is a list of
427.              URL of the original image and resized images for the uploaded file on WordPress.
428.         """
429.         if mimetype is None:
430.             mimetype = mimetypes.guess_type(filename)[0]
431.         if mimetype is None:
432.             raise ValueError("Unable to deduce mimetype from filename")
433.         response = self._post(
434.             f"http://{self.host}/wp-json/wp/v2/media",
435.             headers={
436.                 "X-WP-Nonce": self._gen_wp_rest_nonce(),
437.                 "Content-Type": mimetype,
438.                 "Content-Disposition": f'attachment; filename="{filename}"',
439.             },
440.             data=content,
441.             except_status_code=201,
442.         )
443.         media = response.json()
444.         image_urls = []
445.         for size in media["media_details"]["sizes"].values():
446.             image_urls.append(size["source_url"])
447.         if media["source_url"] not in image_urls:
448.             image_urls.append(media["source_url"])
449.         return {"id": media["id"], "urls": image_urls}
450. 
451.     def login_using_launchpad(self, username: str, password: str) -> None:
452.         """Log in the WordPress site using Launchpad OpenID, require launchpad related plugins.
453. 
454.         Args:
455.             username: Username of the launchpad account.
456.             password: Password of the launchpad account.
457.         """
458.         # If the session was already used to log in, the openid page is different.
459.         # Clear the session to avoid such behavior.
460.         if self._session:
461.             self._session.close()
462.         self._session = requests.session()
463.         login_url = f"http://{self.host}/wp-login.php"
464.         self._get(login_url)
465.         openid_redirect = self._post(
466.             login_url,
467.             data={
468.                 "launchpad": "Login",
469.                 "redirect_to": f"http://{self.host}/wp-admin/",
470.                 "testcookie": "1",
471.             },
472.         )
473.         openid_args = dict(
474.             re.findall(
475.                 '<input type="hidden" name="([^"]+)" value="([^"]+)" />',
476.                 html.unescape(openid_redirect.text),
477.             )
478.         )
479.         login_page = self._post(
480.             "https://login.launchpad.net/+openid",
481.             data=openid_args,
482.         )
483.         csrf_token = re.findall(
484.             "<input type='hidden' name='csrfmiddlewaretoken' value='([^']+)' />", login_page.text
485.         )[0]
486.         login_link = re.findall(
487.             '<a id="login-link" data-qa-id="login_link" href="([^"]+)" class="p-link--soft">',
488.             login_page.text,
489.         )[0]
490.         login_url = f"https://login.launchpad.net{login_link}"
491.         confirm_page = self._post(
492.             login_url,
493.             data={
494.                 "csrfmiddlewaretoken": csrf_token,
495.                 "email": username,
496.                 "user-intentions": "login",
497.                 "password": password,
498.                 "continue": "",
499.                 "openid.usernamesecret": "",
500.             },
501.             headers={"Referer": login_page.url},
502.         )
503.         csrf_token = re.findall(
504.             "<input type='hidden' name='csrfmiddlewaretoken' value='([^']+)' />", confirm_page.text
505.         )[0]
506.         teams = re.findall("Team membership: ([^<]+)<", confirm_page.text)
507.         assert teams, f"no teams found in {confirm_page.text}"
508.         team = teams[0]
509.         self._post(
510.             confirm_page.url,
511.             data={
512.                 "csrfmiddlewaretoken": csrf_token,
513.                 "nickname": "on",
514.                 "email": "on",
515.                 "fullname": "on",
516.                 team: "on",
517.                 "ok": "",
518.                 "yes": "",
519.                 "openid.usernamesecret": "",
520.             },
521.             headers={"Referer": confirm_page.url},
522.             except_status_code=200,
523.         )
524. 
525.     def list_associated_ubuntu_one_accounts(self) -> List[str]:
526.         """List Ubuntu One accounts OpenID IDs associated with the current WordPress account.
527. 
528.         Returns:
529.             A list of Ubuntu One account OpenID IDs
530.             (something like https://login.ubuntu.com/+id/xxxxxxxx).
531.         """
532.         openid_setting = self._get(
533.             f"http://{self.host}/wp-admin/users.php?page=your_openids",
534.             except_status_code=200,
535.         )
536.         return re.findall("<td>(https://login\\.ubuntu\\.com[^<]+)</td>", openid_setting.text)
537. 
538.     def list_roles(self) -> List[str]:
539.         """List all WordPress roles of the current user.
540. 
541.         Raises:
542.             ValueError: No valid user to call list_roles was found.
543. 
544.         Returns:
545.             WordPress roles as a list of str.
546.         """
547.         user_page = self._get(f"http://{self.host}/wp-admin/users.php").text
548.         emails = re.findall("""data-colname="Email"><a href='mailto:([^']+)'>""", user_page)
549.         usernames = re.findall('users\\.php">([^<]+)</a>', user_page)
550.         roles = re.findall('data-colname="Role">([^<]+)</td>', user_page)
551.         for email, username, role in zip(emails, usernames, roles, strict=True):
552.             if self.username in (email, username):
553.                 return [r.strip() for r in role.lower().split(",")]
554.         raise ValueError(f"User {self.username} not found")
555. 
556. 
557. class WordpressApp:
558.     """An object represents the wordpress charm application."""
559. 
560.     def __init__(self, app: Application, ops_test: OpsTest, kube_config: str):
561.         """Initialize the WordpressApp object."""
562.         self.app = app
563.         self.ops_test = ops_test
564.         kubernetes.config.load_kube_config(config_file=kube_config)
565.         self.kube_core_client = kubernetes.client.CoreV1Api()
566. 
567.     @property
568.     def model(self) -> Model:
569.         """Get the current juju model."""
570.         model = self.ops_test.model
571.         assert model
572.         return model
573. 
574.     @property
575.     def name(self) -> str:
576.         """Get the wordpress charm application name."""
577.         return self.app.name
578. 
579.     @retry(times=5, exceptions=(KeyError,))
580.     async def get_unit_ips(self) -> List[str]:
581.         """Retrieve unit ip addresses, similar to fixture_get_unit_status_list.
582. 
583.         Returns:
584.             list of WordPress units ip addresses.
585.         """
586.         _, status, _ = await self.ops_test.juju("status", "--format", "json")
587.         status = json.loads(status)
588.         units = status["applications"][self.name]["units"]
589.         ip_list = []
590.         for key in sorted(units.keys(), key=lambda n: int(n.split("/")[-1])):
591.             ip_list.append(units[key]["address"])
592.         return ip_list
593. 
594.     async def get_default_admin_password(self) -> str:
595.         """Get default admin password using get-initial-password action.
596. 
597.         Returns:
598.             WordPress admin account password
599.         """
600.         action = await self.app.units[0].run_action("get-initial-password")
601.         await action.wait()
602.         return action.results["password"]
603. 
604.     async def set_config(self, config):
605.         """Update the configuration of the wordpress charm."""
606.         await self.app.set_config(config)
607. 
608.     async def get_swift_bucket(self) -> Optional[str]:
609.         """Get the swift bucket name used by the wordpress application."""
610.         config = await self.app.get_config()
611.         openstack_config = config["wp_plugin_openstack-objectstorage_config"]["value"]
612.         return yaml.safe_load(openstack_config).get("bucket")
613. 
614.     async def client_for_units(self) -> List[WordpressClient]:
615.         """Get a list of WordpressClient for each unit of the wordpress application."""
616.         clients = []
617.         default_admin_password = await self.get_default_admin_password()
618.         for unit_ip in await self.get_unit_ips():
619.             clients.append(
620.                 WordpressClient(
621.                     host=unit_ip, username="admin", password=default_admin_password, is_admin=True
622.                 )
623.             )
624.         return clients
625. 
626.     async def wait_for_wordpress_idle(self, status: Optional[str] = None):
627.         """Wait for the wordpress application is idle."""
628.         await self.model.wait_for_idle(status=status, apps=[self.name])
629. 
630.     def get_units(self) -> List[Unit]:
631.         """Get units of the wordpress application."""
632.         return self.app.units
633. 
634.     async def get_wordpress_config(self) -> str:
635.         """Get wp-config.php contents from the leader unit.
636. 
637.         Returns:
638.             The contents of wp-config.php
639.         """
640.         unit = self.app.units[0]
641.         stdout = kubernetes.stream.stream(
642.             self.kube_core_client.connect_get_namespaced_pod_exec,
643.             unit.name.replace("/", "-"),
644.             unit.model.name,
645.             container="wordpress",
646.             command=["cat", "/var/www/html/wp-config.php"],
647.             stderr=True,
648.             stdin=False,
649.             stdout=True,
650.             tty=False,
651.         )
652.         return stdout
653. 
654. 
655. async def wait_for(
656.     func: Callable[[], Union[Awaitable, Any]],
657.     timeout: int = 300,
658.     check_interval: int = 10,
659. ) -> Any:
660.     """Wait for function execution to become truthy.
661. 
662.     Args:
663.         func: A callback function to wait to return a truthy value.
664.         timeout: Time in seconds to wait for function result to become truthy.
665.         check_interval: Time in seconds to wait between ready checks.
666. 
667.     Raises:
668.         TimeoutError: if the callback function did not return a truthy value within timeout.
669.     """
670.     deadline = time.time() + timeout
671.     is_awaitable = inspect.iscoroutinefunction(func)
672.     while time.time() < deadline:
673.         if is_awaitable and (result := await func()):
674.             return result
675.         if result := func():
676.             return result
677.         time.sleep(check_interval)
678.     raise TimeoutError()
679. 
680. 
681. async def get_mysql_primary_unit(units: Iterable[Unit]) -> Optional[Unit]:
682.     """Get the mysql primary unit.
683. 
684.     Args:
685.         units: An iterable list of units to search for primary unit from.
686.     """
687.     for unit in units:
688.         if unit.workload_status_message == "Primary":
689.             return unit
690.     return None
```

</details>


### ✅ `view`

**/tmp/wordpress-k8s-operator/tox.toml**

/tmp/wordpress-k8s-operator/tox.toml

<details>
<summary>167 lines</summary>

```
1. # Copyright 2025 Canonical Ltd.
2. # See LICENSE file for licensing details.
3. 
4. skipsdist = true
5. envlist = [ "lint", "unit", "static", "coverage-report" ]
6. skip_missing_interpreters = true
7. requires = [ "tox>=4.21" ]
8. no_package = true
9. 
10. [env_run_base]
11. passenv = [ "PYTHONPATH", "CHARM_BUILD_DIR", "MODEL_SETTINGS" ]
12. allowlist_externals = [ "docker" ]
13. runner = "uv-venv-lock-runner"
14. 
15. [env_run_base.setenv]
16. PYTHONPATH = "{toxinidir}:{toxinidir}/lib:{[vars]src_path}"
17. PYTHONBREAKPOINT = "ipdb.set_trace"
18. PY_COLORS = "1"
19. 
20. [env.fmt]
21. description = "Apply coding style standards to code"
22. commands = [
23.   [
24.     "ruff",
25.     "check",
26.     "--fix",
27.     "--select",
28.     "I",
29.     { replace = "ref", of = [
30.       "vars",
31.       "all_path",
32.     ], extend = true },
33.   ],
34.   [
35.     "ruff",
36.     "format",
37.     { replace = "ref", of = [
38.       "vars",
39.       "all_path",
40.     ], extend = true },
41.   ],
42. ]
43. dependency_groups = [ "fmt" ]
44. 
45. [env.lint]
46. description = "Check code against coding style standards"
47. commands = [
48.   [
49.     "codespell",
50.     "{toxinidir}",
51.   ],
52.   [
53.     "ruff",
54.     "format",
55.     "--check",
56.     "--diff",
57.     { replace = "ref", of = [
58.       "vars",
59.       "all_path",
60.     ], extend = true },
61.   ],
62.   [
63.     "ruff",
64.     "check",
65.     { replace = "ref", of = [
66.       "vars",
67.       "all_path",
68.     ], extend = true },
69.   ],
70.   [
71.     "mypy",
72.     { replace = "ref", of = [
73.       "vars",
74.       "all_path",
75.     ], extend = true },
76.   ],
77. ]
78. dependency_groups = [ "lint" ]
79. 
80. [env.static]
81. description = "Run static analysis tests"
82. commands = [ [ "bandit", "-c", "{toxinidir}/pyproject.toml", "-r", "{[vars]src_path}", "{[vars]tst_path}" ] ]
83. dependency_groups = [ "static" ]
84. 
85. [env.unit]
86. description = "Run unit tests"
87. commands = [
88.   [
89.     "coverage",
90.     "run",
91.     "--source={[vars]src_path}",
92.     "-m",
93.     "pytest",
94.     "--ignore={[vars]tst_path}integration",
95.     "-v",
96.     "--tb",
97.     "native",
98.     "-s",
99.     { replace = "posargs", extend = "true" },
100.   ],
101.   [
102.     "coverage",
103.     "report",
104.   ],
105. ]
106. dependency_groups = [ "unit" ]
107. 
108. [env.coverage-report]
109. description = "Create test coverage report"
110. commands = [ [ "coverage", "report" ] ]
111. dependency_groups = [ "coverage-report" ]
112. 
113. [env.integration]
114. description = "Run integration tests"
115. commands = [
116.   [
117.     "pytest",
118.     "{[vars]tst_path}",
119.     "-v",
120.     "--tb",
121.     "native",
122.     "--ignore={[vars]tst_path}unit",
123.     "--log-cli-level=INFO",
124.     "-s",
125.     { replace = "posargs", extend = "true" },
126.   ],
127. ]
128. dependency_groups = [ "integration" ]
129. 
130. [env.integration-juju3]
131. description = "Run integration tests using Juju 3"
132. commands = [
133.   [
134.     "pytest",
135.     "{[vars]tst_path}",
136.     "-v",
137.     "--tb",
138.     "native",
139.     "--ignore={[vars]tst_path}unit",
140.     "--log-cli-level=INFO",
141.     "-s",
142.     { replace = "posargs", extend = "true" },
143.   ],
144. ]
145. dependency_groups = [ "integration-juju3" ]
146. 
147. [env.lint-fix]
148. description = "Apply coding style standards to code"
149. commands = [
150.   [
151.     "ruff",
152.     "check",
153.     "--fix",
154.     "--fix-only",
155.     { replace = "ref", of = [
156.       "vars",
157.       "all_path",
158.     ], extend = true },
159.   ],
160. ]
161. dependency_groups = [ "lint" ]
162. 
163. [vars]
164. src_path = "{toxinidir}/src/"
165. tst_path = "{toxinidir}/tests/"
166. all_path = [ "{toxinidir}/src/", "{toxinidir}/tests/" ]
167.
```

</details>


### 💬 Copilot

Perfect! Now let me also check if there are any pre-run scripts and get a summary view:

### ✅ `view`

**/tmp/wordpress-k8s-operator/tests/integration/pre_run_script.sh**

/tmp/wordpress-k8s-operator/tests/integration/pre_run_script.sh

<details>
<summary>21 lines</summary>

```
1. #!/bin/bash
2. 
3. # Copyright 2024 Canonical Ltd.
4. # See LICENSE file for licensing details.
5. 
6. # Pre-run script for integration test operator-workflows action.
7. # https://github.com/canonical/operator-workflows/blob/main/.github/workflows/integration_test.yaml
8. 
9. # Jenkins machine agent charm is deployed on lxd and Jenkins-k8s server charm is deployed on
10. # microk8s.
11. 
12. TESTING_MODEL="$(juju switch)"
13. 
14. # lxd should be install and init by a previous step in integration test action.
15. echo "bootstrapping lxd juju controller"
16. sg microk8s -c "microk8s status --wait-ready"
17. sg microk8s -c "juju bootstrap localhost localhost"
18. 
19. echo "Switching to testing model"
20. sg microk8s -c "juju switch $TESTING_MODEL"
21.
```

</details>


### ✅ `view`

**/tmp/wordpress-k8s-operator/tests/integration/pre_run_script_juju3.sh**

/tmp/wordpress-k8s-operator/tests/integration/pre_run_script_juju3.sh

<details>
<summary>21 lines</summary>

```
1. #!/bin/bash
2. 
3. # Copyright 2024 Canonical Ltd.
4. # See LICENSE file for licensing details.
5. 
6. # Pre-run script for integration test operator-workflows action.
7. # https://github.com/canonical/operator-workflows/blob/main/.github/workflows/integration_test.yaml
8. 
9. # Jenkins machine agent charm is deployed on lxd and Jenkins-k8s server charm is deployed on
10. # microk8s.
11. 
12. TESTING_MODEL="$(juju switch)"
13. 
14. # lxd should be install and init by a previous step in integration test action.
15. echo "bootstrapping lxd juju controller"
16. sg snap_microk8s -c "microk8s status --wait-ready"
17. sg snap_microk8s -c "juju bootstrap localhost localhost"
18. 
19. echo "Switching to testing model"
20. sg snap_microk8s -c "juju switch $TESTING_MODEL"
21.
```

</details>


### 💬 Copilot

Perfect! Now I have all the information. Let me create a comprehensive response with the full file contents.

## Complete Integration Test Exploration

Here are all the relevant files for the WordPress K8s operator integration tests using pytest-operator (not pytest-jubilant):

---

### 1. **conftest.py** - Full Content

```python
# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

"""Fixtures for the wordpress integration tests."""

import configparser
import json
import re
import secrets
from pathlib import Path
from typing import AsyncGenerator, Dict, Optional

import pytest
import pytest_asyncio
import swiftclient
import swiftclient.exceptions
import swiftclient.service
from juju.controller import Controller
from juju.model import Model
from pytest import Config
from pytest_operator.plugin import OpsTest

from tests.integration.helper import WordpressApp


@pytest.fixture(scope="module")
def model(ops_test: OpsTest) -\> Model:
    """Return the juju model object created by pytest-operator."""
    model = ops_test.model
    assert model
    return model


@pytest.fixture(scope="module", name="kube_config")
def kube_config_fixture(pytestconfig: Config):
    """The Kubernetes cluster configuration file."""
    kube_config = pytestconfig.getoption("--kube-config")
    assert kube_config, (
        "The Kubernetes config file path should not be empty, "
        "please include it in the --kube-config parameter"
    )
    return kube_config


@pytest_asyncio.fixture(scope="module", name="machine_controller")
async def machine_controller_fixture() -\> AsyncGenerator[Controller, None]:
    """The lxd controller."""
    controller = Controller()
    await controller.connect_controller("localhost")

    yield controller

    await controller.disconnect()


@pytest_asyncio.fixture(scope="module", name="machine_model")
async def machine_model_fixture(machine_controller: Controller) -\> AsyncGenerator[Model, None]:
    """The machine model for jenkins agent machine charm."""
    machine_model_name = f"mysql-machine-{secrets.token_hex(2)}"
    model = await machine_controller.add_model(machine_model_name)

    yield model

    await model.disconnect()


@pytest_asyncio.fixture(scope="module", name="wordpress")
async def wordpress_fixture(
    pytestconfig: Config, ops_test: OpsTest, model: Model, kube_config: str
) -\> WordpressApp:
    """Prepare the wordpress charm for integration tests."""
    exit_code, _, _ = await ops_test.juju("model-config", "logging-config=\<root\>=INFO;unit=DEBUG")
    assert exit_code == 0
    charm = pytestconfig.getoption("--charm-file")
    charm_dir = Path(__file__).parent.parent.parent
    if not charm:
        charm = await ops_test.build_charm(charm_dir)
    else:
        charm = Path(charm).absolute()
    wordpress_image = pytestconfig.getoption("--wordpress-image")
    if not wordpress_image:
        raise ValueError("--wordpress-image is required to run integration test")
    app = await model.deploy(
        charm,
        resources={
            "wordpress-image": wordpress_image,
        },
        num_units=1,
        series="jammy",
    )
    await model.wait_for_idle(status="blocked", apps=[app.name], timeout=30 * 60)
    return WordpressApp(app, ops_test=ops_test, kube_config=kube_config)


@pytest_asyncio.fixture(scope="module")
async def prepare_mysql(ops_test: OpsTest, wordpress: WordpressApp, model: Model):
    """Deploy and relate the mysql-k8s charm for integration tests."""
    app = await model.deploy("mysql-k8s", channel="8.0/stable", trust=True)
    await model.wait_for_idle(status="active", apps=[app.name], timeout=30 * 60)
    await model.relate(f"{wordpress.name}:database", f"{app.name}:database")
    await model.wait_for_idle(
        status="active", apps=[app.name, wordpress.name], timeout=40 * 60, idle_period=30
    )


@pytest_asyncio.fixture(scope="module")
async def prepare_machine_mysql(
    wordpress: WordpressApp, machine_controller: Controller, machine_model: Model, model: Model
):
    """Deploy and relate the mysql-k8s charm for integration tests."""
    await machine_model.deploy("mysql", channel="8.0/edge", trust=True)
    await machine_model.create_offer("mysql:database")
    await machine_model.wait_for_idle(status="active", apps=["mysql"], timeout=30 * 60)
    await model.relate(
        f"{wordpress.name}:database",
        f"{machine_controller.controller_name}:admin/{machine_model.name}.mysql",
    )


@pytest.fixture(scope="module", name="openstack_environment")
def openstack_environment_fixture(pytestconfig: Config):
    """Parse the openstack rc style configuration file from the --openstack-rc argument.

    Returns: a dictionary of environment variables and values, or None if --openstack-rc isn't
        provided.
    """
    rc_file = pytestconfig.getoption("--openstack-rc")
    if not rc_file:
        raise ValueError("--openstack-rc is required to run this test")
    with open(rc_file, encoding="utf-8") as rc_fo:
        rc_file = rc_fo.read()
    rc_file = re.sub("^export ", "", rc_file, flags=re.MULTILINE)
    openstack_conf = configparser.ConfigParser()
    openstack_conf.read_string("[DEFAULT]\n" + rc_file)
    return {k.upper(): v for k, v in openstack_conf["DEFAULT"].items()}


@pytest.fixture(scope="module", name="swift_conn")
def swift_conn_fixture(openstack_environment) -\> Optional[swiftclient.Connection]:
    """Create a swift connection client."""
    return swiftclient.Connection(
        authurl=openstack_environment["OS_AUTH_URL"],
        auth_version="3",
        user=openstack_environment["OS_USERNAME"],
        key=openstack_environment["OS_PASSWORD"],
        os_options={
            "user_domain_name": openstack_environment["OS_USER_DOMAIN_ID"],
            "project_domain_name": openstack_environment["OS_PROJECT_DOMAIN_ID"],
            "project_name": openstack_environment["OS_PROJECT_NAME"],
        },
    )


@pytest.fixture(scope="module", name="swift_config")
def swift_config_fixture(
    ops_test: OpsTest,
    swift_conn: swiftclient.Connection,
    openstack_environment: Dict[str, str],
) -\> Dict[str, str]:
    """Create a swift config dict that can be used for wp_plugin_openstack-objectstorage_config."""
    swift_service = swiftclient.service.SwiftService(
        options={
            "auth_version": "3",
            "os_auth_url": openstack_environment["OS_AUTH_URL"],
            "os_username": openstack_environment["OS_USERNAME"],
            "os_password": openstack_environment["OS_PASSWORD"],
            "os_project_name": openstack_environment["OS_PROJECT_NAME"],
            "os_project_domain_name": openstack_environment["OS_PROJECT_DOMAIN_ID"],
        }
    )
    container = f"wordpress_{ops_test.model_name}"
    # if the container exists, remove the container
    swift_service.delete(container=container)
    # create a swift container for our test
    swift_conn.put_container(container)
    # change container ACL to allow us getting an object by HTTP request without any authentication
    # the swift server will act as a static HTTP server after this
    swift_service.post(container=container, options={"read_acl": ".r:*,.rlistings"})

    return {
        "auth-url": openstack_environment["OS_AUTH_URL"] + "/v3",
        "bucket": container,
        "password": openstack_environment["OS_PASSWORD"],
        "object-prefix": "wp-content/uploads/",
        "region": openstack_environment["OS_REGION_NAME"],
        "tenant": openstack_environment["OS_PROJECT_NAME"],
        "domain": openstack_environment["OS_PROJECT_DOMAIN_ID"],
        "swift-url": swift_conn.url,
        "username": openstack_environment["OS_USERNAME"],
        "copy-to-swift": "1",
        "serve-from-swift": "1",
        "remove-local-file": "0",
    }


@pytest_asyncio.fixture(scope="module")
async def prepare_swift(wordpress: WordpressApp, swift_config: Dict[str, str]):
    """Configure the wordpress charm to use openstack swift object storage."""
    await wordpress.set_config(
        {"wp_plugin_openstack-objectstorage_config": json.dumps(swift_config)}
    )
    await wordpress.model.wait_for_idle(status="active", apps=[wordpress.name], timeout=30 * 60)


@pytest_asyncio.fixture(scope="module")
async def prepare_nginx_ingress(wordpress: WordpressApp, prepare_mysql):
    """Deploy and relate nginx-ingress-integrator charm for integration tests."""
    await wordpress.model.deploy(
        "nginx-ingress-integrator", channel="latest/edge", series="focal", revision=133, trust=True
    )
    await wordpress.model.wait_for_idle(apps=["nginx-ingress-integrator"], timeout=30 * 60)
    await wordpress.model.relate(f"{wordpress.name}:nginx-route", "nginx-ingress-integrator")
    await wordpress.model.wait_for_idle(status="active")


@pytest_asyncio.fixture(scope="module")
async def prepare_prometheus(wordpress: WordpressApp, prepare_mysql):
    """Deploy and relate prometheus-k8s charm for integration tests."""
    prometheus = await wordpress.model.deploy("prometheus-k8s", channel="1/stable", trust=True)
    await wordpress.model.wait_for_idle(
        status="active", apps=[prometheus.name], raise_on_error=False, timeout=30 * 60
    )
    await wordpress.model.relate(f"{wordpress.name}:metrics-endpoint", prometheus.name)
    await wordpress.model.wait_for_idle(
        status="active",
        apps=[prometheus.name, wordpress.name],
        timeout=20 * 60,
        raise_on_error=False,
    )


@pytest_asyncio.fixture(scope="module")
async def prepare_loki(wordpress: WordpressApp, prepare_mysql):
    """Deploy and relate loki-k8s charm for integration tests."""
    loki = await wordpress.model.deploy("loki-k8s", channel="1/stable", trust=True)
    await wordpress.model.wait_for_idle(apps=[loki.name], status="active", timeout=20 * 60)
    await wordpress.model.relate(f"{wordpress.name}:logging", loki.name)
    await wordpress.model.wait_for_idle(
        apps=[loki.name, wordpress.name], status="active", timeout=40 * 60
    )
```

---

### 2. **test_*.py Files** - All Test Files

#### **test_core.py** - Full Content

```python
# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

"""Integration tests for WordPress charm core functionality."""

import io
import json
import secrets
import urllib.parse

import PIL.Image
import pytest
import requests
from pytest_operator.plugin import OpsTest

from tests.integration.helper import WordpressApp, WordpressClient


@pytest.mark.usefixtures("prepare_mysql")
@pytest.mark.abort_on_fail
async def test_wordpress_up(wordpress: WordpressApp, ops_test: OpsTest):
    """
    arrange: after WordPress charm has been deployed and db relation established.
    act: test wordpress server is up.
    assert: wordpress service is up.
    """
    await wordpress.model.wait_for_idle(status="active")
    for unit_ip in await wordpress.get_unit_ips():
        assert requests.get(f"http://{unit_ip}", timeout=10).status_code == 200


@pytest.mark.usefixtures("prepare_mysql", "prepare_swift")
async def test_wordpress_functionality(wordpress: WordpressApp):
    """
    arrange: after WordPress charm has been deployed and db relation established.
    act: test WordPress basic functionality (login, post, comment).
    assert: WordPress works normally as a blog site.
    """
    for unit_ip in await wordpress.get_unit_ips():
        WordpressClient.run_wordpress_functionality_test(
            host=unit_ip,
            admin_username="admin",
            admin_password=await wordpress.get_default_admin_password(),
        )


@pytest.mark.usefixtures("prepare_mysql")
async def test_change_upload_limit(wordpress: WordpressApp):
    """
    arrange: after WordPress charm has been deployed and db relation established.
    act: change upload limit related settings.
    assert: upload limit change should be reflected in the upload page.
    """
    await wordpress.set_config({"upload_max_filesize": "16M"})
    await wordpress.model.wait_for_idle(status="active")
    password = await wordpress.get_default_admin_password()
    for unit_ip in await wordpress.get_unit_ips():
        wordpress_client = WordpressClient(
            host=unit_ip,
            username="admin",
            password=password,
            is_admin=True,
        )
        text = wordpress_client.get_post(f"http://{unit_ip}/wp-admin/upload.php")
        # upload limit = min(upload_max_filesize, post_max_size)
        assert "Maximum upload file size: 8 MB" in text
    await wordpress.set_config({"post_max_size": "16M"})
    await wordpress.model.wait_for_idle(status="active")
    for unit_ip in await wordpress.get_unit_ips():
        wordpress_client = WordpressClient(
            host=unit_ip,
            username="admin",
            password=password,
            is_admin=True,
        )
        text = wordpress_client.get_post(f"http://{unit_ip}/wp-admin/upload.php")
        assert "Maximum upload file size: 16 MB" in text


@pytest.mark.usefixtures("prepare_mysql", "prepare_swift")
async def test_openstack_object_storage_plugin(
    wordpress: WordpressApp,
    swift_conn,
):
    """
    arrange: after charm deployed, db relation established and openstack swift server ready.
    act: update charm configuration for openstack object storage plugin.
    assert: openstack object storage plugin should be installed after the config update and
        WordPress openstack swift object storage integration should be set up properly.
        After openstack swift plugin activated, an image file uploaded to one unit through
        WordPress media uploader should be accessible from all units.
    """
    container = await wordpress.get_swift_bucket()
    for idx, unit_ip in enumerate(await wordpress.get_unit_ips()):
        image = PIL.Image.new("RGB", (500, 500), color=(idx, 0, 0))
        nonce = secrets.token_hex(8)
        filename = f"{nonce}.{unit_ip}.{idx}.jpg"
        image_buf = io.BytesIO()
        image.save(image_buf, format="jpeg")
        image = image_buf.getvalue()
        wordpress_client = WordpressClient(
            host=unit_ip,
            username="admin",
            password=await wordpress.get_default_admin_password(),
            is_admin=True,
        )
        image_urls = wordpress_client.upload_media(filename=filename, content=image)["urls"]
        swift_object_list = [
            o["name"] for o in swift_conn.get_container(container, full_listing=True)[1]
        ]
        assert any(nonce in f for f in swift_object_list), (
            "media files uploaded should be stored in swift object storage"
        )
        source_url = min(image_urls, key=len)
        for image_url in image_urls:
            assert requests.get(image_url, timeout=10).status_code == 200, (
                "the original image and resized images should be accessible from the WordPress site"
            )
        for host in await wordpress.get_unit_ips():
            url_components = list(urllib.parse.urlsplit(source_url))
            url_components[1] = host
            url = urllib.parse.urlunsplit(url_components)
            assert requests.get(url, timeout=10).content == image, (
                "image downloaded from WordPress should match the image uploaded"
            )


@pytest.mark.usefixtures("prepare_mysql", "prepare_swift")
async def test_apache_config(wordpress: WordpressApp, ops_test: OpsTest):
    """
    arrange: after WordPress charm has been deployed and db relation established.
    act: update the config to trigger a new reconciliation.
    assert: apache config test works properly and prevents the restart of the server.
    """
    await wordpress.set_config(
        {"initial_settings": json.dumps({"user_name": "foo", "admin_email": "bar@example.com"})}
    )
    await wordpress.wait_for_wordpress_idle()
    exit_code, stdout, _ = await ops_test.juju("debug-log", "--replay")
    assert exit_code == 0
    assert "Apache config docker-php-swift-proxy is enabled" in stdout
    assert "Conf docker-php-swift-proxy already enabled" not in stdout


@pytest.mark.usefixtures("prepare_mysql")
async def test_uploads_owner(wordpress: WordpressApp, ops_test: OpsTest):
    """
    arrange: after WordPress charm has been deployed and db relation established.
    act: get uploads directory owner
    assert: uploads belongs to wordpress user.
    """
    cmd = [
        "juju",
        "ssh",
        f"{wordpress.app.name}/0",
        "stat",
        '--printf="%u"',
        "/var/www/html/wp-content/uploads",
    ]

    retcode, stdout, _ = await ops_test.run(*cmd)
    assert retcode == 0
    assert stdout.strip() == "584792"
```

#### **test_addon.py** - Full Content

```python
# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

"""Integration tests for WordPress charm COS addon management."""

from typing import List, Set

import pytest

from charm import WordpressCharm
from tests.integration.helper import WordpressApp


@pytest.mark.usefixtures("prepare_mysql", "prepare_swift")
async def test_wordpress_install_uninstall_themes(wordpress: WordpressApp):
    """
    arrange: after WordPress charm has been deployed and db relation established.
    act: change themes setting in config.
    assert: themes should be installed and uninstalled accordingly.
    """
    theme_change_list: List[Set[str]] = [
        {"twentyfifteen", "classic"},
        {"tt1-blocks", "twentyfifteen"},
        {"tt1-blocks"},
        {"twentyeleven"},
        set(),
    ]
    for themes in theme_change_list:
        await wordpress.set_config({"themes": ",".join(themes)})
        await wordpress.model.wait_for_idle(status="active", apps=[wordpress.name])

        for wordpress_client in await wordpress.client_for_units():
            expected_themes = themes
            expected_themes.update(WordpressCharm._WORDPRESS_DEFAULT_THEMES)
            actual_themes = set(wordpress_client.list_themes())
            assert expected_themes == actual_themes, (
                f"theme installed {themes} should match themes setting in config"
            )


@pytest.mark.usefixtures("prepare_mysql", "prepare_swift")
async def test_wordpress_theme_installation_error(wordpress: WordpressApp):
    """
    arrange: after WordPress charm has been deployed and db relation established.
    act: install a nonexistent theme.
    assert: charm should switch to blocked state and the reason should be included in the status
        message.
    """
    invalid_theme = "invalid-theme-sgkeahrgalejr"
    await wordpress.set_config({"themes": invalid_theme})
    await wordpress.wait_for_wordpress_idle()

    for unit in wordpress.get_units():
        assert unit.workload_status == "blocked", (
            "status should be 'blocked' since the theme in themes config does not exist"
        )

        assert invalid_theme in unit.workload_status_message, (
            "status message should contain the reason why it's blocked"
        )

    await wordpress.set_config({"themes": ""})
    await wordpress.wait_for_wordpress_idle(status="active")


@pytest.mark.usefixtures("prepare_mysql", "prepare_swift")
async def test_wordpress_install_uninstall_plugins(wordpress: WordpressApp):
    """
    arrange: after WordPress charm has been deployed and db relation established.
    act: change plugins setting in config.
    assert: plugins should be installed and uninstalled accordingly.
    """
    plugin_change_list: List[Set[str]] = [
        {"classic-editor", "classic-widgets"},
        {"classic-editor"},
        {"classic-widgets"},
        set(),
    ]
    for plugins in plugin_change_list:
        await wordpress.set_config({"plugins": ",".join(plugins)})
        await wordpress.wait_for_wordpress_idle(status="active")

        for wordpress_client in await wordpress.client_for_units():
            expected_plugins = plugins
            expected_plugins.update(WordpressCharm._WORDPRESS_DEFAULT_PLUGINS)
            actual_plugins = set(wordpress_client.list_plugins())
            assert expected_plugins == actual_plugins, (
                f"plugin installed {plugins} should match plugins setting in config"
            )


@pytest.mark.usefixtures("prepare_mysql", "prepare_swift")
async def test_wordpress_plugin_installation_error(wordpress: WordpressApp):
    """
    arrange: after WordPress charm has been deployed and db relation established.
    act: install a nonexistent plugin.
    assert: charm should switch to blocked state and the reason should be included in the status
        message.
    """
    invalid_plugin = "invalid-plugin-sgkeahrgalejr"
    await wordpress.set_config({"plugins": invalid_plugin})
    await wordpress.wait_for_wordpress_idle()

    for unit in wordpress.get_units():
        assert unit.workload_status == "blocked", (
            "status should be 'blocked' since the plugin in plugins config does not exist"
        )

        assert invalid_plugin in unit.workload_status_message, (
            "status message should contain the reason why it's blocked"
        )

    await wordpress.set_config({"plugins": ""})
    await wordpress.wait_for_wordpress_idle(status="active")
```

#### **test_cos_grafana.py** - Full Content

```python
# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

"""Integration tests for WordPress charm COS integration."""

import functools

import pytest
import requests
from juju.action import Action
from juju.client._definitions import FullStatus

from tests.integration.helper import WordpressApp, wait_for


def dashboard_exist(loggedin_session: requests.Session, unit_address: str):
    """Checks if the WordPress dashboard is registered in Grafana.

    Args:
        loggedin_session: Requests session that's authorized to make API calls.
        unit_address: Grafana unit address.

    Returns:
        True if all dashboard is found. False otherwise.
    """
    dashboards = loggedin_session.get(
        f"http://{unit_address}:3000/api/search",
        timeout=10,
        params={"query": "Wordpress Operator Overview"},
    ).json()
    return len(dashboards)


@pytest.mark.usefixtures("prepare_mysql")
async def test_grafana_integration(
    wordpress: WordpressApp,
):
    """
    arrange: after WordPress charm has been deployed and relations established among cos.
    act: grafana charm joins relation
    assert: grafana wordpress dashboard can be found
    """
    grafana = await wordpress.model.deploy("grafana-k8s", channel="1/stable", trust=True)
    await wordpress.model.wait_for_idle(status="active", apps=["grafana-k8s"], timeout=20 * 60)
    await wordpress.model.add_relation("wordpress-k8s:grafana-dashboard", "grafana-k8s")
    await wordpress.model.wait_for_idle(
        status="active", apps=["grafana-k8s", "wordpress-k8s"], timeout=30 * 60
    )
    action: Action = await grafana.units[0].run_action("get-admin-password")
    await action.wait()
    password = action.results["admin-password"]

    status: FullStatus = await wordpress.model.get_status(filters=[grafana.name])
    for unit in status.applications[grafana.name].units.values():
        sess = requests.session()
        sess.post(
            f"http://{unit.address}:3000/login",
            json={
                "user": "admin",
                "password": password,
            },
        ).raise_for_status()
        await wait_for(
            functools.partial(dashboard_exist, loggedin_session=sess, unit_address=unit.address),
            timeout=60 * 20,
        )
```

#### **test_cos_loki.py** - Full Content

```python
# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

"""Integration tests for WordPress charm COS integration."""

import functools
from typing import Iterable

import kubernetes
import pytest
import requests
from juju.client._definitions import FullStatus

from tests.integration.helper import WordpressApp, wait_for


def log_files_exist(unit_address: str, application_name: str, filenames: Iterable[str]) -\> bool:
    """Returns whether log filenames exist in Loki logs query.

    Args:
        unit_address: Loki unit ip address.
        application_name: Application name to query logs for.
        filenames: Expected filenames to be present in logs collected by Loki.

    Returns:
        True if log files with logs exists. False otherwise.
    """
    series = requests.get(f"http://{unit_address}:3100/loki/api/v1/series", timeout=10).text
    assert application_name in series
    log_query = requests.get(
        f"http://{unit_address}:3100/loki/api/v1/query",
        timeout=10,
        params={"query": f'{{juju_application="{application_name}"}}'},
    ).json()

    return len(log_query["data"]["result"]) != 0


@pytest.mark.abort_on_fail
@pytest.mark.usefixtures("prepare_mysql", "prepare_loki")
async def test_loki_integration(
    wordpress: WordpressApp,
    kube_config: str,
):
    """
    arrange: after WordPress charm has been deployed and relations established.
    act: loki charm joins relation
    assert: loki joins relation successfully, logs are being output to container and to files for
        loki to scrape.
    """
    status: FullStatus = await wordpress.model.get_status(filters=["loki-k8s"])
    for unit in status.applications["loki-k8s"].units.values():
        await wait_for(
            functools.partial(
                log_files_exist,
                unit.address,
                wordpress.name,
                ("/var/log/apache2/error.*.log", "/var/log/apache2/access.*.log"),
            ),
            timeout=10 * 60,
        )
    kubernetes.config.load_kube_config(config_file=kube_config)
    kube_core_client = kubernetes.client.CoreV1Api()

    kube_log = kube_core_client.read_namespaced_pod_log(
        name=f"{wordpress.name}-0", namespace=wordpress.model.name, container="wordpress"
    )
    assert kube_log
```

#### **test_cos_prometheus.py** - Full Content

```python
# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

"""Integration tests for WordPress charm COS integration."""

import pytest
import requests
from juju.client._definitions import FullStatus

from cos import APACHE_PROMETHEUS_SCRAPE_PORT
from tests.integration.helper import WordpressApp


@pytest.mark.abort_on_fail
@pytest.mark.usefixtures("prepare_mysql", "prepare_prometheus")
async def test_prometheus_integration(
    wordpress: WordpressApp,
):
    """
    arrange: none.
    act: deploy the WordPress charm and relations established with prometheus.
    assert: prometheus metrics endpoint for prometheus is active and prometheus has active scrape
        targets.
    """
    for unit_ip in await wordpress.get_unit_ips():
        res = requests.get(f"http://{unit_ip}:{APACHE_PROMETHEUS_SCRAPE_PORT}", timeout=10)
        assert res.status_code == 200
    status: FullStatus = await wordpress.model.get_status(filters=["prometheus-k8s"])
    for unit in status.applications["prometheus-k8s"].units.values():
        query_targets = requests.get(
            f"http://{unit.address}:9090/api/v1/targets", timeout=10
        ).json()
        assert len(query_targets["data"]["activeTargets"])
```

#### **test_external.py** - Full Content

```python
# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

"""Integration tests for WordPress charm external service integration."""

import secrets

import pytest
from pytest import Config

from tests.integration.helper import WordpressApp, WordpressClient


@pytest.mark.requires_secret
@pytest.mark.usefixtures("prepare_mysql", "prepare_swift")
async def test_akismet_plugin(
    wordpress: WordpressApp,
    pytestconfig: Config,
):
    """
    arrange: after WordPress charm has been deployed, db relation established.
    act: update charm configuration for Akismet plugin.
    assert: Akismet plugin should be activated and spam detection function should be working.
    """
    akismet_api_key = pytestconfig.getoption("--akismet-api-key")
    if not akismet_api_key:
        raise ValueError("--akismet-api-key is required for running this test")

    await wordpress.set_config({"wp_plugin_akismet_key": akismet_api_key})
    await wordpress.wait_for_wordpress_idle(status="active")

    for wordpress_client in await wordpress.client_for_units():
        post = wordpress_client.create_post(secrets.token_hex(8), secrets.token_hex(8))
        wordpress_client.create_comment(
            post_id=post["id"], post_link=post["link"], content="akismet-guaranteed-spam"
        )
        wordpress_client.create_comment(
            post_id=post["id"], post_link=post["link"], content="test comment"
        )
        assert len(wordpress_client.list_comments(status="spam", post_id=post["id"])) == 1, (
            "Akismet plugin should move the triggered spam comment to the spam section"
        )
        assert len(wordpress_client.list_comments(post_id=post["id"])) == 1, (
            "Akismet plugin should keep the normal comment"
        )


@pytest.mark.requires_secret
@pytest.mark.usefixtures("prepare_mysql")
async def test_openid_plugin(
    wordpress: WordpressApp,
    pytestconfig: Config,
):
    """
    arrange: after WordPress charm has been deployed, db relation established.
    act: update charm configuration for OpenID plugin.
    assert: A WordPress user should be created with correct roles according to the config.
    """
    openid_username = pytestconfig.getoption("--openid-username")
    if not openid_username:
        raise ValueError("--openid-username is required for running this test")
    openid_password = pytestconfig.getoption("--openid-password")
    if not openid_password:
        raise ValueError("--openid-password is required for running this test")
    launchpad_team = pytestconfig.getoption("--launchpad-team")
    if not launchpad_team:
        raise ValueError("--launchpad-team is required for running this test")
    await wordpress.set_config({"wp_plugin_openid_team_map": f"{launchpad_team}=administrator"})
    await wordpress.wait_for_wordpress_idle(status="active")

    for idx, unit_ip in enumerate(await wordpress.get_unit_ips()):
        # wordpress-teams-integration has a bug causing desired roles not to be assigned to
        # the user when first-time login. Login twice by creating the WordPressClient client twice
        # for the very first time.
        for attempt in range(2 if idx == 0 else 1):
            try:
                wordpress_client = WordpressClient(
                    host=unit_ip,
                    username=openid_username,
                    password=openid_password,
                    is_admin=True,
                    use_launchpad_login=True,
                )
            except AssertionError:
                if attempt == 0:
                    continue
                raise
        assert "administrator" in wordpress_client.list_roles(), (
            "An launchpad OpenID account should be associated with the WordPress admin user"
        )
```

#### **test_ingress.py** - Full Content

```python
# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

"""Integration tests for WordPress charm ingress integration."""

import kubernetes
import pytest
import requests

from tests.integration.helper import WordpressApp


@pytest.mark.usefixtures("prepare_mysql", "prepare_nginx_ingress", "prepare_swift")
async def test_ingress(wordpress: WordpressApp):
    """
    arrange: after WordPress charm has been deployed and db relation established.
    act: deploy the nginx-ingress-integrator charm and create the relation between ingress charm
        and WordPress charm.
    assert: A Kubernetes ingress should be created and the ingress should accept HTTPS connections.
    """
    response = requests.get("http://127.0.0.1", headers={"Host": wordpress.name}, timeout=5)
    assert response.status_code == 200 and "wordpress" in response.text.lower(), (
        "Ingress should accept requests to WordPress and return correct contents"
    )

    new_hostname = "wordpress.test"
    await wordpress.set_config({"blog_hostname": new_hostname})
    await wordpress.model.wait_for_idle(status="active")
    response = requests.get(
        "https://127.0.0.1", headers={"Host": new_hostname}, timeout=5, verify=False
    )  # nosec
    assert response.status_code == 200 and "wordpress" in response.text.lower(), (
        "Ingress should update the server name indication based routing after blog_hostname updated"
    )


@pytest.mark.usefixtures("prepare_mysql", "prepare_nginx_ingress", "prepare_swift")
async def test_ingress_modsecurity(
    wordpress: WordpressApp,
    kube_config: str,
):
    """
    arrange: WordPress charm is running and Nginx ingress integrator deployed and related to it.
    act: update the use_nginx_ingress_modsec WordPress charm config.
    assert: A Kubernetes ingress modsecurity should be enabled and proper rules should be set up
        for WordPress.
    """
    await wordpress.set_config({"use_nginx_ingress_modsec": "true"})
    await wordpress.model.wait_for_idle(status="active")

    kubernetes.config.load_kube_config(config_file=kube_config)
    kube = kubernetes.client.NetworkingV1Api()

    def get_ingress_annotation():
        """Get ingress annotations from kubernetes.

        Returns:
            Nginx ingress annotations.
        """
        ingress_list = kube.list_namespaced_ingress(namespace=wordpress.model.name).items
        return ingress_list[0].metadata.annotations

    ingress_annotations = get_ingress_annotation()
    assert ingress_annotations["nginx.ingress.kubernetes.io/enable-modsecurity"] == "true"
    assert (
        ingress_annotations["nginx.ingress.kubernetes.io/enable-owasp-modsecurity-crs"] == "true"
    )
    assert (
        'SecAction "id:900130,phase:1,nolog,pass,t:none,setvar:tx.crs_exclusions_wordpress=1"\n'
        in ingress_annotations["nginx.ingress.kubernetes.io/modsecurity-snippet"]
    )
```

#### **test_machine.py** - Full Content

```python
# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

"""Integration tests for WordPress charm core functionality with mysql machine charm."""

import functools

import pytest
from helper import get_mysql_primary_unit, wait_for
from juju.application import Application
from juju.model import Model

from tests.integration.helper import WordpressApp


@pytest.mark.usefixtures("prepare_machine_mysql")
async def test_database_endpoints_changed(machine_model: Model, wordpress: WordpressApp):
    """
    arrange: given related mysql charm with 3 units.
    act: when the leader mysql unit is removed and hence the endpoints changed event fired.
    assert: the WordPress correctly connects to the newly elected leader endpoint.
    """
    model: Model = wordpress.model
    mysql: Application = machine_model.applications["mysql"]
    await mysql.add_unit(2)
    await machine_model.wait_for_idle(["mysql"], timeout=30 * 60)
    await model.wait_for_idle(["wordpress-k8s"])

    leader = await get_mysql_primary_unit(mysql.units)
    assert leader, "No leader unit found."
    await mysql.destroy_unit(leader.name)
    await machine_model.wait_for_idle(["mysql"], timeout=30 * 60, idle_period=30)
    await model.wait_for_idle(["wordpress-k8s"])

    leader = await wait_for(functools.partial(get_mysql_primary_unit, mysql.units))

    assert await leader.get_public_address() in await wordpress.get_wordpress_config(), (
        "MySQL leader unit IP not found."
    )
```

---

### 3. **helper.py** - Full Content (Complete File)

```python
# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

"""Helper classes and functions for integration tests."""

import asyncio
import html
import inspect
import json
import logging
import mimetypes
import re
import secrets
import time
from typing import (
    Any,
    Awaitable,
    Callable,
    Dict,
    Iterable,
    List,
    Optional,
    Tuple,
    Type,
    TypedDict,
    Union,
)

import kubernetes
import requests
import yaml
from juju.application import Application
from juju.model import Model
from juju.unit import Unit
from pytest_operator.plugin import OpsTest

logger = logging.getLogger(__name__)


def retry(times: int, exceptions: Tuple[Type[Exception]], interval=5):
    """Retry decorator to catch exceptions and retry.

    Args:
        times: Number of times to retry.
        exceptions: Types of exceptions to catch to retry.
        interval: Interval between retries.
    """

    def decorator(func: Callable):
        """The decorating wrapper function.

        Args:
            func: Function to retry.
        """

        async def newfn(*args: Any, **kwargs: Any):
            """Newly wrapped function with retry.

            Returns:
                The newly decorated function with retry capability.
            """
            attempt = 0
            while attempt \< times:
                try:
                    if asyncio.iscoroutinefunction(func):
                        return await func(*args, **kwargs)
                    return func(*args, **kwargs)
                except exceptions as exc:
                    logger.warning(
                        "Function failed with exception %s, retrying %s/%s times.",
                        exc,
                        attempt,
                        times,
                    )
                    attempt += 1
                time.sleep(interval)
            if asyncio.iscoroutinefunction(func):
                return await func(*args, **kwargs)
            return func(*args, **kwargs)

        return newfn

    return decorator


class WordPressPost(TypedDict):
    """Typing for a WordPress post object.

    Attrs:
        id: A numeric identifier of a given post.
        link: A url path to given post.
    """

    id: int
    link: str


class WordpressClient:
    """A very simple WordPress client for test purpose only."""

    @classmethod
    def run_wordpress_functionality_test(cls, host: str, admin_username: str, admin_password: str):
        """Run standard WordPress functionality test suite.

        Args:
            host: ip address or hostname of the WordPress instance.
            admin_username: WordPress admin user username.
            admin_password: WordPress admin user password.
        """
        wp_client = cls(host=host, username=admin_username, password=admin_password, is_admin=True)
        post_title = secrets.token_hex(16)
        post_content = secrets.token_hex(16)
        post = wp_client.create_post(
            title=post_title,
            content=post_content,
        )
        homepage = wp_client.get_homepage()
        assert post_title in homepage, "admin user should be able to create a new post"
        comment = secrets.token_hex(16)
        post_link = post["link"]
        comment_link = wp_client.create_comment(
            post_id=post["id"],
            post_link=post_link,
            content=comment,
        )
        assert comment_link.startswith(post_link) and comment in wp_client.get_post(post_link), (
            "admin user should be able to create a comment"
        )

    def __init__(
        self,
        host: str,
        username: str,
        password: str,
        is_admin: bool,
        use_launchpad_login: bool = False,
    ):
        """Initialize the WordPress JSON API client.

        Args:
            host: ip address or hostname of the WordPress instance.
            username: WordPress user username.
            password: WordPress user password.
            is_admin: if this user is a WordPress admin.
            use_launchpad_login: Use Launchpad OpenID to login instead of WordPress userpass.

        Raises:
            RuntimeError: if invalid credentials were used to login to WordPress.
            ValueError: if non-admin account was used to access /wp-json/ endpoint or the /wp-json/
                endpoint was not set through permalink.
        """
        self.host = host
        self.username = username
        self.password = password
        self._session = requests.session()
        self.timeout = 10
        if use_launchpad_login:
            self.login_using_launchpad(username, password)
        else:
            if not self._login():
                raise RuntimeError(f"login failed with username {username}")
        # By default, WordPress does not expose the /wp-json/ endpoint test if /wp-json
        # is exposed, and expose that with a permalink setting if not
        try:
            self._get(f"http://{self.host}/wp-json/").json()
        except requests.exceptions.JSONDecodeError as exc:
            if not is_admin:
                raise ValueError(
                    "set options-permalink manually or login with an admin account"
                ) from exc
            self._set_options_permalink()

    def _get(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        except_status_code: Optional[int] = None,
    ) -\> requests.Response:
        """HTTP GET using the instance session.

        The instance session contains user's login session cookies, so this method can assess
        restricted resources on WordPress.

        Args:
            url: Same as the ``url`` argument in :meth:`requests.Session.get`.
            headers: Same as ``url``  in :meth:`requests.Session.get`.
            except_status_code: Except the response http status code,
                raise :exc:`requests.HTTPError` if not match.

        Raises:
            HTTPError: if unexpected status code was returned.

        Returns:
            An instance of :class:`requests.Response`.
        """
        request = requests.Request("GET", url, headers=headers)
        prepped = self._session.prepare_request(request)
        response = self._session.send(prepped, timeout=self.timeout)
        if except_status_code is not None and response.status_code != except_status_code:
            raise requests.HTTPError(request=request, response=response)
        return response

    def _post(
        self,
        url: str,
        json_: Optional[dict] = None,
        data: Optional[Union[bytes, Dict[str, Any]]] = None,
        headers: Optional[Dict[str, str]] = None,
        except_status_code: Optional[int] = None,
    ) -\> requests.Response:
        """HTTP GET using the instance session.

        The instance session contains user's login session cookies, so this method can assess
        restricted resources on WordPress.

        Args:
            url: Same as the ``url`` argument in :meth:`requests.Session.post`.
            json_: Same as the ``json`` argument in :meth:`requests.Session.post`.
            data: Same as the ``data`` argument in :meth:`requests.Session.post`.
            headers: Same as the ``url``  in :meth:`requests.Session.post`.
            except_status_code: Except the response http status code,
                raise :exc:`requests.HTTPError` if not match.

        Raises:
            HTTPError: if unexpected status code was returned.

        Returns:
            An instance of :class:`requests.Response`.
        """
        request = requests.Request("POST", url, json=json_, data=data, headers=headers)
        prepped = self._session.prepare_request(request)
        response = self._session.send(prepped, timeout=self.timeout)
        if except_status_code is not None and response.status_code != except_status_code:
            raise requests.HTTPError(request=request, response=response)
        return response

    def _login(self) -\> bool:
        """Login WordPress with current username and password, set session cookies.

        Returns:
            True if login successfully.
        """
        self._get(f"http://{self.host}/wp-login.php")
        response = self._post(
            f"http://{self.host}/wp-login.php",
            data={
                "log": self.username,
                "pwd": self.password,
                "wp-submit": "Log In",
                "redirect_to": f"http://{self.host}/wp-admin/",
                "testcookie": 1,
            },
            except_status_code=200,
        )
        return response.url == f"http://{self.host}/wp-admin/"

    def _set_options_permalink(self) -\> None:
        """Set WordPress permalink option to /%postname%/."""
        options_permalink_page = self._get(
            f"http://{self.host}/wp-admin/options-permalink.php"
        ).text
        wp_nonce_matches = re.findall(
            'name="_wpnonce" value="([a-zA-Z0-9]+)"', options_permalink_page
        )
        assert wp_nonce_matches, f"wpnonce not found in {options_permalink_page}"
        wp_nonce = wp_nonce_matches[0]
        self._post(
            f"http://{self.host}/wp-admin/options-permalink.php",
            data={
                "_wpnonce": wp_nonce,
                "_wp_http_referer": "/wp-admin/options-permalink.php",
                "selection": "/%postname%/",
                "permalink_structure": "/%postname%/",
                "submit": "Save Changes",
            },
            except_status_code=200,
        )

    def _gen_wp_rest_nonce(self) -\> str:
        """Generate a nonce for WordPress REST API.

        Returns:
            (str) A WordPress nonce for WordPress JSON REST API.
        """
        new_post_page = self._get(f"http://{self.host}/wp-admin/post-new.php").text
        nonce: str = json.loads(re.findall("var wpApiSettings = ([^;]+);", new_post_page)[0])[
            "nonce"
        ]
        return nonce

    def create_post(
        self, title: str, content: str, featured_media: Optional[int] = None
    ) -\> WordPressPost:
        """Create a WordPress post using wp-json API, return post object.

        Args:
            title (str): Title of the post.
            content (str): Content of the post.
            featured_media (Optional[int]): Media ID for the featured media of the post.

        Returns:
            Post object returned from WordPress REST API.
        """
        body: Dict[str, Union[str, int]] = {
            "status": "publish",
            "title": title,
            "content": content,
        }
        if featured_media is not None:
            body["featured_media"] = featured_media
        response = self._post(
            f"http://{self.host}/wp-json/wp/v2/posts/",
            json_=body,
            headers={"X-WP-Nonce": self._gen_wp_rest_nonce()},
            except_status_code=201,
        )
        return response.json()

    def create_comment(self, post_id: int, post_link: str, content: str) -\> str:
        """Add a comment to a WordPress post using HTML form, return url link of the new comment.

        Args:
            post_id: ID of the post that the new comment will be attached to.
            post_link: URL of the post that the new comment will be attached to.
            content: Content of the new comment.

        Raises:
            ValueError: if same comment already exists.

        Returns:
            (str) URL pointed to the comment created.
        """
        post_page = self._get(post_link)
        nonce = re.findall(
            'name="_wp_unfiltered_html_comment_disabled" value="([a-zA-Z0-9]+)"', post_page.text
        )[0]

        response = self._post(
            f"http://{self.host}/wp-comments-post.php",
            data={
                "comment": content,
                "submit": "Post Comment",
                "comment_post_ID": post_id,
                "comment_parent": "0",
                "_wp_unfiltered_html_comment": nonce,
            },
            except_status_code=200,
        )
        if "Duplicate comment detected" in response.text:
            raise ValueError(f"Duplicate comment detected: {content!r}")
        return response.url

    def get_homepage(self) -\> str:
        """Get the WordPress homepage source (HTML).

        Returns:
            (str) The WordPress homepage content, HTML.
        """
        return self._get(f"http://{self.host}").text

    def get_post(self, post_link: str) -\> str:
        """Get the WordPress blog post page source (HTML).

        Args:
            post_link: URL to the WordPress post.

        Returns:
            (str) The WordPress homepage content, HTML.
        """
        return self._get(post_link).text

    def list_themes(self) -\> List[str]:
        """List all installed WordPress theme slugs.

        Return:
            (List[str]) WordPress themes Installed.
        """
        response = self._get(
            f"http://{self.host}/wp-json/wp/v2/themes?per_page=100",
            headers={"X-WP-Nonce": self._gen_wp_rest_nonce()},
            except_status_code=200,
        )
        return [t["stylesheet"] for t in response.json()]

    def list_plugins(self) -\> List[str]:
        """List all installed WordPress plugin slugs.

        Return:
            (List[str]) WordPress plugins Installed.
        """
        response = self._get(
            f"http://{self.host}/wp-json/wp/v2/plugins?per_page=100",
            headers={"X-WP-Nonce": self._gen_wp_rest_nonce()},
            except_status_code=200,
        )
        return [p["plugin"].split("/")[0] for p in response.json()]

    def list_comments(self, status: str = "approve", post_id: Optional[int] = None) -\> List[dict]:
        """List all comments in the WordPress site.

        Args:
            status: WordPress comment status, can be 'hold', 'approve', 'spam', or 'trash'.
            post_id: List all comments attached to the post, None to query the entire site.

        Returns:
            (List[dict]) A list of comment objects returned by WordPress REST API.
        """
        url = f"http://{self.host}/wp-json/wp/v2/comments?status={status}"
        if post_id:
            url += f"&post={post_id}"
        response = self._get(url, headers={"X-WP-Nonce": self._gen_wp_rest_nonce()})
        return response.json()

    def upload_media(self, filename: str, content: bytes, mimetype: Optional[str] = None) -\> dict:
        """Upload a media file (image/video).

        Args:
            filename: Filename of the media file.
            content: Content of the media file, bytes.
            mimetype: Mimetype of the media file, will infer from the filename if not provided.

        Raises:
            ValueError: if filename has invalid mimetype that cannot be automatically deduced.

        Returns:
             A dict with two keys: id and urls. Id is the WordPress media id and urls is a list of
             URL of the original image and resized images for the uploaded file on WordPress.
        """
        if mimetype is None:
            mimetype = mimetypes.guess_type(filename)[0]
        if mimetype is None:
            raise ValueError("Unable to deduce mimetype from filename")
        response = self._post(
            f"http://{self.host}/wp-json/wp/v2/media",
            headers={
                "X-WP-Nonce": self._gen_wp_rest_nonce(),
                "Content-Type": mimetype,
                "Content-Disposition": f'attachment; filename="{filename}"',
            },
            data=content,
            except_status_code=201,
        )
        media = response.json()
        image_urls = []
        for size in media["media_details"]["sizes"].values():
            image_urls.append(size["source_url"])
        if media["source_url"] not in image_urls:
            image_urls.append(media["source_url"])
        return {"id": media["id"], "urls": image_urls}

    def login_using_launchpad(self, username: str, password: str) -\> None:
        """Log in the WordPress site using Launchpad OpenID, require launchpad related plugins.

        Args:
            username: Username of the launchpad account.
            password: Password of the launchpad account.
        """
        # If the session was already used to log in, the openid page is different.
        # Clear the session to avoid such behavior.
        if self._session:
            self._session.close()
        self._session = requests.session()
        login_url = f"http://{self.host}/wp-login.php"
        self._get(login_url)
        openid_redirect = self._post(
            login_url,
            data={
                "launchpad": "Login",
                "redirect_to": f"http://{self.host}/wp-admin/",
                "testcookie": "1",
            },
        )
        openid_args = dict(
            re.findall(
                '\<input type="hidden" name="([^"]+)" value="([^"]+)" /\>',
                html.unescape(openid_redirect.text),
            )
        )
        login_page = self._post(
            "https://login.launchpad.net/+openid",
            data=openid_args,
        )
        csrf_token = re.findall(
            "\<input type='hidden' name='csrfmiddlewaretoken' value='([^']+)' /\>", login_page.text
        )[0]
        login_link = re.findall(
            '\<a id="login-link" data-qa-id="login_link" href="([^"]+)" class="p-link--soft"\>',
            login_page.text,
        )[0]
        login_url = f"https://login.launchpad.net{login_link}"
        confirm_page = self._post(
            login_url,
            data={
                "csrfmiddlewaretoken": csrf_token,
                "email": username,
                "user-intentions": "login",
                "password": password,
                "continue": "",
                "openid.usernamesecret": "",
            },
            headers={"Referer": login_page.url},
        )
        csrf_token = re.findall(
            "\<input type='hidden' name='csrfmiddlewaretoken' value='([^']+)' /\>", confirm_page.text
        )[0]
        teams = re.findall("Team membership: ([^\<]+)\<", confirm_page.text)
        assert teams, f"no teams found in {confirm_page.text}"
        team = teams[0]
        self._post(
            confirm_page.url,
            data={
                "csrfmiddlewaretoken": csrf_token,
                "nickname": "on",
                "email": "on",
                "fullname": "on",
                team: "on",
                "ok": "",
                "yes": "",
                "openid.usernamesecret": "",
            },
            headers={"Referer": confirm_page.url},
            except_status_code=200,
        )

    def list_associated_ubuntu_one_accounts(self) -\> List[str]:
        """List Ubuntu One accounts OpenID IDs associated with the current WordPress account.

        Returns:
            A list of Ubuntu One account OpenID IDs
            (something like https://login.ubuntu.com/+id/xxxxxxxx).
        """
        openid_setting = self._get(
            f"http://{self.host}/wp-admin/users.php?page=your_openids",
            except_status_code=200,
        )
        return re.findall("\<td\>(https://login\\.ubuntu\\.com[^\<]+)\</td\>", openid_setting.text)

    def list_roles(self) -\> List[str]:
        """List all WordPress roles of the current user.

        Raises:
            ValueError: No valid user to call list_roles was found.

        Returns:
            WordPress roles as a list of str.
        """
        user_page = self._get(f"http://{self.host}/wp-admin/users.php").text
        emails = re.findall("""data-colname="Email"\>\<a href='mailto:([^']+)'\>""", user_page)
        usernames = re.findall('users\\.php"\>([^\<]+)\</a\>', user_page)
        roles = re.findall('data-colname="Role"\>([^\<]+)\</td\>', user_page)
        for email, username, role in zip(emails, usernames, roles, strict=True):
            if self.username in (email, username):
                return [r.strip() for r in role.lower().split(",")]
        raise ValueError(f"User {self.username} not found")


class WordpressApp:
    """An object represents the wordpress charm application."""

    def __init__(self, app: Application, ops_test: OpsTest, kube_config: str):
        """Initialize the WordpressApp object."""
        self.app = app
        self.ops_test = ops_test
        kubernetes.config.load_kube_config(config_file=kube_config)
        self.kube_core_client = kubernetes.client.CoreV1Api()

    @property
    def model(self) -\> Model:
        """Get the current juju model."""
        model = self.ops_test.model
        assert model
        return model

    @property
    def name(self) -\> str:
        """Get the wordpress charm application name."""
        return self.app.name

    @retry(times=5, exceptions=(KeyError,))
    async def get_unit_ips(self) -\> List[str]:
        """Retrieve unit ip addresses, similar to fixture_get_unit_status_list.

        Returns:
            list of WordPress units ip addresses.
        """
        _, status, _ = await self.ops_test.juju("status", "--format", "json")
        status = json.loads(status)
        units = status["applications"][self.name]["units"]
        ip_list = []
        for key in sorted(units.keys(), key=lambda n: int(n.split("/")[-1])):
            ip_list.append(units[key]["address"])
        return ip_list

    async def get_default_admin_password(self) -\> str:
        """Get default admin password using get-initial-password action.

        Returns:
            WordPress admin account password
        """
        action = await self.app.units[0].run_action("get-initial-password")
        await action.wait()
        return action.results["password"]

    async def set_config(self, config):
        """Update the configuration of the wordpress charm."""
        await self.app.set_config(config)

    async def get_swift_bucket(self) -\> Optional[str]:
        """Get the swift bucket name used by the wordpress application."""
        config = await self.app.get_config()
        openstack_config = config["wp_plugin_openstack-objectstorage_config"]["value"]
        return yaml.safe_load(openstack_config).get("bucket")

    async def client_for_units(self) -\> List[WordpressClient]:
        """Get a list of WordpressClient for each unit of the wordpress application."""
        clients = []
        default_admin_password = await self.get_default_admin_password()
        for unit_ip in await self.get_unit_ips():
            clients.append(
                WordpressClient(
                    host=unit_ip, username="admin", password=default_admin_password, is_admin=True
                )
            )
        return clients

    async def wait_for_wordpress_idle(self, status: Optional[str] = None):
        """Wait for the wordpress application is idle."""
        await self.model.wait_for_idle(status=status, apps=[self.name])

    def get_units(self) -\> List[Unit]:
        """Get units of the wordpress application."""
        return self.app.units

    async def get_wordpress_config(self) -\> str:
        """Get wp-config.php contents from the leader unit.

        Returns:
            The contents of wp-config.php
        """
        unit = self.app.units[0]
        stdout = kubernetes.stream.stream(
            self.kube_core_client.connect_get_namespaced_pod_exec,
            unit.name.replace("/", "-"),
            unit.model.name,
            container="wordpress",
            command=["cat", "/var/www/html/wp-config.php"],
            stderr=True,
            stdin=False,
            stdout=True,
            tty=False,
        )
        return stdout


async def wait_for(
    func: Callable[[], Union[Awaitable, Any]],
    timeout: int = 300,
    check_interval: int = 10,
) -\> Any:
    """Wait for function execution to become truthy.

    Args:
        func: A callback function to wait to return a truthy value.
        timeout: Time in seconds to wait for function result to become truthy.
        check_interval: Time in seconds to wait between ready checks.

    Raises:
        TimeoutError: if the callback function did not return a truthy value within timeout.
    """
    deadline = time.time() + timeout
    is_awaitable = inspect.iscoroutinefunction(func)
    while time.time() \< deadline:
        if is_awaitable and (result := await func()):
            return result
        if result := func():
            return result
        time.sleep(check_interval)
    raise TimeoutError()


async def get_mysql_primary_unit(units: Iterable[Unit]) -\> Optional[Unit]:
    """Get the mysql primary unit.

    Args:
        units: An iterable list of units to search for primary unit from.
    """
    for unit in units:
        if unit.workload_status_message == "Primary":
            return unit
    return None
```

---

### 4. **pyproject.toml** - Integration Testing Sections

```toml
[dependency-groups]
integration = [
  "allure-pytest\>=2.8.18",
  "allure-pytest-collection-report @ git+https://github.com/canonical/data-platform-workflows@v24.0.0#subdirectory=python/pytest_plugins/allure_pytest_collection_report",
  "juju\>=2.9,\<3",
  "kubernetes",
  "pillow",
  "pytest==9.0.2",
  "pytest-cov",
  "pytest-operator",  # ← KEY DEPENDENCY
  "python-keystoneclient",
  "python-swiftclient",
  "types-pyyaml",
  "types-requests",
  "websockets\<17",
]
integration-juju3 = [
  "juju==3.6.1.3",
  "kubernetes",
  "macaroonbakery==1.3.4",
  "pillow",
  "pytest==9.0.2",
  "pytest-cov",
  "pytest-operator",  # ← KEY DEPENDENCY
  "python-keystoneclient",
  "python-swiftclient",
  "types-pyyaml",
  "types-requests",
]

[tool.pytest.ini_options]
markers = [
  "slow: marks slow and not very important tests",
  "requires_secret: mark tests that require external secrets",
]
```

---

### 5. **tox.toml** - Integration Testing Environments

```toml
[env.integration]
description = "Run integration tests"
commands = [
  [
    "pytest",
    "{[vars]tst_path}",
    "-v",
    "--tb",
    "native",
    "--ignore={[vars]tst_path}unit",
    "--log-cli-level=INFO",
    "-s",
    { replace = "posargs", extend = "true" },
  ],
]
dependency_groups = [ "integration" ]

[env.integration-juju3]
description = "Run integration tests using Juju 3"
commands = [
  [
    "pytest",
    "{[vars]tst_path}",
    "-v",
    "--tb",
    "native",
    "--ignore={[vars]tst_path}unit",
    "--log-cli-level=INFO",
    "-s",
    { replace = "posargs", extend = "true" },
  ],
]
dependency_groups = [ "integration-juju3" ]

[vars]
src_path = "{toxinidir}/src/"
tst_path = "{toxinidir}/tests/"
all_path = [ "{toxinidir}/src/", "{toxinidir}/tests/" ]
```

---

### 6. **Pre-run Scripts**

#### **pre_run_script.sh** - Full Content

```bash
#!/bin/bash

# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

# Pre-run script for integration test operator-workflows action.
# https://github.com/canonical/operator-workflows/blob/main/.github/workflows/integration_test.yaml

# Jenkins machine agent charm is deployed on lxd and Jenkins-k8s server charm is deployed on
# microk8s.

TESTING_MODEL="$(juju switch)"

# lxd should be install and init by a previous step in integration test action.
echo "bootstrapping lxd juju controller"
sg microk8s -c "microk8s status --wait-ready"
sg microk8s -c "juju bootstrap localhost localhost"

echo "Switching to testing model"
sg microk8s -c "juju switch $TESTING_MODEL"
```

#### **pre_run_script_juju3.sh** - Full Content

```bash
#!/bin/bash

# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

# Pre-run script for integration test operator-workflows action.
# https://github.com/canonical/operator-workflows/blob/main/.github/workflows/integration_test.yaml

# Jenkins machine agent charm is deployed on lxd and Jenkins-k8s server charm is deployed on
# microk8s.

TESTING_MODEL="$(juju switch)"

# lxd should be install and init by a previous step in integration test action.
echo "bootstrapping lxd juju controller"
sg snap_microk8s -c "microk8s status --wait-ready"
sg snap_microk8s -c "juju bootstrap localhost localhost"

echo "Switching to testing model"
sg snap_microk8s -c "juju switch $TESTING_MODEL"
```

---

## Key Migration Points

**This project uses `pytest-operator` (not pytest-jubilant)**, so the pattern is:

1. **`@pytest.fixture` + `ops_test: OpsTest`** - The `OpsTest` object from `pytest_operator.plugin` provides charm deployment and juju interaction
2. **`pytest_asyncio.fixture`** - For async setup/teardown of test infrastructure
3. **`await ops_test.juju(...)` or `await ops_test.run(...)`** - Execute juju commands
4. **`await model.deploy(...)`, `await model.relate(...)`** - Deploy and relate charms
5. **`@pytest.mark.usefixtures(...)` + `@pytest.mark.abort_on_fail`** - Control fixture dependency and test failure handling
6. **Custom helper classes** (`WordpressApp`, `WordpressClient`) - Wrap charm-specific operations
7. **Module-scoped fixtures** - Reuse expensive deployments across tests in same module

The integration tests run against a real Kubernetes cluster and use `pytest-operator` to manage the juju model and charm deployment lifecycle.


---

<sub>⏱️ 3m 46s</sub>

### ✅ `bash`

**View WordPress integration test files**

$ ls /tmp/wordpress-k8s-operator/tests/integration/ && cat /tmp/wordpress-k8s-operator/tests/integration/conftest.py

<details>
<summary>205 lines</summary>

```
conftest.py  pre_run_script.sh	      test_addon.py  test_cos_grafana.py  test_cos_prometheus.py  test_ingress.py
helper.py    pre_run_script_juju3.sh  test_core.py   test_cos_loki.py	  test_external.py	  test_machine.py
# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

"""Fixtures for the wordpress integration tests."""

import configparser
import json
import re
import secrets
from pathlib import Path
from typing import AsyncGenerator, Dict, Optional

import pytest
import pytest_asyncio
import swiftclient
import swiftclient.exceptions
import swiftclient.service
from juju.controller import Controller
from juju.model import Model
from pytest import Config
from pytest_operator.plugin import OpsTest

from tests.integration.helper import WordpressApp


@pytest.fixture(scope="module")
def model(ops_test: OpsTest) -> Model:
    """Return the juju model object created by pytest-operator."""
    model = ops_test.model
    assert model
    return model


@pytest.fixture(scope="module", name="kube_config")
def kube_config_fixture(pytestconfig: Config):
    """The Kubernetes cluster configuration file."""
    kube_config = pytestconfig.getoption("--kube-config")
    assert kube_config, (
        "The Kubernetes config file path should not be empty, "
        "please include it in the --kube-config parameter"
    )
    return kube_config


@pytest_asyncio.fixture(scope="module", name="machine_controller")
async def machine_controller_fixture() -> AsyncGenerator[Controller, None]:
    """The lxd controller."""
    controller = Controller()
    await controller.connect_controller("localhost")

    yield controller

    await controller.disconnect()


@pytest_asyncio.fixture(scope="module", name="machine_model")
async def machine_model_fixture(machine_controller: Controller) -> AsyncGenerator[Model, None]:
    """The machine model for jenkins agent machine charm."""
    machine_model_name = f"mysql-machine-{secrets.token_hex(2)}"
    model = await machine_controller.add_model(machine_model_name)

    yield model

    await model.disconnect()


@pytest_asyncio.fixture(scope="module", name="wordpress")
async def wordpress_fixture(
    pytestconfig: Config, ops_test: OpsTest, model: Model, kube_config: str
) -> WordpressApp:
    """Prepare the wordpress charm for integration tests."""
    exit_code, _, _ = await ops_test.juju("model-config", "logging-config=<root>=INFO;unit=DEBUG")
    assert exit_code == 0
    charm = pytestconfig.getoption("--charm-file")
    charm_dir = Path(__file__).parent.parent.parent
    if not charm:
        charm = await ops_test.build_charm(charm_dir)
    else:
        charm = Path(charm).absolute()
    wordpress_image = pytestconfig.getoption("--wordpress-image")
    if not wordpress_image:
        raise ValueError("--wordpress-image is required to run integration test")
    app = await model.deploy(
        charm,
        resources={
            "wordpress-image": wordpress_image,
        },
        num_units=1,
        series="jammy",
    )
    await model.wait_for_idle(status="blocked", apps=[app.name], timeout=30 * 60)
    return WordpressApp(app, ops_test=ops_test, kube_config=kube_config)


@pytest_asyncio.fixture(scope="module")
async def prepare_mysql(ops_test: OpsTest, wordpress: WordpressApp, model: Model):
    """Deploy and relate the mysql-k8s charm for integration tests."""
    app = await model.deploy("mysql-k8s", channel="8.0/stable", trust=True)
    await model.wait_for_idle(status="active", apps=[app.name], timeout=30 * 60)
    await model.relate(f"{wordpress.name}:database", f"{app.name}:database")
    await model.wait_for_idle(
        status="active", apps=[app.name, wordpress.name], timeout=40 * 60, idle_period=30
    )


@pytest_asyncio.fixture(scope="module")
async def prepare_machine_mysql(
    wordpress: WordpressApp, machine_controller: Controller, machine_model: Model, model: Model
):
    """Deploy and relate the mysql-k8s charm for integration tests."""
    await machine_model.deploy("mysql", channel="8.0/edge", trust=True)
    await machine_model.create_offer("mysql:database")
    await machine_model.wait_for_idle(status="active", apps=["mysql"], timeout=30 * 60)
    await model.relate(
        f"{wordpress.name}:database",
        f"{machine_controller.controller_name}:admin/{machine_model.name}.mysql",
    )


@pytest.fixture(scope="module", name="openstack_environment")
def openstack_environment_fixture(pytestconfig: Config):
    """Parse the openstack rc style configuration file from the --openstack-rc argument.

    Returns: a dictionary of environment variables and values, or None if --openstack-rc isn't
        provided.
    """
    rc_file = pytestconfig.getoption("--openstack-rc")
    if not rc_file:
        raise ValueError("--openstack-rc is required to run this test")
    with open(rc_file, encoding="utf-8") as rc_fo:
        rc_file = rc_fo.read()
    rc_file = re.sub("^export ", "", rc_file, flags=re.MULTILINE)
    openstack_conf = configparser.ConfigParser()
    openstack_conf.read_string("[DEFAULT]\n" + rc_file)
    return {k.upper(): v for k, v in openstack_conf["DEFAULT"].items()}


@pytest.fixture(scope="module", name="swift_conn")
def swift_conn_fixture(openstack_environment) -> Optional[swiftclient.Connection]:
    """Create a swift connection client."""
    return swiftclient.Connection(
        authurl=openstack_environment["OS_AUTH_URL"],
        auth_version="3",
        user=openstack_environment["OS_USERNAME"],
        key=openstack_environment["OS_PASSWORD"],
        os_options={
            "user_domain_name": openstack_environment["OS_USER_DOMAIN_ID"],
            "project_domain_name": openstack_environment["OS_PROJECT_DOMAIN_ID"],
            "project_name": openstack_environment["OS_PROJECT_NAME"],
        },
    )


@pytest.fixture(scope="module", name="swift_config")
def swift_config_fixture(
    ops_test: OpsTest,
    swift_conn: swiftclient.Connection,
    openstack_environment: Dict[str, str],
) -> Dict[str, str]:
    """Create a swift config dict that can be used for wp_plugin_openstack-objectstorage_config."""
    swift_service = swiftclient.service.SwiftService(
        options={
            "auth_version": "3",
            "os_auth_url": openstack_environment["OS_AUTH_URL"],
            "os_username": openstack_environment["OS_USERNAME"],
            "os_password": openstack_environment["OS_PASSWORD"],
            "os_project_name": openstack_environment["OS_PROJECT_NAME"],
            "os_project_domain_name": openstack_environment["OS_PROJECT_DOMAIN_ID"],
        }
    )
    container = f"wordpress_{ops_test.model_name}"
    # if the container exists, remove the container
    swift_service.delete(container=container)
    # create a swift container for our test
    swift_conn.put_container(container)
    # change container ACL to allow us getting an object by HTTP request without any authentication
    # the swift server will act as a static HTTP server after this
    swift_service.post(container=container, options={"read_acl": ".r:*,.rlistings"})

    return {
        "auth-url": openstack_environment["OS_AUTH_URL"] + "/v3",
        "bucket": container,
        "password": openstack_environment["OS_PASSWORD"],
        "object-prefix": "wp-content/uploads/",
        "region": openstack_environment["OS_REGION_NAME"],
        "tenant": openstack_environment["OS_PROJECT_NAME"],
        "domain": openstack_environment["OS_PROJECT_DOMAIN_ID"],
        "swift-url": swift_conn.url,
        "username": openstack_environment["OS_USERNAME"],
        "copy-to-swift": "1",
        "serve-from-swift": "1",
        "remove-local-file": "0",
    }


@pytest_asyncio.fixture(scope="module")
async def prepare_swift(wordpress: WordpressApp, swift_config: Dict[str, str]):
    """Configure the wordpress charm to use openstack swift object storage."""
    await wordpress.set_config(
        {"wp_plugin_openstack-objectstorage_config": json.dumps(swift_config)}
    )
    await wordpress.model.wait_for_idle(status="active", apps=[wordpress.name], timeout=30 * 60)


@pytest_asyncio.fixture(scope="module")
async def prepare_nginx_ingress(wordpress: WordpressApp, prepare_mysql):
    """Deploy and relate nginx-ingress-integrator charm for integration tests."""
    await wordpress.model.deploy(
        "nginx-ingress-integrator", channel="latest/edge", series="focal", revision=133, trust=True
    )
    await wordpress.model.wait_for_idle(apps=["nginx-ingress-integrator"], timeout=30 * 60)
    await wordpress.model.relate(f"{wordpress.name}:nginx-route", "nginx-ingress-integrator")
    await wordpress.model.wait_for_idle(status="active")


@pytest_asyncio.fixture(scope="module")
async def prepare_prometheus(wordpress: WordpressApp, prepare_mysql):
    """Deploy and relate prometheus-k8s charm for integration tests."""
    prometheus = await wordpress.model.deploy("prometheus-k8s", channel="1/stable", trust=True)
    await wordpress.model.wait_for_idle(
        status="active", apps=[prometheus.name], raise_on_error=False, timeout=30 * 60
    )
    await wordpress.model.relate(f"{wordpress.name}:metrics-endpoint", prometheus.name)
    await wordpress.model.wait_for_idle(
        status="active",
        apps=[prometheus.name, wordpress.name],
        timeout=20 * 60,
        raise_on_error=False,
    )


@pytest_asyncio.fixture(scope="module")
async def prepare_loki(wordpress: WordpressApp, prepare_mysql):
    """Deploy and relate loki-k8s charm for integration tests."""
    loki = await wordpress.model.deploy("loki-k8s", channel="1/stable", trust=True)
    await wordpress.model.wait_for_idle(apps=[loki.name], status="active", timeout=20 * 60)
    await wordpress.model.relate(f"{wordpress.name}:logging", loki.name)
    await wordpress.model.wait_for_idle(
        apps=[loki.name, wordpress.name], status="active", timeout=40 * 60
    )
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 3m 55s</sub>

### ✅ `bash`

**Check jubilant availability**

$ pip show jubilant pytest-jubilant 2>/dev/null || pip3 install jubilant pytest-jubilant --dry-run 2>&1 | head -20

```
bash: pip3: command not found
<exited with exit code 0>
```


---

<sub>⏱️ 4m 31s</sub>

### ✅ `web_search`

**jubilant pytest-jubilant canonical juju charm integration tests conftest.py juju.deploy juju.wait example**

<details>
<summary>Arguments</summary>

```json
{
  "query": "jubilant pytest-jubilant canonical juju charm integration tests conftest.py juju.deploy juju.wait example"
}
```

</details>

````
{"type":"text","text":{"value":"Here's a canonical example of using Jubilant together with pytest to write integration tests for a Juju charm, centered on the usage of `conftest.py`, `juju.deploy`, and `juju.wait`. This pattern is now recommended in the Canonical ecosystem for modern charm testing, superseding previous recipes built on `pytest-operator` and `python-libjuju`【3:0†source】【3:2†source】【3:9†source】.\n\n## Step 1: Install Jubilant and Requirements\n\n```bash\npip install jubilant pytest\n```\nMake sure the Juju CLI is installed on your system as well【3:1†source】【3:9†source】.\n\n---\n\n## Step 2: Create `conftest.py` Fixture\n\nInside your `tests/integration` or root-level tests directory, create a `conftest.py` file with your custom fixture to provision a temporary Juju model for each test module:\n\n```python\nimport pytest\nimport jubilant\n\n@pytest.fixture(scope='module')\ndef juju():\n    with jubilant.temp_model() as juju:\n        yield juju\n```\n- This context manager ensures a new, temporary model is created before tests and destroyed afterwards【3:9†source】.\n- You may make this fixture function-scoped or module-scoped; module-scoped is common for integration tests.\n\n---\n\n## Step 3: Write Test Using `juju.deploy` and `juju.wait`\n\nHere’s an example test file, say `test_charm.py`:\n\n```python\ndef test_active(juju: jubilant.Juju):\n    juju.deploy('my-charm')\n    juju.wait(jubilant.all_active)  # Wait for all apps in the model to become 'active'\n    # Address checking or endpoint test, e.g.\n    address = juju.status().apps['my-charm'].units['my-charm/0'].address\n    response = requests.get(f'http://{address}:8080/')\n    assert 'expected-string' in response.text.lower()\n```\n- `juju.deploy('my-charm')` deploys your charm. It can take additional arguments for resources, configs, or revision.\n- `juju.wait(jubilant.all_active)` will block until all applications in the model report \"active\" status. You may also use lambda functions for custom conditions (see below)【3:0†source】【3:9†source】.\n\n**For a specific app:**\n\n```python\njuju.wait(lambda status: jubilant.all_active(status, 'my-charm'))\n```\n---\n\n## Step 4: Custom Options\n\n- To keep models after tests (for debugging), add an option in `conftest.py`:\n\n```python\ndef pytest_addoption(parser):\n    parser.addoption('--keep-models', action='store_true', default=False, help='keep models after test')\n```\nAnd use it in your fixture as:\n\n```python\ndef juju(request):\n    keep_models = bool(request.config.getoption('--keep-models'))\n    with jubilant.temp_model(keep=keep_models) as juju:\n        yield juju\n```\n---\n\n## Step 5: Run Your Tests\n\nFrom the project directory:\n\n```bash\npytest tests/integration/\n```\n\n---\n\n## References and Further Reading\n\n- [Jubilant GitHub README](https://github.com/canonical/jubilant)\n- [Jubilant official documentation: Getting Started](https://documentation.ubuntu.com/jubilant/tutorial/getting-started/)\n- [Migration from pytest-operator to jubilant](https://documentation.ubuntu.com/jubilant/how-to/migrate-from-pytest-operator/)\n- [Writing charm integration tests](https://documentation.ubuntu.com/ops/latest/howto/write-integration-tests-for-a-charm/)\n\nThese resources contain in-depth guides, code samples, and migration notes for adopting Jubilant【3:0†source】【3:2†source】【3:9†source】【3:8†source】【3:1†source】.\n\n---\n\n**Summary Table:**\n\n| Step                | File            | What to do                                                    |\n|---------------------|-----------------|----------------------------------------------------------------|\n| Install requirements| N/A             | `pip install jubilant pytest`                                  |\n| Define fixture      | `conftest.py`   | `@pytest.fixture` using `jubilant.temp_model()`                |\n| Write test          | `test_charm.py` | Use `juju.deploy` and `juju.wait`, assert via HTTP or status   |\n| Run tests           | Shell           | `pytest tests/integration/`                                    |\n\nJubilant makes charm integration testing concise, reliable, and easier to maintain than previous approaches【3:0†source】【3:2†source】【3:9†source】.","annotations":[{"text":"【3:0†source】","start_index":344,"end_index":356,"url_citation":{"title":"Jubilant, the joyful library for driving Juju - GitHub","url":"https://github.com/canonical/jubilant"}},{"text":"【3:2†source】","start_index":356,"end_index":368,"url_citation":{"title":"How to migrate from pytest-operator to Jubilant","url":"https://documentation.ubuntu.com/jubilant/how-to/migrate-from-pytest-operator/"}},{"text":"【3:9†source】","start_index":368,"end_index":380,"url_citation":{"title":"Getting started with Jubilant - Jubilant documentation","url":"https://documentation.ubuntu.com/jubilant/tutorial/getting-started/"}},{"text":"【3:1†source】","start_index":527,"end_index":539,"url_citation":{"title":"jubilant · PyPI","url":"https://pypi.org/project/jubilant/"}},{"text":"【3:9†source】","start_index":539,"end_index":551,"url_citation":{"title":"Getting started with Jubilant - Jubilant documentation","url":"https://documentation.ubuntu.com/jubilant/tutorial/getting-started/"}},{"text":"【3:9†source】","start_index":1025,"end_index":1037,"url_citation":{"title":"Getting started with Jubilant - Jubilant documentation","url":"https://documentation.ubuntu.com/jubilant/tutorial/getting-started/"}},{"text":"【3:0†source】","start_index":1951,"end_index":1963,"url_citation":{"title":"Jubilant, the joyful library for driving Juju - GitHub","url":"https://github.com/canonical/jubilant"}},{"text":"【3:9†source】","start_index":1963,"end_index":1975,"url_citation":{"title":"Getting started with Jubilant - Jubilant documentation","url":"https://documentation.ubuntu.com/jubilant/tutorial/getting-started/"}},{"text":"【3:0†source】","start_index":3225,"end_index":3237,"url_citation":{"title":"Jubilant, the joyful library for driving Juju - GitHub","url":"https://github.com/canonical/jubilant"}},{"text":"【3:2†source】","start_index":3237,"end_index":3249,"url_citation":{"title":"How to migrate from pytest-operator to Jubilant","url":"https://documentation.ubuntu.com/jubilant/how-to/migrate-from-pytest-operator/"}},{"text":"【3:9†source】","start_index":3249,"end_index":3261,"url_citation":{"title":"Getting started with Jubilant - Jubilant documentation","url":"https://documentation.ubuntu.com/jubilant/tutorial/getting-started/"}},{"text":"【3:8†source】","start_index":3261,"end_index":3273,"url_citation":{"title":"How to write integration tests for a charm - Ops documentation","url":"https://documentation.ubuntu.com/ops/latest/howto/write-integration-tests-for-a-charm/"}},{"text":"【3:1†source】","start_index":3273,"end_index":3285,"url_citation":{"title":"jubilant · PyPI","url":"https://pypi.org/project/jubilant/"}},{"text":"【3:0†source】","start_index":4062,"end_index":4074,"url_citation":{"title":"Jubilant, the joyful library for driving Juju - GitHub","url":"https://github.com/canonical/jubilant"}},{"text":"【3:2†source】","start_index":4074,"end_index":4086,"url_citation":{"title":"How to migrate from pytest-operator to Jubilant","url":"https://documentation.ubuntu.com/jubilant/how-to/migrate-from-pytest-operator/"}},{"text":"【3:9†source】","start_index":4086,"end_index":4098,"url_citation":{"title":"Getting started with Jubilant - Jubilant documentation","url":"https://documentation.ubuntu.com/jubilant/tutorial/getting-started/"}}]},"bing_searches":[{"text":"jubilant pytest-jubilant canonical juju charm integration tests conftest.py juju.deploy juju.wait example","url":"https://www.bing.com/search?q=jubilant+pytest-jubilant+canonical+juju+charm+integration+tests+conftest.py+juju.deploy+juju.wait+example"}],"annotations":null}
````


---

<sub>⏱️ 4m 38s</sub>

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

<sub>⏱️ 4m 39s</sub>

### ✅ `web_fetch`

**https://github.com/canonical/jubilant**

<details>
<summary>Arguments</summary>

```json
{
  "url": "https://github.com/canonical/jubilant",
  "max_length": 10000
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

<sub>⏱️ 4m 43s</sub>

### 💬 Copilot

Now let me fetch the pytest-jubilant documentation:

---

<sub>⏱️ 4m 44s</sub>

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

<sub>⏱️ 5m 6s</sub>

### ✅ `web_search`

**pytest-jubilant pack() get_resources() charm_path conftest.py integration tests canonical**

<details>
<summary>Arguments</summary>

```json
{
  "query": "pytest-jubilant pack() get_resources() charm_path conftest.py integration tests canonical"
}
```

</details>

````
{"type":"text","text":{"value":"Here is how you can use pytest-jubilant for charm integration tests with fixtures like pack(), get_resources(), charm_path, and appropriately set up your conftest.py. This approach is the modern Canonical-recommended pattern for charm testing, designed to replace the older pytest-operator toolchain.\n\n## Key Points on pytest-jubilant and integration testing\n\n### What is pytest-jubilant?\n- **pytest-jubilant** is a pytest plugin that works with the Jubilant library. Jubilant is a Pythonic wrapper for the Juju CLI, simplifying integration testing for charms (including resources) without the async complexity of python-libjuju【3:2†source】【3:1†source】【3:4†source】【3:7†source】.\n\n### Setting Up conftest.py\n\nJubilant does not provide fixtures out-of-the-box, so you define them yourself in `conftest.py`. The following is the canonical approach for integration tests:\n\n```python\n# tests/integration/conftest.py\nimport pytest\nimport jubilant\n\n@pytest.fixture(scope='module')\ndef juju(request):\n    keep_models = bool(request.config.getoption('--keep-models'))\n    with jubilant.temp_model(keep=keep_models) as juju:\n        juju.wait_timeout = 10 * 60  # 10 minutes\n        yield juju\n    if request.session.testsfailed:\n        log = juju.debug_log(limit=1000)\n        print(log, end='')\n\ndef pytest_addoption(parser):\n    parser.addoption('--keep-models', action='store_true', default=False,\n                     help='keep temporarily-created models')\n```\n- This fixture creates a temporary model for use in each test module, cleans up by default, but can keep models if `--keep-models` is passed.\n- Prints out Juju debug logs if a test fails for easier triage.\n\n### pack() and get_resources()\n\n- **pack()** is a Jubilant utility that wraps `charmcraft pack`, building your charm and returning the path to the `.charm` file.\n- **get_resources()** parses your `charmcraft.yaml` and returns a resources dictionary to use during deploy.\n\nUsage in a fixture:\n\n```python\nimport pytest\nfrom pytest_jubilant import pack, get_resources\n\n@pytest.fixture(scope=\"session\")\ndef charm_path():\n    # Build the charm ONCE per test session\n    return pack()  # Returns the packed charm path\n\n@pytest.fixture(scope=\"session\")\ndef resources():\n    # Parse resources from charmcraft.yaml once per test session\n    return get_resources()\n```\nIn your tests, you can now do:\n\n```python\ndef test_deploy(juju, charm_path, resources):\n    juju.deploy(charm_path, resources=resources)\n    juju.wait(lambda status: jubilant.all_active(status))\n    # ...further testing...\n```\n- This workflow is efficient: the charm is built only once, resources are automatically parsed, and deploying is streamlined【3:0†source】【3:9†source】.\n\n### Example Directory and Usage\n\n```\ntests/\n  integration/\n    conftest.py          # Contains fixtures (juju, charm_path, resources)\n    test_charm.py        # Actual integration tests\n    ...\n```\nInvoke integration tests:\n```bash\npytest tests/integration --keep-models\n```\n\n### Additional References\n- [pytest-jubilant PyPI page](https://pypi.org/project/pytest-jubilant/)\n- [Migrating from pytest-operator to Jubilant](https://documentation.ubuntu.com/jubilant/how-to/migrate-from-pytest-operator/)\n- [Jubilant GitHub](https://github.com/canonical/jubilant)\n\n---\n\n**Summary:**  \nUse `pack()` and `get_resources()` fixtures to build your charm and manage resources efficiently in integration tests. Define these fixtures in `conftest.py` alongside a `juju` fixture for model isolation. This setup is now the canonical best practice for charm integration tests at Canonical【3:0†source】【3:1†source】【3:2†source】【3:9†source】【3:4†source】.","annotations":[{"text":"【3:2†source】","start_index":628,"end_index":640,"url_citation":{"title":"GitHub - canonical/jubilant: Jubilant is a Pythonic wrapper around the ...","url":"https://github.com/canonical/jubilant"}},{"text":"【3:1†source】","start_index":640,"end_index":652,"url_citation":{"title":"How to migrate from pytest-operator to Jubilant","url":"https://documentation.ubuntu.com/jubilant/how-to/migrate-from-pytest-operator/"}},{"text":"【3:4†source】","start_index":652,"end_index":664,"url_citation":{"title":"jubilant · PyPI","url":"https://pypi.org/project/jubilant/"}},{"text":"【3:7†source】","start_index":664,"end_index":676,"url_citation":{"title":"GitHub - dwilding/canonical-jubilant","url":"https://github.com/dwilding/canonical-jubilant"}},{"text":"【3:0†source】","start_index":2674,"end_index":2686,"url_citation":{"title":"pytest-jubilant · PyPI","url":"https://pypi.org/project/pytest-jubilant/"}},{"text":"【3:9†source】","start_index":2686,"end_index":2698,"url_citation":{"title":"Integration Tests | canonical/git-ubuntu-operator | DeepWiki","url":"https://deepwiki.com/canonical/git-ubuntu-operator/6.2.2-integration-tests"}},{"text":"【3:0†source】","start_index":3575,"end_index":3587,"url_citation":{"title":"pytest-jubilant · PyPI","url":"https://pypi.org/project/pytest-jubilant/"}},{"text":"【3:1†source】","start_index":3587,"end_index":3599,"url_citation":{"title":"How to migrate from pytest-operator to Jubilant","url":"https://documentation.ubuntu.com/jubilant/how-to/migrate-from-pytest-operator/"}},{"text":"【3:2†source】","start_index":3599,"end_index":3611,"url_citation":{"title":"GitHub - canonical/jubilant: Jubilant is a Pythonic wrapper around the ...","url":"https://github.com/canonical/jubilant"}},{"text":"【3:9†source】","start_index":3611,"end_index":3623,"url_citation":{"title":"Integration Tests | canonical/git-ubuntu-operator | DeepWiki","url":"https://deepwiki.com/canonical/git-ubuntu-operator/6.2.2-integration-tests"}},{"text":"【3:4†source】","start_index":3623,"end_index":3635,"url_citation":{"title":"jubilant · PyPI","url":"https://pypi.org/project/jubilant/"}}]},"bing_searches":[{"text":"pytest-jubilant pack() get_resources() charm_path conftest.py integration tests canonical","url":"https://www.bing.com/search?q=pytest-jubilant+pack%28%29+get_resources%28%29+charm_path+conftest.py+integration+tests+canonical"}],"annotations":null}
````


---

<sub>⏱️ 5m 10s</sub>

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

<sub>⏱️ 5m 40s</sub>

### ✅ `web_search`

**pytest-jubilant github canonical source code pack get_resources fixture**

<details>
<summary>Arguments</summary>

```json
{
  "query": "pytest-jubilant github canonical source code pack get_resources fixture"
}
```

</details>

````
{"type":"text","text":{"value":"From your query regarding the `pytest-jubilant` plugin for Pytest—a plugin to ease integration testing with Juju charms using Canonical's `jubilant` library—here’s a summary of what is canonical, what fixtures are provided, and how to use or customize them, particularly regarding resource or \"pack get_resources\" style fixtures.\n\n### Canonical Source Code and Official Fixtures\n\n- The **canonical source** of `pytest-jubilant` is Canonical's GitHub repository at: [github.com/canonical/jubilant](https://github.com/canonical/jubilant)【3:0†source】.\n- Official **documentation** further confirms the repo and purpose, noting it's the recommended upgrade path from `pytest-operator` for integration tests involving Juju charms【3:3†source】.\n- The `pytest-jubilant` package itself is available on PyPI with fixture overviews and CLI options: [pytest-jubilant on PyPI](https://pypi.org/project/pytest-jubilant/)【3:1†source】.\n\n#### Built-in Fixtures\n\n- **`juju` fixture**  \n  This is a module-scoped fixture providing a `Juju` instance in a temporary model. It is fundamental for most integration tests and is analogous to the old `ops_test` or `pytest-operator` test setup【3:1†source】【3:5†source】.\n\n  ```python\n  @pytest.fixture(scope='module')\n  def juju():\n      with jubilant.temp_model() as juju:\n          yield juju\n  ```\n\n- **`temp_model_factory` fixture**  \n  This factory allows creation of multiple temporary models if needed for more advanced testing scenarios (for example, cross-model relations in Juju)【3:1†source】.\n\n  ```python\n  @pytest.fixture\n  def istio(temp_model_factory):\n      yield temp_model_factory.get_juju(suffix=\"istio\")\n  ```\n\n  This way, multiple models for test setup can be programmatically managed and torn down.\n\n### \"pack get_resources\" Fixture\n\n**There is no built-in \"pack get_resources\" fixture in `pytest-jubilant`.**  \nIf you need a fixture for charm resource management (akin to what was possible with `pytest-operator` or a custom `pack.get_resources`), you will need to define it yourself.\n\n#### How to Create a Custom Fixture for Resources\n\nUse `conftest.py` to define fixtures for custom resource handling. For example:\n\n```python\n# conftest.py\n\nimport pytest\n\n@pytest.fixture(scope='session')\ndef get_resources():\n    def fetch_resources(charm_path):\n        # Logic to retrieve charm resources, e.g., reading metadata.yaml or using pack API\n        ...\n        return resources\n    return fetch_resources\n```\n\nYou can then inject `get_resources` into your tests:\n\n```python\ndef test_build_resources(get_resources):\n    resources = get_resources('./my-charm')\n    assert 'my_resource' in resources\n```\n\n#### Why Use conftest.py?\n\nFixtures in `conftest.py` are auto-discovered and are reusable across test modules. This is standard pytest best practice and is particularly useful when multiple tests share a common resource setup or teardown pattern【3:4†source】【3:8†source】.\n\n---\n\n### Summary\n\n- The canonical source code is Canonical's [`jubilant`](https://github.com/canonical/jubilant) repo【3:0†source】.\n- The primary built-in fixture is `juju`; `temp_model_factory` is for advanced use【3:1†source】.\n- There is **no built-in \"pack get_resources\" fixture**: you should define it in `conftest.py` or as appropriate for your charm.\n- Use `conftest.py` for centrally managing custom fixtures for your integration tests【3:4†source】.\n\nFor more details, see the [official docs](https://documentation.ubuntu.com/jubilant/), or explore the sample test setups provided on GitHub【3:0†source】【3:3†source】.","annotations":[{"text":"【3:0†source】","start_index":535,"end_index":547,"url_citation":{"title":"GitHub - canonical/jubilant: Jubilant is a Pythonic wrapper around the ...","url":"https://github.com/canonical/jubilant"}},{"text":"【3:3†source】","start_index":724,"end_index":736,"url_citation":{"title":"Jubilant documentation","url":"https://documentation.ubuntu.com/jubilant/"}},{"text":"【3:1†source】","start_index":906,"end_index":918,"url_citation":{"title":"pytest-jubilant · PyPI","url":"https://pypi.org/project/pytest-jubilant/"}},{"text":"【3:1†source】","start_index":1167,"end_index":1179,"url_citation":{"title":"pytest-jubilant · PyPI","url":"https://pypi.org/project/pytest-jubilant/"}},{"text":"【3:5†source】","start_index":1179,"end_index":1191,"url_citation":{"title":"How to migrate from pytest-operator to Jubilant","url":"https://canonical-jubilant.readthedocs-hosted.com/how-to/migrate-from-pytest-operator/"}},{"text":"【3:1†source】","start_index":1511,"end_index":1523,"url_citation":{"title":"pytest-jubilant · PyPI","url":"https://pypi.org/project/pytest-jubilant/"}},{"text":"【3:4†source】","start_index":2890,"end_index":2902,"url_citation":{"title":"Using conftest.py vs. importing fixtures from dedicate modules","url":"https://stackoverflow.com/questions/73191533/using-conftest-py-vs-importing-fixtures-from-dedicate-modules"}},{"text":"【3:8†source】","start_index":2902,"end_index":2914,"url_citation":{"title":"5 Simple Techniques To Resolve The Pytest Fixture Not Found Error","url":"https://pytest-with-eric.com/introduction/pytest-fixture-not-found/"}},{"text":"【3:0†source】","start_index":3034,"end_index":3046,"url_citation":{"title":"GitHub - canonical/jubilant: Jubilant is a Pythonic wrapper around the ...","url":"https://github.com/canonical/jubilant"}},{"text":"【3:1†source】","start_index":3130,"end_index":3142,"url_citation":{"title":"pytest-jubilant · PyPI","url":"https://pypi.org/project/pytest-jubilant/"}},{"text":"【3:4†source】","start_index":3358,"end_index":3370,"url_citation":{"title":"Using conftest.py vs. importing fixtures from dedicate modules","url":"https://stackoverflow.com/questions/73191533/using-conftest-py-vs-importing-fixtures-from-dedicate-modules"}},{"text":"【3:0†source】","start_index":3512,"end_index":3524,"url_citation":{"title":"GitHub - canonical/jubilant: Jubilant is a Pythonic wrapper around the ...","url":"https://github.com/canonical/jubilant"}},{"text":"【3:3†source】","start_index":3524,"end_index":3536,"url_citation":{"title":"Jubilant documentation","url":"https://documentation.ubuntu.com/jubilant/"}}]},"bing_searches":[{"text":"pytest-jubilant github canonical source code pack get_resources fixture","url":"https://www.bing.com/search?q=pytest-jubilant+github+canonical+source+code+pack+get_resources+fixture"}],"annotations":null}
````


---

<sub>⏱️ 5m 46s</sub>

### ❌ `web_fetch`

**https://github.com/dwilding/canonical-jubilant**

<details>
<summary>Arguments</summary>

```json
{
  "max_length": 8000,
  "url": "https://github.com/dwilding/canonical-jubilant"
}
```

</details>

```
Error: Failed to fetch https://github.com/dwilding/canonical-jubilant - status code 404
```


---

<sub>⏱️ 5m 46s</sub>

### ✅ `bash`

**Install and inspect pytest-jubilant**

$ pip install jubilant pytest-jubilant 2>&1 | tail -5 && python -c "import pytest_jubilant; help(pytest_jubilant)" 2>&1 | head -60

```
bash: pip: command not found
bash: python: command not found
<exited with exit code 0>
```


---

<sub>⏱️ 5m 51s</sub>

### ✅ `bash`

**Install jubilant with uv**

$ which python3 uv pip3 2>/dev/null; uv pip install jubilant pytest-jubilant 2>&1 | tail -10

```
/usr/bin/python3
/snap/bin/uv
error: No virtual environment found; run `uv venv` to create an environment, or pass `--system` to install into a non-virtual environment
<exited with exit code 0>
```


---

<sub>⏱️ 5m 55s</sub>

### ✅ `bash`

**Install jubilant system-wide and find source**

$ uv pip install --system jubilant pytest-jubilant 2>&1 | tail -15 && python3 -c "import pytest_jubilant; import inspect; print(inspect.getsourcefile(pytest_jubilant))" 2>&1

<details>
<summary>15 lines</summary>

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
Traceback (most recent call last):
  File "<string>", line 1, in <module>
ModuleNotFoundError: No module named 'pytest_jubilant'
<exited with exit code 1>
```

</details>


---

<sub>⏱️ 6m 29s</sub>

### ✅ `bash`

**Create venv and install jubilant**

$ cd /tmp && uv venv jubilant-env && uv pip install --python /tmp/jubilant-env/bin/python jubilant pytest-jubilant 2>&1 | tail -10

<details>
<summary>5 lines</summary>

```
Using CPython 3.12.3 interpreter at: /usr/bin/python3
Creating virtual environment at: jubilant-env
? A virtual environment already exists at `jubilant-env`. Do you want to replace it? [y/n] › yes

hint: Use the `--clear` flag or set `UV_VENV_CLEAR=1` to skip this prompt
<command with shellId: 9 is still running after 30 seconds. The command is still running. Check the output above - if it looks like the command is waiting for input, use write_bash to provide it. Otherwise, use read_bash to continue waiting for output, or stop_bash to stop it.>
```

</details>


---

<sub>⏱️ 6m 33s</sub>

### ✅ `write_bash`

<details>
<summary>Arguments</summary>

```json
{
  "shellId": "9",
  "input": "y\n",
  "delay": 20
}
```

</details>

<details>
<summary>16 lines</summary>

```
Using CPython 3.12.3 interpreter at: /usr/bin/python3
Creating virtual environment at: jubilant-env
? A virtual environment already exists at `jubilant-env`. Do you want to replace it? [y/n] › yes

hint: Use the `--clear` flag or set `UV_VENV_CLEAR=1` to skip this prompt✔ A virtual environment already exists at `jubilant-env`. Do you want to replace it? · yes
Activate with: source jubilant-env/bin/activate
Resolved 8 packages in 233ms
Installed 8 packages in 6ms
 + iniconfig==2.3.0
 + jubilant==1.7.0
 + packaging==26.0
 + pluggy==1.6.0
 + pygments==2.19.2
 + pytest==9.0.2
 + pytest-jubilant==1.1
 + pyyaml==6.0.3
<command with id: 9 exited with exit code 0>
```

</details>


---

<sub>⏱️ 6m 38s</sub>

### ✅ `bash`

**Find jubilant source files**

$ find /tmp/jubilant-env -name "*.py" -path "*/pytest_jubilant*" | head -20 && echo "---" && find /tmp/jubilant-env -name "*.py" -path "*/jubilant*" | head -20

<details>
<summary>25 lines</summary>

```
/tmp/jubilant-env/lib/python3.12/site-packages/pytest_jubilant/version.py
/tmp/jubilant-env/lib/python3.12/site-packages/pytest_jubilant/main.py
/tmp/jubilant-env/lib/python3.12/site-packages/pytest_jubilant/__init__.py
---
/tmp/jubilant-env/lib/python3.12/site-packages/iniconfig/_version.py
/tmp/jubilant-env/lib/python3.12/site-packages/iniconfig/exceptions.py
/tmp/jubilant-env/lib/python3.12/site-packages/iniconfig/_parse.py
/tmp/jubilant-env/lib/python3.12/site-packages/iniconfig/__init__.py
/tmp/jubilant-env/lib/python3.12/site-packages/py.py
/tmp/jubilant-env/lib/python3.12/site-packages/packaging/metadata.py
/tmp/jubilant-env/lib/python3.12/site-packages/packaging/requirements.py
/tmp/jubilant-env/lib/python3.12/site-packages/packaging/_structures.py
/tmp/jubilant-env/lib/python3.12/site-packages/packaging/_tokenizer.py
/tmp/jubilant-env/lib/python3.12/site-packages/packaging/licenses/_spdx.py
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
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 6m 43s</sub>

### ✅ `bash`

**Read pytest-jubilant source**

$ cat /tmp/jubilant-env/lib/python3.12/site-packages/pytest_jubilant/__init__.py && echo "===" && cat /tmp/jubilant-env/lib/python3.12/site-packages/pytest_jubilant/main.py

<details>
<summary>244 lines</summary>

```
#!/usr/bin/env python3
# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

"""Welcome to pytest-jubilant!"""

from pytest_jubilant.main import pack, get_resources

__all__ = ["pack", "get_resources"]
===
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

<sub>⏱️ 7m 7s</sub>

### 💬 Copilot

Now I have all the information I need. Let me create the plan and implement the migration:

---

<sub>⏱️ 7m 7s</sub>

### ✅ `sql`

**Create migration todos**

<details>
<summary>Arguments</summary>

```json
{
  "description": "Create migration todos",
  "query": "INSERT INTO todos (id, title, description, status) VALUES\n  ('deps', 'Update integration dependencies', 'In pyproject.toml: remove pytest-asyncio, pytest-operator, juju (python-libjuju) from integration group. Add jubilant~=1.0, pytest-jubilant. Also update lint group (remove pytest-operator, pytest-asyncio).', 'pending'),\n  ('conftest', 'Rewrite conftest.py', 'Remove async/await and pytest_asyncio. Use juju fixture from pytest-jubilant. Use pack() from pytest_jubilant to build charm. Replace app fixture to use juju.deploy(). Replace any_charm fixture to use juju.deploy(). Remove app_name fixture (use metadata directly). Remove ops_test/OpsTest imports.', 'pending'),\n  ('test-charm', 'Rewrite test_charm.py', 'Remove async/await, @pytest.mark.asyncio, ops_test, ops.Application imports. Replace model.wait_for_idle with juju.wait(). Replace app.set_config() with juju.config(). Replace model.add_relation with juju.integrate(). Check status with juju.status()', 'pending'),\n  ('tox', 'Update tox.toml integration env', 'Remove asyncio_mode setting if present. Check integration env still has correct dependency_groups.', 'pending'),\n  ('lockfile', 'Update uv.lock', 'Run uv lock to regenerate lockfile after dependency changes.', 'pending'),\n  ('verify', 'Verify linting passes', 'Run tox -e lint to make sure no import or type errors remain after migration.', 'pending');\nINSERT INTO todo_deps VALUES ('conftest', 'deps'), ('test-charm', 'conftest'), ('lockfile', 'deps'), ('verify', 'test-charm');"
}
```

</details>

```
0 row(s) inserted.
```


---

<sub>⏱️ 7m 13s</sub>

### ✅ `bash`

**Check jubilant API methods**

$ cat /tmp/jubilant-env/lib/python3.12/site-packages/jubilant/__init__.py | grep -E "^def |^class |^    def " | head -50

```

<exited with exit code 0>
```


---

<sub>⏱️ 7m 12s</sub>

### ✅ `view`

**/tmp/saml-integrator-L4-sonnet/pyproject.toml**

/tmp/saml-integrator-L4-sonnet/pyproject.toml

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

<sub>⏱️ 7m 17s</sub>

### ✅ `bash`

**Find jubilant config/integrate methods**

$ find /tmp/jubilant-env/lib/python3.12/site-packages/jubilant -name "*.py" | xargs grep -l "def config\|def integrate\|def deploy\|def wait" | head -5

```
/tmp/jubilant-env/lib/python3.12/site-packages/jubilant/_juju.py
<exited with exit code 0>
```


---

<sub>⏱️ 7m 22s</sub>

### ✅ `bash`

**Find jubilant API signatures**

$ grep -n "def config\|def integrate\|def deploy\|def wait\|def set_config" /tmp/jubilant-env/lib/python3.12/site-packages/jubilant/_juju.py

<details>
<summary>8 lines</summary>

```
409:    def config(self, app: str, *, app_config: bool = False) -> Mapping[str, ConfigValue]: ...
412:    def config(
421:    def config(self, app: str, *, reset: str | Iterable[str]) -> None: ...
423:    def config(
522:    def deploy(
757:    def integrate(self, app1: str, app2: str, *, via: str | Iterable[str] | None = None) -> None:
1387:    def wait(
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 7m 28s</sub>

### ✅ `bash`

**Read jubilant config signature**

$ sed -n '409,450p' /tmp/jubilant-env/lib/python3.12/site-packages/jubilant/_juju.py

<details>
<summary>37 lines</summary>

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
        """
        if values is None and not reset:
            stdout = self.cli('config', '--format', 'json', app)
            outer = json.loads(stdout)
            inner = outer['application-config'] if app_config else outer['settings']
            result = {
                k: SecretURI(v['value']) if v['type'] == 'secret' else v['value']
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 7m 44s</sub>

### ✅ `bash`

**Read jubilant deploy signature**

$ sed -n '522,600p' /tmp/jubilant-env/lib/python3.12/site-packages/jubilant/_juju.py

<details>
<summary>76 lines</summary>

```
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

        Args:
            charm: Name of charm or bundle to deploy, or path to a local file (must start with
                ``/`` or ``.``).
            app: Custom application name within the model. Defaults to the charm name.
            attach_storage: Existing storage(s) to attach to the deployed unit, for example,
                ``foo/0`` or ``mydisk/1``. Not available for Kubernetes models.
            base: The base on which to deploy, for example, ``ubuntu@22.04``.
            bind: Either a mapping of endpoint-to-space bindings, for example
                ``{'database-peers': 'internal-space'}``, or a single space name, which is
                equivalent to binding all endpoints to that space.
            channel: Channel to use when deploying from Charmhub, for example, ``latest/edge``.
            config: Application configuration as key-value pairs, for example,
                ``{'name': 'My Wiki'}``.
            constraints: Hardware constraints for new machines, for example, ``{'mem': '8G'}``.
            force: If true, bypass checks such as supported bases.
            num_units: Number of units to deploy for principal charms.
            overlays: File paths of bundles to overlay on the primary bundle, applied in order.
            resources: Specify named resources to use for deployment, for example:
                ``{'bin': '/path/to/some/binary'}``.
            revision: Charmhub revision number to deploy.
            storage: Constraints for named storage(s), for example, ``{'data': 'tmpfs,1G'}``.
            to: Machine or container to deploy the unit in (bypasses constraints). For example,
                to deploy to a new LXD container on machine 25, use ``lxd:25``.
            trust: If true, allows charm to run hooks that require access to cloud credentials.
        """
        # Need this check because str is also an iterable of str.
        if isinstance(overlays, str):
            raise TypeError('overlays must be an iterable of str or pathlib.Path, not str')

        with self._deploy_tempdir(charm, resources) as (_charm, resources):
            assert _charm is not None
            args = ['deploy', _charm]

            if app is not None:
                args.append(app)

            if attach_storage:
                if isinstance(attach_storage, str):
                    args.extend(['--attach-storage', attach_storage])
                else:
                    args.extend(['--attach-storage', ','.join(attach_storage)])
            if base is not None:
                args.extend(['--base', base])
            if bind is not None:
                if not isinstance(bind, str):
                    bind = ' '.join(f'{k}={v}' for k, v in bind.items())
                args.extend(['--bind', bind])
            if channel is not None:
                args.extend(['--channel', channel])
            if config is not None:
                for k, v in config.items():
                    args.extend(['--config', _format_config(k, v)])
            if constraints is not None:
                for k, v in constraints.items():
                    args.extend(['--constraints', f'{k}={v}'])
            if force:
                args.append('--force')
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 8m 41s</sub>

### ✅ `bash`

**Find format_config in jubilant**

$ grep -n "_format_config\|format_config" /tmp/jubilant-env/lib/python3.12/site-packages/jubilant/_juju.py | head -10

<details>
<summary>10 lines</summary>

```
209:                args.extend(['--config', _format_config(k, v)])
347:                args.extend(['--config', _format_config(k, v)])
357:                args.extend(['--model-default', _format_config(k, v)])
458:            args.extend(_format_config(k, v) for k, v in values.items())
595:                    args.extend(['--config', _format_config(k, v)])
818:            args.extend(_format_config(k, v) for k, v in values.items())
849:        args.extend(_format_config(k, v) for k, v in constraints.items())
924:                    args.extend(['--config', _format_config(k, v)])
1531:def _format_config(k: str, v: ConfigValue) -> str:
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 8m 45s</sub>

### ✅ `bash`

**Read _format_config**

$ sed -n '1531,1545p' /tmp/jubilant-env/lib/python3.12/site-packages/jubilant/_juju.py

<details>
<summary>13 lines</summary>

```
def _format_config(k: str, v: ConfigValue) -> str:
    if isinstance(v, bool):
        v = 'true' if v else 'false'
    return f'{k}={v}'


def _status_diff(old: Status | None, new: Status) -> str:
    """Return a line-based diff of two status objects."""
    if old is None:
        old_lines = []
    else:
        old_lines = [line for line in _pretty.gron(old) if _status_line_ok(line)]
    new_lines = [line for line in _pretty.gron(new) if _status_line_ok(line)]
    return '\n'.join(_pretty.diff(old_lines, new_lines))
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 9m 4s</sub>

### 💬 Copilot

Now I have everything I need. Let me implement the migration:

---

<sub>⏱️ 9m 4s</sub>

### ✅ `edit`

**/tmp/saml-integrator-L4-sonnet/pyproject.toml**

/tmp/saml-integrator-L4-sonnet/pyproject.toml

```
File /tmp/saml-integrator-L4-sonnet/pyproject.toml updated with changes.
```


---

<sub>⏱️ 9m 4s</sub>

### ✅ `edit`

**/tmp/saml-integrator-L4-sonnet/pyproject.toml**

/tmp/saml-integrator-L4-sonnet/pyproject.toml

```
File /tmp/saml-integrator-L4-sonnet/pyproject.toml updated with changes.
```


---

<sub>⏱️ 9m 13s</sub>

### 💬 Copilot

Now rewrite conftest.py:

---

<sub>⏱️ 9m 14s</sub>

### ✅ `bash`

**Rewrite conftest.py**

$ cat > /tmp/saml-integrator-L4-sonnet/tests/integration/conftest.py << 'EOF'
# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

"""Fixtures for the SAML Integrator charm integration tests."""

import json
from pathlib import Path

import jubilant
import pytest
import pytest_jubilant
import yaml

APP_NAME = yaml.safe_load(Path("./metadata.yaml").read_text("utf-8"))["name"]


@pytest.fixture(scope="module")
def app(juju: jubilant.Juju) -> str:
    """Deploy the SAML Integrator charm and return the application name."""
    charm = pytest_jubilant.pack()
    juju.deploy(charm, APP_NAME)
    return APP_NAME


@pytest.fixture(scope="module")
def any_charm(juju: jubilant.Juju) -> str:
    """Deploy any-charm with the SAML library loaded and return the application name."""
    path_lib = "lib/charms/saml_integrator/v0/saml.py"
    saml_lib = Path(path_lib).read_text(encoding="utf8")
    any_charm_script = Path("tests/integration/any_charm.py").read_text(encoding="utf8")
    src_overwrite = {
        "saml.py": saml_lib,
        "any_charm.py": any_charm_script,
    }
    juju.deploy(
        "any-charm",
        "any",
        channel="beta",
        config={"python-packages": "pydantic>=2.12.5", "src-overwrite": json.dumps(src_overwrite)},
    )
    return "any"
EOF

```

<exited with exit code 0>
```


---

<sub>⏱️ 9m 22s</sub>

### 💬 Copilot

Now rewrite test_charm.py:

---

<sub>⏱️ 9m 23s</sub>

### ✅ `bash`

**Rewrite test_charm.py**

$ cat > /tmp/saml-integrator-L4-sonnet/tests/integration/test_charm.py << 'EOF'
#!/usr/bin/env python3
# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

"""SAML Integrator charm integration tests."""

import jubilant
import pytest

SAML_CONFIG = {
    "entity_id": "https://login.staging.ubuntu.com",
    "fingerprint": "",
    "metadata_url": "https://login.staging.ubuntu.com/saml/metadata",
}


@pytest.mark.abort_on_fail
def test_active(juju: jubilant.Juju, app: str):
    """Check that the charm is active.

    Assume that the charm has already been built and is running.
    """
    juju.config(app, SAML_CONFIG)
    juju.wait(jubilant.all_active, error=jubilant.any_error)
    status = juju.status()
    assert status.apps[app].units[app + "/0"].is_active


@pytest.mark.abort_on_fail
def test_relation(juju: jubilant.Juju, app: str, any_charm: str):
    """Check that the charm is active once related to another charm.

    Assume that the charm has already been built and is running.
    """
    juju.integrate(f"{any_charm}:require-saml", f"{app}:saml")
    juju.config(app, SAML_CONFIG)
    juju.wait(jubilant.all_active, error=jubilant.any_error)
    status = juju.status()
    assert status.apps[app].units[app + "/0"].is_active
EOF

```

<exited with exit code 0>
```


---

<sub>⏱️ 9m 28s</sub>

### 💬 Copilot

Now update the lockfile and run lint:

---

<sub>⏱️ 9m 29s</sub>

### ✅ `bash`

**Regenerate uv.lock**

$ cd /tmp/saml-integrator-L4-sonnet && uv lock 2>&1 | tail -10

<details>
<summary>11 lines</summary>

```
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

<sub>⏱️ 9m 40s</sub>

### ✅ `bash`

**Run lint to verify changes**

$ cd /tmp/saml-integrator-L4-sonnet && tox -e lint 2>&1 | tail -30

<details>
<summary>14 lines</summary>

```
lint: venv> /home/ubuntu/.local/share/uv/tools/tox/bin/uv venv -p /home/ubuntu/.local/share/uv/tools/tox/bin/python --allow-existing --python-preference system /tmp/saml-integrator-L4-sonnet/.tox/lint
lint: uv-sync> uv sync --locked --python-preference system --no-default-groups --group lint -p /home/ubuntu/.local/share/uv/tools/tox/bin/python
lint: commands[0]> codespell /tmp/saml-integrator-L4-sonnet
lint: commands[1]> ruff format --check --diff /tmp/saml-integrator-L4-sonnet/src/ /tmp/saml-integrator-L4-sonnet/tests/ /tmp/saml-integrator-L4-sonnet/lib/charms/saml_integrator
warning: Selection `CPY` has no effect because preview is not enabled.
17 files already formatted
lint: commands[2]> ruff check /tmp/saml-integrator-L4-sonnet/src/ /tmp/saml-integrator-L4-sonnet/tests/ /tmp/saml-integrator-L4-sonnet/lib/charms/saml_integrator
warning: Selection `CPY` has no effect because preview is not enabled.
All checks passed!
lint: commands[3]> mypy /tmp/saml-integrator-L4-sonnet/src/ /tmp/saml-integrator-L4-sonnet/tests/ /tmp/saml-integrator-L4-sonnet/lib/charms/saml_integrator
Success: no issues found in 17 source files
  lint: OK (3.23=setup[0.08]+cmd[0.08,0.01,0.01,3.06] seconds)
  congratulations :) (3.24 seconds)
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 9m 50s</sub>

### 💬 Copilot

All lint checks pass. Let me commit the changes:

---

<sub>⏱️ 9m 51s</sub>

### ✅ `bash`

**Commit the migration**

$ cd /tmp/saml-integrator-L4-sonnet && git diff --stat && git add -A && git commit -m "Migrate integration tests from pytest-operator to jubilant

Replace python-libjuju/pytest-operator/pytest-asyncio with jubilant
and pytest-jubilant in all integration test files and dependencies.

Changes:
- tests/integration/conftest.py: remove async fixtures and OpsTest;
  use pytest_jubilant.pack() to build the charm, juju.deploy() for
  deployment; return app names as plain strings
- tests/integration/test_charm.py: remove async/await, ops imports,
  and @pytest.mark.asyncio; use juju.config(), juju.wait(), and
  juju.integrate() with synchronous jubilant API; check status via
  juju.status().apps[app].units[...].is_active
- pyproject.toml: replace juju, pytest-asyncio, pytest-operator with
  jubilant and pytest-jubilant in both 'integration' and 'lint'
  dependency groups
- uv.lock: regenerated after dependency changes

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>" 2>&1 | tail -15

<details>
<summary>14 lines</summary>

```
pyproject.toml                  |   9 +-
 tests/integration/conftest.py   |  48 ++---
 tests/integration/test_charm.py |  52 ++---
 uv.lock                         | 825 ++------------------------------------------------------------------------------
 4 files changed, 57 insertions(+), 877 deletions(-)
Author identity unknown

*** Please tell me who you are.

Run

  git config --global user.email "you@example.com"
  git config --global user.name "Your Name"

to set your account's default identity.
Omit --global to set the identity only in this repository.

fatal: unable to auto-detect email address (got 'ubuntu@jubilant-migration.(none)')
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 9m 59s</sub>

### ✅ `bash`

**Commit with git config**

$ cd /tmp/saml-integrator-L4-sonnet && git config user.email "copilot@github.com" && git config user.name "GitHub Copilot" && git commit -m "Migrate integration tests from pytest-operator to jubilant

Replace python-libjuju/pytest-operator/pytest-asyncio with jubilant
and pytest-jubilant in all integration test files and dependencies.

Changes:
- tests/integration/conftest.py: remove async fixtures and OpsTest;
  use pytest_jubilant.pack() to build the charm, juju.deploy() for
  deployment; return app names as plain strings
- tests/integration/test_charm.py: remove async/await, ops imports,
  and @pytest.mark.asyncio; use juju.config(), juju.wait(), and
  juju.integrate() with synchronous jubilant API; check status via
  juju.status().apps[app].units[...].is_active
- pyproject.toml: replace juju, pytest-asyncio, pytest-operator with
  jubilant and pytest-jubilant in both 'integration' and 'lint'
  dependency groups
- uv.lock: regenerated after dependency changes

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>" 2>&1 | tail -10

```
[main 6161d77] Migrate integration tests from pytest-operator to jubilant
 4 files changed, 57 insertions(+), 877 deletions(-)
<exited with exit code 0>
```


---

<sub>⏱️ 10m 8s</sub>

### 💬 Copilot

The migration is complete. Here's a summary of what changed:

**`tests/integration/conftest.py`**:
- Removed all `async`/`await`, `pytest_asyncio`, `OpsTest`, and `ops` imports
- `app` fixture now uses `pytest_jubilant.pack()` to build the charm and `juju.deploy()` — returns the app name as a plain `str`
- `any_charm` fixture uses `juju.deploy()` directly — returns `"any"` as a `str`
- `app_name` fixture removed; replaced by a module-level `APP_NAME` constant
- The `juju` fixture is provided automatically by `pytest-jubilant` (module-scoped, temp model)

**`tests/integration/test_charm.py`**:
- Removed `async def`, `@pytest.mark.asyncio`, `ops_test: OpsTest`, and `ops.Application` imports
- `app.set_config({...})` → `juju.config(app, {...})`
- `model.wait_for_idle(status='active')` → `juju.wait(jubilant.all_active, error=jubilant.any_error)`
- `model.add_relation(...)` → `juju.integrate(...)`
- Status assertion uses `juju.status().apps[app].units[app + "/0"].is_active`

**`pyproject.toml`**: Removed `juju`, `pytest-asyncio`, `pytest-operator` from both `integration` and `lint` groups; added `jubilant` and `pytest-jubilant`.

---

<sub>Generated by [GitHub Copilot CLI](https://github.com/features/copilot/cli)</sub>
