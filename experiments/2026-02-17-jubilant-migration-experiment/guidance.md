# Migrating Integration Tests with Copilot: A Practical Guide

This guide tells you how to use GitHub Copilot to migrate your charm's integration tests from `pytest-operator`/`python-libjuju` to `jubilant` and `pytest-jubilant`. It is based on the findings of this experiment — see the [README](README.md) and [results](results.md) for the full data.

## Before You Start

### Prerequisites

- [GitHub Copilot CLI](https://github.com/features/copilot/cli) installed and authenticated
- Your charm repository cloned locally
- The charm's integration tests currently using `pytest-operator` (`from pytest_operator.plugin import OpsTest` and so on)

### What You'll Get

A complete migration of your integration tests, typically including:
- All `async def` / `await` removed
- `OpsTest` fixtures replaced with `jubilant.Juju`
- `ops_test.build_charm()` replaced with `pytest_jubilant.pack()`
- `model.deploy/wait_for_idle/add_relation` replaced with `juju.deploy/wait/integrate`
- Dependencies updated in `pyproject.toml` or `tox.ini`
- Linting and formatting checks passing

### Expected Quality

Using the recommended approach below, our experiments showed:
- **100% of migrations scored 21/25 or higher** (merge-ready with light review)
- **Average score: 24/25**
- **Time: 3–17 minutes** depending on charm complexity (your mileage may vary based on local resources, even though the bulk of the work is in the cloud)
- **2 out of 7 scored a perfect 25/25**

## The Recommended Approach

### Step 1: Navigate to your charm

```bash
cd /path/to/your-charm-operator
```

### Step 2: Run Copilot with the recommended prompt

```bash
copilot -p "Migrate this charm's integration tests from pytest-operator \
(python-libjuju) to jubilant and pytest-jubilant. Update all test files, \
conftest.py, helpers, and dependencies.

Before starting, install jubilant and pytest-jubilant from PyPI \
(pip install jubilant pytest-jubilant) and read the source code to understand \
the API. The key modules are the Juju class, wait helpers (all_active, \
all_blocked, any_error), and the pytest-jubilant fixtures (pack, \
get_resources, juju fixture, temp_model_factory)." \
  --model claude-sonnet-4.6 \
  --allow-all-paths \
  --allow-all-urls
```

**Key points:**
- Use `claude-sonnet-4.6` — it outperformed Opus on this task in every comparison
- The prompt tells the model to install and read the `jubilant` source code before migrating — this is what makes it work well
- `--allow-all-paths` and `--allow-all-urls` let it read files and fetch documentation without confirmation prompts
- You can add `--allow-all-tools` if you want fully autonomous operation, but I recommend staying present to answer any questions
- I didn't do any tests using Copilot on the web, either directly or via GitHub issues, but presumably you'd get the same results

### Step 3: Light supervision

During the run, Copilot may ask you questions like:
- How to handle `@pytest.mark.abort_on_fail` (answer: remove it, use `--failfast` or `-x` when running tests)
- Whether to run quality checks (answer: yes)
- Which tox command to use (answer: whatever your project uses)

Answer these briefly. Don't volunteer corrections — let it work and review afterwards.

### Step 4: Review the output

After Copilot finishes, review the changes:

```bash
git diff
```

**Check these common areas:**

1. **conftest.py** — Does it use the built-in `juju` fixture from pytest-jubilant, or did it create a custom one with `temp_model()`? The built-in fixture is preferred.

2. **Dependencies** — Are both `jubilant` and `pytest-jubilant` added? Are `pytest-operator`, `pytest-asyncio`, and `juju` (python-libjuju) removed?

3. **`juju.wait()` calls** — Check for hallucinated parameters like `successes=3`. The correct signature is `juju.wait(ready, error=None, timeout=None, delay=None)`.

4. **Action calls** — `juju.run(unit, action, params)` should return a `Task` object. Check that results are accessed via `task.results['key']`.

5. **Unnecessary changes** — Did it modify files outside the test directory? Did it remove unrelated dependencies?

### Step 5: Run quality checks

```bash
tox -e fmt
tox -e lint
```

Copilot usually runs these itself, but verify they pass.

### Step 6: Commit and open PR

```bash
git add -A
git commit -m "Migrate integration tests from pytest-operator to jubilant"
```

## Troubleshooting

### Copilot creates a custom `juju` fixture instead of using pytest-jubilant's

This is the most common issue. The fix is simple: delete the custom fixture from `conftest.py`. The `juju` fixture is provided automatically when `pytest-jubilant` is installed.

### Copilot adds `successes=3` to `juju.wait()` calls

This parameter doesn't exist. Remove it. The correct call is:
```python
juju.wait(jubilant.all_active)
# or with error checking:
juju.wait(jubilant.all_active, error=jubilant.any_error)
```

### Copilot creates `.agent/state/` files

Delete these. They're an artefact of the recipe-based approach and shouldn't be committed.

### Copilot doesn't update the lockfile

Run `uv lock`, `poetry lock`, or the equivalent for your project after the migration.

### The migration is incomplete (some files still use OpsTest)

Re-run copilot with a more specific prompt targeting the remaining files:
```bash
copilot -p "Continue migrating the remaining integration test files from \
pytest-operator to jubilant. The files tests/integration/test_foo.py and \
tests/integration/test_bar.py still use OpsTest and async patterns."
```

## Summary

| Setting | Recommended Value |
|---------|-------------------|
| Model | `claude-sonnet-4.6` |
| Prompt | Level 3 (source inspection) — see above |
| Mode | Light supervision (answer questions, don't volunteer corrections) |
| Expected time | 3–17 minutes |
| Expected quality | 21–25 / 25 (merge-ready with light review) |
| Key review areas | conftest.py fixtures, juju.wait() parameters, dependencies |
