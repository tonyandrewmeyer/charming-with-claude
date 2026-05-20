# Operator (canonical/operator) Bug Fix Classification Summary

Analysis of **218 bug-fix commits** from the canonical/operator repository (Python Ops framework for Juju charms), spanning October 2019 through March 2026.

---

## Total Fixes by Severity

| Severity | Count | Percentage |
|----------|-------|------------|
| High     | 48    | 22.0%      |
| Medium   | 136   | 62.4%      |
| Low      | 34    | 15.6%      |

High-severity fixes include crashes (None/missing guards, naming mismatches), data corruption (mutability bugs), and security issues (info leaks, insecure file permissions).

---

## Top Bug Areas

| Bug Area            | Count | Percentage | Notes                                                    |
|---------------------|-------|------------|----------------------------------------------------------|
| testing-framework   | 51    | 23.4%      | Harness and Scenario divergences from real Juju           |
| relation-data       | 33    | 15.1%      | Databag access, validation, serialization                 |
| pebble              | 32    | 14.7%      | Container interaction, file ops, exec, layer merging      |
| secrets             | 17    | 7.8%       | ID canonicalization, caching, API arg conflicts           |
| error-handling      | 14    | 6.4%       | Wrong exception types, missing error paths, logging       |
| event-framework     | 12    | 5.5%       | Dispatch, deferred events, stored state, snapshots        |
| docs                | 11    | 5.0%       | Docstrings, typos, links, README                          |
| juju-api            | 10    | 4.6%       | Version compat, credential-get, bindings, network-get     |
| ci-build            | 9     | 4.1%       | GitHub workflows, tox, badges, metadata                   |
| type-annotations    | 8     | 3.7%       | Wrong return types, assignment vs annotation syntax        |
| configuration       | 7     | 3.2%       | Falsy defaults, immutability, config-get parsing          |
| security            | 5     | 2.3%       | Info leaks in ExecError, SQLite permissions, CI injection  |
| imports             | 4     | 1.8%       | Cyclic imports, pebble import issues                      |
| actions             | 2     | 0.9%       | Action param handling                                     |
| storage             | 1     | 0.5%       | Storage event name parsing                                |
| status              | 1     | 0.5%       | collect-status lifecycle                                  |
| resources           | 1     | 0.5%       | ResourceMeta for oci-image type                           |

---

## Top Bug Types

| Bug Type          | Count | Percentage | Description                                               |
|-------------------|-------|------------|-----------------------------------------------------------|
| logic-error       | 93    | 42.7%      | General incorrect logic, wrong conditions, missing paths   |
| other             | 25    | 11.5%      | Typos, spacing, metadata, misc                            |
| test-divergence   | 16    | 7.3%       | Testing framework behavior differs from production Juju   |
| data-validation   | 13    | 6.0%       | Missing or incorrect input validation                     |
| type-error        | 12    | 5.5%       | Wrong types, annotation errors, type confusion            |
| naming-mismatch   | 10    | 4.6%       | Hyphen vs underscore, wrong field names, KeyError         |
| none-guard        | 10    | 4.6%       | Missing None checks causing AttributeError/TypeError      |
| version-compat    | 9     | 4.1%       | Juju or Python version incompatibility                    |
| exception-type    | 8     | 3.7%       | Wrong exception class caught or raised                    |
| mutability        | 6     | 2.8%       | Shared mutable state, missing copies at boundaries        |
| edge-case         | 5     | 2.3%       | Unhandled empty, missing, or unusual inputs               |
| api-contract      | 4     | 1.8%       | Wrong API signatures, conflicting arguments               |
| info-leak         | 2     | 0.9%       | Sensitive data exposed in error messages                  |
| race-condition    | 2     | 0.9%       | Flaky tests, hanging connections, timing issues           |
| parsing           | 1     | 0.5%       | Datetime or data format parsing errors                    |
| file-permissions  | 1     | 0.5%       | Insecure file creation modes                              |
| caching           | 1     | 0.5%       | Stale cached data (secrets)                               |

---

## Fix Categories

| Category    | Count | Percentage |
|-------------|-------|------------|
| source-fix  | 145   | 66.5%      |
| test-fix    | 46    | 21.1%      |
| ci-fix      | 14    | 6.4%       |
| docs-fix    | 13    | 6.0%       |

---

## Comparison with Previous Analysis (BUG_PATTERNS.md)

The previous analysis in `/home/ubuntu/operator-analysis/BUG_PATTERNS.md` identified 235 bug fixes and established 13 pattern categories. This classification of 218 commits (a subset focused on fix-labelled commits) confirms and refines those findings:

### Confirmed patterns (consistent with previous analysis)

1. **Data mutability and sharing** -- Still a high-impact pattern. The most recent fix (March 2026) is still in this category: `testing.Context` holding direct references to user dicts. The previous analysis counted 6+; this analysis finds 6, confirming it remains a persistent but relatively rare pattern.

2. **Missing None/optional guards** -- 10 instances found, consistent with previous "5+" estimate. These remain high-severity crashes.

3. **Testing framework / production divergence** -- The largest category at 51 fixes (23.4%), up from the previous "32+" estimate. This is the dominant bug area in the codebase, spanning Harness behavior, Scenario consistency, and event simulation accuracy.

4. **Relation data handling** -- 33 fixes (15.1%), up from previous "25+". Includes databag access validation, non-string key bugs, and relation-broken event handling.

5. **Secrets management** -- 17 fixes (7.8%), up from "13+". Continues to be a significant area with ID canonicalization, caching, and API argument issues.

6. **Pebble/container bugs** -- 32 fixes (14.7%), up from "16+". Path handling, binary files, layer merging, and exec behavior remain common.

7. **Juju version compatibility** -- 10 fixes (4.6%), consistent with "13+" when combined with some now classified under other areas.

8. **Error handling gaps** -- 14 fixes (6.4%), consistent with previous "16+".

9. **Security issues** -- 5 fixes found (previous: 3). The additional ones come from reclassifying related commits.

### New or refined patterns not fully captured before

1. **Pydantic integration edge cases** -- A new pattern emerging in 2026: handling Pydantic's experimental `MISSING` sentinel in `Relation.save()`. As Ops adds more structured data serialization (dataclass/Pydantic support for relation data), new edge cases around sentinel values and model_dump behavior are appearing. This was not present in the previous analysis.

2. **OpenTelemetry / tracing compatibility** -- Multiple fixes related to ops-tracing: not using private OpenTelemetry APIs, restricting SDK versions, allowing TLS 1.2. This represents a new dependency surface area.

3. **Context manager lifecycle in testing** -- The `testing.Context` context manager not properly exiting on exceptions, and `_Abort(0)` not being treated as success. This is a testing-framework sub-pattern around Python context manager semantics that was not called out previously.

4. **JujuContext type mismatches** -- `machine_id` being `int` instead of `str` represents a category of Juju API modeling errors where Python types don't match Juju's actual data types. Related to but distinct from the naming-mismatch pattern.

5. **Deprecation warning management** -- Fixes around `ops.main.main` deprecation warnings leaking into action output. Deprecation path management is a recurring concern as the API evolves.

6. **Environment variable leakage in tests** -- Multiple fixes (`avoid changing os.environ in Harness`, `expose mocked Juju env vars via os.environ`) show an ongoing tension between test isolation and fidelity. Tests that modify `os.environ` can leak state across test cases.

---

## Temporal Trends

- **2019-2021**: Foundational bugs -- wrong event attributes, basic Pebble file handling, Python version compat, relation ID issues
- **2022-2023**: Relation data validation, secrets management (new Juju feature), Pebble path handling, security hardening
- **2024**: Testing framework alignment (Harness and Scenario), config type correctness, secret lifecycle edge cases
- **2025-2026**: Testing framework dominates fixes, Pydantic integration, tracing compatibility, mutability in testing.Context

The codebase has matured: early bugs were fundamental (wrong API usage, crashes), while recent bugs are increasingly about testing fidelity and integration edge cases with new Juju features.
