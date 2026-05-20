# Charmlibs Bug-Fix Classification Summary

**Total fixes analyzed:** 19 (April 2025 - February 2026)

## Fixes by Severity

| Severity | Count | Percentage |
|----------|-------|------------|
| High     | 2     | 10.5%      |
| Medium   | 7     | 36.8%      |
| Low      | 10    | 52.6%      |

## Top Bug Areas

| Area          | Count | Notes |
|---------------|-------|-------|
| typing        | 4     | Type annotation corrections (pyright, Literal, Optional, PathProtocol) |
| ci-build      | 3     | Silent lint failures, CODEOWNERS, workflow filenames |
| packaging     | 3     | Version bumps, directory restructuring, whitespace in version strings |
| other         | 3     | File permissions API, chown consistency, error message text |
| relation-data | 2     | Missing __hash__ on certificate-related classes |
| secrets       | 2     | App-owned vs unit-owned secrets, missed secret_expired events |
| testing       | 1     | Locked dependencies for interface tests |
| docs          | 1     | Wrong package name in README |

## Top Bug Types

| Type           | Count | Notes |
|----------------|-------|-------|
| type-error     | 4     | Mostly pyright/typing corrections |
| other          | 4     | Version bumps, directory moves, docs |
| logic-error    | 3     | Error message text, CODEOWNERS glob, CI workflow names |
| api-contract   | 3     | Secret ownership model, file permission/ownership behavior |
| mutability     | 2     | Missing __hash__ after migrating from dataclasses |
| edge-case      | 2     | Certificate renewal safety net, version string whitespace |
| error-handling | 1     | CI script not propagating exit codes |

## Fix Categories

| Category   | Count |
|------------|-------|
| source-fix | 12    |
| ci-fix     | 4     |
| build-fix  | 2     |
| docs-fix   | 1     |

## Notable Patterns

1. **TLS certificates library dominates fixes (10 of 19).** This is the most actively maintained and most complex library in the monorepo. Fixes range from critical (missed certificate renewals, wrong secret ownership) to cosmetic (type annotations, error messages).

2. **Hashability is a recurring issue.** Two separate commits (commits #280 and #322) add missing `__hash__` methods to certificate-related classes after they were migrated away from dataclasses. This suggests the migration was done without a checklist for protocol compliance.

3. **CI infrastructure masked real failures.** The lint script in the justfile was missing `exit $FAILURES`, causing linting to always report success. This masked pyright type-checking errors across multiple libraries, requiring follow-up fix PRs once discovered.

4. **Secrets ownership model had a correctness bug.** In `Mode.APP`, private keys were stored as unit-owned secrets instead of app-owned, meaning non-leader units could incorrectly generate and access secrets. This is a high-severity API contract violation.

5. **Certificate renewal had a reliability gap.** The `secret_expired` Juju event could fail to trigger or complete, leaving certificates to expire silently. A safety-net check was added in `_renew_expiring_certificates()` as a fallback -- indicating the Juju event model alone is insufficient for critical lifecycle operations.

6. **Pathops library had early-stage API refinement.** Three fixes in April 2025 adjusted file permission and ownership behavior in write methods, suggesting the initial API contract was under-specified for existing-file edge cases.
