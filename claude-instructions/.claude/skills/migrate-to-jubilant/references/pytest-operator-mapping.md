# pytest-operator → Jubilant API Mapping

Complete mapping from `pytest-operator` / `python-libjuju` patterns to `jubilant` / `pytest-jubilant` 2.0.

## Fixtures and Setup

| pytest-operator | jubilant / pytest-jubilant 2.0 | Notes |
|---|---|---|
| `ops_test: OpsTest` (fixture) | `juju: jubilant.Juju` (built-in fixture) | Do not recreate — provided by `pytest-jubilant` |
| `ops_test.model` | `juju` (the Juju instance *is* the model interface) | No separate model object |
| `ops_test.model_full_name` | `juju.model` | Returns `str \| None` |
| `ops_test.tmp_path` | Use `tmp_path` from pytest directly | Standard pytest fixture |
| `@pytest.mark.abort_on_fail` | Remove; use `pytest -x` | CLI-level concern, not a marker |
| `@pytest.mark.skip_if_deployed` | `@pytest.mark.juju_setup` | Skipped with `--no-juju-setup` |
| `@pytest.mark.asyncio` | Remove | Jubilant is synchronous |
| `async def test_...` | `def test_...` | Remove all async/await |

## Building and Deploying

| pytest-operator | jubilant | Notes |
|---|---|---|
| `await ops_test.build_charm(".")` | Pack before tests; pass path via fixture | No build-time equivalent |
| `await ops_test.build_charms("a", "b")` | Pack before tests | No build-time equivalent |
| `await model.deploy(charm, app_name, ...)` | `juju.deploy(charm, app_name, ...)` | Synchronous; use `Path.resolve()` for local charms |
| `await model.deploy(charm, resources={...})` | `juju.deploy(charm, resources={...})` | Same `resources` kwarg |
| `await model.deploy(charm, config={...})` | `juju.deploy(charm, config={...})` | Same `config` kwarg |
| `await model.deploy(charm, num_units=3)` | `juju.deploy(charm, num_units=3)` | Same parameter |
| `await model.deploy(charm, trust=True)` | `juju.deploy(charm, trust=True)` | Same parameter |
| `await model.deploy(charm, channel="edge")` | `juju.deploy(charm, channel="edge")` | Same parameter |
| `ops_test.render_bundle(...)` | Write bundle YAML manually or use `tempfile` | No render helper |
| `ops_test.deploy_bundle(...)` | `juju.deploy(bundle_path)` | Deploy bundle as a path |

## Waiting

| pytest-operator | jubilant | Notes |
|---|---|---|
| `await model.wait_for_idle(apps=["foo"])` | `juju.wait(lambda s: jubilant.all_active(s, "foo"))` | Predicate-based |
| `await model.wait_for_idle(status="active")` | `juju.wait(jubilant.all_active)` | Checks all apps — scope with app names if needed |
| `await model.wait_for_idle(status="blocked")` | `juju.wait(jubilant.all_blocked)` | Or scope: `jubilant.all_blocked(s, "foo")` |
| `await model.wait_for_idle(timeout=600)` | `juju.wait(..., timeout=600)` | Timeout in seconds |
| `await model.wait_for_idle(idle_period=30)` | `juju.wait(..., successes=N)` | `successes` requires N consecutive checks passing (default 3); adjust if needed |
| `await model.wait_for_idle(raise_on_error=False)` | `juju.wait(..., error=None)` | `error=None` is the default — pass `error=jubilant.any_error` to raise on error |
| `await model.block_until(lambda: ...)` | `juju.wait(lambda status: ...)` | Same concept, different signature |

### Status predicate helpers

All accept optional app names to scope the check:

| Function | Checks |
|---|---|
| `jubilant.all_active(status, *apps)` | All units active/idle |
| `jubilant.all_blocked(status, *apps)` | All units blocked |
| `jubilant.all_waiting(status, *apps)` | All units waiting |
| `jubilant.all_maintenance(status, *apps)` | All units in maintenance |
| `jubilant.all_error(status, *apps)` | All units in error |
| `jubilant.any_active(status, *apps)` | At least one unit active |
| `jubilant.any_blocked(status, *apps)` | At least one unit blocked |
| `jubilant.any_error(status, *apps)` | At least one unit in error |
| `jubilant.all_agents_idle(status, *apps)` | All Juju agents idle |

## Relations / Integrations

| pytest-operator | jubilant | Notes |
|---|---|---|
| `await model.add_relation("a:ep", "b:ep")` | `juju.integrate("a:ep", "b:ep")` | `integrate` is the modern Juju term |
| `await model.remove_relation("a:ep", "b:ep")` | `juju.remove_relation("a:ep", "b:ep")` | Same |
| Cross-model: `await model.consume(...)` | `juju.consume(model_and_app, ...)` | |
| Cross-model: `await model.create_offer(...)` | `juju.offer(app, endpoint=...)` | |

## Actions

| pytest-operator | jubilant | Notes |
|---|---|---|
| `action = await unit.run_action("name", **params)` | `task = juju.run("app/0", "name", params)` | Synchronous; returns `Task` |
| `result = await action.wait()` | (returned directly) | No separate wait step |
| `result.results["key"]` | `task.results["key"]` | Same access pattern |
| `result.status` | `task.status` | `"completed"`, `"failed"`, etc. |
| Check for failure | `task.raise_on_failure()` or `pytest.raises(jubilant.TaskError)` | Raises on non-success |

## Configuration

| pytest-operator | jubilant | Notes |
|---|---|---|
| `await app.set_config({"k": "v"})` | `juju.config("app", {"k": "v"})` | |
| `await app.get_config()` | `juju.config("app")` | Returns mapping when no values passed |
| `await app.reset_config(["k"])` | `juju.config("app", reset="k")` | Or `reset=["k1", "k2"]` |

## Status and Model Inspection

| pytest-operator | jubilant | Notes |
|---|---|---|
| `model.applications["foo"]` | `juju.status().apps["foo"]` | Returns `AppStatus` |
| `app.units` | `juju.status().get_units("foo")` | Returns `dict[str, UnitStatus]` |
| `unit.public_address` | `unit_status.address` | From `UnitStatus` |
| `app.status` | `app_status.app_status.current` | `"active"`, `"blocked"`, etc. |
| `unit.workload_status` | `unit_status.workload_status.current` | |
| `unit.workload_status_message` | `unit_status.workload_status.message` | |
| `unit.agent_status` | `unit_status.juju_status.current` | |
| `unit.is_leader_from_status()` | `unit_status.leader` | Boolean |
| `model.machines` | `juju.status().machines` | `dict[str, MachineStatus]` |

## SSH and Exec

| pytest-operator | jubilant | Notes |
|---|---|---|
| `await unit.ssh("command")` | `juju.ssh("app/0", "command")` | |
| `await unit.scp_to(src, dst)` | `juju.scp(src, "app/0:" + dst)` | Source/dest format differs |
| `await unit.scp_from(src, dst)` | `juju.scp("app/0:" + src, dst)` | |
| N/A | `juju.exec("command", unit="app/0")` | Run command on unit via `juju exec` |

## Units

| pytest-operator | jubilant | Notes |
|---|---|---|
| `await app.add_units(count=2)` | `juju.add_unit("app", num_units=2)` | |
| `await app.destroy_units("app/1")` | `juju.remove_unit("app/1")` | |
| `await app.scale(scale=3)` | `juju.add_unit("app", num_units=N)` | Calculate delta yourself |

## Applications

| pytest-operator | jubilant | Notes |
|---|---|---|
| `await model.remove_application("app")` | `juju.remove_application("app")` | |
| `await app.expose()` | `juju.cli("expose", "app", include_model=True)` | No dedicated method |
| `await app.unexpose()` | `juju.cli("unexpose", "app", include_model=True)` | No dedicated method |
| `await app.refresh(path=new_charm)` | `juju.refresh("app", path=new_charm)` | |

## Secrets

| pytest-operator | jubilant | Notes |
|---|---|---|
| N/A (via juju CLI) | `juju.add_secret("name", {"k": "v"})` | Returns `SecretURI` |
| N/A | `juju.show_secret(uri, reveal=True)` | Returns `RevealedSecret` |
| N/A | `juju.grant_secret(uri, "app")` | |
| N/A | `juju.update_secret(uri, {"k": "v2"})` | |
| N/A | `juju.remove_secret(uri)` | |

## Model Management

| pytest-operator | jubilant | Notes |
|---|---|---|
| `ops_test.track_model("alias")` | `juju_factory.get_juju(suffix="alias")` | For multi-model tests |
| `ops_test.forget_model("alias")` | Automatic teardown | `juju_factory` handles cleanup |
| `await ops_test.model_context("alias")` | Use separate `juju` instances | One `Juju` per model |

## CLI Escape Hatch

| pytest-operator | jubilant | Notes |
|---|---|---|
| `await ops_test.juju("cmd", "arg")` | `juju.cli("cmd", "arg")` | Without model context |
| `await ops_test.juju("cmd", "arg")` (model-scoped) | `juju.cli("cmd", "arg", include_model=True)` | With `--model` added |
| `ops_test.run("cmd", "arg")` | `subprocess.run(["cmd", "arg"])` | For non-juju commands |

## Exceptions

| pytest-operator | jubilant | Notes |
|---|---|---|
| Various libjuju exceptions | `jubilant.CLIError` | Raised when a CLI command fails |
| Action failure (check `.status`) | `jubilant.TaskError` | Raised on action/exec failure |
| Timeout (various) | `jubilant.WaitError` | Raised when `wait()` error condition triggers |

## Debug and Logging

| pytest-operator | jubilant | Notes |
|---|---|---|
| `await ops_test.log_model()` | `juju.debug_log(limit=100)` | Returns log string |
| Crash dump (automatic) | `--juju-dump-logs` CLI option | Dumps `juju debug-log` per model |
| `--crash-dump` | `--juju-dump-logs` | Different mechanism |
