# Working notes — identity-saml-provider-operator

## Orientation
- k8s charm, single charm in repo
- charmcraft.yaml: requires juju >= 3.6, k8s-api
- OCI image: ghcr.io/canonical/identity-saml-provider:v0.1.6
- Provides: nothing
- Requires: database (postgresql_client, not optional), public-route (traefik_route, not optional), oauth (hydra, not optional), receive-ca-cert (certificate_transfer, optional)
- Resources: oci-image
- Config: dev (bool), saml_credentials (secret, required), cpu_limit, memory_limit
- Actions: run-migration

## Source files
- src/charm.py — main charm class, holistic handler pattern
- src/constants.py — constants
- src/exceptions.py — PebbleServiceError, MigrationError
- src/utils.py — conditions, decorators
- src/configs.py — file dataclasses, CharmConfig, SecretResolver
- src/integrations.py — PeerData, DatabaseConfig, PublicRouteIntegration, OAuthIntegration, TransferredCertificates
- src/services.py — WorkloadService, PebbleService
- src/cli.py — CommandLine (migrate, version)
- src/env_vars.py — DEFAULT_CONTAINER_ENV

## Libraries (lib/charms/)
- charms.certificate_transfer_interface/v1/certificate_transfer.py
- charms.data_platform_libs/v0/data_interfaces.py
- charms.hydra/v0/oauth.py
- charms.observability_libs/v0/kubernetes_compute_resources_patch.py
- charms.traefik_k8s/v0/traefik_route.py

## Open issues (from open-issues.txt)
1. #72: oauth relation not checked for readiness in holistic handler — `_holistic_handler` has no check for oauth_integration_exists, but `_on_collect_status` does add a BlockedStatus for it. oauth_integration is unconditionally passed to `render_pebble_layer`.
2. #71: Invalid status reporting — migration_needed creates WaitingStatus but can be overridden by BlockedStatus from missing cert.

## Unit tests
- 104 tests, all passing
- Tests cover: charm events, actions, CLI, configs, integrations, services

## Linting
- ruff: all checks passed
- codespell: 0 issues
- pyproject.toml configured with ruff, isort, mypy, codespell

## Code review notes
- `_holistic_handler` at src/charm.py:217-230 — no oauth check in NOOP_CONDITIONS, so it silently proceeds without oauth
- `_on_collect_status` at src/charm.py:233-278 — correctly adds BlockedStatus for missing oauth, but holistic handler won't re-plan
- `oauth_integration.to_env_vars()` at src/integrations.py:152 — returns empty dict if client not created, but pebble layer always gets the integration
- `_pebble_layer` property at src/charm.py:192 — always passes oauth_integration even if oauth not ready
- `PublicRouteIntegration.config` at src/integrations.py:104 — reads template from `templates/public-route.json.j2` at runtime (during hook execution, not build)
- `PeerData.__getitem__` at src/integrations.py:55 — returns `{}` for missing key, but `migration_version` key is string "migration_version_X" — json.loads on None returns {} — this is fine but slightly odd
- `_on_public_route_changed` at src/charm.py:264 — mutates `public_route_requirer._relation` directly — this is a private attribute manipulation

## Deploy plan
- Use concierge-k8s-4 (juju 4.x) 
- Deploy from charmhub edge channel
- Relate to postgresql-k8s (14/stable), traefik-k8s (latest/edge), hydra (latest/stable)
- Create SAML credentials secret, grant to charm
- Integrate all required relations
- Walk lifecycle: config changes, relation changes, scale, remove relations, actions

## Git history
- Latest commit: e64cb6c (2026-07-23) — merge: auto-pre-commit-hooks update
- 79 commits total
- 1.0.3 released
- edge rev 3 on charmhub
