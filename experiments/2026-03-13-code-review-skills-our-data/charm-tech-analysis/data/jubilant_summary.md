# Jubilant Bug-Fix Classification Summary

**Total commits analyzed:** 23 (18 jubilant, 5 pytest-jubilant)

## Fixes by Severity

| Severity | Count | Percentage |
|----------|-------|------------|
| High     | 7     | 30%        |
| Medium   | 11    | 48%        |
| Low      | 5     | 22%        |

### High-severity fixes
- **jubilant:** app/leader syntax crash in run/exec, secrets crash on Juju < 3.6, destroy-model hang on microk8s, deploy --bind wrong format, status-error exception crashing wait()
- **pytest-jubilant:** missing imports in __init__.py, pack_charm crash when no resources

## Top Bug Areas

| Bug Area          | Count | Notes |
|-------------------|-------|-------|
| juju-cli-wrapper  | 6     | Most common area; CLI argument formatting, type mismatches, response key lookups |
| status-checking   | 5     | Error handling for transient states, logging noise, API ergonomics |
| charm-deployment  | 5     | --bind format, resource handling (3 in pytest-jubilant), missing deploy params |
| config            | 1     | Reset API redesign |
| relation-handling | 1     | offer() API redesign |
| model-management  | 1     | destroy-model hang |
| packaging         | 4     | Python 3.8 compat, import errors, param rename |

## Top Bug Types

| Bug Type       | Count | Notes |
|----------------|-------|-------|
| api-contract   | 8     | Dominant type; mostly breaking API redesigns in early development (fix!) |
| edge-case      | 3     | Missing resources, Juju version compat, leader unit syntax |
| logic-error    | 4     | Wrong error message polarity, import issues, walrus operator misuse |
| error-handling | 2     | status-error exceptions, missing upstream-source key |
| type-error     | 1     | machine param int vs str |
| parsing        | 1     | Version string parsing |
| race-condition | 1     | microk8s destroy-model hang |
| other          | 3     | Logging improvements, Python version compat |

## Fix Categories

| Category   | Count |
|------------|-------|
| source-fix | 23    |
| test-fix   | 0     |
| docs-fix   | 0     |
| ci-fix     | 0     |
| build-fix  | 0     |

All 23 fixes are source-level code changes (though many include test updates alongside).

## Notable Patterns

1. **API churn in early development:** 6 of 18 jubilant fixes are breaking changes (fix!) concentrated in April 2025, indicating rapid API iteration. These cover config reset semantics, offer() signature, status helpers, and remove_unit(). The project stabilized after May 2025.

2. **Juju CLI contract mismatches are the top issue:** The most common bugs stem from incorrectly formatting CLI arguments (--bind, --model) or misinterpreting CLI output (leader unit key mapping, version string format). This is inherent to wrapping a CLI tool.

3. **Backward compatibility with older Juju versions:** Two fixes address crashes when running against older Juju controllers (secrets without checksums on Juju < 3.6, version parsing strictness).

4. **pytest-jubilant resource handling was fragile:** 4 of 5 pytest-jubilant fixes relate to charm resource parsing in pack_charm(), with a rapid fix-revert-fix cycle on 2025-05-01 showing the difficulty of handling diverse charm metadata formats.

5. **No pure test/CI/docs fixes:** Every fix touches source code. The project appears to have good test discipline, with tests updated alongside every source fix.

6. **Status-checking is a pain point:** 5 fixes relate to wait()/status handling, covering exception behavior, logging control, and API ergonomics -- reflecting that status polling is a central and complex part of the library.
