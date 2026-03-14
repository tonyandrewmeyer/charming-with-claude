# Sources

## Source Inventory

| Source | Trust Tier | Confidence | Contribution |
|--------|-----------|------------|-------------|
| 143 classified bug-fix commits across 2 Go repos | Canonical | High | Pattern extraction, severity calibration |
| CROSS_REPO_PATTERNS.md (cross-repo synthesis) | Canonical | High | Pattern synthesis, Go-specific sections |
| pebble_audit.md (5 current findings) | Canonical | High | Current-code validation, concurrency patterns |
| concierge_audit.md (12 current findings) | Canonical | High | Current-code validation, idempotency/error patterns |
| operator-analysis (previous skill template) | Canonical | High | Skill structure template |

## Synthesis Decisions

| Decision | Source Evidence | Status |
|----------|---------------|--------|
| Concurrency as top pattern | 19 instances, 76% high severity | Adopted |
| Include copy-paste detection | Current high-severity finding (MicroK8s/Google config) | Adopted |
| Include idempotency checking | 10 instances + current LXD init bug | Adopted |
| Include retry discrimination | Current bug in RunWithRetries + 2 historical precedents | Adopted |
| Include snap status states | Current bug in snapInstalledInfo | Adopted |
| Include credentials map overwrite | Current high-severity finding | Adopted |
| Separate from Python skill | Zero pattern overlap with Python fixes | Adopted |

## Coverage Matrix

| Dimension | Status | Coverage |
|-----------|--------|----------|
| Concurrency/deadlocks | Complete | 4 sub-patterns with examples |
| Nil map/pointer panics | Complete | 2 sub-patterns with before/after |
| Error handling | Complete | 4 sub-patterns with current bugs |
| Resource leaks | Complete | 2 sub-patterns with current bugs |
| Idempotency | Complete | 3 sub-patterns with current + historical |
| Retry logic | Complete | 1 pattern with current bug |
| Snap API | Complete | 3 sub-patterns |
| Copy-paste errors | Complete | 1 pattern with current bug |
| Named return shadowing | Complete | 1 pattern with exception |
| JSON marshaling | Complete | 1 pattern |
| Tomb lifecycle | Complete | 1 pattern |
| Struct initialization | Complete | 1 pattern |
| Security | Complete | 2 sub-patterns |
| State management | Complete | 3 sub-patterns with current bugs |
| False-positive controls | Complete | 6 known-safe patterns |

## Repos Covered

- canonical/pebble (108 fixes analyzed)
- canonical/concierge (35 fixes analyzed)
