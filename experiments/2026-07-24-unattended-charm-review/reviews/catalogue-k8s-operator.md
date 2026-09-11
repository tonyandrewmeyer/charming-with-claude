# catalogue-k8s

A Kubernetes charm that serves an nginx-based service catalogue for the Canonical Observability Stack, aggregating links to other Juju-deployed UIs via the `catalogue` relation. The code is clean, passes lint/type checks, and handles the happy path smoothly, but it has a critical TLS lifecycle bug: removing the `certificates` relation leaves the charm serving stale HTTPS with expiring certs while reporting `active/idle`. The deployed revision (2/stable, rev 113) also ships with no nginx access/error logging at all — a regression already fixed on HEAD but not yet released. The current latest channel (3.0) targets `ubuntu@26.04`, which is not deployable on present infrastructure, forcing operators onto the older 2/stable track. A maintainer's first move should be backporting the TLS-removal fix and the nginx logging fix to a channel that targets `ubuntu@24.04`.

| | |
|---|---|
| Repo | canonical/catalogue-k8s-operator @ `803e5d0` (main, 2026-07-02); deployed rev 113 from track/2 |
| Charms | catalogue-k8s |
| Substrate | k8s |
| Deployed | yes — concierge-k8s-4 (juju 4.0.5), channel 2/stable rev 113; also concierge-k8s-3 (juju 3.6.25), same channel/rev |
| Reviewed | 2026-07-24 |

## What it does

Catalogue-k8s deploys a web landing page that automatically discovers and links to the UIs of other Juju-deployed charms. Charms register via the `catalogue` relation interface, providing name, URL, icon, and description; the charm aggregates these into a static JSON config served by nginx. It supports TLS via the `certificates` relation, ingress via Traefik, and optional integration with Loki, Tempo, and Istio. It can also act as a catalogue consumer, forwarding its own entry to a parent catalogue via `catalogue-item`.

## Deployment log

### Juju 4.0.5 (concierge-k8s-4)
```
juju switch concierge-k8s-4
juju add-model rv-catalogue-k8s

# 3.0/edge fails: "the charm defined bases 'ubuntu@26.04' not supported"
juju deploy catalogue-k8s --channel 3.0/edge  # FAILS

# 2/stable works (ubuntu@24.04)
juju deploy catalogue-k8s --channel 2/stable \
  --resource catalogue-image=ghcr.io/canonical/catalogue-k8s-operator:0.15
# Deployed rev 113, active/idle in ~15s

# TLS via self-signed-certificates
juju deploy self-signed-certificates --channel 1/edge --trust
juju integrate catalogue-k8s:certificates self-signed-certificates:certificates
# Charm reconfigures nginx to HTTPS, pushes certs to /etc/catalogue/certs/, active/idle

# Ingress via traefik
juju deploy traefik-k8s --channel latest/stable --trust
juju integrate catalogue-k8s:ingress traefik-k8s:ingress
# get-url action returns: http://10.43.45.0/rv-catalogue-k8s-catalogue-k8s

# Scale up → 2 units: both active, both get TLS certs, clean
# Scale down → 1 unit: clean

# All actions: only `get-url` exists, works correctly with and without ingress

# Deliberately break: invalid JSON in config
juju config catalogue-k8s links='not valid json'
# Charm → error state: "hook failed: config-changed" with JSONDecodeError traceback
juju config catalogue-k8s links='[{"category":"Test","items":[{"name":"Test","url":"https://test.com"}]}]'
# Recovers to active/idle

# Remove TLS relation
juju remove-relation catalogue-k8s:certificates self-signed-certificates:certificates
# Charm stays active/idle — nginx config NOT updated (still HTTPS with stale certs on disk)
# Only regenerated to HTTP when a subsequent config-changed fires (override_hostname change)

# Kill nginx process
juju ssh --container catalogue catalogue-k8s/0 "pkill -9 nginx"
# Pebble auto-restarts nginx; charm never notices, stays ActiveStatus

# Set empty title config
juju config catalogue-k8s title=''  # No crash, charm stays active

# Remove application
juju remove-application catalogue-k8s --force
# ingress-relation-departed hook FAILED on catalogue-k8s/0 during teardown
# Application was eventually removed
```

### Juju 3.6.25 (concierge-k8s-3)
```
juju add-model rv-catalogue-k8s-36
juju deploy catalogue-k8s --channel 2/stable \
  --resource catalogue-image=ghcr.io/canonical/catalogue-k8s-operator:0.15
# Deployed rev 113, active/idle in ~15s

# Hook order differs from juju 4.x:
# 3.6: install → replicas-relation-created → leader-elected → catalogue-pebble-ready → config-changed → start
# 4.x: install → replicas-relation-created → leader-elected → config-changed → start → catalogue-pebble-ready
# On 3.6, pebble-ready fires BEFORE config-changed; on 4.x, config-changed fires first

# TLS integration: works
# TLS removal: SAME BUG — stays active with HTTPS config after relation removal
```

### Integrations attempted but blocked by ubuntu@26.04
- prometheus-k8s (dev/edge) — fails, ubuntu@26.04 only
- loki-k8s (dev/edge) — fails, ubuntu@26.04 only
- grafana-k8s — fails, ubuntu@26.04 only

No catalogue-item providers or logging consumers are deployable on current infrastructure. All modern COS charms target ubuntu@26.04.

## Observed behaviour

- **Startup time**: ~15s from deploy to active/idle on both Juju versions. On 4.x, `config-changed` fires before `catalogue-pebble-ready`, resulting in a transient "Waiting for Pebble ready" status.
- **Resource usage**: 41 MiB memory, negligible CPU (idle). Charm package is 16 MB compressed.
- **Hook order differs between Juju versions**: on 3.6, `catalogue-pebble-ready` fires before `config-changed`; on 4.0.5, the opposite. The charm handles both sequences gracefully (returns `WaitingStatus` when the container is not yet ready).
- **Hook count on deploy (4.x)**: install, replicas-relation-created, leader-elected, config-changed, start, catalogue-pebble-ready — 6 hooks.
- **TLS cert removal not detected (both Juju versions)**: after `juju remove-relation catalogue-k8s:certificates`, the charm stayed active/idle with the HTTPS nginx config and cert files still on disk. The config was only regenerated to HTTP when a subsequent `config-changed` fired (triggered here by an `override_hostname` change). The charm does not observe `certificates-relation-broken`/`-departed` or any "certificate removed" event from the TLS library. Runtime-observed, not inferable from code alone.
- **Cert files not cleaned up**: even after the nginx config regenerated to HTTP, stale cert files at `/etc/catalogue/certs/*` remained on disk. The `_push_certs` cleanup path only runs when `push_certs=True`, which only happens on `certificate_available` and `pebble_ready`.
- **Invalid config crash**: setting `links` to a non-JSON string raises `json.decoder.JSONDecodeError` on every hook, putting the charm in error state with a raw Python traceback. Recovery requires setting a valid value.
- **Empty config values**: setting `title=''` does not crash the charm; empty strings are accepted for string config values.
- **Pebble auto-restart masks crashes (both Juju versions)**: killing nginx with `SIGKILL` causes Pebble to restart it automatically; the charm never observes the crash and continues reporting `ActiveStatus`, even if nginx were in a crash loop.
- **No nginx logs in deployed revision (rev113)**: the rev113 nginx config lacks `access_log`/`error_log` directives in both the HTTP and HTTPS templates, so Pebble log forwarding is silent regardless of TLS state. HEAD adds these lines to both templates.
- **Unused `upstream self` block**: the HTTP nginx config in rev113 defines an upstream block pointing to `localhost:80` never referenced by any `proxy_pass`. Removed in HEAD.
- **Tracing warnings**: every hook emits `WARNING server_ca_cert_path is None; sending traces over INSECURE connection.` — noisy but harmless in a test environment.
- **Port 80 always exposed on juju 4.x**: `self.unit.set_ports(80)` is called unconditionally in `__init__`, even when TLS is configured and the charm only serves on 443. Juju 3.6 does not surface port information in status.
- **ingress-relation-departed hook failure during teardown**: `juju remove-application catalogue-k8s --force` triggers a failing `ingress-relation-departed` hook (exit status 1) on the unit, briefly putting it in error state before the forced removal proceeds; traefik-k8s also errors on `ingress-relation-broken`.
- **Scale up/down clean**: scaling to 2 and back to 1 works without errors; both units independently configure TLS and serve correctly.
- **`get-url` action**: works correctly, returning the ingress URL when related to Traefik, otherwise the internal FQDN URL.

## Findings

### 1. No handler for TLS certificate removal — charm serves stale HTTPS config after relation removal
- **Severity**: critical
- **Kind**: bug
- **Where**: `charm/src/charm.py:122-125` (event subscription), `charm/src/charm.py:175-176` (`_on_certificate_available`)
- **Evidence**: The charm observes only `self._cert_requirer.on.certificate_available` (line 124). The handler at 175-176 only provisions certs, it never handles removal, and `TLSCertificatesRequiresV4` emits no "certificate removed" event. `certificates-relation-departed`/`-broken` fire on relation removal but neither is observed. Confirmed on both Juju 4.x and 3.6: after removing the TLS relation, `juju status` showed active/idle while `/etc/nginx/nginx.conf` still contained the HTTPS server block and cert files remained on disk; config only regenerated on a subsequent, unrelated `config-changed`.
- **Impact**: An operator who removes or loses the TLS relation (e.g. the CA charm is removed) ends up serving HTTPS with certs that will eventually expire, causing connection failures, while the charm continues reporting `ActiveStatus` on a broken configuration.
- **Fix**: Observe `self.on.certificates_relation_broken` and call `self._configure(self.items, push_certs=True)` to regenerate the nginx config and remove stale cert files. Alternatively, reconcile TLS state on `update_status`.
- **Linter rule**: charm that uses `TLSCertificatesRequiresV4` must observe `certificates-relation-broken` (or `update-status`) to handle TLS removal — mechanically checkable by detecting `TLSCertificatesRequiresV4` usage without a corresponding observer.

### 2. Unguarded JSON parse of config `links` crashes the charm on invalid input
- **Severity**: high
- **Kind**: bug
- **Where**: `charm/src/charm.py:325` (`charm_config` property)
- **Evidence**: `"links": json.loads(cast(str, self.model.config["links"])),` has no try/except. Confirmed: `juju config catalogue-k8s links='not valid json'` put the charm in error state with `json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)`, propagating from `charm_config` → `_update_catalogue_config` → `_configure`, with no recovery until a valid value was set.
- **Impact**: An operator pasting malformed JSON crashes the charm; it cannot self-recover, and the traceback gives no operator-friendly guidance.
- **Fix**: Wrap the `json.loads()` call in try/except `json.JSONDecodeError`, log clearly, and set `BlockedStatus("Invalid JSON in 'links' config")` or fall back to an empty list.
- **Linter rule**: `json.loads()` on config values must be wrapped in try/except `JSONDecodeError` — mechanically checkable.

### 3. Unguarded JSON parse of `api_endpoints` from untrusted relation data
- **Severity**: medium
- **Kind**: bug
- **Where**: `charm/lib/charms/catalogue_k8s/v1/catalogue.py:219`
- **Evidence**: `"api_endpoints": json.loads(relation.data[relation.app].get("api_endpoints", "{}")),` inside `CatalogueProvider.items`, with no try/except. Since every event handler calls `self.items`, a remote charm writing invalid JSON to that field would crash any hook.
- **Impact**: A misbehaving or malicious remote charm can crash the catalogue via its own relation databag; the catalogue charm has no defence.
- **Fix**: Wrap in try/except `JSONDecodeError`, log a warning, default to `{}`.
- **Linter rule**: `json.loads()` on relation data must be wrapped in try/except — mechanically checkable.

### 4. Nginx config lacks access_log and error_log directives — Pebble log forwarding silent (deployed rev113)
- **Severity**: medium
- **Kind**: bug
- **Where**: `charm/src/nginx_config.py:19-44` (HTTP_SERVICE), `charm/src/nginx_config.py:50-73` (HTTPS_SERVICE) — track/2 (rev113)
- **Evidence**: Neither directive is present in either template in the deployed rev113. Verified via `juju ssh --container catalogue catalogue-k8s/0 "cat /etc/nginx/nginx.conf"` and by diffing against `git show rev113:charm/src/nginx_config.py`. HEAD adds `access_log /dev/stdout;` and `error_log /dev/stderr;` to both templates, but this fix has not reached a deployable channel (3.0 targets `ubuntu@26.04`).
- **Impact**: Operators relying on Pebble log forwarding (e.g. via Loki) get zero nginx access/error visibility on the currently deployable revision.
- **Fix**: Already fixed on HEAD — needs backporting to a channel that targets `ubuntu@24.04`.
- **Linter rule**: nginx config in Pebble-based charms should include `access_log`/`error_log` directives to stdout/stderr — mechanically checkable by pattern matching.

### 5. Nginx config advertises deprecated TLSv1 and TLSv1.1
- **Severity**: medium
- **Kind**: bug
- **Where**: `charm/src/nginx_config.py:72` (rev113; same in HEAD)
- **Evidence**: `ssl_protocols TLSv1 TLSv1.1 TLSv1.2 TLSv1.3;` — TLSv1.0/1.1 are deprecated by RFC 8996 (March 2021) and considered insecure.
- **Impact**: The catalogue could be flagged by security scanners; modern browsers already block these versions but the server still negotiates them.
- **Fix**: `ssl_protocols TLSv1.2 TLSv1.3;`
- **Linter rule**: nginx `ssl_protocols` should not include TLSv1 or TLSv1.1 — mechanically checkable by pattern matching.

### 6. Charm does not detect workload crashes — stays ActiveStatus in a crash loop
- **Severity**: medium
- **Kind**: bug
- **Where**: `charm/src/charm.py:109-112` (no `update_status` handler observed)
- **Evidence**: The charm only observes event-driven hooks (`pebble_ready`, `config_changed`, `upgrade_charm`, relation events); no `update_status` handler, health check, or Pebble service status check. Confirmed: `pkill -9 nginx` inside the container caused Pebble to auto-restart nginx, and the charm never noticed, staying `ActiveStatus`.
- **Impact**: `juju status` can show active/idle while the service is actually down or crash-looping, breaking the Juju status contract.
- **Fix**: Add an `update_status` handler checking `self.workload.get_service(self.name).is_running()`, or an internal HTTP health check, setting `BlockedStatus`/`WaitingStatus` on failure.
- **Linter rule**: k8s charms should observe `update_status` for workload health reporting — partially mechanically checkable (absence of observation).

### 7. Unsorted items cause unnecessary nginx restarts (flapping)
- **Severity**: medium
- **Kind**: bug
- **Where**: `charm/src/charm.py:173` (items used unsorted), config comparison in `_update_catalogue_config` (line 246)
- **Evidence**: `self._configure(event.items)` in `_on_items_changed` consumes `CatalogueProvider.items`, whose ordering depends on relation iteration order, which is not guaranteed stable. `_update_catalogue_config` compares new config (including items) against `_running_catalogue_config`; differently-ordered but identical data triggers a spurious `workload.push()` and nginx restart. Tracked as issue #250.
- **Impact**: Every hook could trigger an unnecessary nginx restart and brief service disruption, more likely on models with many catalogue items.
- **Fix**: Sort items by a stable key (e.g. name) before writing to `config.json` and before comparing against the running config.
- **Linter rule**: unordered collections written to on-disk files should be sorted — mechanically checkable (existing flaplint rule).

### 8. ingress-relation-departed hook fails during charm teardown
- **Severity**: medium
- **Kind**: bug
- **Where**: `charm/src/charm.py:85-91` (`IngressPerAppRequirer` initialization)
- **Evidence**: `juju remove-application catalogue-k8s --force` produced a failing `ingress-relation-departed` hook (exit status 1) on catalogue-k8s/0 before force removal proceeded; debug-log showed `ERROR juju.worker.uniter.operation hook "ingress-relation-departed" ... failed: exit status 1`. traefik-k8s also errored on `ingress-relation-broken`.
- **Impact**: A plain `remove-application` leaves error artifacts in status/debug-log even though removal ultimately succeeds with `--force`; without `--force` this could block clean removal.
- **Fix**: Either `IngressPerAppRequirer` should tolerate teardown (relation data unavailable), or the charm should observe `ingress-relation-departed`/`-broken` and handle errors gracefully rather than letting them propagate.
- **Linter rule**: not established (runtime behaviour, not mechanically checkable).

### 9. Dead `upstream self` block in HTTP nginx config (deployed rev113)
- **Severity**: low
- **Kind**: lint
- **Where**: `charm/src/nginx_config.py:33-35` (rev113/track-2)
- **Evidence**: `upstream self { server localhost:80; }` is defined but never referenced by any `proxy_pass`; the server block serves files directly from `/web`. Removed in HEAD.
- **Impact**: Dead code that could confuse future maintainers about the architecture.
- **Fix**: Remove the unused upstream block (already done in HEAD).
- **Linter rule**: not established (structural pattern matching on nginx config needed).

### 10. ubuntu@26.04 base requirement blocks deployment on current infrastructure
- **Severity**: low
- **Kind**: bug
- **Where**: `charm/charmcraft.yaml:45`
- **Evidence**: `platforms: ubuntu@26.04:amd64:` for the 3.0 channel (rev 148). Confirmed: `juju deploy catalogue-k8s --channel 3.0/edge` fails with `the charm defined bases "ubuntu@26.04" not supported`; only 2/stable (ubuntu@24.04) is deployable. All COS companion charms tested (prometheus-k8s, loki-k8s, grafana-k8s) also target ubuntu@26.04, blocking integration testing.
- **Impact**: Operators following the default/latest channel hit a deployment failure; the only workable channel (2/stable) is old and not obviously discoverable.
- **Fix**: Keep at least one active channel targeting `ubuntu@24.04` until 26.04 infrastructure is widely available, or publish multi-base with `ubuntu@24.04` alongside `ubuntu@26.04`.
- **Linter rule**: charm should support at least one currently deployable Ubuntu LTS base — mechanically checkable against known deployed bases.

### 11. Unit tests use deprecated `Harness` (ops.testing)
- **Severity**: low
- **Kind**: test-gap
- **Where**: `charm/tests/unit/test_charm.py:26`
- **Evidence**: `self.harness = Harness(CatalogueCharm)` emits `PendingDeprecationWarning: Harness is deprecated`; `test_override_hostname.py` and `test_logging.py` already use the modern `ops.testing.Context`.
- **Impact**: `Harness`-based tests will eventually break when it's removed from ops; the suite mixes two testing styles.
- **Fix**: Migrate `test_charm.py` to `ops.testing.Context`; a branch `chore/change-harness-test-scenario` in the repo suggests this is already planned.
- **Linter rule**: `ops.testing.Harness` should not be used in new tests — mechanically checkable.

### 12. Catch-all `Exception` in `_push_certs` error handler
- **Severity**: low
- **Kind**: bug
- **Where**: `charm/src/charm.py:200`
- **Evidence**: `except (ProtocolError, PathError, Exception) as e:` — listing `Exception` alongside specific types is redundant and overly broad, and also catches `KeyboardInterrupt`/`SystemExit`.
- **Impact**: Hides unexpected errors under one blanket handler, making debugging harder.
- **Fix**: Drop the generic `Exception` and list only the specific exceptions expected from `workload.push()`/`workload.remove_path()`.
- **Linter rule**: bare `Exception` in except clause — mechanically checkable.

### 13. Charm-level README uses wrong interface name
- **Severity**: low
- **Kind**: docs
- **Where**: `charm/README.md:12`
- **Evidence**: README states: "Relate the charm to an ingress of your choice, followed by any charms implementing the providing side of the `dashboard_info` interface." The actual interface is `catalogue`; `dashboard_info` appears to be a stale pre-release name.
- **Impact**: Operators and new charm authors following the README will use the wrong interface name.
- **Fix**: Replace `dashboard_info` with `catalogue`.
- **Linter rule**: interface names in docs should match `metadata.yaml`/`charmcraft.yaml` — mechanically checkable by cross-reference.

### 14. Port 80 always advertised even when TLS-only
- **Severity**: nit
- **Kind**: ux
- **Where**: `charm/src/charm.py:60`
- **Evidence**: `self.unit.set_ports(80)` is called unconditionally in `__init__`; when TLS is active nginx only listens on 443, but the unit still advertises `80/tcp` in `juju status` on Juju 4.x.
- **Impact**: Confusing status output — advertised port isn't actually serving.
- **Fix**: Move `set_ports` into `_configure` and set dynamically based on `_tls_available` (80 for HTTP, 443 for HTTPS).
- **Linter rule**: not established.

### 15. `_on_certificate_available` calls `provide_ingress_requirements` unconditionally
- **Severity**: nit
- **Kind**: performance
- **Where**: `charm/src/charm.py:178-181`
- **Evidence**: `self._ingress.provide_ingress_requirements(scheme=parsed.scheme, port=port)` runs every time `_on_certificate_available` fires, even when scheme/port are unchanged (e.g. certificate rotation).
- **Impact**: Unnecessary relation data writes on cert rotation — minor.
- **Fix**: Compare current scheme/port against previous values before calling `provide_ingress_requirements`.
- **Linter rule**: not established.

## Worth copying

- **Clean reconciliation pattern in `_configure`** (`charm/src/charm.py:193-224`): checks current vs desired state across nginx config, catalogue config, and pebble layer, only pushing/restarting when something changed. `_running_nginx_config`/`_running_catalogue_config` (lines 265-286) implement read-back verification, avoiding unnecessary restarts.
- **`push_certs` parameter pattern**: a boolean flag on `_configure` avoids pushing certs (an expensive multi-file write) on every hook.
- **Catalogue library v1 separation of concerns** (`charm/lib/charms/catalogue_k8s/v1/catalogue.py`): clean split between `CatalogueProvider` and `CatalogueConsumer`, with a well-designed `CatalogueItem` dataclass.
- **Mixed test styles with a migration path**: `Context`-based tests (`test_override_hostname.py`, `test_logging.py`) are concise and show the modern pattern well, with a branch already in flight to migrate the remaining `Harness` tests.
- **Good static analysis setup**: `pyproject.toml` configures ruff, pyright, and codespell sensibly; both `ruff check` and `pyright` pass cleanly.
- **No `defer()` or `StoredState` usage**: the charm is fully event-driven with a reconciliation pattern, avoiding two of the most common sources of ops charm state bugs.

## Common-practice notes

- **Follows**: single `src/charm.py` layout, `lib/charms/<name>/v<N>/` library hierarchy, `tox.ini` with lint/static/unit/integration environments — standard COS charm conventions.
- **Follows**: `charmcraft.yaml` explicitly declares all relations, config, actions, containers, and resources; `assumes: [k8s-api, juju >= 3.6]` is good practice.
- **Drifts**: `IngressPerAppRequirer`'s `scheme` parameter uses a lambda (`scheme=lambda: urlparse(self._internal_url).scheme`) rather than the usual static string — works, but adds indirection.
- **Drifts**: the charm acts as both `CatalogueProvider` and `CatalogueConsumer` (forwarding itself to a parent catalogue); this dual role is uncommon and undocumented in the README.
- **Drifts**: `charmcraft.yaml` declares a `replicas` peer relation but no code in `src/`/`lib/` references it — appears vestigial or reserved for future scale-out; no code coordinates multiple units.

## Tests

- **Unit tests**: 10 tests across 3 files, all passing (with `PYTHONPATH` set correctly). Coverage: 89% for `src/charm.py`, 100% for `src/nginx_config.py`.
- **Test styles**: mixed — `test_charm.py` uses deprecated `Harness`; `test_override_hostname.py`/`test_logging.py` use modern `ops.testing.Context`. Migration branch `chore/change-harness-test-scenario` exists.
- **Coverage gaps** (untested paths in `charm.py`):
  - `_push_certs` when TLS config is `None` (cert removal path, lines 185-187)
  - `_configure` error handling for cert push failures (lines 200-203) and restart failures (lines 217-221)
  - `_on_certificate_available` callback itself (line 167) — `test_server_cert` patches away `_push_certs` and only checks URL scheme
  - No test for the TLS-removal scenario (`certificates-relation-broken`)
  - No test for invalid `links` config JSON
  - No test for `_running_nginx_config`/`_running_catalogue_config` returning empty on `can_connect=False`
  - No test for `override_hostname` being `None`/empty
- **Integration tests**: 3 files. `test_charm.py` deploys, relates to self-signed-certificates, verifies HTTPS, and relates to prometheus-k8s for catalogue items; `test_ingress.py`/`test_logging.py` cover ingress and Loki. Tests use `jubilant` and assert real HTTP responses and config file contents, with `tenacity` retries for eventual consistency — good beyond simply waiting for active/idle.
- **Not run**: integration tests were not executed here — they require a full COS stack, and the prometheus-k8s/loki-k8s dependencies cannot deploy on this cluster (`ubuntu@26.04` only).
- **Static analysis**: `ruff check` → all checks passed. `pyright` → 0 errors, 0 warnings. `codespell` → 2 false positives (`defintion` in the istio lib, `aNULL` in nginx `ssl_ciphers`).

## Docs

- **Repo README**: minimal (two sentences).
- **Charm README**: brief, covers usage, OCI images, and contributing links; has a bug — says `dashboard_info` interface instead of `catalogue`.
- **Charmhub description**: comprehensive, lists all features/relations, matches `charmcraft.yaml`.
- **CONTRIBUTING.md**: present and detailed (environment setup, testing, coding standards).
- **Terraform module**: exists under `charm/terraform/` with its own README and tagged releases (`tf-3.0.0` through `tf-3.0.3`).
- **Key doc gaps**:
  - No documentation of the `links` config JSON schema (format only discoverable from the default value) — related to open issue #199 about broken links.
  - No mention of the `override_hostname` config option.
  - No mention of the dual provider/consumer role.
  - No upgrade/migration documentation between 2/stable and 3.0.

## Open questions

1. Why does the charm declare a `replicas` peer relation (`interface: catalogue_replica`) when no code references it? Is scale-out planned?
2. What is the intended upgrade path from 2/stable to 3.0, given 3.0 targets `ubuntu@26.04` with no migration documentation? Operators on 2/stable are effectively stuck until 26.04 infrastructure is available.
3. `_update_status` (line 162-164) sets both unit and app status, but only unit status when not leader — if a non-leader later becomes leader, is stale app status intentional? (unverified)
4. Should the charm observe `update_status` for TLS reconciliation, trading increased hook frequency for detecting a stale TLS relation state sooner?
