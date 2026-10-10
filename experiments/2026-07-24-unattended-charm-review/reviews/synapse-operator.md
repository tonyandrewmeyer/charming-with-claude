# Synapse

This is a mature, well-structured k8s charm for Matrix Synapse with a clean reconciler pattern and broad integration support (PostgreSQL, Redis, S3, SAML, SMTP, Traefik, observability, Mjolnir). Code quality is generally high — Pydantic config validation, typed dataclasses, DeepDiff-driven change detection — and lint/type/security tooling is clean (pylint 10.00/10, mypy clean, bandit zero issues). But two critical bugs undermine that polish: the charm ignores database relation removal entirely (stays pointed at stale, possibly-destroyed Postgres, no handler registered), and four Pydantic validators raise `ValidationError` with the wrong constructor signature, which crashes the hook with a `RuntimeError` instead of setting `BlockedStatus` for several common bad-config paths. Two further high-severity bugs — broken matrix-auth appservice registration (writes to the wrong filesystem) and un-cleaned-up worker/federation-sender state on scale-down or Redis removal — mean multi-unit and appservice deployments can silently degrade while the charm reports `active`. A maintainer should fix the two critical bugs first (both are small, mechanical fixes), then the two high-severity ones, before this charm is safe to run in production topologies with more than one unit.

| | |
|---|---|
| Repo | canonical/synapse-operator @ `b6e2231` (2026-07-21) |
| Charms | synapse |
| Substrate | k8s |
| Deployed | yes — concierge-k8s-3 (Juju 3.6.25), latest/edge rev 523 across 6 models; concierge-k8s-4 (Juju 4.0.5), latest/edge rev 523 (SQLite only) |
| Reviewed | 2026-08-03 |

## What it does

Deploys Matrix Synapse on Kubernetes. Supports database (PostgreSQL), media storage (S3), backup/restore (S3), SAML auth, SMTP email, Redis (required for multi-unit), ingress via Traefik or nginx-route, observability (Grafana dashboards, Prometheus metrics, Loki logging), Mjolnir moderation bot, and Matrix Auth integration. Actions: `register-user`, `promote-user-admin`, `anonymize-user`, and create/list/restore/delete backup.

## Deployment log

### First deploy (rv-syn2) — Juju 3.6.25, basic
```
juju add-model rv-syn2 -c concierge-k8s-3
juju deploy postgresql-k8s --channel 14/stable
juju deploy synapse --channel edge --config server_name=example.com
juju trust postgresql-k8s --scope=cluster
juju integrate synapse postgresql-k8s
```
An initial attempt on concierge-k8s-4 (Juju 4.0.5) failed because `postgresql-k8s` 14/stable requires Juju < 4.0.0. The Synapse OCI rock (~400MB) took ~6 minutes to pull; synapse reached `active` about 7 minutes after deploy. Deployed revision 523 runs Synapse 1.120.0, while the local source declares `SYNAPSE_VERSION = "1.146.0"`.

### Second deploy (rv-synapse) — Juju 3.6.25, multi-integration
```
juju add-model rv-synapse -c concierge-k8s-3
juju deploy postgresql-k8s --channel 14/stable --trust
juju deploy synapse --channel edge --config server_name=example.com
juju deploy redis-k8s --channel latest/edge --trust
juju deploy s3-integrator --channel latest/edge
juju deploy self-signed-certificates --channel latest/edge
juju deploy traefik-k8s --channel latest/edge --trust
juju integrate synapse postgresql-k8s
juju integrate synapse redis-k8s
juju integrate synapse traefik-k8s
```
All 6 apps deployed. Synapse reached `active` on SQLite first, then reconfigured to PostgreSQL once the database relation fired. After the switch, `pebble services` showed synapse, nginx and stats-exporter active, with `synapse-cron` still inactive.

### Third deploy (rv-deep3) — Juju 3.6.25, failure testing
```
juju add-model rv-deep3 -c concierge-k8s-3
juju deploy postgresql-k8s --channel 14/stable --trust
juju deploy synapse --channel edge --config server_name=example.com
juju deploy redis-k8s --channel latest/edge --trust
juju deploy s3-integrator --channel latest/edge
juju integrate synapse postgresql-k8s
juju integrate synapse redis-k8s
```
Built to exercise failure modes: database relation removal, kill/recovery, scale up/down with Redis, action correctness against Postgres, bad-config injection, and backup actions without S3.

### Fourth deploy (rv-j4) — Juju 4.0.5
```
juju add-model rv-j4 -c concierge-k8s-4
juju deploy synapse --channel edge --config server_name=example.com
```
Charm-only deploy, no integrations. Synapse came up `active` with SQLite. `postgresql-k8s` 14/stable does not support Juju 4.x, so Postgres integration could not be tested on 4.x. No Juju-version-specific behavioural differences observed.

### Fifth deploy (rv-deep4) — Juju 3.6.25, full integration suite
```
juju add-model rv-deep4 -c concierge-k8s-3
juju deploy postgresql-k8s --channel 14/stable --trust
juju deploy synapse --channel edge --config server_name=example.com
juju deploy redis-k8s --channel latest/edge --trust
juju deploy s3-integrator --channel latest/edge
juju deploy traefik-k8s --channel latest/edge --trust
juju deploy smtp-integrator --channel latest/edge
juju deploy grafana-agent-k8s --channel 1/edge --trust
juju run s3-integrator/0 sync-s3-credentials access-key=testaccesskey secret-key=testsecretkey
juju config s3-integrator endpoint=http://minio.example.com:9000 bucket=synapse-media path=/media s3-uri-style=path
juju integrate synapse postgresql-k8s
juju integrate synapse redis-k8s
juju integrate synapse traefik-k8s
juju integrate synapse:media s3-integrator:s3-credentials
juju integrate synapse:backup s3-integrator:s3-credentials
juju integrate synapse:smtp smtp-integrator:smtp
juju integrate grafana-agent-k8s:grafana-dashboards-consumer synapse:grafana-dashboard
juju integrate grafana-agent-k8s:metrics-endpoint synapse:metrics-endpoint
juju integrate grafana-agent-k8s:logging-provider synapse:logging
```
All integrations active. S3 media config correctly populated in `homeserver.yaml`. Promtail from grafana-agent started. SMTP integrator was `blocked` (no host configured) but synapse remained `active`. Used for deep failure testing: config validation crashes, Redis removal, pod restart, scaling, teardown.

### Sixth deploy (rv-deep5) — Juju 3.6.25, deep failure injection
```
juju add-model rv-deep5 -c concierge-k8s-3
juju deploy postgresql-k8s --channel 14/stable --trust
juju deploy synapse --channel edge --config server_name=example.com
juju deploy redis-k8s --channel latest/edge --trust
juju deploy s3-integrator --channel latest/edge
juju integrate synapse postgresql-k8s
juju integrate synapse redis-k8s
juju integrate synapse:media s3-integrator:s3-credentials
juju integrate synapse:backup s3-integrator:s3-credentials
```
Systematic failure injection: Redis removal with 2 units, scale-down with stale services, pod kill after Redis removal, all 4 backup actions without S3, all 3 user actions, `bad public_baseurl` crash, `publish_rooms_allowlist` crash, `trusted_key_servers` BlockedStatus, `federation_domain_whitelist` silent accept. All four apps deployed and integrated successfully; synapse reached `active` after ~3 minutes (Postgres took longer).

### Refresh
```
juju refresh synapse --channel latest/stable  # downgrade: rev 523 → rev 426
```
Triggered a pod restart (image re-pull). Both units came back up after ~5 minutes of `PodInitializing`.

## Observed behaviour

### Deployment and runtime

1. **Image pull time**: consistently 5–6 minutes `PodInitializing` for both edge and stable images. The OCI rock bundles Synapse, NGINX, Mjolnir, cron, and stats-exporter into one ~400MB image.

2. **Hook fan-out**: during initial deployment, `build_charm_state()` ran 7+ times for unit 0 alone — once per `database-relation-changed` event — each call logging the full parsed config at INFO (`charm_state.py:479`). Total log volume during deployment was high.

3. **Cron service not started on initial deploy**: `pebble services` showed `synapse-cron: enabled, inactive` after initial deploy on both rev 523 and rev 426, and on Juju 4.x. `restart_synapse()` (`pebble.py:90-98`) adds the cron layer with `startup: enabled` but only calls `container.restart(SYNAPSE_SERVICE_NAME)` — it never calls `container.start(SYNAPSE_CRON_SERVICE_NAME)` and does not replan. After a pod restart (rv-deep4, rv-deep5), `synapse-cron` became active, suggesting a Pebble timing issue specific to first deploy.

4. **Scaling with Redis works correctly**: with Redis integrated and active, `juju scale-application synapse 2` brought both units to `active` (main + worker). The worker runs synapse+nginx; the main runs synapse+nginx+stats-exporter. NGINX correctly routes to the main unit for both units.

5. **Scaling without Redis — race condition**: in rv-syn2 (rev 523), both units reached `active` despite no Redis being integrated — likely because `planned_units()` returned 1 during the initial reconcile before the scale-up was fully applied. In rv-synapse (rev 426), after Redis was removed and pods restarted, both units correctly blocked. The `redis_required` check at `charm_state.py:499` is logically correct but races with the controller's `planned_units()`.

6. **Scaling down 2→1 leaves stale `worker.yaml` and federation-sender**: after scaling down to 1 unit (rv-deep4, rv-deep5), the `synapse-federation-sender` Pebble service remained in `backoff` with `worker.yaml` still on disk (219 bytes, `root:root`). `reconcile()` pushes `worker.yaml` unconditionally (`pebble.py:382-386`) and only restarts the federation sender when `instance_map_config is not None` (line 391); the old layer is never removed.

7. **Secrets visible in Pebble plan / homeserver.yaml**: `POSTGRES_PASSWORD`, `PROM_SYNAPSE_PASSWORD`, `registration_shared_secret`, and `macaroon_secret_key` are all in plaintext in the Pebble layer environment and in `homeserver.yaml`. That file is owned `root:root` (644) — readable by the `synapse` user, so functionally fine, but unconventional. The database password persisted in `homeserver.yaml` even after the database relation was removed.

8. **NO_PROXY/no_proxy duplicate**: `get_environment()` (`workload.py:243-246`) sets both lowercase and uppercase proxy env vars. DeepDiff warns about a case-insensitive key collision on every reconcile.

9. **Kill recovery**: SIGKILL of the synapse process was recovered by Pebble within ~1–3s across multiple runs. `kubectl delete pod` recovered cleanly, with synapse `active` within ~30s of the new pod starting.

10. **Version mismatch**: deployed revision 523 reports Synapse 1.120.0; local HEAD declares `SYNAPSE_VERSION = "1.146.0"`.

### Failure injections

11. **Database removal not handled — confirmed via debug-log**: after `juju remove-relation synapse postgresql-k8s` (reproduced in rv-synapse and rv-deep3/5), synapse remained `active` with `homeserver.yaml` still pointing at the old Postgres endpoint (`postgresql-k8s-primary...svc.cluster.local`, `database: name: psycopg2`). Debug-log confirms `database-relation-departed` and `database-relation-broken` hooks did fire (observed at 16:50:40 UTC in one run, 17:29:53/54 UTC in another), but `DatabaseObserver` registers only `_on_database_created` and `_on_endpoints_changed` — no handler for broken/departed. Compare with SAML, which has `_on_saml_relation_broken` (`charm.py:421`). The charm does not fall back to SQLite; the original `homeserver.db` remains on disk but unused.

12. **Redis removal leaves federation-sender crashing (1 unit case)**: after `juju remove-relation synapse redis-k8s` (rv-deep4), `homeserver.yaml` was correctly regenerated without the `redis` section, but `synapse-federation-sender` stayed in `backoff` with `AssertionError: assert self.config.redis.redis_enabled`. `worker.yaml` was not cleaned up and the federation-sender layer was not removed. The charm still reported `active`.

13. **Stats exporter crashes with empty DB credentials**: before the database relation delivers credentials, `replan_stats_exporter()` starts the exporter with `POSTGRES_PORT=""`, causing `ValueError: invalid literal for int() with base 10: ''`. The error is caught and logged only at DEBUG (`pebble.py:186`), so the operator sees `active` while stats-exporter is in `error`. Pebble logs confirmed the crash on both initial deploy attempts; the exporter started correctly once credentials arrived.

14. **Pydantic ValidationError crashes hook with RuntimeError**: setting `experimental_alive_check="not-valid-format"` (rv-deep4, rv-deep5, reproduced twice) did not produce `BlockedStatus`. Instead the hook failed with `RuntimeError: Unknown error object: I`. Root cause at `charm_state.py:342-359`: the `to_pebble_check` validator raises `pydantic.v1.error_wrappers.ValidationError("message", cls)`, but the real constructor expects `errors` (a list of `ErrorWrapper`), not a string. When `from_charm()` calls `exc.errors()` at line 505, `flatten_errors` hits the unexpected error object (the model class `cls`, printed as `I`) and raises `RuntimeError`. The `BlockedStatus` path in `inject_charm_state` is never reached — the operator sees `error: hook failed: "config-changed"`. The same crash was reproduced with `publish_rooms_allowlist="not,a,user,!bad:room"` (`userids_to_list`, line 317/321) and with `public_baseurl="bad"` (unconfirmed whether this hits the same validator or a separate URL-parsing path).

15. **register-user action** (rv-deep5): succeeded but generated a random password (`QRXpqlKzj07k33zU` / `NfaNOmBOYpJC8YSx` across runs) because `actions.yaml` has no `password` parameter; `User.__init__` unconditionally generates one.

16. **promote-user-admin and anonymize-user actions** (rv-deep5): both succeeded with Postgres available.

17. **All four backup actions without S3** (rv-deep5): `create-backup`, `list-backups`, `restore-backup`, `delete-backup` all failed gracefully with clear error messages.

18. **Bad config recovery — server_name**: setting `server_name=bad!!hostname!!` correctly produced `BlockedStatus: The server_name modification is not allowed, please check the logs`. Restoring recovered cleanly.

19. **Bad config recovery — ip_range_whitelist**: setting `"not.valid!!!"` correctly blocked both units. Only `--reset` cleared it; setting an empty string did not, since the regex rejects empty strings too.

20. **Bad config — trusted_key_servers**: setting `'[{"server_name": "bad!!host"}]'` (rv-deep5) correctly produced `BlockedStatus: invalid configuration: trusted_key_servers`.

21. **Bad config — federation_domain_whitelist silently accepted**: setting `"bad!!hostname"` (rv-deep5) was accepted with no `BlockedStatus`. No validation exists for this field, confirmed both at the `config.yaml` level (no regex) and in `charm_state.py` (no custom validator).

22. **report_stats bad config rejected at Juju level**: setting a non-boolean value for `report_stats` was rejected by the Juju CLI itself (`type: boolean`), never reaching the charm.

23. **Pod restart recovery**: `kubectl delete pod synapse-0` → pod recreated, synapse `active` again in ~30s. After a single-unit pod restart: federation-sender correctly absent (no instance_map), `synapse-cron` active, but `worker.yaml` still present on disk (219 bytes) despite no service using it.

24. **Refresh between revisions**: `juju refresh synapse --channel latest/stable` (edge→stable, rev 523→426) triggered a clean transition; image re-pull took ~5 minutes and synapse came back `active`.

### Redis removal and scale-down with 2 units (rv-deep5)

25. **Redis removal leaves both units active with services in backoff**: after `juju remove-relation synapse redis-k8s` with 2 units deployed, both units kept `active`. Unit 0's `synapse-federation-sender` crashed with `AssertionError: assert self.config.redis.redis_enabled`; unit 1's `synapse` (worker) crashed with `AssertionError: not self.streams` (`ReplicationStreamer.__init__`). `homeserver.yaml` was correctly regenerated without the `redis` section, but `worker.yaml` still referenced Redis-dependent workers and was never cleaned up. `redis_required` (`charm_state.py:499`, computed as `redis_config is None and planned_units > 1`) should have been `True` but wasn't — during the `relation-broken` hook, `planned_units()` still returns 2 and relation data is still accessible.

26. **Scale-down after Redis removal — federation-sender persists in backoff**: after scaling back to 1 unit, `synapse-federation-sender` remained in `backoff` and `worker.yaml` (219 bytes, `root:root`) stayed on disk. The charm reported `active` throughout.

### Metrics and integrations

27. **Memory usage** (postgres + redis, 2 units, rv-deep3): synapse-0 302Mi, synapse-1 192Mi, postgresql-k8s 363Mi, redis 47Mi.

28. **Traefik integration**: `juju integrate synapse traefik-k8s` correctly updated `public_baseurl` from `https://example.com` to `http://10.43.45.0/rv-synapse-synapse`.

29. **S3 media integration**: `homeserver.yaml` correctly contained the media storage provider config with credentials set via `sync-s3-credentials`.

30. **Grafana-agent integration**: promtail started (`disabled, active` in Pebble), forwarding logs to Loki. Grafana dashboard and Prometheus metrics endpoints established correctly.

31. **SMTP integrator**: relation established but the integrator was `blocked` (no host configured); synapse remained `active` — the charm handles a blocked SMTP relation gracefully.

32. **Juju 4.x compatibility**: synapse deployed cleanly on Juju 4.0.5 with SQLite; Postgres could not be integrated because 14/stable requires Juju < 4.0.0. No Juju-version-specific behaviour differences observed for the parts that could be tested.

33. **Config mismatch — deployed vs local source**: deployed revision 523 lacks the `rate_limiting_level` and `max_upload_size` config options present in local `config.yaml`. Local HEAD also declares `SYNAPSE_VERSION=1.146.0` while rev 523 runs 1.120.0.

34. **homeserver.yaml file ownership**: `/data/homeserver.yaml` is owned `root:root` (644). `_push_synapse_config()` (`pebble.py:232`) calls `container.push(config_path, ...)` without `user`/`group`. Synapse itself runs as `synapse:synapse` (`pebble.py:360`). Other files under `/data/` (keys, db) are correctly owned `synapse:synapse`.

## Findings

### Database relation removal not handled — Synapse stays on stale Postgres config
- **Severity**: critical
- **Kind**: bug
- **Where**: `src/database_observer.py:39-40` (no relation-broken handler), `src/charm.py:140-153`
- **Evidence**: After `juju remove-relation synapse postgresql-k8s` (confirmed in two separate runs), synapse remained `active` with `homeserver.yaml` still pointing at the removed Postgres endpoint. `DatabaseObserver` registers only `_on_database_created` and `_on_endpoints_changed`. No handler exists for relation-broken or relation-departed. Compare with SAML's `_on_saml_relation_broken` (`charm.py:421`). Debug-log confirmed both hooks fired.
- **Impact**: When the DB relation is removed, Synapse keeps talking to the old Postgres, which may eventually be destroyed. No fallback to SQLite. Recovery requires manual intervention.
- **Fix**: Add a `_on_database_broken` handler that triggers a reconcile so the charm regenerates config without the datasource.
- **Linter rule**: "Observer registers relation-created/changed but not relation-broken" — checkable per observer/relation pair.

### Pydantic validators raise ValidationError with wrong constructor args, crash the hook
- **Severity**: critical
- **Kind**: bug
- **Where**: `src/charm_state.py:505` (`from_charm` calls `exc.errors()`); validators at `src/charm_state.py:296` (`roomids_to_list`), `:317` (`userids_to_list`), `:342-359` (`to_pebble_check`)
- **Evidence**: These validators raise `pydantic.v1.error_wrappers.ValidationError("msg", cls)` — the real constructor expects `errors` (a list of `ErrorWrapper`), not a string. When `from_charm` calls `exc.errors()` at line 505, `flatten_errors` encounters the unexpected error object and raises `RuntimeError: Unknown error object: I`. Reproduced with `experimental_alive_check="not-valid-format"` and `publish_rooms_allowlist="not,a,user,!bad:room"` across two deployments. The `BlockedStatus` path in `inject_charm_state` is never reached; the operator sees `error: hook failed: "config-changed"` with no actionable message. The same crash pattern was suspected (not fully confirmed) with `public_baseurl="bad"`.
- **Impact**: Any invalid config touching these validators crashes the hook with a traceback instead of setting `BlockedStatus`. Affects `experimental_alive_check`, `publish_rooms_allowlist`, and any other field routed through these validators.
- **Fix**: Replace `raise ValidationError(...)` with `raise ValueError(...)` in all affected validators; Pydantic v1 automatically wraps `ValueError` into a proper `ValidationError`.
- **Linter rule**: "Custom Pydantic validator raises ValidationError instead of ValueError" — mechanically checkable.

### create_registration_secrets_files writes to local filesystem, not workload container
- **Severity**: high
- **Kind**: bug
- **Where**: `src/synapse/workload.py:417`, `src/matrix_auth_observer.py:75-96`
- **Evidence**: `create_registration_secrets_files()` calls `registration_secret.file_path.write_text(registration_secret.value)` at line 417. `file_path` is built from `Path(SYNAPSE_CONFIG_DIR)` where `SYNAPSE_CONFIG_DIR = "/data"` (`workload.py:22`) — but `pathlib.Path.write_text()` writes to the charm container's local filesystem, not the workload container. The `container` parameter is accepted but unused. The unit test `test_matrix_auth_registration_secret_success` mocks this function entirely and only checks call count.
- **Impact**: Matrix-auth appservice registrations are broken — the config references files that never land in the workload container. Synapse would fail to start with those appservices configured.
- **Fix**: Replace `Path.write_text()` with `container.push(str(registration_secret.file_path), registration_secret.value, make_dirs=True)`. Add an integration test that actually deploys a matrix-auth requirer.
- **Linter rule**: "pathlib.Path.write_text called with a workload container path instead of container.push" — mechanically checkable if the path starts with a known container mount point.

### Worker.yaml and federation-sender not cleaned up on scale-down or Redis removal
- **Severity**: high
- **Kind**: bug
- **Where**: `src/pebble.py:382-391` (worker.yaml pushed unconditionally; federation sender restarted only when `instance_map_config is not None`), `src/charm.py:224-226` (`redis_required` check races with relation-broken)
- **Evidence**: After scaling 2→1 with Redis already removed, the federation-sender remained in `backoff` with `worker.yaml` still on disk. `reconcile()` pushes `worker.yaml` at lines 382-386 regardless of `instance_map_config` and only restarts the federation sender when it is not `None` (line 391); the old Pebble layer is never removed. With 2 units and Redis removed, both services crashed — federation-sender with `AssertionError: assert self.config.redis.redis_enabled`, worker synapse with `AssertionError: not self.streams` — while the `redis_required` guard at `charm.py:224` failed to fire because `planned_units()` still returns the pre-removal count during relation-broken. Charm status remained `active` throughout.
- **Impact**: Stale services sit in `backoff` with no visible indication; both the federation sender and worker synapse fail silently. The intended safety net (`redis_required`) doesn't fire during Redis removal.
- **Fix**: When `instance_map_config` is `None`, stop and remove the federation-sender layer and skip writing `worker.yaml`. Regenerate `worker.yaml` without Redis-dependent config when Redis is removed. Fix `redis_required` to account for a departing relation reducing effective unit count below `planned_units()`.
- **Linter rule**: "Pebble layer added but never removed" — not easily checkable.

### register-user action generates a random password; README misleading
- **Severity**: medium
- **Kind**: bug / docs
- **Where**: `actions.yaml` (no `password` param), `src/user.py:42` (`_generate_password()`), `README.md:50`
- **Evidence**: README documents `juju run synapse/0 register-user username=alice password=<secure-password>`, but `actions.yaml` has no `password` property and `User.__init__` unconditionally calls `_generate_password()`. Observed: supplying `password=testpass123` still returned a random password (`NfaNOmBOYpJC8YSx` / `QRXpqlKzj07k33zU` across runs).
- **Impact**: Operators expect the password they supply to be used; the random one is easily missed in action output.
- **Fix**: Either add `password` to `actions.yaml` and honor it, or remove it from the README and document the random-password behaviour explicitly. The README is currently misleading.
- **Linter rule**: "Action parameter in README not present in actions.yaml" — mechanically checkable.

### Cron service not started automatically on first deploy
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/pebble.py:90-98` (`restart_synapse`)
- **Evidence**: After deploy, `pebble services` consistently showed `synapse-cron: enabled, inactive` (observed across all models on both rev 523 and rev 426, and on Juju 4.x). `restart_synapse()` adds the cron layer via `container.add_layer` but only calls `container.restart(SYNAPSE_SERVICE_NAME)` — never `container.start(SYNAPSE_CRON_SERVICE_NAME)`, and no replan. Compare with `replan_mjolnir` (line 160) and `replan_synapse_federation_sender` (line 202), which both call `container.replan()`. After pod restart, cron reliably became active.
- **Impact**: The cron service runs `cleanup.py` for media retention; without it, old media accumulates indefinitely until the first pod restart.
- **Fix**: Add `container.start(synapse.SYNAPSE_CRON_SERVICE_NAME)` after `add_layer`, or call `container.replan()`.
- **Linter rule**: "Pebble layer with startup=enabled added but no explicit start/replan" — partially checkable.

### Missing container.can_connect() guard in backup/restore actions
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/backup_observer.py:94-97` (create), `:186-189` (restore)
- **Evidence**: `_on_create_backup_action` and `_on_restore_backup_action` fetch the container and call `container.exec(...)` without checking `container.can_connect()`. If the container isn't ready, this raises an unhandled `ops.pebble.ConnectionError` rather than calling `event.fail()`. `_on_delete_backup_action` doesn't touch the container and is unaffected.
- **Impact**: Actions fail with a Python traceback instead of a user-friendly error message.
- **Fix**: Add `if not container.can_connect(): event.fail("Container not ready"); return` at the top of each affected handler.
- **Linter rule**: "Action handler calls container.exec/push/pull without a can_connect() guard" — mechanically checkable.

### stats-exporter started with empty DB credentials, crashes silently
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/pebble.py:175-186`
- **Evidence**: On initial deploy (reproduced on two separate models), `PROM_SYNAPSE_PORT` was set to `""` because the database relation hadn't yet delivered credentials, crashing the exporter with `ValueError: invalid literal for int() with base 10: ''`. Pebble runs it with `on-failure: ignore` (`pebble.py:525`), and the charm catches the resulting `ops.pebble.Error` and logs only at DEBUG (`pebble.py:182-185`: "Ignoring error while restarting Synapse Stats Exporter"). Pebble plan showed `stats-exporter: startup: disabled` in this state. The exporter started correctly once credentials arrived.
- **Impact**: The exporter is silently broken until database credentials arrive, with no visible status change; on slow database integrations this gap can last minutes.
- **Fix**: Don't start the stats-exporter until the datasource is fully populated, or surface a `WaitingStatus`/`MaintenanceStatus` while it can't start.
- **Linter rule**: "Pebble service started with environment variables that may be empty" — partially checkable.

### federation_domain_whitelist lacks any validation
- **Severity**: medium
- **Kind**: bug
- **Where**: `config.yaml` (`federation_domain_whitelist`, `type: string`, no pattern), `src/charm_state.py` (no custom validator)
- **Evidence**: Setting `federation_domain_whitelist="bad!!hostname"` (rv-deep5) was accepted with no `BlockedStatus`. Unlike `ip_range_whitelist` (regex `r"^[\.:,/\d]+\d+(?:,[:,\d]+)*$"`) or `publish_rooms_allowlist` (`userids_to_list` validator), this field has neither a `config.yaml` pattern nor a Pydantic validator.
- **Impact**: An operator setting this field will believe it took effect; Synapse will later fail with a cryptic error from the generated homeserver config.
- **Fix**: Add a regex pattern in `config.yaml` or a custom Pydantic validator.
- **Linter rule**: "Charm config string field with no validation pattern" — mechanically checkable.

### Redis removal with 2+ units never reaches the redis_required guard
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm_state.py:499`, `src/charm.py:224-226`
- **Evidence**: After `juju remove-relation synapse redis-k8s` with 2 units, both units remained `active` with services in `backoff` (see observed-behaviour #25). `redis_required` is computed as `redis_config is None and planned_units > 1`, but during `relation-broken`, `planned_units()` still returns 2 and the redis library's relation data may still be present, so `redis_required` evaluates `False` when it should be `True`.
- **Impact**: The primary safety mechanism preventing multi-unit deployment without Redis fails specifically during Redis removal, leaving workers crashing silently under `active` status.
- **Fix**: Either compute `redis_required` from actual relation membership rather than `planned_units()` alone, or add a `_on_redis_relation_broken` handler that explicitly transitions to a blocking state.
- **Linter rule**: not mechanically checkable.

### CharmState rebuilt and fully logged on every relation event
- **Severity**: low
- **Kind**: performance
- **Where**: `src/charm.py:153` (`build_charm_state()`), `src/charm_state.py:478-479` (`from_charm` logging)
- **Evidence**: Every relation-changed event triggers `build_charm_state()` → Pydantic validation → `logger.info("parsed synapse config: %s", ...)`. A single DB relation change produced 6+ duplicate INFO log lines with the full config dump.
- **Impact**: Adds log noise and measurable hook latency on busy systems.
- **Fix**: Move the config log to DEBUG; consider caching CharmState and invalidating only on relevant events.
- **Linter rule**: "Charm config logged at INFO level with full dump" — checkable.

### worker.yaml pushed unconditionally even on single-unit deployments
- **Severity**: low
- **Kind**: bug
- **Where**: `src/pebble.py:382-386`
- **Evidence**: `reconcile()` pushes `worker.yaml` regardless of `instance_map_config`. After a pod restart with 1 unit, `worker.yaml` existed on disk (219 bytes, `root:root`) with no Pebble service referencing it.
- **Impact**: Unused config files on disk are confusing and a potential source of future misbehaviour if a later reconcile misreads the stale file.
- **Fix**: Only push `worker.yaml` when `instance_map_config is not None`.
- **Linter rule**: "Pebble config file pushed unconditionally regardless of state" — partially checkable.

### Password/secret exposure in Pebble environment variables
- **Severity**: low
- **Kind**: ux
- **Where**: `src/synapse/workload.py:32` (config path), `:237-240` (env vars with credentials), `src/pebble.py:175-185` (stats-exporter env)
- **Evidence**: `pebble plan` reveals `PROM_SYNAPSE_PASSWORD` and `POSTGRES_PASSWORD` in plaintext; `homeserver.yaml` contains `password`, `macaroon_secret_key`, and `registration_shared_secret` in plaintext.
- **Impact**: Anyone with `kubectl exec` access into the container can retrieve DB credentials. The stats-exporter password specifically is a charm construct that could be passed via file instead.
- **Fix**: Pass stats-exporter DB credentials via a file rather than an environment variable; document the security model for `homeserver.yaml`.
- **Linter rule**: not mechanically checkable.

### Config mismatch between deployed revision and local source
- **Severity**: low
- **Kind**: docs / test-gap
- **Where**: `config.yaml` (local) vs deployed revision 523
- **Evidence**: Revision 523 lacks the `rate_limiting_level` and `max_upload_size` config options present locally (`juju config` returns `unknown option`). Local HEAD also declares `SYNAPSE_VERSION=1.146.0` (`charm.py:66`) while rev 523 runs 1.120.0.
- **Impact**: Reviewers or operators comparing deployed behaviour to source will hit features that exist in source but not in the published revision.
- **Fix**: Publish a new revision including these options.
- **Linter rule**: not mechanically checkable.

### `_on_s3_credential_gone` unconditionally sets ActiveStatus
- **Severity**: low
- **Kind**: bug
- **Where**: `src/backup_observer.py:74`
- **Evidence**: When S3 credentials are removed, `_on_s3_credential_gone` sets `self._charm.unit.status = ops.ActiveStatus()` directly. If the charm was in `BlockedStatus` from a different path (e.g. invalid media S3 config, `charm.py:316`), this overwrites it unconditionally.
- **Impact**: An operator removing S3 backup credentials may see `active` even while a different integration is genuinely broken — a status-precedence bug.
- **Fix**: Don't set `ActiveStatus` directly; trigger a reconcile and let the charm's status resolution decide.
- **Linter rule**: not mechanically checkable.

### macaroon_key.write_to_container silently returns on missing secret
- **Severity**: low
- **Kind**: bug
- **Where**: `src/macaroon_key.py:67-74`
- **Evidence**: `write_to_container()` uses `if secret:` — if the secret is missing, it silently returns `None` with no log message. Compare `signing_key.py:65-66`, which raises `SigningKeyWriteError` in the equivalent situation. The caller at `charm.py:200` does not check the return value.
- **Impact**: If the macaroon key secret is missing on a non-leader unit, the key file is silently absent; Synapse may fail unexpectedly or fall back to a default key.
- **Fix**: Log at WARNING or raise an error consistent with `signing_key`'s behaviour.
- **Linter rule**: not mechanically checkable.

### rate_limiting_level validator silently swallows invalid values
- **Severity**: low
- **Kind**: bug
- **Where**: `src/charm_state.py:363-380`
- **Evidence**: `validate_rate_limit` catches `ValueError`, logs an error, and returns the default value instead of rejecting the config. The charm shows `active` with no indication the value was ignored.
- **Impact**: An operator setting `rate_limiting_level=invalid` will believe it took effect when it was silently discarded.
- **Fix**: Either raise `ValueError` to produce `BlockedStatus`, or surface a maintenance-status message. The current silent-swallow is the worst of both options.
- **Linter rule**: "Pydantic validator catches exception and returns default without raising" — mechanically checkable.

### Invalid ip_range_whitelist clears only with --reset
- **Severity**: low
- **Kind**: ux
- **Where**: `config.yaml` (`ip_range_whitelist` regex `r"^[\.:,/\d]+\d+(?:,[:,\d]+)*$"`), `src/charm_state.py:237`
- **Evidence**: After setting an invalid value, `juju config ip_range_whitelist=""` does not clear the `BlockedStatus` because the empty string also fails the regex; only `juju config --reset ip_range_whitelist` works.
- **Impact**: Operators may reasonably expect setting an empty string to clear the error.
- **Fix**: Document that `--reset` is required to clear this field.
- **Linter rule**: not mechanically checkable.

### homeserver.yaml owned by root despite synapse running as its own user
- **Severity**: nit
- **Kind**: ux
- **Where**: `src/pebble.py:232`
- **Evidence**: `_push_synapse_config()` calls `container.push(config_path, ...)` without `user`/`group`, leaving `/data/homeserver.yaml` owned `root:root` (644) while Synapse runs as `synapse:synapse` (`pebble.py:360`). Other files under `/data/` are correctly owned `synapse:synapse`.
- **Impact**: Inconsistent ownership; a future permission-hardening change could accidentally break Synapse's ability to read its own config.
- **Fix**: Pass `user=SYNAPSE_USER, group=SYNAPSE_GROUP` to `container.push()`.
- **Linter rule**: "container.push without user/group when service runs as a specific user" — mechanically checkable.

### redis_required typed Optional[bool] but always assigned bool
- **Severity**: nit
- **Kind**: lint
- **Where**: `src/charm_state.py:413` (annotation `typing.Optional[bool]`), `:499` (assignment always `bool`)
- **Evidence**: `redis_required` is declared `Optional[bool]` but assigned `redis_config is None and planned_units > 1`, which is always a `bool`, never `None`.
- **Impact**: Misleading type annotation for readers.
- **Fix**: Change annotation to `bool`.
- **Linter rule**: "Optional type annotation on variable that is never None" — checkable with static analysis.

### rate_limiting_level type annotation mismatch
- **Severity**: nit
- **Kind**: lint
- **Where**: `src/charm_state.py:223`
- **Evidence**: `rate_limiting_level: str = Field(None)` — annotated `str` but defaults to `None`.
- **Impact**: Static type checkers should flag this; other fields in `SynapseConfig` share the pattern.
- **Fix**: Use `Optional[str] = Field(None)`.
- **Linter rule**: "Field default is None but type annotation doesn't include None" — checkable with mypy/pyright.

### Unit test suite uses deprecated Harness
- **Severity**: nit
- **Kind**: test-gap
- **Where**: `tests/unit_harness/conftest.py` and 20+ test files
- **Evidence**: All 191 tests in `tests/unit_harness/` use the deprecated `ops.testing.Harness` (141 `PendingDeprecationWarning`s). Docs recommend `ops-scenario`, already used in `tests/unit/`.
- **Impact**: Harness will eventually be removed from `ops`; these tests will break.
- **Fix**: Migrate to `ops-scenario`.
- **Linter rule**: "Use of deprecated ops.testing.Harness" — mechanically checkable.

### No update-status handler
- **Severity**: nit
- **Kind**: test-gap
- **Where**: `src/charm.py`
- **Evidence**: No `update-status` event handler; the charm relies entirely on relation-changed, config-changed, pebble-ready, and upgrade-charm events.
- **Impact**: If Synapse crashes without triggering a Pebble event, or a secret changes outside an observed event, the charm won't self-repair until the next relevant event. This would catch the federation-sender-in-backoff issue above.
- **Fix**: Add an update-status handler that checks service health and re-reconciles if needed.
- **Linter rule**: "Charm without update-status handler" — mechanically checkable.

### is_main uses a fragile substring check
- **Severity**: nit
- **Kind**: bug
- **Where**: `src/charm.py:186-191`
- **Evidence**: `is_main` returns `f"/{MAIN_UNIT_ID}" in self.unit.name`. With `MAIN_UNIT_ID=0`, `"/0" in "synapse/10"` is `True`, which would incorrectly identify unit 10 as main. Not currently triggerable with single-digit unit counts, but fragile.
- **Impact**: Breaks silently if the charm is ever scaled to 10+ units.
- **Fix**: Use `self.unit.name.endswith(f"/{MAIN_UNIT_ID}")` or split on `/` and compare.
- **Linter rule**: not easily checkable.

### Deprecated JujuVersion.from_environ() and untested AdminAccessTokenService
- **Severity**: nit
- **Kind**: lint / test-gap
- **Where**: `src/admin_access_token.py:19`, `:28`
- **Evidence**: `JUJU_HAS_SECRETS = JujuVersion.from_environ().has_secrets` triggers a `DeprecationWarning` at module load. The class is marked `# pragma: no cover` with a TODO.
- **Impact**: Deprecated API will eventually be removed; untested code handling admin access tokens is a security-sensitive test gap.
- **Fix**: Move the check into an instance method using `self.model.juju_version`; add unit tests for the class.
- **Linter rule**: "Deprecated JujuVersion.from_environ() call" — mechanically checkable.

## Worth copying

1. **CharmState with Pydantic validation** (`src/charm_state.py`): Pydantic v1 models with custom validators handle type coercion (`report_stats` → yes/no), default inference (`notif_from` from `server_name`), and complex formats (`experimental_alive_check` comma-separated parsing, `publish_rooms_allowlist` regex validation). Catches bad config early — provided validators raise `ValueError` and not `ValidationError` (see finding above).
2. **inject_charm_state decorator** (`src/charm_state.py:73`): builds CharmState, catches validation errors, sets `BlockedStatus` for hooks or fails actions, with a thoughtful `isinstance(event, ops.charm.ActionEvent)` distinction. DRY error handling across many handlers.
3. **Observer pattern** (`src/database_observer.py`, `src/backup_observer.py`, `src/matrix_auth_observer.py`): each relation encapsulated in its own observer class emitting reconcile calls, keeping `charm.py` manageable despite 9+ integrations.
4. **DeepDiff for change detection** (`src/pebble.py:298-302`): compares current vs proposed config before restart, avoiding unnecessary Synapse restarts.
5. **Config validation pre-push** (`src/synapse/workload.py:241`): runs `synapse validate_config` before pushing, catching semantic errors Pydantic can't see.
6. **Signing/macaroon key two-step** (`src/signing_key.py`, `src/macaroon_key.py`): leader generates keys → stores as Juju secrets → non-leaders read from secrets, using `MaintenanceStatus` (not error) for missing secrets since a later event may resolve it. Note the documented asymmetry: `macaroon_key.write_to_container()` silently returns while `signing_key.write_to_container()` raises.
7. **S3 backup design** (`src/backup.py`): streaming pipe (tar → gpg → aws s3 cp) with size pre-calculation, MinIO path-quirk handling, and `set -euxo pipefail` in the bash pipeline.
8. **Integration test quality** (`tests/integration/test_charm.py`): asserts actual HTTP responses, content, and status codes, not just idle/active status. `test_synapse_enable_smtp` verifies specific error responses confirming SMTP is actually configured.

## Common-practice notes

- **ops 3.8.0**: modern `ops` usage with `pebble.Check` objects; follows current conventions.
- **charmcraft.yaml**: uses `charm-binary-python-packages` for native extensions (`psycopg2-binary`, `cryptography`). Standard.
- **Library versions**: ships v1 `matrix_auth`, v0 `s3`, v2 `traefik_k8s.ingress` — current.
- **pydantic.v1 import**: uses the v1 compat layer — migration debt.
- **No terraform module**: unlike some IS DevOps charms.
- **Bundled OCI rock** (`synapse_rock/`): NGINX, Synapse, Mjolnir, cron, stats-exporter in one image — practical, but makes the image large (~400MB).

## Tests

- **Unit tests** (`tests/unit/`): 9 passing, covering charm state injection, database, SMTP, Mjolnir, backups, and scaling via `ops-scenario`. Sub-second in coverage run.
- **Unit tests** (`tests/unit_harness/`): 191 passing, 14 xfail. Covers backup, API, workload config, actions, database, SMTP, media, observability, matrix-auth, charm state injection.
- **Total**: 200 passing, 14 xfail, 141 `PendingDeprecationWarning`s from Harness. `tox -e unit` completes in ~6.3-6.5s.
- **XFAIL tests**: 14 tests in `test_synapse_workload.py` document known edge cases with regex-based validators (e.g. leading whitespace in IP ranges, empty strings). Good practice.
- **Integration tests**: `test_charm.py` (core + SMTP + nginx + Mjolnir + user actions + workload version), `test_scaling.py` (Redis-required scaling with HTTP assertions), `test_s3.py`, `test_matrix_auth.py`, `test_nginx.py`. Assert actual HTTP responses. `test_synapse_scale_blocked` uses `raise_on_blocked=True`, a testing mode that may not match production event ordering.
- **Coverage target**: 88% branch coverage (`pyproject.toml`). `AdminAccessTokenService` is explicitly excluded (`# pragma: no cover`). Lowest-coverage files: `mjolnir.py` (62%), `signing_key.py` (70%), `workload_configuration.py` (79%).
- **Linters**: `tox -e lint` → pylint 10.00/10. `tox -e static` (bandit) → 0 High/Medium/Low. `mypy` → no issues in 55 source files. `codespell` → 3 false positives (`showIn` in Grafana JSON, already excluded).
- **Test gaps relative to findings**:
  1. `create_registration_secrets_files` is mocked entirely in unit tests; no test catches the wrong-filesystem write.
  2. No test for database relation removal (broken/departed).
  3. No test for stats-exporter with empty DB credentials (DEBUG-only error path).
  4. `AdminAccessTokenService` entirely untested.
  5. No integration test reliably exercising matrix-auth appservice registration (`test_matrix_auth.py` uses CMR and may not run in standard CI).
  6. No test for macaroon key write failure vs signing_key's raise.
  7. No test exercising the `ValidationError`→`RuntimeError` crash path for any of the four affected validators.
  8. No test for worker.yaml/federation-sender cleanup on scale-down or Redis removal.
  9. No test for Redis relation removal producing `BlockedStatus` (the `planned_units()` race).
  10. No test for `federation_domain_whitelist` validation (field has none).
  11. No test for `_on_s3_credential_gone` overwriting an existing blocked status with `ActiveStatus`.

## Docs

- **README**: comprehensive but has the misleading `password=<secure-password>` example for `register-user`. Charmhub description matches.
- **docs/ directory**: Diátaxis structure (tutorial, how-to, reference); comprehensive for backup/restore, SMTP config, horizontal scaling.
- **config.yaml**: options well documented with descriptions referencing upstream Synapse docs.
- **actions.yaml**: descriptions clear; `register-user` doesn't mention the password is auto-generated.
- **CONTRIBUTING.md**: detailed; `.github/pull_request_template.md` present.

### Lint tool results
- **pylint**: 10.00/10
- **mypy**: no issues found in 55 source files
- **bandit**: 0 High, 0 Medium, 0 Low (19 lines skipped via `# nosec`)
- **codespell**: 3 false positives, already excluded from tox config
- **black / isort / flake8 / pydocstyle**: all passing
- **Coverage**: 88% (meets target)

## Open questions

1. **redis_required race, both directions**: the guard at `charm_state.py:499` uses `planned_units()`, which races with the controller in both directions — failing to block on Redis removal (planned_units still shows the old, higher count) and possibly failing to block on scale-up (planned_units may lag behind the actual scale-out). `test_synapse_scale_blocked` uses `raise_on_blocked=True`, which forces a different event order than production. A more robust check would look at actual peer-relation membership rather than `planned_units()` alone.
2. Is `synapse-cron` staying inactive on first deploy a Pebble quirk around `startup: enabled` combined with `add_layer(combine=True)`, or does the cron process exit immediately on first start? Pebble logs for `synapse-cron` were empty in the affected runs.
3. `AdminAccessTokenService` stores the token both as a Juju secret and as a raw value — is the raw storage needed for performance, or could it derive from the secret alone? Untested, so hard to validate either way.
4. Why does `macaroon_key.write_to_container()` silently return on a missing secret while `signing_key.write_to_container()` raises? The asymmetry is undocumented and could mask issues during horizontal scaling.
5. Is `rate_limiting_level`'s silent-swallow-and-default behaviour deliberate (to avoid blocking on a field with a safe default) or an oversight? It's inconsistent with the charm's other validators, which reject invalid input.
