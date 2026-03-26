# databag-init-validation

## Version
ops 2.22.0

## Type
Behaviour change

## Summary
Databag access validation is now enforced during `__init__`. Charms that incorrectly read or write relation data during initialisation (before the event context is established) will now get errors earlier, surfacing latent bugs that previously went unnoticed or caused subtle issues.

## Before
```python
import ops

class MyCharm(ops.CharmBase):
    def __init__(self, *args):
        super().__init__(*args)
        # This was silently allowed before 2.22.0 but is incorrect:
        # relation data access during __init__ doesn't have the right
        # Juju context and could return stale or incorrect data
        for rel in self.model.relations.get("database", []):
            data = rel.data[self.app].get("connection-string", "")
            self._cached_connection = data
```

## After
```python
import ops

class MyCharm(ops.CharmBase):
    def __init__(self, *args):
        super().__init__(*args)
        # Move relation data access to event handlers
        self.framework.observe(self.on.config_changed, self._on_config_changed)

    def _on_config_changed(self, event):
        # Access relation data in event handlers where context is established
        for rel in self.model.relations.get("database", []):
            data = rel.data[self.app].get("connection-string", "")
            self._configure_database(data)
```

## Why Upgrade
- **Correctness**: surfacing these errors early prevents subtle bugs from incorrect data access.
- **Predictability**: ensures relation data is only accessed when the Juju context guarantees its consistency.
- **Future-proof**: aligns with ops' direction towards stricter lifecycle enforcement.

## Complexity
Moderate — requires restructuring charm initialisation to move relation data access into event handlers or lazy properties. Can be tricky for charms that cache relation data early.

## Detection
Search for relation data access patterns in `__init__` methods: `rel.data[`, `self.model.relations` followed by data access, or `self.model.get_relation(...).data`.

## Exemplar Charms
This is primarily a fix-up change — exemplars are charms that already follow the correct pattern of accessing relation data only in event handlers.

## Pitfalls
- This may surface latent bugs in existing charms that appeared to work fine — the data access was always incorrect, but it only raises an error now.
- Some charms use `__init__` to build a "current state" snapshot. These need refactoring to build state lazily or in a common handler method.
- The error may appear only with specific relation states (e.g. when a relation exists but the peer data is empty), making it hard to reproduce without the right test scenario.
