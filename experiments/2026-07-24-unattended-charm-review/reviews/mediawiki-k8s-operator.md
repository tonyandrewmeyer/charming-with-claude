# mediawiki-k8s

A well-structured, production-grade Kubernetes charm for MediaWiki, with a clean reconciliation-based architecture (no `defer()`/`StoredState`), strong unit-test coverage, and thorough S3/ClamAV integration tests. In its current state it is **broken on Juju 4.x**: a Kubernetes RBAC gap around `secret.set_content()` causes `leader-elected` to fail permanently and non-leaders to deadlock waiting on the blocked leader — every unit gets stuck in `maintenance`. On Juju 3 the charm works well but has several real correctness gaps: a Pebble `after` field bug (string iterated as a list of single characters), a manually-stopped service that never self-heals because nothing triggers reconciliation outside of hook events, an implicit (unhandled) upgrade path, a rare race in the force-reconciliation flag protocol, and an uninformative error from `rotate-mediawiki-secrets` on Juju 4. A maintainer should first fix the `clamd.after` bug (one-line, high value, easy to test) and then decide how to unblock Juju 4 — either by pre-creating all secret fields at secret-creation time or by getting Juju to grant `patch secrets` to the `juju-secret-consumer` role — since that is what makes the charm currently non-functional on newer Juju.

| | |
|---|---|
| Repo | canonical/mediawiki-k8s-operator @ `beef565` (2026-07-22) |
| Charms | mediawiki-k8s |
| Substrate | k8s |
| Deployed | yes — concierge-k8s-3, 1.46/edge rev 110 (local HEAD = `beef565`) |
| Reviewed | 2026-08-18 |

## What it does

Deploys and manages MediaWiki 1.46 on Kubernetes: Apache + PHP 8, ClamAV antivirus scanning, a Redis-backed job queue, Composer-based extension management, SAML/OAuth authentication, S3 file storage, SMTP email, Loki logging, Prometheus metrics, Grafana dashboards, Traefik ingress routing, and git-sync of static assets from a private repository. A MySQL database relation is mandatory; everything else is optional.

## Deployment log

### Juju 3.6 deployment (primary)

```
juju switch concierge-k8s-3:admin/rv-mwk8s-3
juju deploy mediawiki-k8s --channel 1.46/edge        # rev 110, ubuntu@24.04
juju deploy mysql-k8s --channel 8.0/edge --trust      # rev 434, ubuntu@22.04
juju integrate mediawiki-k8s mysql-k8s:database
```

- MediaWiki image pull took ~2 minutes. Pod `Running` at ~12:09, unit `active` at ~12:11 (~9 minutes deploy to active).
- All Pebble services started: `apache-exporter`, `clamd`, `freshclam`, `logrotate`, `mediawiki`, `mediawikiLogs`.
- Redis job services (`redisJobRunnerService`, `redisJobChronService`) correctly stay `inactive` with no Redis relation.

### Juju 4.x deployment (secondary model) — non-functional

```
juju switch concierge-k8s-4:admin/rv-mediawiki-k8s
juju status
```

A mediawiki-k8s unit was already present on `rv-mediawiki-k8s` (concierge-k8s-4, Juju 4.0.12), stuck in `maintenance` for the entire review period. `leader-elected` fails repeatedly:

```
hook "leader-elected" failed: saving content for secret "...": attempt count exceeded:
secrets "..." is forbidden: User "system:serviceaccount:rv-mediawiki-k8s:juju-secret-consumer-..."
cannot patch resource "secrets" in API group "" in the namespace "rv-mediawiki-k8s"
```

The `juju-secret-consumer-...` Kubernetes Role that Juju 4 creates only grants `get`/`list` on namespaces, no `secrets` permissions. `_replica_secrets()` calls `secret.set_content()`, which requires `patch` on secrets, and fails. The charm cannot progress past `leader-elected`. See Findings below.

### Scale and relation tests

```
juju add-unit mediawiki-k8s
juju integrate mediawiki-k8s:traefik-route traefik-k8s
juju integrate mediawiki-k8s:logging loki-k8s
juju deploy grafana-agent-k8s --channel stable --trust
juju integrate mediawiki-k8s:metrics-endpoint grafana-agent-k8s:metrics-endpoint
```

- Scaling 1→2 units worked; both units reached `active` independently within ~2 minutes.
- Traefik: charm submitted `rule: Host('wiki.example.com')`, routed to `mediawiki-k8s-endpoints.rv-mwk8s-3.svc.cluster.local:80`. Verified end-to-end: `curl -H 'Host: wiki.example.com' http://10.43.45.1/w/api.php?action=query&meta=siteinfo` → 200, MediaWiki 1.46.0.
- Loki: relation established. `loki-k8s` itself was `blocked` on an unrelated RBAC issue in this environment, but the mediawiki-k8s side of the relation was correctly active.
- `juju refresh mediawiki-k8s --channel 1.46/edge` → "already up-to-date" (no newer revision in-channel at review time).
- `grafana-agent-k8s` (rev 233) integrated with `metrics-endpoint`; agent reports `blocked` needing `grafana-cloud-config`/`send-remote-write` — a grafana-agent-k8s configuration gap, not a mediawiki-k8s defect. mediawiki-k8s correctly serves metrics at `http://localhost:9117/metrics`.

### Actions tested (all succeeded on Juju 3)

- `create-and-promote` — created `testadmin` with a generated 64-char password, promoted to bureaucrat/sysop.
- `rotate-mediawiki-secrets` — rotated the Juju secret.
- `force-reconciliation` — triggered immediate reconciliation.
- `update-database` — requested async DB schema update.

### Failure injection

- **`pebble stop mediawiki`** inside the container: service went `inactive`, Juju unit stayed `active`, no hook fired, no self-heal — recovered only via `force-reconciliation` action. See Finding: manually-stopped Pebble service not self-healed.
- **`juju remove-relation mediawiki-k8s mysql-k8s`** → `BlockedStatus("Waiting for relation database")` within ~5s; restoring the relation returned to `active` within ~15s.
- **`kubectl delete pod mysql-k8s-0`** (MySQL outage): pod recreated but Group Replication took several minutes to recover (mysql-k8s infra issue, not mediawiki-k8s). During the outage, MediaWiki API returned HTTP 500 and Pebble check `mediawiki-api-ready` accumulated 26+ failures (threshold 3); the mediawiki container's Kubernetes readiness probe failed. **Juju unit status stayed `active` throughout.** After MySQL recovered, the container self-healed; unit remained `active`.
- **`killall apache2`** inside the mediawiki container: Pebble restarted Apache immediately and invisibly; Juju unit stayed `active` throughout.
- **`create-and-promote` without password/force**: failed with a clear, non-tracebacked message directing the operator to `generate-password=true` or `force=true`.
- **`update-database` on a non-leader unit**: failed cleanly with "Only the leader unit can request a database update".
- **Invalid `ssh-key` secret URI** via `juju config`: rejected by Juju's own config validation before the charm loaded it ("invalid secret URI for option 'ssh-key' ... not valid").
- **Scale down** (`juju remove-unit mediawiki-k8s --num-units 1`): unit removed cleanly, remaining unit stayed `active`.

### Config changes tested

- `url-origin` change → reconciliation → `active` again in ~10s.
- `url-origin=ftp://invalid` → `BlockedStatus("Invalid charm configuration.")` (pydantic scheme validation).
- Setting `url-origin` to its *current* value still fires `config-changed` and a full reconciliation pass (performance finding below).

### Untested integrations

- **S3**: covered by integration tests (Minio, bucket policy, upload+scan), not re-run live during this review.
- **OAuth**: covered by integration tests against a mock provider; code review confirms correct `None` handling.
- **SAML**: covered by integration tests.
- **SMTP**: covered by unit tests (`test_smtp.py`).
- **Redis**: `redis-k8s` does not support `ubuntu@24.04` (only 22.04/20.04), so this integration could not be exercised against the current mediawiki-k8s base.

### Loki behaviour when the target is unreachable

With `loki-k8s` unreachable, the Pebble log fills with repeated:
```
Cannot flush logs to target "loki-k8s/0": Post "http://loki-k8s-0.loki-k8s-endpoints...3100/loki/api/v1/push": dial tcp 10.1.0.233:3100: connection refused
```
Expected Pebble log-forwarding behaviour, not a charm bug — but the noisy retries could mislead an operator who doesn't know to check the `loki-k8s` unit's own status.

## Observed behaviour

- **Pebble plan**: 8 services, 3 checks (`mediawiki-api-ready` at `ready` level; `apache-alive`, `apache-exporter-up` at `alive` level).
- **`clamd.after` bug confirmed**: `pebble plan` shows `"after": ["f","r","e","s","h","c","l","a","m"]` for the `clamd` service — the string `"freshclam"` iterated character-by-character. `mediawiki` correctly has `"after": ["mediawikiLogs"]` (and, redundantly but validly, `"requires": ["mediawikiLogs"]`).
- **MediaWiki API**: `GET /w/api.php?action=query&meta=siteinfo` → 200, MediaWiki 1.46.0, site "CharmedMediaWiki".
- **File permissions**: `LocalSettings.php` `rw-r----- root _daemon_`; `LateSettings.php` and `UserSettings.php` `rw-r----- _daemon_ _daemon_` — correct.
- **Static assets**: `/var/www/html/static -> /mnt/static-assets/repo` — correct.
- **Composer peer sync**: leader publishes `composer.json`/`composer.lock` to peer app data; non-leaders read and mirror it. Verified in relation data.
- **SSH key**: read via `load_charm_config().ssh_key` and validated before use.
- **Proxy config**: `JUJU_CHARM_HTTP_PROXY`/`HTTPS_PROXY`/`NO_PROXY` read and passed to all services.
- **Metrics**: `http://localhost:9117/metrics` returns Prometheus-format Apache metrics (`apache_accesses_total`, `apache_cpu_time_ms_total`, `apache_cpuload`, `apache_duration_ms_total`, `apache_scoreboard`, `apache_workers`, `apache_sent_kilobytes_total`, `apache_received_kilobytes_total`, etc.), verified via `python3` inside the container.
- **Grafana dashboard** (`src/grafana_dashboards/mediawiki.json`): well-structured panels for alerts, Loki logs, Apache version/workers/scoreboard/accesses, request-duration percentiles, load, throughput, CPU, git-sync. Uses `${juju_application}`, `${juju_model}`, `${juju_model_uuid}`, `${juju_unit}`, `${lokids}`.
- **Manually-stopped service, no self-heal**: `pebble stop mediawiki` leaves the service `inactive` indefinitely; no hook fires from a bare `pebble stop`, so `_reconciliation` never runs. Recovery required `force-reconciliation`.
- **Juju 4 failure mode**: `leader-elected` fails on the `patch secrets` RBAC error and loops forever; the unit never leaves `maintenance`. Non-leaders call `_replica_secrets()` in `_pre_reconciliation()`, find missing keys, and raise `MediaWikiWaitingStatusException("Waiting for leader to migrate replica secrets")` — waiting forever because the leader itself is blocked. All units are stuck.
- **MySQL outage**: Juju unit status stayed `active` while the Pebble readiness check failed 26+ times — see finding below.
- **Resource usage** at steady state: 3m CPU, 1164 MiB memory for the mediawiki-k8s pod.
- **OAuth/SAML code**: `article_url_template` can be `None` (missing `articlepath`/`server`); `src/auth.py` correctly raises `MediaWikiBlockedStatusException` in that case, and `special_namespace_name` correctly falls back to `"Special"`.
- **Redis gating**: `runner_queue_service_is_ready()` (`src/mediawiki/_core.py:264`) checks both relation availability and the existence of the job-runner config file before enabling Redis job services.
- **Container command timeout**: `ContainerService._run_cli()` (`src/container.py`) uses a 60-second default timeout and converts a `TimeoutError` into a logged `ContainerError`.

## Findings

### `clamd.after` field receives a string instead of a list

- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:245`
- **Evidence**: `"after": self._FRESHCLAM_SERVICE_NAME,` where `_FRESHCLAM_SERVICE_NAME = "freshclam"` (a plain string). `pebble plan` on the running unit confirms the deployed layer shows `"after": ["f","r","e","s","h","c","l","a","m"]` — nine non-existent service names. `mediawiki` correctly uses `"after": ["mediawikiLogs"]` (a list) at `src/charm.py:200`. ClamAV still starts only because both services have `startup: enabled`, so Pebble starts them regardless of the unsatisfiable ordering constraint.
- **Impact**: The ordering constraint is silently ignored rather than enforced. If ClamAV ever needs a restart, Pebble would wait indefinitely on nine non-existent services if a future Pebble release enforces `after` more strictly; today it's silently harmless but wrong.
- **Fix**: `"after": [self._FRESHCLAM_SERVICE_NAME],` — wrap in a list, matching the pattern already used for `mediawikiLogs`.
- **Linter rule**: mechanically checkable — `isinstance(layer["services"][svc].get("after"), str)` should be false for every service in the Pebble layer dict.

### Juju 4 — `leader-elected` fails permanently on Kubernetes secrets RBAC

- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:317` (`_replica_secrets` → `secret.set_content()`)
- **Evidence**: On `concierge-k8s-4` (Juju 4.0.12), the unit is stuck in `maintenance`; `leader-elected` fails repeatedly with `secrets "..." is forbidden: ... cannot patch resource "secrets"`. The `juju-secret-consumer-...` Kubernetes Role Juju 4 creates grants only `get`/`list` on namespaces, no secrets permissions. The charm calls `secret.get_content(refresh=True)` then `secret.set_content()` to migrate newly-added secret fields on upgrade, and `set_content()` requires `patch` on secrets, which the role lacks.
- **Impact**: The charm is completely non-functional on Juju 4.x. CI disables Juju 4 integration tests (`integration_test.yaml`, `if: false`) citing mysql-k8s incompatibility, but mediawiki-k8s itself is independently broken on Juju 4.
- **Fix**: (a) avoid `set_content()` in the leader-elected path by pre-creating all secret fields at secret-creation time in `_setup_replica_data` rather than migrating lazily; or (b) request a Kubernetes Role with `secrets` permissions via `kubernetes.resources` in `charmcraft.yaml`; or (c) file a Juju bug about the missing secrets permissions on the `juju-secret-consumer` role.
- **Linter rule**: not mechanically checkable; requires Juju 4 integration testing.

### Juju 4 — non-leader deadlock when the leader is stuck on secret migration

- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:305` (`_replica_secrets`)
- **Evidence**: When the leader's `_pre_reconciliation()` → `_replica_secrets()` raises `MediaWikiWaitingStatusException("Waiting for leader to migrate replica secrets")` (blocked on the RBAC error above), non-leaders independently call `_replica_secrets()`, find missing keys, and raise the same exception — waiting for a leader migration that will never happen because the leader is itself blocked. Confirmed on `rv-mediawiki-k8s`: all units stuck, none reaches `ActiveStatus`.
- **Impact**: Every hook that reaches `_pre_reconciliation` fails on every unit — `leader-elected`, `config-changed`, `pebble-ready`, and all relation events. No unit can complete a hook.
- **Fix**: Same root fix as above (pre-create secret fields at creation time); this removes the migration step non-leaders are waiting on.
- **Linter rule**: not mechanically checkable; requires Juju 4 integration testing.

### Manually-stopped Pebble service is not self-healed

- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:451` (`_reconcile_services`), `src/charm.py:797` (`force-reconciliation` action)
- **Evidence**: `kubectl exec mediawiki-k8s-0 -c mediawiki -- pebble stop mediawiki` stops the service. The Juju unit stays `active` and the service stays `inactive` indefinitely — no hook fires as a result of a bare `pebble stop`, so `_reconciliation` never runs and `_reconcile_services()` never restarts it. Recovery required an explicit `force-reconciliation` action.
- **Impact**: If a service is stopped externally (operator error, node-level automation), the charm neither detects nor heals it, and `juju status` continues reporting `active`, giving a false impression of health.
- **Fix**: Add a periodic reconciliation trigger (e.g. driven off Pebble check status) or a custom Pebble check that fires an internal event when a should-be-running service is found stopped, rather than relying solely on Juju hook delivery.
- **Linter rule**: not mechanically checkable; requires runtime observation.

### No explicit `upgrade-charm` handler

- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py` (event registrations near line 51; `self.on.config_changed` / `self.on.secret_changed` observed, `self.on.upgrade_charm` is not)
- **Evidence**: `grep` confirms no `on.upgrade_charm` registration. The charm relies on Juju firing `upgrade-charm` then `config-changed` on `juju refresh`, with `config-changed` triggering `_reconciliation`. This works on Juju 3. On Juju 4, `_replica_secrets()` in that reconciliation path fails with the RBAC error above, so the implicit upgrade path silently fails with no distinguishing signal that it was specifically the upgrade that broke.
- **Impact**: Fragile, implicit upgrade path with no dedicated failure surface; on Juju 4 an operator running `juju refresh` sees the unit stuck in `maintenance` with no indication the problem is upgrade-specific.
- **Fix**: Add an explicit `upgrade-charm` handler that calls `_reconciliation`, giving the upgrade path a visible, testable entry point.
- **Linter rule**: mechanically checkable — `grep -q "on.upgrade_charm" src/charm.py`.

### `_check_and_clear_force_reconciliation_flag` race on new unit join

- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:561` (`_check_and_clear_force_reconciliation_flag`), lines ~582, 589, 596
- **Evidence**: When the app-level force-reconciliation flag is set and all existing units have acked, the leader clears the app flag. If a new unit joins in the narrow window between the last ack and the flag clear, it reads the app flag as still `true`, sets its own unit flag to `true` — but the leader's "all acked" check has already passed, so the leader clears the app flag anyway. The new unit's unit-level flag is now stuck `true` against a cleared app flag. On the next reconciliation, the `if not app_flag:` branch (line 582) is meant to clear stale unit flags, but per the draft's trace this unit's flag is never read by the leader again and persists in peer relation data.
- **Impact**: A stale unit-level flag accumulates in relation data. No immediately observable functional damage, but it represents un-cleaned state that could confuse a future force-reconciliation.
- **Fix**: In the `if not app_flag:` branch, explicitly clear any unit flag set in the current hook context, or replace the boolean flag with a versioned/counter mechanism.
- **Linter rule**: not mechanically checkable; requires a multi-unit test with a unit joining mid-force-reconciliation.

### `rotate-mediawiki-secrets` fails with a generic, unhelpful error on Juju 4

- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:720-723`
- **Evidence**: `model.get_secret(label=...).set_content()` (line 720) fails on Juju 4 with the same `patch secrets` RBAC `ModelError` as `_replica_secrets()` — not a `SecretNotFoundError`. The `except SecretNotFoundError:` branch (line 722, message "Failed to rotate secrets: replica secret not found") is not matched; the generic `except Exception as e:` branch (line 723) catches it and reports "Failed to rotate secrets due to unexpected error" without surfacing the underlying cause.
- **Impact**: On Juju 4, the operator gets a generic failure with no actionable detail and cannot distinguish the RBAC problem from any other failure.
- **Fix**: Add `except ModelError as e:` before the catch-all `except Exception`, and surface the specific error to the action result.
- **Linter rule**: not mechanically checkable; requires Juju 4 integration testing with the action.

### Juju unit stays `active` while the readiness check is failing

- **Severity**: medium
- **Kind**: ux
- **Where**: `src/charm.py:68` (`_MEDIAWIKI_API_READY_CHECK`)
- **Evidence**: After `kubectl delete pod mysql-k8s-0`, MySQL was unavailable for several minutes. The MediaWiki API returned HTTP 500; the Pebble `mediawiki-api-ready` check accumulated 26+ failures against a threshold of 3 (`Check "mediawiki-api-ready" failure 26/3: non-2xx status code 500`); the mediawiki container's Kubernetes readiness probe failed. The Juju unit status remained `active` throughout, and only self-healed to a fully working state once the database returned.
- **Impact**: An operator watching `juju status` sees `active` and believes the unit is healthy while it cannot actually serve requests; the discrepancy is only visible in Pebble/container logs.
- **Fix**: After `_reconcile_services()`, read the Pebble check status (`container.get_check(name).status`) and set `WaitingStatus`/`MaintenanceStatus` when the check is failing, so Juju status reflects actual readiness.
- **Linter rule**: not mechanically checkable; requires monitoring the gap between Pebble check failure and Juju unit status.

### No unit test for the `clamd` `after` field

- **Severity**: medium
- **Kind**: test-gap
- **Where**: `tests/unit/test_charm.py` (`TestPebbleLayerAndServiceReconciliation`)
- **Evidence**: The class exercises `_reconcile_services` and asserts `startup` values and `service_statuses`, but never asserts the `after` field for `clamd`. `grep -n "clamd\|_FRESHCLAM\|_CLAMD\|after.*freshclam" tests/unit/test_charm.py` returns nothing relevant. This is how the string-vs-list bug above shipped unnoticed.
- **Impact**: The bug regresses silently if reintroduced; no test would catch it.
- **Fix**: Add `assert plan.services[Charm._CLAMD_SERVICE_NAME].after == [Charm._FRESHCLAM_SERVICE_NAME]`.
- **Linter rule**: not mechanically checkable directly, but the test itself should exist.

### Ruff errors in bundled charm libraries

- **Severity**: medium
- **Kind**: lint
- **Where**: `lib/charms/*/v*/*.py`
- **Evidence**: `ruff check lib/charms/` reports 211 errors: `data_platform_libs` 93, `grafana_k8s` 46, `loki_k8s` 24, `smtp_integrator` 23, `prometheus_k8s` 16, `redis_k8s` 6, `traefik_k8s` 2, `hydra` 1 (`saml_integrator` 0). `lib/charms/loki_k8s/v1/loki_push_api.py:2272` uses the deprecated `JujuVersion.from_environ()`, generating 62 deprecation warnings during unit test runs. `src/` itself is clean (`ruff check src/` → 0 issues).
- **Impact**: Accumulated maintenance debt in vendored code; contributes noisy warnings to every test run until the libs are refreshed.
- **Fix**: Refresh vendored libs with `charmcraft fetch-lib`, or drop vendored copies in favour of pack-time fetching.
- **Linter rule**: `ruff check lib/charms/` — mechanically checkable.

### Juju 4 deployment also blocked by mysql-k8s incompatibility

- **Severity**: medium
- **Kind**: ux
- **Where**: `charmcraft.yaml` (`assumes: juju >= 3.4`); CI workflow `integration_test.yaml` (`if: false`)
- **Evidence**: `juju deploy mysql-k8s --channel 8.0/edge` on `concierge-k8s-4` fails with "charm requires Juju version < 4.0.0". mediawiki-k8s itself declares `juju >= 3.4` and, apart from the secrets issue above, would be compatible with Juju 4, but the mandatory database relation makes the combination non-deployable today. CI confirms Juju 4 integration tests are disabled.
- **Impact**: Users on Juju 4 infrastructure cannot deploy a functional MediaWiki stack even once the mediawiki-k8s secrets bug is fixed, until mysql-k8s also supports Juju 4.
- **Fix**: Track mysql-k8s Juju 4 support alongside the mediawiki-k8s secrets fix; document the constraint prominently until then.
- **Linter rule**: not mechanically checkable; requires cross-charm integration testing.

### No-op config changes trigger full reconciliation

- **Severity**: medium
- **Kind**: performance
- **Where**: `src/charm.py:158` (`self.on.config_changed` registered on `_reconciliation`)
- **Evidence**: Setting `url-origin` to its current value still fires `config-changed` and triggers `_reconciliation` → `MediaWiki.reconciliation()` → `_composer_reconciliation()`, which reads/writes files in the container even though `_should_skip_composer` ultimately skips the actual composer work. Observed via `juju debug-log`.
- **Impact**: Unnecessary container I/O on every config-changed hook, including no-op ones; could add up on scaled-out deployments with frequent config churn.
- **Fix**: Short-circuit `_reconciliation` when no watched config value actually changed, or use targeted event handlers instead of a catch-all `config_changed` registration.
- **Linter rule**: not mechanically checkable.

### No unit test for `_check_and_clear_force_reconciliation_flag`

- **Severity**: low
- **Kind**: test-gap
- **Where**: `tests/unit/test_charm.py`
- **Evidence**: The `force_reconciliation` action's leader/unit flag coordination is only covered by the slower `test_force_reconciliation_action` integration test; grep confirms no unit test for the flag-clearing logic itself, including the race condition above.
- **Impact**: Non-trivial peer-relation coordination logic (with a known race) is only exercised end-to-end, not at unit-test speed/isolation.
- **Fix**: Add Scenario/`ops.testing` unit tests for the flag flow, including a unit joining mid-force-reconciliation.
- **Linter rule**: not mechanically checkable.

### `charmcraft analyze` reports an entrypoint error on a valid charm

- **Severity**: low
- **Kind**: lint
- **Where**: `charmcraft.yaml` dispatch (`${python_path}` / `${dispatch_path}` shell variables)
- **Evidence**: `charmcraft analyze mediawiki-k8s_amd64.charm` reports `[ERROR] Cannot find the entrypoint file: '/tmp/.../${dispatch_path}/src/charm.py'` even though the dispatch script correctly runs `exec "${python_path}" "${dispatch_path}/src/charm.py"` and the file exists — the analyzer appears not to expand the shell variable before checking.
- **Impact**: A charmcraft tooling false positive that could confuse CI pipelines relying on a clean `charmcraft analyze` exit code.
- **Fix**: Not a charm code fix — report upstream to the charmcraft team.
- **Linter rule**: not mechanically checkable in the charm source.

### Stale `#TODO` comment in `charmcraft.yaml`

- **Severity**: nit
- **Kind**: docs
- **Where**: `charmcraft.yaml` (`traefik-route` provides block)
- **Evidence**: `#TODO: Switch to ingress once gateway-api-integrator supports an upstream ingress, or once we can connect to HAProxy more directly.` — predates the current `traefik-route` implementation (unverified: reviewer estimates it as roughly three years old).
- **Impact**: Stale, unactionable TODO.
- **Fix**: File a GitHub issue and either remove the comment or replace it with a link to the issue.
- **Linter rule**: mechanically checkable — `grep -n "TODO" charmcraft.yaml` flags TODOs lacking an issue reference.

### `relation-broken` correctly re-fires reconciliation even from a blocked state

- **Severity**: informational
- **Kind**: confirm
- **Where**: `src/charm.py:109`, `src/charm.py:601`
- **Evidence**: `database` relation's `relation_broken` is registered to fire `_reconciliation`. Removing the relation (`juju remove-relation mediawiki-k8s mysql-k8s`) produced `BlockedStatus("Waiting for relation database")` within ~5s; restoring it returned to `active` within ~15s.
- **Linter rule**: not mechanically checkable.

### SQL injection is not a risk in the database module

- **Severity**: informational
- **Kind**: confirm
- **Where**: `src/mediawiki/_database.py`
- **Evidence**: All `cursor.execute()` calls use table names drawn only from hardcoded constants (`constants.PRIMARY_KEY_LESS_TABLES`, `constants.MYISAM_TABLES`), backtick-escaped via `table.replace("`", "``")` for constant names only; all dynamic values (hostnames, ports, credentials) use `%s` parameterised queries. The `# noqa: S608 # nosec: B608` suppression on the `SELECT 1 FROM \`{table}\`` line is justified since `table` is always a constant.
- **Linter rule**: `bandit` covers this pattern; confirmed 0 issues.

### S3 and ClamAV integration tests are thorough end-to-end coverage

- **Severity**: informational
- **Kind**: confirm
- **Where**: `tests/integration/test_s3.py`
- **Evidence**: Tests deploy Minio (`ckf-1.10/stable`), configure an anonymous-read S3 bucket via policy, integrate via s3-integrator, upload a test PNG via the MediaWiki API and verify success. A separate ClamAV test uploads the EICAR test string and verifies a `verification-error` with `"Eicar-Test-Signature FOUND"` — proving ClamAV is actively scanning uploads. These exercise real end-to-end paths that code review alone cannot confirm.
- **Linter rule**: not mechanically checkable.

## Worth copying

- **Reconciler pattern without `defer()`/`StoredState`**: a clean single-pass reconciliation registered on all relevant events; no deferred events, every hook evaluates current state and drives toward desired state. (`src/charm.py:_reconciliation`)
- **Status exception hierarchy**: `MediaWikiStatusException` → `MediaWikiBlockedStatusException`/`MediaWikiWaitingStatusException`, each carrying its own `Status` subclass, caught centrally in `_reconciliation`. (`src/exceptions.py`)
- **Mixin-based container logic separation**: `MediaWiki` composed of `_ComposerMixin` + `_DatabaseMixin` + `_SettingsMixin` + `_MediaWikiBase`. (`src/mediawiki/`)
- **Composer peer synchronization with leader coordination**: leader runs `composer update`, publishes `composer.lock` to peer app data; non-leaders run `composer install` against the same lock. The `force_reconciliation` action's app-flag + per-unit-ack mechanism is a well-designed (if slightly racy) distributed coordination pattern. (`src/charm.py:_check_and_clear_force_reconciliation_flag`, `src/mediawiki/_composer.py:_composer_reconciliation`)
- **Group Replication compatibility fixes**: adds surrogate `BINARY(16)` keys to historically PK-less core tables (MySQL error 3098) and converts MyISAM tables to InnoDB, idempotently and well-commented. (`src/mediawiki/_database.py`)
- **Database initialization flag table**: `mediawiki_charm_setup` marker table lets non-leader units poll for leader-completed install, with no secrets required. (`src/mediawiki/_database.py:_is_database_initialized`)
- **SSH config reconciliation**: handles full key/config lifecycle including proxy-aware `ProxyCommand` for git-over-SSH through HTTP proxies. (`src/utils.py:ssh_reconcile_config`)
- **ProxyConfig from environment**: reads `JUJU_CHARM_HTTP_PROXY`/`HTTPS_PROXY`/`NO_PROXY` into a typed Pydantic model used consistently. (`src/state.py:ProxyConfig`)
- **Test fixture architecture**: `base_state` → `active_state` → `configured_state` fixture graph with autouse mocks (MediaWiki, GitSync, SiteInfo, MySQL) keeps individual tests focused. (`tests/unit/conftest.py`)
- **MySQL retry decorator with bounded timeout**: `_db_retry_deco` retries with a 180-second deadline (3×60s), bounding worst-case DDL latency under transient MySQL failures. (`src/mediawiki/_database.py:_db_retry_deco`)
- **ContainerService command wrapper**: wraps Pebble `exec` with timeout handling, `combine_stderr`, sensitive-command redaction, and `ExecError` → `CommandExecResult` conversion. (`src/container.py`)
- **Deferred-error settings write**: `_push_late_settings()` collects S3/SMTP/auth errors during settings generation but only raises after all settings are written, keeping the config file consistent. (`src/mediawiki/_settings.py:81`)

## Common-practice notes

**Follows convention**: `lib/charms/<name>/v<N>/` versioned charmlibs; `src/` layout; `ops.CharmBase` + `framework.observe`; `testing.Context` (Scenario) for unit tests; `charmcraft.yaml` with `type: charm`, `base: ubuntu@24.04`, `platforms: amd64`; `pyproject.toml` with uv build system and ruff/mypy/bandit config; CHANGELOG.md + Sphinx docs; `CONTRIBUTING.md` with CLA; actions defined inline in `charmcraft.yaml` rather than a separate `actions.yaml`; `charmlibs-pathops` pulled from PyPI as a declared dependency rather than vendored.

**Drifts from convention**:
- All 10 charm libs vendored under `lib/charms/` rather than fetched at build time — conventional for pinned/stable libs, but 211 ruff errors accumulate in the vendored copies (Finding above).
- No explicit `upgrade-charm` handler — the upgrade path relies on `config-changed` firing after `juju refresh`, which works on Juju 3 but is implicit and fragile, and fails outright on Juju 4 (Finding above).

**Notable**: `assumes: juju >= 3.4` is well-calibrated for the Juju 3.4+ features the charm actually uses (secrets, secret grants). It is not, however, evidence that the charm works on Juju 4 — it currently does not, due to the secrets RBAC issue.

## Tests

**Unit tests**: 289 pass (`PYTHONPATH=. uv run pytest tests/unit -v`, 11.54s). Covers charm events, Pebble service reconciliation, composer peer sync, database schema reconciliation, git-sync, Redis, S3, SMTP, OAuth, SAML, config validation, SSH reconciliation, URL-origin validation, state management. No `defer()`/`StoredState` to test.

**Test gaps**:
1. No assertion that `clamd.after == [self._FRESHCLAM_SERVICE_NAME]`.
2. No unit test for `_check_and_clear_force_reconciliation_flag` flag coordination (only integration coverage via `test_force_reconciliation_action`).
3. No unit test for the race condition where a unit joins mid-force-reconciliation.
4. No direct unit test of the `_pebble_layer` method (only indirect coverage via service-status checks).
5. No unit test for an externally-stopped Pebble service and whether the charm self-heals (it does not — see Findings).
6. No unit test for `_replica_secrets` failure behaviour on Juju 4 (`secret.set_content()` failing) — only observable in a real Juju 4 deployment.

**Integration tests**: jubilant + pytest, per-charm fixtures (mysql, traefik, redis, ssc). Cover relation add/remove, SSH key secret handling, extension installation, all actions (`rotate-secrets`, `create-and-promote`, `force-reconciliation`, `update-database`), MediaWiki API reachability, and the `all-units` flag for `force-reconciliation` (not covered by unit tests). `disable_ssl_verification` autouse fixture is appropriate for self-signed test environments.

**CI**: runs on Juju 3/stable with mysql-k8s 1.35-strict/stable. Juju 4 tests are disabled (`if: false`) citing mysql-k8s incompatibility — but mediawiki-k8s itself is also independently broken on Juju 4 (see Findings).

**Linters**: `ruff check src/` → 0 issues; `ruff check lib/charms/` → 211 issues (all vendored libs); `codespell` → 0; `mypy` (21 source files) → 0; `bandit` → 0; `charmcraft analyze` → false-positive entrypoint error (charmcraft bug, not charm bug).

## Docs

- **README.md**: accurate, with licensing table, badges, a basic deployment snippet correctly showing `juju deploy mysql-k8s --trust` and `juju integrate mediawiki-k8s mysql-k8s:database`.
- **Tutorial** (`docs/tutorial/basic-deployment.rst`): step-by-step from bootstrap to admin creation; the `create-and-promote` action behaviour matched the tutorial exactly.
- **Upgrade docs** (`docs/how-to/upgrade.rst`): correctly warns about database backup and the `update-database` action, and mentions `juju refresh`. It does not mention that there is no explicit `upgrade-charm` handler — an operator expecting a dedicated upgrade hook path may be surprised.
- **COS integration** (`docs/how-to/integrate-with-cos.rst`): detailed COS/COS Lite guide; documented metrics (`apache_exporter`, `git_sync`) match the deployed Pebble layer; the Grafana dashboard JSON covers all documented metrics.
- **Allowlist** (`docs/reference/allowlist.rst`): lists packagist.org, gerrit.wikimedia.org, github.com, codeload.github.com, clamav.net — no discrepancies observed.
- **Terraform module** (`terraform/`): standard Juju provider module with README, import example, integration snippet; `versions.tf` pins `juju/juju >= 2.0.0`.
- **Security docs** (`docs/explanation/security.rst`): covers static-asset serving, SAML session storage, secrets management, file permissions — consistent with what was observed.
- **Relation endpoints** (`docs/reference/relation-endpoints.rst`): detailed (~10KB) and consistent with `charmcraft.yaml`.

## Open questions

1. Is there a Juju-level API for updating secret content that doesn't require Kubernetes `patch secrets` permission? If not, the `juju-secret-consumer` Role gap needs a Juju-side fix as well as a charm-side workaround.
2. What is the intended relationship between the `mediawiki-api-ready` Pebble check (`level: ready`) and Juju workload status? Today, repeated check failures are logged by Pebble but never reflected in `juju status`.
3. Can a leader-election event mid-reconciliation race with `_reconciliation` on the new leader (e.g. both old and new leader attempting `composer update`)? `_replica_consensus_reached()` guards part of this, but `_reconciliation` itself has no leadership guard beyond that (unverified — not directly exercised in testing).
4. Should `mediawiki-api-ready`'s `formatversion=2` query-string dependency be a concern for future MediaWiki version upgrades? Not a practical issue today since only 1.46 is shipped.
5. Does the hardcoded `${lokids}` Grafana template variable match what COS Lite provides by default for the Loki datasource UID, or does it require manual operator configuration?
