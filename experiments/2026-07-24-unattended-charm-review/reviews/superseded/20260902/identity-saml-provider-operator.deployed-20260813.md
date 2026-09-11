# identity-saml-provider-operator

A Kubernetes sidecar charm that runs the Identity SAML Provider — a SAML-to-OIDC bridge for Ory Hydra. It requires PostgreSQL, Traefik ingress, and a Hydra OAuth provider, and accepts an optional CA via `certificate_transfer`. Code quality is genuinely high: a clean reconciler ("holistic handler") pattern, protocol-based config sources, thorough unit tests (104 passing, 97% coverage), and good status reporting. The serious defect is that **removing the `oauth` relation leaves the charm blocked with a correct-looking message while the workload crash-loops** (confirmed live, matches open issue #72) — fix that first. Behind it sit a `startup: disabled` pebble override that only works by accident of ephemeral storage, a cluster-wide `SUPERUSER` database grant, a failed auto-migration that leaves a permanently misleading "Waiting for database migration" status, and per-hook overhead (uncached `version` exec, file pulls, a k8s API patch) repeated on every hook including the 5-minute `update-status`.

| | |
|---|---|
| Repo | canonical/identity-saml-provider-operator @ e64cb6c (2026-07-23) |
| Charms | identity-saml-provider-operator |
| Substrate | k8s |
| Deployed | yes — concierge-k8s-3 (Juju 3.6.25), charmhub `latest/edge` rev 3, active; partial on concierge-k8s-4 (Juju 4.0.5), blocked (see below) |
| Reviewed | 2026-08-13 |

## What it does

Deploys `ghcr.io/canonical/identity-saml-provider` (workload version 0.1.6) behind Pebble. It wires four integrations (`charmcraft.yaml:33-49`):

- `database` (`postgresql_client`, required) — feeds `SAML_PROVIDER_DB_*` env vars and runs the schema migration (`/usr/bin/identity-saml-provider migrate up`) via the `data_platform_libs` `DatabaseRequires` with `extra_user_roles="SUPERUSER"` (`src/charm.py:124-128`).
- `public-route` (`traefik_route`, required) — publishes a raw Traefik route and derives the external base URL for the OIDC callback (`src/integrations.py:88-161`).
- `oauth` (`oauth`, required) — registers an OIDC client with Hydra and injects the client id/secret and Hydra issuer URL (`src/integrations.py:167-175`).
- `receive-ca-cert` (`certificate_transfer`, optional) — injects a Hydra CA bundle (`src/integrations.py:198-207`).

SAML signing credentials come from a Juju secret referenced by the required `saml_credentials` config (`charmcraft.yaml:60-64`), documented in `docs/adr/001-saml-credentials-via-juju-secret.md`. A `run-migration` action provides manual migration, and `dev`/`cpu_limit`/`memory_limit` config options exist.

The control flow is a single `_holistic_handler` (`src/charm.py:396-411`) gated by two condition tuples in `src/utils.py:77-85`: `NOOP_CONDITIONS` (peer, database, database-resource-created, migration-ready → early return) and `EVENT_DEFER_CONDITIONS` (container connectivity → defer). Status is computed in `_on_collect_status` (`src/charm.py:352-394`).

## Deployment log

Deployed the published charm (`juju deploy identity-saml-provider-operator --channel latest/edge`, rev 3, workload 0.1.6). Rev 3 corresponds to tag v1.0.3 (published 2026-07-07); `git diff v1.0.3..HEAD` shows **zero** changes to `src/` or `lib/` — the only functional change since is the `charmcraft.yaml` build plugin `charm`→`uv` plus CI/renovate churn. Every behaviour observed on rev 3 therefore applies to `HEAD` (e64cb6c, 2026-07-23) as reviewed.

- `concierge-k8s-3` (Juju 3.6.25), model `rv-saml-idp2`: full stack — `postgresql-k8s 14/stable`, `hydra`, `traefik-k8s`, `self-signed-certificates`, `identity-platform-login-ui-operator`. Related `database`, `oauth`, `public-route`, `receive-ca-cert`, plus a secret. Reaches **active** with 2 units.
- `concierge-k8s-4` (Juju 4.0.5), model `rv-saml-review`: charm deploys and reaches **blocked "Missing integration database"**. A complete Juju 4 deploy is impossible because the only `postgresql_client` provider in the ecosystem, `postgresql-k8s` (14/stable and 16/stable), declares `assumes: juju < 4.0.0` and refuses to deploy on 4.0.5. The charm's own `assumes: juju >= 3.6` (`charmcraft.yaml:14-16`) is thus optimistic about Juju 4 end-to-end. This is an ecosystem gap, not a bug in this charm.

Notable commands:

```shell
juju deploy identity-saml-provider-operator --channel latest/edge
juju deploy postgresql-k8s --channel 14/stable --trust
juju deploy hydra --channel latest/stable --trust   # + login-ui + traefik-k8s + self-signed-certificates
juju integrate identity-saml-provider-operator postgresql-k8s:database
juju integrate identity-saml-provider-operator hydra:oauth
juju integrate identity-saml-provider-operator traefik-k8s:traefik-route
juju integrate identity-saml-provider-operator self-signed-certificates:send-ca-cert
juju add-secret saml-credential private-key#file=... public-cert#file=...
juju grant-secret saml-credential identity-saml-provider-operator
juju config identity-saml-provider-operator saml_credentials=secret:<id>
```

## Observed behaviour

Everything below was read off the live system (pebble API over the unix socket `/charm/containers/identity-saml-provider/pebble.socket` from the `charm` container, `kubectl`, `juju status`/`debug-log`). The workload container is a distroless rock with no `sh`, `cat` or `ps`, so the pebble API is the only way in — worth knowing for anyone operating this charm.

**Startup & resource shape.** The pod is 2/2 (charm + workload). The workload container requests `{cpu: 1, memory: 1Gi}` (hardcoded, `src/configs.py:193`) and the charm container uses Juju's default `64Mi`/`1Gi`. `kubectl top` showed ~2 mCPU / ~44 Mi per pod at rest.

**Pebble plan quirk — `startup: disabled`.** The merged plan shows the service as `startup: disabled, current: active`:

```yaml
services:
    identity-saml-provider:
        startup: disabled
        override: replace
        command: /usr/bin/identity-saml-provider serve
        on-check-failure:
            alive: restart
```

The charm's layer (`src/services.py:30-36`) sets `"startup": "disabled"` with `override: replace`, overriding the rockcraft layer's `startup: enabled`. The service runs only because `plan()` explicitly `restart()`s it. On a pod restart, recovery happened via `restart()` (pebble change `restart` at 08:36:35) *only because* the `/etc/saml/*` cert files are on the ephemeral container filesystem and get re-pushed, flipping `restart_needed` to True (`src/services.py:133-141`). Had the certs survived (e.g. on storage), a pod restart would leave the workload down indefinitely, because `replan()` does not start a `startup: disabled` service and `update-status` → `replan` is a no-op. See finding below.

**Pod restart.** `kubectl delete pod` → new pod, service recovered in ~35 s: `pebble-ready` → `version` execs → file re-push → `restart`. No operator intervention needed.

**Config change.** Toggling `dev` true↔false re-rendered the layer (env `SAML_PROVIDER_DEV_MODE` flipped in the plan) and the service restarted (`current-since` advanced), confirming `replan` restarts a service whose plan actually changed.

**Failure injection — junk secret.** A secret containing only `foo=bar` (no `public-cert`/`private-key`) was granted and set. The charm pushed empty `/etc/saml/bridge.crt`/`bridge.key`, restarted, and the workload died: `FATAL cmd/serve.go:54 Failed to build application … tls: failed to find any PEM data in certificate input`. Status went to **blocked "Failed to start the service, please check the identity-saml-provider container logs"** — no traceback, but the message points to the real error in the logs. Restoring the good secret recovered to active. Because `saml_bridge_certs_exist` only checks file *existence* (`src/utils.py:67-74`), the more precise "Missing SAML bridge certificate and/or key file" status is never shown for a well-formed-but-wrong secret; the operator gets the generic container-logs message instead.

**Failure injection — invalid resource config.** `memory_limit=not-a-quantity` → **blocked "Failed obtaining resource limit spec: Invalid limits spec: {'cpu': None, 'memory': 'not-a-quantity'}"**, recovered on `--reset memory_limit`. Sensible and actionable.

**Failure injection — remove required relation (database).** `remove-relation …:database` → **blocked "Missing integration database"**, workload kept serving. Re-adding recovered to active in ~45 s with the migration re-run automatically on the leader.

**Failure injection — remove `oauth` relation (the big one).** `remove-relation …:oauth` → app status **blocked "Missing integration oauth"** (correct-looking), but the workload was restarted with no OIDC env vars and went into a `backoff` crash loop:

```
FATAL cmd/serve.go:54 Failed to build application
  error: failed to query Hydra OIDC provider: Get "http://localhost:4444/.well-known/openid-configuration": dial tcp [::1]:4444: connect: connection refused
```

The `is_blocked` status hides the fact the pod is crash-looping, and also masks the "Failed to start the service" blocked status that would otherwise be reported (the first-added blocked status wins). Re-adding `oauth` recovered to active.

**Scaling.** 1→3 units and 3→1 both settle to active with no issue. Migration is leader-only and non-leaders wait (observed cleanly during the scale-up).

**Action.** `juju run identity-saml-provider-operator/leader run-migration` → "Started migrating the database … Successfully migrated the database … Successfully updated migration version". No revision beyond rev 3 exists on any channel (`juju info`: only `latest/edge` rev 3), so `juju refresh` to a newer revision was not possible.

**Teardown.** `remove-application` ran without charm-hook errors; the Juju-4 modeloperator left the statefulset/pod in a brief `0/1` terminating state before cleaning up.

**Per-hook cost.** A single trivial `config-changed` (`dev` toggle) caused 2 new `exec` changes of `/usr/bin/identity-saml-provider version` on the leader (measured via pebble `/v1/changes`), plus the 3 cert-file `pull`s, a `replan`, and the `KubernetesComputeResourcesPatch` GET+PATCH of the StatefulSet (visible in `debug-log` as `HTTP Request: GET/PATCH …/statefulsets/…` on every hook). This repeats on every `update-status` (5 min default). The version is not cached: `migration_needed` (`src/charm.py:215-223`) calls `self._workload_service.version`, whose getter re-execs the command each time (`src/services.py:69-71`).

**Stale status.** After a StatefulSet rollout (triggered by any `cpu_limit`/`memory_limit` change), one unit frequently sat in **waiting "waiting for resources patch to apply"** long after the StatefulSet was fully ready (`readyReplicas==replicas`), clearing only on the next hook (up to the 5-minute `update-status`). This comes from `KubernetesComputeResourcesPatch.get_status()` (`lib/charms/observability_libs/v0/kubernetes_compute_resources_patch.py:741`) and its rollout-tracking `is_in_progress()`.

## Findings

### Removing the `oauth` relation crash-loops the workload behind a healthy-looking blocked status
- **Severity**: high
- **Kind**: bug
- **Where**: `src/utils.py:77-82` (NOOP_CONDITIONS omits oauth); `src/integrations.py:167-169`; `src/charm.py:343-344`
- **Evidence**: `NOOP_CONDITIONS` is `(peer_integration_exists, database_integration_exists, database_resource_is_created, migration_is_ready)` — oauth is absent, so `_holistic_handler` still runs when oauth is missing. `OAuthIntegration.to_env_vars` returns `{}` when `is_client_created()` is falsy (`src/integrations.py:167-169`), so the layer is re-rendered and restarted without `SAML_PROVIDER_HYDRA_PUBLIC_URL`/`_OIDC_CLIENT_ID`/`_OIDC_CLIENT_SECRET`. Observed live: `remove-relation …:oauth` → blocked "Missing integration oauth" while the service entered `backoff` and logged `FATAL … failed to query Hydra OIDC provider: Get "http://localhost:4444/…"`. Matches open issue #72.
- **Impact**: an operator who removes the oauth relation (even temporarily) believes the charm is just "waiting for oauth"; in fact the workload is down and the SAML bridge is returning 503s. The relation is declared required (`charmcraft.yaml:44-45`), so the charm should degrade gracefully like it does for the database (early-return without touching the service), not render a broken layer.
- **Fix**: add `oauth_integration_exists` (or a "oauth client created" condition) to `NOOP_CONDITIONS`, or gate the OIDC env vars so the layer isn't re-rendered empty.
- **Linter rule**: mechanically checkable — "a required relation declared in `charmcraft.yaml` is not present in the NOOP/EARLY-RETURN condition tuple" (cross-reference `requires` with the gating conditions).

### `startup: disabled` pebble override makes pod restart depend on ephemeral files
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/services.py:30-36`
- **Evidence**: `"startup": "disabled"` with `"override": "replace"` overrides the rock layer's `startup: enabled`. Confirmed via pebble `/v1/services`: `startup: disabled, current: active`.
- **Impact**: on pod restart, Pebble will not auto-start the service. It recovers today only because `/etc/saml/*` is on the ephemeral container layer and is re-pushed, which flips `restart_needed` (`src/services.py:136-142`) and triggers an explicit `restart()`. If the cert files were ever on attached storage (or the comparison reported them unchanged), the workload would stay down indefinitely — `replan()` is a no-op for a disabled service, and nothing else restarts it.
- **Fix**: keep `startup: enabled` (the rock layer default) and rely on the charm pushing files and `replan`/`restart` when config actually changes, or explicitly set `startup: enabled` once config is first applied.
- **Linter rule**: mechanically checkable — "charm pebble layer overrides `startup` to `disabled` while the OCI rock layer sets `enabled`".

### Database user is granted cluster-wide `SUPERUSER`
- **Severity**: medium
- **Kind**: bug (security posture)
- **Where**: `src/charm.py:124-128`
- **Evidence**: `DatabaseRequires(…, extra_user_roles="SUPERUSER")`.
- **Impact**: the SAML provider's DB user gets superuser on the whole PostgreSQL instance, not just its own `saml_provider` database. If the workload is compromised (it's an internet-facing SAML/SSO component), that's full control of the shared database cluster, including any other tenants on the same PostgreSQL charm. It's a common Canonical-identity-platform pattern, but broader than the migration likely needs (typically only `CREATE EXTENSION` in its own DB).
- **Fix**: investigate whether the migration can run under a less-privileged role (e.g. one that can create extensions/schemas in its own database); if `SUPERUSER` is genuinely required, document why.
- **Linter rule**: mechanically checkable — "`extra_user_roles` contains `SUPERUSER`/`CREATEDB`/`CREATEROLE`".

### Failed auto-migration leaves a permanent, misleading "Waiting for database migration"
- **Severity**: medium
- **Kind**: bug / ux
- **Where**: `src/charm.py:301-302` (catch); `src/charm.py:373` (status)
- **Evidence**: the catch at L301-302 does `except MigrationError: logger.error("Auto migration job failed. Please use the run-migration action"); return`. The `database_created` event is then consumed and never re-fires, while `_on_collect_status` at L373 reports `WaitingStatus("Waiting for database migration")` whenever `migration_needed` is still true.
- **Impact**: if the automatic migration fails once (transient DB issue, bad DSN), the charm settles into a permanent *waiting* status that says "waiting" when nothing will ever happen — the operator must run `run-migration` manually but is never told so. A waiting status also doesn't trigger alerts the way blocked does. Part of the "invalid status reporting" family flagged in open issue #71.
- **Fix**: on migration failure set a BlockedStatus (e.g. "Database migration failed, run the run-migration action"), or retry with a bounded defer loop.
- **Linter rule**: not mechanically checkable (requires tracing event lifecycle).

### Workload version re-exec'd on every hook (uncached)
- **Severity**: low
- **Kind**: performance
- **Where**: `src/charm.py:215-223` (`migration_needed`) → `src/services.py:69-71` (`application_version`)
- **Evidence**: `application_version` calls `self._cli.get_application_version()` on every access (runs `/usr/bin/identity-saml-provider version` in the container with a 20 s timeout, `src/cli.py:19-33`). `migration_needed` is evaluated by `NOOP_CONDITIONS` on every hook and by `_on_collect_status`. Measured: a single `config-changed` produced 2 new `version` execs.
- **Impact**: the OCI image version is fixed for the life of a pod; re-execing it on every hook (including `update-status` every 5 min, per unit) is pure overhead and adds a 20 s worst-case stall per hook if the container is slow.
- **Fix**: cache the version at `pebble-ready` (or in `StoredState`/peer data) and re-read only on upgrade events.
- **Linter rule**: mechanically checkable — "hook handler path calls `container.exec` without caching a value that is invariant for the pod lifetime".

### `saml_bridge_certs_exist` checks existence, not content
- **Severity**: low
- **Kind**: bug / ux
- **Where**: `src/utils.py:67-74`
- **Evidence**: `container.exists(SAML_BRIDGE_CERT) and container.exists(SAML_BRIDGE_KEY)` — files pushed empty still pass. Observed with a junk secret: empty files existed, so the precise "Missing SAML bridge certificate and/or key file" status was skipped and the generic "Failed to start the service" was shown instead.
- **Impact**: a misconfigured/rotated secret that lacks the two fields produces a less-precise status; operators have to dig through container logs to learn the cert is empty.
- **Fix**: compare file content (the `ContainerFile.from_workload_container` machinery already reads content) rather than `exists()`.
- **Linter rule**: mechanically checkable — "`saml_bridge_certs_exist` uses `container.exists` on files whose content the charm itself writes".

### `cpu_limit`/`memory_limit` below the hardcoded requests are silently ignored
- **Severity**: low
- **Kind**: ux / docs
- **Where**: `src/configs.py:193-199` + `lib/charms/observability_libs/v0/kubernetes_compute_resources_patch.py:158-247`
- **Evidence**: requests are hardcoded `{"cpu": "1", "memory": "1Gi"}` and `adjust_resource_requirements(..., adhere_to_requests=True)` raises limits to `max(limit, request)`. Observed: setting `cpu_limit=500m` produced a StatefulSet with `limits.cpu: 1`, not 500m. The config description advertises `"500m"` as an example (`charmcraft.yaml:66-69`).
- **Impact**: an operator setting a small limit to constrain the workload gets the opposite (a *higher* limit) with no warning.
- **Fix**: either pass `adhere_to_requests=False` (pulling requests down) or document that limits below 1 CPU / 1 Gi are ineffective, and drop the misleading `500m` example.
- **Linter rule**: not mechanically checkable (semantic).

### `mypy` reports 2 errors in `src/` that CI never sees
- **Severity**: low
- **Kind**: lint
- **Where**: `src/configs.py:170` and `src/services.py:128`
- **Evidence**: `uv run --group dev mypy src/` → `configs.py:170: error: Argument 1 to "resolve" of "SecretResolver" has incompatible type "int | float | str | None"; expected "str"` and `services.py:128: error: Incompatible types in assignment (expression has type "dict[str, Collection[str]]", variable has type "LayerDict")`.
- **Impact**: `tox -e lint` (codespell/isort/ruff) passes, but mypy is only wired into pre-commit, which type-checks only *staged* files, so these have likely gone unnoticed. `ruff`, `codespell`, `isort`, `ruff format` all pass cleanly.
- **Fix**: fix the two annotations and add mypy to `tox -e lint` (or a dedicated env).
- **Linter rule**: mechanically checkable — it *is* a linter, just not wired into CI.

### Stale "waiting for resources patch to apply" after rollouts
- **Severity**: low
- **Kind**: ux
- **Where**: `src/charm.py:392` (`event.add_status(self._resources_patch.get_status())`) + `lib/.../kubernetes_compute_resources_patch.py:459-496,741`
- **Evidence**: after any `cpu_limit`/`memory_limit` change (which rolls the StatefulSet), one unit repeatedly showed `waiting "waiting for resources patch to apply"` while the StatefulSet was already `readyReplicas==replicas`, until the next hook event.
- **Impact**: operators see a spurious waiting status (and, transiently, "Missing SAML bridge certificate and/or key file" when a new pod's ephemeral `/etc/saml` is still empty) for up to the `update-status` interval.
- **Fix**: none obvious in-charm — it's inherent to the library's rollout tracking; a shorter `update-status` interval or accepting the library's own `ActiveStatus()` would mitigate.
- **Linter rule**: not mechanically checkable.

## Worth copying

- **Condition-tuple reconciler** (`src/utils.py:77-85`): `NOOP_CONDITIONS` vs `EVENT_DEFER_CONDITIONS` split "do nothing" from "try again later" declaratively, and `_holistic_handler` (`src/charm.py:396-411`) is a small, single reconciliation entry point. Cleaner than the usual per-handler if-spaghetti.
- **Protocol-based config sources** (`src/configs.py:20-44`, `src/env_vars.py:18-21`): `ServiceConfigSource`, `EnvVarConvertible`, `ContainerFile` protocols with `from_sources`/`from_workload_container` make config assembly composable and testable.
- **Frozen dataclass models with loader classmethods** (`src/integrations.py:66-120, 183-207`): `DatabaseConfig.load`, `TransferredCertificates.load` keep relation plumbing out of the main charm file.
- **`SecretResolver` abstraction** (`src/configs.py:110-136`): resolves the Juju secret with graceful degradation (missing prefix, `SecretNotFoundError`) and logs an operator-actionable warning rather than raising.
- **Pebble checks** (`src/services.py:37-57`): `alive`/`ready` HTTP checks with `on-check-failure: restart`; verified the workload self-heals from a SIGKILL (Pebble's default `on-failure: restart` brought it back within ~5 s, no operator action).
- **Real integration assertions** (`tests/integration/test_charm.py:120-146, 149-158`): asserts actual relation databag contents and hits `/healthz`, `/readyz`, `/saml/metadata` for HTTP 200 — not just `active/idle`.
- **The ADR** (`docs/adr/001-saml-credentials-via-juju-secret.md`) is short, honest about the negatives, and explains *why* secrets were chosen over a TLS-certificate integration.

## Common-practice notes

- Uses the canonical identity-platform libraries exactly as intended: `data_platform_libs` `DatabaseRequires`, `hydra` `oauth`, `traefik_route`, `certificate_transfer`, `observability_libs` `KubernetesComputeResourcesPatch`. LIBPATCH tracking is up to date (oauth at LIBPATCH 11).
- The "holistic handler" is the current canonical-iam house style; this is a good example of it done readably.
- **Drift**: `startup: disabled` + `override: replace` in the pebble layer is unusual — the ecosystem norm is to let the rock's `startup: enabled` stand and manage restarts via `replan`. This charm's version works only by the accident described above.
- **Drift**: requesting `extra_user_roles="SUPERUSER"` is a known identity-platform anti-pattern; several sibling charms are moving to narrower grants.
- **Ahead of the curve**: the `charmcraft.yaml` `parts.charm.plugin: uv` + `astral-uv` build-snap migration (and `uv.lock`) is newer than most charms still on `plugin: charm`.
- The workload rock is fully distroless (no shell) — operationally clean, but it means `juju ssh --container` is useless for debugging and everything must go through the Pebble API; not documented anywhere.
- The terraform module (`terraform/main.tf`) is a bare `juju_application` with no relation wiring and defaults `channel = "latest/stable"`, a channel that does not exist for this charm (only `latest/edge` rev 3); using it as-is yields a permanently blocked app.

## Tests

- **Unit**: `uv run --group unit pytest --ignore=tests/integration` → **104 passed** in ~1.8 s. Coverage (`coverage run --source=src,tests/unit`): **97%** overall; `src/charm.py` 90% (uncovered: leader-only public-route/OAuth paths at `charm.py:316-341`, the non-leader migration branch, and the `run-migration` failure paths at `charm.py:412+`).
- **Lint**: `ruff check`, `ruff format --check`, `codespell`, `isort --check-only` all pass. `mypy src/` fails with 2 errors (finding above).
- **Integration** (`tests/integration/test_charm.py`, pytest-jubilant): deploys the full stack and asserts `/healthz` `/readyz` `/saml/metadata` return 200, relation databags are populated, migration action completes, scale up/down, and relation-removal → blocked. Not run here (needs `charmcraft pack` + a model with postgresql; the same ground was already covered manually against the published charm).
- **Coverage gaps relative to the risks found**: `test_remove_oauth_integration` (`test_charm.py:193-199`) asserts only `is_blocked` and would *pass* while the workload is crash-looping — the exact bug in the top finding. There is no test for: secret rotation with a wrong-content secret (empty cert), the failed-auto-migration status, the `startup: disabled` pod-restart path, invalid `cpu_limit`/`memory_limit` values, or the `dev` toggle.

## Docs

- `README.md` gives a correct, complete deploy sequence (secret creation, all four relations) and matches what was observed, including the `--trust` requirement (the resources patch needs it — confirmed by the k8s API PATCH calls in `debug-log`).
- `docs/adr/001-saml-credentials-via-juju-secret.md` is accurate and current.
- Gap: nothing documents that the workload container has no shell (so `juju ssh --container` fails with "executable file not found in $PATH"), nor that the published channel is `latest/edge` only, nor that `cpu_limit`/`memory_limit` are floor-limited by the hardcoded 1 CPU / 1 Gi requests.
- The `AGENTS.*.md` files are copilot-swe-agent conventions (`AGENTS.md` pins the same style rules the repo actually follows); they don't describe the charm's runtime behaviour.

## Open questions

- **Does the migration genuinely require `SUPERUSER`?** The migration's SQL wasn't visible (the workload is distroless and image internals are out of scope). Settling it: inspect the `identity-saml-provider` migration source, or run the migration against `postgresql-k8s` with a non-superuser role and see what fails.
- **Would `adhere_to_requests=False` be intended for `cpu_limit`?** The hardcoded 1 CPU / 1 Gi requests combined with `adhere_to_requests=True` look like a copy-paste from another charm; the original author's intent is unclear from the history.
- **Juju 4 end-to-end**: blocked by `postgresql-k8s`'s `assumes`, not by this charm. Worth re-testing once a Juju-4 postgresql provider ships.
