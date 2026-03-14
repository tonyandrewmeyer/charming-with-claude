---
name: operator-find-bugs
description: Find bugs in the canonical/operator (ops) Python framework for Juju charms. Use when asked to "find bugs in operator", "audit ops code", "review operator for bugs", "check ops for issues", "find bugs in this charm framework code", or review ops/, testing/, or pebble code for correctness issues. Specialized for Juju operator framework bug patterns including relation data, secrets, Pebble containers, data mutability, and testing-production divergence.
---

# Operator Bug Finder

Find bugs in the canonical/operator codebase using domain-specific knowledge from 235+ historical bug fixes.

## Scope

Report on: only the files or diff the user specifies.
Research: the entire codebase to build confidence before reporting.

Do not report issues based solely on pattern matching. Investigate data flow and confirm the bug is real before reporting.

## Step 1: Determine review scope

Identify what code areas are being reviewed:

| Code Area | Indicators | Load Reference |
|-----------|-----------|----------------|
| Relation data handling | `relation_get`, `relation_set`, `RelationData`, databag | `references/bug-patterns.md` section "Relation Data" |
| Secrets management | `secret_get`, `secret_set`, `secret_add`, `Secret` | `references/bug-patterns.md` section "Secrets" |
| Pebble / containers | `Container`, `push`, `pull`, `exec`, `pebble`, `Layer` | `references/bug-patterns.md` section "Pebble" |
| Testing framework | `Harness`, `Scenario`, `Context`, `_MockModelBackend` | `references/bug-patterns.md` section "Testing Divergence" |
| Data structures / API boundaries | `dict`, `copy`, `__init__`, `config`, return statements | `references/bug-patterns.md` section "Data Mutability" |
| Event framework | `emit`, `observe`, `defer`, `StoredState`, `Handle` | `references/bug-patterns.md` section "Event Framework" |
| Hook commands | `hookcmds`, `_ModelBackend`, Juju CLI calls | `references/bug-patterns.md` section "Juju API" |
| Error handling | `raise`, `except`, `Error`, exception classes | `references/bug-patterns.md` section "Error Handling" |
| Security-sensitive code | `open()`, `tempfile`, `ExecError`, permissions, credentials | `references/bug-patterns.md` section "Security" |
| Broad review / full audit | Multiple areas or unspecified | Read full `references/bug-patterns.md` |

Always read `references/anti-patterns.md` for concrete code patterns to search for.

## Step 2: Search for known bug patterns

For each relevant code area, search the codebase for the anti-patterns listed in `references/anti-patterns.md`. Use Grep with the provided search patterns.

For each match:
1. Read surrounding context (at least 20 lines around the match).
2. Trace data flow to determine if the pattern is actually buggy.
3. Check if there is an existing fix, test, or guard.
4. Only report if the bug is confirmed after investigation.

## Step 2.5: Hunt for novel bugs

The anti-patterns reference covers *known* recurring patterns. After searching for those, actively look for *new* bugs that do not match any documented pattern:

1. **Read each file in scope end-to-end** — do not rely solely on grep matches. Bugs hide between the patterns.
2. **Trace data through call chains**: pick 3-5 public API methods in the reviewed code and trace their inputs from caller to callee. Look for:
   - Assumptions about input types that callers can violate
   - Missing validation at API boundaries that exists at internal boundaries (or vice versa)
   - State changes that are not rolled back on error
3. **Compare parallel implementations**: for any operation implemented in both ops and a testing backend (Harness or Scenario), diff the logic side by side. Divergences not covered by the known patterns are likely new bugs.
4. **Check recent commits** (`git log --oneline -20 -- <file>`): recently changed code is statistically more likely to contain bugs. Read the diff for each recent change and look for regressions.
5. **Look for incomplete fixes**: when a bug was fixed in one place, search for the same pattern in analogous code. Historical fixes often miss parallel implementations.

## Step 3: Check for cross-cutting concerns

Always check these regardless of code area:

1. **Mutability at boundaries**: Are dicts/lists copied when stored from external input? Are internal dicts copied when returned?
2. **None guards**: Are values from Juju (env vars, API responses, metadata) guarded against None?
3. **Naming conventions**: Are hyphens vs underscores handled correctly at Juju API boundaries?
4. **Testing parity**: If a bug exists in ops, does the same bug exist in Harness or Scenario (or vice versa)?
5. **Timezone awareness**: Are datetimes created with explicit timezone info?

## Step 4: Verify each finding

For each potential bug:
- Confirm the input is actually reachable (trace callers).
- Check if another code path already handles the case.
- Search for existing tests that cover the scenario.
- Check git blame to see if the code was recently changed.
- Compare behavior between ops (production) and testing backends (Harness/Scenario).

## Step 5: Report findings

### Severity classification

| Severity | Criteria | Examples |
|----------|----------|----------|
| **Critical** | Security issue or data corruption | Credential leak in error messages, world-readable secret files |
| **High** | Runtime crash or silent wrong behavior | KeyError from missing None guard, mutated internal state via returned reference |
| **Medium** | Testing-production divergence or edge case | Harness returns reference instead of copy, naive datetime without timezone |
| **Low** | Code quality or unlikely edge case | Missing type annotation, theoretical mutability risk on immutable types |

### Output format

```markdown
## Bug Review: [Scope Description]

### Summary
- **Findings**: X (Y High, Z Medium, ...)
- **Code areas reviewed**: [list]

### Findings

#### [BUG-001] [Category] — [Brief description] (Severity)
- **Location**: `file.py:123`
- **Pattern**: [Which known bug pattern this matches]
- **Issue**: [What the bug is]
- **Impact**: [What goes wrong at runtime]
- **Evidence**:
  ```python
  [Buggy code snippet]
  ```
- **Recommended fix**:
  ```python
  [Fixed code snippet]
  ```
- **Historical precedent**: [Link to commit that fixed a similar bug, if applicable]

### Needs Verification
[Items where you could not fully confirm the bug]

### Confirmed Safe
[Patterns that looked suspicious but were verified as correct, with explanation]
```

### False positive controls

Do NOT flag:
- Immutable types (str, int, bool, float) returned without copying
- `.get()` with a safe default value (e.g., `.get('key', {})` followed by `.items()`)
- Objects intentionally returned by reference (e.g., event emitters, the `on` attribute)
- Testing-only code that is documented as a known limitation
- Code paths guarded by version checks that correctly handle the version range

### Known false-positive patterns in this codebase

| Pattern | Why it's safe |
|---------|--------------|
| `return self._data[key]` in `ConfigData` | Values are immutable primitives |
| `return self._data.on` in `StoredStateData` | `on` must be live for event observation |
| `.get('options', {}).get(key)` | Default `{}` makes chained access safe |
| `env.get('JUJU_STORAGE_ID', '').split('/')` | Default `''` makes split safe |
| `return self._state.leader` in Scenario mock | Returns a `bool`, which is immutable |
| `return self._state.planned_units` in Scenario mock | Returns an `int`, which is immutable |
| Secret temp files inside `TemporaryDirectory` | Parent dir has 0o700 perms; files are deleted on block exit |
| `status_get()` returning dict directly | Caller destructures immediately, dict is not retained |
