# Sources

## Source Inventory

| Source | Trust Tier | Confidence | Contribution | Constraints |
|--------|-----------|------------|-------------|-------------|
| `BUG_PATTERNS.md` (local analysis) | canonical | high | 13 bug pattern categories from 235+ fixes | Derived from git history analysis of canonical/operator |
| `CURRENT_CODE_AUDIT.md` (local analysis) | canonical | high | 14 current findings (3 high, 6 medium, 5 low) | Cross-referenced against current HEAD |
| `code_audit_findings.json` (local analysis) | canonical | high | 20 static analysis findings | Automated pattern matching, some false positives |
| `commit-summaries/` (local analysis) | canonical | high | 200+ individual bug fix commit analyses | Full diff and context analysis per commit |
| `operator/AGENTS.md` | canonical | high | Project structure, conventions, dev standards | Upstream maintained |
| `high_severity_analysis.json` (local analysis) | canonical | high | 15 high-severity fix deep-dives | Root cause and fix pattern analysis |
| `detailed_analysis.json` (local analysis) | secondary | medium | Extended pattern analysis | Includes lower-confidence findings |

## Synthesis Decisions

| Decision | Source Evidence | Status |
|----------|---------------|--------|
| Classify as security-review skill | Matches vulnerability-finding pattern with domain-specific knowledge | adopted |
| Use Domain Expert pattern (SKILL.md + references/) | Bug patterns too large for single file (~380 lines catalog + ~200 lines anti-patterns) | adopted |
| Conditional loading by code area | 13 distinct pattern categories map to different code areas | adopted |
| Include false-positive controls | 5 low-severity findings in audit confirmed as false positives | adopted |
| Include historical commit precedents | Links to fix commits help verify pattern is real, not theoretical | adopted |
| Separate anti-patterns reference | Searchable grep patterns need different structure from narrative catalog | adopted |

## Coverage Matrix

| Dimension | Status | Notes |
|-----------|--------|-------|
| Security patterns | complete | 3 patterns: info leak, file perms, CI injection |
| Data mutability | complete | Copy-on-store, copy-on-return, immutable alternatives |
| Relation data | complete | 6 sub-patterns from 25+ fixes |
| Secrets management | complete | 5 sub-patterns from 13+ fixes |
| Pebble/container | complete | 6 sub-patterns from 16+ fixes |
| Testing divergence | complete | 6 sub-patterns from 32+ fixes |
| Juju API compat | complete | Version deps, Python compat, datetime |
| Error handling | complete | Wrong types, missing edges, poor messages |
| Event framework | complete | Snapshots, transactions, handle reuse |
| Configuration | complete | Falsy defaults, immutability |
| Type annotations | complete | Wrong types, syntax, imports |
| False positive controls | complete | 5 confirmed-safe patterns documented |
| Anti-pattern search patterns | complete | 13 grepable patterns with true/false positive guidance |

## Retrieval Stopping Rationale

All 13 bug pattern categories from the historical analysis are covered. The coverage matrix shows no missing high-impact dimensions. The anti-patterns reference provides concrete search patterns for each category. Further retrieval would yield diminishing returns as the source material (235+ bug fixes) has been fully analyzed.

## Changelog

- 2026-03-14: Initial creation from comprehensive bug fix analysis
