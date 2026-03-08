# Level 3: Prompt + Source Code Inspection

Instructs the model to install jubilant and read the source code directly.

## Prompt

```
Migrate this charm's integration tests from pytest-operator (python-libjuju) to jubilant and pytest-jubilant. Update all test files, conftest.py, and dependencies.

Before starting, install jubilant and pytest-jubilant from PyPI (`pip install jubilant pytest-jubilant`) and read the source code to understand the API. The key modules are the Juju class, wait helpers (all_active, all_blocked, any_error), and the pytest-jubilant fixtures (pack, get_resources, juju fixture, temp_model_factory).
```
