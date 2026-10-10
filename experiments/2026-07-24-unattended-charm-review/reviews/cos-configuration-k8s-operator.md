# cos-configuration-k8s

A well-structured k8s sidecar charm that syncs observability configuration from a git repository and forwards it to the COS stack via relations. The code is idiomatic ops, with a thoughtful hash-based change-detection scheme that avoids redundant reinitialisation, and sensible defaults (e.g. `known_hosts_config` pre-populated with github.com/git.launchpad.net keys). It recovered cleanly from every failure injection tried — pod deletion, missing config, unreachable repos, bad SSH keys, invalid secrets, scale up/down, relation add/remove, cross-revision refresh — reaching sensible active/blocked states each time, though blocked statuses routinely swallow the git-sync stderr that would tell an operator what actually went wrong. The charm is not broken, but it carries a leftover git-sync v3→v4 migration bug (workload version never populates), a double-exec bug in the `sync-now` action, and an entirely-skipped upgrade test suite. A maintainer should first fix the workload-version regex and the `sync-now` double-call, then surface git-sync stderr in `BlockedStatus`, then add a same-base upgrade test to replace the skipped cross-base one.

| | |
|---|---|
| Repo | canonical/cos-configuration-k8s-operator @ `04600d3` (2026-07-13) |
| Charms | cos-configuration-k8s |
| Substrate | k8s |
| Deployed | yes — concierge-k8s-3 (Juju 3.6.25), charmhub `3.0/edge` rev 116; full COS integration (prometheus-k8s, loki-k8s, grafana-k8s); cross-revision refresh to `dev/edge` rev 112; scale 1→2→1 |
| Reviewed | 2026-07-29 |

## What it does

The charm runs a git-sync v4.7.0 sidecar container that syncs a git repository to shared storage (`content-from-git`). From the charm container it reads Prometheus alert/recording rules, Loki alert rules, Grafana dashboards, and Sloth SLO specs from the synced files and forwards them over Juju relations to `prometheus-k8s`, `loki-k8s`, `grafana-k8s`, and `sloth-k8s`. It also supports `send-remote-write` for Prometheus remote write. SSH auth for private repos is supported via both cleartext `git_ssh_key` config (deprecation-warned) and Juju secrets (`git_ssh_key_secret`). A `sync-now` action provides on-demand sync alongside the periodic `update-status`-driven sync. The charm deliberately does not inject Juju topology into dashboards or alert rules (documented design choice in the README).

## Deployment log

### Juju 3.6 k8s deployment and basic config
1. `juju add-model rv-cos-cfg2 --controller concierge-k8s-3` — model on Juju 3.6.25 k8s.
2. `juju deploy cos-configuration-k8s --channel 3.0/edge --trust` — deployed revision 116.
3. Without config: `blocked: Config options missing - use juju config` — correct.
4. `juju config cos-configuration-k8s git_repo="https://github.com/canonical/cos-configuration-k8s-operator.git" git_branch="main"` — git-sync ran, went active. Deploy-to-active: ~60s.

### Relation testing
5. `juju deploy prometheus-k8s --channel edge --trust` — rev 311, 3.11.3.
6. `juju relate cos-configuration-k8s:prometheus-config prometheus-k8s:metrics-endpoint` — active/idle both sides. App data `alert_rules: '{}'` (no rules dir in synced repo) — correct.
7. `juju relate cos-configuration-k8s:send-remote-write prometheus-k8s:receive-remote-write` — cos-config app data `{}`; prometheus sends `remote_write: '{"url": "http://prometheus-k8s-0...9090/api/v1/write"}'`. Both active.
8. `juju remove-relation` on both prometheus relations — removed cleanly, cos-config stayed active/idle.

### Full COS integration (second deployment, `rv-cos-deep`)
9. Deployed cos-configuration-k8s (3.0/edge rev 116) + prometheus-k8s (3.11/edge rev 311) + loki-k8s (1/edge rev 207) + grafana-k8s (2/edge rev 180).
10. Related all 4 endpoints (`prometheus-config`, `send-remote-write`, `loki-config`, `grafana-dashboards`) simultaneously — all apps reached active/idle.
11. Relation data confirmed: `prometheus-config` → `alert_rules: '{}'`; `send-remote-write` → `{}` + prometheus's `remote_write` URL; `loki-config` → `alert_rules: '{}'` + `metadata` (model info); `grafana-dashboards` → `{}` both sides. Empty because the default repo has no rule/dashboard subdirectories — correct.
12. Removed `prometheus-config` — stayed active. Removed `send-remote-write` — stayed active. Both relations re-added without issue, no dangling relation data.
13. Scale 1→2: both units active, hash shared via peer app data. Scale 2→1: clean teardown.

### Actions and config changes
14. `juju run cos-configuration-k8s/0 sync-now` — action succeeded but called git-sync twice (4 Pebble WebSocket tracebacks = 2 exec calls × 2 websocket finalisers). git-sync v4 deprecation warnings for `--branch`, `--rev`, `--dest` appeared.
15. Config change tests:
    - `git_branch="nonexistent-branch"` → `blocked: Sync failed: Sync error: Exited with code 1.` — unhelpful, stderr not shown.
    - Restored valid config → recovered to active.
    - `git_repo="https://nonexistent.invalid/repo.git"` → blocked with the same unhelpful message.
    - `git_depth="not-a-number"` → rejected at Juju level (`expected int, got "not-a-number"`) — correct.
    - `git_ssh_key_secret="secret://nonexistent/key"` → `blocked: missing charm permissions for the secret, see debug-log.` — clear.
    - `git_ssh_key_secret="not-a-valid-url"` → `blocked: git SSH key secret not found.` — clear.
    - `git_branch` set to a 10,000-character string → blocked "Exited with code 1"; restored to `main` → recovered.
    - `git_branch="branch/with/slashes"` → blocked with the same message (branch doesn't exist); restored → recovered.
16. **Action stderr swallowed**: with the charm blocked on a bad repo, running `sync-now` shows the real error in the action's git-sync JSON stdout — `stderr: "fatal: unable to access 'https://nonexistent.invalid/repo.git/': Could not resolve host: nonexistent.invalid"` — but the action's final failure message is only `Sync error: Exited with code 1.`. Stderr reaches action output via `event.log` but not the failure message.

### SSH and secret testing (deepened)
17. Created Juju secret `test-ssh-secret` (key `ssh-key`, fake data), granted to the charm, set `git_ssh_key_secret="secret://<id>/ssh-key"` with an HTTPS repo URL:
    - Charm stayed `active` — correct, git-sync ignores SSH for HTTPS. `--ssh` flag still appended (deprecation noise). Secret value written to disk (`/run/cos-config-ssh-key.priv`).
    - Unsetting the secret recovered cleanly.
18. `git_repo="git@github.com:canonical/cos-configuration-k8s-operator.git"` with a fake SSH key: blocked `"Sync failed: Sync error: Exited with code 1."` — the known_hosts check passed (github.com is in the defaults) but SSH auth failed; the actual stderr (`Permission denied (publickey)`, per notes) is not visible in the status.
19. `juju resolved` on an active unit → `ERROR unit is not in an error state` — expected Juju behaviour.

### Scaling
20. `juju scale-application cos-configuration-k8s 2` — second unit active. Peer relation app data correctly shared `hash` and `reinit_without_topology_dropdowns`.
21. Scale back to 1 — clean.

### Pod recovery
22. `kubectl delete pod cos-configuration-k8s-0 --grace-period=0` while active with relations connected — pod recreated, charm recovered to `active` within ~15s. Storage persisted across restart.

### Cross-revision refresh
23. `juju refresh cos-configuration-k8s --channel dev/edge` (rev 116 → rev 112, same base ubuntu@26.04) — succeeded. Both units restarted, returned to `active`. `_on_upgrade_charm` fired, called `_common_exit_hook`, no issues observed. Relations survived.

### Juju 4.x deployment attempt
24. `juju add-model rv-test-4x --controller concierge-k8s-4` on Juju 4.0.5.
25. `juju deploy cos-configuration-k8s --channel 3.0/edge` → `ERROR the charm defined bases "ubuntu@26.04" not supported`. Controller infrastructure limitation, not a charm bug — `assumes: juju >= 3.6` is satisfied, the base is the constraint.

## Observed behaviour

- **Resource usage**: ~1m CPU, ~35Mi memory per pod. Lightweight.
- **Containers**: two per pod — `git-sync` (Pebble, no running services) and the charm container. `kubectl exec ... -c git-sync -- ps aux` shows only pebble; git-sync runs on-demand via `container.exec()`.
- **Unused Pebble service**: the rock image ships a `git-sync` Pebble service with `startup: enabled` and a hardcoded command, but the charm never starts or modifies it — it runs git-sync via `container.exec(["/bin/git-sync", ...])` instead. Pebble runs with `--hold`, so the service never starts.
- **git-sync/git versions**: git-sync v4.7.0, git v2.53.0.
- **Workload version not set**: `juju status` shows no version — regex `r"v(\d*\.\d*\.\d*)"` expects a `v` prefix but git-sync v4 outputs `4.7.0` (no `v`). Silently lost, only a `logger.debug`.
- **Pebble websocket errors**: every `container.exec()` produces `WebSocketConnectionClosedException` tracebacks at WARNING level (Python 3.14 / ops incompatibility), 4 per exec call — noisy, no functional impact, but also shows up in action output.
- **Deprecation warnings**: every git-sync run emits JSON deprecation warnings for `--branch`, `--rev`, `--dest` (v3 flags); git-sync v4 auto-translates them to `--ref`/`--link`.
- **Hash-based change detection works**: worktree hash read from `.git`, stored in peer app data (e.g. `hash: 04600d3804b201c2d1a9cde3609bb037c03294db`); `_reinitialize_*` only fires on hash change. Both units in a scaled deployment share the hash.
- **Git-sync runs on every config change**: any `juju config`, even a non-repo option like `prometheus_alert_rules_path`, triggers a full `git-sync --one-time` network fetch even though the hash check prevents re-pushing unchanged relation data.
- **No-op config changes don't fire config-changed**: setting `git_branch="main"` when already `"main"` did not trigger config-changed — Juju 3.6 correctly skips no-op changes.
- **`known_hosts_config` default is sensible**: ships with SSH host keys for github.com (rsa/ecdsa/ed25519) and git.launchpad.net (rsa), so "Unknown host" only triggers for custom hosts. Confirmed with a fake SSH key against a github.com repo URL — known_hosts passes, sync then fails on the fake key with the unhelpful "Exited with code 1".
- **`--ssh` flag deprecated but always sent**: `Flag --ssh has been deprecated, no longer necessary` observed. Charm unconditionally passes `--ssh` whenever `git_ssh_key`/`git_ssh_key_secret` is set, even for HTTPS URLs.
- **Grafana dashboard warnings during startup**: "Invalid Grafana dashboards folder" logged 6 times on initial startup (once per hook: install, replicas-relation-created, leader-elected, git-sync-pebble-ready, content-from-git-storage-attached, config-changed) — each hook builds a new `GrafanaDashboardProvider`. Noisy but transient.
- **sync-now error flow**: on SyncError the action logs stderr via `event.log`, then calls `event.fail(e.message)` (no stderr in the failure text), then `_common_exit_hook()` runs `_exec_sync_repo()` a second time, producing a second SyncError that sets BlockedStatus.
- **Relation data flows**: all 4 relation types exercised (see log above); relations are optional — removing any one leaves the charm active with no status change.
- **Full COS stack integration**: cos-configuration-k8s + prometheus-k8s (3.11/edge) + loki-k8s (1/edge) + grafana-k8s (2/edge), all 4 relations live simultaneously, all apps active/idle. Cross-base relations (grafana on 24.04, loki on 20.04, cos-config on 26.04) worked fine.
- **Relation removal**: no dangling relation data observed after removing/re-adding prometheus relations.
- **SSH key with HTTPS repo**: `git_ssh_key="fake-key"` with an HTTPS repo works — `_trust_ssh_remote` passes (no SSH remote to verify), key is saved but ignored by git-sync; status shows `WARN: cleartext ssh key, see debug-log`.
- **SSH key with SSH repo + fake key**: blocked "Exited with code 1"; known_hosts passes (github.com default) but the real SSH failure stderr isn't visible — an operator would need `sync-now` output to see it.
- **Junk secret handling**: a valid-looking but incorrect SSH key via Juju secret is handled gracefully (key written to disk, git-sync fails at auth). `secrets_helper.py`'s secret getter validates URL format, secret existence, and permissions correctly; all 6 invalid-secret-URL formats in unit tests produce proper BlockedStatus messages.
- **Pod recovery preserves hash state**: after pod deletion, recovered to active in ~15s; hash file survived on persisted storage; debug-log showed no "Updating stored hash" during recovery, confirming no unnecessary reinitialisation.

## Findings

### `_push_ssh_config` log messages are plain strings, not f-strings — variables never interpolated
- **Severity**: high
- **Kind**: bug (logging)
- **Where**: `src/charm.py:536, 543`
- **Evidence**: `logger.info("Invalid proxy hostname in model config: {proxy_host}")` and the port equivalent use `{proxy_host}`/`{proxy_port}` as literal text, not an f-string. An operator sees the literal string `{proxy_host}` instead of the actual bad value.
- **Impact**: SSH proxy misconfiguration produces an unhelpful log line; the charm still correctly goes to `BlockedStatus("Invalid proxy configuration — see debug-log")`, but the operator can't tell from the log which value was wrong.
- **Fix**: Use f-strings: `logger.info(f"Invalid proxy hostname in model config: {proxy_host}")` (and likewise for port).
- **Linter rule**: mechanically checkable — flag `logger.*("...{name}...")` calls where the string literal is not prefixed `f`.

### Workload version never set — regex mismatch with git-sync v4 output
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:592-596`
- **Evidence**: `re.search(r"v(\d*\.\d*\.\d*)", version_output)` expects a `v` prefix, but git-sync v4.7.0 outputs `4.7.0` with no `v`. The comment above the regex still says `# Output looks like this: # v3.5.0`. The handler returns `None`, logged only at `logger.debug`.
- **Impact**: `juju status` shows no workload version; operators get no signal that this silently broke.
- **Fix**: `r"v?(\d+\.\d+\.\d+)"` (optional `v`, one-or-more digits). Add a `logger.warning` when the regex fails to match.
- **Linter rule**: not mechanically checkable.

### `sync-now` action calls git-sync twice
- **Severity**: medium
- **Kind**: bug / performance
- **Where**: `src/charm.py:284, 293` (action handler calling `_exec_sync_repo()` directly, then `_common_exit_hook()` calling it again at line 258)
- **Evidence**: 4 Pebble tracebacks observed per action run (2 exec calls × 2 websocket finalisers). If the first sync fails, the second can fail too, and its stderr is silently converted to BlockedStatus with only the first error surfaced in the action output.
- **Impact**: Double network fetch on every `sync-now`; on failure, the operator gets only half the picture.
- **Fix**: Drop the manual `_exec_sync_repo()` call in the action handler and let `_common_exit_hook()` do the sync once; move stderr surfacing into the shared path.
- **Linter rule**: mechanically checkable via AST — "action handler calls `_exec_sync_repo` and then calls `_common_exit_hook`".

### git-sync stderr not surfaced in BlockedStatus on sync failure
- **Severity**: medium
- **Kind**: ux
- **Where**: `src/charm.py:263-264` (status built from `e.message` only; stderr captured in `e.details` at line ~334)
- **Evidence**: Observed status `"Sync failed: Sync error: Exited with code 1."` when the real cause (visible via the `sync-now` action's `event.log` output) was `"fatal: unable to access 'https://nonexistent.invalid/repo.git/': Could not resolve host: nonexistent.invalid"`. Same pattern for bad branches and failed SSH auth.
- **Impact**: Operators see a blocking status with no way to tell whether it's DNS, auth, or a bad URL without running `sync-now` and reading raw output.
- **Fix**: Include the first meaningful stderr line in the status message, e.g. `BlockedStatus(f"Sync failed: {e.message} — {first_stderr_line}")`.
- **Linter rule**: partially checkable — flag `BlockedStatus` built from a `SyncError` without referencing its `details` attribute.

### No upgrade test coverage — `test_upgrade_charm.py` entirely skipped
- **Severity**: medium
- **Kind**: test-gap
- **Where**: `tests/integration/test_upgrade_charm.py:18`
- **Evidence**: `pytestmark = pytest.mark.skip(reason="Cross-base upgrade from 24.04 to 26.04 not supported")` skips the whole file. `_on_upgrade_charm` (`src/charm.py:397`) has 0% coverage in both unit and integration tests.
- **Impact**: `juju refresh` is a routine operator task; it works in practice (confirmed: 3.0/edge rev 116 → dev/edge rev 112, same base), but nothing automated would catch a regression if migration logic is ever added to the handler.
- **Fix**: Add a same-base upgrade test (deploy from `3.0/edge`, then `juju refresh` to locally-built HEAD) plus a scenario unit test for `_on_upgrade_charm`.
- **Linter rule**: not mechanically checkable.

### `slos_path` config change without a hash change never triggers SLO reinitialisation
- **Severity**: low
- **Kind**: bug
- **Where**: `src/charm.py:444-475` (`_update_hash_and_rel_data`)
- **Evidence**: `SlothSloProvider` has no `config_changed` handler of its own; the charm calls `_reinitialize_slo_specs()` only when `current_hash != stored_hash`. Prometheus/Loki/Grafana providers register their own library-level `config_changed` handlers (`prometheus_scrape.py:1865`, `loki_push_api.py:1500`, `grafana_dashboard.py:1189`) and pick up new paths independently at construction time (charm `__init__` runs on every hook dispatch); Sloth has no equivalent.
- **Impact**: Changing `slos_path` alone (no git content change) leaves stale SLO relation data until the next real git-sync change or `sync-now`. Low severity — Sloth is less commonly used and path-only changes are atypical.
- **Fix**: Store the last-used path values in peer data alongside the hash and call `_reinitialize_slo_specs()` when paths change even if the hash hasn't; or give `SlothSloProvider` its own `config_changed` handler like the other providers.
- **Linter rule**: not mechanically checkable.

### Non-leader units repeat unnecessary work every hook for Grafana dashboards
- **Severity**: low
- **Kind**: correctness / performance
- **Where**: `src/charm.py:471-473`
- **Evidence**: The `elif` branch calls `self.grafana_dashboards_provider._reinitialize_dashboard_data(inject_dropdowns=False)` with no `is_leader()` guard. `_stored_set("reinit_without_topology_dropdowns", "Done")` no-ops on non-leaders (line ~435: `if not self.unit.is_leader(): return`), so the stored flag never gets set and non-leaders call `_reinitialize_dashboard_data` on every hook forever. The library itself intentionally reads files on non-leaders by design.
- **Impact**: Wasted filesystem I/O on non-leader units. Negligible in practice (cos-config is usually single-unit, and dashboards are usually absent from the default repo).
- **Fix**: Add `and self.unit.is_leader()` to the `elif` condition.
- **Linter rule**: mechanically checkable — call to `_reinitialize_dashboard_data` without an `is_leader` guard where a sibling branch has one.

### `_stored_set` iterates all peer relations with a stale TODO
- **Severity**: low
- **Kind**: bug (latent) / code quality
- **Where**: `src/charm.py:438-442`
- **Evidence**: `for relation in self.model.relations[self._peer_relation_name]: relation.data[self.app][key] = value` iterates every peer relation, though app data is shared per-application in Juju. A TODO at line 441 (`# TODO: is this needed for every relation? app data should be the same for all`) confirms the authors already suspected this. `_stored_get` at line 425 uses `self.model.get_relation(...)` (single relation) — inconsistent with the setter.
- **Impact**: Unnecessary writes in a scaled deployment with multiple peer relations; harmless in practice given typical cos-config deployments are single-unit.
- **Fix**: Use `self.model.get_relation(self._peer_relation_name)` in `_stored_set` to match `_stored_get`; remove the TODO.
- **Linter rule**: mechanically checkable — `_stored_get` uses `get_relation`, `_stored_set` uses a `self.model.relations[name]` loop.

### `test_prometheus_scrape.py` tests `send-remote-write`, not `prometheus-config`
- **Severity**: low
- **Kind**: test-gap / docs
- **Where**: `tests/integration/test_prometheus_scrape.py:45`
- **Evidence**: The test relates `prom:receive-remote-write` — that's the `send-remote-write` relation (`prometheus_remote_write` interface). The `prometheus-config` relation (`prometheus_scrape` interface, using a separate `PrometheusRulesProvider` instance internally) is never exercised in integration despite the misleading file name.
- **Impact**: The primary rule-forwarding path has no integration coverage; a regression there would go unnoticed.
- **Fix**: Rename to `test_send_remote_write.py`; add a real `prometheus-config` integration test against `metrics-endpoint`.
- **Linter rule**: not mechanically checkable.

### git-sync v3 flag deprecation warnings not addressed
- **Severity**: low
- **Kind**: lint / maintenance
- **Where**: `src/charm.py:369-380`
- **Evidence**: Code uses `--branch`, `--rev`, `--dest` — all deprecated in git-sync v4. Every run logs `Flag --branch has been deprecated, use --ref instead` and similar for `--dest`.
- **Impact**: Log noise now; risk that git-sync drops the auto-translation of old flags in a future release.
- **Fix**: Migrate to `--ref` (covers both branch and rev) and `--link` (replaces `--dest`); may need logic changes since `--ref` combines branch/rev semantics differently.
- **Linter rule**: not mechanically checkable.

### `--ssh` flag deprecated in git-sync v4 but still unconditionally appended
- **Severity**: low
- **Kind**: lint / maintenance
- **Where**: `src/charm.py:383-384`
- **Evidence**: `cmd.extend(["--ssh"])` is added whenever `git_ssh_key`/`git_ssh_key_secret` is set, regardless of the repo URL's protocol. Observed log line: `Flag --ssh has been deprecated, no longer necessary`.
- **Impact**: Adds noise, confusing for HTTPS repos with an SSH key also configured.
- **Fix**: Drop `--ssh` entirely (git-sync v4 auto-detects) or condition it on the repo URL being an SSH URL.
- **Linter rule**: not mechanically checkable.

### Grafana dashboards: 6 warnings logged during startup for a missing directory
- **Severity**: low
- **Kind**: ux / noise
- **Where**: `lib/charms/grafana_k8s/v0/grafana_dashboard.py:1304` (via `src/charm.py:186`)
- **Evidence**: "Invalid Grafana dashboards folder at ... directory does not exist" logged once per startup hook (install, replicas-relation-created, leader-elected, git-sync-pebble-ready, content-from-git-storage-attached, config-changed) — 6 identical warnings within seconds.
- **Impact**: A new operator seeing 6 identical warnings may suspect a real problem when there is none.
- **Fix**: Log at DEBUG/INFO rather than WARNING — the library already handles the missing-directory case gracefully.
- **Linter rule**: not mechanically checkable.

### Prometheus rules pushed twice on config-change when the hash also changes
- **Severity**: low
- **Kind**: performance
- **Where**: `src/charm.py:156, 458`; `lib/charms/prometheus_k8s/v0/prometheus_scrape.py:1865, 1888`
- **Evidence**: On a config-changed where git content actually changed, both the library's own `config_changed` handler (`_update_relation_data`) and the charm's `_update_hash_and_rel_data`→`_reinitialize_alert_rules()` write relation data. When the hash is unchanged the charm's guard prevents the duplicate; when it changes, both fire.
- **Impact**: Two relation-data writes instead of one — minor.
- **Fix**: Rely on either the library's `config_changed` registration or the charm's explicit call, not both.
- **Linter rule**: not mechanically checkable.

### `_git_sync_version` regex uses `\d*` instead of `\d+`
- **Severity**: nit
- **Kind**: bug (minor)
- **Where**: `src/charm.py:593`
- **Evidence**: `re.search(r"v(\d*\.\d*\.\d*)", version_output)` — `\d*` matches zero digits, so a malformed string like `"v.4.7"` would match with empty capture groups.
- **Impact**: Fragile parsing in the unlikely event git-sync emits malformed version output.
- **Fix**: Use `r"v?(\d+\.\d+\.\d+)"`.
- **Linter rule**: mechanically checkable — regex using `\d*` in a version capture group.

### Unused Pebble service defined in rock image
- **Severity**: nit
- **Kind**: code quality / clarification
- **Where**: rock image Pebble layer (`001-rockcraft-git-sync.yaml`); `src/charm.py` (no `add_layer`/`start` calls)
- **Evidence**: The rock ships a `git-sync` Pebble service with `startup: enabled` and a hardcoded command; the charm never calls `container.add_layer()`/`container.start("git-sync")`, running git-sync via `container.exec()` instead. Pebble runs with `--hold`.
- **Impact**: Confusing dead code for anyone reading the Pebble plan; may be intended for a future continuous-sync mode.
- **Fix**: Remove the unused service definition, or comment that it's reserved for future use.
- **Linter rule**: not mechanically checkable.

### Grammar/typo in `BlockedStatus` message
- **Severity**: nit
- **Kind**: ux
- **Where**: `src/charm.py:229-230`
- **Evidence**: `BlockedStatus("Invalid proxy configuration - use see debug-log")` — "use see" should be "see"; inconsistent punctuation vs. the nearby SSH status `BlockedStatus("Unknown host; see debug-log")` (semicolon vs. dash).
- **Impact**: Cosmetic but visible to every operator hitting this path.
- **Fix**: `"Invalid proxy configuration — see debug-log"`; unify punctuation across both messages.
- **Linter rule**: not mechanically checkable.

### `_common_exit_hook` complexity suppressed with `noqa: C901`
- **Severity**: nit
- **Kind**: lint
- **Where**: `src/charm.py:177`
- **Evidence**: `def _common_exit_hook(self) -> None:  # noqa: C901` — the method handles container readiness, peer relation, config completeness, SSH host verification, SSH proxy, secret/SSH key, sync, and hash checks (8 concerns) in one function.
- **Impact**: Hard to test exhaustively; complexity will only grow as more status checks are added.
- **Fix**: Extract SSH checks into `_reconcile_ssh` and config validation into `_reconcile_config`, keeping the progressive-return pattern but with fewer branches per method.
- **Linter rule**: mccabe complexity check (already flagged by ruff as C901).

### `RELEASE.md` references "Alertmanager charm"
- **Severity**: nit
- **Kind**: docs
- **Where**: `RELEASE.md`
- **Evidence**: Copy-paste artifact referencing an Alertmanager release process.
- **Impact**: Misleading for contributors following the release docs.
- **Fix**: Rewrite to describe this charm's release process specifically.
- **Linter rule**: not mechanically checkable.

### Integration tests target outdated charm channels/bases
- **Severity**: low
- **Kind**: test-gap / docs
- **Where**: `tests/integration/test_prometheus_scrape.py:38`, `tests/integration/test_grafana_dashboards.py:51`, `tests/integration/test_loki_push_api.py:36`
- **Evidence**: All integration tests deploy related charms from `2/edge` (24.04/20.04 bases) while cos-config now ships on 26.04; the grafana test is already `@pytest.mark.xfail`. Live deploy in this review used `prometheus-k8s 3.11/edge` (26.04) and `loki-k8s 1/edge` (20.04) instead, which worked fine.
- **Impact**: CI test channels may stop resolving or may not reflect recommended deployment configurations.
- **Fix**: Update test channels to current recommended versions; un-xfail the grafana test once a 26.04-compatible grafana-k8s exists.
- **Linter rule**: not mechanically checkable.

### `test_workload_version.py` mocks the property under test, bypassing the regex bug
- **Severity**: low
- **Kind**: test-gap
- **Where**: `tests/unit/charm/test_workload_version.py:21`
- **Evidence**: The test mocks `_git_sync_version` directly to return `"1.2.3"`, so the real regex at `src/charm.py:593` is never exercised. `_git_sync_version` has 0% coverage in the report despite a test named `test_workload_version_is_set`.
- **Impact**: The regex bug (see above) went undetected by a test that looks like it should have caught it.
- **Fix**: Mock `container.exec` to return a version string (e.g. `"4.7.0"`, no `v` prefix) and assert the regex correctly extracts it; add a case for the `v`-prefixed v3 format too.
- **Linter rule**: mechanically checkable — unit test patches the method/property under test rather than its dependencies.

## Worth copying

1. **Hash-based change detection** (`src/charm.py:444-475`): stores the git worktree hash in peer relation app data and only calls `_reinitialize_*` when it changes — avoids unnecessary churn on related charms.
2. **Intentional failure recovery** (`src/charm.py:258-263`): on git-sync failure the charm goes `BlockedStatus` but does not remove the repo folder or update relation data — existing rules/dashboards stay active during a transient failure. The distinction from `_remove_repo_folder` when `git_repo` is deliberately unset is correctly modelled.
3. **Progressive status precedence** (`src/charm.py:177-272`): `_common_exit_hook` checks conditions in priority order (container readiness → peer relation → config completeness → SSH host verification → SSH proxy → secret/SSH key → sync success → hash file presence), returning early at each stage. Avoids nested conditionals.
4. **Scenario tests for SSH secret validation** (`tests/unit/scenario/test_ssh_config.py`): parametrised over 6 invalid secret URL formats using ops-scenario `Context`, verifying container filesystem side effects from output state.
5. **Deprecation nudge for cleartext SSH keys** (`src/charm.py:240-245`): setting `git_ssh_key` produces `ActiveStatus("WARN: cleartext ssh key, see debug-log")` plus a `logger.warning`, nagging operators toward `git_ssh_key_secret` without breaking anything.
6. **Remote host verification** (`src/charm.py:506-518`, `utils.py`): extracts the remote hostname from the repo URL (3 SSH URL formats supported) and checks it against `known_hosts_config` before SSH, with `extract_remote`/`remote_in_known_hosts` implemented as clean pure functions.
7. **SecretGetter pattern** (`src/secrets_helper.py`): self-contained Juju secret resolution with distinct error handling per failure mode (invalid URL, missing secret, missing permissions, unexpected errors).
8. **Sensible `known_hosts_config` defaults** (`charmcraft.yaml`): pre-populated with github.com and git.launchpad.net SSH keys, so most operators don't need to configure known_hosts manually while the "Unknown host" check still fires correctly for custom hosts.

## Common-practice notes

- **Follows**: standard COS sidecar pattern with git-sync; library usage (`PrometheusRulesProvider`, `GrafanaDashboardProvider`, `LokiPushApiConsumer`) follows canonical patterns.
- **Follows**: `charmcraft.yaml` uses `uv` (`build-snaps: [astral-uv]`, `plugin: uv`) — modern, matches other COS repos.
- **Drifts**: `src/` layout is relatively new — old tests import `from charm import COSConfigCharm` (bare) while scenario tests import `from src.charm import COSConfigCharm` — a transitional state.
- **Drifts**: the Sloth provider uses `charmlibs.interfaces.sloth` from pip rather than a vendored library under `lib/charms/sloth_k8s/`, unlike most COS charms — can't be audited without inspecting the installed wheel.
- **Notable absence**: no overlay bundle, terraform module, or integration test bundle. `cos-configuration-k8s` is deployed solo and related to other charms.
- **Default branch still `master`**: `git_branch` defaults to `master` (open issue #153); the industry has largely moved to `main`.

## Tests

### Unit tests (`tox -e unit`)
- 42 tests pass; full run completes in ~2.18s.
- Coverage: `src/charm.py` 70%, `src/secrets_helper.py` 78%, `src/sloth.py` 85%, `src/utils.py` 100%; overall 74%.
- Framework mix: `test_reinitialize.py`, `test_status_vs_config.py`, `test_workload_version.py`, `test_app_relation_data.py` use the deprecated `ops.testing.Harness` (`PendingDeprecationWarning`); `test_ssh_config.py`, `test_slo_provider.py`, `test_utils.py` use modern `ops-scenario` `Context`.
- Hypothesis property tests: `test_reinitialize.py` and `test_status_vs_config.py` use `@given` over random unit counts and config values.
- Import fragility: running `pytest tests/unit/` without tox fails with `ModuleNotFoundError` because old tests import `from charm import ...` while scenario tests import `from src.charm import ...`. Host `pytest` also fails due to an ops/scenario version mismatch.

### Coverage gaps
- `_on_sync_now_action` (lines 275-300): 0% coverage.
- `_push_ssh_config` (lines 523-569): 0% coverage — SSH proxy config untested (also where the f-string bug lives).
- `_exec_sync_repo` error handling (lines 329-341): `APIError`/`ChangeError` branches untested.
- `tracing_endpoint` property (line 589): untested.
- `_on_upgrade_charm` (line 397): untested at both unit and integration level.
- SSH flag branches in `_git_sync_command_line` (lines 383-385): the `git_ssh_key` branch untested.
- `_on_start` (line 478): untested; just calls `_common_exit_hook()`.

### Integration tests
- 6 files exist in `tests/integration/`; none executed during this review (require a full COS Juju environment). Deployment-log steps above cover the equivalent scenarios manually.
- `test_upgrade_charm.py`: entirely skipped (see Findings) — cross-base upgrade is legitimately unsupported, but a same-base test is missing.
- `test_grafana_dashboards.py`: `@pytest.mark.xfail`, deploys grafana-k8s from `2/edge` (24.04, outdated base).
- `test_kubectl_delete.py`: only asserts the charm returns to `blocked` after pod deletion with no config set — doesn't test recovery with active config/relations (the scenario actually exercised in this review's manual testing).
- `test_loki_push_api.py`, `test_prometheus_scrape.py`: deploy and relate loki/prometheus, assert rules via the workload API; both set `update-status-hook-interval` to 10s as a workaround for a file-appearance timing issue.
- `grafana_workload.py`, `loki_workload.py`, `prometheus_workload.py`: workload API helper modules.
- Channel inconsistency: all integration tests use `2/edge` for related charms (24.04/20.04 bases) while cos-config itself now targets 26.04.

## Docs

- **README.md**: comprehensive — deployment, SSH auth (cleartext and secrets), relation types, verification commands, and the rationale for not injecting Juju topology. The OCI Images section references v3.5.0 and the resource revision table lists only r1 (v3.4.0)/r2 (v3.5.0); the current image is v4.7.0 — the one substantive doc/reality mismatch.
- **CONTRIBUTING.md**: minimal — states the one-cos-config-per-repo design choice and `git-sync --one-time`.
- **INTEGRATING.md**: mermaid diagram of cos-config↔COS relationships; good visual, thin on detail.
- **RELEASE.md**: standard process, but has the "Alertmanager charm" copy-paste artifact (see Findings).
- **SECURITY.md**: standard Canonical security policy.
- **Charmhub description**: accurate, matches observed behaviour.
- **Doc/reality mismatch**: README `juju ssh` examples omit the `--container` flag, which is required on k8s — minor.
- **Default branch**: `git_branch` defaults to `master`, not `main` (open issue #153).

## Open questions

1. **Why is the rock's `git-sync` Pebble service defined but never started?** Is it a relic, or reserved for a future continuous-sync mode (issue #184)?
2. **What is the 24.04→26.04 upgrade path?** The charm now only builds for `ubuntu@26.04`; operators on the 2.x/24.04 track cannot `juju refresh` in place, and there is no documented upgrade story. Cross-base refresh is technically blocked at the Python/venv level (3.12 on 24.04 vs 3.14 on 26.04).
3. **Does `send-remote-write` work end-to-end in production?** `test_prometheus_scrape.py` does exercise this relation in CI (despite its misleading name) and the live deploy confirmed relation data flows correctly; actual remote-write ingestion into a downstream long-term store was not separately verified.
4. **Is `charmlibs.interfaces.sloth` publicly maintained?** It's pip-installed (`pyproject.toml`: `charmlibs-interfaces-sloth>=0.1.0`) rather than vendored under `lib/charms/sloth_k8s/` like other COS libraries — should it be vendored for consistency and auditability?
5. **Can `test_grafana_dashboards.py` be un-xfailed?** It currently targets grafana-k8s `2/edge` (24.04); could it be updated to a 26.04-compatible grafana-k8s and un-marked?
6. **How often are the default `known_hosts_config` keys reviewed?** If GitHub rotates its host keys, operators relying on the shipped defaults will see sync failures surfaced only as the unhelpful "Exited with code 1".
