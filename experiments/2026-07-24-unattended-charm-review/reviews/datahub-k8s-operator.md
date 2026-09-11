# datahub-k8s

A well-architected Kubernetes charm for DataHub (Canonical Commercial Systems). Manages three workload containers (GMS, Frontend, Actions) with a stateless reconciler pattern and integrations with PostgreSQL, Kafka, OpenSearch, Trino, OAuth/OIDC, Traefik, and COS. Code quality is high — clean static analysis (pylint 10/10, mypy clean, bandit clean), no `defer()`/`StoredState`, and one of the most thorough integration test suites seen in the ecosystem. The charm is not yet production-safe on Juju 4.x: a missing default on a required Pydantic config field crashes the charm on first deploy instead of showing a blocked status. A maintainer should fix that field first, then address the fire-and-forget `reindex` action.

| | |
|---|---|
| Repo | canonical/datahub-k8s-operator @ `1d9272d` (2026-07-10) |
| Charms | datahub-k8s |
| Substrate | k8s |
| Deployed | yes — concierge-k8s-3 (Juju 3.6.25), latest/edge rev 29; full stack reached active, actions exercised, failure injections tested |
| Reviewed | 2026-07-26 |

## What it does

Deploys and manages a full DataHub instance on Kubernetes. DataHub is a metadata catalog for data discovery, observability, and governance. The charm manages three containers: `datahub-gms` (backend API), `datahub-frontend` (web UI), and `datahub-actions` (async event processing). It integrates with PostgreSQL for metadata storage, Kafka for messaging/ingestion, OpenSearch for search indices, Trino for automatic metadata ingestion source management, and OAuth/OIDC providers for SSO. Supports Traefik ingress (separate frontend and GMS endpoints), COS metrics/dashboards/logging, proxy configuration, multi-deployment topic/index prefix sharing, and ships Terraform modules for charm-level and full-product deployment. Provides `get-password` and `reindex` actions.

## Deployment log

**Juju 3.6 (concierge-k8s-3, rev 29) — primary deployment:**
```sh
juju add-model rv-deep-k8s -c concierge-k8s-3
juju switch concierge-k8s-3:rv-deep-k8s
juju deploy datahub-k8s --channel edge --trust
juju deploy postgresql-k8s --channel 14/stable --trust
juju deploy kafka-k8s --channel 3/stable --trust
juju deploy zookeeper-k8s --channel 3/stable --trust
juju relate kafka-k8s zookeeper-k8s

# Encryption secret:
juju add-secret dh-enc 'gms-key=KEY123' 'frontend-key=KEY456'
juju grant-secret dh-enc datahub-k8s
juju config datahub-k8s encryption-keys-secret-id=secret:l09eels8kfsc4ejndjh0
# → blocked: missing required relation(s): db, kafka, opensearch

# ~5 min later:
juju relate datahub-k8s postgresql-k8s
juju relate datahub-k8s kafka-k8s
# → blocked: missing required relation(s): opensearch
```

Timeline: PostgreSQL 14.23 and Kafka 3.9.0/ZK 3.9.2 all reached active by 00:33:11. Config-change and relation-removal fault injections were exercised at this point (see Observed behaviour).

**OpenSearch on LXD (concierge-lxd):**
```sh
juju add-model rv-deep-os -c concierge-lxd
juju deploy opensearch --channel 2/edge -n 2
juju deploy self-signed-certificates
juju relate opensearch self-signed-certificates
# → SSC active after ~3 min; OpenSearch still "Installing OpenSearch..." after 20+ min
```

**OpenSearch install barriers:**
- Deployed `opensearch --channel 2/edge -n 2` + `self-signed-certificates --channel 1/stable`
- SSC active after ~3 min
- OpenSearch "Installing OpenSearch..." for ~20 min (apt/dpkg install time on LXD)
- Then blocked: "Missing requirements: vm.swappiness should be at most 0" — required `sudo sysctl -w vm.swappiness=0` on the host
- After the swappiness fix, OpenSearch went active (~22 min total)

**Cross-model integration:**
```sh
juju offer opensearch:opensearch-client os-client
juju consume -m <k8s-model> concierge-lxd:admin/rv-deep-os.os-client
juju relate datahub-k8s os-client
# → data published → charm runs backend bootstrap → Active within ~1 min
```

**Juju 4.x (concierge-k8s-4, rev 29) — confirmatory test:**
```sh
juju deploy datahub-k8s --channel edge --trust
# → hook failed: "config-changed" — Pydantic ValidationError: encryption_keys_secret_id Field required
```
Reproduced the Pydantic crash (Finding 1). After configuring the secret and resolving, the charm went to `blocked: missing required relation(s): db, kafka, opensearch` — same as on 3.6.

## Observed behaviour

### Full deployment
- Total time to active: ~28 min from deploy, dominated by the OpenSearch install (~20 min on LXD). PostgreSQL ~7 min, Kafka ~7 min, ZooKeeper ~6 min.
- One-time bootstrap: PostgreSQL setup + OpenSearch index creation + `SystemUpdate` JVM completed in ~46s total (00:55:12–00:56:00). The backend-provisioned gate skipped bootstrap on subsequent reconciles — re-relating OpenSearch after removal returned to active in <15s.
- Pebble-ready event sequence: three pebble-ready events fire (actions, frontend, gms) during install; two pebble-check-failed events follow because workload containers aren't started yet — harmless.
- Pod resources: 4 containers (charm + actions + frontend + gms), ~3 CPU cores, ~1.1 GB RAM total.

### Lifecycle and recovery
- Blocked → active: when OpenSearch data arrived, the charm ran DB init → OpenSearch init → `SystemUpdate` → Pebble replan → `ActiveStatus`, fully automated.
- Bad config (`trino-patterns='not-json'`): `BlockedStatus: invalid 'trino-patterns' config: Expecting value: line 1 column 1 (char 0)`. Restoring valid JSON returned to active in ~15s.
- Relation removal (opensearch): active → `BlockedStatus: missing required relation(s): opensearch`. Re-adding returned to active. Services stayed running throughout.
- Relation removal (kafka) while blocked on opensearch: correctly updated to `missing required relation(s): kafka, opensearch`.
- Pebble service stop: stopping `datahub-gms` via `pebble stop` and running `reconcile()` restored the service — Pebble's `on-check-failure: restart` and the reconciler's replan both contribute.
- No `defer()` usage anywhere in the charm.

### Actions
- `get-password`: returned a 24-char URL-safe secret (e.g. `Tfd3zpVU1kItP7iVMJiJBfVE-VfsOGEX`); same password on all units (single app-owned secret).
- `reindex`: returned `result: command succeeded` immediately, message `Observe reindexing progress on 'datahub-gms' container logs.` — confirms fire-and-forget pattern (Finding 2).

### Pebble plan contents
- GMS container: service `datahub-gms` enabled/active, 70+ environment variables (DB/Kafka/OpenSearch connection details), health check at `http://localhost:8080/health/live`, 10s period, 30-failure threshold.
- Frontend container: service `datahub-frontend` enabled/active.
- Actions container: service `datahub-actions` enabled/active.

### What could not be observed
- Scale-up/scale-down behaviour (would need additional units).
- `juju refresh` between revisions (only one revision published).
- Traefik ingress routing, OAuth integration, COS metrics (optional integrations) beyond what CI exercises.

## Findings

### Pydantic `encryption_keys_secret_id` crash on fresh deploy (Juju 4.x)
- **Severity**: critical
- **Kind**: bug
- **Where**: `src/structured_config.py:39`, triggered via `src/charm.py:384`
- **Evidence**: Deploy on Juju 4.0.5 with no config set:
  ```
  pydantic_core._pydantic_core.ValidationError: 1 validation error for CharmConfig
  encryption_keys_secret_id
    Field required [type=missing, input_value={'trino_patterns': ..., input_type=dict]
  ```
  The field is `encryption_keys_secret_id: str` (line 39) with no default. On Juju 4.x the config dict omits the key entirely, so Pydantic raises `ValidationError` on model construction. On Juju 3.6.25 the config dict includes the key as an empty string, which the `blank_string` validator converts to `None`, so the crash doesn't occur there.
- **Impact**: A fresh deploy on Juju 4.x crashes with "hook failed" instead of the intended `BlockedStatus("missing required configurations: encryption-keys-secret-id")`. The operator sees a raw traceback with no guidance.
- **Fix**: `encryption_keys_secret_id: Optional[str] = None`
- **Linter rule**: Mechanically checkable — "Pydantic model field with no default value in a `BaseConfigModel` used as `config_type` accessed via `self.config`"

### `reindex` action does not wait for process completion
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/services.py:1046-1052`, action handler `src/charm.py:232`
- **Evidence**:
  ```python
  container.exec(
      command,
      encoding="utf-8",
      environment=environment,
      timeout=180,
  )
  logger.info("Reindex process started asynchronously.")
  return True
  ```
  `container.exec()` returns a process object; `.wait_output()` is never called. `timeout=180` only bounds how long `exec()` waits to *launch* the process, not how long it runs. The action always reports `"command succeeded"` regardless of exit status.
- **Impact**: An operator running `juju run datahub-k8s/leader reindex` after a migration sees success and moves on, while the reindex may have crashed silently. The action's own message ("observe container logs") confirms it cannot detect a startup failure.
- **Fix**:
  ```python
  process = container.exec(command, encoding="utf-8", environment=environment, timeout=180)
  stdout, stderr = process.wait_output()
  ```
  or use a longer timeout and catch `ChangeError` on failure.
- **Linter rule**: Mechanically checkable — "call to `container.exec()` without subsequent `.wait_output()` or `.wait()` in a non-background context"

### OpenSearch deployment experience is painful
- **Severity**: medium
- **Kind**: ux / docs
- **Where**: deployment documentation, cross-model setup
- **Evidence**: The full DataHub stack requires OpenSearch on LXD machines (no `opensearch-k8s` charm exists). Install took ~22 minutes and required manual host-level `sysctl` configuration (`vm.swappiness=0`) to pass the charm's requirements check. The integration test conftest sets this via `sudo sysctl` before deploying, acknowledging the requirement, but it is not called out for operators following the README.
- **Impact**: A first-time operator will watch OpenSearch sit at "Installing" for 20+ minutes, then get blocked on swappiness with no in-charm guidance.
- **Fix**: Document `sudo sysctl -w vm.swappiness=0 vm.max_map_count=262144` as a prerequisite in the README, or ship a `pre-deploy-setup.sh` script.
- **Linter rule**: not established

### GraphQL module has near-zero unit test coverage
- **Severity**: medium
- **Kind**: test-gap
- **Where**: `src/graphql.py` (83 statements, 15% covered)
- **Evidence**: All DataHub GraphQL API functions (`create_access_token`, `list_secrets`, `ensure_secret`, `list_ingestion_sources`, `create/update/delete_ingestion_source`, `delete_secret`) are untested at unit level. They are exercised only by the Trino integration test, which requires a full active deployment and runs only in CI.
- **Impact**: Refactoring the GraphQL module carries real risk with no fast feedback loop.
- **Fix**: Add scenario-based unit tests mocking `requests.post` for each GraphQL function.
- **Linter rule**: Coverage threshold — flag business-logic modules below 50% coverage (excluding trivial constants/config modules).

### No unit tests for failure-mode paths
- **Severity**: medium
- **Kind**: test-gap
- **Where**: `src/charm.py` (`reconcile()` main flow, `_on_update_status`, `_on_reindex_action`)
- **Evidence**: No tests exercise: missing/unreachable `encryption-keys-secret-id` secret, corrupted secret content (missing `gms-key`/`frontend-key`), removal of a required relation while active, killing the workload process and observing recovery, invalid JSON in `trino-patterns` while otherwise healthy, or refresh with different encryption keys. `reconcile()`'s add_layer/replan paths and the `_on_update_status` health-check loop are also untested at unit level; the `base_state` test fixture always includes `encryption_keys_secret_id`, which is why the Pydantic crash (Finding 1) went uncaught.
- **Impact**: These are the most likely operational failure modes; a regression in error handling would go undetected between the (slow, CI-only) integration test runs.
- **Fix**: Add scenario tests for each failure mode, including one that constructs `CharmConfig` without `encryption_keys_secret_id`.
- **Linter rule**: not established

### Early-return on non-connectable container skips remaining services
- **Severity**: low
- **Kind**: bug
- **Where**: `src/charm.py:525-530` (initialization loop), `src/charm.py:537-544` (replan loop)
- **Evidence**:
  ```python
  for service in SERVICES:  # [GMSService, FrontendService, ActionsService]
      container = self.unit.get_container(service.name)
      if not container.can_connect():
          logger.info("Cannot connect to service '%s', skipping initialization", service.name)
          return  # exits the entire loop; remaining services never processed
      service.run_initialization(context)
  ```
  If `datahub-actions` is slow to connect while GMS and Frontend are ready, neither of the latter is initialized until Actions connects. Same pattern in the replan loop. Since all three containers come up in the same pod, this is unlikely to cause real problems in practice.
- **Fix**: Replace `return` with `continue` in both loops; track whether all services are connectable to decide the final status.
- **Linter rule**: not established — requires semantic understanding of loop intent

### Kafka JAAS config embeds password without escaping
- **Severity**: low
- **Kind**: bug
- **Where**: `src/services.py:403-405` (Frontend), `src/services.py:634-636` (GMS), `src/services.py:1006-1008` (Upgrade)
- **Evidence**: All three sites build the same string:
  ```python
  "KAFKA_PROPERTIES_SASL_JAAS_CONFIG": (  # or SPRING_KAFKA_PROPERTIES_SASL_JAAS_CONFIG
      "org.apache.kafka.common.security.scram.ScramLoginModule required "
      f'username="{kafka_conn["username"]}" password="{kafka_conn["password"]}";'
  ),
  ```
  If the Kafka password contains a double-quote character, the JAAS config string becomes malformed. `data_platform_libs` generates alphanumeric passwords, so this is unlikely to trigger, and there is no validation or escaping.
- **Fix**: Escape special characters before embedding, or validate that credentials are alphanumeric.
- **Linter rule**: not established — requires knowledge of the JAAS config format and provenance of the fields

### `is_down` handling in `_on_update_status` is hard to reason about
- **Severity**: low
- **Kind**: bug
- **Where**: `src/charm.py:298-355`
- **Evidence**: The health-check loop `break`s on `is_invalid` (a replan will fix everything) but `continue`s on `is_down` to keep checking other services. Traced through, the logic is correct — if service 1 is down and service 2 is invalid, service 2 is still reached and `is_invalid` triggers the `break` — but the control flow requires careful tracing to confirm.
- **Fix**: Refactor to check all services and aggregate status before acting once, or add a comment explaining the precedence.
- **Linter rule**: not established

### Fragile secret ID matching with `str.endswith()`
- **Severity**: nit
- **Kind**: bug
- **Where**: `src/charm.py:282`
- **Evidence**:
  ```python
  id_match = encryption_keys_secret_id and event.secret.id.endswith(encryption_keys_secret_id)
  ```
  If the config value is `secret:abc`, a Juju secret ID `secret:xyzabc` would also match. Extremely unlikely in practice since Juju secret IDs use random suffixes, but a direct comparison is trivially safer.
- **Fix**: Use `event.secret.id == encryption_keys_secret_id`, or strip the `secret:` prefix from both before comparing.
- **Linter rule**: Can flag `endswith` used against Juju secret IDs.

### `random.shuffle` used alongside `secrets` module in password generation
- **Severity**: nit
- **Kind**: lint
- **Where**: `src/utils.py:74`
- **Evidence**: `random.shuffle(chars)` in `generate_secret()`, which otherwise uses `secrets.choice()` for character selection. Doesn't meaningfully compromise entropy (characters were already chosen via `secrets`), but mixing `random` and `secrets` invites auditor scrutiny.
- **Fix**: Use `secrets.SystemRandom().shuffle(chars)`.
- **Linter rule**: Mechanically checkable — "use of `random.shuffle` in a function whose name/purpose indicates security-sensitive randomness"

## Worth copying

- **Stateless reconciler pattern** (`src/charm.py:502-555`): every hook delegates to a single `reconcile()` method that reads current state, computes desired state, and applies it. No `StoredState`, no `defer()`, no state cached beyond secret references in peer relation data. Connection details are read live from relation databags on each reconcile.
- **Backend-provisioned gate** (`src/services.py:756-802`): `_backend_is_provisioned()` queries PostgreSQL directly for the root auth policy (`SELECT 1 FROM metadata_aspect_v2 WHERE urn = 'urn:li:dataHubPolicy:0'`), gating the expensive `SystemUpdate` JVM bootstrap (~10 min) on the backend's own state rather than workload liveness. A rebuilt pod on a provisioned backend skips the bootstrap entirely.
- **`ServiceContext` dataclass** (`src/services.py:160-175`): a single lightweight context object passed to all service methods instead of threading the charm instance through every call. Makes testing trivial — mock the context, not the charm.
- **Stateless secret lookup by label** (`src/charm.py:439-469`): admin password and system client secret are stored as Juju secrets with deterministic labels (`datahub-init-pwd`, `datahub-system-client-secret`). Any unit can look them up without peer relation data; the leader creates them once, others read by label.
- **`log_event_handler` decorator** (`src/log.py`): every observer is wrapped with `@log_event_handler(logger)`, logging entry/exit with timing — makes debug-log tracing trivial.
- **Pebble health check with long threshold** (`src/charm.py:64-82`, `src/literals.py:15-22`): `HEALTHCHECK_FAILURE_THRESHOLD = 30` at 10s period gives ~5 min before restart — long enough for a cold JVM to start, short enough to rescue a genuinely hung process.
- **Truststore self-healing** (`src/services.py:41-79`): `_import_certificates_to_truststore` deletes existing aliases before importing, so a rotated CA is always refreshed; runs unconditionally on every reconcile.
- **Trino auth retry** (`src/relations/trino.py:525-559`): `_prepare_ingestion_state` retries on `AuthenticationError` by creating a fresh access token, persisting it, and retrying the entire GraphQL operation atomically.
- **Comprehensive `charmcraft.yaml`**: all metadata (relations, containers, resources, config, actions) in a single file, using `plugin: uv` with `uv-groups: [charmlibs-pydeps]`.
- **Makefile with full dev workflow**: build (charm + rocks), test (unit, static, integration), deploy-local, clean-dev, and create-secret targets, well documented via `make help`. The `create-secret` target generates encryption keys with `openssl rand -base64 32`.
- **Terraform modules** (`terraform/charm/`, `terraform/product/`): ships both a per-charm module and a full-product module deploying the entire stack — rare and valuable.
- **Copilot instructions** (`.github/instructions/`): five markdown files with coding guidelines for AI-assisted development.
- **Trino ingestion schedule stability** (`src/relations/trino.py`): `_update_ingestion_source` preserves the original schedule from the DataHub API rather than regenerating a random one; patterns from existing sources are preserved rather than overwritten by current config.

## Common-practice notes

- Follows ecosystem conventions: `data_platform_libs` for database/Kafka/OpenSearch, `traefik_k8s.ingress` for ingress, `hydra.oauth` for OAuth, COS libraries for observability. Standard `src/` layout with a `relations/` sub-package, `TypedCharmBase` with `BaseConfigModel`.
- `charmcraft.yaml` is the single source of truth (no separate `metadata.yaml`), correctly declaring relations, containers, resources, config, and actions.
- Three OCI image resources declared in `charmcraft.yaml`; `datahub_rocks/` contains `rockcraft.yaml` files and startup/init scripts. Uses `bare` base with `ubuntu@22.04` build-base.
- Uses `plugin: uv` with `uv-groups: [charmlibs-pydeps]`, plus `uv-venv-runner` in `tox.ini` — fully modern toolchain.
- No `StoredState` or `defer()`. Secret IDs are stored in peer relation data as references to Juju-managed secrets, not as state.
- `trino-patterns` is modelled as a JSON string (Juju config doesn't support nested objects), validated in `_check_state()`. The description accurately notes pattern changes only affect future catalogs, not existing ingestion sources.
- `assumes: juju >= 3.4` is correct for the features used (Juju secrets, structured config), but the Pydantic crash on Juju 4.x is a compatibility gap not covered by this constraint.
- Integration tests use `jubilant` rather than `pytest-operator` — newer, well suited to hybrid-cloud testing.

## Tests

### Unit tests (92 pass, 63% coverage)
- Framework: `ops.testing` (scenario/state-transition).
- Well covered: config validation, secret handling, relation connection properties, service environment compilation, Trino ingestion reconciliation (CRUD + auth retry), Pebble layer construction.
- Coverage gaps: `graphql.py` (15%), `services.py` (58% — reindex, upgrade, postgres/opensearch/truststore init paths untested), `charm.py` (56% — `reconcile()` main flow, update-status loop, reindex action untested), `trino.py` (70% — some reconciliation branches missing), `utils.py` (69% — `split_certificates`, `get_from_optional_dict` untested).

### Integration tests (7 tests, run in CI)
- Framework: `jubilant` + `pytest` on hybrid LXD + Canonical K8s cloud, using `canonical/operator-workflows` (`integration_test.yaml`) across `test_charm.py`, `test_upgrade.py`, `test_scaling.py`.
- Matrix: solo deploy (BlockedStatus), full stack deploy + login + GraphQL search + workload version, reindex action, ingress routing, OAuth+TLS block-and-recover, 1→3→1 scaling, edge→local refresh.
- Exceptionally thorough — exercises real authentication, GraphQL queries, ingress routing, TLS, scaling, and upgrade paths.
- Not run locally (requires a full hybrid cloud environment with locally-built rocks).

### Static analysis
- Bandit: clean, 0 issues (all `# nosec` annotations reviewed and appropriate).
- Pylint: 10.00/10.
- Mypy: clean, 0 issues across 27 source files.
- Codespell: clean.
- pydocstyle: clean.
- isort / black: clean, 27 files unchanged.

## Docs

- **README** (`README.md`, ~14KB): comprehensive — architecture, deployment dependencies, SSO, Terraform, proxies, migration, ingress, Trino integration, troubleshooting. Accurate against observed behaviour.
- **CONTRIBUTING.md** (~10KB): detailed developer setup (uv, tox, LXD, charmcraft, rockcraft), code quality commands, testing instructions — above average.
- **Terraform docs**: `terraform/charm/README.md` (1.6KB) and `terraform/product/README.md` (4.7KB), both present and useful.
- **Charmhub page**: thorough description in `charmcraft.yaml`; the marketing line "core component of the Canonical Data Mesh solution" is aspirational.
- **Doc/reality gap**: the README describes a cross-model deployment (Kafka/PostgreSQL/OpenSearch on LXD, DataHub on K8s) matching the integration test setup. The k8s-native path (`postgresql-k8s`/`kafka-k8s`) worked fine in this deployment but is not separately documented.
- **`.github/instructions/`**: five markdown files with coding guidelines for AI-assisted development.

## Open questions

1. **Is the `reindex` action intentionally fire-and-forget?** Confirmed — the code logs "Reindex process started asynchronously" and returns immediately. The integration test likely only covers the happy path where the JVM starts quickly; a failed JVM startup would go undetected.
2. **Pydantic crash is reproducible only on Juju 4.x**: confirmed on Juju 4.0.5, not on 3.6.25. On 3.6 the config dict includes an empty string (converted to `None` via `blank_string`); on 4.x the key is absent entirely. Worth a Juju bug report — config key presence should behave consistently across versions.
3. **Kafka/OpenSearch topic and index orphans on prefix change**: if `kafka-topic-prefix` or `opensearch-index-prefix` is changed, the charm creates new topics/indices but leaves old ones behind. Not documented as a limitation. (unverified — not directly exercised in this deployment)
4. **Health check plan comparison robustness**: `_on_update_status` compares `dict(container.get_plan().to_dict()) != expected_plan` (`src/charm.py:340`), working around a Pebble dict-subclass comparison quirk. If another process added layers to the same container this comparison would always evaluate false, potentially causing a reconcile loop — but the container is dedicated to this charm, so it's fine in practice.
