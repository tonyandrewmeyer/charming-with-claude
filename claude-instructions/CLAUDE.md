# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Custom Skills

Before working on tasks, check for relevant skills in `.claude/skills/`. Available skills:
- `charmcraft` — `.claude/skills/charmcraft/SKILL.md` — pack charms, fetch libraries
- `concierge` — `.claude/skills/concierge/SKILL.md` — set up dev and test environments
- `jhack` — `.claude/skills/jhack/SKILL.md` — diagnostic tools for charming
- `juju` — `.claude/skills/juju/SKILL.md` — operate a Juju controller: deploy, configure, integrate, debug
- `migrate-to-jubilant` — `.claude/skills/migrate-to-jubilant/SKILL.md` — tools for migrating charm integration tests from pytest-operator and python-libjuju, or from pytest-jubilant 1.x, to pytest-jubilant 2.0 and Jubilant
- `juju-doctor` — `.claude/skills/juju-doctor/SKILL.md` — validate deployments with probes
- `go-standards` — `.claude/skills/go-standards/SKILL.md` — Canonical Go coding standards
- `cli-standards` — `.claude/skills/cli-standards/SKILL.md` — Canonical CLI design standards
- `code-review` — `.claude/skills/code-review/SKILL.md` — code review guidelines
- `charm-logging` — `.claude/skills/charm-logging/SKILL.md` — charm logging level guidelines
- `charm-development-commands` — `.claude/skills/charm-development-commands/SKILL.md` — standard commands to make available for developing and testing charms
- `charm-docs` — `.claude/skills/charm-docs/SKILL.md` — charm documentation guidelines

Read the appropriate SKILL.md before starting any related work.

## Juju, Pebble, and Charms

We are building a *charm* to be deployed on a *Juju* controller. All the information you need about Juju can be found at https://documentation.ubuntu.com/juju/latest/

Charms can be "machine" or "Kubernetes". Machine charms generally install their workload as Debian packages or as snaps. Kubernetes charms use OCI images (ideally Rocks) that contain the workload, and are run as one or more sidecar containers to the charm container in a Kubernetes pod.

Before scaffolding, classify the charm into one of three shapes, as this drives almost every later decision:

* **12-Factor application** (Flask, Django, FastAPI, Go, Express, Spring Boot): use the matching `paas-charm` Charmcraft profile (`charmcraft init --profile=flask-framework`, and so on). These are always Kubernetes charms — do not ask the user about the substrate. This is the fastest path.
* **Custom application**: a full Ops charm (not `paas-charm`-based), targeting either Kubernetes (Pebble, OCI images) or machine (systemd, apt/snap). Confirm the substrate with the user before scaffolding.
* **Infrastructure software** (databases, caches, message brokers, proxies, monitoring): **search Charmhub first** for any workload with a recognisable name before designing one from scratch, then decide with the user whether to use, fork, or build. These charms carry the most operational logic — peer relations, leader election, and actions for administrative tasks.

Kubernetes charms interact with the workload containers using Pebble. For Pebble, the most important information is:

* [The layer specification](https://documentation.ubuntu.com/pebble/reference/layer-specification/)
* [The Python API](https://documentation.ubuntu.com/ops/latest/reference/pebble.html#ops-pebble)

Charms are built using Ops. Ops provides the charm with a way to communicate with Juju via environment variables and hook commands. The charm never reads the environment or executes hook commands directly - it always uses the Ops model to do this. Read the Ops API for details: https://documentation.ubuntu.com/ops/latest/reference/ops.html

## Quality Checks

Charm code is always formatted, linted, and staticly type checked before commiting. Format the code using `tox -e format` and run the linting and type checking using `tox -e lint`. Under the hood, these use `ruff format`, `ruff check` and `pyright`.

Charms always have a comprehensive set of automated tests. These tests are often run locally but also always run in a CI workflow for every PR and merge to main.

Charms have three forms of tests:

* State transition tests, which we refer to as unit tests. These use [ops.testing](https://documentation.ubuntu.com/ops/latest/reference/ops-testing.html). Each test prepares by creating a `testing.Context` object and a `testing.State` object that describes the Juju state when the event is run, then acts by using `ctx.run` to run an event, then asserts on the output state, which is returned by `ctx.run`. Pass the real charm class to `testing.Context(MyCharm)` and let it read metadata from `charmcraft.yaml` — do not pass `meta=` or `config=` overrides (those are leftovers from older Scenario versions). Compare statuses with `==` (for example `out.unit_status == testing.ActiveStatus()`) rather than `isinstance`, so the status message is checked too. `State` is immutable: to chain a sequence of events, use `dataclasses.replace()` to derive the next state from the previous output rather than mutating in place.
* Functional tests (machine charms only). These validate the workload interaction code using the real workload but without using Juju.
* Integration tests, which use a real Juju controller. Snap install `concierge` and run `sudo concierge prepare -p dev` to set up a development environment, and use [Jubilant](https://documentation.ubuntu.com/jubilant/reference/jubilant/) with `pytest-jubilant` to run Juju CLI commands to validate the expected behaviour. Use the module-scoped `juju` fixture that `pytest-jubilant` provides (it creates a model per test file, tears it down, and dumps debug logs on failure) — do **not** roll your own `juju` fixture. The only fixture you need to write is a `charm` fixture that resolves the packed `.charm` path; call `.resolve()`, since Jubilant rejects relative paths, and deploy the test from the packed `.charm` so the full build is exercised. Wait on the built-in predicates such as `jubilant.all_active` and assert with `status.apps[APP_NAME].is_active`, rather than the older `apps=…, status="active"` forms. Pin `jubilant>=1.8,<2` and `pytest-jubilant>=2,<3` in the integration dependency group of `pyproject.toml`.

The focus of the tests is ensuring that the *charm* behaves as expected. It is *not* testing the functionality of the workload itself, other than validating that the charm has configured it correctly.

Use `pytest` for tests, and prefer pytest's `monkeypatch` over the standard library `patch` functionality. Use `pytest.mark.parametrize` when appropriate to avoid excessive duplication (a small amount of duplication is healthy). Avoid collecting tests in classes unless there is a clear benefit (think hard before doing that). Run unit tests under `coverage` with `fail_under = 80` configured in `pyproject.toml`, and do not let coverage drop as the charm grows.

We **never** use `ops.testing.Harness` for unit tests, and we **never** use `pytest-operator` or `python-libjuju` (the `juju` module) for integration tests.

Integration tests can be run with `tox -e integration`, but also with `charmcraft test`.

GitHub workflows should be created for:

* CI: Running `tox -e lint`, `tox -e unit`, and `tox -e integration` - prefer `uv` over using `pip` directly.
* Zizmor: to ensure that the workflows are secure. See https://docs.zizmor.sh/usage/

A pre-commit configuration should be added that has the standard pre-commit checks and also `ruff check` and `ruff format check`. Dependabot should be configured to open PRs for security updates.

All tool usage, whether in GitHub actions, pre-commit, or tox, should use the tool versions declared in `pyproject.toml` and locked (including hashes) in the lock file (for example `uv.lock`), and these environments should install from the lock file to guarantee consistent tool versions everywhere.

## Process

To develop a charm:

1. Research the workload. Does it suit a machine charm or a Kubernetes charm? What configuration should the charm set with suitable defaults, and what should it make available to Juju users? What actions make sense for the charm? What other charms should the charm work with (ingress, databases, and so on). Make sure you have read the Juju, Pebble, and Ops documentation mentioned above.
2. Run `charmcraft init --profile=machine --force` or `charmcraft init --profile=kubernetes --force`. This will scaffold the local directory with the files needed for the charm.

At this point, you should plan the charm. Use the research from the first step and plan what config, actions, storage, resources, secrets, and so on it should use, and how it will scale and interact with other charms. Capture your workload research in a `WORKLOAD.md` (purpose, dependencies, configuration, networking, storage, health endpoints, scaling, backup, and security surface) and the proposed charm shape in a `DESIGN.md` (substrate, charm path, Charmhub recommendation, integrations, config options, actions, scaling, and operational patterns). Do *not* start implementing the charm until the user has confirmed that the design is acceptable.

Continuing:

3. In `src/charm.py` there should be a configuration dataclass and an action dataclass for each action. There will be an existing class that is a `CharmBase` subclass, and this is where you should configure all the event observation.
4. In `src/` there is a workload Python module. This should contain methods that provide interaction with the workload - for machine charms, this will be installing, updating, and removing packages with `apt` or `snap`, and communication with the workload via `subprocess` or an HTTP API. For Kubernetes charms, services are managed via Pebble and interaction with the workload is typically via an HTTP API, but might also involve running processes in the workfload containers with Pebble's `exec`.
5. The first thing to get working is installation (for machine charms) and getting the workload running, often by providing a configuration file.

Always keep the `README.md` and `CONTRIBUTING.md` files updated as changes are made. The `uv.lock` file should be committed to git and regularly updated. You should have a `.gitignore` file that includes `.claude/settings.local.json`.

### Extra setup

* Create a `SECURITY.md` file that explains how to report security issues using the GitHub reporting facility.
* Create a `TUTORIAL.md` file that provides a basic tutorial for deploying and using the charm.

### Day-2 operations

Once the charm installs and runs, plan for operating the workload in production. Research and, where appropriate, implement: backup and restore, scaling (and clustering or high availability where the workload supports it), upgrades, disaster recovery, and security hardening. The user's operational knowledge is the most valuable input here; fall back to web research and upstream documentation when they cannot answer.

### Managing changes

* At appropriate intervals commit the changes to the local git repository. Always use conventional commit messages.
* All notable changes must be documented in `CHANGELOG.md`.
* Add new entries under a `[Unreleased]` section as you work.
* Focus on functional changes that affect users.
* Categorise changes using the conventional commit types (feat, fix, refactor, test, and so on).

## Using the charm with Juju

When the charm is ready to test, run `charmcraft pack` to create the `.charm` file. Always run `charmcraft analyse` after packing, to verify that there are no problems with the charm.

You can interact with the charm using the Juju CLI. All of the commands are well documented: https://documentation.ubuntu.com/juju/3.6/reference/juju-cli/

For example, to deploy the charm: `juju deploy ./{charm-name}.charm`, to scale up `juju add-unit {charm name}`, to run an action `juju run {charm name}/{unit number} {action name}`, and to see the status `juju status --format=json`.

Juju bundles are deprecated — do not author new `bundle.yaml` files. For multi-charm deployments, issue a sequence of `juju deploy` and `juju integrate` commands, or ship a Terraform module that uses the Juju Terraform provider.

## Observability

Every production charm should integrate with the Canonical Observability Stack (COS) and emit traces. Wire these up by default rather than as an afterthought.

* **Tracing**: always add `ops-tracing` (from PyPI). Declare a `tracing` relation in `charmcraft.yaml` (`interface: tracing`, `limit: 1`) and construct the tracer in `__init__` after `super().__init__`: `self._tracing = ops_tracing.Tracing(self, "tracing")`, where the second argument matches the relation name. Do **not** call `ops_tracing.setup(self)` — that shorthand has been removed and raises `AttributeError` at charm import. ops-tracing already instruments every hook execution, Pebble call, relation data access, status change, and secret operation, so only add manual spans for long-running workload operations, external API calls, or fallback decision logic.
* **Metrics**: provide a `metrics-endpoint` relation (`interface: prometheus_scrape`) and ship Prometheus alert rules under `src/prometheus_alert_rules/`.
* **Logs**: require a `logging` relation (`interface: loki_push_api`) and forward workload logs to Loki.
* **Dashboards**: provide a `grafana-dashboard` relation and place dashboard JSON under `src/grafana_dashboards/`.

Keep COS in a separate Juju model from the charm and integrate across the model boundary. When debugging, ground every fix in observability data — start with `juju debug-log`, then query traces (Tempo) and logs (Loki) — rather than guessing.

## General coding advice

* **VERY IMPORTANT**: Never catch `Exception`, and always keep the amount of code in `try`/`except` blocks as small as possible.
* Use absolute paths in subprocesses, and do not execute processes via a shell. Capture `stdout` and `stderr` in the charm and transform it to appropriate logging calls as required.
* Require Python 3.10 or above.
* Use modern type annotations, like `x | y | None` rather than `Optional[Union[x, y]]`. Add `future` imports if required.
* Where possible, make the charm stateless.
* Always include the `optional` key when defining `requires` relations in `charmcraft.yaml`. Always include `additionalProperties: false` in action definitions, and list mandatory parameters under `required:`.
* Declare an `assumes:` block in `charmcraft.yaml`: `juju >= 3.6` for every charm, plus `k8s-api` for Kubernetes charms, so deployment fails fast on incompatible controllers.
* Manage charm dependencies in `pyproject.toml` (the Charmcraft 4.2+ `kubernetes` and `machine` profiles scaffold a `uv`-based layout); `requirements.txt` is no longer the recommended format.
* Minimise dependencies: prefer the standard library, and justify every third-party dependency in the design document. Avoid native or binary dependencies unless the workload genuinely requires them, as they enlarge the attack surface and complicate reproducibility.
* Never pass secrets as command-line arguments — `ps`, audit logs, and process lists capture them. Use Juju secrets, environment variables, or a config file the workload reads directly. Native binaries declared in charm metadata (resources, extra-bins) should carry checksums so packing fails if the upstream artefact is tampered with.
* Always use "import x" rather than "from x import y", *except* for `typing` imports. For example, always `import pathlib` and `pathlib.Path()` rather than `from pathlib import Path` and `Path()`. Other code style guidelines can be found at: https://github.com/canonical/operator/blob/main/STYLE.md
* Outside of the `src/charm.py` file, only use classes when there is a clear benefit. Remember that a module provides most of the benefits of a class, unless multiple instances are required.
* Imports go at the top of modules, never inside of classes or methods.
* Use Google-style docstrings. Comments explain *why*, not *what*; they are rare and are full sentences ending with punctuation.
* Always use British English for comments and documentation, not American English. If possible, rephrase to avoid using words that are spelt differently in American English.

Prefer charm libraries published to PyPI in the `charmlibs-*` namespace over `charmcraft fetch-libs`: they are versioned, hash-pinnable, and need no fetch step. The import path becomes `from charmlibs import apt` (or `from charmlibs.interfaces import ...`). In particular, `charmlibs-apt`, `charmlibs-snap`, `charmlibs-systemd`, `charmlibs-sysctl`, `charmlibs-passwd`, and `charmlibs-pathops` replace the corresponding `charms.operator_libs_linux.*` submodules — use these when you need to run `apt`, `snap`, manage `systemd`, or do pathlib-style file operations against a workload container. `cosl` (COS topology labels and the Loki logging handler) is also on PyPI. Some libraries are still Charmhub-only and must be fetched with `charmcraft fetch-libs` — notably the observability charm libraries (`charms.loki_k8s.*`, `charms.grafana_k8s.*`, `charms.prometheus_k8s.*`, `charms.tempo_*`, `charms.catalogue_k8s.*`, `charms.observability_libs.*`), `charms.traefik_k8s.*`, and `charms.data_platform_libs.*`.
