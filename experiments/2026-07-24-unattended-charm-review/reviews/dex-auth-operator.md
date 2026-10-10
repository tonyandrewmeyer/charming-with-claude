# dex-auth-operator

Dex Auth is a Kubernetes charm that runs [Dex](https://github.com/dexidp/dex), a federated OpenID Connect provider, as the authentication component of Charmed Kubeflow. It is a well-structured, actively-maintained operator with good test coverage (95% unit line coverage) and clean idempotent config handling. Deployment, config changes, and blocked/recovery transitions all worked as expected in testing. The main gaps are a missing `authorization_endpoint` in the OIDC relation data, no schema validation on the `connectors` config option, and no user-facing actions. A maintainer should first fix or validate the `authorization_endpoint` gap (it affects other charms' ability to consume this relation) and add basic validation for `connectors`.

| | |
|---|---|
| Repo | canonical/dex-auth-operator @ `f809bc1` (2026-05-29) |
| Charms | dex-auth |
| Substrate | k8s |
| Deployed | yes — concierge-k8s-4, 2.41/edge rev 815 (local HEAD is `f809bc1`, gap is 9 revisions / ~3 months) |
| Reviewed | 2026-08-20 |

## What it does

- Runs the Dex server as a Pebble workload in a Kubernetes pod
- Exposes `dex-oidc-config` (issuer URL), `metrics-endpoint`, `grafana-dashboard` relations
- Consumes `ingress`, `oidc-client`, `istio-ingress-route-unauthenticated`, `service-mesh`, `require-cmr-mesh`, `logging` relations
- Supports static username/password login and external connectors (GitHub, OIDC, LDAP, etc.)
- Configures its own Kubernetes Service (patched ports) and ambient mesh ingress

## Deployment log

### Deploy (concierge-k8s-4, 2.41/edge rev 815)
```bash
juju add-model rv-dex-k8s k8s --controller concierge-k8s-4
juju deploy dex-auth --channel 2.41/edge --model rv-dex-k8s \
  --config static-username=admin --config static-password=testing123 --trust
```
- Deploy completed: ~25s
- Pod running: ~40s
- Active: ~60s
- Hook sequence: install → leader-elected → dex-pebble-ready → config-changed → start

### Lifecycle tests

| Action | Result |
|---|---|
| `juju config issuer-url=...` | Config applied, Dex config updated, Dex restarted — ✅ |
| `juju config port=6666` | Dex config updated with `web.http: 0.0.0.0:6666`, K8s Service updated to port 6666 — ✅ |
| Same config re-applied (`issuer-url` same value) | No restart — ✅ idempotent |
| `enable-password-db=false` (no connectors) | `BlockedStatus("Please add a connectors configuration to proceed without a static login.")` — ✅ |
| Re-enable `enable-password-db=true` | Recovered to `ActiveStatus` — ✅ |
| `juju run dex-auth/0 show-status-log` | `ERROR: no actions defined for charm dex-auth` — no `actions.yaml` |

### Observed behaviour

- **Deploy timing**: ~60s from deploy to ActiveStatus on k8s/4.0.12
- **Config change**: ~15s from config change to ActiveStatus recovery
- **Idempotency**: Setting the same value twice does NOT restart the workload — Dex config is compared before pushing
- **Failure mode**: Disabling static login with no connectors → clear `BlockedStatus` with actionable message
- **Hook count**: install (1), leader-elected (1), dex-pebble-ready (1), config-changed (1), start (1) = 5 hooks for initial deploy
- **Hook count (config change)**: config-changed only — only the hooks registered in `__init__` fire
- **K8s Service**: patched correctly on deploy and on config change (both port and targetPort update); this directly contradicts open issue #210, which appears fixed as of the deployed/local revisions tested
- **Pebble**: Dex running as a non-root user (uid 584792), logs show `listening on` for both HTTP (5556/6666) and telemetry (5558) ports
- **No actions**: Zero actions defined; `actions.yaml` does not exist

### Resource use

- Pod: `dex-auth-0` with 2/2 containers (dex workload + Juju unit agent)
- Dex image: `charmedkubeflow/dex:2.41.1-1d3fe19`
- Container security context: non-root (uid/gid 584792)

## Findings

### `authorization_endpoint` not provided in `dex-oidc-config` relation data
- **Severity**: medium
- **Kind**: bug
- **Where**: `lib/charms/dex_auth/v0/dex_oidc_config.py:120`
- **Evidence**: `send_data` only writes `"issuer-url": issuer_url`; `REQUIRED_ATTRIBUTES = ["issuer-url"]` at line 120. The library exposes no `authorization_endpoint` field.
- **Impact**: Clients on the `dex-oidc-config` relation (e.g. `oidc-gatekeeper`) only get `issuer-url` and must fetch `/.well-known/openid-configuration` from Dex at runtime to learn the authorization endpoint. If a client needs this before ingress to Dex is up, it has no way to get it from the relation. Whether requirer charms actually need it at relation-join time (vs. doing OIDC discovery later) is unverified.
- **Fix**: Add `authorization_endpoint` to `DexOidcConfigObject` and include it in `send_data`, computed as `{issuer_url.rstrip('/')}/authorization`.
- **Linter rule**: not established — requires domain knowledge of OIDC, not mechanically checkable.

### `connectors` config has no schema validation
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:309`
- **Evidence**: `connectors = yaml.safe_load(self.model.config["connectors"])` is parsed but never validated. If a user supplies a non-list string (e.g. `connectors: not-a-yaml-list`), `yaml.safe_load` returns a truthy string, so `if not enable_password_db and not connectors` evaluates `True` and the `BlockedStatus` guard is bypassed. Related open issue #42 (since 2022) documents that the expected connectors format is non-intuitive.
- **Impact**: Invalid connector config reaches Dex with no charm-level validation error; Dex then fails or misbehaves with no clear signal from Juju.
- **Fix**: After `yaml.safe_load`, validate: `if connectors is not None and not isinstance(connectors, (list, dict)): raise ErrorWithStatus("connectors must be a YAML list or null", BlockedStatus)`.
- **Linter rule**: not established — not mechanically checkable without a schema.

### Unit test coverage gaps — 5% uncovered lines
- **Severity**: medium
- **Kind**: test-gap
- **Where**: `src/charm.py:258-261` (`_get_interface` body), `src/charm.py:304`, `src/charm.py:359`
- **Evidence**: Coverage XML shows missed lines 258–261 (the entire `_get_interface` method, including its `NoVersionsListed`/`NoCompatibleVersions` exception handlers), line 304 (`oidc_client_info = list(oidc.get_data().values())`, reached only when `_generate_dex_auth_config` runs unmocked), and line 359 (`if __name__ == "__main__":`, trivial).
- **Impact**: `_get_interface`'s exception paths are the primary error handling for relation-version mismatches (`NoCompatibleVersions → BlockedStatus`) and missing relation data (`NoVersionsListed → WaitingStatus`) — realistic failure modes with zero unit test coverage.
- **Fix**: Add tests for `_get_interface` under `NoCompatibleVersions` and `NoVersionsListed`, and a test for `_generate_dex_auth_config` with an active oidc-client relation that does not mock `_update_layer`.
- **Linter rule**: not established.

### No `actions.yaml` — no user-facing actions
- **Severity**: low
- **Kind**: ux
- **Where**: `src/charm.py` (whole file); `actions.yaml` absent from repo
- **Evidence**: `juju run dex-auth/0 show-status-log` → `ERROR: no actions defined for charm dex-auth`. The charm defines zero actions.
- **Impact**: Operators typically expect actions like `get-credentials` or `get-oidc-config` on auth charms; absence is a usability gap, not a correctness bug.
- **Fix**: Add at minimum a `get-oidc-config` action returning the issuer URL, OIDC discovery URL, and connector type.
- **Linter rule**: `charmcraft analyze` could warn when a charm has no `actions.yaml` but non-trivial relations.

### Grafana dashboard directory is empty
- **Severity**: low
- **Kind**: ux
- **Where**: `src/grafana_dashboards/` (contains only `.gitkeep`)
- **Evidence**: `GrafanaDashboardProvider` (from `charms.grafana_k8s.v0.grafana_dashboard`) auto-discovers dashboards from `src/grafana_dashboards/*.json` but finds none, despite the charm declaring `provides: grafana-dashboard` and initializing the provider in `__init__`.
- **Impact**: The `grafana-dashboard` relation exists but provides no dashboard data. Integration tests pass `dashboard=True` to `deploy_and_assert_grafana_agent`, which likely only asserts the relation exists rather than that a dashboard is delivered.
- **Fix**: Add a Dex-specific Grafana dashboard JSON covering auth codes, token grants, and connector latency.
- **Linter rule**: `charmcraft analyze` could warn when `provides.grafana-dashboard` is declared but no dashboard files exist.

### Deprecated `public-url` config not removed
- **Severity**: low
- **Kind**: docs
- **Where**: `config.yaml`, `src/charm.py:130-140`
- **Evidence**: `config.yaml` marks `public-url` as "DEPRECATED... This configuration option will be removed soon." Code still handles it as a fallback for `_issuer_url`. The deprecation language predates related issue #210 (July 2024) and is now over a year old.
- **Impact**: Stale "removal soon" language erodes trust in future deprecation notices.
- **Fix**: Either remove `public-url` (breaking change, needs migration path) or give a concrete removal date and keep it until then.
- **Linter rule**: not established.

### `ruff I001`: import block unsorted
- **Severity**: nit
- **Kind**: lint
- **Where**: `src/charm.py:5-36`
- **Evidence**: `ruff check src/` reports `I001 Import block is un-sorted or un-formatted` across the multi-line import groups (`charms.istio_beacon_k8s...`, `charms.istio_ingress_k8s...`, `charms.loki_k8s...`).
- **Fix**: `isort src/charm.py`.
- **Linter rule**: `ruff I001`, auto-fixable with `--fix`.

### `ruff UP032`: `.format()` instead of f-string
- **Severity**: nit
- **Kind**: lint
- **Where**: `src/charm.py:75`
- **Evidence**: `"static_configs": [{"targets": ["*:{}".format(METRICS_PORT)]}]` mixes legacy `.format()` with the rest of the codebase's f-string style.
- **Fix**: `"static_configs": [{"targets": [f"*:{METRICS_PORT}"]}]`
- **Linter rule**: `ruff UP032`, auto-fixable.

## Worth copying

- **Clean error-with-status pattern** (`src/charm.py:243-248`): `_check_leader`/`_check_container_connection` raise `ErrorWithStatus(status, message)` instead of setting status inline; `main()` catches it in one try/except, sets status, logs, returns.
- **Config-change idempotency** (`src/charm.py:199-205`): `_update_layer` compares generated Dex config against on-disk config before pushing, avoiding unnecessary Pebble restarts.
- **Explicit blocked-status messages** (`src/charm.py:319-322`): `"Please add a connectors configuration to proceed without a static login."` — actionable, unlike generic `BlockedStatus("Error")`.
- **`KubernetesServicePatch` for multi-port service** (`src/charm.py:62-65`): exposes both the Dex HTTP port and metrics port dynamically from config, rather than a fixed single-port Service.
- **Service mesh integration with leader guard** (`src/charm.py:155-175`): `_ambient_mesh_ingress()` returns early on non-leader units, avoiding spurious errors.
- **OWASP event logging on password change** (`src/charm.py:51`): security event emission on static password change is good practice for auth charms.

## Common-practice notes

- Standard k8s charm layout (`src/charm.py`, `lib/charms/`, `metadata.yaml`, `config.yaml`); uses `ops.framework.StoredState` correctly.
- Uses `charmed-kubeflow-chisme` for shared patterns (service patch, log forwarding).
- `lib/charms/dex_auth/v0/dex_oidc_config.py` has `LIBAPI = 0`, `LIBPATCH = 1` — correct convention.
- `charmcraft.yaml` uses the `poetry` plugin with a custom `poetry-deps` part installing Rust via rustup, needed to build `cryptography` on older Ubuntu bases — complex but correct.
- CI uses `canonical/data-platform-workflows` and `canonical/charmed-kubeflow-workflows`; runs lint, unit, integration (with Selenium browser tests), and ambient (Cilium mesh) integration tests.
- Terraform module is complete: exposes `provides`/`requires` maps as outputs, sets `trust = true` in `main.tf`.
- Unit tests use `ops.testing.Harness`, which is deprecated in favour of `ops.Scenario` (confirmed by `PendingDeprecationWarning`s in the test run).
- `DexOidcConfigProvider` broadcasts `issuer-url` on `relation_created`, `leader_elected`, and `config_changed` — correct pattern for handling relations created before config is set.

## Tests

### Unit tests
- **Result**: 28 passed, 0 failed, 0 skipped (`tox -e unit`)
- **Coverage**: 95% line coverage; missing ranges are `_get_interface` (258-261), line 304, line 359 (see findings above)
- **Frame**: `ops.testing.Harness` (deprecated but functional); mocks `KubernetesServicePatch` and `LogForwarder`

### Integration tests
- **Location**: `tests/integration/test_charm.py`, `test_charm_ambient.py`, `test_upgrade_charm.py`
- **Scope**: build-and-deploy, StatefulSet readiness, relations with istio/oidc-gatekeeper/kubeflow*, Grafana agent (metrics/dashboard/logging), Selenium browser login test, alert rules, metrics endpoint, container security context
- **Ambient mesh**: Cilium-based service mesh test with forward-auth
- **Upgrade test**: builds charm, deploys from charmhub, upgrades to local build
- **Note**: integration tests build the charm locally (`ops_test.build_charm(".")`) rather than testing the published charm — appropriate for local-change testing.

### Lint
- `tox -e lint`: passes (codespell, pflake8, isort, black)
- Standalone `ruff check src/`: 2 findings (`I001`, `UP032`), as noted above

## Docs

- **README.md**: heavy on Kubeflow marketing, minimal on operational detail (essentially `juju deploy dex-auth`); contributing section is solid.
- **charmhub description**: matches actual charm function.
- **CONTRIBUTING.md**: excellent — covers poetry, tox environments, local dev, CI workflow.
- **Terraform README**: clear, covers both `juju_model` resource and data source usage.
- **Gap**: no public doc on configuring Dex connectors (open issue #216, since 2024).

## Open questions

1. **Issue #210 (port config not applied to Dex)**: observed behaviour (port 6666 config → Dex listens on 6666, K8s Service updated) contradicts the issue. Likely fixed between rev 806 and rev 815, or the report was based on a misunderstanding of Dex's config-file vs CLI port handling. No action needed unless the currently deployed revision shows different behaviour.
2. **Issue #303 (API rate limit stuck)**: the charm has explicit handling for Pebble "Too Many Requests" (`ErrorWithStatus` → `WaitingStatus`), but it's unclear whether `update-status` alone can retry the underlying Pebble restart, or whether a subsequent event (config/relation change) is required to unstick it. (unverified)
3. **`authorization_endpoint`**: unclear whether requirer charms like `oidc-gatekeeper` do OIDC discovery at runtime (in which case the missing field is harmless) or need it at relation-join time before ingress is configured (in which case it's a real gap). (unverified)
