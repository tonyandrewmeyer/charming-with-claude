# Sources

## Source Inventory

| Source | Trust Tier | Confidence | Contribution |
|--------|-----------|------------|-------------|
| 344 classified bug-fix commits across 8 Python repos | Canonical | High | Pattern extraction, severity calibration |
| CROSS_REPO_PATTERNS.md (cross-repo synthesis) | Canonical | High | Pattern synthesis, cross-repo validation |
| operator_audit.md (7 current findings) | Canonical | High | Current-code validation, novel patterns |
| python_repos_audit.md (15 current findings) | Canonical | High | Cross-repo validation, falsy value pattern |
| operator-analysis BUG_PATTERNS.md (previous analysis) | Canonical | High | Established patterns, 235 operator fixes |
| operator-analysis anti-patterns.md (previous skill) | Canonical | High | Searchable pattern template |
| operator-analysis SKILL.md (previous skill) | Canonical | High | Skill structure template |

## Synthesis Decisions

| Decision | Source Evidence | Status |
|----------|---------------|--------|
| Include falsy value confusion as top-level pattern | 10+ current audit findings, commit 1c0ff40d | Adopted |
| Include snap CLI embedded quotes | Current audit finding in both operator-libs-linux and charmlibs | Adopted |
| Include context manager safety | Current high-severity finding in operator _event_context | Adopted |
| Include exception constructor printf-style | Current finding in passwd.py across 2 repos | Adopted |
| Separate from Go skill | Zero pattern overlap between Python and Go fixes | Adopted |
| Include testing divergence as major section | 51 fixes — largest single area | Adopted |
| Include cross-repo propagation awareness | 8/15 Python audit bugs exist in both operator-libs-linux and charmlibs | Adopted |

## Coverage Matrix

| Dimension | Status | Coverage |
|-----------|--------|----------|
| Security patterns | Complete | 3 sub-patterns with examples |
| Data mutability | Complete | 5 sub-patterns with before/after |
| Falsy value confusion | Complete | 4 sub-patterns, most pervasive current finding |
| Relation data | Complete | 5 sub-patterns with precedents |
| Secrets management | Complete | 5 sub-patterns with precedents |
| Pebble/containers | Complete | 4 sub-patterns with examples |
| Testing divergence | Complete | 5 sub-patterns with current bugs |
| Juju CLI | Complete | 3 sub-patterns with examples |
| Snap CLI | Complete | 3 sub-patterns with current bugs |
| Error handling | Complete | 3 sub-patterns with current bugs |
| Type confusion | Complete | 3 sub-patterns with precedents |
| Context manager safety | Complete | 1 sub-pattern with current bug |
| False-positive controls | Complete | 8 known-safe patterns |

## Repos Covered

- canonical/operator (218 fixes analyzed)
- canonical/charmlibs (19 fixes)
- canonical/jubilant (18 fixes)
- canonical/pytest-jubilant (5 fixes)
- canonical/operator-libs-linux (29 fixes)
- canonical/charmhub-listing-review (6 fixes)
- canonical/charmcraft-profile-tools (7 fixes)
- canonical/charm-ubuntu (7 fixes)
