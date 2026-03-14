---
name: charm-python-find-bugs
description: Find bugs in Canonical Charm Tech Python repositories (operator/ops, charmlibs, jubilant, pytest-jubilant, operator-libs-linux, and other Python charm code). Use when asked to "find bugs", "audit code", "review for bugs", "check for issues", or review Python code in any Juju charm framework repository. Specialized for charm ecosystem bug patterns including data mutability, falsy value confusion, relation data, secrets, Pebble containers, testing-production divergence, and snap/Juju CLI interactions. Built from analysis of 344 historical bug fixes across 8 Python repos.
---

# Charm Python Bug Finder

Find bugs in Canonical Charm Tech Python codebases using domain-specific knowledge from 344+ historical bug fixes across 8 repositories.

## Scope

Report on: only the files or diff the user specifies.
Research: the entire codebase to build confidence before reporting.

Do not report issues based solely on pattern matching. Investigate data flow and confirm the bug is real before reporting.

## Step 1: Determine review scope

Identify what code areas are being reviewed and load the relevant reference sections:

| Code Area | Indicators | Reference Section |
|-----------|-----------|-------------------|
| Data structures / API boundaries | `dict`, `list`, `copy`, `__init__`, `return self._`, property getters | `references/bug-patterns.md` — Mutability, Falsy Values |
| Relation data handling | `relation_get`, `relation_set`, `RelationData`, databag | `references/bug-patterns.md` — Relation Data |
| Secrets management | `secret_get`, `secret_set`, `Secret`, `secret:` prefix | `references/bug-patterns.md` — Secrets |
| Pebble / containers | `Container`, `Layer`, `Service`, `push`, `pull`, `exec`, `pebble` | `references/bug-patterns.md` — Pebble |
| Testing framework | `Harness`, `Scenario`, `Context`, `_MockModelBackend`, `mocking.py` | `references/bug-patterns.md` — Testing Divergence |
| Snap interaction | `snap`, `_snap_client`, `SnapCache`, `Snap.` | `references/bug-patterns.md` — Snap CLI |
| System libraries | `passwd`, `grub`, `sysctl`, `apt`, `systemd` | `references/bug-patterns.md` — System Libraries |
| Hook commands / Juju CLI | `hookcmds`, `_ModelBackend`, `juju`, CLI arg construction | `references/bug-patterns.md` — Juju CLI |
| Error handling | `raise`, `except`, `Error`, exception classes | `references/bug-patterns.md` — Error Handling |
| Security-sensitive code | `open()`, `tempfile`, permissions, credentials | `references/bug-patterns.md` — Security |
| Broad review / full audit | Multiple areas or unspecified | Read full `references/bug-patterns.md` |

Always read `references/anti-patterns.md` for concrete code patterns to search for.

## Step 2: Search for known bug patterns

For each relevant code area, search the codebase for the anti-patterns listed in `references/anti-patterns.md`. Use Grep with the provided search patterns.

For each match:
1. Read surrounding context (at least 20 lines around the match).
2. Trace data flow to determine if the pattern is actually buggy.
3. Check if there is an existing fix, test, or guard.
4. Only report if the bug is confirmed after investigation.

## Step 3: Hunt for novel bugs

After searching for known patterns, actively look for new bugs:

1. **Read each file in scope end-to-end** — do not rely solely on grep matches.
2. **Trace data through call chains**: pick 3-5 public API methods and trace inputs from caller to callee. Look for:
   - Assumptions about input types that callers can violate
   - Missing validation at API boundaries
   - State changes not rolled back on error
3. **Compare parallel implementations**: for operations implemented in both production and testing code, diff the logic side by side. Divergences are likely bugs.
4. **Check recent commits** (`git log --oneline -20 -- <file>`): recently changed code is more likely to contain bugs.
5. **Look for incomplete fixes**: when a bug was fixed in one place, search for the same pattern in analogous code. Historical fixes often miss parallel implementations (e.g., a mutability fix in `relation_get` but not `secret_get`).

## Step 4: Check cross-cutting concerns

Always check these regardless of code area:

1. **Mutability at boundaries**: Are dicts/lists copied when stored from external input? Copied when returned from public methods?
2. **Falsy value confusion**: Are `if value` or `if not value` checks used where `value is not None` is needed? Especially for values that can legitimately be 0, empty string, or False.
3. **None guards**: Are values from external sources (Juju, env vars, JSON, CLI output) guarded against None?
4. **Context manager safety**: Do `@contextmanager` functions wrap `yield` in `try/finally`?
5. **Testing parity**: If a bug exists in production code, does the same bug exist in testing code (or vice versa)?
6. **Type confusion**: Are `type()` checks used instead of `isinstance()`? Are int/str types confused for IDs, revisions, UIDs?
7. **Exception constructors**: Are exceptions raised with printf-style formatting (`TypeError("msg %s", val)`) instead of f-strings?

## Step 5: Verify each finding

For each potential bug:
- Confirm the input is actually reachable (trace callers).
- Check if another code path already handles the case.
- Search for existing tests that cover the scenario.
- Check git blame to see if the code was recently changed.
- Compare behavior between production and testing backends.

## Step 6: Report findings

### Severity classification

| Severity | Criteria | Examples |
|----------|----------|----------|
| **Critical** | Security issue or data corruption | Credential leak, world-readable files, CI injection |
| **High** | Runtime crash or silent wrong behavior | KeyError from missing guard, mutated internal state, UID 0 dropped |
| **Medium** | Testing divergence or edge case | Scenario returns reference not copy, naive datetime, falsy check on rarely-zero value |
| **Low** | Code quality or unlikely edge case | Missing type annotation, theoretical mutability on seldom-used path |

### Output format

```markdown
## Bug Review: [Scope Description]

### Summary
- **Findings**: X (Y High, Z Medium, ...)
- **Code areas reviewed**: [list]
- **Repos affected**: [list]

### Findings

#### [BUG-001] [Category] — [Brief description] (Severity)
- **Location**: `file.py:123`
- **Pattern**: [Which known pattern this matches, or "novel"]
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
- **Historical precedent**: [Commit that fixed a similar bug, if applicable]

### Confirmed Safe
[Patterns that looked suspicious but were verified as correct]
```

### False-positive controls

Do NOT flag:
- Immutable types (str, int, bool, float, tuple, frozenset) returned without copying
- `.get()` with a safe default followed by safe usage
- Objects intentionally returned by reference (event emitters, `on` attribute)
- Testing-only code documented as a known limitation
- Code paths guarded by version checks that correctly handle the version range
- `if value` checks where the value genuinely cannot be 0, empty string, or False (e.g., required string fields)

### Known false-positive patterns

| Pattern | Why it's safe |
|---------|--------------|
| `return self._data[key]` in `ConfigData` | Values are immutable primitives |
| `return self._data.on` in `StoredStateData` | `on` must be live for event observation |
| `.get('options', {}).get(key)` | Default `{}` makes chained access safe |
| `env.get('JUJU_STORAGE_ID', '').split('/')` | Default `''` makes split safe |
| `return self._state.leader` in Scenario | Returns `bool`, immutable |
| `return self._state.planned_units` in Scenario | Returns `int`, immutable |
| `if channel` in snap install | Channel is always a non-empty string when provided |
| `if name` for string parameters | Name strings are never empty when provided |
