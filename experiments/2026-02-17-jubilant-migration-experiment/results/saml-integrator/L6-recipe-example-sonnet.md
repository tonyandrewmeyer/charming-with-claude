# 🤖 Copilot CLI Session

> **Session ID:** `772b73c4-2ba4-4b9a-80bf-81b5a3987af6`
> **Started:** 3/7/2026, 12:41:37 PM
> **Duration:** 6m 19s
> **Exported:** 3/7/2026, 12:47:57 PM

<sub>⏱️ 4s</sub>

### 👤 User

IMPORTANT: You are running in non-interactive mode. For all decision points in the recipe below, use these defaults: (1) abort_on_fail: remove the markers and use --failfast, (2) test execution: skip test execution (we cannot run tests in this environment), (3) tox runner: use 'tox' directly, (4) quality check failures: fix them automatically, (5) at all checkpoints: continue without pausing.

Before beginning the migration, clone https://github.com/canonical/wordpress-k8s-operator and study its tests/integration/ directory as a working example of what the final result should look like. Pay attention to how conftest.py sets up the juju fixture, how tests use juju.deploy(), juju.wait(), juju.integrate(), and how pytest-jubilant's pack() and get_resources() are used.

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

**Explore repo structure and config files**

$ find /tmp/saml-integrator-L6-sonnet -type f | sort && echo "---" && cat /tmp/saml-integrator-L6-sonnet/tox.toml 2>/dev/null || echo "no tox.toml" && cat /tmp/saml-integrator-L6-sonnet/pyproject.toml

<details>
<summary>401 lines</summary>

```
/tmp/saml-integrator-L6-sonnet/.git/HEAD
/tmp/saml-integrator-L6-sonnet/.git/config
/tmp/saml-integrator-L6-sonnet/.git/description
/tmp/saml-integrator-L6-sonnet/.git/hooks/applypatch-msg.sample
/tmp/saml-integrator-L6-sonnet/.git/hooks/commit-msg.sample
/tmp/saml-integrator-L6-sonnet/.git/hooks/fsmonitor-watchman.sample
/tmp/saml-integrator-L6-sonnet/.git/hooks/post-update.sample
/tmp/saml-integrator-L6-sonnet/.git/hooks/pre-applypatch.sample
/tmp/saml-integrator-L6-sonnet/.git/hooks/pre-commit.sample
/tmp/saml-integrator-L6-sonnet/.git/hooks/pre-merge-commit.sample
/tmp/saml-integrator-L6-sonnet/.git/hooks/pre-push.sample
/tmp/saml-integrator-L6-sonnet/.git/hooks/pre-rebase.sample
/tmp/saml-integrator-L6-sonnet/.git/hooks/pre-receive.sample
/tmp/saml-integrator-L6-sonnet/.git/hooks/prepare-commit-msg.sample
/tmp/saml-integrator-L6-sonnet/.git/hooks/push-to-checkout.sample
/tmp/saml-integrator-L6-sonnet/.git/hooks/sendemail-validate.sample
/tmp/saml-integrator-L6-sonnet/.git/hooks/update.sample
/tmp/saml-integrator-L6-sonnet/.git/index
/tmp/saml-integrator-L6-sonnet/.git/info/exclude
/tmp/saml-integrator-L6-sonnet/.git/logs/HEAD
/tmp/saml-integrator-L6-sonnet/.git/logs/refs/heads/main
/tmp/saml-integrator-L6-sonnet/.git/logs/refs/remotes/origin/HEAD
/tmp/saml-integrator-L6-sonnet/.git/objects/pack/pack-e4a6a3cd8c20be131a8ca31c4c0ca38b6ea4b84c.idx
/tmp/saml-integrator-L6-sonnet/.git/objects/pack/pack-e4a6a3cd8c20be131a8ca31c4c0ca38b6ea4b84c.pack
/tmp/saml-integrator-L6-sonnet/.git/objects/pack/pack-e4a6a3cd8c20be131a8ca31c4c0ca38b6ea4b84c.rev
/tmp/saml-integrator-L6-sonnet/.git/packed-refs
/tmp/saml-integrator-L6-sonnet/.git/refs/heads/main
/tmp/saml-integrator-L6-sonnet/.git/refs/remotes/origin/HEAD
/tmp/saml-integrator-L6-sonnet/.github/.jira_sync_config.yaml
/tmp/saml-integrator-L6-sonnet/.github/ISSUE_TEMPLATE/bug_report.yml
/tmp/saml-integrator-L6-sonnet/.github/ISSUE_TEMPLATE/enhancement_proposal.yml
/tmp/saml-integrator-L6-sonnet/.github/pull_request_template.yaml
/tmp/saml-integrator-L6-sonnet/.github/workflows/auto_update_libs.yaml
/tmp/saml-integrator-L6-sonnet/.github/workflows/bot_pr_approval.yaml
/tmp/saml-integrator-L6-sonnet/.github/workflows/comment.yaml
/tmp/saml-integrator-L6-sonnet/.github/workflows/comment_contributing.yaml
/tmp/saml-integrator-L6-sonnet/.github/workflows/docs.yaml
/tmp/saml-integrator-L6-sonnet/.github/workflows/integration_test.yaml
/tmp/saml-integrator-L6-sonnet/.github/workflows/issues.yaml
/tmp/saml-integrator-L6-sonnet/.github/workflows/promote_charm.yaml
/tmp/saml-integrator-L6-sonnet/.github/workflows/publish_charm.yaml
/tmp/saml-integrator-L6-sonnet/.github/workflows/terraform-docs.yaml
/tmp/saml-integrator-L6-sonnet/.github/workflows/test.yaml
/tmp/saml-integrator-L6-sonnet/.gitignore
/tmp/saml-integrator-L6-sonnet/.jujuignore
/tmp/saml-integrator-L6-sonnet/.licenserc.yaml
/tmp/saml-integrator-L6-sonnet/.vale.ini
/tmp/saml-integrator-L6-sonnet/.vale/styles/config/vocabularies/local/accept.txt
/tmp/saml-integrator-L6-sonnet/.woke.yaml
/tmp/saml-integrator-L6-sonnet/CHANGELOG.md
/tmp/saml-integrator-L6-sonnet/CODEOWNERS
/tmp/saml-integrator-L6-sonnet/CONTRIBUTING.md
/tmp/saml-integrator-L6-sonnet/LICENSE
/tmp/saml-integrator-L6-sonnet/Makefile
/tmp/saml-integrator-L6-sonnet/Makefile.docs
/tmp/saml-integrator-L6-sonnet/README.md
/tmp/saml-integrator-L6-sonnet/SECURITY.md
/tmp/saml-integrator-L6-sonnet/charmcraft.yaml
/tmp/saml-integrator-L6-sonnet/config.yaml
/tmp/saml-integrator-L6-sonnet/docs/changelog.md
/tmp/saml-integrator-L6-sonnet/docs/how-to/configure-saml.md
/tmp/saml-integrator-L6-sonnet/docs/how-to/contribute.md
/tmp/saml-integrator-L6-sonnet/docs/how-to/upgrade.md
/tmp/saml-integrator-L6-sonnet/docs/index.md
/tmp/saml-integrator-L6-sonnet/docs/reference/actions.md
/tmp/saml-integrator-L6-sonnet/docs/reference/charm-architecture.md
/tmp/saml-integrator-L6-sonnet/docs/reference/configurations.md
/tmp/saml-integrator-L6-sonnet/docs/reference/integrations.md
/tmp/saml-integrator-L6-sonnet/docs/tutorial/getting-started.md
/tmp/saml-integrator-L6-sonnet/lib/charms/saml_integrator/v0/saml.py
/tmp/saml-integrator-L6-sonnet/metadata.yaml
/tmp/saml-integrator-L6-sonnet/pyproject.toml
/tmp/saml-integrator-L6-sonnet/renovate.json
/tmp/saml-integrator-L6-sonnet/src/charm.py
/tmp/saml-integrator-L6-sonnet/src/charm_state.py
/tmp/saml-integrator-L6-sonnet/src/saml.py
/tmp/saml-integrator-L6-sonnet/terraform/.gitignore
/tmp/saml-integrator-L6-sonnet/terraform/charm/README.md
/tmp/saml-integrator-L6-sonnet/terraform/charm/main.tf
/tmp/saml-integrator-L6-sonnet/terraform/charm/outputs.tf
/tmp/saml-integrator-L6-sonnet/terraform/charm/variables.tf
/tmp/saml-integrator-L6-sonnet/terraform/charm/versions.tf
/tmp/saml-integrator-L6-sonnet/terraform/product/README.md
/tmp/saml-integrator-L6-sonnet/terraform/product/main.tf
/tmp/saml-integrator-L6-sonnet/terraform/product/outputs.tf
/tmp/saml-integrator-L6-sonnet/terraform/product/variables.tf
/tmp/saml-integrator-L6-sonnet/terraform/product/versions.tf
/tmp/saml-integrator-L6-sonnet/tests/__init__.py
/tmp/saml-integrator-L6-sonnet/tests/conftest.py
/tmp/saml-integrator-L6-sonnet/tests/integration/__init__.py
/tmp/saml-integrator-L6-sonnet/tests/integration/any_charm.py
/tmp/saml-integrator-L6-sonnet/tests/integration/conftest.py
/tmp/saml-integrator-L6-sonnet/tests/integration/test_charm.py
/tmp/saml-integrator-L6-sonnet/tests/interface/conftest.py
/tmp/saml-integrator-L6-sonnet/tests/interface/test_saml.py
/tmp/saml-integrator-L6-sonnet/tests/unit/__init__.py
/tmp/saml-integrator-L6-sonnet/tests/unit/files/metadata_default_namespaces.xml
/tmp/saml-integrator-L6-sonnet/tests/unit/files/metadata_signed.xml
/tmp/saml-integrator-L6-sonnet/tests/unit/files/metadata_signed_tampered.xml
/tmp/saml-integrator-L6-sonnet/tests/unit/files/metadata_unsigned.xml
/tmp/saml-integrator-L6-sonnet/tests/unit/files/non_utf8_metadata_unsigned.xml
/tmp/saml-integrator-L6-sonnet/tests/unit/test_charm.py
/tmp/saml-integrator-L6-sonnet/tests/unit/test_charm_state.py
/tmp/saml-integrator-L6-sonnet/tests/unit/test_library_saml.py
/tmp/saml-integrator-L6-sonnet/tests/unit/test_saml.py
/tmp/saml-integrator-L6-sonnet/tox.toml
/tmp/saml-integrator-L6-sonnet/uv.lock
---
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

<sub>⏱️ 15s</sub>

### ✅ `bash`

**Read all integration test files**

$ ls /tmp/saml-integrator-L6-sonnet/tests/integration/ && echo "---" && for f in /tmp/saml-integrator-L6-sonnet/tests/integration/*.py; do echo "=== $f ===" && cat "$f"; done

<details>
<summary>117 lines</summary>

```
__init__.py  any_charm.py  conftest.py	test_charm.py
---
=== /tmp/saml-integrator-L6-sonnet/tests/integration/__init__.py ===
# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.
=== /tmp/saml-integrator-L6-sonnet/tests/integration/any_charm.py ===
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
=== /tmp/saml-integrator-L6-sonnet/tests/integration/conftest.py ===
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
        config={"python-packages": "pydantic>=2.12.5", "src-overwrite": json.dumps(src_overwrite)},
    )
    yield application
=== /tmp/saml-integrator-L6-sonnet/tests/integration/test_charm.py ===
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
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 19s</sub>

### 💬 Copilot

Now let me clone the reference repo and study it:

---

<sub>⏱️ 21s</sub>

### ✅ `bash`

**Clone wordpress-k8s-operator reference repo**

$ cd /tmp && git clone --depth=1 --quiet https://github.com/canonical/wordpress-k8s-operator /tmp/wp-ref 2>&1 | tail -5 && ls /tmp/wp-ref/tests/integration/

```
conftest.py  pre_run_script.sh	      test_addon.py  test_cos_grafana.py  test_cos_prometheus.py  test_ingress.py
helper.py    pre_run_script_juju3.sh  test_core.py   test_cos_loki.py	  test_external.py	  test_machine.py
<exited with exit code 0>
```


---

<sub>⏱️ 26s</sub>

### ✅ `bash`

**Study reference conftest and test file**

$ cat /tmp/wp-ref/tests/integration/conftest.py && echo "===" && cat /tmp/wp-ref/tests/integration/test_core.py | head -80

<details>
<summary>272 lines</summary>

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
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 26s</sub>

### ✅ `bash`

**Study reference pyproject.toml integration deps**

$ cat /tmp/wp-ref/pyproject.toml | grep -A 20 "integration" && echo "===" && cat /tmp/wp-ref/tox.ini 2>/dev/null | head -60

<details>
<summary>53 lines</summary>

```
integration = [
  "allure-pytest>=2.8.18",
  "allure-pytest-collection-report @ git+https://github.com/canonical/data-platform-workflows@v24.0.0#subdirectory=python/pytest_plugins/allure_pytest_collection_report",
  "juju>=2.9,<3",
  "kubernetes",
  "pillow",
  "pytest==9.0.2",
  "pytest-cov",
  "pytest-operator",
  "python-keystoneclient",
  "python-swiftclient",
  "types-pyyaml",
  "types-requests",
  "websockets<17",
]
integration-juju3 = [
  "juju==3.6.1.3",
  "kubernetes",
  "macaroonbakery==1.3.4",
  "pillow",
  "pytest==9.0.2",
  "pytest-cov",
  "pytest-operator",
  "python-keystoneclient",
  "python-swiftclient",
  "types-pyyaml",
  "types-requests",
]

[tool.uv]
package = false
conflicts = [ [ { group = "integration" }, { group = "integration-juju3" }, { group = "lint" } ] ]

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
--
skips = [ "*/integration/helper.py", "*/*test*" ]
===
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 1m 6s</sub>

### ✅ `bash`

**Check charmcraft.yaml and metadata.yaml**

$ cat /tmp/saml-integrator-L6-sonnet/charmcraft.yaml && echo "===" && cat /tmp/saml-integrator-L6-sonnet/metadata.yaml

<details>
<summary>47 lines</summary>

```
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
===
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

<sub>⏱️ 1m 6s</sub>

### ✅ `bash`

**Check jubilant API**

$ pip show jubilant pytest-jubilant 2>/dev/null || pip install jubilant pytest-jubilant --quiet 2>&1 | tail -5 && python -c "import jubilant; help(jubilant.Juju.wait)" 2>/dev/null | head -30

```
bash: pip: command not found
<exited with exit code 0>
```


---

<sub>⏱️ 1m 11s</sub>

### ✅ `bash`

**Install jubilant and check Juju API**

$ python3 -c "import jubilant; help(jubilant.Juju.wait)" 2>/dev/null | head -40 || python3 -m pip install jubilant pytest-jubilant --quiet 2>&1 | tail -3 && python3 -c "import jubilant; help(jubilant.Juju.wait)" 2>/dev/null | head -40

```

<exited with exit code 0>
```


---

<sub>⏱️ 1m 15s</sub>

### ✅ `bash`

**Install jubilant and inspect Juju API**

$ python3 -m pip install jubilant pytest-jubilant --quiet 2>&1 && python3 -c "
import jubilant
import inspect
# Check Juju class methods
for name, obj in inspect.getmembers(jubilant.Juju, predicate=inspect.isfunction):
    sig = inspect.signature(obj)
    print(f'{name}{sig}')
" 2>&1 | head -60

```
/usr/bin/python3: No module named pip
<exited with exit code 1>
```


---

<sub>⏱️ 1m 19s</sub>

### ✅ `bash`

**Try using uv to install jubilant**

$ which uv && uv pip install jubilant pytest-jubilant 2>&1 | tail -5

```
/snap/bin/uv
error: No virtual environment found; run `uv venv` to create an environment, or pass `--system` to install into a non-virtual environment
<exited with exit code 0>
```


---

<sub>⏱️ 1m 23s</sub>

### ✅ `bash`

**Install jubilant system-wide and inspect Juju API**

$ uv pip install --system jubilant pytest-jubilant 2>&1 | tail -5 && python3 -c "
import jubilant
import inspect
for name, obj in inspect.getmembers(jubilant.Juju, predicate=inspect.isfunction):
    sig = inspect.signature(obj)
    print(f'{name}{sig}')
"

<details>
<summary>7 lines</summary>

```
virtual environment for you. Make sure you have pipx installed.

  See /usr/share/doc/python3.12/README.venv for more information.

hint: Virtual environments were not considered due to the `--system` flag
Traceback (most recent call last):
  File "<string>", line 2, in <module>
ModuleNotFoundError: No module named 'jubilant'
<exited with exit code 1>
```

</details>


---

<sub>⏱️ 1m 27s</sub>

### ✅ `bash`

**Install pip and jubilant**

$ apt-get install -y python3-pip 2>&1 | tail -3 && pip3 install jubilant pytest-jubilant 2>&1 | tail -3

```
E: Could not open lock file /var/lib/dpkg/lock-frontend - open (13: Permission denied)
E: Unable to acquire the dpkg frontend lock (/var/lib/dpkg/lock-frontend), are you root?
bash: pip3: command not found
<exited with exit code 0>
```


---

<sub>⏱️ 2m 1s</sub>

### ✅ `bash`

**Create venv and install jubilant to inspect API**

$ cd /tmp && uv venv jubilant-env 2>&1 && /tmp/jubilant-env/bin/pip install jubilant pytest-jubilant 2>&1 | tail -5 && /tmp/jubilant-env/bin/python -c "
import jubilant, inspect
for name, obj in inspect.getmembers(jubilant.Juju, predicate=inspect.isfunction):
    sig = inspect.signature(obj)
    print(f'{name}{sig}')
"

<details>
<summary>5 lines</summary>

```
Using CPython 3.12.3 interpreter at: /usr/bin/python3
Creating virtual environment at: jubilant-env
? A virtual environment already exists at `jubilant-env`. Do you want to replace it? [y/n] › yes

hint: Use the `--clear` flag or set `UV_VENV_CLEAR=1` to skip this prompt
<command with shellId: 12 is still running after 30 seconds. The command is still running. Check the output above - if it looks like the command is waiting for input, use write_bash to provide it. Otherwise, use read_bash to continue waiting for output, or stop_bash to stop it.>
```

</details>


---

<sub>⏱️ 2m 5s</sub>

### ✅ `write_bash`

<details>
<summary>Arguments</summary>

```json
{
  "shellId": "12",
  "input": "y\n",
  "delay": 15
}
```

</details>

<details>
<summary>10 lines</summary>

```
Using CPython 3.12.3 interpreter at: /usr/bin/python3
Creating virtual environment at: jubilant-env
? A virtual environment already exists at `jubilant-env`. Do you want to replace it? [y/n] › yes

hint: Use the `--clear` flag or set `UV_VENV_CLEAR=1` to skip this prompt✔ A virtual environment already exists at `jubilant-env`. Do you want to replace it? · yes
Activate with: source jubilant-env/bin/activate
bash: /tmp/jubilant-env/bin/pip: No such file or directory
Traceback (most recent call last):
  File "<string>", line 2, in <module>
ModuleNotFoundError: No module named 'jubilant'
<command with id: 12 exited with exit code 1>
```

</details>


---

<sub>⏱️ 2m 40s</sub>

### ✅ `bash`

**Create seed venv and install jubilant**

$ cd /tmp && uv venv jubilant-env --seed 2>&1 && /tmp/jubilant-env/bin/pip install jubilant pytest-jubilant 2>&1 | tail -5 && /tmp/jubilant-env/bin/python -c "
import jubilant, inspect
for name, obj in inspect.getmembers(jubilant.Juju, predicate=inspect.isfunction):
    sig = inspect.signature(obj)
    print(f'{name}{sig}')
"

<details>
<summary>5 lines</summary>

```
Using CPython 3.12.3 interpreter at: /usr/bin/python3
Creating virtual environment with seed packages at: jubilant-env
? A virtual environment already exists at `jubilant-env`. Do you want to replace it? [y/n] › yes

hint: Use the `--clear` flag or set `UV_VENV_CLEAR=1` to skip this prompt
<command with shellId: 13 is still running after 30 seconds. The command is still running. Check the output above - if it looks like the command is waiting for input, use write_bash to provide it. Otherwise, use read_bash to continue waiting for output, or stop_bash to stop it.>
```

</details>


---

<sub>⏱️ 2m 48s</sub>

### ✅ `write_bash`

<details>
<summary>Arguments</summary>

```json
{
  "shellId": "13",
  "input": "y\n",
  "delay": 30
}
```

</details>

<details>
<summary>50 lines</summary>

```
Using CPython 3.12.3 interpreter at: /usr/bin/python3
Creating virtual environment with seed packages at: jubilant-env
? A virtual environment already exists at `jubilant-env`. Do you want to replace it? [y/n] › yes

hint: Use the `--clear` flag or set `UV_VENV_CLEAR=1` to skip this prompt✔ A virtual environment already exists at `jubilant-env`. Do you want to replace it? · yes
 + pip==26.0.1
Activate with: source jubilant-env/bin/activate
Downloading pygments-2.19.2-py3-none-any.whl (1.2 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 1.2/1.2 MB 3.2 MB/s  0:00:00
Installing collected packages: PyYAML, pygments, pluggy, packaging, iniconfig, pytest, jubilant, pytest-jubilant

Successfully installed PyYAML-6.0.3 iniconfig-2.3.0 jubilant-1.7.0 packaging-26.0 pluggy-1.6.0 pygments-2.19.2 pytest-9.0.2 pytest-jubilant-1.1
__init__(self, *, model: 'str | None' = None, wait_timeout: 'float' = 180.0, cli_binary: 'str | pathlib.Path | None' = None)
__repr__(self) -> 'str'
_cli(self, *args: 'str', include_model: 'bool' = True, stdin: 'str | None' = None, log: 'bool' = True, timeout: 'float | None' = None) -> 'tuple[str, str]'
_deploy_tempdir(self, charm: 'str | pathlib.Path | None', resources: 'Mapping[str, str] | None') -> 'Generator[tuple[str | None, Mapping[str, str] | None]]'
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
<command with id: 13 exited with exit code 0>
```

</details>


---

<sub>⏱️ 2m 56s</sub>

### 💬 Copilot

Now I have the full API. Let me also check Status and the all_active helpers:

---

<sub>⏱️ 2m 57s</sub>

### ✅ `bash`

**Inspect jubilant Status and helpers**

$ /tmp/jubilant-env/bin/python -c "
import jubilant, inspect
# Check Status class
print('=== Status ===')
for name, obj in inspect.getmembers(jubilant.Status, predicate=lambda x: not callable(x) or isinstance(x, property)):
    if not name.startswith('_'):
        print(f'  {name}')
print('=== module helpers ===')
for name in dir(jubilant):
    if not name.startswith('_'):
        print(f'  {name}')
print('=== AppStatus ===')
for name, obj in inspect.getmembers(jubilant.AppStatus):
    if not name.startswith('_'):
        print(f'  {name}')
"


<details>
<summary>34 lines</summary>

```
=== Status ===
=== module helpers ===
  CLIError
  ConfigValue
  Juju
  ModelInfo
  RevealedSecret
  Secret
  SecretURI
  Status
  Task
  TaskError
  Version
  WaitError
  all_active
  all_agents_idle
  all_blocked
  all_error
  all_maintenance
  all_waiting
  any_active
  any_blocked
  any_error
  any_maintenance
  any_waiting
  modeltypes
  secrettypes
  statustypes
  temp_model
=== AppStatus ===
Traceback (most recent call last):
  File "<string>", line 13, in <module>
AttributeError: module 'jubilant' has no attribute 'AppStatus'. Did you mean: 'Status'?
<exited with exit code 1>
```

</details>


---

<sub>⏱️ 2m 57s</sub>

### ✅ `bash`

**Inspect pytest-jubilant API**

$ /tmp/jubilant-env/bin/python -c "
import pytest_jubilant, inspect
print('=== pytest_jubilant exports ===')
for name in dir(pytest_jubilant):
    if not name.startswith('_'):
        obj = getattr(pytest_jubilant, name)
        try:
            sig = inspect.signature(obj)
            print(f'  {name}{sig}')
        except (ValueError, TypeError):
            print(f'  {name}')
"

```
=== pytest_jubilant exports ===
  get_resources(root: Union[pathlib.Path, str] = './') -> Optional[Dict[str, str]]
  main
  pack(root: Union[pathlib.Path, str] = './', platform: Optional[str] = None) -> pathlib.Path
<exited with exit code 0>
```


---

<sub>⏱️ 3m 4s</sub>

### ✅ `bash`

**Inspect status types fields**

$ /tmp/jubilant-env/bin/python -c "
import jubilant
s = jubilant.statustypes
import inspect
print('=== statustypes module ===')
for name in dir(s):
    if not name.startswith('_'):
        obj = getattr(s, name)
        print(f'  {name}')
        if hasattr(obj, '__dataclass_fields__'):
            for field in obj.__dataclass_fields__:
                print(f'    .{field}')
"

<details>
<summary>171 lines</summary>

```
=== statustypes module ===
  Any
  AppStatus
    .charm
    .charm_origin
    .charm_name
    .charm_rev
    .exposed
    .base
    .charm_channel
    .charm_version
    .charm_profile
    .can_upgrade_to
    .scale
    .provider_id
    .address
    .life
    .app_status
    .relations
    .subordinate_to
    .units
    .version
    .endpoint_bindings
  AppStatusRelation
    .related_app
    .interface
    .scope
  CombinedStorage
    .storage
    .filesystems
    .volumes
  ControllerStatus
    .timestamp
  EntityStatus
    .current
    .message
    .since
  FilesystemAttachment
    .mount_point
    .read_only
    .life
  FilesystemAttachments
    .machines
    .containers
    .units
  FilesystemInfo
    .size
    .provider_id
    .volume
    .storage
    .attachments
    .pool
    .life
    .status
  FormattedBase
    .name
    .channel
  LxdProfileContents
    .config
    .description
    .devices
  MachineStatus
    .juju_status
    .hostname
    .dns_name
    .ip_addresses
    .instance_id
    .display_name
    .machine_status
    .modification_status
    .base
    .network_interfaces
    .containers
    .constraints
    .hardware
    .controller_member_status
    .ha_primary
    .lxd_profiles
  ModelStatus
    .name
    .type
    .controller
    .cloud
    .version
    .region
    .upgrade_available
    .model_status
  NetworkInterface
    .ip_addresses
    .mac_address
    .is_up
    .gateway
    .dns_nameservers
    .space
  OfferStatus
    .app
    .endpoints
    .charm
    .total_connected_count
    .active_connected_count
  RemoteAppStatus
    .url
    .endpoints
    .life
    .app_status
    .relations
  RemoteEndpoint
    .interface
    .role
  Status
    .model
    .machines
    .apps
    .app_endpoints
    .offers
    .storage
    .controller
  StatusInfo
    .current
    .message
    .reason
    .since
    .version
    .life
  StorageAttachments
    .units
  StorageInfo
    .kind
    .status
    .persistent
    .life
    .attachments
  UnitStatus
    .workload_status
    .juju_status
    .leader
    .upgrading_from
    .machine
    .open_ports
    .public_address
    .address
    .provider_id
    .subordinates
  UnitStorageAttachment
    .machine
    .location
    .life
  VolumeAttachment
    .read_only
    .device
    .device_link
    .bus_address
    .life
  VolumeAttachments
    .machines
    .containers
    .units
  VolumeInfo
    .size
    .persistent
    .provider_id
    .storage
    .attachments
    .pool
    .hardware_id
    .wwn
    .life
    .status
  annotations
  dataclasses
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 3m 50s</sub>

### 💬 Copilot

Now I have all I need. Let me set up the state file and proceed with the migration:

---

<sub>⏱️ 3m 50s</sub>

### ✅ `bash`

**Check all_active signature and create state dir**

$ mkdir -p /tmp/saml-integrator-L6-sonnet/.agent/state && /tmp/jubilant-env/bin/python -c "
import jubilant, inspect
# Check all_active signature
print(inspect.signature(jubilant.all_active))
print(inspect.getsource(jubilant.all_active))
"

<details>
<summary>15 lines</summary>

```
(status: 'Status', *apps: 'str') -> 'bool'
def all_active(status: Status, *apps: str) -> bool:
    """Report whether all apps and units in *status* (or in *apps* if provided) are "active".

    Examples::

        # Use the callable directly to wait for all apps in status to be active.
        juju.wait(jubilant.all_active)

        # Use a lambda to wait for all apps specified (blog, mysql) to be active.
        juju.wait(lambda status: jubilant.all_active(status, 'blog', 'mysql'))

    Args:
        status: The status object being tested.
        apps: If provided, only these applications (and their units) are tested. If an app is not
            present in ``status.apps``, returns False.
    """
    return _all_statuses_are('active', status, apps)
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 4m 0s</sub>

### ✅ `sql`

**Create migration todos**

<details>
<summary>Arguments</summary>

```json
{
  "description": "Create migration todos",
  "query": "INSERT INTO todos (id, title, description, status) VALUES\n  ('state-file', 'Create agent state file', 'Create .agent/state/jubilant-migration.md with migration plan', 'pending'),\n  ('conftest', 'Migrate conftest.py', 'Remove pytest-operator/asyncio imports, add jubilant/pytest-jubilant, convert async fixtures to sync, use pack() for charm, use juju.deploy() in app/any_charm fixtures', 'pending'),\n  ('test-charm', 'Migrate test_charm.py', 'Remove @pytest.mark.asyncio and @pytest.mark.abort_on_fail, replace OpsTest with Juju, convert await calls to sync jubilant API', 'pending'),\n  ('pyproject', 'Update pyproject.toml', 'In integration and lint dep groups: remove pytest-asyncio, pytest-operator, juju; add jubilant, pytest-jubilant', 'pending'),\n  ('tox-failfast', 'Add --failfast to tox integration env', 'Since abort_on_fail markers are removed, add --failfast to tox.toml integration command', 'pending'),\n  ('quality-checks', 'Run quality checks (fmt, lint, static)', 'Run tox -e fmt, then lint, then static; fix any failures automatically', 'pending');"
}
```

</details>

```
6 row(s) inserted. Last inserted row ID: 6.
```


---

<sub>⏱️ 4m 15s</sub>

### ✅ `bash`

**Create agent state file**

$ cat > /tmp/saml-integrator-L6-sonnet/.agent/state/jubilant-migration.md << 'EOF'
# Jubilant Migration State

**Started:** 2026-03-06
**Last Updated:** 2026-03-06
**Status:** in_progress

## Quality Check Configuration

- tox.toml found: yes (note: tox.toml, not tox.ini)
- fmt environment: fmt
- lint environment: lint
- static environment: static

## Files to Migrate

- [ ] `tests/integration/conftest.py`
- [ ] `tests/integration/test_charm.py`

## Current Task

Migrating conftest.py

## Progress

### conftest.py
- [ ] Remove pytest-operator/asyncio imports
- [ ] Add jubilant/pytest-jubilant imports
- [ ] Add charm fixture with pack()
- [ ] Convert app fixture to sync using juju.deploy()
- [ ] Convert any_charm fixture to sync using juju.deploy()
- [ ] Remove async from fixtures

### test_charm.py
- [ ] Remove @pytest.mark.asyncio and @pytest.mark.abort_on_fail
- [ ] Remove ops and pytest_operator imports
- [ ] Replace OpsTest with Juju
- [ ] Convert await ops_test.model.wait_for_idle → juju.wait(all_active)
- [ ] Convert await ops_test.model.add_relation → juju.integrate()
- [ ] Convert await app.set_config → juju.config()
- [ ] Update app.units[0].workload_status check to use juju.status()

## Dependencies

- [ ] Update pyproject.toml: add jubilant, pytest-jubilant to integration + lint groups
- [ ] Update pyproject.toml: remove pytest-operator, pytest-asyncio, juju from integration + lint groups
- [ ] Add --failfast to tox.toml integration env (replaces abort_on_fail)

## Quality Checks

- [ ] Run fmt - fix any formatting issues
- [ ] Run lint - fix any linting errors
- [ ] Run static - fix any type errors

## Notes

- abort_on_fail strategy: remove markers + use --failfast (per instructions)
- test execution: skip test execution (per instructions)
- tox runner: use 'tox' directly (per instructions)
- No helpers.py exists in this repo
- Only one test file: test_charm.py with 2 tests
- charm has no OCI resources; charmcraft.yaml has no resources section → get_resources() not needed
- UnitStatus workload check: status.apps[app].units[f"{app}/0"].workload_status.current == "active"
EOF
echo "State file created"

```
State file created
<exited with exit code 0>
```


---

<sub>⏱️ 4m 21s</sub>

### ✅ `sql`

**Mark state-file done, start conftest**

<details>
<summary>Arguments</summary>

```json
{
  "description": "Mark state-file done, start conftest",
  "query": "UPDATE todos SET status = 'done' WHERE id = 'state-file';\nUPDATE todos SET status = 'in_progress' WHERE id = 'conftest';"
}
```

</details>

```
0 row(s) updated.
```


---

<sub>⏱️ 4m 37s</sub>

### 💬 Copilot

Now let me write all the migrated files:

---

<sub>⏱️ 4m 37s</sub>

### ✅ `edit`

**/tmp/saml-integrator-L6-sonnet/tests/integration/conftest.py**

/tmp/saml-integrator-L6-sonnet/tests/integration/conftest.py

```
File /tmp/saml-integrator-L6-sonnet/tests/integration/conftest.py updated with changes.
```


---

<sub>⏱️ 4m 50s</sub>

### ✅ `edit`

**/tmp/saml-integrator-L6-sonnet/tests/integration/test_charm.py**

/tmp/saml-integrator-L6-sonnet/tests/integration/test_charm.py

```
File /tmp/saml-integrator-L6-sonnet/tests/integration/test_charm.py updated with changes.
```


---

<sub>⏱️ 4m 57s</sub>

### 💬 Copilot

Now update `pyproject.toml` — remove `pytest-asyncio`, `pytest-operator`, `juju` and add `jubilant`, `pytest-jubilant` to the `integration` and `lint` groups:

---

<sub>⏱️ 4m 57s</sub>

### ✅ `edit`

**/tmp/saml-integrator-L6-sonnet/pyproject.toml**

/tmp/saml-integrator-L6-sonnet/pyproject.toml

```
File /tmp/saml-integrator-L6-sonnet/pyproject.toml updated with changes.
```


---

<sub>⏱️ 5m 3s</sub>

### ✅ `edit`

**/tmp/saml-integrator-L6-sonnet/pyproject.toml**

/tmp/saml-integrator-L6-sonnet/pyproject.toml

```
File /tmp/saml-integrator-L6-sonnet/pyproject.toml updated with changes.
```


---

<sub>⏱️ 5m 11s</sub>

### 💬 Copilot

Now add `--failfast` to the tox integration env:

---

<sub>⏱️ 5m 11s</sub>

### ✅ `edit`

**/tmp/saml-integrator-L6-sonnet/tox.toml**

/tmp/saml-integrator-L6-sonnet/tox.toml

```
File /tmp/saml-integrator-L6-sonnet/tox.toml updated with changes.
```


---

<sub>⏱️ 5m 15s</sub>

### 💬 Copilot

Now update the uv.lock file to reflect the dependency changes, then run quality checks:

---

<sub>⏱️ 5m 16s</sub>

### ✅ `bash`

**Update uv.lock after dependency changes**

$ cd /tmp/saml-integrator-L6-sonnet && uv lock 2>&1 | tail -10

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

<sub>⏱️ 5m 21s</sub>

### ✅ `bash`

**Run fmt quality check**

$ cd /tmp/saml-integrator-L6-sonnet && tox -e fmt 2>&1 | tail -20

<details>
<summary>11 lines</summary>

```
fmt: venv> /home/ubuntu/.local/share/uv/tools/tox/bin/uv venv -p /home/ubuntu/.local/share/uv/tools/tox/bin/python --allow-existing --python-preference system /tmp/saml-integrator-L6-sonnet/.tox/fmt
fmt: uv-sync> uv sync --locked --python-preference system --no-default-groups --group fmt -p /home/ubuntu/.local/share/uv/tools/tox/bin/python
fmt: commands[0]> ruff check --fix --select I /tmp/saml-integrator-L6-sonnet/src/ /tmp/saml-integrator-L6-sonnet/tests/ /tmp/saml-integrator-L6-sonnet/lib/charms/saml_integrator
warning: Selection `CPY` has no effect because preview is not enabled.
All checks passed!
fmt: commands[1]> ruff format /tmp/saml-integrator-L6-sonnet/src/ /tmp/saml-integrator-L6-sonnet/tests/ /tmp/saml-integrator-L6-sonnet/lib/charms/saml_integrator
warning: Selection `CPY` has no effect because preview is not enabled.
17 files left unchanged
  fmt: OK (0.09=setup[0.08]+cmd[0.01,0.01] seconds)
  congratulations :) (0.11 seconds)
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 5m 30s</sub>

### ✅ `bash`

**Run lint quality check**

$ cd /tmp/saml-integrator-L6-sonnet && tox -e lint 2>&1 | tail -30

<details>
<summary>24 lines</summary>

```
lint: venv> /home/ubuntu/.local/share/uv/tools/tox/bin/uv venv -p /home/ubuntu/.local/share/uv/tools/tox/bin/python --allow-existing --python-preference system /tmp/saml-integrator-L6-sonnet/.tox/lint
lint: uv-sync> uv sync --locked --python-preference system --no-default-groups --group lint -p /home/ubuntu/.local/share/uv/tools/tox/bin/python
lint: commands[0]> codespell /tmp/saml-integrator-L6-sonnet
lint: commands[1]> ruff format --check --diff /tmp/saml-integrator-L6-sonnet/src/ /tmp/saml-integrator-L6-sonnet/tests/ /tmp/saml-integrator-L6-sonnet/lib/charms/saml_integrator
warning: Selection `CPY` has no effect because preview is not enabled.
17 files already formatted
lint: commands[2]> ruff check /tmp/saml-integrator-L6-sonnet/src/ /tmp/saml-integrator-L6-sonnet/tests/ /tmp/saml-integrator-L6-sonnet/lib/charms/saml_integrator
warning: Selection `CPY` has no effect because preview is not enabled.
F401 [*] `pytest` imported but unused
 --> tests/integration/test_charm.py:7:8
  |
5 | """SAML Integrator charm integration tests."""
6 |
7 | import pytest
  |        ^^^^^^
8 | from jubilant import Juju, all_active
  |
help: Remove unused import: `pytest`

Found 1 error.
[*] 1 fixable with the `--fix` option.
lint: exit 1 (0.01 seconds) /tmp/saml-integrator-L6-sonnet> ruff check /tmp/saml-integrator-L6-sonnet/src/ /tmp/saml-integrator-L6-sonnet/tests/ /tmp/saml-integrator-L6-sonnet/lib/charms/saml_integrator pid=11056
  lint: FAIL code 1 (0.18=setup[0.08]+cmd[0.08,0.01,0.01] seconds)
  evaluation failed :( (0.19 seconds)
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 5m 39s</sub>

### 💬 Copilot

Unused `import pytest` in test_charm.py — fix it:

---

<sub>⏱️ 5m 39s</sub>

### ✅ `edit`

**/tmp/saml-integrator-L6-sonnet/tests/integration/test_charm.py**

/tmp/saml-integrator-L6-sonnet/tests/integration/test_charm.py

```
File /tmp/saml-integrator-L6-sonnet/tests/integration/test_charm.py updated with changes.
```


---

<sub>⏱️ 5m 49s</sub>

### ✅ `bash`

**Re-run lint after fix**

$ cd /tmp/saml-integrator-L6-sonnet && tox -e lint 2>&1 | tail -20

<details>
<summary>13 lines</summary>

```
lint: uv-sync> uv sync --locked --python-preference system --no-default-groups --group lint -p /home/ubuntu/.local/share/uv/tools/tox/bin/python
lint: commands[0]> codespell /tmp/saml-integrator-L6-sonnet
lint: commands[1]> ruff format --check --diff /tmp/saml-integrator-L6-sonnet/src/ /tmp/saml-integrator-L6-sonnet/tests/ /tmp/saml-integrator-L6-sonnet/lib/charms/saml_integrator
warning: Selection `CPY` has no effect because preview is not enabled.
17 files already formatted
lint: commands[2]> ruff check /tmp/saml-integrator-L6-sonnet/src/ /tmp/saml-integrator-L6-sonnet/tests/ /tmp/saml-integrator-L6-sonnet/lib/charms/saml_integrator
warning: Selection `CPY` has no effect because preview is not enabled.
All checks passed!
lint: commands[3]> mypy /tmp/saml-integrator-L6-sonnet/src/ /tmp/saml-integrator-L6-sonnet/tests/ /tmp/saml-integrator-L6-sonnet/lib/charms/saml_integrator
Success: no issues found in 17 source files
  lint: OK (3.42=setup[0.02]+cmd[0.09,0.01,0.03,3.27] seconds)
  congratulations :) (3.43 seconds)
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 5m 54s</sub>

### ✅ `bash`

**Run static quality check**

$ cd /tmp/saml-integrator-L6-sonnet && tox -e static 2>&1 | tail -15

<details>
<summary>15 lines</summary>

```
Run metrics:
	Total issues (by severity):
		Undefined: 0
		Low: 0
		Medium: 0
		High: 0
	Total issues (by confidence):
		Undefined: 0
		Low: 0
		Medium: 0
		High: 0
Files skipped (0):
  static: OK (0.31=setup[0.07]+cmd[0.24] seconds)
  congratulations :) (0.33 seconds)
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 5m 58s</sub>

### 💬 Copilot

All quality checks pass. Now commit:

---

<sub>⏱️ 5m 59s</sub>

### ✅ `bash`

**Stage changes and show diff summary**

$ cd /tmp/saml-integrator-L6-sonnet && git config user.email "migration@example.com" && git config user.name "Migration" && git add -A && git --no-pager diff --cached --stat

<details>
<summary>8 lines</summary>

```
.agent/state/jubilant-migration.md |  62 ++++++
 pyproject.toml                     |   9 +-
 tests/integration/conftest.py      |  49 +++--
 tests/integration/test_charm.py    |  55 ++----
 tox.toml                           |   1 +
 uv.lock                            | 825 ++---------------------------------------------------------------------------
 6 files changed, 127 insertions(+), 874 deletions(-)
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 6m 11s</sub>

### ✅ `bash`

**Commit migration changes**

$ cd /tmp/saml-integrator-L6-sonnet && git commit -m "Migrate integration tests from pytest-operator to jubilant + pytest-jubilant

- Replace pytest-operator/pytest-asyncio with jubilant/pytest-jubilant
- Convert async fixtures and tests to synchronous
- Use pack() to build charm in charm fixture
- Use juju.deploy() in app and any_charm fixtures
- Replace OpsTest with Juju, await calls with sync jubilant API:
  - wait_for_idle → juju.wait(lambda s: all_active(s, app), ...)
  - add_relation → juju.integrate()
  - app.set_config → juju.config()
  - app.units[0].workload_status → juju.status().apps[app].units[...].workload_status.current
- Remove @pytest.mark.asyncio and @pytest.mark.abort_on_fail markers
- Add --failfast to tox integration env (replaces abort_on_fail behaviour)
- Update pyproject.toml: remove juju, pytest-asyncio, pytest-operator;
  add jubilant, pytest-jubilant in integration and lint groups

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"

```
[main 23dc523] Migrate integration tests from pytest-operator to jubilant + pytest-jubilant
 6 files changed, 127 insertions(+), 874 deletions(-)
 create mode 100644 .agent/state/jubilant-migration.md
<exited with exit code 0>
```


---

<sub>⏱️ 6m 19s</sub>

### 💬 Copilot

Migration complete. Here's a summary of what was done:

**`tests/integration/conftest.py`**
- Removed `pytest_asyncio`, `pytest_operator.plugin.OpsTest`
- Added `jubilant.Juju`, `pytest_jubilant.pack`
- Added `charm` fixture using `pack()` (or `$CHARM_PATH` env var)
- Converted `app` and `any_charm` from `async` to sync, using `juju.deploy()` and returning app name strings

**`tests/integration/test_charm.py`**
- Removed `ops`, `pytest_operator`, `@pytest.mark.asyncio`, `@pytest.mark.abort_on_fail`
- Replaced `OpsTest` with `Juju`, `app: ops.Application` with `app: str`
- Converted all `await` calls to sync jubilant equivalents: `juju.config()`, `juju.wait(lambda s: all_active(...))`, `juju.integrate()`, `juju.status()`

**`pyproject.toml`** — removed `juju`, `pytest-asyncio`, `pytest-operator`; added `jubilant`, `pytest-jubilant` in both `integration` and `lint` groups

**`tox.toml`** — added `--failfast` to the integration env (replacing `abort_on_fail` marker behaviour)

All three quality checks (`fmt`, `lint`, `static`) pass cleanly.

---

<sub>Generated by [GitHub Copilot CLI](https://github.com/features/copilot/cli)</sub>
