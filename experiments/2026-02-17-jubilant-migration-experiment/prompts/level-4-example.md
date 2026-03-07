# Level 4: Prompt + Example Charm Reference

Points the model to an already-migrated charm as a working reference.

## Prompt

```
Migrate this charm's integration tests from pytest-operator (python-libjuju) to jubilant and pytest-jubilant. Update all test files, conftest.py, and dependencies.

For a working example of what jubilant integration tests look like, clone https://github.com/canonical/wordpress-k8s-operator and study its tests/integration/ directory. Pay attention to how conftest.py sets up the juju fixture, how tests use juju.deploy(), juju.wait(), juju.integrate(), and how pytest-jubilant's pack() and get_resources() are used.
```
