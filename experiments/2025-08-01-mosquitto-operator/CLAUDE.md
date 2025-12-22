# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

Note that to run `charmcraft` on macOS, you will need to run `uvx charmcraft`.

## Juju, Pebble, and Charms

We are building a *charm* to be deployed on a *Juju* controller. All the information you need about Juju can be found at https://juju.is/docs

Charms can be "machine" or "Kubernetes". Machine charms generally install their workload as Debian packages or as snaps. Kubernetes charms use OCI images (ideally Rocks) that contain the workload, and are run as one or more sidecar containers to the charm container in a Kubernetes pod.

Kubernetes charms interact with the workload containers using Pebble. For Pebble, the most important information is:

* [The layer specification](https://documentation.ubuntu.com/pebble/reference/layer-specification/)
* [The Python API](https://documentation.ubuntu.com/ops/latest/reference/pebble.html#ops-pebble)

Charms are built using Ops. Ops provides the charm with a way to communicate with Juju via environment variables and hook commands. The charm never reads the environment or executes hook commands directly - it always uses the Ops model to do this. Read the Ops API for details: https://documentation.ubuntu.com/ops/latest/reference/ops.html

## Quality Checks

Charm code is always formatted, linted, and statically type checked before committing. Format the code using `tox -e format` and run the linting and type checking using `tox -e lint`. Under the hood, these use `ruff format`, `ruff check` and `pyright`.

Charms always have a comprehensive set of automated tests. These tests are often run locally but also always run in a CI workflow for every PR and merge to main.

Charms have three forms of tests:

* State transition tests, which we refer to as unit tests. These use [ops.testing[(https://documentation.ubuntu.com/ops/latest/reference/ops-testing.html). Each test prepares by creating an `testing.Context` object and a `testing.State` object that describes the Juju state when the event is run, then acts by using `ctx.run` to run an event, then asserts on the output state, which is returned by `ctx.run`.
* Functional tests (machine charms only). These validate the workload interaction code using the real workload but without using Juju.
* Integration tests, which use a real Juju controller. Snap install `concierge` and run `concierge prepare -p dev` to set up a development environment, and use [Jubilant](https://documentation.ubuntu.com/jubilant/reference/jubilant/) to run Juju CLI commands to validate the expected behaviour.

The focus of the tests is ensuring that the *charm* behaves as expected. It is *not* testing the functionality of the workload itself, other than validating that the charm has configured it correctly.

Use `pytest` for tests, and prefer pytest's `monkeypatch` over the standard library `patch` functionality. Use `pytest.mark.parametrize` when appropriate to avoid excessive duplication (a small amount of duplication is healthy). Avoid collecting tests in classes unless there is a clear benefit (think hard before doing that).

We **never** use `ops.testing.Harness` for unit tests, and we **never** use `pytest-operator` or `python-libjuju` (the `juju` module) for integration tests.

Integration tests can be run with `tox -e integration`, but also with `charmcraft test`.

GitHub workflows should be created for:

* CI: Running `tox -e lint`, `tox -e unit`, and `tox -e integration` - prefer `uv` over using `pip` directly.
* Zizmor: to ensure that the workflows are secure. See https://docs.zizmor.sh/usage/

A pre-commit configuration should be added that has the standard pre-commit checks and also `ruff check` and `ruff format check`. Dependabot should be configured to open PRs for security updates.

## Process

To develop a charm:

1. Research the workload. Does it suit a machine charm or a Kubernetes charm? What configuration should the charm set with suitable defaults, and what should it make available to Juju users? What actions make sense for the charm? What other charms should the charm work with (ingress, databases, and so on). Make sure you have read the Juju, Pebble, and Ops documentation mentioned above.
2. Run `charmcraft init --profile=machine` or `charmcraft init --profile=kubernetes`. This will scaffold the local directory with the files needed for the charm.

At this point, you should ultrathink about a plan for the charm. Use the research from the first step and plan what config, actions, storage, resources, secrets, and so on it should use, and how it will scale and interact with other charms. Do *not* start implementing the charm until you have confirmed that the plan is acceptable. You'll want to document this plan in a markdown file so that it can be referred to later.

Continuing:

3. In `src/charm.py` there should be a configuration dataclass and an action dataclass for each action. There will be an existing class that is a `CharmBase` subclass, and this is where you should configure all the event observation.
4. In `src/` there is a workload Python module. This should contain methods that provide interaction with the workload - for machine charms, this will be installing, updating, and removing packages with `apt` or `snap`, and communication with the workload via `subprocess` or an HTTP API. For Kubernetes charms, services are managed via Pebble and interaction with the workload is typically via an HTTP API, but might also involve running processes in the workfload containers with Pebble's `exec`.
5. The first thing to get working is installation (for machine charms) and getting the workload running, often by providing a configuration file.

Always keep the `README.md` and `CONTRIBUTING.md` files updated as changes are made. The `uv.lock` file should be committed to git and regularly updated.

### Extra setup

* Create a `SECURITY.md` file that explains how to report security issues using the GitHub reporting facility.
* Create a `CODE_OF_CONDUCT.md` file based on https://www.contributor-covenant.org/version/1/4/code-of-conduct/
* Create a `TUTORIAL.md` file that provides a basic tutorial for deploying and using the charm.

### Managing changes

* At appropriate intervals commit the changes to the local git repository. Always use conventional commit messages.
* All notable changes must be documented in `CHANGELOG.md`.
* Add new entries under a `[Unreleased]` section as you work.
* Focus on functional changes that affect users.
* Categorise changes using the conventional commit types (feat, fix, refactor, test, and so on).

## Using the charm with Juju

When the charm is ready to test, run `charmcraft pack` to create the `.charm` file. Always run `charmcraft lint` after packing, to verify that there are no problems with the charm.

You can interact with the charm using the Juju CLI. All of the commands are well documented: https://documentation.ubuntu.com/juju/3.6/reference/juju-cli/

For example, to deploy the charm: `juju deploy ./{charm-name}.charm`, to scale up `juju add-unit {charm name}`, to run an action `juju run {charm name}/{unit number} {action name}`, and to see the status `juju status --format=json`.

## General coding advice

* **VERY IMPORTANT**: Never catch `Exception`, and always keep the amount of code in `try`/`except` blocks as small as possible.
* Use absolute paths in subprocesses, and do not execute processes via a shell. Capture `stdout` and `stderr` in the charm and transform it to appropriate logging calls as required.
* Require Python 3.10 or above.
* Use modern type annotations, like `x | y | None` rather than `Optional[Union[x, y]]`. Add `future` imports if required.
* Where possible, make the charm stateless.
* Always include the ``optional`` key when defining relations in `charmcraft.yaml`.
* Always use "import x" rather than "from x import y", *except* for `typing` imports. For example, always `import pathlib` and `pathlib.Path()` rather than `from pathlib import Path` and `Path()`. Other code style guidelines can be found at: https://github.com/canonical/operator/blob/main/STYLE.md
* Outside of the `src/charm.py` file, only use classes when there is a clear benefit. Remember that a module provides most of the benefits of a class, unless multiple instances are required.
* Imports go at the top of modules, never inside of classes or methods.

If you need to run `apt` or `snap` or manage `system`, then you should the charm libs from [operator-libs-linux](https://github.com/canonical/operator-libs-linux/tree/main/lib/charms/operator_libs_linux). Add the dependency to `charmcraft.yaml` like:

```yaml
charm-libs:
  - lib: operator_libs_linux.apt
    version: "0"
  - lib: operator_libs_linux.systemd
    version: "1"
```

And then run `charmcraft fetch-libs`. There will now be a top level `lib` folder that should be added to `PYTHONPATH` in development (in production this happens automatically), that contains the fetched libraries.

**IMPORTANT: Make sure you follow this plan:**

The best development pattern is a "testing sandwich". Start by writing integration tests that clearly show what the behaviour of the charm should be, from the perspective of the Juju user. When the tests are complete -- they will not pass yet -- confirm that this is a good plan. Once confirmed, go ahead and carefully implement the functionality, thinking hard about how to do that. When the implementation is complete, verify that it behaves as expected by checking that the integration tests pass. If they fail, then the problem is *most likely* the implementation, but if it seems like it is not, think harder about it and suggest changes to the tests, but do not implement those until confirmed. Once the tests are passing, go ahead and add unit tests as well, and then verify that those pass. At that point, you can check the functionality off as complete, and start on documentation.
