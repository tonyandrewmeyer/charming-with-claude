# traefik-k8s

A mature, feature-rich Kubernetes ingress charm built on Traefik v2. The codebase is large (~2100 lines in `charm.py`) and covers per-app/per-unit ingress, traefik-route, TLS via `tls-certificates` or local config, forward-auth, observability, and ingress chaining, backed by an extensive test suite (552 unit/scenario tests, 86% coverage). It deploys cleanly, survives scaling, refresh, and workload crashes without issue. But it ships two **critical** bugs that put the charm into a permanent, unrecoverable crash loop from ordinary operator actions (removing a broken requirer, or a typo in `routing_mode`), plus a **high**-severity gap where malformed TLS material is accepted and served as if valid, a **high**-severity cluster of `cached_property` staleness bugs that make several config options silently no-ops, and a **high**-severity bug that deletes the LoadBalancer service on a bad annotation string. A maintainer should first fix the two crash-loop bugs (`wipe_ingress_data`'s unguarded `del`, and the unguarded `RoutingMode()` call in `__init__`), since both leave the charm in `error` state with no self-recovery path.

| | |
|---|---|
| Repo | canonical/traefik-k8s-operator @ 51ffb5e (2026-07-23) |
| Charms | traefik-k8s |
| Substrate | k8s |
| Deployed | yes — concierge-k8s-4 (Juju 4.0.5) and concierge-k8s-3 (Juju 3.6.25), stable rev 377 and edge rev 393 |
| Reviewed | 2026-07-25 |

## What it does

Traefik-k8s deploys a Traefik reverse proxy / ingress controller on Kubernetes. It watches Juju relations for ingress requests and generates Traefik dynamic configuration files. Key capabilities:

- **Ingress v2 (per-app)** and **v1 (legacy per-leader)** via `ingress` relation, load-balancing across all units
- **Ingress-per-unit** via `ingress-per-unit` relation, routing to individual pods (HTTP and TCP)
- **Traefik-route** relation for direct static/dynamic config injection
- **TLS termination** via `tls-certificates` relation or local `tls-ca`/`tls-cert`/`tls-key` config
- **Certificate transfer** (`receive-ca-cert`) for trusting external CAs
- **Path** and **subdomain** routing modes
- **Upstream ingress chaining** to layer multiple Traefik instances
- **Forward-auth** (experimental) for integration with Oathkeeper
- **Observability**: Prometheus metrics, Grafana dashboard, Loki logging, Tempo tracing
- **LoadBalancer annotations** config

## Deployment log

```bash
# Initial deployment (Juju 4.0.5, concierge-k8s-4, model rv-traefik)
juju add-model rv-traefik
juju deploy traefik-k8s --channel stable --trust                # rev 377, ubuntu@20.04
# deploy took ~18s from "installing agent" to active/idle
# initially cycles through blocked ("Traefik load balancer is unable to obtain an IP...")
# then goes active: "Serving at http://10.43.45.0"

# Config changes
juju config traefik-k8s routing_mode=subdomain
# -> blocked: "external_hostname" must be set while using routing mode "subdomain"  ✓
juju config traefik-k8s external_hostname=test.example.com
# -> active: "Serving at http://test.example.com"  ✓

# CRITICAL BUG #1: Set invalid routing mode -> charm crashes entirely
juju config traefik-k8s routing_mode=random
# -> error: hook failed: "config-changed" — stuck in crash loop
# ValueError in RoutingMode() triggered from __init__, before event handlers registered
# Had to juju resolve and reset config externally. Confirmed on Juju 3.6.25 too.

# TLS integration
juju deploy self-signed-certificates --channel stable
juju relate traefik-k8s:certificates self-signed-certificates:certificates
# -> active: "Serving at https://10.43.45.0"  ✓
# certificates.yaml created at /opt/traefik/juju/ with cert, key, TLS options

# TLS relation removal
juju remove-relation self-signed-certificates:certificates traefik-k8s:certificates
# -> active: "Serving at http://10.43.45.0"  ✓

# Actions
juju run traefik-k8s/0 show-proxied-endpoints   # {"traefik-k8s": {"url": "http://10.43.45.0"}}  ✓
juju run traefik-k8s/0 show-external-endpoints  # {"traefik-k8s": {"url": "http://10.43.45.0"}}  ✓

# Annotations cached_property bug
juju config traefik-k8s loadbalancer_annotations="key1=val1,key2=val2"
# -> no annotations appear on the LB service; further changes never apply without pod restart

# Deeper testing deployment (Juju 4.0.5, model rv-traefik-deep)
juju add-model rv-traefik-deep
juju deploy traefik-k8s --channel stable --trust
juju deploy self-signed-certificates --channel stable
juju relate traefik-k8s:certificates self-signed-certificates:certificates
# -> active: "Serving at https://10.43.45.0"  ✓

# Bad TLS config, partial (cert only, no key/ca)
juju config traefik-k8s tls-cert="badcert"
# -> blocked: "Please set tls-cert, tls-key, and tls-ca"  ✓

# CRITICAL BUG #2: Force-remove requirer while ingress relation exists
juju deploy any-charm --channel edge ingress-requirer \
  --config src-overwrite='{"requires": {"ingress": {"interface": "ingress"}}}' \
  --config python-packages='["ops"]'
# ingress-requirer fails install (no ingress library), relation created anyway
juju relate ingress-requirer:ingress traefik-k8s:ingress
# traefik-k8s goes blocked: "setup of some ingress relation failed"
# Remove the broken requirer
juju remove-application ingress-requirer --force
# -> traefik-k8s stuck in error: hook failed: "config-changed" permanently
# Error: _wipe_ingress_for_relation -> wipe_ingress_data -> del relation.data[self.app]["ingress"]
#   -> ModelError: "cannot read relation application settings: permission denied"
# The try/except in wipe_ingress_data guards relation.data access but NOT the del operation

# BUG #3: Bad TLS config (all three fields) accepted silently
juju config traefik-k8s tls-cert="bad-cert-data" tls-key="bad-key-data" tls-ca="bad-ca-data"
# -> active: "Serving at https://10.43.45.2" — but cert files contain "bad-cert-data" literally!
# No PEM validation whatsoever. Traefik serves broken TLS while charm reports active.

# Kill workload process -> Pebble restarts, charm stays active  ✓
kubectl exec -n rv-traefik-deep traefik-k8s-0 -c traefik -- kill $(pgrep traefik)
# -> traefik restarted by Pebble within 1s, charm never left active  ✓

# Juju 3.6 scaling test (model rv-traefik3)
juju scale-application traefik-k8s 2
# -> unit 1 starts, both active, serving same https://test3.example.com  ✓
juju scale-application traefik-k8s 1
# -> unit 1 terminates cleanly, unit 0 stays active  ✓

# Refresh test (Juju 4.0.5, model rv-traefik-final)
juju deploy traefik-k8s --channel stable --trust  # rev 377
juju refresh traefik-k8s --channel edge            # rev 393
# -> active, pod recreated (IP changes), LB IP unchanged  ✓

# Same refresh on Juju 3.6: rev 377 -> 393 — successful  ✓

# Remove application (Juju 4.0.5)
juju remove-application traefik-k8s
# -> pod and LB service removed cleanly, app scale 0, no errors  ✓

# Same on Juju 3.6: clean teardown including storage detachment  ✓

# Cleanup: destroyed rv-traefik, rv-traefik-deep, rv-traefik-final (k8s-4), rv-traefik3 (k8s-3)
```

Attempted observability integration (grafana-k8s, loki-k8s, prometheus-k8s) in a separate model but these require ubuntu@26.04, unsupported on the available clusters — not tested.

## Observed behaviour

- **Startup time**: ~18s from deployment to active/idle on both Juju versions
- **Memory**: 63Mi for the pod (charm + workload), very reasonable
- **CPU**: 376m at startup, idle afterwards
- **Workload**: Traefik v2.11.49, running via Pebble with `tee /var/log/traefik.log` for log capture
- **Static config**: Generated at `/etc/traefik/traefik.yaml` with entrypoints web:80, websecure:443, diagnostics:8082
- **Dynamic config**: Stored at `/opt/traefik/juju/` (on a Juju storage volume, survives pod churn)
- **LB service**: `traefik-k8s-lb` of type LoadBalancer, ports 80 and 443
- **TLS recovery (relation)**: Removing the TLS relation correctly cleans up `certificates.yaml` and cert/key files, reverting to http scheme ✓
- **Trivial config change** (setting `routing_mode=path` when it's already `path`): 13 "restarting"/"replan" log entries — every config-changed triggers a full Traefik restart because `_on_change` calls `_configure()` directly, bypassing the `_update_config_if_changed` hash guard. Even a no-op config set restarts the workload.
- **Kill workload → Pebble recovery**: Killing the traefik process inside the container results in Pebble restarting it within 1 second. Charm stays active throughout. ✓
- **Scale up/down**: Scaling from 1→2→1 on Juju 3.6 worked correctly, both units active, clean teardown of the scale-down unit. ✓
- **Refresh**: rev 377 (stable) → rev 393 (edge) succeeds on both Juju 3.6 and 4.0.5. Pod is recreated with a new IP but LB IP unchanged. ✓
- **Remove-application**: Clean teardown on both Juju versions. LB service, pod, and storage all removed. ✓
- **Crash loop on invalid `routing_mode`**: The charm enters a permanent `error` state because the `ValueError` from `RoutingMode()` occurs inside `__init__` (via the `_routing_mode` property, accessed during `Traefik` object construction), not inside the guarded `_process_status_and_configurations()` method. Every hook invocation re-creates the charm and hits the same crash. Confirmed on both Juju 4.0.5 and 3.6.25. The existing unit test `test_bad_routing_mode_config_and_recovery` passes only because the ops Harness reuses the same charm instance across events; in production, each hook spawns a new process with a fresh `__init__`.
- **Crash loop on broken relation**: When a remote app is force-removed while an ingress relation exists, every subsequent config-changed hook crashes because `_update_ingress_configurations` → `_process_ingress_relation` → `_wipe_ingress_for_relation` → `wipe_ingress_data` attempts `del relation.data[self.app]["ingress"]`, which raises `ModelError: permission denied`. The try/except in `wipe_ingress_data` only guards the `relation.data` access, not the `del`. Confirmed on Juju 4.0.5.
- **Bad TLS config, partial**: Setting only `tls-cert` (without `tls-key`/`tls-ca`) is correctly rejected with `BlockedStatus("Please set tls-cert, tls-key, and tls-ca")`.
- **Bad TLS config, complete**: Setting `tls-cert`, `tls-key`, `tls-ca` to arbitrary non-PEM strings together is accepted without validation. The cert files contain "bad-cert-data" literally and Traefik serves broken TLS while the charm reports `active` with `https://`.
- **Misleading status when one ingress fails**: When the ingress-requirer relation fails but TLS from self-signed-certificates succeeds, the charm reports "setup of some ingress relation failed" — the operator cannot tell which relation failed or that TLS is actually working correctly.
- **Annotation staleness**: Changing `loadbalancer_annotations` has no effect on the LB service. Only a pod restart picks up the change. Root cause: `@functools.cached_property` on `_loadbalancer_annotations`.

## Findings

### CRITICAL: `wipe_ingress_data` crashes with `ModelError` when remote app is force-removed (permanent crash loop)
- **Severity**: critical
- **Kind**: bug
- **Where**: `lib/charms/traefik_k8s/v1/ingress.py:273`, also `v2/ingress.py:543`, `v1/ingress_per_unit.py:467`
- **Evidence**: `wipe_ingress_data` guards `relation.data` access with try/except for `ModelError`, but `del relation.data[self.app]["ingress"]` sits **outside** that try block. When a remote app is force-removed, `relation.data` access succeeds (the object exists), but `del` triggers a `relation-set` call that fails with `ModelError: "cannot read relation application settings: permission denied (unauthorized access)"`. Confirmed in deployment: force-removing `ingress-requirer` while the ingress relation exists causes a permanent crash loop on every subsequent `config-changed` hook.
- **Impact**: An operator who force-removes a broken requirer charm ends up with a permanently broken Traefik that cannot be recovered without external intervention. The crash propagates through `_wipe_ingress_for_relation` → `_process_ingress_relation` → `_update_ingress_configurations` → `_process_status_and_configurations`, which runs on every hook. Even `juju config` commands crash.
- **Fix**: Move the `del` inside the try/except, or wrap it separately. All three library implementations have the same bug and need the same fix.
- **Linter rule**: "`del relation.data[...]` not guarded by try/except for `ModelError`" — mechanically checkable.

### CRITICAL: Invalid `routing_mode` crashes charm in `__init__` (unrecoverable error state)
- **Severity**: critical
- **Kind**: bug
- **Where**: `src/charm.py:1950` (`_routing_mode` property, called from `__init__` at line 254)
- **Evidence**: `return RoutingMode(self.config["routing_mode"])` is called during `__init__` to construct the `Traefik` object. When `routing_mode` is invalid, `RoutingMode` raises `ValueError`, which is **not caught at this level** — the try/except in `_process_status_and_configurations` is never reached. Confirmed in deployment: `juju config traefik-k8s routing_mode=random` causes a permanent `error: hook failed` crash loop on both Juju 3.6 and 4.0.5.
- **Impact**: A typo in `routing_mode` makes the entire charm non-functional, including `juju config` itself, since every hook crashes in `__init__`. Recovery requires `juju resolve` combined with resetting the config externally. The existing unit test `test_bad_routing_mode_config_and_recovery` passes only because the ops Harness reuses the same charm instance across events — a scenario test with fresh charm construction would catch this.
- **Fix**: Guard the `RoutingMode()` call in the `_routing_mode` property with a try/except and return a safe default (e.g. `RoutingMode.PATH`), or restructure so invalid config never crashes `__init__`. `_process_status_and_configurations` should be the sole validation point.
- **Linter rule**: "Charm `__init__` (including property access during init) must not call functions that can raise exceptions on invalid config values" — partially checkable with call-graph analysis.

### No TLS certificate validation — arbitrary strings accepted as serving certs
- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:907` (`_get_certs`), `src/traefik.py:219,231-233` (`update_cert_configuration`)
- **Evidence**: `_get_certs` casts `self.config["tls-cert"]`, `self.config["tls-key"]`, `self.config["tls-ca"]` directly to strings and passes them to `update_cert_configuration`, which writes them verbatim to `.cert`/`.key` files. No PEM parsing, no `cryptography`/`ssl` check. Confirmed in deployment: setting all three fields to non-PEM strings together results in `active: "Serving at https://10.43.45.2"` while the cert files contain the literal string "bad-cert-data". (Setting only `tls-cert` without key/ca is correctly rejected as incomplete, but complete-but-invalid input passes.)
- **Impact**: An operator providing malformed certificate data gets an `active`/`https://` status with no indication anything is wrong, while Traefik serves non-functional TLS and clients get SSL errors.
- **Fix**: Validate `tls-cert`, `tls-key`, `tls-ca` with `cryptography.x509.load_pem_x509_certificate` / `serialization.load_pem_private_key` before accepting. Set `BlockedStatus` with a clear message on failure.
- **Linter rule**: "TLS config values written to disk without cryptographic validation" — mechanically checkable (file writes of `self.config["tls-*"]` without prior `cryptography`/`ssl` calls).

### Multiple `@functools.cached_property` decorators cache config/API reads forever
- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:624` (`_loadbalancer_annotations`), `:681` (`_get_loadbalancer_status`), `:702` (`_traefik_loadbalancer_ip`), `:1858` (`_traefik_external_address`), `:1875` (`gateway_address`)
- **Evidence**: Five `@functools.cached_property` methods on the charm class read from `self.config`, `self.model`, or the Kubernetes API via `self.lightkube_client`. `cached_property` computes once per charm instance and never invalidates. Confirmed in deployment: `juju config traefik-k8s loadbalancer_annotations="newkey=newval"` had zero effect on the LB service — stale cached annotations were used.
- **Impact**: Operators changing `external_hostname`, `loadbalancer_annotations`, or any config feeding into these properties see the config accepted but no change in behaviour. If a cloud provider reassigns the LB IP, `_get_loadbalancer_status`/`_traefik_loadbalancer_ip` return the stale IP. This is a silent failure — the charm remains `active` and serving with wrong configuration. `_traefik_external_address` in turn nests `_get_loadbalancer_status`, chaining the staleness.
- **Fix**: Replace all five `@functools.cached_property` instances with regular `@property`, or add explicit event-based cache invalidation.
- **Linter rule**: "`functools.cached_property` on a `CharmBase` method" — mechanically checkable.

### Malformed `loadbalancer_annotations` silently deletes the LoadBalancer service
- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:671` (`_reconcile_lb`), `:723` (`_annotations_valid`)
- **Evidence**: `_reconcile_lb` builds `resources_list = []` and only appends `_construct_lb()` if `self._annotations_valid` is True. `_annotations_valid` is `False` whenever `self._loadbalancer_annotations` is `None`, which happens when `parse_annotations` fails on a malformed annotation string. This causes `klm.reconcile([])`, which **deletes the existing LB service**.
- **Impact**: A typo in the annotation config not only fails to apply the annotation but destroys the LoadBalancer service, causing a total ingress outage. Combined with the `cached_property` staleness bug, fixing the config may not recreate the LB without a pod restart.
- **Fix**: Separate "no annotations to apply" from "delete the LB". `_construct_lb` should always be appended; annotations should only augment, not gate existence of the LB resource.
- **Linter rule**: "`reconcile` called with empty list when a service resource exists" — not mechanically checkable with static analysis alone.

### `_config_hash` uses non-deterministic Python `hash()`, making the change-detection guard dead code
- **Severity**: high
- **Kind**: bug, performance
- **Where**: `src/charm.py:1261`
- **Evidence**: `return hash((self._traefik_external_address, self.config["routing_mode"], ...))` — Python's `hash()` is randomized per process (`PYTHONHASHSEED`). Since each Juju hook spawns a new process, the resulting hash differs every invocation, so `_stored.config_hash != new_config_hash` is always `True`. `_update_config_if_changed` therefore always proceeds with full reconfiguration.
- **Impact**: The optimization designed to skip reconfiguration on no-op config changes never triggers, adding unnecessary latency and disruption on every hook. Observed: a config-changed with no actual value change triggers "restarting traefik..." multiple times.
- **Fix**: Use `hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()` instead of `hash()`.
- **Linter rule**: "Use of `hash()` on a non-integer type in a `CharmBase` method" — mechanically checkable.

### `_configure` always runs on config-changed, bypassing the `_update_config_if_changed` guard
- **Severity**: medium
- **Kind**: performance
- **Where**: `src/charm.py:1277` (`_on_change`) vs `:1287-1304` (`_update_config_if_changed`)
- **Evidence**: `_on_change` calls `_configure()` directly, which unconditionally runs `_update_cert_configs`, `_configure_traefik`, `_restart_traefik`, and `_process_status_and_configurations`. `_update_config_if_changed` is only called from the tracing endpoint handlers. Even a trivial `juju config` call that changes nothing triggers a full Traefik restart (13 restart/replan log entries observed for a no-op `routing_mode=path` set).
- **Impact**: Every config change, even a no-op one, restarts Traefik and drops in-flight connections. Since the hash guard is separately broken (see above), fixing only one of the two bugs would not restore the optimization.
- **Fix**: Route `_on_change` through `_update_config_if_changed` after fixing hash determinism, or remove the dead code path to avoid misleading future maintainers.
- **Linter rule**: "Config-changed handler calls `_configure` directly without going through hash guard" — mechanically checkable.

### `_provider_from_relation` defaults to v1 for incomplete/inert relations
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:1820-1841`
- **Evidence**: When neither `is_ready()` for v2 nor v1 returns True, `_provider_from_relation` returns `self.ingress_per_appv1`. A brand-new, empty relation (or one whose remote app has been force-removed) gets routed through the v1 provider, whose `wipe_ingress_data` has the unguarded `del` (see critical finding above).
- **Impact**: This default is the specific path that triggers the critical crash-loop bug: every incomplete ingress relation walks into the v1 path and its unprotected `del`.
- **Fix**: Check whether the remote app exists and can be accessed before attempting a wipe, or add a `can_write` guard to `_wipe_ingress_for_relation`.
- **Linter rule**: not mechanically checkable.

### `_wipe_ingress_for_all_relations` raises `KeyError` when no ingress relations exist
- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:1926` (draft cites `1785`; kept as noted, both locations point to the same loop)
- **Evidence**: `for relation in self.model.relations["ingress"] + self.model.relations["ingress-per-unit"]:` — `model.relations` is a `Mapping` that raises `KeyError` when a relation name is not present.
- **Impact**: Called from the `ready` property and from the error-recovery path in `_process_status_and_configurations`. On a fresh deployment with no ingress relations, this crashes.
- **Fix**: `self.model.relations.get("ingress", []) + self.model.relations.get("ingress-per-unit", [])`
- **Linter rule**: "Direct key access on `model.relations` without `.get()` fallback" — mechanically checkable.

### `ready` property has side effects (status mutation, relation wiping)
- **Severity**: medium
- **Kind**: ux
- **Where**: `src/charm.py:1455-1465`
- **Evidence**: The `ready` property calls `self._wipe_ingress_for_all_relations()` and sets `self.unit.status` as a side effect; the code itself has a `# fixme: no side-effects in prop` comment.
- **Impact**: Reading `self.ready` mutates unit status and wipes relation data as a side effect, which is surprising and can destructively wipe data before the caller decides what to do with the result.
- **Fix**: Refactor into an explicit method, e.g. `_check_ready_and_block_if_not()`, and move status-setting into the event handler.
- **Linter rule**: "Property on `CharmBase` that sets `unit.status`" — mechanically checkable.

### Misleading status message when one ingress relation fails but others succeed
- **Severity**: medium
- **Kind**: ux
- **Where**: `src/charm.py:1436`
- **Evidence**: `self.unit.status = BlockedStatus("setup of some ingress relation failed")` names no specific relation or error. Confirmed in deployment: TLS from self-signed-certificates was working (certs present, serving HTTPS) but status said "setup of some ingress relation failed" because the unrelated `ingress-requirer` had no valid data.
- **Impact**: The operator sees a blocked charm and cannot tell what's wrong or which relation to fix, risking tearing down working TLS while chasing an unrelated failure.
- **Fix**: Include the failing relation name(s) and specific error in the status message.
- **Linter rule**: not mechanically checkable.

### Synchronous DNS lookups can block charm startup
- **Severity**: medium
- **Kind**: performance
- **Where**: `src/charm.py:541` (`_get_cert_requests`), `:1976` (`server_cert_sans_dns`)
- **Evidence**: Both call `socket.gethostbyaddr(target)`, a synchronous DNS lookup that can block for 2-5 seconds on slow DNS. `_get_cert_requests` is reached during `__init__` (via `_get_valid_csrs`), so a slow lookup directly delays every hook that constructs the charm.
- **Impact**: In environments with slow or unavailable reverse DNS, charm startup (measured at 18s in the test environment) could balloon significantly. Not reproducible in the fast-DNS test environment (unverified in a slow-DNS environment).
- **Fix**: Wrap `socket.gethostbyaddr` in a thread with a timeout, or use `dnspython`'s resolver with an explicit timeout.
- **Linter rule**: "`socket.gethostbyaddr` called in a CharmBase method" — mechanically checkable.

### Stale dynamic configs persist on relation-broken until next update-status
- **Severity**: low
- **Kind**: bug
- **Where**: `src/charm.py:1475-1484` (`_handle_ingress_data_removed`)
- **Evidence**: The handler explicitly skips `_process_status_and_configurations()` on `RelationBrokenEvent` (citing a Juju limitation where relation data is still present when broken), calling only `_reconcile_lb()`. Stale dynamic ingress configs persist on disk until the next `update-status` hook (default interval: 5 minutes).
- **Impact**: A removed ingress relation leaves stale routes in Traefik for up to 5 minutes; requests to the stale route fail while Traefik still tries to route them.
- **Fix**: On relation-broken, delete the dynamic config for that relation from disk immediately and flush the change to Traefik's live config.
- **Linter rule**: not mechanically checkable.

### `_wipe_ingress_for_all_relations` misses `traefik-route` relations
- **Severity**: low
- **Kind**: bug
- **Where**: `src/charm.py:1926`
- **Evidence**: The loop only covers `"ingress"` and `"ingress-per-unit"`; `traefik-route` relations are not included.
- **Impact**: When Traefik enters blocked state, dynamic configs for traefik-route relations are left in place, potentially serving stale routes.
- **Fix**: Add `"traefik-route"` to the loop, or iterate over all known ingress relation names.
- **Linter rule**: not mechanically checkable.

### `publish_url` writes to relation data without a `ModelError` guard
- **Severity**: low
- **Kind**: bug
- **Where**: `lib/charms/traefik_k8s/v1/ingress.py:337`, `v2/ingress.py:614`, `v1/ingress_per_unit.py:451`
- **Evidence**: All three `publish_url` methods write to `relation.data[self.app]["ingress"]` without a try/except for `ModelError` — the same unguarded-write pattern as the critical `wipe_ingress_data` bug, on the write side.
- **Impact**: Less likely to trigger in practice since `publish_url` normally follows an `is_ready` check, but if a relation breaks between the check and the call, this crashes.
- **Fix**: Wrap the relation data write in a try/except for `ModelError`.
- **Linter rule**: "`relation.data[...] = ...` not guarded by try/except for `ModelError`" — mechanically checkable.

### `show-proxied-endpoints` returns incomplete data when a provider's `proxied_endpoints` raises
- **Severity**: low
- **Kind**: ux
- **Where**: `src/charm.py:1088-1120` (`_get_proxied_endpoints`)
- **Evidence**: The method catches `Exception` per-provider, logs a warning, and continues, silently omitting the failed provider's endpoints from the action result.
- **Impact**: An operator running `show-proxied-endpoints` may see their app missing and wrongly conclude the relation doesn't exist, when in fact it does but has bad data.
- **Fix**: Include an `"errors"` key in the result listing which providers failed and why.
- **Linter rule**: not mechanically checkable.

## Worth copying

- **`flush_dynamic_configs` with tar archive**: `src/traefik.py:793-851` — builds a tar.gz in memory and extracts atomically, avoiding repeated `push` calls. Good pattern for bulk config updates.
- **TLS cleanup on relation removal**: `src/charm.py:360-378` — `cleanup_tls_configuration` is hooked to multiple events (pebble-ready, start, update-status, config-changed, certificates relation broken) and cleans up `certificates.yaml` when TLS is disabled. Recovery from TLS removal worked flawlessly in testing.
- **Certificate migration logic**: `src/charm.py:482-505` — `_migrate_unit_csrs_to_app_databag` handles upgrading from `Mode.UNIT` to `Mode.APP` cleanly, with clear error messages for corrupt secrets.
- **Forward-auth guard**: `src/charm.py:732-741` — `_on_forward_auth_config_changed` checks `_is_forward_auth_enabled` before processing, preventing relation config from taking effect when the feature flag is off.
- **Extensive integration test matrix**: 36 integration test files covering TLS, upgrades, forward-auth, TCP, route, basic-auth, upstream-ingress, etc. Unusually thorough.
- **`is_hostname` utility**: `src/utils.py` — uses `ipaddress.ip_address` to distinguish IPs from hostnames, avoiding regex-based approaches that get edge cases wrong.
- **Pebble recovery**: Traefik restarted by Pebble within 1s of being killed — process supervision works correctly and transparently.
- **Minimal `StoredState`**: only `config_hash` is stored; all other state is derived from Juju model objects on each hook, avoiding stale stored state (though the hash itself is broken — see finding above).

## Common-practice notes

- **`cached_property` on mutable state**: a known anti-pattern in the ecosystem, particularly severe here because it affects config changes, LB status, and gateway address — all externally visible.
- **`hash()` for config fingerprinting**: several ecosystem charms misuse `hash()` for change detection unaware it's non-deterministic across processes. This instance is particularly impactful because it gates the main optimization path, making `_update_config_if_changed` dead code.
- **Library versioning**: maintains both v3 and v4 TLS certificate libraries and both v1 and v2 ingress libraries — good backward compatibility, with a clear v1 deprecation warning in logs.
- **`tox.ini` layout**: uses `tox -e unit` with uv and scenario tests, following current PFE conventions. 552 tests in 52 seconds.
- **Concierge configs**: both `concierge-juju3.yaml` and `concierge-juju4.yaml` present, testing against both Juju versions.
- **Terraform module**: present at `terraform/` with its own test suite.
- **Code size**: `charm.py` at ~2100 lines is on the large side; `_process_status_and_configurations` alone is ~90 lines with multiple early returns. A reconciliation-based architecture would reduce complexity, but the current level is manageable for the feature set.

## Tests

- **Unit + scenario tests**: 552 passed, 1 skipped, 86% coverage (`charm.py` 87%, `traefik.py` 84%, `utils.py` 83%). Run via `tox -e unit` in ~52 seconds.
- **Scenario tests**: 7 files covering TLS certificates, certificate transfer, upgrade migration, ingress-per-app requirer, certificate cleanup, removal.
- **Integration tests**: 36 files in `tests/integration/`, many using `any-charm` for requirer simulation. Spellbook cache at `tests/integration/spellbook/` for faster runs.
- **Interface tests**: `test_ingress.py` for the ingress library interface contract.
- **Coverage gaps relative to findings**:
  - `_config_hash` early return (`1293->exit`) is untested — the hash always changes so the guard is never observed to work.
  - `parse_annotations` and `is_valid_hostname` (lines ~1971-2014) are untested — would catch the LB-deletion finding.
  - `wipe_ingress_data` error path — no test for `ModelError` on `del`; would catch the critical crash finding.
  - `_get_certs` with invalid PEM — no test; would catch the TLS-validation finding.
  - `_provider_from_relation` default-v1 fallback path is untested.
  - `server_cert_sans_dns` / `_get_cert_requests` DNS lookup paths — no test with slow/missing DNS.
  - The config-changed → `_configure` → restart path — no test verifies a no-op config change skips restart.
  - `_on_stop` and `_on_remove` handlers have limited coverage.
- **No scenario test for invalid `routing_mode` with fresh construction**: `test_bad_routing_mode_config_and_recovery` passes only because the Harness reuses the charm instance across events.

## Docs

- **README**: clear setup instructions with microk8s example, config documentation, relation descriptions.
- **`docs/` directory**: comprehensive Sphinx docs (tutorial, how-to, reference, explanation) using Diátaxis structure.
- **Charmhub description**: brief but accurate, links to discourse docs.
- **Doc/reality mismatch**: the README example uses `juju deploy ./traefik-k8s_ubuntu-20.04-amd64.charm` with `--resource traefik-image=...`, but charmhub deployment doesn't require the resource flag — misleading for new users deploying from charmhub.
- **Terraform module**: `terraform/README.md` has clear usage instructions.
- **Manual test bundles**: `tests/manual/` contains 5 bundle YAML files for different TLS scenarios — useful as operator documentation.
- **Missing**: no inline `config.yaml` reference in docs showing all config options and defaults; `tls-cert`/`tls-key`/`tls-ca` options lack documentation of the expected PEM format, which may contribute to operators providing invalid data (see TLS-validation finding).

## Open questions

1. Does `cached_property` on `_get_loadbalancer_status` cause staleness in practice if the cloud provider reassigns the LB IP? Not tested — single cloud-provider environment.
2. Does `_stored.config_hash` survive charm upgrades cleanly from pre-hash revisions? If `None`, the first run does a full reconfigure, which is correct but wasteful — untested.
3. `_on_stop` clears workload version but does nothing else, and the LB service is only removed on `_on_remove` when `planned_units() == 0` — believed correct but untested.
4. Are there other unguarded `ModelError` paths in the ingress libraries beyond `wipe_ingress_data` and `publish_url`? Worth a full audit of relation-data writes in all three libraries.
5. Is `_provider_from_relation` defaulting to v1 for any not-yet-ready relation actually safe, or could a malformed v2 payload be misinterpreted by the v1 provider? Not verified — would need confirmation that v1/v2 data schemas are disjoint.
6. Do the synchronous DNS lookups meaningfully slow down deployment in environments with slow external DNS? Not reproducible in the fast-DNS test environment (unverified).
7. Should the `_update_config_if_changed` code path (only reachable from tracing handlers) be removed given it's effectively dead, or fixed and wired into `_on_change`?
