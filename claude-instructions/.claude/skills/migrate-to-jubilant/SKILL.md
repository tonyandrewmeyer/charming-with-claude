---
name: migrate-to-jubilant
description: >
  Migrate charm integration tests to Jubilant and pytest-jubilant 2.0.
  Handles migration from pytest-operator (python-libjuju) or from
  pytest-jubilant 1.x. Covers async removal, fixture replacement,
  API translation, dependency updates, and verification.
---

# Migrate Integration Tests to Jubilant + pytest-jubilant 2.0

Migrate a charm's integration tests to use [Jubilant](https://documentation.ubuntu.com/jubilant/) and [pytest-jubilant](https://github.com/canonical/pytest-jubilant) 2.0. This skill handles two migration paths:

- **(A) pytest-operator → jubilant 2.0**: Full migration from python-libjuju async patterns
- **(B) pytest-jubilant 1.x → 2.0**: Namespace and API renames only

## When to Use

- Test files import `pytest_operator`, `OpsTest`, or `from juju` (python-libjuju) → path A
- Test files use `pytest-jubilant` <2.0 fixtures (`temp_model_factory`, `--keep-models`, `@pytest.mark.setup`) → path B
- The charm's `pyproject.toml` or `tox.ini` pins `pytest-jubilant<2` or `pytest-operator` → either path

## Before You Start: Read the Source

Install `jubilant` and `pytest-jubilant` and **read the source code** to understand the current API. This step is critical — it consistently produces better migrations than relying on documentation alone.

```bash
uv pip install jubilant pytest-jubilant
```

Then read these modules to understand the API surface:
- `jubilant.Juju` — the main class, with `deploy`, `wait`, `integrate`, `run`, `config`, `status`, `ssh`, `cli`, etc.
- `jubilant` module-level helpers — `all_active`, `all_blocked`, `any_error`, `temp_model`, etc.
- `jubilant.statustypes` — `Status`, `AppStatus`, `UnitStatus` and their attributes
- `jubilant.Task` — returned by `juju.run()` (actions) and `juju.exec()`, with `.results`, `.status`, `.success` (note that `.run()` will call `.raise_on_failure()` itself, so do not assert on `.success`)
- `pytest_jubilant` — the `juju` fixture, `juju_factory` fixture, markers (`juju_setup`, `juju_teardown`)

Do not skip this step. Reading the source prevents hallucinated parameters and ensures you use the correct API signatures.

## Step 1: Survey the Existing Tests

Before editing any files, read all integration test files, `conftest.py`, helper modules, and dependency files. Note:

1. Which migration path applies (A or B)
2. All test files that need changes
3. Custom fixtures and helpers that wrap the old API
4. Dependency declarations in `pyproject.toml`, `tox.ini`, `requirements.txt`
5. CI workflows that reference test dependencies or commands
6. Any existing patterns worth preserving (multi-model, cross-model relations, custom wait conditions)

## Step 2: Migrate

Work through files systematically. For each file, migrate completely before moving to the next.

### Path A: pytest-operator → jubilant 2.0

See [references/pytest-operator-mapping.md](references/pytest-operator-mapping.md) for the complete API mapping table.

Key changes:

1. **Remove all async/await** — Jubilant is synchronous. Remove `async def`, `await`, `@pytest.mark.asyncio`.

2. **Replace the fixture** — Delete any custom `ops_test` / `OpsTest` fixture. The `juju` fixture is provided by `pytest-jubilant` automatically when installed — do not recreate it with `temp_model()`.

   ```python
   # Before
   async def test_deploy(ops_test: OpsTest):
       ...

   # After
   def test_deploy(juju: jubilant.Juju):
       ...
   ```

3. **Replace charm building** — Jubilant does not build charms. The charm should be packed before tests run (via `charmcraft pack` or CI). Pass the `.charm` path to `juju.deploy()`.

   ```python
   # Before
   charm = await ops_test.build_charm(".")
   await ops_test.model.deploy(charm)

   # After — use a fixture or env var for the charm path
   juju.deploy(charm)
   ```

4. **Replace wait patterns** — `model.wait_for_idle()` becomes `juju.wait()` with a predicate.

   ```python
   # Before
   await ops_test.model.wait_for_idle(apps=["foo"], status="active", timeout=600)

   # After
   juju.wait(jubilant.all_active, timeout=600)  # Generally, wait for all apps, but you can specifically wait for "foo" if needed.
   ```

5. **Replace relation/integration calls**:
   ```python
   # Before
   await ops_test.model.add_relation("foo:db", "bar:db")

   # After
   juju.integrate("foo:db", "bar:db")
   ```

6. **Replace action calls**:
   ```python
   # Before
   action = await unit.run_action("backup", **{"target": "/data"})
   result = await action.wait()
   assert result.results["status"] == "success"

   # After
   task = juju.run("foo/0", "backup", {"target": "/data"})
   # The above call will raise if the action is not successful.
   ```

7. **Replace status access**:
   ```python
   # Before
   app = ops_test.model.applications["foo"]
   unit = app.units[0]
   address = await unit.get_public_address()

   # After
   status = juju.status()
   units = status.get_units("foo")
   address = list(units.values())[0].address
   ```

8. **Replace config calls**:
   ```python
   # Before
   await ops_test.model.applications["foo"].set_config({"key": "value"})

   # After
   juju.config("foo", {"key": "value"})
   ```

9. **Replace markers**:
   - `@pytest.mark.abort_on_fail` → remove (use `pytest -x` or `--failfast` at the CLI instead)
   - `@pytest.mark.skip_if_deployed` → `@pytest.mark.juju_setup` (skipped with `--no-juju-setup`)

10. **Update dependencies** — see Step 3.

### Path B: pytest-jubilant 1.x → 2.0

The 2.0 release namespaces all options, fixtures, and markers under `juju_`. See [references/jubilant-1x-to-2x.md](references/jubilant-1x-to-2x.md) for the complete mapping.

Key changes:

1. **Fixture renames**:
   - `temp_model_factory` → `juju_factory`
   - The `juju` fixture name is unchanged

2. **CLI option renames**:
   - `--model` → `--juju-model`
   - `--keep-models` → removed (use `--no-juju-teardown` instead)

3. **Marker renames**:
   - `@pytest.mark.setup` → `@pytest.mark.juju_setup`
   - `@pytest.mark.teardown` → `@pytest.mark.juju_teardown`

4. **Removed helpers**:
   - `pytest_jubilant.pack()` → removed; pack the charm before running tests
   - `pytest_jubilant.get_resources()` → removed; handle resources in your own fixtures

5. **Update dependency pin**: `pytest-jubilant>=2,<3`

## Step 3: Update Dependencies

### pyproject.toml

```toml
[dependency-groups]
integration = [
    "jubilant",
    "pytest>=9,<10",
    "pytest-jubilant>=2,<3",
    # Add any other test deps (requests, etc.)
]
```

Remove: `pytest-operator`, `pytest-asyncio`, `juju` (python-libjuju)

### tox.ini

Update the integration test environment to use the new dependency group. If the project uses `uv`:

```ini
[testenv:integration]
runner = uv-venv-lock-runner
dependency_groups = integration
```

### Lock files

After updating dependencies, regenerate lock files:
- `uv lock` (if using uv)
- `poetry lock` (if using Poetry)

## Step 4: Verify

Run these checks after migrating. Fix any failures before proceeding.

1. **Linting and formatting**:
   ```bash
   tox -e format    # or: make format
   tox -e lint      # or: make lint
   ```

2. **Import check** — verify no remaining imports of old libraries:
   ```bash
   grep -rn "from pytest_operator\|from juju\b\|from juju import\|import juju\b\|OpsTest" tests/
   ```

3. **Integration tests** (if a Juju environment is available):
   ```bash
   tox -e integration
   ```

4. **Review the diff** — ensure changes are minimal and focused. The migration should not refactor test logic, add logging, or restructure files beyond what is needed.

## Gotchas and Common Mistakes

These are the patterns that most frequently cause problems. Pay special attention to them.

1. **Do not recreate the `juju` fixture** — `pytest-jubilant` provides it automatically. If you see `jubilant.temp_model()` in a `conftest.py` fixture called `juju`, delete it. The built-in fixture handles model creation and teardown.

2. **`juju.wait()` signature** — The correct signature is `juju.wait(ready, *, error=None, delay=1.0, timeout=None, successes=3)`. The `ready` argument is a callable that receives a `Status` and returns `bool`. The `successes` parameter requires N consecutive checks to pass (default 3). The `timeout` defaults to the `Juju` instance's `wait_timeout` (180s) when `None`.

3. **`jubilant.all_active` checks ALL apps** — If you only want to check specific apps, pass their names: `jubilant.all_active(status, "foo", "bar")`. Without app names, it checks every app in the model, which fails if a related app is still in "waiting" status.

4. **`juju.run()` raises `TaskError` on failure** — Unlike python-libjuju where you check `result.status`, Jubilant raises `jubilant.TaskError` if the action fails. Use `pytest.raises(jubilant.TaskError)` for expected failures.

5. **`juju.model` is `str | None`** — If you pass `juju.model` to something expecting `str`, you may get type errors. Check for `None` or assert first.

6. **Multi-model testing** — Use the `juju_factory` fixture (not `temp_model_factory`, which was the 1.x name). See the pytest-jubilant README for the pattern.

7. **No `build_charm()` equivalent** — Jubilant does not build charms. Pack the charm before tests run and pass the path via a fixture, environment variable, or CLI argument.

8. **The `--keep-models` flag is gone in 2.0** — Use `--no-juju-teardown` instead. Tests that check for `--keep-models` need updating.

9. **`juju.cli()` for escape hatches** — For Juju operations not covered by the Jubilant API, use `juju.cli("command", "arg1", "arg2")`. Pass `include_model=True` if the command needs `--model`. Recommend to the user that they consider opening a Jubilant feature request for the missing functionality.

## Quality Bar

The migration is complete when:

- [ ] No imports of `pytest_operator`, `juju` (python-libjuju), or `pytest_asyncio` remain in test files
- [ ] No `async def` or `await` in test files (unless used for non-Juju async operations)
- [ ] The `juju` fixture comes from `pytest-jubilant`, not a custom `conftest.py` definition
- [ ] `pyproject.toml` / `tox.ini` pins `pytest-jubilant>=2,<3` and `jubilant`
- [ ] Old dependencies (`pytest-operator`, `juju`, `pytest-asyncio`) are removed
- [ ] Linting passes (`tox -e lint` or equivalent)
- [ ] The diff is minimal — no unnecessary refactoring, added logging, or structural changes
- [ ] Lock files are regenerated if the project uses them
