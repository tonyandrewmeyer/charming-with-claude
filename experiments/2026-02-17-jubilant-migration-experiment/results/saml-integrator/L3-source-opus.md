# 🤖 Copilot CLI Session

> **Session ID:** `07a1259e-4c05-47e6-9e0e-fda2af9fca6f`
> **Started:** 3/7/2026, 12:06:51 PM
> **Duration:** 3m 48s
> **Exported:** 3/7/2026, 12:10:39 PM

<sub>⏱️ 4s</sub>

### 👤 User

Migrate this charm's integration tests from pytest-operator (python-libjuju) to jubilant and pytest-jubilant. Update all test files, conftest.py, and dependencies.

Before starting, install jubilant and pytest-jubilant from PyPI (pip install jubilant pytest-jubilant) and read the source code to understand the API. The key modules are the Juju class, wait helpers (all_active, all_blocked, any_error), and the pytest-jubilant fixtures (pack, get_resources, juju fixture, temp_model_factory).

---

<sub>⏱️ 11s</sub>

### 💬 Copilot





---

<sub>⏱️ 11s</sub>

### ✅ `view`

**/tmp/saml-integrator-L3-opus**

/tmp/saml-integrator-L3-opus

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

<sub>⏱️ 11s</sub>

### ✅ `view`

**/tmp/saml-integrator-L3-opus/tests**

/tmp/saml-integrator-L3-opus/tests

```
__init__.py
conftest.py
integration
interface
unit
```


---

<sub>⏱️ 11s</sub>

### ✅ `bash`

**Install jubilant and pytest-jubilant**

$ pip install jubilant pytest-jubilant 2>&1 | tail -5

```
bash: pip: command not found
<exited with exit code 0>
```


---

<sub>⏱️ 15s</sub>

### ✅ `bash`

**Install jubilant with pip3**

$ which pip3 && pip3 install jubilant pytest-jubilant 2>&1 | tail -5

```

<exited with exit code 1>
```


---

<sub>⏱️ 15s</sub>

### ✅ `view`

**/tmp/saml-integrator-L3-opus/tests/integration**

/tmp/saml-integrator-L3-opus/tests/integration

```
__init__.py
any_charm.py
conftest.py
test_charm.py
```


---

<sub>⏱️ 15s</sub>

### ✅ `view`

**/tmp/saml-integrator-L3-opus/tests/conftest.py**

/tmp/saml-integrator-L3-opus/tests/conftest.py

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

<sub>⏱️ 20s</sub>

### ✅ `bash`

**Install jubilant with python3 -m pip**

$ which python3 && python3 -m pip install jubilant pytest-jubilant 2>&1 | tail -10

```
/usr/bin/python3
/usr/bin/python3: No module named pip
<exited with exit code 0>
```


---

<sub>⏱️ 19s</sub>

### ✅ `view`

**/tmp/saml-integrator-L3-opus/tests/integration/conftest.py**

/tmp/saml-integrator-L3-opus/tests/integration/conftest.py

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

<sub>⏱️ 19s</sub>

### ✅ `view`

**/tmp/saml-integrator-L3-opus/tests/integration/test_charm.py**

/tmp/saml-integrator-L3-opus/tests/integration/test_charm.py

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

<sub>⏱️ 19s</sub>

### ✅ `view`

**/tmp/saml-integrator-L3-opus/tests/integration/any_charm.py**

/tmp/saml-integrator-L3-opus/tests/integration/any_charm.py

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

<sub>⏱️ 24s</sub>

### ✅ `bash`

**View pyproject.toml**

$ cat /tmp/saml-integrator-L3-opus/pyproject.toml

<details>
<summary>139 lines</summary>

```
# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

[project]
name = "saml-integrator-operator"
version = "0.0.0"
description = "SAML Integrator to abstract SAML IdP details."
readme = "README.md"
requires-python = ">=3.10"
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
  "allure-pytest>=2.8.18",
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
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 24s</sub>

### ✅ `bash`

**View tox.toml**

$ cat /tmp/saml-integrator-L3-opus/tox.toml

<details>
<summary>155 lines</summary>

```
# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

skipsdist = true
skip_missing_interpreters = true
envlist = [ "lint", "unit", "static", "interface", "coverage-report" ]
requires = [ "tox>=4.21" ]
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
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 29s</sub>

### ✅ `bash`

**Find available Python tooling**

$ ls /usr/bin/python* /usr/local/bin/python* 2>/dev/null; uv --version 2>/dev/null

```
/usr/bin/python3   /usr/bin/python3.12
uv 0.10.8 (c021be36a 2026-03-03)
<exited with exit code 0>
```


---

<sub>⏱️ 33s</sub>

### ✅ `bash`

**Install jubilant with uv**

$ cd /tmp && uv pip install --system jubilant pytest-jubilant 2>&1 | tail -10

<details>
<summary>8 lines</summary>

```
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

<sub>⏱️ 1m 7s</sub>

### ✅ `bash`

**Install jubilant in venv**

$ cd /tmp && uv venv /tmp/jubilant-env && source /tmp/jubilant-env/bin/activate && uv pip install jubilant pytest-jubilant 2>&1 | tail -10

<details>
<summary>5 lines</summary>

```
Using CPython 3.12.3 interpreter at: /usr/bin/python3
Creating virtual environment at: jubilant-env
? A virtual environment already exists at `jubilant-env`. Do you want to replace it? [y/n] › yes

hint: Use the `--clear` flag or set `UV_VENV_CLEAR=1` to skip this prompt
<command with shellId: 7 is still running after 30 seconds. The command is still running. Check the output above - if it looks like the command is waiting for input, use write_bash to provide it. Otherwise, use read_bash to continue waiting for output, or stop_bash to stop it.>
```

</details>


---

<sub>⏱️ 1m 10s</sub>

### ✅ `write_bash`

<details>
<summary>Arguments</summary>

```json
{
  "shellId": "7",
  "input": "y",
  "delay": 15
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
Resolved 8 packages in 1ms
Installed 8 packages in 3ms
 + iniconfig==2.3.0
 + jubilant==1.7.0
 + packaging==26.0
 + pluggy==1.6.0
 + pygments==2.19.2
 + pytest==9.0.2
 + pytest-jubilant==1.1
 + pyyaml==6.0.3
<command with id: 7 exited with exit code 0>
```

</details>


---

<sub>⏱️ 1m 14s</sub>

### 💬 Copilot



Good, jubilant and pytest-jubilant are installed. Now let me study their APIs.

---

<sub>⏱️ 1m 15s</sub>

### ✅ `bash`

**Find jubilant package location**

$ source /tmp/jubilant-env/bin/activate && python3 -c "import jubilant; print(jubilant.__file__)"

```
/tmp/jubilant-env/lib/python3.12/site-packages/jubilant/__init__.py
<exited with exit code 0>
```


---

<sub>⏱️ 1m 15s</sub>

### ✅ `bash`

**Find pytest-jubilant location**

$ source /tmp/jubilant-env/bin/activate && python3 -c "import pytest_jubilant; print(pytest_jubilant.__file__)"

```
/tmp/jubilant-env/lib/python3.12/site-packages/pytest_jubilant/__init__.py
<exited with exit code 0>
```


---

<sub>⏱️ 1m 18s</sub>

### ✅ `view`

**/tmp/jubilant-env/lib/python3.12/site-packages/jubilant**

/tmp/jubilant-env/lib/python3.12/site-packages/jubilant

<details>
<summary>13 lines</summary>

```
__init__.py
__pycache__
_all_any.py
_juju.py
_pretty.py
_task.py
_test_helpers.py
_version.py
_yaml.py
modeltypes.py
py.typed
secrettypes.py
statustypes.py
```

</details>


---

<sub>⏱️ 1m 18s</sub>

### ✅ `view`

**/tmp/jubilant-env/lib/python3.12/site-packages/pytest_jubilant**

/tmp/jubilant-env/lib/python3.12/site-packages/pytest_jubilant

```
__init__.py
__pycache__
main.py
version.py
```


---

<sub>⏱️ 1m 22s</sub>

### ✅ `view`

**/tmp/jubilant-env/lib/python3.12/site-packages/jubilant/__init__.py**

/tmp/jubilant-env/lib/python3.12/site-packages/jubilant/__init__.py

<details>
<summary>56 lines</summary>

```
1. """Jubilant is a Pythonic wrapper around the Juju CLI."""
2. 
3. from . import modeltypes, secrettypes, statustypes
4. from ._all_any import (
5.     all_active,
6.     all_agents_idle,
7.     all_blocked,
8.     all_error,
9.     all_maintenance,
10.     all_waiting,
11.     any_active,
12.     any_blocked,
13.     any_error,
14.     any_maintenance,
15.     any_waiting,
16. )
17. from ._juju import CLIError, ConfigValue, Juju, WaitError
18. from ._task import Task, TaskError
19. from ._test_helpers import temp_model
20. from ._version import Version
21. from .modeltypes import ModelInfo
22. from .secrettypes import RevealedSecret, Secret, SecretURI
23. from .statustypes import Status
24. 
25. __all__ = [
26.     'CLIError',
27.     'ConfigValue',
28.     'Juju',
29.     'ModelInfo',
30.     'RevealedSecret',
31.     'Secret',
32.     'SecretURI',
33.     'Status',
34.     'Task',
35.     'TaskError',
36.     'Version',
37.     'WaitError',
38.     'all_active',
39.     'all_agents_idle',
40.     'all_blocked',
41.     'all_error',
42.     'all_maintenance',
43.     'all_waiting',
44.     'any_active',
45.     'any_blocked',
46.     'any_error',
47.     'any_maintenance',
48.     'any_waiting',
49.     'modeltypes',
50.     'secrettypes',
51.     'statustypes',
52.     'temp_model',
53. ]
54. 
55. __version__ = '1.7.0'
56.
```

</details>


---

<sub>⏱️ 1m 22s</sub>

### ✅ `view`

**/tmp/jubilant-env/lib/python3.12/site-packages/pytest_jubilant/__init__.py**

/tmp/jubilant-env/lib/python3.12/site-packages/pytest_jubilant/__init__.py

<details>
<summary>10 lines</summary>

```
1. #!/usr/bin/env python3
2. # Copyright 2025 Canonical Ltd.
3. # See LICENSE file for licensing details.
4. 
5. """Welcome to pytest-jubilant!"""
6. 
7. from pytest_jubilant.main import pack, get_resources
8. 
9. __all__ = ["pack", "get_resources"]
10.
```

</details>


---

<sub>⏱️ 1m 22s</sub>

### ✅ `view`

**/tmp/jubilant-env/lib/python3.12/site-packages/pytest_jubilant/main.py**

/tmp/jubilant-env/lib/python3.12/site-packages/pytest_jubilant/main.py

<details>
<summary>286 lines</summary>

```
1. #!/usr/bin/env python3
2. # Copyright 2025 Canonical Ltd.
3. # See LICENSE file for licensing details.
4. 
5. """Main plugin module."""
6. import dataclasses
7. import logging
8. import os
9. import secrets
10. import shlex
11. import subprocess
12. from pathlib import Path
13. from typing import Union, Optional, Dict
14. from unittest.mock import MagicMock, patch
15. 
16. import jubilant
17. import pytest
18. import yaml
19. 
20. JDL_LOGFILE_EXTENSION = "-jdl.txt"
21. DEFAULT_JDL_DUMP_PATH = "./.logs"
22. 
23. 
24. def pytest_addoption(parser):
25.     group = parser.getgroup("jubilant")
26.     group.addoption(
27.         "--model",
28.         action="store",
29.         default=None,
30.         help="Juju model name to target.",
31.     )
32.     group.addoption(
33.         "--keep-models",
34.         action="store_true",
35.         default=False,
36.         help="Skip model teardown.",
37.     )
38.     group.addoption(
39.         "--no-setup",
40.         action="store_true",
41.         default=False,
42.         help='Skip tests marked with "setup".',
43.     )
44.     group.addoption(
45.         "--no-teardown",
46.         action="store_true",
47.         default=False,
48.         help='Skip tests marked with "teardown".',
49.     )
50.     group.addoption(
51.         "--switch",
52.         action="store_true",
53.         default=False,
54.         help="Switch to the temporary model that is currently being worked on.",
55.     )
56.     group.addoption(
57.         "--dump-logs",
58.         action="store",
59.         default=DEFAULT_JDL_DUMP_PATH,
60.         help="Directory in which to dump any juju debug-log for any model prior to tearing it down. "
61.         "Set to empty string to disable the behaviour.",
62.     )
63. 
64. 
65. _cli_mock: Optional[MagicMock] = None
66. 
67. 
68. def pytest_configure(config):
69.     config.addinivalue_line(
70.         "markers", "setup: tests that setup some parts of the environment."
71.     )
72.     config.addinivalue_line(
73.         "markers", "teardown: tests that tear down some parts of the environment."
74.     )
75. 
76.     # horrible to do it this way, but it's easy
77.     if os.getenv("PYTESTING_PYTEST_JUBILANT"):
78.         mm = MagicMock()
79.         mm.return_value = MagicMock(stdout="output", stderr="error")
80.         ctx = patch("subprocess.run", new=mm)
81.         ctx.__enter__()
82.         global _cli_mock
83.         _cli_mock = mm
84. 
85. 
86. def pytest_collection_modifyitems(config: pytest.Config, items):
87.     def _set_keep_models(val: bool = True):
88.         # TODO: less hacky way to do this?
89.         optname = config._opt2dest.get("--keep-models", "--keep-models")  # noqa
90.         config.option.__setattr__(optname, val)
91. 
92.     if config.getoption("--no-teardown"):
93.         skipper = pytest.mark.skip(reason="--no-teardown provided.")
94.         for item in items:
95.             if "teardown" in item.keywords:
96.                 item.add_marker(skipper)
97. 
98.         if config.getoption("--keep-models"):
99.             logging.warning("--no-teardown implies --keep-models")
100.         else:
101.             _set_keep_models(True)
102. 
103.     if config.getoption("--no-setup"):
104.         skipper = pytest.mark.skip(reason="--no-setup provided.")
105.         for item in items:
106.             if "setup" in item.keywords:
107.                 item.add_marker(skipper)
108. 
109. 
110. class TempModelFactory:
111.     """Manages temporary models for testing."""
112. 
113.     def __init__(
114.         self,
115.         prefix: str,
116.         randbits: Optional[str] = None,
117.         check_models_unique: bool = True,
118.     ):
119.         self.prefix = prefix
120.         self.randbits = randbits
121.         self._models: Dict[str, jubilant.Juju] = {}
122.         self._check_models_unique = check_models_unique
123. 
124.     def get_juju(self, suffix: str) -> jubilant.Juju:
125.         model_name = "-".join(filter(None, (self.prefix, self.randbits, suffix)))
126.         if model_name in self._models:
127.             raise ValueError(
128.                 f"model {model_name} already registered on this temp_model factory. "
129.                 "choose a different prefix."
130.             )
131. 
132.         juju = jubilant.Juju(model=model_name)
133.         try:
134.             juju.add_model(model_name)
135.         except jubilant.CLIError as e:
136.             # If --model is set (_check_models_unique is False), then the user wants collisions.
137.             # If the name is randomly generated, the chance of colliding with another
138.             # randomly generated model that wasn't torn down is tiny, but still present.
139.             if (
140.                 "already exists on this k8s cluster" in e.args[1]
141.                 and self._check_models_unique
142.             ):
143.                 raise
144. 
145.         self._models[model_name] = juju
146.         return juju
147. 
148.     def dump_all_logs(self, path: Path = Path(DEFAULT_JDL_DUMP_PATH)):
149.         path.mkdir(parents=True, exist_ok=True)
150.         for model, juju in self._models.items():
151.             jdl_path = path / (model + JDL_LOGFILE_EXTENSION)
152.             jdl = juju.cli("debug-log", "--replay")
153.             jdl_path.write_text(jdl)
154.             logging.info(f"dropping jdl for model {model} to {jdl_path}")
155. 
156.     def teardown(self, force: bool = False):
157.         for model, juju in self._models.items():
158.             juju.destroy_model(model, destroy_storage=True, force=force)
159. 
160. 
161. @pytest.fixture(scope="module")
162. def cli_mock(request):
163.     yield _cli_mock
164. 
165. 
166. @pytest.fixture(scope="module")
167. def temp_model_factory(request):
168.     user_model = request.config.getoption("--model")
169.     if user_model:
170.         prefix = user_model
171.         randbits = None
172.     else:
173.         prefix = (request.module.__name__.rpartition(".")[-1]).replace("_", "-")
174.         randbits = (
175.             "testing"
176.             if os.getenv("PYTESTING_PYTEST_JUBILANT")
177.             else secrets.token_hex(4)
178.         )
179.     factory = TempModelFactory(
180.         prefix=prefix, randbits=randbits, check_models_unique=not user_model
181.     )
182. 
183.     yield factory
184. 
185.     # BEFORE tearing down the models, dump any and all juju debug-logs
186.     if dump_logs := request.config.getoption("--dump-logs"):
187.         factory.dump_all_logs(Path(dump_logs))
188. 
189.     if not request.config.getoption("--keep-models"):
190.         # TODO: jubilant defaults to --force, but is that a good idea?
191.         factory.teardown(force=True)
192. 
193.     if _cli_mock:
194.         _cli_mock.reset_mock()
195. 
196. 
197. @pytest.fixture(scope="module")
198. def juju(request, temp_model_factory):
199.     juju = temp_model_factory.get_juju("")
200.     if request.config.getoption("--switch"):
201.         juju.cli("switch", juju.model, include_model=False)
202.     return juju
203. 
204. 
205. @dataclasses.dataclass
206. class _Result:
207.     charm: Path
208.     resources: Optional[Dict[str, str]]
209. 
210. 
211. def _pack(root: Union[Path, str], platform: Optional[str] = None):
212.     _platform = f" --platform {platform}" if platform else ""
213.     cmd = f"charmcraft pack -p {root}{_platform}"
214.     proc = subprocess.run(
215.         shlex.split(cmd),
216.         check=True,
217.         capture_output=True,
218.         text=True,
219.     )
220. 
221.     # The output looks like:
222.     # ❯ charmcraft pack
223.     # Packed tempo-coordinator-k8s_ubuntu@24.04-amd64.charm
224.     # Packed tempo-coordinator-k8s_ubuntu@22.04-amd64.charm
225. 
226.     # Don't ask me why this goes to stderr.
227.     output = proc.stderr
228. 
229.     # we parse it and collect all the built charms.
230.     packed_charms = []
231.     for line in output.strip().splitlines():
232.         if line.startswith("Packed"):
233.             packed_charms.append(line.split()[1])
234. 
235.     if not packed_charms:
236.         raise ValueError(
237.             f"unable to get packed charm(s) ({cmd!r} completed with {proc.returncode=}, {proc.stdout=}, {proc.stderr=})"
238.         )
239. 
240.     return packed_charms
241. 
242. 
243. def pack(root: Union[Path, str] = "./", platform: Optional[str] = None) -> Path:
244.     """Pack a local charm and return it."""
245.     packed_charms = _pack(root, platform)
246. 
247.     if len(packed_charms) > 1:
248.         raise ValueError(
249.             "This charm supports multiple platforms. "
250.             "Pass a `platform` argument to control which charm you're getting instead."
251.         )
252. 
253.     return Path(packed_charms[0]).resolve()
254. 
255. 
256. def get_resources(root: Union[Path, str] = "./") -> Optional[Dict[str, str]]:
257.     """Obtain the charm resources from metadata.yaml's upstream-source fields."""
258.     for meta_name in ("metadata.yaml", "charmcraft.yaml"):
259.         if (meta_yaml := Path(root) / meta_name).exists():
260.             logging.debug(f"found metadata file: {meta_yaml}")
261.             meta = yaml.safe_load(meta_yaml.read_text())
262.             if meta_resources := meta.get("resources"):
263.                 try:
264.                     resources = {
265.                         resource: res_meta["upstream-source"]
266.                         for resource, res_meta in meta_resources.items()
267.                     }
268.                 except KeyError:
269.                     logging.exception(
270.                         "The `upstream-source` key wasn't found in the resource. If your charm follows a different convention of pointing at an OCI image, you need to pack it manually."
271.                     )
272.                     raise
273.             else:
274.                 resources = None
275.                 logging.info(
276.                     f"resources not found in {meta_name}; proceeding without resources"
277.                 )
278.             break
279.     else:
280.         resources = None
281.         logging.error(
282.             f"metadata/charmcraft.yaml not found at {root}; unable to load resources"
283.         )
284. 
285.     return resources
286.
```

</details>


---

<sub>⏱️ 1m 26s</sub>

### 💬 Copilot

Now let me study the Juju class API:

---

<sub>⏱️ 1m 26s</sub>

### ✅ `view`

**/tmp/jubilant-env/lib/python3.12/site-packages/jubilant/_juju.py**

/tmp/jubilant-env/lib/python3.12/site-packages/jubilant/_juju.py

```
File too large to read at once (59.4 KB). Consider using tools like grep (for searching), head/tail (for viewing start/end), view with view_range (for specific sections), or jq (for JSON) to examine portions of the file.
```


---

<sub>⏱️ 1m 31s</sub>

### ✅ `bash`

**List Juju class methods**

$ source /tmp/jubilant-env/bin/activate && python3 -c "
import inspect
import jubilant
members = inspect.getmembers(jubilant.Juju, predicate=inspect.isfunction)
for name, _ in members:
    if not name.startswith('_'):
        sig = inspect.signature(getattr(jubilant.Juju, name))
        print(f'{name}{sig}')
"

<details>
<summary>36 lines</summary>

```
add_credential(self, cloud: 'str', credential: 'str | pathlib.Path | Mapping[str, Any]', *, client: 'bool' = False, controller: 'str | None' = None, region: 'str | None' = None) -> 'None'
add_model(self, model: 'str', cloud: 'str | None' = None, *, controller: 'str | None' = None, config: 'Mapping[str, ConfigValue] | None' = None, credential: 'str | None' = None) -> 'None'
add_secret(self, name: 'str', content: 'Mapping[str, str]', *, info: 'str | None' = None) -> 'SecretURI'
add_ssh_key(self, *keys: 'str') -> 'None'
add_unit(self, app: 'str', *, attach_storage: 'str | Iterable[str] | None' = None, num_units: 'int' = 1, to: 'str | Iterable[str] | None' = None)
bootstrap(self, cloud: 'str', controller: 'str', *, bootstrap_base: 'str | None' = None, bootstrap_constraints: 'Mapping[str, str] | None' = None, config: 'Mapping[str, ConfigValue] | None' = None, constraints: 'Mapping[str, str] | None' = None, credential: 'str | None' = None, force: 'bool' = False, model_defaults: 'Mapping[str, ConfigValue] | None' = None, storage_pool: 'Mapping[str, str] | None' = None, to: 'str | Iterable[str] | None' = None) -> 'None'
cli(self, *args: 'str', include_model: 'bool' = True, stdin: 'str | None' = None) -> 'str'
config(self, app: 'str', values: 'Mapping[str, ConfigValue] | None' = None, *, app_config: 'bool' = False, reset: 'str | Iterable[str]' = ()) -> 'Mapping[str, ConfigValue] | None'
consume(self, model_and_app: 'str', alias: 'str | None' = None, *, controller: 'str | None' = None, owner: 'str | None' = None) -> 'None'
debug_log(self, *, limit: 'int' = 0) -> 'str'
deploy(self, charm: 'str | pathlib.Path', app: 'str | None' = None, *, attach_storage: 'str | Iterable[str] | None' = None, base: 'str | None' = None, bind: 'Mapping[str, str] | str | None' = None, channel: 'str | None' = None, config: 'Mapping[str, ConfigValue] | None' = None, constraints: 'Mapping[str, str] | None' = None, force: 'bool' = False, num_units: 'int' = 1, overlays: 'Iterable[str | pathlib.Path]' = (), resources: 'Mapping[str, str] | None' = None, revision: 'int | None' = None, storage: 'Mapping[str, str] | None' = None, to: 'str | Iterable[str] | None' = None, trust: 'bool' = False) -> 'None'
destroy_model(self, model: 'str', *, destroy_storage: 'bool' = False, force: 'bool' = False, no_wait: 'bool' = False, release_storage: 'bool' = False, timeout: 'float | None' = None) -> 'None'
exec(self, command: 'str', *args: 'str', machine: 'int | str | None' = None, unit: 'str | None' = None, wait: 'float | None' = None) -> 'Task'
grant_secret(self, identifier: 'str | SecretURI', app: 'str | Iterable[str]') -> 'None'
integrate(self, app1: 'str', app2: 'str', *, via: 'str | Iterable[str] | None' = None) -> 'None'
model_config(self, values: 'Mapping[str, ConfigValue] | None' = None, reset: 'str | Iterable[str]' = ()) -> 'Mapping[str, ConfigValue] | None'
model_constraints(self, constraints: 'Mapping[str, ConstraintValue] | None' = None) -> 'Mapping[str, ConstraintValue] | None'
offer(self, app: 'str', *, controller: 'str | None' = None, endpoint: 'str | Iterable[str]', name: 'str | None' = None) -> 'None'
refresh(self, app: 'str', *, base: 'str | None' = None, channel: 'str | None' = None, config: 'Mapping[str, ConfigValue] | None' = None, force: 'bool' = False, path: 'str | pathlib.Path | None' = None, resources: 'Mapping[str, str] | None' = None, revision: 'int | None' = None, storage: 'Mapping[str, str] | None' = None, trust: 'bool' = False)
remove_application(self, *app: 'str', destroy_storage: 'bool' = False, force: 'bool' = False) -> 'None'
remove_relation(self, app1: 'str', app2: 'str', *, force: 'bool' = False) -> 'None'
remove_secret(self, identifier: 'str | SecretURI', *, revision: 'int | None' = None) -> 'None'
remove_ssh_key(self, *ids: 'str') -> 'None'
remove_unit(self, *app_or_unit: 'str', destroy_storage: 'bool' = False, force: 'bool' = False, num_units: 'int' = 0) -> 'None'
run(self, unit: 'str', action: 'str', params: 'Mapping[str, Any] | None' = None, *, wait: 'float | None' = None) -> 'Task'
scp(self, source: 'str | pathlib.Path', destination: 'str | pathlib.Path', *, container: 'str | None' = None, host_key_checks: 'bool' = True, scp_options: 'Iterable[str]' = ()) -> 'None'
secrets(self, *, owner: 'str | None' = None) -> 'list[Secret]'
show_model(self, model: 'str | None' = None) -> 'ModelInfo'
show_secret(self, identifier: 'str | SecretURI', *, reveal: 'bool' = False, revision: 'int | None' = None, revisions: 'bool' = False) -> 'Secret | RevealedSecret'
ssh(self, target: 'str | int', command: 'str', *args: 'str', container: 'str | None' = None, host_key_checks: 'bool' = True, ssh_options: 'Iterable[str]' = (), user: 'str | None' = None) -> 'str'
status(self) -> 'Status'
trust(self, app: 'str', *, remove: 'bool' = False, scope: "Literal['cluster'] | None" = None) -> 'None'
update_secret(self, identifier: 'str | SecretURI', content: 'Mapping[str, str]', *, info: 'str | None' = None, name: 'str | None' = None, auto_prune: 'bool' = False) -> 'None'
version(self) -> 'Version'
wait(self, ready: 'Callable[[Status], bool]', *, error: 'Callable[[Status], bool] | None' = None, delay: 'float' = 1.0, timeout: 'float | None' = None, successes: 'int' = 3) -> 'Status'
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 1m 36s</sub>

### 💬 Copilot

Now let me look at the `wait` method and `all_active` more closely:

---

<sub>⏱️ 1m 36s</sub>

### ✅ `view`

**/tmp/jubilant-env/lib/python3.12/site-packages/jubilant/_all_any.py**

/tmp/jubilant-env/lib/python3.12/site-packages/jubilant/_all_any.py

<details>
<summary>214 lines</summary>

```
1. from __future__ import annotations
2. 
3. from collections.abc import Iterable
4. 
5. from .statustypes import Status
6. 
7. 
8. def all_active(status: Status, *apps: str) -> bool:
9.     """Report whether all apps and units in *status* (or in *apps* if provided) are "active".
10. 
11.     Examples::
12. 
13.         # Use the callable directly to wait for all apps in status to be active.
14.         juju.wait(jubilant.all_active)
15. 
16.         # Use a lambda to wait for all apps specified (blog, mysql) to be active.
17.         juju.wait(lambda status: jubilant.all_active(status, 'blog', 'mysql'))
18. 
19.     Args:
20.         status: The status object being tested.
21.         apps: If provided, only these applications (and their units) are tested. If an app is not
22.             present in ``status.apps``, returns False.
23.     """
24.     return _all_statuses_are('active', status, apps)
25. 
26. 
27. def all_blocked(status: Status, *apps: str) -> bool:
28.     """Report whether all apps and units in *status* (or in *apps* if provided) are "blocked".
29. 
30.     See :func:`all_active` for examples.
31. 
32.     Args:
33.         status: The status object being tested.
34.         apps: If provided, only these applications (and their units) are tested. If an app is not
35.             present in ``status.apps``, returns False.
36.     """
37.     return _all_statuses_are('blocked', status, apps)
38. 
39. 
40. def all_error(status: Status, *apps: str) -> bool:
41.     """Report whether all apps and units in *status* (or in *apps* if provided) are "error".
42. 
43.     See :func:`all_active` for examples.
44. 
45.     Args:
46.         status: The status object being tested.
47.         apps: If provided, only these applications (and their units) are tested. If an app is not
48.             present in ``status.apps``, returns False.
49.     """
50.     return _all_statuses_are('error', status, apps)
51. 
52. 
53. def all_maintenance(status: Status, *apps: str) -> bool:
54.     """Report whether all apps and units in *status* (or in *apps* if provided) are "maintenance".
55. 
56.     See :func:`all_active` for examples.
57. 
58.     Args:
59.         status: The status object being tested.
60.         apps: If provided, only these applications (and their units) are tested. If an app is not
61.             present in ``status.apps``, returns False.
62.     """
63.     return _all_statuses_are('maintenance', status, apps)
64. 
65. 
66. def all_waiting(status: Status, *apps: str) -> bool:
67.     """Report whether all apps and units in *status* (or in *apps* if provided) are "waiting".
68. 
69.     See :func:`all_active` for examples.
70. 
71.     Args:
72.         status: The status object being tested.
73.         apps: If provided, only these applications (and their units) are tested. If an app is not
74.             present in ``status.apps``, returns False.
75.     """
76.     return _all_statuses_are('waiting', status, apps)
77. 
78. 
79. def any_active(status: Status, *apps: str) -> bool:
80.     """Report whether any app or unit in *status* (or in *apps* if provided) is "active".
81. 
82.     See :func:`any_error` for examples.
83. 
84.     Args:
85.         status: The status object being tested.
86.         apps: If provided, only these applications (and their units) are tested.
87.     """
88.     return _any_status_is('active', status, apps)
89. 
90. 
91. def any_blocked(status: Status, *apps: str) -> bool:
92.     """Report whether any app or unit in *status* (or in *apps* if provided) is "blocked".
93. 
94.     See :func:`any_error` for examples.
95. 
96.     Args:
97.         status: The status object being tested.
98.         apps: If provided, only these applications (and their units) are tested.
99.     """
100.     return _any_status_is('blocked', status, apps)
101. 
102. 
103. def any_error(status: Status, *apps: str) -> bool:
104.     """Report whether any app or unit in *status* (or in *apps* if provided) is "error".
105. 
106.     Examples::
107. 
108.         # Use the callable directly to raise an error if any apps go into error.
109.         juju.wait(jubilant.all_active, error=jubilant.any_error)
110. 
111.         # Use a lambda to wait for any of the apps specified (blog, mysql) to go into error.
112.         juju.wait(
113.             jubilant.all_active,
114.             error=lambda status: jubilant.any_error(status, 'blog', 'mysql')),
115.         )
116. 
117.     Args:
118.         status: The status object being tested.
119.         apps: If provided, only these applications (and their units) are tested.
120.     """
121.     return _any_status_is('error', status, apps)
122. 
123. 
124. def any_maintenance(status: Status, *apps: str) -> bool:
125.     """Report whether any app or unit in *status* (or in *apps* if provided) is "maintenance".
126. 
127.     See :func:`any_error` for examples.
128. 
129.     Args:
130.         status: The status object being tested.
131.         apps: If provided, only these applications (and their units) are tested.
132.     """
133.     return _any_status_is('maintenance', status, apps)
134. 
135. 
136. def any_waiting(status: Status, *apps: str) -> bool:
137.     """Report whether any app or unit in *status* (or in *apps* if provided) is "waiting".
138. 
139.     See :func:`any_error` for examples.
140. 
141.     Args:
142.         status: The status object being tested.
143.         apps: If provided, only these applications (and their units) are tested.
144.     """
145.     return _any_status_is('waiting', status, apps)
146. 
147. 
148. def all_agents_idle(status: Status, *apps: str) -> bool:
149.     """Report whether all unit agents in *status* (filtered to *apps* if provided) are "idle".
150. 
151.     Unlike the other ``all_*`` and ``any_*`` helpers, this method looks at the status of each
152.     Juju unit agent, not the workload's application or unit status.
153. 
154.     Examples::
155. 
156.         # Use the callable directly to wait for unit agents from all apps to be idle.
157.         juju.wait(jubilant.all_agents_idle)
158. 
159.         # Use a lambda to wait for unit agents only from specified apps (blog, mysql).
160.         juju.wait(lambda status: jubilant.all_agents_idle(status, 'blog', 'mysql'))
161. 
162.     Args:
163.         status: The status object being tested.
164.         apps: If provided, only the unit agents of units from these applications are tested.
165.             If an app is not present in ``status.apps``, returns False.
166.     """
167.     return _all_agent_statuses_are('idle', status, apps)
168. 
169. 
170. def _all_statuses_are(expected: str, status: Status, apps: Iterable[str]) -> bool:
171.     if not apps:
172.         apps = status.apps
173. 
174.     for app in apps:
175.         app_info = status.apps.get(app)
176.         if app_info is None:
177.             return False
178.         if app_info.app_status.current != expected:
179.             return False
180.         for unit_info in status.get_units(app).values():
181.             if unit_info.workload_status.current != expected:
182.                 return False
183.     return True
184. 
185. 
186. def _any_status_is(expected: str, status: Status, apps: Iterable[str]) -> bool:
187.     if not apps:
188.         apps = status.apps
189. 
190.     for app in apps:
191.         app_info = status.apps.get(app)
192.         if app_info is None:
193.             continue
194.         if app_info.app_status.current == expected:
195.             return True
196.         for unit_info in status.get_units(app).values():
197.             if unit_info.workload_status.current == expected:
198.                 return True
199.     return False
200. 
201. 
202. def _all_agent_statuses_are(expected: str, status: Status, apps: Iterable[str]) -> bool:
203.     if not apps:
204.         apps = status.apps
205. 
206.     for app in apps:
207.         app_info = status.apps.get(app)
208.         if app_info is None:
209.             return False
210.         for unit_info in status.get_units(app).values():
211.             if unit_info.juju_status.current != expected:
212.                 return False
213.     return True
214.
```

</details>


---

<sub>⏱️ 1m 36s</sub>

### ✅ `view`

**/tmp/jubilant-env/lib/python3.12/site-packages/jubilant/statustypes.py**

/tmp/jubilant-env/lib/python3.12/site-packages/jubilant/statustypes.py

```
File too large to read at once (26.5 KB). Consider using tools like grep (for searching), head/tail (for viewing start/end), view with view_range (for specific sections), or jq (for JSON) to examine portions of the file.
```


---

<sub>⏱️ 1m 39s</sub>

### ✅ `view`

**/tmp/jubilant-env/lib/python3.12/site-packages/jubilant/statustypes.py**

/tmp/jubilant-env/lib/python3.12/site-packages/jubilant/statustypes.py (lines 1-60)

<details>
<summary>60 lines</summary>

```
1. """Dataclasses that contain parsed output from ``juju status --format=json``.
2. 
3. These dataclasses were originally `generated from <https://github.com/juju/juju/compare/main...benhoyt:juju:status-dataclasses>`_
4. the Go structs in the Juju codebase, to ensure they are correct. Class names
5. come from the Go struct name, whereas attribute names come from the JSON field
6. names. The one exception is that "Application" has been renamed to "App"
7. throughout, for brevity (and "application" to "app").
8. """
9. 
10. from __future__ import annotations
11. 
12. import dataclasses
13. from typing import Any
14. 
15. from . import _pretty
16. 
17. __all__ = [
18.     'AppStatus',
19.     'AppStatusRelation',
20.     'CombinedStorage',
21.     'ControllerStatus',
22.     'EntityStatus',
23.     'FilesystemAttachment',
24.     'FilesystemAttachments',
25.     'FilesystemInfo',
26.     'FormattedBase',
27.     'LxdProfileContents',
28.     'MachineStatus',
29.     'ModelStatus',
30.     'NetworkInterface',
31.     'OfferStatus',
32.     'RemoteAppStatus',
33.     'RemoteEndpoint',
34.     'Status',
35.     'StatusInfo',
36.     'StorageAttachments',
37.     'StorageInfo',
38.     'UnitStatus',
39.     'UnitStorageAttachment',
40.     'VolumeAttachment',
41.     'VolumeAttachments',
42.     'VolumeInfo',
43. ]
44. 
45. 
46. @dataclasses.dataclass(frozen=True)
47. class FormattedBase:
48.     name: str
49.     channel: str
50. 
51.     @classmethod
52.     def _from_dict(cls, d: dict[str, Any]) -> FormattedBase:
53.         return cls(
54.             name=d['name'],
55.             channel=d['channel'],
56.         )
57. 
58. 
59. @dataclasses.dataclass(frozen=True)
60. class StatusInfo:
```

</details>


---

<sub>⏱️ 1m 55s</sub>

### 💬 Copilot

Now I have a thorough understanding of the jubilant API. Let me create my plan and implement the migration.

---

<sub>⏱️ 1m 55s</sub>

### ✅ `create`

**/home/ubuntu/.copilot/session-state/07a1259e-4c05-47e6-9e0e-fda2af9fca6f/plan.md**

/home/ubuntu/.copilot/session-state/07a1259e-4c05-47e6-9e0e-fda2af9fca6f/plan.md

```
Created file /home/ubuntu/.copilot/session-state/07a1259e-4c05-47e6-9e0e-fda2af9fca6f/plan.md with 1485 characters
```


---

<sub>⏱️ 1m 59s</sub>

### 💬 Copilot

Now let me check the metadata to understand the app name and any resources:

---

<sub>⏱️ 2m 0s</sub>

### ✅ `bash`

**View metadata.yaml**

$ cat /tmp/saml-integrator-L3-opus/metadata.yaml

<details>
<summary>28 lines</summary>

```
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
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 2m 31s</sub>

### 💬 Copilot

Good - no resources in metadata.yaml. Now let me implement all the changes:

---

<sub>⏱️ 2m 31s</sub>

### ✅ `edit`

**/tmp/saml-integrator-L3-opus/tests/conftest.py**

/tmp/saml-integrator-L3-opus/tests/conftest.py

```
File /tmp/saml-integrator-L3-opus/tests/conftest.py updated with changes.
```


---

<sub>⏱️ 2m 31s</sub>

### ✅ `edit`

**/tmp/saml-integrator-L3-opus/tests/integration/conftest.py**

/tmp/saml-integrator-L3-opus/tests/integration/conftest.py

```
File /tmp/saml-integrator-L3-opus/tests/integration/conftest.py updated with changes.
```


---

<sub>⏱️ 2m 31s</sub>

### ✅ `edit`

**/tmp/saml-integrator-L3-opus/tests/integration/test_charm.py**

/tmp/saml-integrator-L3-opus/tests/integration/test_charm.py

```
File /tmp/saml-integrator-L3-opus/tests/integration/test_charm.py updated with changes.
```


---

<sub>⏱️ 2m 37s</sub>

### 💬 Copilot

Now update the dependencies in pyproject.toml:

---

<sub>⏱️ 2m 37s</sub>

### ✅ `edit`

**/tmp/saml-integrator-L3-opus/pyproject.toml**

/tmp/saml-integrator-L3-opus/pyproject.toml

```
File /tmp/saml-integrator-L3-opus/pyproject.toml updated with changes.
```


---

<sub>⏱️ 2m 43s</sub>

### 💬 Copilot

Now let me also check if `pytest-asyncio` and `pytest-operator` are still needed in the lint group (they are, since the linter may type-check all code including integration - but since we've removed the async code, let me check what remains):

---

<sub>⏱️ 2m 43s</sub>

### ✅ `grep`

**/tmp/saml-integrator-L3-opus**

"pytest.asyncio|pytest_asyncio|pytest.operator|pytest_operator|ops_test|OpsTest" (/tmp/saml-integrator-L3-opus)

```
/tmp/saml-integrator-L3-opus/pyproject.toml
/tmp/saml-integrator-L3-opus/uv.lock
```


---

<sub>⏱️ 2m 49s</sub>

### 💬 Copilot

Good - no more source code references. The remaining references in `pyproject.toml` are in the lint dependency group. Let me update those too since they're no longer needed for linting:

---

<sub>⏱️ 2m 49s</sub>

### ✅ `edit`

**/tmp/saml-integrator-L3-opus/pyproject.toml**

/tmp/saml-integrator-L3-opus/pyproject.toml

```
File /tmp/saml-integrator-L3-opus/pyproject.toml updated with changes.
```


---

<sub>⏱️ 2m 53s</sub>

### 💬 Copilot

Now let me verify all the changed files look correct:

---

<sub>⏱️ 2m 53s</sub>

### ✅ `view`

**/tmp/saml-integrator-L3-opus/tests/conftest.py**

/tmp/saml-integrator-L3-opus/tests/conftest.py

```
1. # Copyright 2025 Canonical Ltd.
2. # See LICENSE file for licensing details.
3. 
4. """Test fixtures."""
5. 
```


---

<sub>⏱️ 2m 53s</sub>

### ✅ `view`

**/tmp/saml-integrator-L3-opus/tests/integration/conftest.py**

/tmp/saml-integrator-L3-opus/tests/integration/conftest.py

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
9. import jubilant
10. import yaml
11. from pytest import fixture
12. from pytest_jubilant import pack
13. 
14. 
15. @fixture(scope="module", name="app_name")
16. def app_name_fixture():
17.     """Provide app name from the metadata."""
18.     metadata = yaml.safe_load(Path("./metadata.yaml").read_text("utf-8"))
19.     yield metadata["name"]
20. 
21. 
22. @fixture(scope="module", name="charm")
23. def charm_fixture():
24.     """Pack the charm and return the path."""
25.     yield pack()
26. 
27. 
28. @fixture(scope="module")
29. def app(juju: jubilant.Juju, charm: Path, app_name: str):
30.     """SAML Integrator charm used for integration testing.
31. 
32.     Build the charm and deploy it.
33.     """
34.     juju.deploy(charm, app_name)
35.     yield app_name
36. 
37. 
38. @fixture(scope="module")
39. def any_charm(juju: jubilant.Juju):
40.     """Deploy any-charm for testing the saml relation."""
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
52.         config={
53.             "python-packages": "pydantic>=2.12.5",
54.             "src-overwrite": json.dumps(src_overwrite),
55.         },
56.     )
57.     yield "any"
58.
```

</details>


---

<sub>⏱️ 2m 53s</sub>

### ✅ `view`

**/tmp/saml-integrator-L3-opus/tests/integration/test_charm.py**

/tmp/saml-integrator-L3-opus/tests/integration/test_charm.py

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
27.     assert status.apps[app].app_status.current == "active"
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
47.     assert status.apps[app].app_status.current == "active"
48.
```

</details>


---

<sub>⏱️ 2m 59s</sub>

### 💬 Copilot

Now let me regenerate the lock file and run linting to validate:

---

<sub>⏱️ 2m 59s</sub>

### ✅ `bash`

**Regenerate uv.lock**

$ cd /tmp/saml-integrator-L3-opus && uv lock 2>&1 | tail -10

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

<sub>⏱️ 3m 4s</sub>

### 💬 Copilot

Good, the lock file updated successfully. Now run the linter:

---

<sub>⏱️ 3m 4s</sub>

### ✅ `bash`

**Run ruff lint on changed files**

$ cd /tmp/saml-integrator-L3-opus && uv run --group lint ruff check tests/integration/ tests/conftest.py 2>&1

<details>
<summary>6 lines</summary>

```
Using CPython 3.12.3 interpreter at: /usr/bin/python3
Creating virtual environment at: .venv
░░░░░░░░░░░░░░░░░░░░ [0/0] Installing wheels...                                                                         ░░░░░░░░░░░░░░░░░░░░ [0/42] Installing wheels...                                                                        ░░░░░░░░░░░░░░░░░░░░ [0/42] annotated-types==0.7.0                                                                      ░░░░░░░░░░░░░░░░░░░░ [1/42] annotated-types==0.7.0                                                                      ░░░░░░░░░░░░░░░░░░░░ [1/42] pytest-jubilant==1.1                                                                        ░░░░░░░░░░░░░░░░░░░░ [2/42] pytest-jubilant==1.1                                                                        ░░░░░░░░░░░░░░░░░░░░ [2/42] requests==2.32.5                                                                            █░░░░░░░░░░░░░░░░░░░ [3/42] requests==2.32.5                                                                            █░░░░░░░░░░░░░░░░░░░ [3/42] packaging==25.0                                                                             █░░░░░░░░░░░░░░░░░░░ [4/42] packaging==25.0                                                                             █░░░░░░░░░░░░░░░░░░░ [4/42] types-mock==5.2.0.20250924                                                                  ██░░░░░░░░░░░░░░░░░░ [5/42] types-mock==5.2.0.20250924                                                                  ██░░░░░░░░░░░░░░░░░░ [5/42] types-requests==2.32.4.20250913                                                             ██░░░░░░░░░░░░░░░░░░ [6/42] types-requests==2.32.4.20250913                                                             ██░░░░░░░░░░░░░░░░░░ [6/42] ruff==0.14.6                                                                                ███░░░░░░░░░░░░░░░░░ [7/42] ruff==0.14.6                                                                                ███░░░░░░░░░░░░░░░░░ [7/42] pydantic-core==2.41.5                                                                       ███░░░░░░░░░░░░░░░░░ [8/42] pydantic-core==2.41.5                                                                       ███░░░░░░░░░░░░░░░░░ [8/42] pycodestyle==2.14.0                                                                         ████░░░░░░░░░░░░░░░░ [9/42] pycodestyle==2.14.0                                                                         Installed 42 packages in 13ms
warning: Selection `CPY` has no effect because preview is not enabled.
All checks passed!
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 3m 9s</sub>

### 💬 Copilot

Let me also run mypy and codespell to be thorough:

---

<sub>⏱️ 3m 11s</sub>

### ✅ `bash`

**Run mypy on changed files**

$ cd /tmp/saml-integrator-L3-opus && uv run --group lint mypy tests/integration/ tests/conftest.py 2>&1 | tail -10

```
Success: no issues found in 5 source files
<exited with exit code 0>
```


---

<sub>⏱️ 3m 16s</sub>

### 💬 Copilot

Let me also verify the unit tests still pass (since we only changed integration test files, this should work fine):

---

<sub>⏱️ 3m 17s</sub>

### ✅ `bash`

**Run unit tests**

$ cd /tmp/saml-integrator-L3-opus && uv run --group unit coverage run --source=src/,lib/charms/saml_integrator -m pytest --ignore=tests/integration --ignore=tests/interface -v --tb=native -s 2>&1 | tail -15

<details>
<summary>13 lines</summary>

```
tests/unit/test_library_saml.py::test_requirer_charm_emits_event[False]
  /tmp/saml-integrator-L3-opus/tests/unit/test_library_saml.py:150: PendingDeprecationWarning: Harness is deprecated. For the recommended approach, see: https://documentation.ubuntu.com/ops/latest/howto/write-unit-tests-for-a-charm/
    harness = Harness(SamlRequirerCharm, meta=REQUIRER_METADATA)

tests/unit/test_saml.py::test_saml_with_valid_signed_metadata
tests/unit/test_saml.py::test_saml_with_valid_tampered_signed_metadata
  /tmp/saml-integrator-L3-opus/src/saml.py:80: FutureWarning: Truth-testing of elements was a source of confusion and will always return True in future versions. Use specific 'len(elem)' or 'elem is not None' test instead.
    if self.signing_certificate and self.signature:

tests/unit/test_saml.py::test_saml_with_valid_signed_metadata
  /tmp/saml-integrator-L3-opus/.venv/lib/python3.12/site-packages/signxml/processor.py:22: DeprecationWarning: open_text is deprecated. Use files() instead. Refer to https://importlib-resources.readthedocs.io/en/latest/using.html#migrating-from-legacy for migration advice.
    with importlib.resources.open_text(pkg_name, schema_file) as schema_fh:

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
======================= 20 passed, 11 warnings in 0.58s ========================
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 3m 22s</sub>

### 💬 Copilot

All unit tests pass. Let me do a final review of the diff:

---

<sub>⏱️ 3m 22s</sub>

### ✅ `bash`

**Review full diff**

$ cd /tmp/saml-integrator-L3-opus && git --no-pager diff --stat && echo "---" && git --no-pager diff -- tests/ pyproject.toml

<details>
<summary>186 lines</summary>

```diff
pyproject.toml                  |  10 +-
 tests/conftest.py               |  11 -
 tests/integration/conftest.py   |  48 ++---
 tests/integration/test_charm.py |  36 ++--
 uv.lock                         | 871 ++------------------------------------------------------------------------------
 5 files changed, 58 insertions(+), 918 deletions(-)
---
diff --git a/pyproject.toml b/pyproject.toml
index 59170c2..4409058 100644
--- a/pyproject.toml
+++ b/pyproject.toml
@@ -32,8 +32,7 @@ lint = [
   "ops-scenario",
   "pep8-naming",
   "pytest",
-  "pytest-asyncio",
-  "pytest-operator",
+  "pytest-jubilant",
   "requests",
   "ruff",
   "types-mock",
@@ -57,12 +56,9 @@ interface = [
   "pytest-interface-tester",
 ]
 integration = [
-  "allure-pytest>=2.8.18",
-  "allure-pytest-collection-report @ git+https://github.com/canonical/data-platform-workflows@v24.0.0#subdirectory=python/pytest_plugins/allure_pytest_collection_report",
-  "juju",
+  "jubilant",
   "pytest",
-  "pytest-asyncio",
-  "pytest-operator",
+  "pytest-jubilant",
 ]
 
 [tool.uv]
diff --git a/tests/conftest.py b/tests/conftest.py
index 33cbabe..30b6048 100644
--- a/tests/conftest.py
+++ b/tests/conftest.py
@@ -2,14 +2,3 @@
 # See LICENSE file for licensing details.
 
 """Test fixtures."""
-
-import pytest
-
-
-def pytest_addoption(parser: pytest.Parser):
-    """Add test arguments.
-
-    Args:
-        parser: pytest parser.
-    """
-    parser.addoption("--charm-file", action="store")
diff --git a/tests/integration/conftest.py b/tests/integration/conftest.py
index e933368..c509f62 100644
--- a/tests/integration/conftest.py
+++ b/tests/integration/conftest.py
@@ -6,10 +6,10 @@
 import json
 from pathlib import Path
 
-import pytest_asyncio
+import jubilant
 import yaml
-from pytest import Config, fixture
-from pytest_operator.plugin import OpsTest
+from pytest import fixture
+from pytest_jubilant import pack
 
 
 @fixture(scope="module", name="app_name")
@@ -19,27 +19,25 @@ def app_name_fixture():
     yield metadata["name"]
 
 
-@pytest_asyncio.fixture(scope="module")
-async def app(ops_test: OpsTest, pytestconfig: Config, app_name: str):
-    """SAML Integrator charm used for integration testing.
-
-    Build the charm and deploy it along with Anycharm.
-    """
-    charm = pytestconfig.getoption("--charm-file")
-    assert ops_test.model
-    application = await ops_test.model.deploy(
-        f"./{charm}",
-        application_name=app_name,
-    )
-    yield application
+@fixture(scope="module", name="charm")
+def charm_fixture():
+    """Pack the charm and return the path."""
+    yield pack()
 
 
-@pytest_asyncio.fixture(scope="module")
-async def any_charm(ops_test: OpsTest):
+@fixture(scope="module")
+def app(juju: jubilant.Juju, charm: Path, app_name: str):
     """SAML Integrator charm used for integration testing.
 
-    Build the charm and deploy it along with Anycharm.
+    Build the charm and deploy it.
     """
+    juju.deploy(charm, app_name)
+    yield app_name
+
+
+@fixture(scope="module")
+def any_charm(juju: jubilant.Juju):
+    """Deploy any-charm for testing the saml relation."""
     path_lib = "lib/charms/saml_integrator/v0/saml.py"
     saml_lib = Path(path_lib).read_text(encoding="utf8")
     any_charm_script = Path("tests/integration/any_charm.py").read_text(encoding="utf8")
@@ -47,11 +45,13 @@ async def any_charm(ops_test: OpsTest):
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
-        config={"python-packages": "pydantic>=2.12.5", "src-overwrite": json.dumps(src_overwrite)},
+        config={
+            "python-packages": "pydantic>=2.12.5",
+            "src-overwrite": json.dumps(src_overwrite),
+        },
     )
-    yield application
+    yield "any"
diff --git a/tests/integration/test_charm.py b/tests/integration/test_charm.py
index de64441..e50cc49 100644
--- a/tests/integration/test_charm.py
+++ b/tests/integration/test_charm.py
@@ -4,48 +4,44 @@
 
 """SAML Integrator charm integration tests."""
 
-import ops
+import jubilant
 import pytest
-from pytest_operator.plugin import OpsTest
 
 
-@pytest.mark.asyncio
 @pytest.mark.abort_on_fail
-async def test_active(ops_test: OpsTest, app: ops.Application):
+def test_active(juju: jubilant.Juju, app: str):
     """Check that the charm is active.
 
     Assume that the charm has already been built and is running.
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
+    juju.wait(jubilant.all_active, error=jubilant.any_error)
+    status = juju.status()
+    assert status.apps[app].app_status.current == "active"
 
 
-@pytest.mark.asyncio
 @pytest.mark.abort_on_fail
-async def test_relation(ops_test: OpsTest, app: ops.Application, any_charm: ops.Application):
+def test_relation(juju: jubilant.Juju, app: str, any_charm: str):
     """Check that the charm is active once related to another charm.
 
     Assume that the charm has already been built and is running.
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
+    juju.wait(jubilant.all_active, error=jubilant.any_error)
+    status = juju.status()
+    assert status.apps[app].app_status.current == "active"
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 3m 31s</sub>

### 💬 Copilot

Everything looks clean. Let me commit the changes:

---

<sub>⏱️ 3m 32s</sub>

### ✅ `bash`

**Commit all changes**

$ cd /tmp/saml-integrator-L3-opus && git add -A && git commit -m "Migrate integration tests from pytest-operator to jubilant

Replace python-libjuju/pytest-operator with jubilant and pytest-jubilant:

- Convert async tests to synchronous using jubilant.Juju API
- Replace OpsTest fixture with juju fixture from pytest-jubilant
- Use juju.deploy(), juju.config(), juju.integrate(), juju.wait()
- Use jubilant.all_active/any_error for wait conditions
- Add charm fixture using pytest_jubilant.pack()
- Remove --charm-file CLI option (pytest-jubilant handles packing)
- Update integration and lint dependency groups in pyproject.toml
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

<sub>⏱️ 3m 40s</sub>

### ✅ `bash`

**Commit changes**

$ cd /tmp/saml-integrator-L3-opus && git config user.email "copilot@github.com" && git config user.name "Copilot" && git add -A && git commit -m "Migrate integration tests from pytest-operator to jubilant

Replace python-libjuju/pytest-operator with jubilant and pytest-jubilant:

- Convert async tests to synchronous using jubilant.Juju API
- Replace OpsTest fixture with juju fixture from pytest-jubilant
- Use juju.deploy(), juju.config(), juju.integrate(), juju.wait()
- Use jubilant.all_active/any_error for wait conditions
- Add charm fixture using pytest_jubilant.pack()
- Remove --charm-file CLI option (pytest-jubilant handles packing)
- Update integration and lint dependency groups in pyproject.toml
- Regenerate uv.lock

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"

```
[main fad28d9] Migrate integration tests from pytest-operator to jubilant
 5 files changed, 58 insertions(+), 918 deletions(-)
<exited with exit code 0>
```


---

<sub>⏱️ 3m 48s</sub>

### 💬 Copilot

Migration complete. Here's what changed:

- **`tests/integration/test_charm.py`** — Converted from async (`pytest-asyncio`, `OpsTest`) to sync using `jubilant.Juju`. Tests now use `juju.config()`, `juju.integrate()`, and `juju.wait(jubilant.all_active, error=jubilant.any_error)`.
- **`tests/integration/conftest.py`** — Replaced `pytest_asyncio` fixtures with sync ones. Added a `charm` fixture using `pytest_jubilant.pack()`, and fixtures now yield app name strings (used by `juju.deploy()`) instead of `ops.Application` objects.
- **`tests/conftest.py`** — Removed the `--charm-file` option (pytest-jubilant handles charm packing).
- **`pyproject.toml`** — Replaced `juju`, `pytest-asyncio`, `pytest-operator`, and allure deps with `jubilant` and `pytest-jubilant` in both `integration` and `lint` groups.

---

<sub>Generated by [GitHub Copilot CLI](https://github.com/features/copilot/cli)</sub>
