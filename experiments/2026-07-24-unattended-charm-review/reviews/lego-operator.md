# lego-operator

A machine charm implementing the provider side of the `tls-certificates` interface: it obtains signed certificates from an ACME server (Let's Encrypt or other) via DNS-01/HTTP-01 challenges, using the `lego` CLI embedded as a ctypes-loaded Go shared library (`pylego`/`lego.so`). It runs no persistent workload — `lego` is invoked per certificate request and exits.

Individual config errors are handled well: the charm reaches sensible `BlockedStatus` for most tested validation failures and recovers cleanly, and `secret-changed` correctly triggers reconfiguration on secret content changes. But a critical gap exists: **deleting the plugin secret while the charm is running produces no event and no status change** — the charm reports `active` indefinitely and will only fail, silently, at the next certificate request. Two further bugs (a stale `_plugin` cache, and unknown plugin names silently passing validation) compound the risk of misconfiguration going unnoticed. The local source is also five weeks behind the published charm, missing a config option (`disable-cname-support`) that is live in production.

**What a maintainer should do first**: fix the secret-deletion status gap (check secret existence directly in `collect_unit_status` rather than relying on events), make `_plugin` a live property instead of an `__init__`-time cache, and resync the local source with the published charm before doing anything else.

| | |
|---|---|
| Repo | canonical/lego-operator @ `ae566dc` (2026-07-10) |
| Charms | lego (machine) |
| Substrate | machine (LXD) |
| Deployed | yes — `concierge-lxd-4`, `4/edge` rev 516 (published 2026-08-17) |
| Reviewed | 2026-09-01 |

## What it does

The lego charm is a TLS certificate provider. It takes CSR requests from related requirer charms via the `tls-certificates` interface, runs the `lego` CLI (via the embedded `pylego` Go library) against an ACME server using DNS-01 or HTTP-01 challenges, and returns signed certificates. It also distributes CA certificates via the `certificate_transfer` interface and optionally integrates with Traefik (HTTP-01 validation) and Loki (logging).

## TLS certificates integration (live test with vault)

Vault (rev 745, `2.0/edge`) was related to lego via:

```bash
juju relate lego:certificates vault:tls-certificates-access
```

Observed lifecycle:
1. `certificates-relation-created` → `certificates-relation-joined` → `certificates-relation-changed`
2. Vault sends a CSR (PEM-encoded, machine IP as CN)
3. Lego receives it via `TLSCertificatesProvidesV4`, calls `run_lego_command()`
4. Lego returns a certificate or error via `set_relation_error`/`set_relation_certificate`
5. Vault receives the response

With test email `test@example.com`, the exchange completed but returned an ACME error:

```json
{"code": 999, "name": "OTHER", "message": "contact email has forbidden domain \"example.com\""}
```

This is correct LEGO/Let's Encrypt behaviour (`example.com` is a reserved domain), correctly translated to `CertificateError` and written to relation data. Vault itself stayed blocked (waiting for an auto-unseal provider, unrelated to lego); lego correctly showed `0/1 certificate requests are fulfilled. please monitor logs for any errors`.

On relation removal (`juju remove-relation`):
- `certificates-relation-departed` → `certificates-relation-broken` both fired on lego
- The library's `_on_relation_broken` cleaned up certificate secrets (private key + cert) for the relation
- Status correctly updated to `0/0 certificate requests are fulfilled` after the broken hook completed

## Deployment log

Deployed from charmhub (`4/edge`, rev 516) onto `concierge-lxd-4`, Ubuntu 24.04:

```bash
juju add-model rv-lego --controller concierge-lxd-4
juju deploy lego --channel 4/edge
```

Machine provisioned in ~1 minute; charm install took ~3 minutes from machine creation to first status. Initial status was `blocked: email address was not provided` — correct.

Status timeline:
```
04:05:38 unit started
04:05:44 install hook done
04:05:44 leader-elected hook done
04:05:45 config-changed: blocked (email)
04:05:46 start hook done
04:07:29 config-changed: blocked (http01, no ingress)
04:07:48 config-changed: blocked (no plugin secret)
04:07:53 config-changed: blocked (secret not granted)
04:08:31 config-changed: active (secret granted)
```

Lifecycle: blocked (no email) → blocked (http plugin, no ingress) → blocked (namecheap, no secret) → blocked (secret not granted) → active (secret granted with valid config).

Additional observations:
- `self-signed-certificates` was also deployed and related via `receive-ca-cert`/`send-ca-cert` (`certificate_transfer`).
- With the secret not granted, the charm logged `WARNING unable to access the secret: ERROR "lego/0" is not allowed to read this secret` and handled it gracefully.
- After granting the secret and triggering a config change, the charm went straight to `active`; no intermediate maintenance/error states in this path.
- `juju config` fires exactly two `config-changed` hooks (one from `leader-elected`, one from the direct event) — normal Juju machine-charm behaviour, handled correctly.
- **`secret-changed` fires on content changes**: changing the plugin secret content from valid namecheap keys to `{"wrong-key": "..."}` fired `secret-changed` within ~5 seconds; charm went `blocked: namecheap-api-key and namecheap-api-user must be set`. Restoring correct keys recovered to `active`.
- **Unit restart**: `sudo systemctl restart jujud-machine-0` — unit restarted cleanly, `start` and `config-changed`×2 fired, recovered to `active` in ~15s. ACME account key persisted (Juju secret); CA bundle file rebuilt on next `_configure`.
- **Scale-up blocked by environment**: `juju add-unit lego` created lego/2 but its machine stayed `pending` (LXD provisioning stalled). Not a charm defect — the LXD host has 31GB RAM / 24 cores available.
- **`juju refresh lego`**: already up to date at rev 516; no newer revision available to test against.
- **`pylego` packaging**: `lego` is not a standalone binary — it's compiled into `lego.so` inside the `pylego` package (v0.1.45), loaded via `ctypes.cdll.LoadLibrary` from `/var/lib/juju/agents/unit-lego-0/charm/venv/lib/python3.12/site-packages/pylego/lego.so`. No separate install step for it in the install hook.
- **`disable-cname-support`**: present in the deployed `config.yaml` (`/var/lib/juju/agents/unit-lego-0/charm/config.yaml`), boolean, default `false`, "Disable CNAME following during the DNS-01 pre-check." Not present in the local `charmcraft.yaml`. Handled in deployed `charm.py` via a `_disable_cname_support_env` property, used as `env = base_env | http01_env | self._disable_cname_support_env`; the local source has neither the property nor this env merge.

## Observed behaviour

- **Install time**: ~3 minutes from machine creation to first blocked status.
- **Config change latency**: status reflects change within seconds of hook completion.
- **Hook count**: exactly one `config-changed` per direct `juju config` call plus one from `leader-elected` — no unexpected duplicates.
- **Status transitions**: correctly blocked for each validation failure tested (missing email, missing plugin, missing secret, missing ingress for http-01, invalid email, invalid server, invalid DNS nameserver port, EAB partial secret).
- **Secret access failure (grant revoked)**: handled gracefully with a WARNING log; charm goes blocked via `collect_unit_status`.
- **Secret deletion while running**: charm stays `active` — no event fires, `collect_unit_status` only checks that the config value is set, not that the secret exists. Confirmed live: `juju remove-secret secret:9kvnr39qm0s1k6q6dc00` while charm was running.
- **Unknown plugin (typo `rout53`)**: charm stays `active`, only logs `WARNING this plugin's config options are not validated by the charm.`. Confirmed live: `juju config lego plugin=rout53` → `active` with two WARNING lines in debug-log.
- **No actions defined** beyond ops defaults.
- **No persistent workload**: the machine runs only the Juju unit agent; no systemd unit for the charm workload itself.

### Failure injection results

| Scenario | Observed | Traceback? | Recovery? |
|---|---|---|---|
| `plugin=rout53` (typo) | `active` (WARNING logged) | No | Yes — `juju config lego plugin=namecheap` |
| `dns-nameservers=8.8.8.8:notaport` | `blocked: Invalid port format in dns-nameserver: 8.8.8.8:notaport` | No | Yes — valid nameserver string |
| `server=not-a-url` | `blocked: invalid ACME server` | No | Yes — valid URL |
| EAB secret with only `eab-kid` | `blocked: eab-secret-id secret must contain both 'eab-kid' and 'eab-hmac'` | No | Yes — `juju config --reset eab-secret-id`, then non-empty value |
| `juju remove-secret` of plugin secret while running | **`active` — no event fired, no status change** | No | Requires re-grant/new secret and a subsequent hook to re-evaluate |
| Secret content changed to wrong keys | **`secret-changed` fires → `blocked: namecheap-api-key and namecheap-api-user must be set`** | No | Yes — `juju update-secret` with correct keys |
| Unit agent restart (`systemctl restart jujud-machine-0`) | Restarted, `start` hook fired, `config-changed`×2, recovered to `active` | No | Automatic |
| `juju add-unit lego` | lego/2 created, machine stuck `pending` (environment constraint) | N/A | N/A — environment issue, not a charm defect |
| `juju refresh` | Already at latest revision | N/A | N/A |
| `juju remove-application lego` | Not tested | N/A | N/A |

### Integration exercised

| Integration | Interface | Observed |
|---|---|---|
| `self-signed-certificates` → lego (CA transfer) | `certificate_transfer` | lego received CA cert via `receive-ca-cert`; stored in `/var/lib/acme-ca-certificates.pem`; relation-changed and relation-broken hooks fired cleanly |
| `vault` → lego (TLS certificates) | `tls-certificates` | Full CSR exchange via `vault:tls-certificates-access` → `lego:certificates`: `relation-created`→`joined`→`changed`, lego calls `run_lego_command()`, sets certificate/error on relation; `relation-departed`→`relation-broken` clean up correctly; status returns to `0/0` after removal |
| Ingress (HTTP-01) | `ingress` | Not exercised — machine substrate, no ingress provider available |
| Logging | `loki_push_api` | Declared optional; not related in this deployment |

## Findings

### Plugin secret deletion leaves charm `active` — no event, no status change

- **Severity**: critical
- **Kind**: bug
- **Where**: `src/charm.py` `__init__` (registers `secret_changed` but not `secret_remove`); `_on_collect_status` / `_validate_charm_config_options` (checks `_plugin_config`, which is fed by `_plugin_config` property catching `SecretNotFoundError`)
- **Evidence**: `juju remove-secret secret:9kvnr39qm0s1k6q6dc00` on the running charm produced `INFO ... scheduled removal of user secret "secret:9kvnr39qm0s1k6q6dc00"` in the Juju log, but no hook fired on the lego unit, and `juju status` showed `active` both before and after. `secret_remove` fires on the secret **owner**, not on a consumer whose secret was deleted, and no other event notifies a consumer of deletion. `_plugin_config` catches `SecretNotFoundError` and returns `{}`; the charm's checks would then correctly flag it as `"plugin configuration secret is not available"` — but only if `collect_unit_status` runs. Since no hook fires, `collect_unit_status` never re-evaluates, and the status set before deletion persists indefinitely.
- **Impact**: An operator who deletes the plugin secret (or otherwise loses charm access to it) while the charm is running gets no indication anything is wrong. `juju status` reports `active`. The next certificate request fails with an authentication error inside `lego`, surfacing only in logs and in relation data (`request_errors`) for the requirer — not in the charm's own status. In a production environment where lego is the sole TLS provider, this can cause hard-to-diagnose outages.
- **Fix**: In `_on_collect_status`, verify the secret directly with `self.model.get_secret(id=plugin_config_secret_id)` (not via `_plugin_config`, which swallows `SecretNotFoundError`) and catch `SecretNotFoundError`/`ModelError` to return `BlockedStatus`. This makes correctness independent of whether any hook happens to fire.
- **Linter rule**: "A charm reading secrets from config in `collect_unit_status` must check secret existence directly, not through a helper that silently returns a default on `SecretNotFoundError`" — not fully mechanical, but greppable for `except SecretNotFoundError: return {}` patterns feeding into status logic.

### `_plugin` config is cached at `__init__` time and never refreshed

- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py` `__init__` (`self._plugin = str(self.model.config.get("plugin", ""))`), read throughout via `self._plugin`/`self._is_http_plugin`
- **Evidence**: `self._plugin` is set once in `__init__` and never updated on config-changed. Confirmed live: `juju config lego plugin=rout53` (typo) leaves the charm `active` with only a WARNING logged, because plugin-name validation and ingress logic still act on stale state consistent with the previous good config in some paths.
- **Impact**: Changes to the `plugin` config option after startup are not reliably picked up by logic that depends on `self._plugin` being current, risking use of the wrong plugin at certificate-request time.
- **Fix**: Make `_plugin` a `@property` that reads live from `self.model.config`.
- **Linter rule**: "Config-dependent attributes cached in `__init__` without refresh on config-changed" — not mechanically checkable with current tooling.

### Stale `_plugin` cache also prevents ingress from ever being (re-)instantiated after startup

- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py` `__init__` (`self._ingress = None; if self._is_http_plugin: self._ingress = IngressPerAppRequirer(self)`)
- **Evidence**: `_ingress` is set once at startup based on the plugin value at that time. If an operator switches to `plugin=http` later and adds an ingress relation, `self._is_http_plugin` (derived from the stale `_plugin`) may still read false, so `_ingress` is never created and ingress requirements are never provided.
- **Impact**: HTTP-01 plugin switching after startup can deadlock without a unit restart.
- **Fix**: Same as the `_plugin` cache fix — making `_plugin` a live property resolves both issues.
- **Linter rule**: "Config-dependent attribute reads that affect object construction must not be cached in `__init__`" — not mechanically checkable.

### Source/repo is behind published charm by ~5 weeks

- **Severity**: high
- **Kind**: bug
- **Where**: local source `src/charm.py` at `ae566dc` (2026-07-10) vs deployed charm rev 516 (published 2026-08-17)
- **Evidence**: Local `charm.py` is 819 lines; the deployed charm's is 826 lines, with an extra `_disable_cname_support_env` property and a differing env-merge line (`env = base_env | http01_env | self._disable_cname_support_env` deployed vs `env = base_env | http01_env` locally). `disable-cname-support` appears in the deployed `config.yaml` but not the local `charmcraft.yaml`.
- **Impact**: Anyone reviewing or contributing to the local source is looking at code materially different from what's in production.
- **Fix**: Resync local source with the published charm; investigate how the release diverged from the visible git history.
- **Linter rule**: not mechanically checkable.

### `disable-cname-support` declared in published charm but absent from local `charmcraft.yaml`

- **Severity**: high
- **Kind**: bug
- **Where**: deployed `config.yaml` vs local `charmcraft.yaml`
- **Evidence**: The deployed charm's `config.yaml` contains a `disable-cname-support` boolean option, handled by `_disable_cname_support_env` in the deployed `charm.py`. Neither the option nor the handler exists in local source.
- **Impact**: Anyone reading the local `charmcraft.yaml` would not know this option exists; if it were manually added to config without the corresponding code, it would silently do nothing.
- **Fix**: Add `disable-cname-support` to `charmcraft.yaml` and port the handler into `src/charm.py`.
- **Linter rule**: `charmcraft analyse` would flag a declared-but-unhandled option, but it can't catch a gap between two different snapshots (published vs local).

### `--reset` for string config options sets empty string, which blocks the charm

- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py` `_validate_dns_nameservers` (`if not nameservers.strip(): return "dns-nameservers cannot be empty if provided"`); same issue noted for `eab-secret-id`
- **Evidence**: `juju config --reset dns-nameservers` sets the value to `""` (not `None`). `_validate_dns_nameservers`'s `if not nameservers.strip()` check fires on `""`, blocking the charm with `dns-nameservers cannot be empty if provided`. Confirmed live; the same `--reset` behaviour was also observed not to clear the block for `eab-secret-id`. Recovery required setting an explicit non-empty value (e.g. `juju config lego dns-nameservers="8.8.8.8"`).
- **Impact**: `--reset` is the canonical way to unset a Juju config option, but here it produces a `BlockedStatus` instead of restoring default behaviour, and the resulting error message doesn't hint at the actual fix (setting a value), since the operator just tried the opposite.
- **Fix**: Treat `None`/`""` as equivalent to "unset" in `_validate_dns_nameservers` (and any similarly-affected validators), e.g. `if nameservers is None or not nameservers.strip(): return ""`.
- **Linter rule**: "String-type config validators must treat empty string as equivalent to unset unless empty is a valid value" — mechanically checkable for validators using `if not x.strip()` without a prior `is None` guard.

### Unknown plugin silently passes validation — confirmed live

- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py` `_validate_plugin_config_options` (`except AttributeError: logger.warning(...); return ""`)
- **Evidence**: `getattr(plugin_configs, self._plugin)` on an unknown plugin name raises `AttributeError`, which is caught and treated as valid (`return ""`). Confirmed live: `juju config lego plugin=rout53` → `active`, debug-log shows `WARNING this plugin's config options are not validated by the charm.` (twice, once per `config-changed` hook).
- **Impact**: Typos in plugin names are silently accepted; LEGO only rejects the plugin at certificate-request time.
- **Fix**: Replace `return ""` with an explicit error, e.g. `return f"plugin '{self._plugin}' is not a supported plugin (supported: http, httpreq, namecheap, route53)"`.
- **Linter rule**: "Plugin name must be validated against a known allowlist before use" — mechanically checkable by flagging `return ""` inside an `AttributeError` handler in plugin-validation code.

### Error log line logs raw CSR, leaking domain names and public keys

- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py` `_generate_signed_certificate` (`logger.error("Error occurred while obtaining certificate for request %s, setting relation data.", csr.raw)`)
- **Evidence**: `csr.raw` is the raw PEM-encoded CSR, which contains the public key, common name, and all requested SANs. Logged at ERROR level.
- **Impact**: Domain names and key material end up in log aggregation at high visibility — a privacy concern.
- **Fix**: Log `csr.common_name` or a hash of the CSR instead of the raw bytes.
- **Linter rule**: "Do not log raw bytes fields from certificate objects" — mechanically checkable via a custom rule or grep for `csr.raw` in logger calls.

### Non-leader units silently do nothing on certificate-related hooks

- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py` `_configure` (`if not self.unit.is_leader(): logger.error(...); return`)
- **Evidence**: The non-leader early return in `_configure` only logs an error; it sets no status. If a non-leader unit receives a `certificates` relation-changed event, it stays in whatever status it currently has.
- **Impact**: In an HA scenario where the leader changes, a new non-leader that happens to be `active` will silently ignore certificate traffic, leaving requirers without certificates and no visible signal in `juju status`.
- **Fix**: Set `self.unit.status = BlockedStatus(...)` before returning on non-leader in `_configure`, mirroring `_on_collect_status`.
- **Linter rule**: "Hook handler that returns early on non-leader must set a BlockedStatus" — checkable with a custom rule.

### `_configure` returns early on config validation errors without setting status

- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py` `_configure` (`if err := self._validate_charm_config_options(): logger.error(...); return` and the same pattern for `_validate_plugin_config_options`)
- **Evidence**: Both early returns log the error but set no status; status is only updated via `collect_unit_status` at hook end.
- **Impact**: If `_configure` runs mid-hook (e.g. during `relation-changed`) and hits a validation error, the unit's prior status (possibly `active`) persists until the next `collect_unit_status` call, misrepresenting the charm's actual state during that window.
- **Fix**: Set `self.unit.status = BlockedStatus(err)` before each early return in `_configure`, matching `_on_collect_status`.
- **Linter rule**: "Hook handler that calls a validator and returns on error must set BlockedStatus before returning" — checkable with a custom rule.

### `maintenance_status` context manager swallows `InvalidStatusError` silently

- **Severity**: low
- **Kind**: bug
- **Where**: `src/charm.py` `maintenance_status` (`except InvalidStatusError: pass`)
- **Evidence**:
```python
@contextmanager
def maintenance_status(self, message: str):
    previous_status = self.unit.status
    self.unit.status = MaintenanceStatus(message)
    try:
        yield
    finally:
        try:
            self.unit.status = previous_status
        except InvalidStatusError:
            pass
```
- **Impact**: If status restoration fails, there is no trace of it — the charm could end up in an unexpected status with no diagnostic signal.
- **Fix**: Replace `pass` with a `logger.warning(...)` call.
- **Linter rule**: "Exception handlers must not use bare `pass`" — not fully caught by standard ruff rules.

### No explicit handler for `certificates-relation-departed`

- **Severity**: low
- **Kind**: bug
- **Where**: `src/charm.py` `__init__` (only `certificates-relation-changed` is explicitly observed for `CERTIFICATES_RELATION_NAME`)
- **Evidence**: `certificates-relation-departed`/`certificates-relation-broken` are not explicitly registered on the charm; cleanup relies on the `TLSCertificatesProvidesV4` library's own `_on_relation_broken` handler and its subsequent `relation_changed` emission to trigger `_configure`. This was observed to work correctly in the vault integration test, but it depends on library internals.
- **Impact**: The charm's cleanup path is indirect; a future change to the library's event wiring could silently break it.
- **Fix**: Register `self.on[CERTIFICATES_RELATION_NAME].relation_departed` → `_configure` explicitly.
- **Linter rule**: "If a charm uses relation data in `_configure`, it should register `relation_departed` for that relation" — mechanically checkable by flagging relations with `relation_changed` registered but not `relation_departed`.

### `_get_dns_nameservers` double-negative is confusing

- **Severity**: low
- **Kind**: lint
- **Where**: `src/charm.py` (`if not self._validate_dns_nameservers() == "" or not isinstance(nameservers, str): return None`)
- **Evidence**: Works correctly but is unidiomatic; `_validate_dns_nameservers()` already returns `""` on success (falsy) and a non-empty string on error (truthy).
- **Fix**: `if self._validate_dns_nameservers() or not isinstance(nameservers, str): return None`
- **Linter rule**: not mechanically checkable.

### `plugin_configs.py` has copy-paste docstring errors

- **Severity**: nit
- **Kind**: lint
- **Where**: `src/plugin_configs.py` — `route53.validate` and `namecheap.validate` docstrings
- **Evidence**: Both docstrings read `"Validate httpreq options."` instead of naming their own plugin. `httpreq.validate`'s docstring is correct.
- **Fix**: Correct the docstrings.
- **Linter rule**: not mechanically checkable.

### `httpreq.validate` error message references the wrong endpoint type

- **Severity**: nit
- **Kind**: lint
- **Where**: `src/plugin_configs.py` — `httpreq` validator
- **Evidence**: The error message reads `"HTTREQ_ENDPOINT must point to a valid DNS server."` — a typo (`HTTREQ_ENDPOINT` vs `HTTPREQ_ENDPOINT`) and a misleading description (`HTTPREQ_ENDPOINT` is an HTTP(S) URL, not a DNS server); compare `route53.validate`'s correct "DNS nameserver" wording.
- **Fix**: `return "HTTPREQ_ENDPOINT must point to a valid HTTP or HTTPS URL."`
- **Linter rule**: not mechanically checkable.

## Worth copying

- **Good status precedence in `_on_collect_status`**: each blocked condition has an explicit `return`, so exactly one status is always set — no fall-through bugs.
- **`maintenance_status` context manager**: temporarily setting `MaintenanceStatus` during long-running ACME operations gives useful `juju status` visibility; try/finally correctly restores prior status (aside from the `InvalidStatusError` swallow noted above). Observed working correctly during deployment.
- **`# noqa: C901` on `_validate_charm_config_options`**: an honest, documented suppression rather than a silent one.
- **Comprehensive error mapping**: `_map_lego_error_to_certificate_error` maps LEGO errors to retry-semantic-aware `CertificateRequestErrorCode` values, with a clear docstring on which errors are transient; well covered by tests (rate limit, DNS, unauthorized, IP rejection, wildcard, network, other).
- **Expiry alerting with structured JSON logs**: `_log_expiring_certificates` emits machine-parseable JSON that Loki/Prometheus rules can consume without custom parsing; the paired `lego_certificate_expiring_critical.rule` is a clean complement.
- **No `StoredState`**: all state derives from Juju model data (config, relations, secrets), avoiding the most common ops-framework staleness bugs.
- **No `defer()`**: event-driven reconciliation via `_configure` on every relevant event — the correct modern pattern.
- **`loki_endpoints` property + `@log_charm`**: clean separation feeding `LogForwarder` with zero boilerplate in the charm body.
- **`receive_ca_certificates.on.certificates_removed` → `_configure`**: the CA bundle is correctly rebuilt when certificates are removed from the `receive-ca-cert` relation.

## Common-practice notes

- Correctly uses `collect_unit_status` (`CollectStatusEvent`) rather than `update_status` for status reporting.
- `ops` usage is appropriate throughout: `CharmBase`, `CollectStatusEvent`, `UpdateStatusEvent`, `BlockedStatus`, `ActiveStatus`, `MaintenanceStatus`, `InvalidStatusError`, `Secret`, `SecretNotFoundError`, `ModelError`.
- Charm libraries are pulled via `charmcraft.yaml`/PyPI, not vendored — correct for a 2024+ charm; no `lib/charms/` directory.
- `terraform/MODULE_SPECS.md` is 0 bytes; the actual `.tf` files (`main.tf`, `outputs.tf`, `variables.tf`, `versions.tf`) exist.
- No `upgrade_charm` handler: acceptable, since the ACME account key lives in a Juju secret, config lives in model state, and the CA bundle is rebuilt by `_configure` on the next hook.
- `IngressPerAppRequirer` uses `StoredState` internally to track `current_url`, which is appropriate for a library; the charm itself avoids `StoredState`.
- `http` and `http-01` are both accepted as HTTP-01 plugin names by `_is_http_plugin`; the LEGO binary accepts both.
- Double `config-changed` per `juju config` call (once from `leader-elected`, once direct) is normal Juju machine-charm behaviour and handled correctly.
- `_email_is_valid` uses a permissive regex (`r"[^@]+@[^@]+\.[^@]+"`) by design, since LEGO validates the email itself — reasonable.
- CI runs integration tests on microk8s with Juju 3/stable; this review's deployment was on machine substrate with Juju 4.x. The charm is machine-only (`type: "charm"`), no Kubernetes support declared.

## Tests

53 unit tests using `scenario` and `pytest`, all passing. `ruff`, `codespell`, and `pyright` report zero issues. 77 deprecation warnings from `charmlibs.interfaces.tls_certificates` (deprecated `generate_*` fixtures used in tests).

| Area | Coverage | Notes |
|---|---|---|
| `src/charm.py` | 84–85% | Secret-handling error paths and `_log_expiring_certificates` untested |
| `src/plugin_configs.py` | 95% | Well covered |

**Verified untested paths** (from `coverage report --show-missing`):
- `_log_expiring_certificates`: no test exercises the expiry-ratio alerting path or its JSON payload / the Loki alert rule.
- `_get_ca_certs_from_config` / `_configure_acme_ca_certificates_bundle` with actual relation certificates: no scenario test for the combine-and-write path with a live `CertificateTransferRequires`.
- `_validate_dns_nameservers` error paths ("invalid port", "empty entry") in `collect_unit_status`: not unit-tested, though confirmed working live (`dns-nameservers=8.8.8.8:notaport` → blocked).
- `SecretNotFoundError`/`ModelError` paths in `_plugin_config`: not forced by any test — the live secret-deletion test confirmed the resulting behaviour (charm stays active).
- `_is_ip_rejection`: only exercised indirectly via `_map_lego_error_to_certificate_error`.
- `maintenance_status`'s `InvalidStatusError` catch path: not exercised.
- `_write_acme_ca_bundle_file` with an empty cert list (deletion path): no scenario test.
- `_validate_eab_config` partial-key error path: tested in `collect_unit_status` but not in `_configure`.
- `secret-changed` with a revoked grant: not unit-tested (confirmed working live).

**Integration tests**: `tests/integration/test_charm.py` is a smoke test only — deploy, wait for blocked, set secret, wait for active, assert `workload_status == "active"`. No assertions on relation data, certificate content, error codes, or the `receive-ca-cert` integration. The `certificates` relation — the charm's primary interface — is never exercised in integration tests. In this review environment, `tox -e integration` failed ("The path specified for the charm under test does not exist: None"), requiring a Juju controller (jubilant) not available here; the test suite targets `https://acme-staging-v02.api.letsencrypt.org/directory` (staging).

**Unit tests require `charmcraft fetch-libs`**: running `tox -e unit` on a fresh checkout fails with `ModuleNotFoundError: No module named 'charms'`. CI calls `charmcraft fetch-libs` first; `tox.ini` has no equivalent pre-command.

## Docs

- **README.md**: ~390 bytes — one-line description plus links to CONTRIBUTING.md and the Juju SDK docs. No usage examples, config documentation, or relation examples; an operator cannot succeed from this README alone.
- **CONTRIBUTING.md**: clear and correct development setup (uv, tox, charmcraft).
- **charmcraft.yaml description**: detailed and accurate; config option descriptions are well-written.
- **Charmhub description**: matches `charmcraft.yaml`; accurate.
- **Terraform module**: `.tf` files exist and are correct; `terraform/MODULE_SPECS.md` is empty (0 bytes).
- **SECURITY.md**: present and appropriate.

## Open questions

1. **Why is the local source behind the published charm?** Local HEAD `ae566dc` (2026-07-10) predates the published rev 516 (2026-08-17) by about five weeks, and the published charm has `_disable_cname_support_env` / `disable-cname-support` that the local source lacks entirely. Either the release was built from a branch not reflected in the shown git history, or there's a gap in that history — needs reconciling with the maintainers.
2. **Does Juju fire any consumer-facing event when a consumer secret is deleted?** Confirmed no — `secret_changed` does not fire for deletion, and `secret_remove` fires on the owner, not the consumer. This is the root cause of the critical finding above; the `scenario` framework also has no `secret_removed` event type, so this isn't currently a testable path in unit tests either.
3. **What happens when a certificate request arrives after the plugin secret is gone?** Confirmed by code + log inspection: `_configure` → `_generate_signed_certificate` → `run_lego_command()` fails (no credentials) → `LEGOError` caught → error set on the relation via `set_relation_error`. No status change occurs; the charm stays `active` and the failure is visible only in logs and in the requirer's relation data.
4. **Does `secret-changed` fire for secret content changes?** Confirmed yes, live: updating the plugin secret's content (correct → wrong keys, and back) fired `secret-changed` each time within ~5 seconds, correctly toggling `blocked`/`active`. The distinction is sharp: **content change → event fires**; **deletion → no event**.
</content>
