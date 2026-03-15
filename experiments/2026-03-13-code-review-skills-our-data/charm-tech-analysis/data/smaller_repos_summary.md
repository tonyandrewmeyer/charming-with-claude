# Smaller Charm Tech Repos -- Bug-Fix Classification Summary

**Total fixes classified:** 49 across 4 repositories

## Per-Repository Breakdown

### operator-libs-linux (29 fixes)

- **Severity:** low: 15, high: 7, medium: 7
- **Top areas:** snap: 13, apt-package-management: 9, systemd: 4
- **Top types:** logic-error: 8, type-error: 5, other: 5
- **Fix categories:** source-fix: 18, test-fix: 6, docs-fix: 4, build-fix: 1

### charmhub-listing-review (6 fixes)

- **Severity:** medium: 6
- **Top areas:** automation: 3, ci-build: 2, config: 1
- **Top types:** config: 3, data-validation: 1, api-contract: 1
- **Fix categories:** source-fix: 4, build-fix: 1, ci-fix: 1

### charmcraft-profile-tools (7 fixes)

- **Severity:** medium: 4, low: 3
- **Top areas:** automation: 3, ci-build: 2, other: 1
- **Top types:** logic-error: 3, config: 2, other: 1
- **Fix categories:** source-fix: 3, ci-fix: 2, docs-fix: 1, test-fix: 1

### charm-ubuntu (7 fixes)

- **Severity:** medium: 3, low: 3, high: 1
- **Top areas:** packaging: 2, testing: 2, config: 2
- **Top types:** config: 3, other: 1, api-contract: 1
- **Fix categories:** source-fix: 4, ci-fix: 1, build-fix: 1, test-fix: 1

## Total Fixes by Severity

| Severity | Count | Percentage |
|----------|-------|------------|
| High     | 8 | 16% |
| Medium   | 20 | 40% |
| Low      | 21 | 42% |

## Top Bug Areas

| Area | Count |
|------|-------|
| snap | 13 |
| apt-package-management | 9 |
| automation | 6 |
| ci-build | 5 |
| systemd | 4 |
| packaging | 3 |
| config | 3 |
| testing | 3 |
| sysctl | 2 |
| other | 1 |

## Top Bug Types

| Type | Count |
|------|-------|
| logic-error | 12 |
| config | 9 |
| other | 7 |
| edge-case | 5 |
| type-error | 5 |
| api-contract | 4 |
| test-fix | 3 |
| data-validation | 2 |
| state-management | 1 |
| parsing | 1 |

## Fix Categories

| Category | Count |
|----------|-------|
| source-fix | 29 |
| test-fix | 8 |
| docs-fix | 5 |
| ci-fix | 4 |
| build-fix | 3 |

## Notable Patterns

1. **Snap library dominates fixes in operator-libs-linux.** 14 of 29 fixes target the snap management library, with recurring issues around CLI argument formatting (cohort, classic confinement flags) and edge cases in the snapd API (task status, revision types, falsy keys).

2. **apt package management is the second most-fixed area** (9 fixes), with critical bugs around package installation logic (retry/failure tracking, environment inheritance, sources.list parsing, GPG key handling).

3. **Type system issues are a recurring theme.** Multiple fixes address `type()` vs `isinstance()`, missing type annotations, and string-vs-int confusion for snap revisions. This suggests the codebase grew before adopting strict typing.

4. **CI and configuration issues are prominent in newer/smaller repos.** charmhub-listing-review and charmcraft-profile-tools have a higher proportion of CI/config fixes, consistent with projects still maturing their build pipelines.

5. **Path handling is a repeated pain point** in charmhub-listing-review, with three separate fixes addressing where and how the reviewers file is located (relative path, hardcoded CI path, then CLI argument).

6. **Test quality issues discovered late.** Several sysctl tests used `==` instead of function calls (`f.write == data` instead of `f.write(data)`), meaning tests were silently passing without actually testing anything.

7. **High-severity fixes concentrate in the core libraries.** All high-severity bugs are in operator-libs-linux (snap, apt) and charm-ubuntu (packaging), while peripheral tools mostly have medium/low severity issues.
