# landscape-server-operator

A mature, well-structured machine charm for deploying Self-Hosted Landscape Server. It manages a multi-process Landscape deployment including API, appserver, message-server, pingserver, package-search, package-upload, hostagent, and an outbox snap. The charm has strong config validation via Pydantic, good use of ops patterns, and a comprehensive test suite. It deploys and operates correctly on LXD with PostgreSQL and RabbitMQ relations. The main concerns are a secret-token leak into error logs, unnecessary service restarts on every config change, and broken unit tests that crash pytest at session teardown.

| | |
|---|---|
| Repo | canonical/landscape-server-operator @ b753f20 (2026-07-17) |
| Charms | landscape-server |
| Substrate | machine |
| Deployed | yes — concierge-lxd, landscape-server 26.04/edge (rev 472) |
| Reviewed | 2026-08-25 |

## What it does

The landscape-server charm deploys and configures Canonical's Self-Hosted Landscape Server — a multi-process Python/Fortran systems-management platform. It owns the full lifecycle: installing packages from a PPA and snaps, configuring `/etc/landscape/service.conf` and `/etc/default/landscape-server`, setting up systemd drop-ins for deployment-mode and analytics-id, establishing PostgreSQL and RabbitMQ connections, wiring HAProxy frontends (legacy `website` relation + modern `haproxy-route` relations), publishing COS metrics, writing GPG credentials from Juju secrets, and managing the landscape-outbox snap. It also provides a `cos-agent` integration, `nrpe-external-master` monitoring, `debarchive` and `task-handler` cross-charm integrations, and SMTP relay configuration.

## Deployment log

**Model**: `rv-ls-test` on `concierge-lxd` (Juju 3.6.27, LXD)

**Charm deployed**: `landscape-server` from charmhub `26.04/edge` rev 472 (2026-08-25). This is newer than the local `HEAD` (`b753f20`, 2026-07-17); the local code may be slightly behind the published 26.04/edge revision.

```
juju add-model rv-ls-test localhost/localhost -c concierge-lxd
juju deploy landscape-server --channel 26.04/edge --base ubuntu@24.04
```

**Machine provisioning**: 1 machine (`juju-3e33e4-0`) provisioned and running, 3 machines total after adding PostgreSQL and RabbitMQ.

**Install hook timeline** (all on machine 0, landscape-server unit):
- 20:07:02 — install hook starts: PPA added, `needrestart` removed, landscape-server + landscape-hashids installed from PPA `ppa:landscape/self-hosted-beta`, landscape-outbox snap installed
- 20:10:18 — install hook completes
- 20:10:18 — replicas-relation-created, leader-elected hooks fire; leader elected
- 20:10:23 — config-changed fires; config validated, snap refreshed, GPG configured (no secret set), secret-token and cookie-encryption-key generated and written, services started
- 20:10:25 — start hook fires; services start
- 20:10:26 — replicas-relation-changed fires; "HTTP traffic is allowed alongside HTTPS" warning logged (expected with redirect_https=default)

**Total install time**: ~3 min 16 sec (20:07:02 → 20:10:18).

**Relations added**:
```
juju deploy postgresql --channel 16/stable  # active by 20:14
juju deploy rabbitmq-server --channel latest/edge  # active by 20:15
juju relate landscape-server:database postgresql:database
juju relate landscape-server:inbound-amqp rabbitmq-server
juju relate landscape-server:outbound-amqp rabbitmq-server
```

**Post-relation**: landscape-server transitioned through `maintenance → "Setting up databases"` → `active` in ~2 minutes. Schema bootstrap ran `landscape-schema --bootstrap`, WSL distributions updated, all 10 Landscape services started. Charm reached `active` at 20:21:17.

**Config change test** (`worker_counts=4`): services restarted, ports updated from 8070-8071 to 8070-8073 (4 workers). Hook count for config change: 1 `config-changed` hook. Services restarted confirmed by "Starting services" log line.

**Pause/resume**: pause action completed successfully (services stopped, status maintenance/"Services stopped"). resume action completed successfully (all services active).

**Bad config tests**:
- `redirect_https=invalid_value` → `BlockedStatus` with "Invalid configuration. See `juju debug-log`." ✅
- `appserver_base_port=8080 pingserver_base_port=8080` (port conflict with worker_counts=4) → `BlockedStatus` with detailed port-overlap message. Pydantic `haproxy_backend_port_validation` caught this. ✅
- `migrate-schema` while running → action failed with "Cannot migrate schema while running." ✅

## Observed behaviour

**Service inventory** (after full deployment with worker_counts=4, db + rabbitmq relations):
All 10 Landscape systemd services running:
```
landscape-api.service         (4 workers: ports 9080-9083)
landscape-appserver.service   (4 workers: ports 8080-8083)
landscape-async-frontend.service
landscape-hostagent-consumer.service
landscape-hostagent-messenger.service
landscape-job-handler.service
landscape-msgserver.service  (4 workers: ports 8090-8093)
landscape-package-search.service  (leader-only, port 9099)
landscape-package-upload.service  (leader-only, port 9100)
landscape-pingserver.service  (4 workers: ports 8070-8073)
landscape-secrets-service.service
```
Plus: `landscape-outbox` snap (rev 11, tracking latest/stable).

**Persistent issues observed from logs**:
1. `Cannot modify autoregistration because no account exists.` — logged as ERROR on every hook that calls `_set_autoregistration` (every config-changed, every relation-changed). The error is expected when no admin account is configured, but it is logged at ERROR level, suggesting it is an unexpected condition.
2. "HTTP traffic is allowed alongside HTTPS. This is a security risk" — logged twice per `replicas-relation-changed` hook (one per HAProxy frontend, HTTP and HTTPS). Expected warning with redirect_https=default, but logged at WARNING level every time the replicas relation changes.
3. `min-cluster-size is not defined` warnings from RabbitMQ — from the RabbitMQ charm, not landscape-server.
4. `Cannot modify autoregistration because no account exists.` is also logged at `_migrate_schema_bootstrap` path — this is a duplicate call path.
5. Services restart on every config-changed hook even for trivial changes (confirmed: "Starting services" appears in logs for every config change including `site_name=test-name`).

**Secrets observed**: service.conf contains plaintext `secret_token`, `cookie_encryption_key`, PostgreSQL password, RabbitMQ password, and database credentials. The GPG home dir (`/var/lib/landscape-server/gnupg`) was created with mode 0700.

**Config-error log secret leak**: When an invalid config was submitted (`appserver_base_port=8080 pingserver_base_port=8080`), the ERROR log at `src/charm.py:285` dumped the full Pydantic input dict including `secret_token` value — confirming a live secret was written to the Juju debug log.

## Findings

### Secret token written to Juju debug log on config validation failure
- **Severity**: critical
- **Kind**: bug
- **Where**: `src/charm.py:285`
- **Evidence**: `logger.error(f"Invalid configuration: {e.errors()}")` — `e.errors()` includes the full Pydantic `ValidationError` input dict, which contains `secret_token` and `cookie_encryption_key` values. Observed in debug-log when submitting a port-conflict config:
  ```
  ERROR ... Invalid configuration: [{..., 'input': {'secret_token': 'IqDpccZgsb3xD...',
         'cookie_encryption_key': '8i-e75VXIgMm...', ...}}]
  ```
- **Why it matters**: Juju debug logs are accessible to anyone with model access. A cluster operator reviewing logs to diagnose a bad config change would see all secret tokens and keys in plaintext.
- **Fix**: Sanitize the Pydantic validation error before logging. Either `logger.error("Invalid configuration: %s", e.error())` (which omits input data), or extract only the `loc` and `msg` fields from each error dict.
- **Linter rule**: "Never log Pydantic ValidationError.errors() directly; sanitize to remove `input` field before logging" — not mechanically checkable without AST analysis of all `logger.error` calls with Pydantic errors.

### Services restarted on every config-changed hook without change detection
- **Severity**: high
- **Kind**: performance
- **Where**: `src/charm.py:466` (`_on_config_changed` unconditionally calls `_update_ready_status(restart_services=True)`)
- **Evidence**: Observed in debug-log: "Starting services" appears on every `config-changed` hook invocation, including for truly trivial changes like `site_name=test-name` (which only affects the registration/title, not any service configuration). Hook at 20:23:45 triggered a restart logged at 20:23:41.
- **Why it matters**: In production with frequent config updates (e.g., autoscaling, monitoring), every hook restart causes a brief service outage. The `lsctl restart` call stops and starts all 10 Landscape services. Some config changes (e.g., `site_name`, `nagios_context`) do not require a service restart — only changes to `worker_counts`, port bases, broker connection, db connection, ssl_cert, secret_token, deployment_mode, or GPG credentials require a restart.
- **Fix**: Add change detection before `_update_ready_status(restart_services=True)`. Compute a config-change-hash (or compare a set of restart-relevant keys against stored values) and only restart if something actually changed.
- **Linter rule**: "Hook handler `_on_config_changed` unconditionally calls service restart; add guard to skip restart when no restart-relevant config changed" — not mechanically checkable.

### `_update_wsl_distributions` returns True on FileNotFoundError, masking missing script
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:847-852`
- **Evidence**:
  ```python
  except FileNotFoundError:
      logger.warning(
          "WSL distributions script not found at '%s'; "
          "Landscape may not be installed yet.",
          UPDATE_WSL_DISTRIBUTIONS_SCRIPT,
      )
      return True  # ← treats missing script as success
  ```
- **Why it matters**: If the script is missing for any reason other than "Landscape not installed yet" (e.g., packaging bug, filesystem corruption), the caller proceeds as if WSL distributions were updated. This could leave Landscape in a misconfigured state without any error.
- **Fix**: Return `False` or `None` on `FileNotFoundError`, or add a more specific check (e.g., verify the package is installed before assuming the error is benign).
- **Linter rule**: not mechanically checkable.

### Non-leader units skip WSL distribution update while leader does not
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:1096-1097` (`_database_relation_changed` non-leader path)
- **Evidence**:
  ```python
  if not self.unit.is_leader():
      self._stored.ready["db"] = True
      self.unit.status = ActiveStatus("Unit is ready")
      self._update_ready_status(restart_services=True)
      return  # ← _update_wsl_distributions not called
  ```
  The leader path calls `_update_wsl_distributions()` before setting `ready["db"] = True`.
- **Why it matters**: In a multi-unit HA deployment, non-leader units would not update WSL distributions. The script updates `/var/lib/landscape-server/wsl/distributions` which may be needed on all units. However, this may be intentional (the script may only need to run once on the leader).
- **Fix**: Verify whether WSL distributions must be updated on non-leader units. If not, add a comment explaining why. If yes, add the call to the non-leader path.
- **Linter rule**: not mechanically checkable.

### SMTP postfix config line parsing uses `line.split("=", 1)` — not `split("=", 1)`; silently truncates values with embedded `=`
- **Severity**: low
- **Kind**: bug
- **Where**: `src/charm.py:2253`
- **Evidence**:
  ```python
  key = line.split("=")[0].strip() if "=" in line else None
  ```
  This uses `split("=")` with no limit, so for a line like `smtp_tls_security_level = encrypt --comment`, `key` becomes `"smtp_tls_security_level "` and the value `" encrypt --comment"` would be used. Postfix would then fail to parse the trailing comment, or worse, a malicious value with embedded `=` could override settings unexpectedly.
- **Why it matters**: The current tests use only simple values without embedded `=`, so the bug has not manifested. But Postfix configs can have values with `=` (e.g., from advanced configuration).
- **Fix**: Use `line.split("=", 1)` to properly split on the first `=` only.
- **Linter rule**: "Use `split(delimiter, 1)` when parsing key=value pairs to avoid truncating values with embedded delimiters" — mechanically checkable with ruff `E201`/`E202` or custom rule.

### PostgreSQL password variable shadowed before use — confusing, not a functional bug
- **Severity**: low
- **Kind**: lint
- **Where**: `src/charm.py:1079-1087`
- **Evidence**:
  ```python
  password = db_ctx.password      # from relation
  if landscape_password:
      password = landscape_password  # from config, overrides
  ```
  Then later: `update_db_conf(..., password=password, ...)` — the config password overrides the relation password. This is intentional and correct behavior (config takes precedence). But the variable reuse without a comment makes it unclear whether this is intentional.
- **Why it matters**: Future maintainers may think the relation password is always used. The pattern is correct but the code is confusing.
- **Fix**: Use distinct variable names (`relation_password`, `config_password`) or add a comment explaining the precedence.
- **Linter rule**: not mechanically checkable.

### Unit tests crash pytest at session teardown
- **Severity**: high
- **Kind**: test-gap
- **Where**: `tests/unit/test_settings_files.py:79,87`
- **Evidence**: Running `uv run pytest tests/unit` crashes pytest with:
  ```
  TypeError: Path.replace() takes 2 positional arguments but 3 were given
  ```
  The `fake_open`, `fake_exists`, `fake_remove`, `fake_makedirs` functions all call:
  ```python
  path.replace("/etc/systemd/system", str(tmp_path))
  ```
  But `path` is a `pathlib.Path` object. `Path.replace()` takes exactly 1 argument (the new path). The correct code should be `str(path).replace(...)` or `path.parent / ...`. The mock intercepts `builtins.open` during test teardown, and pytest's own code calls it with a `Path` object, triggering the crash.
- **Why it matters**: Unit tests cannot be run to completion. Coverage is unknown. Developers cannot verify their changes.
- **Fix**: Change all `path.replace(old, new)` calls in the `redirect_systemd_paths` fixture to `str(path).replace(old, new)`.
- **Linter rule**: "Path.replace() called with two arguments; use str.replace() for string replacement or pathlib operations for path operations" — mechanically checkable (ruff has no rule for this specific case).

### `_provide_all_haproxy_route_requirements` called on every config-changed without checking for actual changes
- **Severity**: low
- **Kind**: performance
- **Where**: `src/charm.py:466`
- **Evidence**: `_on_config_changed` unconditionally calls `_provide_all_haproxy_route_requirements()`, which writes to all 8 HAProxy-route relation databags on every config hook. Only changes to `worker_counts`, `root_url`, `unit_ip`, or `leader_ip` actually affect the route data. Most config changes (e.g., `site_name`, `nagios_context`, `analytics_id`) do not change the route requirements.
- **Why it matters**: Unnecessary writes to relation databags, which trigger relation-changed events on the consuming charms. Wastes Juju state-server writes and may cause unnecessary work in peer charms.
- **Fix**: Store a hash of the last-published route requirements and skip publishing if nothing changed.
- **Linter rule**: not mechanically checkable.

## Worth copying

1. **Pydantic config with rich validation** (`src/config.py`): The `LandscapeCharmConfiguration` pydantic model with cross-field validators (`openid_oidc_exclusive`, `haproxy_backend_port_validation`, `oidc_minimum_fields`) is a strong pattern for config safety. The `get_config_defaults()` → `DEFAULT_CONFIGURATION` fallback allows the charm to set a safe default and go to `BlockedStatus` on bad config.

2. **Port conflict detection** (`src/config.py:haproxy_backend_port_validation`): Using `Counter` from `collections` to detect overlapping ports across all workers is elegant and catches real misconfiguration early.

3. **GPG credential handling** (`src/charm.py:_configure_gpg`): The umask trick (`os.umask(0o177)`) before creating the passphrase file, combined with immediate `os.chmod(0o700)` on the directory, is the correct pattern for sensitive file creation.

4. **Atomic certificate writes** (`src/charm.py:_write_outbox_certificates`): Writing to a `.tmp` file, setting permissions, then `os.replace()` is the textbook atomic-write pattern. Well done.

5. **Juju secret lifecycle management** (`src/charm.py:_update_debarchive_relations`, `_update_task_handler_relations`): The pattern of storing a secret ID in the relation databag, reusing it on subsequent calls, and only creating a new secret if the stored ID is stale is correct.

6. **`get_modified_env_vars()` Python path cleaning** (`src/helpers.py`): Explicitly excluding juju paths AND the stdlib paths of the wrong Python version from PYTHONPATH before running subprocesses is careful and necessary for the landscape venv's Python 3.12 vs the charm's Python 3.14 conflict.

7. **`StoredState` for `running`/`paused`/`account_bootstrapped`**: Tracking these lifecycle flags in `StoredState` allows recovery after Juju agent restarts.

8. **`cos_agent` integration** (`src/charm.py:_generate_scrape_configs`): The COS integration is clean, with static scrape configs per service and Grafana dashboards bundled in `src/grafana_dashboards/`.

## Common-practice notes

- **Source layout**: Standard `src/` + `lib/` + `tests/` layout — follows ecosystem convention.
- **Charm libs**: Vendored under `lib/charms/` (data_platform_libs v0.54, grafana_agent v0.25, haproxy v1.13, smtp_integrator v0.21). Declared in `charmcraft.yaml` charm-libs section. Convention followed.
- **Config**: Pydantic models (not ops `ConfigData`) — this is a newer pattern that provides richer validation than the standard ops approach.
- **StoredState**: Still used for lifecycle flags — still common in machine charms. The newer ops pattern would use `context.manager` or `StoredDict`.
- **No `src/` discoverable entrypoint**: The charm uses `charmcraft.yaml` with the `uv` plugin, not a `src/charm.py` dispatch. Convention for modern charms.
- **uv for dependency management**: Project uses `uv.lock` and `pyproject.toml` — current best practice.
- **Terraform modules**: Both `charm/` and `product/` modules present, tested with `make terraform-test-all`. Follows CC006.
- **CI**: GitHub Actions workflows for build, lint, unit tests, release. Convention followed.
- **Copyright headers**: `Copyright 2025 Canonical Ltd` on source, `Copyright 2025-2026 Canonical Ltd` on charm.py — a minor inconsistency. The pyproject.toml version is `0.1.0`.

## Tests

**Unit tests**: `tests/unit/` — pytest + `ops.testing.Harness`. The `TestCharm` class in `test_charm.py` is large and comprehensive. The `redirect_systemd_paths` fixture in `test_settings_files.py` has a bug (see finding) that crashes pytest at session teardown, preventing the test suite from completing. **Result: cannot run to completion.**

**Integration tests**: `tests/integration/test_bundle.py` — jubilant-based, tests the full landscape-scalable bundle. Many tests are skipped when `USE_HOST_JUJU_MODEL` is set (live model). Tests cover: HAProxy redirects, service health, schema migration, COS agent, debarchive/task-handler relations, pause/resume, upgrade action, snap refresh.

**Coverage**: `make coverage` runs coverage with `--branch`. No coverage threshold is enforced in CI.

**Linters**: `make check` runs `ruff check` and `ruff format --check`. **Result: All checks passed.** No lint errors in source or tests.

## Docs

- `README.md`: Brief, links to landscape documentation. Adequate for operators.
- `AGENTS.md`: Good developer onboarding doc with exact commands for unit/integration tests, linting, terraform.
- `CONTRIBUTING.md`: Standard contribution guidelines.
- `terraform/charm/README.md`, `terraform/product/README.md`: Module documentation. Auto-generated from terraform docs.
- `terraform/README.md`: Points to subdirectory READMEs.
- **No charmhub detailed description** visible in the review context — the `charmhub.md` shows the summary but not the full description text.
- **No `docs/` directory** at repo root — all documentation is in `README.md`, `AGENTS.md`, and `CONTRIBUTING.md`.

## Open questions

1. **Is the `_update_wsl_distributions` FileNotFoundError→True intentional?** The comment says "Landscape may not be installed yet" but the script is installed as part of the `landscape-server` package. If the script is missing, it likely means the package is corrupt or misinstalled, not that it's an initial deploy. Should return `False` and log an error.

2. **Why does the non-leader path skip `_update_wsl_distributions`?** If the WSL distributions file needs to be updated on all units (not just leader), the non-leader path should call it too. The current asymmetry should be documented or fixed.

3. **What is the expected behaviour of `_configure_smtp` when postfix config has duplicate keys?** The current code silently keeps the first occurrence. Postfix would use the last occurrence. This is an unusual edge case but worth clarifying the expected behaviour.

4. **The charm ships `landscape-server` as a PPA package, not bundled.** The actual Landscape Server code is not in this repo. The dependency is on `ppa:landscape/self-hosted-beta` or `ppa:landscape/self-hosted-24.04`. The `deps/` directory is empty, confirming this is a pure charm wrapper. The review covered only the charm code, not the Landscape Server package itself.
