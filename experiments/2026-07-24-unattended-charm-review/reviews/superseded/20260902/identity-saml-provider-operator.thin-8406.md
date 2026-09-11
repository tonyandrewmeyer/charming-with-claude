# identity-saml-provider-operator

A k8s charm that fronts Ory Hydra with a SAML identity provider (SAML-to-OIDC bridge), wired to PostgreSQL, Traefik and Hydra via standard relations. The code is clean, uses a holistic-handler reconciler pattern, and ships a full unit test suite (104/104 passing) with clean linters. No deployment was carried out for this review — findings below are from static/code review and two open upstream issues, not from an observed running system. The most serious known defect is that the `oauth` relation is not gated in the holistic handler (upstream issue #72): a missing/not-ready oauth integration can let the charm proceed to render and restart the Pebble layer with no OIDC credentials, even though `_on_collect_status` separately reports a blocked status for it. A maintainer should fix that gating first, then resolve the status-priority bug in issue #71.

| | |
|---|---|
| Repo | canonical/identity-saml-provider-operator @ e64cb6c (2026-07-23) |
| Charms | identity-saml-provider-operator |
| Substrate | k8s |
| Deployed | no — no deployment log exists for this review; only a deploy plan was recorded, it was not executed |
| Reviewed | 2026-08-15 |

## What it does

Deploys the `ghcr.io/canonical/identity-saml-provider:v0.1.6` OCI image as a Kubernetes workload. It requires `database` (`postgresql_client`), `public-route` (`traefik_route`) and `oauth` (hydra), and optionally accepts `receive-ca-cert` (`certificate_transfer`). SAML signing credentials are supplied via a required Juju secret (`saml_credentials` config). The charm runs database migrations and renders Pebble layers with environment variables derived from all integrations, using a single holistic handler pattern (`_holistic_handler`) gated by condition tuples. Config also exposes `dev`, `cpu_limit`, `memory_limit`; a `run-migration` action triggers migrations manually.

## Deployment log

Not attempted. The reviewer's notes record only a deploy plan (concierge-k8s-4, Juju 4.x, charmhub edge channel, relate to `postgresql-k8s`, `traefik-k8s`, `hydra`, create/grant a SAML credentials secret, then walk the lifecycle) — there is no evidence in the draft or notes that this plan was carried out.

## Observed behaviour

Not observed — no deployment was performed, so there is no runtime evidence to report.

## Findings

### `oauth` relation not gated in the holistic handler
- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:217-230` (`_holistic_handler` / `NOOP_CONDITIONS`); `src/charm.py:233-278` (`_on_collect_status`); `src/integrations.py:152` (`OAuthIntegration.to_env_vars`); `src/charm.py:192` (`_pebble_layer`)
- **Evidence**: `NOOP_CONDITIONS` does not include an oauth-readiness check, so `_holistic_handler` proceeds even when the oauth integration is absent or not ready. `_on_collect_status` does add a `BlockedStatus` for missing oauth, but the holistic handler does not re-plan around it. `OAuthIntegration.to_env_vars()` returns an empty dict when the client hasn't been created, yet `_pebble_layer` unconditionally passes the oauth integration into the rendered layer. This matches upstream issue #72.
- **Impact**: the charm can render and restart the Pebble layer without OIDC credentials while oauth is missing, even as the reported status claims "blocked" for that reason — the operator-visible status and the actual workload state can disagree. (unverified against a running system — no deployment was performed for this review.)
- **Fix**: add an oauth-readiness condition to `NOOP_CONDITIONS` (mirroring how the database integration is gated), or otherwise avoid re-rendering/restarting the layer when the oauth client hasn't been created.
- **Linter rule**: mechanically checkable — flag a relation declared `required` in `charmcraft.yaml` that is absent from the noop/early-return condition tuple used by the reconciler.

### Migration `WaitingStatus` can be masked by other blocked statuses
- **Severity**: medium
- **Kind**: bug (status reporting)
- **Where**: not established (upstream issue #71; exact status-priority code path not cited in the draft or notes)
- **Evidence**: notes record upstream issue #71: `migration_needed` produces a `WaitingStatus`, but that status can be overridden by a `BlockedStatus` from an unrelated cause (e.g. a missing cert).
- **Impact**: an operator can be shown a blocked status for one problem while a pending database migration is silently waiting behind it, delaying diagnosis.
- **Fix**: review the status-priority/collection logic so migration-pending state is not silently suppressed by unrelated blocked statuses — e.g. surface both, or make the priority explicit and documented.
- **Linter rule**: not established.

### `PublicRouteIntegration` loads its Traefik route template from disk at hook-execution time
- **Severity**: low
- **Kind**: robustness / code smell
- **Where**: `src/integrations.py:104`
- **Evidence**: `PublicRouteIntegration.config` reads `templates/public-route.json.j2` at runtime during hook execution rather than at build/charm-init time.
- **Impact**: a missing or corrupted template file would only surface as a runtime failure during a relation-changed hook, not earlier. (unverified — not exercised in this review.)
- **Fix**: load/validate the template once at charm construction, or add a unit test that asserts the template renders for representative inputs.
- **Linter rule**: not established.

### `PeerData.__getitem__` returns `{}` for a missing key with an oddly-named migration key
- **Severity**: low
- **Kind**: code smell
- **Where**: `src/integrations.py:55`
- **Evidence**: `PeerData.__getitem__` returns `{}` for a missing key; the `migration_version` peer-data key is stored as the string `"migration_version_X"`. The reviewer's notes describe the current behaviour as functionally fine but "slightly odd".
- **Impact**: no functional defect identified; readability/maintainability concern only.
- **Fix**: none required; a clarifying comment or renamed accessor would reduce confusion for future readers.
- **Linter rule**: not established.

### `_on_public_route_changed` mutates a library object's private attribute
- **Severity**: low
- **Kind**: code smell
- **Where**: `src/charm.py:264`
- **Evidence**: `_on_public_route_changed` sets `public_route_requirer._relation` directly, reaching into a private (underscore-prefixed) attribute of the `traefik_route` library object.
- **Impact**: depends on library internals that aren't part of its public API; a future library upgrade could silently break this without any public-API change to flag it.
- **Fix**: use the library's public interface to update the relation reference, or file an upstream request if no public API exists for this.
- **Linter rule**: mechanically checkable — flag direct read/write access to underscore-prefixed attributes on objects imported from `lib/charms/*`.

## Worth copying

Not established in the draft or notes beyond the general code-quality praise (clean holistic-handler pattern, comprehensive unit tests, clean linters) already captured in the verdict.

## Common-practice notes

- Uses the canonical identity-platform libraries as intended: `data_platform_libs` (`postgresql_client`), `hydra` (`oauth`), `traefik_route`, `certificate_transfer`.
- Holistic-handler reconciler (single `_holistic_handler` gated by condition tuples) is a clean, readable implementation of this pattern.

## Tests

- Unit tests: 104/104 passing, per the reviewer's notes.
- Linting: ruff — all checks passed; codespell — 0 issues; `pyproject.toml` has ruff, isort, mypy and codespell configured.
- Test coverage against the top finding: not established — the notes do not record whether the existing test suite exercises the oauth-relation-removal path.

## Docs

Not established — the draft and notes do not evaluate documentation.

## Open questions

- Does `run-migration`'s automatic counterpart ever get re-triggered after a failed auto-migration, or does it require manual intervention every time? (relates to issue #71, not settled in the notes)
- What is the actual operator-visible behaviour when the oauth relation is removed on a live deployment — does the workload restart with empty credentials as the code suggests, or does something else prevent it? This needs an actual deployment to confirm; none was performed for this review.
