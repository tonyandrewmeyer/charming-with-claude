# Level 6: Recipe + Example Charm Reference

Combines the detailed recipe with a working example. Maximum assistance level.

## Prompt

The full content of `/home/ubuntu/charmgpt-recipes/integration-testing/commands/migrate-jubilant.md` is provided, with the following addition prepended:

```
Before beginning the migration, clone https://github.com/canonical/wordpress-k8s-operator and study its tests/integration/ directory as a working example of what the final result should look like. Pay attention to how conftest.py sets up the juju fixture, how tests use juju.deploy(), juju.wait(), juju.integrate(), and how pytest-jubilant's pack() and get_resources() are used.

Now proceed with the migration following the recipe below:
```

Followed by the full recipe content.
