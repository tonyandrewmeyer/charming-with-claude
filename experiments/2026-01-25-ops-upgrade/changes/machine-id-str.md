# machine-id-str

## Version
ops 3.4.0

## Type
Breaking change

## Summary
`JujuContext.machine_id` changed from `int` to `str`, fixing a type inconsistency. Juju machine IDs can contain slashes (e.g. `0/lxd/1`) which cannot be represented as integers.

## Before
```python
# machine_id was typed as int (incorrect for Juju's actual format)
machine_id: int = context.machine_id
# Could break on nested containers: "0/lxd/1" is not a valid int
```

## After
```python
# machine_id is now correctly typed as str
machine_id: str = context.machine_id
# Works for all Juju machine ID formats: "0", "0/lxd/1", etc.
```

## Why Upgrade
- Correctness: machine IDs in Juju are strings, not integers. Nested containers produce IDs like `0/lxd/1`.
- Type safety: code that performs string operations on machine IDs no longer needs `str()` conversion.
- This is a breaking change — code that treats `machine_id` as an integer (e.g. arithmetic, int comparisons) will break.

## Complexity
Trivial (but requires attention to type usage)

## Detection
Search for usage of `machine_id` in charm code and tests. Check for:
- Integer comparisons: `if machine_id == 0`
- Arithmetic: `machine_id + 1`
- Type annotations: `machine_id: int`

## Exemplar Charms
Not applicable — this is a type correction, not a new feature.

## Pitfalls
- Most charms don't access `machine_id` directly, so this change is unlikely to affect many charms.
- Only relevant for machine charms that use `JujuContext` (introduced in ops 3.3.0).
- If a charm does use `machine_id`, ensure all comparisons use string values: `if machine_id == "0"` instead of `if machine_id == 0`.
