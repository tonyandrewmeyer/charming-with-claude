# Charm Bug Pattern Analysis: 6,116 Fixes Across 134 Repositories

## Overview

This analysis systematically examined bug fix commits across the entire Juju charm ecosystem to identify recurring bug patterns and build an automated bug-finding skill. The work follows the methodology established in the [operator-analysis](../operator-analysis/) (single-repo, 235 fixes) and [charm-tech-analysis](../charm-tech-analysis/) (10 repos, 452 fixes) projects, but at ecosystem scale.

### Scope

- **134 charm repositories** cloned from `charms.csv`
- **10 teams**: Data, Observability, MLOps, IS, Identity, Telco, Commercial Systems, K8s, BootStack, Charm-Tech
- **6,116 bug fix commits** identified via conventional commit parsing and keyword scoring
- **2,519 source-code fixes** sampled for deep analysis (excluding CI-only, docs-only, test-only changes)

### Key Outputs

1. **CROSS_REPO_PATTERNS.md** -- 15 universal patterns, 58 searchable anti-patterns
2. **charm-find-bugs skill** -- Domain expert skill with SKILL.md + 2 reference files
3. **Per-repo fix data** -- JSON files for each of 134 repos in `data/`
4. **Validation results** -- 59 real bugs found across 14 test repos, 0 false positives (4 iteration rounds)

---

## Methodology

### Phase 1: Data Collection

All 144 unique GitHub repositories from `charms.csv` were cloned (2 failed -- personal repos not publicly accessible). For each repo, bug fix commits were identified using two methods:

1. **Conventional commits**: Messages matching `^fix[\s(:]` (case-insensitive)
2. **Keyword scoring**: Commit messages scored against 30+ fix-related keywords (fix, bug, crash, broken, missing, etc.) minus negative keywords (feat, refactor, docs, bump, etc.), threshold >= 3

This dual approach was critical because conventional commit adoption varies widely:
- Identity team: 96% conventional
- K8s team: 35% conventional

Without keyword scoring, 37% of the K8s team's fixes would have been missed entirely.

### Phase 2: Classification

Fixes were classified in two passes:

1. **Automated heuristic classification** of all 6,116 fixes by bug area (19 categories), bug type (12 categories), and severity (high/medium/low) using regex pattern matching against commit messages, changed files, and diff content.

2. **Deep agent analysis** of 18 representative batches (2 per team, ~40 fixes each) by Claude agents that read actual diffs and identified recurring patterns with concrete code examples.

### Phase 3: Pattern Synthesis

Team-level patterns were synthesized into cross-repo patterns by a synthesis agent that read all 8 team analysis reports plus aggregate statistics. The synthesis identified 15 universal patterns (appearing across 3+ teams) and team-specific patterns.

### Phase 4: Skill Construction

A `charm-find-bugs` skill was built following the Domain Expert pattern:
- `SKILL.md` -- 6-step workflow with code area routing table
- `references/bug-patterns.md` -- 13 pattern categories with before/after code examples
- `references/anti-patterns.md` -- 43 searchable patterns with grep commands and false-positive controls

### Phase 5: Validation

The skill was tested against 2 charm repos not used in synthesis:

| Repo | Findings | High | Medium | Low | False Positives |
|------|----------|------|--------|-----|----------------|
| grafana-k8s-operator | 3 | 1 | 2 | 0 | 0 |
| kafka-k8s-operator | 3 | 1 | 1 | 1 | 0 |
| **Total** | **6** | **2** | **3** | **1** | **0** |

Notable finds:
- **grafana-k8s**: Profiling feature silently broken due to unused constructor parameter (High)
- **kafka-k8s**: `event.relation.app` accessed without None guard in relation_broken handler (High)
- **kafka-k8s**: Typo "controller-passwrod" in requested_secrets silently prevents secret retrieval (Low)
- Both repos had dead code: relation_broken handlers defined but never registered with `framework.observe()`

---

## Findings

### Severity Distribution

| Severity | Count | Percentage |
|----------|-------|------------|
| Low | 3,047 | 49.8% |
| Medium | 2,840 | 46.4% |
| High | 229 | 3.7% |

Nearly half of all fixes are low severity (docs, formatting, test-only, trivial config). The 229 high-severity fixes concentrate in two areas: **observability** (44) and **database** (41), accounting for 37% of all critical bugs.

### Where Bugs Live

The top bug areas by fix count, excluding CI/build and test-only fixes:

| Area | Fixes | Repos | Teams | Why |
|------|-------|-------|-------|-----|
| Observability | 648 | 88 | 10 | Dashboard wiring, alert rules, scrape config, metric labels |
| Database | 546 | 41 | 7 | Connection handling, TLS, replication, backup safety |
| Packaging | 446 | 83 | 8 | Requirements pinning, dependency management |
| Juju interaction | 314 | 92 | 9 | Leader guards, secrets, model API, peer data |
| TLS/certificates | 299 | 67 | 9 | Certificate lifecycle, CA chain format, renewal |
| Ingress/networking | 278 | 46 | 9 | URL construction, scheme detection, external hostname |
| Status management | 243 | 79 | 10 | Status coherence, blocked vs waiting, early returns |
| Config handling | 210 | 79 | 9 | Truthiness, type mismatches, f-string omission |
| Pebble | 199 | 61 | 8 | Readiness, replanning, plan mutation, ChangeError |
| Auth/identity | 204 | 45 | 9 | Credential logging, permissions, method/property confusion |

### The Most Pervasive Patterns

**1. Missing exception handling** (15+ repos, 60% high severity)
External calls to K8s APIs, Pebble, databases, or Juju secrets without adequate try/except. The narrow-except variant (catching only one type when multiple are possible) is especially common.

**2. Truthiness vs explicit comparison** (virtually every team)
`if self.config['port']:` treats 0 as "not configured". This is the single most pervasive bug pattern. The Observability team alone fixed this 12+ times.

**3. Unregistered event handlers** (found in 2/2 validation repos)
Methods defined for relation_broken but never wired up with `framework.observe()`. The handler exists, the cleanup logic is correct, but the event never reaches it. This suggests a systematic issue with how event registration is organised.

**4. event.relation.app is None** (39+ repos)
During relation teardown, `event.relation.app` can be None. Code that accesses `.name` or `.data[app]` without a guard crashes.

**5. Stale TLS flags** (67 repos)
Storing `tls_enabled: true` in relation data instead of checking relation existence. When leadership changes, the flag becomes stale.

### Team-Specific Patterns

| Team | Distinctive Pattern | Why |
|------|-------------------|-----|
| Data | TLS toggle race conditions | Coordinating TLS state between charm and database requires two-phase handshake |
| Observability | Wrong datasource variables in dashboards | Importing dashboards from standalone Grafana uses `${DS_PROMETHEUS}` instead of COS `${prometheusds}` |
| MLOps | K8s resource cleanup on removal | CRDs and PVCs not cleaned up when charm is removed |
| Identity | Method vs property confusion | Auth library APIs changed signatures across versions |
| Telco | K8s API idempotency | Create-or-update patterns not handling "already exists" errors |
| IS | Pebble lifecycle ordering | Web app charms need config files pushed before service starts |
| K8s | Subprocess error handling | Missing `CalledProcessError` handling on snap/kubectl commands |
| BootStack | Hardware detection edge cases | BIOS/BMC queries failing on non-standard hardware |

### Temporal Trends

Bug fix volume grew from 101 (2020) to 1,563 (2023), then stabilised:
- **Config bugs dominate and grow**: From 45 (2020) to 539 (2024), reflecting increasing charm complexity
- **Security awareness increased in 2025**: Security fixes jumped from 7 (2024) to 26 (2025)
- **Race conditions emerged in 2023**: Correlates with multi-unit and multi-relation patterns in Data team charms
- **Edge cases are persistent**: High since 2022, reflecting diverse deployment environments

### Conventional Commit Adoption

| Team | Adoption | Impact |
|------|----------|--------|
| Identity | 96% | Easy to track fixes automatically |
| MLOps | 88% | Good coverage |
| Telco | 84% | Good coverage |
| IS | 83% | Good coverage |
| BootStack | 85% | Good coverage |
| Data | 69% | Many fixes found only via keyword scoring |
| Observability | 69% | Same |
| Charm-Tech | 65% | Small sample |
| Commercial Systems | 62% | Significant gap |
| K8s | 35% | Most fixes found via keyword scoring only |

---

## Skill Validation Analysis

### What Worked Well

1. **Anti-pattern catalogue produces high-signal matches.** All 6 bugs found by the skill were real, actionable issues. Zero false positives.

2. **Cross-cutting concern checklist catches systematic issues.** The "unregistered event handler" pattern was found in both validation repos independently, confirming it's a systematic issue not caught by existing reviews.

3. **False-positive controls prevent noise.** The skill correctly dismissed 7 patterns in grafana-k8s and 5 patterns in kafka-k8s that looked suspicious but were verified as correct (e.g., truthiness checks on genuinely boolean configs, credentials in container-internal Kafka config files).

4. **Novel bug detection works.** 2 of 6 bugs were "novel" (not matching any catalogued anti-pattern): the profiling parameter never passed in grafana-k8s, and the typo in kafka-k8s. The step 3 "hunt for novel bugs" methodology (end-to-end reading, tracing call chains) found these.

### Limitations

1. **Coverage depth vs breadth tradeoff.** With 134 repos, deep analysis of every repo was not feasible. The heuristic classification provides aggregate statistics but may miss nuanced patterns. The deep analysis covered ~18 batches (representative, not exhaustive).

2. **Keyword scoring has noise.** Some "fixes" identified by keyword scoring are actually features, refactors, or CI changes that happened to use fix-related words. The sampling step (filtering to source-code fixes) mitigated this.

3. **Heuristic severity classification is approximate.** The auto-classifier uses keyword matching on commit messages and diff size, which is a rough proxy. Some medium-severity bugs may actually be high-severity, and vice versa.

4. **No VM charm coverage.** The Launchpad and OpenDev repos in charms.csv (17 repos) were excluded because they require different cloning mechanisms. These include older machine charms that may have different bug patterns.

### Comparison to Prior Analyses

| Metric | operator-analysis | charm-tech-analysis | This analysis |
|--------|------------------|--------------------|-|
| Repos | 1 | 10 | 134 |
| Fixes analysed | 235 | 452 | 6,116 |
| Pattern categories | 13 | 16 (Python) + 14 (Go) | 15 + 58 anti-patterns |
| Bugs found in validation | 11 | 33 | 59 (14 repos tested) |
| False positive rate | 0% | 0% | 0% |
| Languages | Python | Python + Go | Python |

The scaling from 10 to 134 repos revealed patterns not visible at smaller scale:
- **Unregistered event handlers** -- only detectable as a systematic issue when seen across multiple repos
- **Team-specific patterns** -- TLS race conditions are a Data team problem; datasource variables are an Observability problem
- **Convention adoption variance** -- the 35-96% range in conventional commit adoption significantly affects automated analysis

---

## Iteration

After the initial skill build and validation (6 bugs, 0 FP across 2 repos), the skill was tested against 4 additional repos covering teams not in the initial validation:

| Repo | Team | Findings | High | Medium | Low | FP |
|------|------|----------|------|--------|-----|----|
| discourse-k8s | IS | 4 | 2 | 2 | 0 | 0 |
| hydra | Identity | 4 | 2 | 1 | 1 | 0 |
| opensearch | Data (VM) | 4 | 3 | 1 | 0 | 0 |
| sdcore-amf | Telco | 4 | 1 | 3 | 0 | 0 |

This iteration revealed 5 new anti-patterns not in the original catalogue:

1. **AP-044: Missing return after event.fail()** -- `event.fail()` doesn't stop execution; without `return`, the success path runs with None values. Found in hydra-operator.
2. **AP-045: next() without default** -- `next(gen)` raises `StopIteration` when no match. Especially dangerous in generator contexts where it silently terminates. Found in discourse-k8s.
3. **AP-046: Shell-style $VAR in f-strings** -- `f"${self.path}/logs"` includes a literal `$` because Python f-strings only interpolate `{...}`. Found in opensearch-operator.
4. **AP-047: Contradictory unit vs app status** -- Unit shows BlockedStatus while app shows WaitingStatus for the same condition. Found in sdcore-amf.
5. **AP-005 expanded** -- Boolean values (not just None) in Pebble environment dicts. Python `True` becomes `"True"` (capital T), which may not match Go expectations. Found in hydra-operator.

The false-positive controls were also expanded with 8 new known-safe patterns observed during validation (e.g., library-internal leader guards, `datetime.utcnow()` paired with naive-UTC cert expiry, `shell=True` with controlled inputs).

### Cumulative Validation Results (Rounds 1-2)

| Round | Repos Tested | Bugs Found | High | Medium | Low | False Positives |
|-------|-------------|------------|------|--------|-----|----------------|
| 1 | grafana-k8s, kafka-k8s | 6 | 2 | 3 | 1 | 0 |
| 2 | discourse-k8s, hydra, opensearch, sdcore-amf | 16 | 8 | 7 | 1 | 0 |
| **Total** | **6 repos** | **22** | **10** | **10** | **2** | **0** |

Notable findings across both rounds:
- **Unregistered event handlers** found in 3 of 6 repos (grafana-k8s, kafka-k8s, discourse-k8s dead SAML handler)
- **None guard missing** found in 3 of 6 repos (kafka-k8s, hydra, opensearch)
- **Unconditional replan** found in 2 of 6 repos (discourse-k8s, sdcore-amf)
- **Novel bugs** (not matching any catalogued pattern) found in 4 of 6 repos

### Round 3

The skill was tested against 4 more repos covering ingress, secrets management, workflow orchestration, and database delegation patterns:

| Repo | Team | Findings | High | Medium | Low | FP |
|------|------|----------|------|--------|-----|----|
| traefik-k8s | Observability | 5 | 1 | 2 | 2 | 0 |
| temporal-k8s | Commercial Systems | 6 | 0 | 4 | 2 | 0 |
| vault-k8s | Identity | 5 | 0 | 2 | 3 | 0 |
| mongodb-k8s | Data | 0* | 0 | 0 | 0 | 0 |

\* mongodb-k8s delegates all charm logic to the external `mongo-charms-single-kernel` package. The in-repo `src/charm.py` is a 36-line wrapper. 7 bugs were found in test helpers, but no charm-runtime bugs can be assessed without the external package. This revealed a limitation: **charms that vendor logic into external packages cannot be fully audited from their repo alone**.

This iteration revealed 6 new anti-patterns not in the previous catalogue:

1. **AP-048: exec() without wait()** -- `container.exec(["find", dir, "-delete"])` runs asynchronously; discarding the Process object means subsequent file pushes race with the still-running command. Found in traefik-k8s-operator.
2. **AP-049: Hardcoded string slicing for file extensions** -- `path.name[:5]` to strip `.cert` only works for 5-character basenames. Found in traefik-k8s-operator (cert cleanup deletes valid certs / retains stale ones).
3. **AP-050: Status set by helper overwritten by caller** -- `_handle_frontend_tls()` sets `BlockedStatus` and returns, but the calling `_update()` continues and overwrites with `MaintenanceStatus`. Found in temporal-k8s-operator.
4. **AP-051: Inverted boolean condition** -- `if skip_verify is False: logger.warning("configured to skip verification")` fires on the safe path. Found in vault-k8s-operator.
5. **AP-052: Wrong config key name** -- `self.config.get("pki_ca_allowed_domains")` when the actual key is `pki_allowed_domains`. `.get()` silently returns None, bypassing validation. Found in vault-k8s-operator.
6. **AP-053: Missing return after event.set_results()** -- Similar to AP-044 but for `set_results()`. Execution falls through to a second API call with invalid parameters. Found in temporal-k8s-operator.

Notable findings from round 3:
- **traefik-k8s cert cleanup** uses `path.name[:5]`, `path.name[:4]`, and `path.name[:18]` to extract hostnames from filenames -- all broken for any hostname not matching the assumed length (High severity)
- **vault-k8s hardcoded PKI mount path** -- ACME issuing cert and CRL URLs use `/v1/pki/` instead of the actual mount point (`charm-acme`), causing certificate chain validation failures for clients that follow AIA/CRL URLs (Medium)
- **temporal-k8s proxy env None values** -- when only one of HTTP_PROXY/HTTPS_PROXY is set, the other is None in the Pebble environment dict, causing `add_layer` to fail (Medium, AP-005)
- **Missing can_connect() guard** found in traefik-k8s (cert-removed handler) and temporal-k8s (restart action), confirming this remains one of the most pervasive patterns (AP-006)

The false-positive controls were expanded with 3 new known-safe patterns (exec without wait for read-only commands, intentionally disabled TLS in remove handlers, test helper code type issues).

### Round 4

The skill was tested against 4 more repos, including core COS infrastructure and a complex database charm:

| Repo | Team | Findings | High | Medium | Low | FP |
|------|------|----------|------|--------|-----|----|
| postgresql-k8s | Data | 6 | 0 | 2 | 4 | 0 |
| indico | IS | 10 | 2 | 5 | 3 | 0 |
| prometheus-k8s | Observability | 2 | 0 | 2 | 0 | 0 |
| kratos | Identity | 3 | 0 | 0 | 3 | 0 |

This iteration revealed 5 new anti-patterns:

1. **AP-054: String comparison of numeric counter values** -- `"9" > "10"` is True lexicographically. Relation data is always strings, so counter comparisons need `int()` conversion. Found in postgresql-k8s async replication primary selection.
2. **AP-055: None value in f-string URL interpolation** -- `f"{self.external_url}/path"` produces `"None/path"` when external_url is None. Found in prometheus-k8s catalogue API endpoints.
3. **AP-056: Action handler missing event.fail() on error path** -- Action catches exception, logs error, but doesn't call `event.fail()`. Action silently succeeds with empty results. Found in postgresql-k8s and indico.
4. **AP-057: os.path.join for URL construction** -- Works on Linux by coincidence but discards base URL if second arg starts with `/`. Found in kratos-operator.
5. **AP-058: model.get_secret(id=None)** -- `peer_data.get("secret-id")` returns None before leader sets it, then `model.get_secret(id=None)` crashes. Found in indico-operator.

Notable findings from round 4:
- **postgresql-k8s** has a subtle bug in `get_primary_cluster()` that uses string comparison for promotion counters while its sibling method correctly uses `int()` -- only triggers after 10+ async replication promotions
- **indico** has pervasive non-string values in Pebble environment dicts (booleans, ints, and potential Nones from 11+ sources in `_get_indico_env_config`)
- **prometheus-k8s** uses `self.external_url` (which can be None) in f-strings for catalogue API endpoints but correctly uses `self.most_external_url` for the main URL -- likely a copy-paste error
- **indico** calls `container.exec()` via `_get_installed_plugins()` BEFORE checking `can_connect()` in action handlers (AP-006 ordering variant)
- **AP-005 (non-string Pebble env)** continues to be the most pervasive pattern, found in 3 of 4 repos this round (postgresql-k8s LDAP port, indico multiple values, kratos boolean)

### Cumulative Validation Results (Rounds 1-4)

| Round | Repos Tested | Bugs Found | High | Medium | Low | False Positives |
|-------|-------------|------------|------|--------|-----|----------------|
| 1 | grafana-k8s, kafka-k8s | 6 | 2 | 3 | 1 | 0 |
| 2 | discourse-k8s, hydra, opensearch, sdcore-amf | 16 | 8 | 7 | 1 | 0 |
| 3 | traefik-k8s, temporal-k8s, vault-k8s, mongodb-k8s* | 16 | 1 | 8 | 7 | 0 |
| 4 | postgresql-k8s, indico, prometheus-k8s, kratos | 21 | 2 | 9 | 10 | 0 |
| **Total** | **14 repos** | **59** | **13** | **27** | **19** | **0** |

\* mongodb-k8s excluded from bug count (external package delegation).

---

## Rounds 5-10: Human-Reviewed Iteration

After building the review tool (see below), the skill was iterated through 6 further rounds with human review of every finding. An `iterate-bugs` skill was created to automate the cycle: run `charm-find-bugs` against untested repos → import results into the review tool → human reviews each finding → export reviewed data → update the skill.

### Round 5

| Repo | Team | Findings | High | Medium | Low | FP |
|------|------|----------|------|--------|-----|----|
| pgbouncer-k8s | Data | 7 | 3 | 3 | 0 | 0 |
| redis-k8s | Data | 6 | 3 | 3 | 0 | 0 |
| synapse | IS | 6 | 2 | 3 | 0 | 0 |
| loki-k8s | Observability | 5 | 1 | 3 | 1 | 0 |
| wordpress-k8s | IS | 5 | 1 | 2 | 1 | 0 |
| oathkeeper | Identity | 4 | 2 | 2 | 0 | 0 |
| tempo-coordinator-k8s | Observability | 3 | 2 | 0 | 1 | 0 |
| alertmanager-k8s | Observability | 2 | 1 | 1 | 0 | 0 |

Notable findings:
- **wordpress-k8s Critical**: Unescaped DB password interpolated into PHP code -- potential code injection
- **pgbouncer-k8s Critical**: Monitoring password exposed in Pebble CLI arguments
- **redis-k8s**: `==` instead of `=` for status assignment (novel pattern, now AP-059)
- **loki-k8s**: Operator precedence bug with ternary expression (now AP-060)
- **synapse**: Glob pattern in exec without shell (now AP-061); `DeepDiff is not None` always True (now AP-062)
- **AP-005 (non-string Pebble env)** found in 2/8 repos, confirming it as the most pervasive pattern

This round's human review identified **10 false positives** across rounds 1-5, revealing three systematic FP categories:

1. **`relation.app` is never None with modern ops** (5 FPs) -- AP-014 removed from catalogue
2. **Unconditional `container.replan()` is fine** (3 FPs) -- AP-008 removed; Pebble handles idempotency
3. **ExecError on workload binary is acceptable** (1 FP) -- added to FP controls

### Rounds 6-10

After incorporating the FP corrections, the skill achieved 0% false positive rate across the remaining rounds:

| Round | Repos Tested | Confirmed | FP | FP Rate |
|-------|-------------|-----------|-----|---------|
| 6 | postgresql-vm, grafana-agent, zookeeper-k8s, seldon-core | 17 | 0 | 0% |
| 7 | pgbouncer-vm, trino-k8s, cos-proxy, mlflow | 17 | 1 | 5.6% |
| 8 | identity-platform-admin-ui, cos-configuration-k8s, superset-k8s, sdcore-nms | 19 | 0 | 0% |
| 9 | self-signed-certificates, gunicorn-k8s, openfga, mimir-coordinator-k8s | 11 | 0 | 0% |
| 10 | hardware-observer, kubeflow-profiles, nginx-ingress-integrator, content-cache-k8s | 15 | 1 | 6.3% |

New anti-patterns added from rounds 5-10: AP-059 through AP-065 (comparison operator as assignment, operator precedence with ternary, glob in exec without shell, DeepDiff truthiness, unescaped data in config language, missing None guard on version field, implicit None return).

Additional false-positive controls added from reviewer notes:
- `@cached_property` on charm instances is safe (ops reinitialises per hook)
- Short busy-wait loops are acceptable (Juju lacks retry facilities)

### Historical Batch Analysis

After 10 validation rounds showed diminishing returns, 4 of the 50 unanalysed historical fix batches were examined to check for patterns missed during the initial 18-batch deep analysis:

- **Batch 9** (Data: mysql-k8s, mysql-operator, 40 fixes)
- **Batch 22** (IS: jenkins-k8s, mattermost, nginx-ingress, 40 fixes)
- **Batch 39** (MLOps: knative, kserve, kubeflow-dashboard, 40 fixes)
- **Batch 53** (Observability: loki-k8s, mimir-coordinator, 40 fixes)

Results: The existing catalogue covered the majority of recurring patterns. Most fixes were test-only, dependency bumps, or linting. The substantive source-code fixes mapped to existing APs (AP-006, AP-018, AP-020, AP-027, AP-028, AP-029, AP-033, AP-036, AP-041, AP-052, AP-055). Four new patterns were identified and added:

- **AP-066**: `lstrip()`/`rstrip()` used as `removeprefix()`/`removesuffix()` -- classic Python footgun
- **AP-067**: Missing initialisation guard in early-lifecycle event handlers (4 commits across 2 repos)
- **AP-068**: Config-derived relation data not re-sent on `config_changed`
- **AP-069**: Exception message or traceback leaks credentials

### Cumulative Validation Results (All Rounds)

| Round | Repos Tested | Confirmed | FP | FP Rate |
|-------|-------------|-----------|-----|---------|
| 1-4 | 14 | 59 | 0 | 0% |
| 5 | 8 | 28 | 10 | 26.3%* |
| 6 | 4 | 17 | 0 | 0% |
| 7 | 4 | 17 | 1 | 5.6% |
| 8 | 4 | 19 | 0 | 0% |
| 9 | 4 | 11 | 0 | 0% |
| 10 | 4 | 15 | 1 | 6.3% |
| **Total** | **41 repos** | **166** | **12** | **6.7%** |

\* Round 5 FPs were from systematic categories (relation.app None, unconditional replan) that were corrected in the skill. After correction, FP rate dropped to 1.6% across rounds 6-10.

The skill now catalogues **69 anti-patterns** (AP-001 through AP-069, minus AP-008 and AP-014) and **25 cross-cutting concerns**.

### Pattern frequency across all validation repos

| Pattern | Repos found in | Frequency |
|---------|---------------|-----------|
| AP-005 (non-string Pebble env) | 14/41 | Most pervasive |
| AP-010 (restart without ChangeError) | 8/41 | Very common |
| AP-006 (missing can_connect) | 7/41 | Very common |
| AP-044/056 (missing return/fail in actions) | 7/41 | Very common |
| AP-012 (missing relation_broken) | 5/41 | Common |
| AP-018/020 (credential exposure) | 7/41 | Common |
| AP-045 (next without default) | 5/41 | Common |
| AP-050 (status overwritten by caller) | 4/41 | Common |
| AP-001 (truthiness on config) | 4/41 | Common |
| AP-054 (string comparison of counters) | 3/41 | Moderate |
| AP-055 (None in f-string URL) | 3/41 | Moderate |
| AP-057 (os.path.join for URLs) | 3/41 | Moderate |

---

## Review Tool

To support the iterative validation workflow, a local review tool was built for triaging and tracking bug findings. The `charm-find-bugs` skill produces structured markdown reports (`skill_validation_*.md`), but reviewing dozens of findings across multiple rounds required more than reading files -- it needed filtering, status tracking, and a way to record reviewer judgements that could feed back into skill improvement.

### What It Does

The tool implements a four-stage loop:

1. **Import** -- Parses structured markdown validation reports and loads findings into a local SQLite database, keyed by `(repo, bug_id)` for deduplication.
2. **Review** -- Presents each finding in a two-panel interface where a reviewer reads the issue, evidence, and recommended fix, then marks it as **reviewed** (true positive) or **false positive**.
3. **Track** -- Maintains review progress, statistics by severity/repo/round, and reviewer notes.
4. **Export** -- Dumps all findings and their review status as JSON for feeding back into skill improvement.

### Stack and Design

The tool provides three interfaces -- a web UI, a terminal UI (TUI), and a CLI -- all backed by the same SQLite database:

- **Web UI** (FastAPI + htmx + Pico CSS): A dashboard with progress bars and breakdowns, plus a two-panel findings page with filter dropdowns and keyboard shortcuts (`j`/`k` navigate, `r` reviewed, `f` false positive, `n` notes).
- **TUI** (Textual): The same two-panel review workflow in the terminal, useful for SSH sessions or when a browser is inconvenient.
- **CLI** (Click): `import`, `import-all`, `list`, `show`, `review`, `stats`, `export`, `serve`, and `tui` subcommands.

Key design choices:
- **Dual sync/async DB layer** -- the CLI and TUI use synchronous SQLite; the web server uses `aiosqlite`. Both share the same schema.
- **htmx-driven UI** -- partial HTML responses keep the UI responsive without a JavaScript framework. Filters, row selection, and review actions all use htmx swaps.
- **Markdown parser** -- `parser.py` extracts structured fields from the `#### [BUG-NNN]` format used by the skill's validation reports, handling code blocks, severity levels, and confirmed-safe sections.
- **Deduplication on import** -- `UNIQUE(repo, bug_id)` constraint means re-imports are safe.

### Why It Matters

The review tool closed the feedback loop between skill validation and skill improvement. Without it, tracking which findings were true positives across 41 repos and 10 rounds would have been error-prone and tedious. The export capability meant that after each review round, confirmed true positives could be fed back to expand the anti-pattern catalogue, while false positives informed tightening of the false-positive controls. Reviewer notes captured domain knowledge (e.g., "modern ops guarantees `.app` is non-None", "Pebble handles replan idempotency") that directly shaped the skill's evolution. The tool lives at `review-tool/` in this experiment directory.

---

## Files Produced

```
charm-analysis/
├── WRITEUP.md                          # This document
├── CROSS_REPO_PATTERNS.md              # 15 universal patterns
├── .claude/skills/charm-find-bugs/     # Bug-finding skill (iterated x10)
│   ├── SKILL.md                        # 6-step workflow + 25 cross-cutting concerns
│   └── references/
│       ├── bug-patterns.md             # 15 pattern categories with examples
│       └── anti-patterns.md            # 69 searchable anti-patterns
├── .claude/skills/iterate-bugs/        # Iteration workflow skill
│   └── SKILL.md                        # 8-step cycle: audit → import → review → update
├── scripts/
│   ├── extract_fixes.py                # Clone repos and extract fix commits
│   ├── auto_classify.py                # Heuristic classification
│   ├── sample_for_analysis.py          # Sample representative fixes
│   ├── prepare_batches.py              # Batch fixes for agent analysis
│   └── aggregate_patterns.py           # Cross-repo aggregate analysis
├── data/
│   ├── all_fixes.json                  # 6,116 raw fix commits
│   ├── all_classified.json             # Heuristic classification of all fixes
│   ├── classification_stats.json       # Aggregate statistics
│   ├── aggregate_analysis.json         # Cross-repo analysis
│   ├── analysis_*.json                 # Per-team deep analysis (8 files)
│   ├── skill_validation_*.md           # Validation reports (41 repos, rounds 1-10)
│   ├── all_rounds_reviewed.json        # Full reviewed dataset (178 findings)
│   ├── reviewer_notes.md               # Human reviewer domain knowledge
│   ├── batches/                        # 68 batch files for agent analysis
│   └── *_fixes.json                    # Per-repo fix data (134 files)
├── review-tool/                        # Finding review and triage tool
│   ├── review_tool/
│   │   ├── app.py                      # FastAPI app factory
│   │   ├── cli.py                      # Click CLI (import, review, stats, export, serve, tui)
│   │   ├── config.py                   # Paths, round/repo mappings
│   │   ├── db.py                       # Schema, sync + async DB helpers
│   │   ├── models.py                   # Pydantic models
│   │   ├── parser.py                   # Markdown parser for validation reports
│   │   ├── tui.py                      # Textual TUI (two-panel review)
│   │   ├── routes/                     # API and page routes
│   │   ├── templates/                  # Jinja2 + htmx templates
│   │   └── static/                     # CSS
│   ├── review.db                       # SQLite database (178 findings, fully reviewed)
│   └── pyproject.toml
└── repos/                              # 142 cloned charm repos (not committed)
```

Note: The `repos/` directory contains 142 cloned charm repositories and is excluded from the committed version of this experiment due to size. To reproduce, use the `get-charms` tool from [github.com/tonyandrewmeyer/charm-analysis](https://github.com/tonyandrewmeyer/charm-analysis), which efficiently clones all repositories listed in `charms.csv`.

---

## Future Work

### CI, Documentation, and Test Fix Analysis

This analysis deliberately filtered to source-code fixes, excluding CI-only (GitHub Actions, tox), docs-only, and test-only changes from deep analysis. Of the 6,116 fix commits, 1,732 (28%) fell into these categories. Repeating the methodology on these excluded fixes could yield:

- **CI/GHA anti-patterns** -- recurring workflow bugs, insecure action pinning, flaky test handling
- **Test anti-patterns** -- common testing mistakes in Juju charm test suites (mock vs integration, fixture patterns, scenario testing pitfalls)
- **Documentation anti-patterns** -- stale docs, wrong API references, missing examples

A `charm-find-test-bugs` or `charm-find-ci-bugs` skill built from this data could complement `charm-find-bugs` for full-spectrum code review.

### Remaining Historical Batches

Of the 68 historical fix batches, 22 were deeply analysed (18 during initial skill construction + 4 during the historical batch analysis). The remaining 46 batches could be examined to find further patterns, though the historical batch analysis suggests diminishing returns -- the 4 batches examined confirmed existing patterns and yielded only 4 new anti-patterns (AP-066 to AP-069).

### Scaling to More Repos

41 of 142 repos (29%) have been validated. The remaining 101 repos include many smaller charms, multi-charm repos without `src/charm.py`, and SD-Core network functions. Running the skill against more repos would further validate its coverage, particularly for under-represented archetypes (VM/machine charms, Kubeflow multi-charm repos, ACME certificate automation).
