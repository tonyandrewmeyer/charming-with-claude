# 🤖 Copilot CLI Session

> **Session ID:** `41a90c79-d9e9-49a7-a627-d1622c940f7c`
> **Started:** 3/7/2026, 3:02:52 PM
> **Duration:** 7m 36s
> **Exported:** 3/7/2026, 3:10:28 PM

<sub>⏱️ 5s</sub>

### 👤 User

IMPORTANT: You are running in non-interactive mode. For all decision points in the recipe below, use these defaults: (1) abort_on_fail: remove the markers and use --failfast, (2) test execution: skip test execution (we cannot run tests in this environment), (3) tox runner: use 'tox' directly, (4) quality check failures: fix them automatically, (5) at all checkpoints: continue without pausing.

Before beginning the migration, clone https://github.com/canonical/wordpress-k8s-operator and study its tests/integration/ directory as a working example of what the final result should look like.

Now proceed with the migration following the recipe below:

# Migrate Integration Tests from Ops to Jubilant

You are migrating this charm's integration tests from `pytest-operator` (ops framework) to `jubilant` + `pytest-jubilant`.

---

## BEFORE YOU BEGIN: Quality Check Validation

**This step is MANDATORY and must be completed before any migration work.**

### Step 0: Detect and Validate Quality Checks

1. **Check for tox.ini in the repository root:**
   - If `tox.ini` exists: parse it to identify available environments
   - If `tox.ini` does NOT exist: **STOP and report to user**

2. **If tox.ini is missing:**
   ```
   ⚠️  QUALITY CHECKS NOT CONFIGURED

   No tox.ini found in this repository. Quality checks (fmt, lint, static)
   cannot be validated automatically.

   Options:
   1. Create a tox.ini with quality check environments
   2. Proceed without automated quality checks (NOT RECOMMENDED)

   Do you want to proceed without quality checks?
   ```

   **🛑 WAIT FOR USER RESPONSE - Do not proceed without explicit permission.**

3. **If tox.ini exists, identify quality environments:**
   Look for environments matching these patterns:
   - `fmt` / `format` / `black` / `ruff-format` - code formatting
   - `lint` / `ruff` / `flake8` / `pylint` - linting
   - `static` / `type` / `mypy` / `pyright` - static type checking

   Report what was found:
   ```
   ✓ Quality check environments detected in tox.ini:
     - fmt: [environment name]
     - lint: [environment name]
     - static: [environment name]

   These will be run after migration to catch any issues.
   ```

4. **If required environments are missing:**
   ```
   ⚠️  INCOMPLETE QUALITY CHECKS

   tox.ini exists but missing some quality environments:
     ✓ fmt: found
     ✗ lint: NOT FOUND
     ✗ static: NOT FOUND

   Proceed with available checks only?
   ```

   **🛑 WAIT FOR USER RESPONSE**

---

## Critical Instructions - Human Guidance Required

**The following decisions REQUIRE human input. DO NOT proceed with assumptions.**

### 🛑 CRITICAL DECISION POINTS

Throughout this migration, you MUST stop and wait for user input at these points:

| Decision Point | Why Human Input Required |
|---------------|-------------------------|
| `@pytest.mark.abort_on_fail` handling | Multiple valid approaches exist |
| Test execution strategy | User may prefer manual testing |
| Tox runner command | Environment-specific (`uvx tox` vs `tox` vs custom) |
| Quality check failures | User decides fix priority |
| Blocked/errored charms during test | May require domain knowledge |

**When you reach these points:**
1. Present the options clearly
2. State "Waiting for your decision before proceeding"
3. **DO NOT make assumptions or proceed with a default**

---

## State Management

**State file:** `.agent/state/jubilant-migration.md`

### On Start

1. Create `.agent/state/` directory if it doesn't exist
2. Check if state file exists
3. If exists: read it, show user current progress, ask "Continue from where you left off, or start fresh?"
4. If not exists: analyze tests and create state file with full plan

### During Work

- Update state file after completing each major task
- Mark items: `[x]` done, `[-]` blocked, `[ ]` pending
- Add notes about decisions, blockers, or context

### Checkpoints

At these points, ask the user: "Do you want to continue, or pause and save progress?"

- After conftest.py migration
- After helpers.py migration
- After each test file migration
- Before running tests
- After fixing test failures
- **After each quality check run**

### State File Template

```markdown
# Jubilant Migration State

**Started:** {date}
**Last Updated:** {date}
**Status:** in_progress | completed | blocked

## Quality Check Configuration

- tox.ini found: yes/no
- fmt environment: {name or "not found"}
- lint environment: {name or "not found"}
- static environment: {name or "not found"}

## Files to Migrate

- [ ] `tests/integration/conftest.py`
- [ ] `tests/integration/helpers.py`
- [ ] `tests/integration/test_charm_scaling.py`
- [ ] `tests/integration/test_charm_ipa.py`
- [ ] ... (list all test files)

## Current Task

{What is currently being worked on}

## Progress

### conftest.py
- [ ] Remove pytest-operator imports
- [ ] Add jubilant/pytest-jubilant imports
- [ ] Convert charm fixture to use pack()
- [ ] Add resources fixture with get_resources()
- [ ] Remove async from fixtures
- [ ] Update multi-model fixtures to use temp_model_factory

### helpers.py
- [ ] Remove async from functions
- [ ] Replace subprocess juju calls with juju.cli()
- [ ] Keep lightkube code as-is

### test_charm_scaling.py
- [ ] Convert async→sync
- [ ] Replace OpsTest with Juju
- [ ] Update deploy/wait/integrate calls
- [ ] Add @pytest.mark.setup where appropriate

... (repeat for each test file)

## Dependencies

- [ ] Update pyproject.toml: add jubilant, pytest-jubilant
- [ ] Update pyproject.toml: remove pytest-operator

## Quality Checks

- [ ] Run fmt - fix any formatting issues
- [ ] Run lint - fix any linting errors
- [ ] Run static - fix any type errors

## Test Execution

- [ ] Run simple test file
- [ ] Fix issues
- [ ] Run full suite --failfast
- [ ] All tests pass

## Notes

{Decisions, blockers, context}

## Next Session

{What to do when resuming}
```

---

## Library Responsibilities

**jubilant** (core library):
- `Juju` class - main interface for juju operations
- `all_active`, `all_blocked`, `any_active`, etc. - wait condition helpers
- `Status`, `CLIError`, `WaitError` - types and exceptions

**pytest-jubilant** (pytest plugin):
- `pack()` - builds charm (replaces `ops_test.build_charm()`)
- `get_resources()` - extracts resources from charmcraft.yaml
- `juju` fixture - provides `Juju` instance connected to temp model
- `temp_model_factory` fixture - for multi-model testing
- `--model`, `--keep-models`, `--no-setup`, `--no-teardown` CLI options
- `@pytest.mark.setup` and `@pytest.mark.teardown` markers

## Key Differences

| Ops (pytest-operator) | Jubilant + pytest-jubilant |
|----------------------|----------------------------|
| `from pytest_operator.plugin import OpsTest` | `from jubilant import Juju, all_active` |
| `async def test_foo(ops_test: OpsTest)` | `def test_foo(juju: Juju)` |
| `await ops_test.build_charm(".")` | `from pytest_jubilant import pack; pack()` |
| Manual resources dict | `from pytest_jubilant import get_resources; get_resources()` |
| `await ops_test.model.deploy(...)` | `juju.deploy(...)` |
| `await ops_test.model.wait_for_idle([apps], status="active")` | `juju.wait(lambda s: all_active(s, *apps), timeout=N, delay=5, successes=3)` |
| `await ops_test.model.add_relation(a, b)` | `juju.integrate(a, b)` |
| `await ops_test.model.applications[app].set_config({...})` | `juju.config(app, {...})` |
| `await ops_test.model.applications[app].scale(n)` | `juju.add_unit(app, num_units=delta)` |
| `ops_test.model.name` | `juju.model` |
| `ops_test.track_model("alias")` | `temp_model_factory.get_juju("suffix")` |
| subprocess juju commands | `juju.cli("cmd", "arg")` or `juju.ssh(unit, cmd)` |

## Migration Steps

### Step 1: Analyze & Plan

1. Read all test files
2. Create state file with checklist
3. Present plan to user, wait for approval

### Step 2: Migrate conftest.py

```python
# BEFORE (ops)
from pytest_operator.plugin import OpsTest

@pytest.fixture(scope="module")
async def charm(ops_test: OpsTest):
    return await ops_test.build_charm(".")

# AFTER (jubilant + pytest-jubilant)
from pytest_jubilant import pack, get_resources

@pytest.fixture(scope="session")
def charm():
    if charm_file := os.environ.get("CHARM_PATH"):
        return Path(charm_file)
    return pack()

@pytest.fixture(scope="session")
def resources():
    return get_resources()
```

**🛑 CHECKPOINT:** Ask user to continue or pause.

### Step 3: Migrate helpers.py

- Remove async
- Replace subprocess juju calls with `juju.cli()` / `juju.ssh()`
- Keep lightkube code as-is

**🛑 CHECKPOINT:** Ask user to continue or pause.

### Step 4: Migrate Test Files (one at a time)

```python
# BEFORE
@pytest.mark.abort_on_fail
async def test_deploy(ops_test: OpsTest, charm):
    await ops_test.model.deploy(charm, ...)
    await ops_test.model.wait_for_idle([APP_NAME], status="active")

# AFTER
from jubilant import Juju, all_active

@pytest.mark.setup
@pytest.mark.abort_on_fail
def test_deploy(juju: Juju, charm, resources):
    juju.deploy(charm, app=APP_NAME, resources=resources, trust=True)
    juju.wait(lambda s: all_active(s, APP_NAME), timeout=1000, delay=5, successes=3)
```

**🛑 CHECKPOINT after each file:** Ask user to continue or pause.

### Step 5: Update Dependencies

- Add `jubilant`, `pytest-jubilant` to pyproject.toml
- Remove `pytest-operator`

**🛑 CHECKPOINT:** Ask user to continue or pause.

### Step 6: Run Quality Checks

**This step is MANDATORY before test execution.**

1. **Run formatting check:**
   ```bash
   # Detect and use the appropriate command
   tox -e fmt  # or equivalent detected environment
   ```

2. **Run linting:**
   ```bash
   tox -e lint  # or equivalent detected environment
   ```

3. **Run static analysis:**
   ```bash
   tox -e static  # or equivalent detected environment
   ```

4. **On failures:**
   ```
   ⚠️  QUALITY CHECK FAILURES DETECTED

   {Show the specific errors}

   Options:
   1. Fix these issues now (RECOMMENDED)
   2. Skip and proceed to test execution

   How do you want to proceed?
   ```

   **🛑 WAIT FOR USER RESPONSE - Do not auto-fix without permission**

5. **Fix issues and re-run until clean**

**🛑 CHECKPOINT:** Ask user to continue or pause.

### Step 7: Test Execution

**🛑 CRITICAL DECISION REQUIRED:**

Ask user:
1. "Do you want to run tests yourself, or should I run and iterate on failures?"
2. (if model runs) "What command do you use to run tox?"
   - Examples: `uvx tox`, `tox`, `python -m tox`, custom script

**DO NOT assume `uvx tox` or any default. Wait for user response.**

**If model runs tests:**

1. **Detect required Python version** by checking (in order):
   - `pyproject.toml` → `[project].requires-python` or `[tool.poetry.dependencies].python`
   - `tox.ini` → `basepython`
   - `.python-version` file
   - Use detected version with the user's tox command

2. **Run tests in background** with reduced log noise:
   ```bash
   {user's tox command} -e integration -- tests/integration/test_X.py -x --log-cli-level=WARNING &
   ```
   Use `--log-cli-level=WARNING` to avoid context pollution from verbose juju status logs.

3. **Periodically check output** using the task output tool or by tailing logs

4. **Check juju status of test model** - tests may hang if charms are blocked/error:
   ```bash
   juju status -m \<test-model-name\>
   ```
   Look for:
   - Charms stuck in `blocked`, `error`, or `waiting` status
   - Status messages explaining why (missing relation, bad config, etc.)
   - If stuck, this is likely the root cause - fix the charm issue, not the test

5. **Update user on progress:**
   - "Tests running... currently on test_deploy"
   - "Test failed at test_scaling - analyzing..."
   - "3/5 tests passed so far"
   - "Charm X is blocked: 'missing relation to Y' - investigating..."

6. **On failure:**
   - Analyze output
   - Check juju status
   - **Present findings and ask user how to proceed before making fixes**

7. **🛑 CHECKPOINT:** Ask user to continue or pause

8. **Expand to full suite** once individual files pass:
   ```bash
   {user's tox command} -e integration -- --failfast --log-cli-level=WARNING &
   ```

### Step 8: Final Quality Check

After all tests pass, run quality checks one more time:

1. Run fmt, lint, static environments
2. Ensure no regressions were introduced during test fixes
3. Report final status to user

---

## Common Patterns to Update

### @pytest.mark.abort_on_fail

**🛑 CRITICAL DECISION REQUIRED - DO NOT PROCEED WITHOUT USER INPUT**

`abort_on_fail` is **pytest-operator specific** - it xfails remaining tests if the marked test fails. pytest-jubilant does NOT have this.

**You MUST ask the user:**

```
The tests use @pytest.mark.abort_on_fail which doesn't exist in pytest-jubilant.

Options:
1. Use `--failfast` flag - stops on first failure (simpler)
2. Add `pytest-dependency` plugin - explicit test dependencies
3. Remove markers entirely - tests fail normally
4. Keep markers as documentation - shows intent but won't function

Which approach do you prefer?
```

**Wait for user response before proceeding.**

### CharmDeploymentConfiguration Dataclass

Ops-based tests often use a dataclass with `entity_url` and `application_name`. Update to match jubilant's API:

```python
# BEFORE (ops naming)
@dataclass
class CharmDeploymentConfiguration:
    entity_url: str
    application_name: str
    channel: str
    trust: bool

# Using it with ops
await ops_test.model.deploy(
    cfg.entity_url,
    application_name=cfg.application_name,
    ...
)

# AFTER (jubilant naming)
@dataclass
class CharmDeploymentConfiguration:
    charm: str          # was entity_url
    app: str            # was application_name
    channel: str
    trust: bool

# Using it with jubilant
juju.deploy(
    charm=cfg.charm,
    app=cfg.app,
    ...
)
```

Or use `**asdict(cfg)` if field names match jubilant's API exactly.

## Multi-Model Testing

```python
@pytest.fixture(scope="module")
def istio_juju(temp_model_factory):
    istio_juju = temp_model_factory.get_juju("istio-system")
    istio_juju.deploy(...)
    return istio_juju
```

## Pausing Work

When user chooses to pause:

1. Update state file with current progress
2. Mark completed items `[x]`
3. Fill in "Current Task" and "Next Session" sections
4. Tell user: "Progress saved to `.agent/state/jubilant-migration.md`. Re-run this command to continue."

---

## Summary of Required User Interactions

For reference, here are ALL points where you MUST wait for user input:

1. **tox.ini missing** - Permission to proceed without quality checks
2. **Quality environments incomplete** - Permission to proceed with partial checks
3. **Each checkpoint** - Continue or pause decision
4. **@pytest.mark.abort_on_fail** - Strategy selection
5. **Test execution** - Self-run vs model-run decision
6. **Tox command** - User's specific command
7. **Quality check failures** - Fix now or skip
8. **Test failures** - Review findings before fixing
9. **Blocked charms** - May require domain-specific decisions

**Never assume defaults for these decisions.**

---

<sub>⏱️ 15s</sub>

### ✅ `bash`

**List integration test files and view tox.ini**

$ find /tmp/s3-integrator-L6-recipe-example-sonnet-4.6/tests/integration -type f | sort && echo "---" && cat /tmp/s3-integrator-L6-recipe-example-sonnet-4.6/tox.ini

<details>
<summary>70 lines</summary>

```
/tmp/s3-integrator-L6-recipe-example-sonnet-4.6/tests/integration/__init__.py
/tmp/s3-integrator-L6-recipe-example-sonnet-4.6/tests/integration/application-charm/actions.yaml
/tmp/s3-integrator-L6-recipe-example-sonnet-4.6/tests/integration/application-charm/charmcraft.yaml
/tmp/s3-integrator-L6-recipe-example-sonnet-4.6/tests/integration/application-charm/lib/charms/data_platform_libs/v0/s3.py
/tmp/s3-integrator-L6-recipe-example-sonnet-4.6/tests/integration/application-charm/metadata.yaml
/tmp/s3-integrator-L6-recipe-example-sonnet-4.6/tests/integration/application-charm/poetry.lock
/tmp/s3-integrator-L6-recipe-example-sonnet-4.6/tests/integration/application-charm/pyproject.toml
/tmp/s3-integrator-L6-recipe-example-sonnet-4.6/tests/integration/application-charm/src/charm.py
/tmp/s3-integrator-L6-recipe-example-sonnet-4.6/tests/integration/architecture.py
/tmp/s3-integrator-L6-recipe-example-sonnet-4.6/tests/integration/helpers.py
/tmp/s3-integrator-L6-recipe-example-sonnet-4.6/tests/integration/test_s3_charm.py
---
# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.

[tox]
no_package = True
skip_missing_interpreters = True
env_list = lint, unit

[vars]
src_path = {tox_root}/src
tests_path = {tox_root}/tests
test_charm_libs_path = {[vars]tests_path}/integration/application-charm/lib/
all_path = {[vars]src_path} {[vars]tests_path}

[testenv]
set_env =
    PYTHONPATH = {tox_root}/lib:{[vars]src_path}
    PYTHONBREAKPOINT=ipdb.set_trace
    PY_COLORS=1
pass_env =
    PYTHONPATH
    CHARM_BUILD_DIR
    MODEL_SETTINGS
allowlist_externals =
    poetry

[testenv:format]
description = Apply coding style standards to code
commands_pre =
    poetry install --only format --no-root
commands =
    poetry lock
    poetry run ruff check --fix {[vars]all_path} --exclude {[vars]test_charm_libs_path}
    poetry run ruff format {[vars]all_path} --exclude {[vars]test_charm_libs_path}

[testenv:lint]
description = Check code against coding style standards
commands_pre =
    poetry install --only lint,format --no-root
commands =
    poetry check --lock
    poetry run codespell {[vars]all_path}
    poetry run ruff check {[vars]all_path} --exclude {[vars]test_charm_libs_path}
    poetry run ruff format --check --diff {[vars]all_path} --exclude {[vars]test_charm_libs_path}

[testenv:unit]
description = Run unit tests
commands_pre =
    poetry install --only main,charm-libs,unit --no-root
commands =
    poetry run coverage run --source={[vars]src_path} \
        -m pytest -v --tb native -s {posargs} {[vars]tests_path}/unit
    poetry run coverage report

[testenv:integration]
description = Run integration tests
pass_env =
    CI
    GITHUB_OUTPUT
    SECRETS_FROM_GITHUB
commands_pre =
    poetry install --only integration --no-root
commands =
    poetry run pytest -v --tb native --log-cli-level=INFO -s --ignore={[vars]tests_path}/unit/ {posargs}
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 15s</sub>

### ✅ `bash`

**View pyproject.toml**

$ cat /tmp/s3-integrator-L6-recipe-example-sonnet-4.6/pyproject.toml

<details>
<summary>78 lines</summary>

```
# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.

[tool.poetry]
package-mode = false
requires-poetry = ">=2.0.0"

[tool.poetry.dependencies]
python = "^3.10"
ops = "^3.6.0"

[tool.poetry.group.charm-libs.dependencies]

[tool.poetry.group.format]
optional = true

[tool.poetry.group.format.dependencies]
ruff = "^0.15.4"

[tool.poetry.group.lint]
optional = true

[tool.poetry.group.lint.dependencies]
codespell = "^2.4.1"

[tool.poetry.group.unit.dependencies]
coverage = {extras = ["toml"], version = "^7.13.4"}
pytest = "^8.4.2"
pytest-asyncio = "*"
parameterized = "^0.9.0"

[tool.poetry.group.integration.dependencies]
pytest = "^8.4.2"
pytest-operator = "^0.43.2"
juju = "^3.5.2.0"

# Testing tools configuration
[tool.coverage.run]
branch = true

[tool.coverage.report]
show_missing = true

[tool.pytest.ini_options]
minversion = "6.0"
log_cli_level = "INFO"
asyncio_mode = "auto"
markers = ["unstable"]

# Formatting tools configuration
[tool.black]
line-length = 99
target-version = ["py310"]

# Linting tools configuration
[tool.ruff]
# preview and explicit preview are enabled for CPY001
preview = true
target-version = "py310"
src = ["src", "."]
line-length = 99

[tool.ruff.lint]
explicit-preview-rules = true
select = ["A", "E", "W", "F", "C", "N", "D", "I001", "CPY001"]
extend-ignore = [
    "D203",
    "D204",
    "D213",
    "D215",
    "D400",
    "D404",
    "D406",
    "D407",
    "D408",
    "D409",
    "D413",
]
# Ignore E501 because using black creates errors with this
# Ignore D107 Missing docstring in __init__
ignore = ["E501", "D107"]

[tool.ruff.lint.per-file-ignores]
"tests/*" = ["D100", "D101", "D102", "D103", "D104"]

[tool.ruff.lint.flake8-copyright]
# Check for properly formatted copyright header in each file
author = "Canonical Ltd."
notice-rgx = "Copyright\\s\\d{4}([-,]\\d{4})*\\s+"
min-file-size = 1

[tool.ruff.lint.mccabe]
max-complexity = 10

[tool.ruff.lint.pydocstyle]
convention = "google"
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 20s</sub>

### ✅ `bash`

**View integration test files**

$ cat /tmp/s3-integrator-L6-recipe-example-sonnet-4.6/tests/integration/test_s3_charm.py && echo "===" && cat /tmp/s3-integrator-L6-recipe-example-sonnet-4.6/tests/integration/helpers.py && echo "===" && cat /tmp/s3-integrator-L6-recipe-example-sonnet-4.6/tests/integration/architecture.py

<details>
<summary>368 lines</summary>

```
#!/usr/bin/env python3
# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.
import asyncio
import base64
import json
import logging
from pathlib import Path

import pytest
import yaml
from pytest_operator.plugin import OpsTest

from . import architecture
from .helpers import (
    fetch_action_get_connection_info,
    fetch_action_sync_s3_credentials,
    get_application_data,
    get_certificate_from_file,
    get_relation_data,
    is_relation_broken,
    is_relation_joined,
)

logger = logging.getLogger(__name__)

S3_METADATA = yaml.safe_load(Path("./metadata.yaml").read_text())
S3_APP_NAME = S3_METADATA["name"]

APP_METADATA = yaml.safe_load(
    Path("./tests/integration/application-charm/metadata.yaml").read_text()
)
APPLICATION_APP_NAME = APP_METADATA["name"]

APPS = [S3_APP_NAME, APPLICATION_APP_NAME]
FIRST_RELATION = "first-s3-credentials"
SECOND_RELATION = "second-s3-credentials"


@pytest.mark.group(1)
@pytest.mark.abort_on_fail
@pytest.mark.skip_if_deployed
async def test_build_and_deploy(ops_test: OpsTest):
    """Build the charm and deploy 1 units for provider and requirer charm."""
    # Build and deploy charm from local source folder
    s3_charm = f"./s3-integrator_ubuntu@22.04-{architecture.architecture}.charm"
    app_charm = f"./tests/integration/application-charm/application_ubuntu@22.04-{architecture.architecture}.charm"

    await asyncio.gather(
        ops_test.model.deploy(s3_charm, application_name=S3_APP_NAME, num_units=1),
        ops_test.model.deploy(app_charm, application_name=APPLICATION_APP_NAME, num_units=1),
    )
    # Reduce the update_status frequency until the cluster is deployed
    async with ops_test.fast_forward():
        await ops_test.model.block_until(
            lambda: len(ops_test.model.applications[S3_APP_NAME].units) == 1
        )

        await ops_test.model.block_until(
            lambda: len(ops_test.model.applications[APPLICATION_APP_NAME].units) == 1
        )
        await asyncio.gather(
            ops_test.model.wait_for_idle(
                apps=[S3_APP_NAME],
                status="blocked",
                timeout=1000,
            ),
            ops_test.model.wait_for_idle(
                apps=[APPLICATION_APP_NAME],
                status="waiting",
                raise_on_blocked=True,
                timeout=1000,
            ),
        )

    assert len(ops_test.model.applications[S3_APP_NAME].units) == 1

    for unit in ops_test.model.applications[S3_APP_NAME].units:
        assert unit.workload_status == "blocked"

    assert len(ops_test.model.applications[APPLICATION_APP_NAME].units) == 1


@pytest.mark.group(1)
@pytest.mark.abort_on_fail
async def test_sync_credential_action(ops_test: OpsTest):
    """Tests the correct output of actions."""
    s3_integrator_unit = ops_test.model.applications[S3_APP_NAME].units[0]
    action = await s3_integrator_unit.run_action(action_name="get-s3-credentials")
    result = await action.wait()
    assert result.status == "failed"

    access_key = "test-access-key"
    secret_key = "test-secret-key"

    action_result = await fetch_action_sync_s3_credentials(
        s3_integrator_unit, access_key=access_key, secret_key=secret_key
    )

    # test the correct status of the charm
    async with ops_test.fast_forward():
        await ops_test.model.wait_for_idle(apps=[S3_APP_NAME], status="active")

    assert action_result["ok"] == "Credentials successfully updated."

    connection_info = await fetch_action_get_connection_info(s3_integrator_unit)
    assert connection_info["access-key"] == "************"
    assert connection_info["secret-key"] == "************"

    # checks for another update of of the credentials
    updated_secret_key = "new-test-secret-key"
    action_result = await fetch_action_sync_s3_credentials(
        s3_integrator_unit, access_key=access_key, secret_key=updated_secret_key
    )

    async with ops_test.fast_forward():
        await ops_test.model.wait_for_idle(apps=[S3_APP_NAME], status="active")

    # check that secret key has been updated
    assert action_result["ok"] == "Credentials successfully updated."

    connection_info = await fetch_action_get_connection_info(s3_integrator_unit)
    assert connection_info["access-key"] == "************"
    assert connection_info["secret-key"] == "************"


@pytest.mark.group(1)
@pytest.mark.abort_on_fail
async def test_config_options(ops_test: OpsTest):
    """Tests the correct handling of configuration parameters."""
    # test tls-ca-chain
    ca_chain = get_certificate_from_file("tests/ca_chain.pem")
    ca_chain_bytes = base64.b64encode(ca_chain.encode("utf-8"))
    configuration_parameters = {
        "tls-ca-chain": ca_chain_bytes.decode("utf-8"),
        "s3-api-version": "1.0",
        "storage-class": "cinder",
        "attributes": "a1:v1, a2:v2, a3:v3",
        "path": "/test/path_1/",
        "region": "us-east-2",
        "endpoint": "s3.amazonaws.com",
        "experimental-delete-older-than-days": "7",
    }
    # apply new configuration options
    await ops_test.model.applications[S3_APP_NAME].set_config(configuration_parameters)
    # wait for active status
    await ops_test.model.wait_for_idle(apps=[S3_APP_NAME], status="active")
    # test the returns
    s3_integrator_unit = ops_test.model.applications[S3_APP_NAME].units[0]
    action = await s3_integrator_unit.run_action(action_name="get-s3-connection-info")
    action_result = await action.wait()
    configured_options = action_result.results
    # test the correctness of the configuration fields
    assert configured_options["storage-class"] == "cinder"
    assert configured_options["s3-api-version"] == "1.0"
    assert configured_options["delete-older-than-days"] == "7"
    assert len(json.loads(configured_options["attributes"])) == 3
    assert len(json.loads(configured_options["tls-ca-chain"])) == 2
    assert configured_options["region"] == "us-east-2"
    assert configured_options["path"] == "/test/path_1/"
    assert configured_options["endpoint"] == "s3.amazonaws.com"


@pytest.mark.group(1)
@pytest.mark.abort_on_fail
async def test_relation_creation(ops_test: OpsTest):
    """Relate charms and wait for the expected changes in status."""
    await ops_test.model.add_relation(S3_APP_NAME, f"{APPLICATION_APP_NAME}:{FIRST_RELATION}")

    async with ops_test.fast_forward():
        await ops_test.model.block_until(
            lambda: is_relation_joined(ops_test, FIRST_RELATION, FIRST_RELATION) is True
        )

        await ops_test.model.wait_for_idle(apps=APPS, status="active")
    await ops_test.model.wait_for_idle(apps=APPS, status="active")
    # test the content of the relation data bag

    relation_data = await get_relation_data(ops_test, APPLICATION_APP_NAME, FIRST_RELATION)
    application_data = await get_application_data(ops_test, APPLICATION_APP_NAME, FIRST_RELATION)
    # check if the different parameters correspond to expected ones.
    relation_id = relation_data[0]["relation-id"]
    # check correctness for some fields
    assert "access-key" in application_data
    assert "secret-key" in application_data
    assert "bucket" in application_data
    assert application_data["bucket"] == f"relation-{relation_id}"
    assert application_data["access-key"] == "test-access-key"
    assert application_data["secret-key"] == "new-test-secret-key"
    assert application_data["storage-class"] == "cinder"
    assert application_data["s3-api-version"] == "1.0"
    assert application_data["delete-older-than-days"] == "7"
    assert len(json.loads(application_data["attributes"])) == 3
    assert len(json.loads(application_data["tls-ca-chain"])) == 2
    assert application_data["region"] == "us-east-2"
    assert application_data["path"] == "/test/path_1/"

    # update bucket name and check if the change is propagated in the relation databag
    new_bucket_name = "new-bucket-name"
    params = {"bucket": new_bucket_name}
    await ops_test.model.applications[S3_APP_NAME].set_config(params)
    # wait for active status
    await ops_test.model.wait_for_idle(apps=[S3_APP_NAME], status="active")
    application_data = await get_application_data(ops_test, APPLICATION_APP_NAME, FIRST_RELATION)
    # check bucket name
    assert application_data["bucket"] == new_bucket_name

    # check that bucket name set in the requirer application is correct
    await ops_test.model.add_relation(S3_APP_NAME, f"{APPLICATION_APP_NAME}:{SECOND_RELATION}")
    # wait for relation joined
    async with ops_test.fast_forward():
        await ops_test.model.block_until(
            lambda: is_relation_joined(ops_test, SECOND_RELATION, SECOND_RELATION) is True
        )
        await ops_test.model.wait_for_idle(apps=APPS, status="active")

    # read data of the second relation
    application_data = await get_application_data(ops_test, APPLICATION_APP_NAME, SECOND_RELATION)
    assert "access-key" in application_data
    assert "secret-key" in application_data
    assert "bucket" in application_data
    # check correctness of connection parameters in the relation databag
    assert application_data["bucket"] == new_bucket_name
    assert application_data["access-key"] == "test-access-key"
    assert application_data["secret-key"] == "new-test-secret-key"
    assert application_data["storage-class"] == "cinder"
    assert application_data["s3-api-version"] == "1.0"
    assert application_data["delete-older-than-days"] == "7"
    assert len(json.loads(application_data["attributes"])) == 3
    assert len(json.loads(application_data["tls-ca-chain"])) == 2
    assert application_data["region"] == "us-east-2"
    assert application_data["path"] == "/test/path_1/"


@pytest.mark.group(1)
async def test_relation_broken(ops_test: OpsTest):
    """Remove relation and wait for the expected changes in status."""
    # Remove relations
    await ops_test.model.applications[S3_APP_NAME].remove_relation(
        f"{APPLICATION_APP_NAME}:{FIRST_RELATION}", S3_APP_NAME
    )
    await ops_test.model.block_until(
        lambda: is_relation_broken(ops_test, FIRST_RELATION, FIRST_RELATION) is True
    )
    await ops_test.model.applications[S3_APP_NAME].remove_relation(
        f"{APPLICATION_APP_NAME}:{SECOND_RELATION}", S3_APP_NAME
    )
    await ops_test.model.block_until(
        lambda: is_relation_broken(ops_test, SECOND_RELATION, SECOND_RELATION) is True
    )
    # test correct application status
    async with ops_test.fast_forward():
        await asyncio.gather(
            ops_test.model.wait_for_idle(
                apps=[S3_APP_NAME], status="active", raise_on_blocked=True
            ),
            ops_test.model.wait_for_idle(
                apps=[APPLICATION_APP_NAME], status="waiting", raise_on_blocked=True
            ),
        )
===
#!/usr/bin/env python3
# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.

import logging
from typing import Dict, Optional

import yaml
from juju.unit import Unit
from pytest_operator.plugin import OpsTest

logger = logging.getLogger(__name__)


async def fetch_action_get_credentials(unit: Unit) -> Dict:
    """Helper to run an action to fetch credentials.

    Args:
        unit: The juju unit on which to run the get-s3-credentials action for credentials
        action: the
    Returns:
        A dictionary with the server config username and password
    """
    action = await unit.run_action(action_name="get-s3-credentials")
    result = await action.wait()
    return result.results


async def fetch_action_get_connection_info(unit: Unit) -> Dict:
    """Helper to run an action to fetch connection info.

    Args:
        unit: The juju unit on which to run the get_connection_info action for credentials
    Returns:
        A dictionary with the server config username and password
    """
    action = await unit.run_action(action_name="get-s3-connection-info")
    result = await action.wait()
    return result.results


async def fetch_action_sync_s3_credentials(unit: Unit, access_key: str, secret_key: str) -> Dict:
    """Helper to run an action to sync credentials.

    Args:
        unit: The juju unit on which to run the get-password action for credentials
        access_key: the access_key to access the s3 compatible endpoint
        secret_key: the secret key to access the s3 compatible endpoint
    Returns:
        A dictionary with the server config username and password
    """
    parameters = {"access-key": access_key, "secret-key": secret_key}
    action = await unit.run_action(action_name="sync-s3-credentials", **parameters)
    result = await action.wait()

    return result.results


def is_relation_joined(ops_test: OpsTest, endpoint_one: str, endpoint_two: str) -> bool:
    """Check if a relation is joined.

    Args:
        ops_test: The ops test object passed into every test case
        endpoint_one: The first endpoint of the relation
        endpoint_two: The second endpoint of the relation
    """
    for rel in ops_test.model.relations:
        endpoints = [endpoint.name for endpoint in rel.endpoints]
        if endpoint_one in endpoints and endpoint_two in endpoints:
            return True
    return False


def is_relation_broken(ops_test: OpsTest, endpoint_one: str, endpoint_two: str) -> bool:
    """Check if a relation is broken.

    Args:
        ops_test: The ops test object passed into every test case
        endpoint_one: The first endpoint of the relation
        endpoint_two: The second endpoint of the relation
    """
    for rel in ops_test.model.relations:
        endpoints = [endpoint.name for endpoint in rel.endpoints]
        if endpoint_one not in endpoints and endpoint_two not in endpoints:
            return True
    return False


async def run_command_on_unit(unit: Unit, command: str) -> Optional[str]:
    """Run a command in one Juju unit.

    Args:
        unit: the Juju unit instance.
        command: the command to run.

    Returns:
        command execution output or none if the command produces no output.
    """
    # workaround for https://github.com/juju/python-libjuju/issues/707
    action = await unit.run(command)
    result = await action.wait()
    code = str(result.results.get("Code") or result.results.get("return-code"))
    stdout = result.results.get("Stdout") or result.results.get("stdout")
    stderr = result.results.get("Stderr") or result.results.get("stderr")
    assert code == "0", f"{command} failed ({code}): {stderr or stdout}"
    return stdout


async def get_relation_data(
    ops_test: OpsTest,
    application_name: str,
    relation_name: str,
) -> list:
    """Returns a list that contains the relation-data.

    Args:
        ops_test: The ops test framework instance
        application_name: The name of the application
        relation_name: name of the relation to get connection data from
    Returns:
        a list that contains the relation-data
    """
    # get available unit id for the desired application
    units_ids = [
        app_unit.name.split("/")[1]
        for app_unit in ops_test.model.applications[application_name].units
    ]
    assert len(units_ids) > 0
    unit_name = f"{application_name}/{units_ids[0]}"
    raw_data = (await ops_test.juju("show-unit", unit_name))[1]
    if not raw_data:
        raise ValueError(f"no unit info could be grabbed for {unit_name}")
    data = yaml.safe_load(raw_data)
    # Filter the data based on the relation name.
    relation_data = [v for v in data[unit_name]["relation-info"] if v["endpoint"] == relation_name]
    if len(relation_data) == 0:
        raise ValueError(
            f"no relation data could be grabbed on relation with endpoint {relation_name}"
        )

    return relation_data


async def get_application_data(
    ops_test: OpsTest,
    application_name: str,
    relation_name: str,
) -> Dict:
    """Returns the application data bag of a given application and relation.

    Args:
        ops_test: The ops test framework instance
        application_name: The name of the application
        relation_name: name of the relation to get connection data from
    Returns:
        a dictionary that contains the application-data
    """
    relation_data = await get_relation_data(ops_test, application_name, relation_name)
    application_data = relation_data[0]["application-data"]
    return application_data


def get_certificate_from_file(filename: str) -> str:
    """Returns the certificate as a string."""
    with open(filename, "r") as file:
        certificate = file.read()
    return certificate
===
# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.
import subprocess

architecture = subprocess.run(
    ["dpkg", "--print-architecture"], capture_output=True, check=True, encoding="utf-8"
).stdout.strip()
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 21s</sub>

### ✅ `bash`

**Clone wordpress-k8s-operator reference**

$ cd /tmp && git clone --depth=1 https://github.com/canonical/wordpress-k8s-operator /tmp/wordpress-ref 2>&1 | tail -5 && find /tmp/wordpress-ref/tests/integration -type f | sort

<details>
<summary>14 lines</summary>

```
Cloning into '/tmp/wordpress-ref'...
/tmp/wordpress-ref/tests/integration/conftest.py
/tmp/wordpress-ref/tests/integration/helper.py
/tmp/wordpress-ref/tests/integration/pre_run_script.sh
/tmp/wordpress-ref/tests/integration/pre_run_script_juju3.sh
/tmp/wordpress-ref/tests/integration/test_addon.py
/tmp/wordpress-ref/tests/integration/test_core.py
/tmp/wordpress-ref/tests/integration/test_cos_grafana.py
/tmp/wordpress-ref/tests/integration/test_cos_loki.py
/tmp/wordpress-ref/tests/integration/test_cos_prometheus.py
/tmp/wordpress-ref/tests/integration/test_external.py
/tmp/wordpress-ref/tests/integration/test_ingress.py
/tmp/wordpress-ref/tests/integration/test_machine.py
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 26s</sub>

### ✅ `bash`

**View wordpress reference integration tests**

$ cat /tmp/wordpress-ref/tests/integration/conftest.py && echo "===" && head -60 /tmp/wordpress-ref/tests/integration/test_core.py && echo "===" && head -40 /tmp/wordpress-ref/tests/integration/helper.py

<details>
<summary>289 lines</summary>

```
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
===
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
===
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
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 35s</sub>

### ✅ `bash`

**View charmcraft.yaml and metadata.yaml**

$ cat /tmp/s3-integrator-L6-recipe-example-sonnet-4.6/charmcraft.yaml && echo "===" && cat /tmp/s3-integrator-L6-recipe-example-sonnet-4.6/metadata.yaml

<details>
<summary>112 lines</summary>

```
# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.

type: charm
platforms:
  ubuntu@22.04:amd64:
  ubuntu@22.04:arm64:
  ubuntu@22.04:s390x:
# Files implicitly created by charmcraft without a part:
# - dispatch (https://github.com/canonical/charmcraft/pull/1898)
# - manifest.yaml
#   (https://github.com/canonical/charmcraft/blob/9ff19c328e23b50cc06f04e8a5ad4835740badf4/charmcraft/services/package.py#L259)
# Files implicitly copied/"staged" by charmcraft without a part:
# - actions.yaml, config.yaml, metadata.yaml
#   (https://github.com/canonical/charmcraft/blob/9ff19c328e23b50cc06f04e8a5ad4835740badf4/charmcraft/services/package.py#L290-L293
#   https://github.com/canonical/charmcraft/blob/9ff19c328e23b50cc06f04e8a5ad4835740badf4/charmcraft/services/package.py#L156-L157)
parts:
  # "poetry-deps" part name is a magic constant
  # https://github.com/canonical/craft-parts/pull/901
  poetry-deps:
    plugin: nil
    build-packages:
      - curl
    override-build: |
      # Use environment variable instead of `--break-system-packages` to avoid failing on older
      # versions of pip that do not recognize `--break-system-packages`
      # `--user` needed (in addition to `--break-system-packages`) for Ubuntu >=24.04
      PIP_BREAK_SYSTEM_PACKAGES=true python3 -m pip install --user --upgrade pip==26.0.1  # renovate: charmcraft-pip-latest

      # Use uv to install poetry so that a newer version of Python can be installed if needed by poetry
      curl --proto '=https' --tlsv1.2 -LsSf https://github.com/astral-sh/uv/releases/download/0.10.7/uv-installer.sh | sh  # renovate: charmcraft-uv-latest
      # poetry 2.0.0 requires Python >=3.9
      if ! "$HOME/.local/bin/uv" python find '>=3.9'
      then
        # Use first Python version that is >=3.9 and available in an Ubuntu LTS
        # (to reduce the number of Python versions we use)
        "$HOME/.local/bin/uv" python install 3.10.12  # renovate: charmcraft-python-ubuntu-22.04
      fi
      "$HOME/.local/bin/uv" tool install --no-python-downloads --python '>=3.9' poetry==2.3.2 --with poetry-plugin-export==1.10.0  # renovate: charmcraft-poetry-latest

      ln -sf "$HOME/.local/bin/poetry" /usr/local/bin/poetry
  # "charm-poetry" part name is arbitrary; use for consistency
  # Avoid using "charm" part name since that has special meaning to charmcraft
  charm-poetry:
    # By default, the `poetry` plugin creates/stages these directories:
    # - lib, src
    #   (https://github.com/canonical/charmcraft/blob/9ff19c328e23b50cc06f04e8a5ad4835740badf4/charmcraft/parts/plugins/_poetry.py#L76-L78)
    # - venv
    #   (https://github.com/canonical/charmcraft/blob/9ff19c328e23b50cc06f04e8a5ad4835740badf4/charmcraft/parts/plugins/_poetry.py#L95
    #   https://github.com/canonical/craft-parts/blob/afb0d652eb330b6aaad4f40fbd6e5357d358de47/craft_parts/plugins/base.py#L270)
    plugin: poetry
    source: .
    after:
      - poetry-deps
    poetry-export-extra-args: ['--only', 'main,charm-libs']
    build-packages:
      - libffi-dev  # Needed to build Python dependencies with Rust from source
      - libssl-dev  # Needed to build Python dependencies with Rust from source
      - pkg-config  # Needed to build Python dependencies with Rust from source
    override-build: |
      # Workaround for https://github.com/canonical/charmcraft/issues/2068
      # rustup used to install rustc and cargo, which are needed to build Python dependencies with Rust from source
      if [[ "$CRAFT_PLATFORM" == ubuntu@20.04:* || "$CRAFT_PLATFORM" == ubuntu@22.04:* ]]
      then
        snap install rustup --classic
      else
        apt-get install rustup -y
      fi

      # If Ubuntu version < 24.04, rustup was installed from snap instead of from the Ubuntu
      # archive—which means the rustup version could be updated at any time. Print rustup version
      # to build log to make changes to the snap's rustup version easier to track
      rustup --version

      # rpds-py (Python package) >=0.19.0 requires rustc >=1.76, which is not available in the
      # Ubuntu 22.04 archive. Install rustc and cargo using rustup instead of the Ubuntu archive
      rustup set profile minimal
      rustup default 1.93.1  # renovate: charmcraft-rust-latest

      craftctl default
      # Include requirements.txt in *.charm artifact for easier debugging
      cp requirements.txt "$CRAFT_PART_INSTALL/requirements.txt"
  # "files" part name is arbitrary; use for consistency
  files:
    plugin: dump
    source: .
    stage:
      - LICENSE
===
# Copyright 2023 Canonical Ltd.
# See LICENSE file for licensing details.

name: s3-integrator
display-name: S3 Integrator
summary: A provider charm for s3 credentials.
description: |
  S3 Integrator is an integrator charm for providing S3 credentials to
  consumer charms which seek to access shared S3 data. Store the
  credentials centrally in the integrator charm and relate consumer
  charms as needed.

  This charm supports both bare-metal/virtual-machines and K8s.
docs: https://discourse.charmhub.io/t/s3-integrator-documentation/10947
source: https://github.com/canonical/s3-integrator
issues: https://github.com/canonical/s3-integrator/issues
website:
  - https://ubuntu.com/data
  - https://charmhub.io/s3-integrator
  - https://github.com/canonical/s3-integrator
  - https://launchpad.net/~data-platform
  - https://chat.charmhub.io/charmhub/channels/data-platform
maintainers:
  - Data Platform Team <data-platform@lists.launchpad.net>

peers:
  s3-integrator-peers:
    interface: s3-integrator-peers

provides:
  s3-credentials:
    interface: s3
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 3m 14s</sub>

### ✅ `bash`

**Check if unit tests use async**

$ grep -r "async def" /tmp/s3-integrator-L6-recipe-example-sonnet-4.6/tests/unit/ 2>/dev/null | head -5 && echo "---" && ls /tmp/s3-integrator-L6-recipe-example-sonnet-4.6/tests/unit/

```
---
__init__.py  helpers.py  test_charm.py
<exited with exit code 0>
```


---

<sub>⏱️ 3m 14s</sub>

### ✅ `bash`

**Check/install jubilant and pytest-jubilant**

$ pip show jubilant pytest-jubilant 2>/dev/null || pip install jubilant pytest-jubilant 2>&1 | tail -5

<details>
<summary>22 lines</summary>

```
Name: jubilant
Version: 1.7.0
Summary: Juju CLI wrapper, primarily for charm integration testing
Home-page: 
Author: The Charm Tech team at Canonical Ltd.
Author-email: 
License: 
Location: /home/ubuntu/.local/lib/python3.12/site-packages
Requires: PyYAML
Required-by: pytest-jubilant
---
Name: pytest-jubilant
Version: 1.1
Summary: Add your description here
Home-page: 
Author: 
Author-email: 
License: 
Location: /home/ubuntu/.local/lib/python3.12/site-packages
Requires: jubilant, pytest
Required-by:
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 3m 20s</sub>

### ✅ `bash`

**View jubilant Juju.run source**

$ python3 -c "import jubilant; import inspect; print(inspect.getsource(jubilant.Juju.run))"

<details>
<summary>71 lines</summary>

```
def run(
        self,
        unit: str,
        action: str,
        params: Mapping[str, Any] | None = None,
        *,
        wait: float | None = None,
    ) -> Task:
        """Run an action on the given unit and wait for the result.

        Note: this method does not support running an action on multiple units
        at once. If you need that, let us know, and we'll consider adding it
        with a new ``run_multiple`` method or similar.

        Example::

            juju = jubilant.Juju()
            result = juju.run('mysql/0', 'get-password')
            assert result.results['username'] == 'USER0'

        Args:
            unit: Name of unit to run the action on, for example ``mysql/0`` or
                ``mysql/leader``.
            action: Name of action to run.
            params: Named parameters to pass to the action.
            wait: Maximum time to wait for action to finish; :class:`TimeoutError` is raised if
                this is reached. Juju's default is to wait 60 seconds.

        Returns:
            The task created to run the action, including logs, failure message, and so on.

        Raises:
            ValueError: if the action or the unit doesn't exist.
            TaskError: if the action failed.
            TimeoutError: if *wait* was specified and the wait time was reached.
        """
        args = ['run', '--format', 'json', unit, action]
        if wait is not None:
            args.extend(['--wait', f'{wait}s'])

        with (
            tempfile.NamedTemporaryFile('w+', dir=self._temp_dir)
            if params is not None
            else contextlib.nullcontext()
        ) as params_file:
            # params_file is defined when params is not None
            if params_file is not None:
                _yaml.safe_dump(params, params_file)
                params_file.flush()
                args.extend(['--params', params_file.name])
            try:
                stdout, stderr = self._cli(*args)
            except CLIError as exc:
                if 'timed out' in exc.stderr:
                    msg = f'timed out waiting for action, stderr:\n{exc.stderr}'
                    raise TimeoutError(msg) from None
                # With Juju 4, trying to run an action that is not defined gives an error like:
                # ERROR action "not-defined-action" not defined for unit "unit/0". (not found)
                if '(not found)' in exc.stderr:
                    raise ValueError(
                        f'error running action {action!r}, stderr:\n{exc.stderr}'
                    ) from None
                # The "juju run" CLI command fails if the action has an uncaught exception.
                if 'task failed' not in exc.stderr:
                    raise
                stdout = exc.stdout
                stderr = exc.stderr

            # Command doesn't return any stdout if no units exist.
            results: dict[str, Any] = json.loads(stdout) if stdout.strip() else {}
            if not results:
                raise ValueError(f'error running action {action!r}, stderr:\n{stderr}')
            # Don't look up results[unit] directly, because if the caller specifies
            # app/leader it is returned as app/N, for example app/0.
            task_dict = next(iter(results.values()))
            task = Task._from_dict(task_dict)
            task.raise_on_failure()
            return task
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 3m 20s</sub>

### ✅ `bash`

**List jubilant exports**

$ python3 -c "import jubilant; print([x for x in dir(jubilant) if not x.startswith('_')])"

```
['CLIError', 'ConfigValue', 'Juju', 'ModelInfo', 'RevealedSecret', 'Secret', 'SecretURI', 'Status', 'Task', 'TaskError', 'Version', 'WaitError', 'all_active', 'all_agents_idle', 'all_blocked', 'all_error', 'all_maintenance', 'all_waiting', 'any_active', 'any_blocked', 'any_error', 'any_maintenance', 'any_waiting', 'modeltypes', 'secrettypes', 'statustypes', 'temp_model']
<exited with exit code 0>
```


---

<sub>⏱️ 3m 28s</sub>

### ✅ `bash`

**View jubilant Task class**

$ python3 -c "import jubilant; import inspect; print(inspect.getsource(jubilant.Task))"

<details>
<summary>66 lines</summary>

```
@dataclasses.dataclass(frozen=True)
class Task:
    """A task holds the results of Juju running an action or exec command on a single unit."""

    id: str
    """Task ID of the action, for use with ``juju show-task``."""

    status: Literal['aborted', 'cancelled', 'completed', 'error', 'failed']
    """Status of the action (Juju operation). Typically "completed" or "failed"."""

    results: dict[str, Any] = dataclasses.field(default_factory=dict)  # type: ignore
    """Results of the action provided by the charm.

    This excludes the special "return-code", "stdout", and "stderr" keys
    inserted by Juju; those values are provided by separate attributes.
    """

    return_code: int = 0
    """Return code from executing the charm action hook."""

    stdout: str = ''
    """Stdout printed by the action hook."""

    stderr: str = ''
    """Stderr printed by the action hook."""

    message: str = ''
    """Failure message, if the charm provided a message when it failed the action."""

    log: list[str] = dataclasses.field(default_factory=list)  # type: ignore
    """List of messages logged by the action hook."""

    def __str__(self) -> str:
        details: list[str] = []
        if self.results:
            details.append(f'Results: {self.results}')
        if self.stdout:
            details.append(f'Stdout:\n{self.stdout}')
        if self.stderr:
            details.append(f'Stderr:\n{self.stderr}')
        if self.message:
            details.append(f'Message: {self.message}')
        if self.log:
            log_str = '\n'.join(self.log)
            details.append(f'Log:\n{log_str}')
        s = f'Task {self.id}: status {self.status!r}, return code {self.return_code}'
        if details:
            s += ', details:\n' + '\n'.join(details)
        return s

    def __repr__(self) -> str:
        return _pretty.dump(self)

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> Task:
        results: dict[str, Any] = d.get('results') or {}
        return_code = results.pop('return-code', 0)
        stdout = results.pop('stdout', '')
        stderr = results.pop('stderr', '')
        return cls(
            id=d['id'],
            status=d['status'],
            results=results,
            return_code=return_code,
            stdout=stdout,
            stderr=stderr,
            message=d.get('message') or '',
            log=d.get('log') or [],
        )

    @property
    def success(self) -> bool:
        """Whether the action was successful."""
        return self.status == 'completed' and self.return_code == 0

    def raise_on_failure(self):
        """If task was not successful, raise a :class:`TaskError`."""
        if not self.success:
            raise TaskError(self)
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 3m 28s</sub>

### ✅ `bash`

**View jubilant UnitStatus**

$ python3 -c "import jubilant.statustypes as st; import inspect; print(inspect.getsource(st.UnitStatus))"

<details>
<summary>61 lines</summary>

```
@dataclasses.dataclass(frozen=True)
class UnitStatus:
    """Status of a single unit."""

    workload_status: StatusInfo = dataclasses.field(default_factory=StatusInfo)
    juju_status: StatusInfo = dataclasses.field(default_factory=StatusInfo)
    leader: bool = False
    upgrading_from: str = ''
    machine: str = ''
    open_ports: list[str] = dataclasses.field(default_factory=list)  # type: ignore
    public_address: str = ''
    address: str = ''
    provider_id: str = ''
    subordinates: dict[str, UnitStatus] = dataclasses.field(default_factory=dict)  # type: ignore

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> UnitStatus:
        if 'status-error' in d:
            return cls(
                workload_status=StatusInfo(current='failed', message=d['status-error']),
                juju_status=StatusInfo(current='failed', message=d['status-error']),
            )
        return cls(
            workload_status=(
                StatusInfo._from_dict(d['workload-status'])
                if 'workload-status' in d
                else StatusInfo()
            ),
            juju_status=(
                StatusInfo._from_dict(d['juju-status']) if 'juju-status' in d else StatusInfo()
            ),
            leader=d.get('leader') or False,
            upgrading_from=d.get('upgrading-from') or '',
            machine=d.get('machine') or '',
            open_ports=d.get('open-ports') or [],
            public_address=d.get('public-address') or '',
            address=d.get('address') or '',
            provider_id=d.get('provider-id') or '',
            subordinates={
                k: UnitStatus._from_dict(v) for k, v in d.get('subordinates', {}).items()
            },
        )

    @property
    def is_active(self) -> bool:
        """Report whether the workload status for this unit status is "active"."""
        return self.workload_status.current == 'active'

    @property
    def is_blocked(self) -> bool:
        """Report whether the workload status for this unit status is "blocked"."""
        return self.workload_status.current == 'blocked'

    @property
    def is_error(self) -> bool:
        """Report whether the workload status for this unit status is "error"."""
        return self.workload_status.current == 'error'

    @property
    def is_maintenance(self) -> bool:
        """Report whether the workload status for this unit status is "maintenance"."""
        return self.workload_status.current == 'maintenance'

    @property
    def is_waiting(self) -> bool:
        """Report whether the workload status for this unit status is "waiting"."""
        return self.workload_status.current == 'waiting'
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 3m 38s</sub>

### ✅ `bash`

**View jubilant Juju.cli source**

$ python3 -c "import jubilant; import inspect; print(inspect.getsource(jubilant.Juju.cli))" 2>&1 | head -40

<details>
<summary>11 lines</summary>

```
def cli(self, *args: str, include_model: bool = True, stdin: str | None = None) -> str:
        """Run a Juju CLI command and return its standard output.

        Args:
            args: Command-line arguments (excluding ``juju``).
            include_model: If true and :attr:`model` is set, insert the ``--model`` argument
                after the first argument in *args*.
            stdin: Standard input to send to the process, if any.
        """
        stdout, _ = self._cli(*args, include_model=include_model, stdin=stdin)
        return stdout
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 3m 38s</sub>

### ✅ `bash`

**View pytest_jubilant source**

$ python3 -c "import pytest_jubilant; import inspect; print(inspect.getsource(pytest_jubilant))" 2>&1 | head -80

<details>
<summary>7 lines</summary>

```
#!/usr/bin/env python3
# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

"""Welcome to pytest-jubilant!"""

from pytest_jubilant.main import pack, get_resources

__all__ = ["pack", "get_resources"]
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 3m 43s</sub>

### ✅ `bash`

**View pytest_jubilant.main source**

$ python3 -c "import pytest_jubilant.main; import inspect; print(inspect.getsource(pytest_jubilant.main))" 2>&1 | head -100

<details>
<summary>87 lines</summary>

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
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 3m 54s</sub>

### ✅ `bash`

**View jubilant integrate method**

$ python3 -c "import jubilant; import inspect; print(inspect.getsource(jubilant.Juju.integrate))"

<details>
<summary>25 lines</summary>

```
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
        if via:
            if isinstance(via, str):
                args.extend(['--via', via])
            else:
                args.extend(['--via', ','.join(via)])
        self.cli(*args)
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 3m 54s</sub>

### ✅ `bash`

**View jubilant deploy method signature**

$ python3 -c "import jubilant; import inspect; print(inspect.getsource(jubilant.Juju.deploy))" 2>&1 | head -60

<details>
<summary>57 lines</summary>

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
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 4m 2s</sub>

### 💬 Copilot

Now I have all the info needed. Let me implement the migration.

---

<sub>⏱️ 4m 2s</sub>

### ✅ `bash`

**Create state directory**

$ mkdir -p /tmp/s3-integrator-L6-recipe-example-sonnet-4.6/.agent/state

```

<exited with exit code 0>
```


---

<sub>⏱️ 4m 17s</sub>

### ✅ `create`

**/tmp/s3-integrator-L6-recipe-example-sonnet-4.6/.agent/state/jubilant-migration.md**

/tmp/s3-integrator-L6-recipe-example-sonnet-4.6/.agent/state/jubilant-migration.md

```
Created file /tmp/s3-integrator-L6-recipe-example-sonnet-4.6/.agent/state/jubilant-migration.md with 1204 characters
```


---

<sub>⏱️ 4m 17s</sub>

### ✅ `create`

**/tmp/s3-integrator-L6-recipe-example-sonnet-4.6/tests/integration/conftest.py**

/tmp/s3-integrator-L6-recipe-example-sonnet-4.6/tests/integration/conftest.py

```
Created file /tmp/s3-integrator-L6-recipe-example-sonnet-4.6/tests/integration/conftest.py with 663 characters
```


---

<sub>⏱️ 4m 46s</sub>

### 💬 Copilot

Now rewrite helpers.py:

---

<sub>⏱️ 4m 46s</sub>

### ✅ `edit`

**/tmp/s3-integrator-L6-recipe-example-sonnet-4.6/tests/integration/helpers.py**

/tmp/s3-integrator-L6-recipe-example-sonnet-4.6/tests/integration/helpers.py

```
File /tmp/s3-integrator-L6-recipe-example-sonnet-4.6/tests/integration/helpers.py updated with changes.
```


---

<sub>⏱️ 5m 45s</sub>

### 💬 Copilot

Now rewrite the main test file:

---

<sub>⏱️ 5m 45s</sub>

### ✅ `edit`

**/tmp/s3-integrator-L6-recipe-example-sonnet-4.6/tests/integration/test_s3_charm.py**

/tmp/s3-integrator-L6-recipe-example-sonnet-4.6/tests/integration/test_s3_charm.py

```
File /tmp/s3-integrator-L6-recipe-example-sonnet-4.6/tests/integration/test_s3_charm.py updated with changes.
```


---

<sub>⏱️ 5m 56s</sub>

### 💬 Copilot

Now update `pyproject.toml`:

---

<sub>⏱️ 5m 56s</sub>

### ✅ `edit`

**/tmp/s3-integrator-L6-recipe-example-sonnet-4.6/pyproject.toml**

/tmp/s3-integrator-L6-recipe-example-sonnet-4.6/pyproject.toml

```
File /tmp/s3-integrator-L6-recipe-example-sonnet-4.6/pyproject.toml updated with changes.
```


---

<sub>⏱️ 6m 5s</sub>

### 💬 Copilot

Now remove `asyncio_mode = "auto"` and `pytest-asyncio` from unit deps since they're only needed for async tests:

---

<sub>⏱️ 6m 5s</sub>

### ✅ `bash`

**Check if unit tests use async**

$ grep -n "async" /tmp/s3-integrator-L6-recipe-example-sonnet-4.6/tests/unit/test_charm.py | head -5

```
5:from asyncio.log import logger
<exited with exit code 0>
```


---

<sub>⏱️ 6m 11s</sub>

### 💬 Copilot

Good - no async tests in unit tests. Remove asyncio-specific settings:

---

<sub>⏱️ 6m 11s</sub>

### ✅ `edit`

**/tmp/s3-integrator-L6-recipe-example-sonnet-4.6/pyproject.toml**

/tmp/s3-integrator-L6-recipe-example-sonnet-4.6/pyproject.toml

```
File /tmp/s3-integrator-L6-recipe-example-sonnet-4.6/pyproject.toml updated with changes.
```


---

<sub>⏱️ 6m 19s</sub>

### ✅ `edit`

**/tmp/s3-integrator-L6-recipe-example-sonnet-4.6/pyproject.toml**

/tmp/s3-integrator-L6-recipe-example-sonnet-4.6/pyproject.toml

```
File /tmp/s3-integrator-L6-recipe-example-sonnet-4.6/pyproject.toml updated with changes.
```


---

<sub>⏱️ 6m 24s</sub>

### 💬 Copilot

Now run quality checks (format + lint):

---

<sub>⏱️ 6m 25s</sub>

### ✅ `bash`

**Run format quality check**

$ cd /tmp/s3-integrator-L6-recipe-example-sonnet-4.6 && tox -e format 2>&1

<details>
<summary>8 lines</summary>

```
format: venv> /home/ubuntu/.local/share/uv/tools/tox/bin/uv venv -p /home/ubuntu/.local/share/uv/tools/tox/bin/python --allow-existing --python-preference system /tmp/s3-integrator-L6-recipe-example-sonnet-4.6/.tox/format
format: commands_pre[0]> poetry install --only format --no-root
Installing dependencies from lock file

pyproject.toml changed significantly since poetry.lock was last generated. Run `poetry lock` to fix the lock file.
format: exit 1 (0.32 seconds) /tmp/s3-integrator-L6-recipe-example-sonnet-4.6> poetry install --only format --no-root pid=2877
  format: FAIL code 1 (0.35=setup[0.03]+cmd[0.32] seconds)
  evaluation failed :( (0.36 seconds)
<exited with exit code 1>
```

</details>


---

<sub>⏱️ 6m 32s</sub>

### ✅ `bash`

**Update poetry.lock**

$ cd /tmp/s3-integrator-L6-recipe-example-sonnet-4.6 && poetry lock --no-update 2>&1 | tail -5

```
Creating virtualenv non-package-mode-aySOm2B4-py3.12 in /home/ubuntu/.cache/pypoetry/virtualenvs

The option "--no-update" does not exist
<exited with exit code 0>
```


---

<sub>⏱️ 6m 37s</sub>

### ✅ `bash`

**Regenerate poetry.lock**

$ cd /tmp/s3-integrator-L6-recipe-example-sonnet-4.6 && poetry lock 2>&1 | tail -5

```
Resolving dependencies...

Writing lock file
<exited with exit code 0>
```


---

<sub>⏱️ 6m 44s</sub>

### ✅ `bash`

**Run format again**

$ cd /tmp/s3-integrator-L6-recipe-example-sonnet-4.6 && tox -e format 2>&1

<details>
<summary>15 lines</summary>

```
format: commands_pre[0]> poetry install --only format --no-root
Installing dependencies from lock file

Package operations: 1 install, 0 updates, 0 removals

  - Installing ruff (0.15.4): Pending...
  - Installing ruff (0.15.4): Installing...
  - Installing ruff (0.15.4)
format: commands[0]> poetry lock
Resolving dependencies... (0.0s)Resolving dependencies... (0.1s)
format: commands[1]> poetry run ruff check --fix /tmp/s3-integrator-L6-recipe-example-sonnet-4.6/src /tmp/s3-integrator-L6-recipe-example-sonnet-4.6/tests --exclude /tmp/s3-integrator-L6-recipe-example-sonnet-4.6/tests/integration/application-charm/lib/
All checks passed!
format: commands[2]> poetry run ruff format /tmp/s3-integrator-L6-recipe-example-sonnet-4.6/src /tmp/s3-integrator-L6-recipe-example-sonnet-4.6/tests --exclude /tmp/s3-integrator-L6-recipe-example-sonnet-4.6/tests/integration/application-charm/lib/
1 file reformatted, 10 files left unchanged
  format: OK (1.52=setup[0.01]+cmd[0.51,0.50,0.25,0.25] seconds)
  congratulations :) (1.54 seconds)
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 6m 50s</sub>

### 💬 Copilot

Format passed (reformatted 1 file). Now run lint:

---

<sub>⏱️ 6m 52s</sub>

### ✅ `bash`

**Run lint quality check**

$ cd /tmp/s3-integrator-L6-recipe-example-sonnet-4.6 && tox -e lint 2>&1

<details>
<summary>24 lines</summary>

```
lint: venv> /home/ubuntu/.local/share/uv/tools/tox/bin/uv venv -p /home/ubuntu/.local/share/uv/tools/tox/bin/python --allow-existing --python-preference system /tmp/s3-integrator-L6-recipe-example-sonnet-4.6/.tox/lint
lint: commands_pre[0]> poetry install --only lint,format --no-root
Installing dependencies from lock file

Package operations: 2 installs, 0 updates, 0 removals

  - Installing codespell (2.4.1): Pending...
  - Installing ruff (0.15.4): Pending...
  - Installing ruff (0.15.4): Pending...
  - Installing codespell (2.4.1): Installing...
  - Installing ruff (0.15.4): Pending...
  - Installing ruff (0.15.4): Installing...
  - Installing ruff (0.15.4): Installing...
  - Installing codespell (2.4.1)
  - Installing ruff (0.15.4): Installing...
  - Installing ruff (0.15.4)
lint: commands[0]> poetry check --lock
All set!
lint: commands[1]> poetry run codespell /tmp/s3-integrator-L6-recipe-example-sonnet-4.6/src /tmp/s3-integrator-L6-recipe-example-sonnet-4.6/tests
lint: commands[2]> poetry run ruff check /tmp/s3-integrator-L6-recipe-example-sonnet-4.6/src /tmp/s3-integrator-L6-recipe-example-sonnet-4.6/tests --exclude /tmp/s3-integrator-L6-recipe-example-sonnet-4.6/tests/integration/application-charm/lib/
All checks passed!
lint: commands[3]> poetry run ruff format --check --diff /tmp/s3-integrator-L6-recipe-example-sonnet-4.6/src /tmp/s3-integrator-L6-recipe-example-sonnet-4.6/tests --exclude /tmp/s3-integrator-L6-recipe-example-sonnet-4.6/tests/integration/application-charm/lib/
11 files already formatted
  lint: OK (1.62=setup[0.03]+cmd[0.52,0.27,0.30,0.24,0.25] seconds)
  congratulations :) (1.63 seconds)
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 6m 58s</sub>

### 💬 Copilot

Both format and lint pass cleanly. Let me verify the final state of the migrated files:

---

<sub>⏱️ 6m 58s</sub>

### ✅ `bash`

**Show changed files**

$ cd /tmp/s3-integrator-L6-recipe-example-sonnet-4.6 && git diff --stat HEAD 2>/dev/null || git status --short

<details>
<summary>6 lines</summary>

```
poetry.lock                        | 1418 +---------------------------------------------------------------------------
 pyproject.toml                     |    6 +-
 tests/integration/helpers.py       |  147 +++-----
 tests/integration/test_s3_charm.py |  173 ++++------
 4 files changed, 133 insertions(+), 1611 deletions(-)
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 7m 12s</sub>

### ✅ `bash`

**Commit migration changes**

$ cd /tmp/s3-integrator-L6-recipe-example-sonnet-4.6 && git add -A && git commit -m "Migrate integration tests from pytest-operator to jubilant

- Replace pytest-operator/python-libjuju with jubilant + pytest-jubilant
- Convert async tests and helpers to synchronous
- Create tests/integration/conftest.py with charm/app_charm fixtures using pack()
- Replace OpsTest with Juju fixture throughout
- Replace wait_for_idle() with juju.wait() + all_active/all_blocked/all_waiting
- Replace add_relation()/remove_relation() with juju.integrate()/juju.cli()
- Replace set_config() with juju.config()
- Replace action run/wait pattern with juju.run() returning Task
- Replace ops_test.juju('show-unit') with juju.cli('show-unit')
- Remove @pytest.mark.abort_on_fail (use --failfast instead)
- Remove @pytest.mark.skip_if_deployed (no jubilant equivalent)
- Remove is_relation_joined/is_relation_broken helpers (replaced by wait conditions)
- Update pyproject.toml: add jubilant/pytest-jubilant, remove pytest-operator/juju
- Remove pytest-asyncio and asyncio_mode=auto (no more async tests)
- Regenerate poetry.lock

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

<sub>⏱️ 7m 22s</sub>

### ✅ `bash`

**Commit migration changes**

$ cd /tmp/s3-integrator-L6-recipe-example-sonnet-4.6 && git config user.email "copilot@github.com" && git config user.name "Copilot" && git add -A && git commit -m "Migrate integration tests from pytest-operator to jubilant

- Replace pytest-operator/python-libjuju with jubilant + pytest-jubilant
- Convert async tests and helpers to synchronous
- Create tests/integration/conftest.py with charm/app_charm fixtures using pack()
- Replace OpsTest with Juju fixture throughout
- Replace wait_for_idle() with juju.wait() + all_active/all_blocked/all_waiting
- Replace add_relation()/remove_relation() with juju.integrate()/juju.cli()
- Replace set_config() with juju.config()
- Replace action run/wait pattern with juju.run() returning Task
- Replace ops_test.juju('show-unit') with juju.cli('show-unit')
- Remove @pytest.mark.abort_on_fail (use --failfast instead)
- Remove @pytest.mark.skip_if_deployed (no jubilant equivalent)
- Remove is_relation_joined/is_relation_broken helpers (replaced by wait conditions)
- Update pyproject.toml: add jubilant/pytest-jubilant, remove pytest-operator/juju
- Remove pytest-asyncio and asyncio_mode=auto (no more async tests)
- Regenerate poetry.lock

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"

```
[main fbccd22] Migrate integration tests from pytest-operator to jubilant
 6 files changed, 205 insertions(+), 1611 deletions(-)
 create mode 100644 .agent/state/jubilant-migration.md
 create mode 100644 tests/integration/conftest.py
<exited with exit code 0>
```


---

<sub>⏱️ 7m 36s</sub>

### 💬 Copilot

Migration complete. Here's a summary of what was done:

**Files changed:**
- **`tests/integration/conftest.py`** *(new)* — `charm` and `app_charm` session fixtures using `pack()` from pytest-jubilant; supports `CHARM_PATH`/`APP_CHARM_PATH` env overrides
- **`tests/integration/helpers.py`** — Removed `OpsTest`/`Unit` imports; all functions converted sync; now take `(juju: Juju, unit: str, ...)`; `juju.run()` returns `Task` so results accessed via `task.results`; `juju.cli("show-unit", ...)` replaces `ops_test.juju(...)`; removed `is_relation_joined`/`is_relation_broken` (no longer needed)
- **`tests/integration/test_s3_charm.py`** — Fully sync; uses `juju: Juju` fixture; `juju.deploy/integrate/config/wait/cli/run`; `juju.wait()` with `all_active/all_blocked/all_waiting` replaces `wait_for_idle`; `pytest.raises(TaskError)` for expected action failures; `@pytest.mark.setup` replaces `skip_if_deployed`; removed `abort_on_fail` (use `--failfast`)
- **`pyproject.toml`** — Replaced `pytest-operator`+`juju` with `jubilant`+`pytest-jubilant`; removed `pytest-asyncio` and `asyncio_mode = "auto"`

Both `tox -e format` and `tox -e lint` pass cleanly.

---

<sub>Generated by [GitHub Copilot CLI](https://github.com/features/copilot/cli)</sub>
