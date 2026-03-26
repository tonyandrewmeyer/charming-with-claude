# relation-active

## Version
ops 2.10.0

## Type
Feature / behaviour change

## Summary
`Relation.active` property added. Relations in a `broken` or `departing` state are now excluded from `Model.relations` by default. Charms can check `relation.active` to determine whether a relation is still active, and use `Model.relations[name, include_broken=True]` to access departing relations when needed.

## Before
```python
import ops

class MyCharm(ops.CharmBase):
    def _on_relation_broken(self, event: ops.RelationBrokenEvent):
        # Before 2.10.0, the departing relation was still in Model.relations
        remaining = self.model.relations.get("database", [])
        # Had to manually filter out the departing relation
        remaining = [r for r in remaining if r.relation_id != event.relation.relation_id]
        if not remaining:
            self.unit.status = ops.BlockedStatus("No database relation")
```

## After
```python
import ops

class MyCharm(ops.CharmBase):
    def _on_relation_broken(self, event: ops.RelationBrokenEvent):
        # After 2.10.0, the departing relation is automatically excluded
        remaining = self.model.relations.get("database", [])
        # No manual filtering needed
        if not remaining:
            self.unit.status = ops.BlockedStatus("No database relation")
```

## Why Upgrade
- **Correctness**: the most common pattern (counting remaining relations in `relation-broken`) now works correctly without manual filtering.
- **Simpler code**: removes a common boilerplate pattern.
- **Fewer bugs**: the manual filtering pattern was a frequent source of off-by-one style bugs.

## Complexity
Trivial to moderate — trivial if the charm already filters correctly (just remove the filter), moderate if the charm relies on the departing relation being in `Model.relations` (need to add `include_broken=True`).

## Detection
Search for manual relation filtering in `relation-broken` handlers, e.g. patterns like `[r for r in relations if r.relation_id != event.relation.relation_id]` or `[r for r in relations if r != event.relation]`.

## Exemplar Charms
Most charms handling `relation-broken` events can benefit. This was widely adopted.

## Pitfalls
- Charms that *need* access to the departing relation's data during `relation-broken` must use `include_broken=True`.
- This is a behaviour change that could affect charms upgrading from ops < 2.10.0 — the relation count in `relation-broken` handlers changes by one.
- Code that iterates `Model.relations` for a given name and expects to find the departing relation will silently get different results after upgrade.
