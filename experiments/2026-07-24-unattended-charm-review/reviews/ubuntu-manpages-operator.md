# ubuntu-manpages

A well-architected K8s charm fronting a substantial, well-tested Go application for manpages.ubuntu.com. The charm's Python glue (~120 lines) is mostly clean but has one real correctness bug — an uncaught `ValueError` from invalid config drives the unit into `error` state instead of `BlockedStatus` — plus a config-sanitation gap that silently drops bad release tokens, three unused Python dependencies, a storage definition with no minimum size, and a handful of smaller hygiene issues. Ingress re-integration after a relation revoke also showed a long delay before `MANPAGES_SITE` updates, likely caused by an outdated ingress library. The Go workload itself is solid: well-tested, well-structured, and behaved correctly under scale, refresh, process kills, and teardown.

A maintainer picking this up should first fix the uncaught `ValueError` (Finding 1) since it produces the worst operator experience for a routine mistake, then look at the ingress re-integration delay (Finding 4) and the missing storage minimum (Finding 5), which is the type of gap that turns into a production incident.

| | |
|---|---|
| Repo | `canonical/ubuntu-manpages-operator` @ `d633458` (2026-07-21) |
| Charms | ubuntu-manpages |
| Substrate | k8s |
| Deployed | yes — concierge-k8s-4 (Juju 4.0.5) and concierge-k8s-3 (Juju 3.6.25), latest/edge rev 65, then refreshed to latest/stable rev 62 |
| Reviewed | 2026-08-10 |

## What it does

The charm deploys a Go web application that downloads Ubuntu `.deb` packages, extracts manpages, converts them to HTML via `mandoc`, and serves them with search, browse, and sitemap capabilities. Two Pebble services run in the workload container: `/usr/bin/server` (HTTP on port 8080) and `/usr/bin/ingest` (package ingestion). Two Juju storage mounts (`manpages`, `manpages-gz`) hold the generated HTML tree and gzipped variants.

Config exposes one option, `releases` (comma-separated Ubuntu codenames). An `update-manpages` action re-triggers ingestion. An `ingress` relation integrates with traefik-k8s. Two Pebble checks (`up` TCP on 8080, `ready` HTTP on localhost:9090) monitor workload health.

## Deployment log

### Deploy: concierge-k8s-4, latest/edge rev 65

```bash
$ juju add-model rv-manpages
$ juju deploy ubuntu-manpages --channel latest/edge --config releases="noble"
```

- Container image pulled in ~25s. Pod started with `PodInitializing` then `maintenance: Updating manpages`.
- Initial config-changed hook fired before pebble-ready (container not yet running), causing a transient `BlockedStatus` ("Failed to connect to workload container"). Cleared once pebble-ready fired.
- After pebble-ready: Pebble layer added, both services started, server serving HTTP 200 on port 8080 within ~10s.
- Both Pebble checks (`up` TCP, `ready` HTTP) healthy after 8 consecutive successes.

### Deploy: concierge-k8s-3 (Juju 3.6.25), latest/edge rev 65

```bash
$ juju add-model rv-manpages-3
$ juju deploy ubuntu-manpages --channel latest/edge --config releases="noble"
```

Identical behaviour to Juju 4. No Juju-version-specific discrepancies observed.

### Config change: `releases=""` (empty)

```bash
$ juju config ubuntu-manpages releases=""
```

Unit went to **error** state on both Juju 4 and Juju 3.6: `hook failed: "config-changed"`. The `ValueError` raised by `pebble_layer()` in `src/manpages.py:38` is not caught by `_replan_workload()`, which only catches Pebble connection errors (`ConnectionError`, `ProtocolError`, `APIError`). Traceback from debug-log:

```
  File "src/manpages.py", line 38, in pebble_layer
    raise ValueError("failed to build manpages config: invalid releases specified")
ValueError: failed to build manpages config: invalid releases specified
```

### Config change: `releases="12345,!!!"` (no alphabetic match)

Same result: **error** state with the uncaught `ValueError`. Confirmed on both Juju versions.

### Config change: `releases="noble,🔧,😀"` (valid token + garbage)

No error. The charm silently accepted the config: only `noble` was extracted by `RELEASES_PATTERN = re.compile(r"([a-z]+)(?:[,][ ]*)*")`, but the raw config string `noble,🔧,😀` was still passed as-is into `MANPAGES_RELEASES` in the Pebble layer. The Go application's `splitCSV` also silently discards the emoji tokens. No warning at any level.

### Config change: `releases="noble"` (recovery)

Recovered automatically once config-changed re-fired. Charm correctly purged old release directories on disk (verified via `kubectl exec`).

### Ingress integration

```bash
$ juju deploy traefik-k8s --trust --config routing_mode=subdomain --config external_hostname=manpages.test
$ juju integrate ubuntu-manpages traefik-k8s
```

- Integration succeeded. `MANPAGES_SITE` changed from `http://10.1.0.211:8080` to `http://rv-manpages-ubuntu-manpages.manpages.test/`.
- `curl -H "Host: rv-manpages-ubuntu-manpages.manpages.test" http://<traefik-ip>/` returned HTTP 200 with the landing page.
- Debug-log showed a schema validation warning from traefik's ingress library about `strip-prefix` being sent as a string instead of boolean — didn't block the integration. Likely an ingress-library version mismatch between the two charms.
- On relation removal, `MANPAGES_SITE` correctly reverted to `http://10.1.0.211:8080`.
- **Re-adding the relation after revoke**: `ingress-relation-created`, `-joined`, and `-changed` all fired within 1 second, but `ingress.ready` — the only event the charm observes to trigger `_on_config_changed` and the Pebble replan — had **not fired after 60 seconds**. The Pebble plan still showed `MANPAGES_SITE=http://10.1.0.20:8080`. An operator who removes and re-adds ingress sees no URL update for an extended period. The ingress library (LIBPATCH=19) may be behind the traefik-k8s charm's version (rev 377). See Finding 4.

### Scale up and down

```bash
$ juju add-unit ubuntu-manpages   # 1 → 3
$ juju scale-application ubuntu-manpages 1   # 3 → 1
```

Both clean. All 3 units independently reached `maintenance: Updating manpages` with no inter-unit coupling issues. Scale-down terminated units cleanly.

### `juju refresh` (edge rev 65 → stable rev 62)

```bash
$ juju refresh ubuntu-manpages --channel latest/stable
```

Downgrade succeeded. Pod rescheduled (new IP); hook sequence upgrade-charm → config-changed → start → pebble-ready ran cleanly. Total time from stop to pebble-ready: ~36s. Post-refresh status: `maintenance: Updating manpages`, identical to initial deploy.

### `update-manpages` action

```bash
$ juju run ubuntu-manpages/0 update-manpages
```

Ran successfully on both Juju versions, completing in ~3 seconds (enqueued 04:28:37, completed 04:28:40). The action handler is bound to `_on_config_changed`, which triggers a full replan (`add_layer` + `replan` + ingest restart + purge) rather than just restarting ingest. `replan()` also restarts the `manpages` server unnecessarily, since the layer content hadn't changed. See Finding 8.

### Kill workload process

- **Kill server (`SIGTERM`)**: Pebble restarted the server within seconds. Status unchanged.
- **Kill ingest (`SIGKILL`)**: Pebble restarted ingest. `on-success: ignore` correctly means the service only stays dead after a *successful* exit, not a crash.

### Restart unit (via refresh)

Pod recreated. Hook sequence stop → pod terminated → new pod → upgrade-charm → config-changed → start → pebble-ready. Status progressed `waiting` → `maintenance: Updating manpages`. No errors.

### Admin health endpoint

`http://localhost:9090/_/healthz` returns `{"status":"ok"}` (confirmed via Pebble check). Binds only to `127.0.0.1`, not externally exposed — correct posture. Includes a disk-space guard (`pipeline.CheckDiskSpace`, 100 MiB free / 1000 free inodes required).

### Resource usage

`kubectl top pod`: 88m CPU, 140Mi memory during active ingestion of a single release (noble) — well below any practical limit.

### Ingest progress and filesystem state

After ~5 minutes of ingesting `noble`, the workload had downloaded 17 MB into `/app/www/manpages/noble/`, with man sections (`man1`, `man3`, `man5`, ...) and translations (`ca`, `cs`, `de`, `es`, `fr`, ...) populating. The failure log `/app/www/noble-failures.log` was present at 0 bytes — created eagerly so operators can `tail` it during processing. The `ingest` service was still `active` at observation time.

### Application removal and teardown

```bash
$ juju remove-application ubuntu-manpages --no-prompt
```

Teardown clean: pod and PVCs destroyed within ~30 seconds, no errors in debug-log, storage (`manpages`, `manpages-gz`) removed with the application — no orphaned volumes.

## Observed behaviour

- **Config validation gap**: `RELEASES_PATTERN` in `src/manpages.py:20` silently strips non-alphabetic tokens. A typo like `focal` for `fossa` matches `[a-z]+` and is passed through with no error, wasting time in the Go app fetching packages that don't exist.
- **No `BlockedStatus` for invalid releases**: the uncaught `ValueError` (Finding 1) is the single most user-visible bug.
- **Ingress revoke works correctly**: `MANPAGES_SITE` reverts to the unit-IP URL within seconds of relation removal.
- **Config-changed-before-pebble-ready race is self-healing**: initial config-changed fails with `BlockedStatus`, then pebble-ready re-triggers config-changed and recovers. Visible for ~25s.
- **Purge of old releases works correctly**: confirmed on disk via `kubectl exec` after narrowing the `releases` config.
- **Server serves the landing page immediately**, with no ingestion data required for homepage, browse, or search.
- **File ownership**: everything under `/app/www/` is `root:root` with standard permissions (`drwxr-xr-x` / `-rw-r--r--`). No concerns.
- **Ingress re-integration delay**: `MANPAGES_SITE` reverts correctly on revoke but does not update to the ingress URL after re-integration (`ingress.ready` did not fire within 60s). See Finding 4.
- **Server restart on action**: `update-manpages` briefly interrupts the server because `_replan_workload` calls `container.replan()`, which restarts all services with a changed plan, including `manpages`. See Finding 8.
- **Eager failure-log creation**: pipeline creates `{release}-failures.log` (0 bytes) before processing starts, for `tail -f` during ingestion.

## Findings

### 1. Uncaught `ValueError` on invalid releases config causes hook error instead of blocked status
- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:58` (catch clause), `src/manpages.py:38` (raise site)
- **Evidence**:
  ```python
  # charm.py — only catches ConnectionError, ProtocolError, APIError
  except (ConnectionError, ProtocolError, APIError) as e:
      ...
  ```
  ```python
  # manpages.py:37-38 — ValueError not among caught types
  releases_list = RELEASES_PATTERN.findall(releases)
  if not releases_list:
      raise ValueError("failed to build manpages config: invalid releases specified")
  ```
  Confirmed on both Juju 4 and Juju 3.6: `juju config ubuntu-manpages releases=""` and `releases="12345,!!!"` both drive the unit into **error** state with a stack trace.
- **Impact**: A routine config mistake produces a hard hook error requiring manual recovery, instead of a clear `BlockedStatus` message. There is no auto-retry.
- **Fix**: Catch `ValueError` in `_replan_workload()` and convert to `BlockedStatus`:
  ```python
  except ValueError as e:
      self.unit.status = ops.BlockedStatus(str(e))
      return
  ```
- **Linter rule**: "`raise ValueError` in a method invoked from a hook handler without a matching `except ValueError` in the caller" — narrowly checkable via cross-function exception-type analysis.

### 2. Non-alphabetic release tokens silently discarded with no operator feedback
- **Severity**: medium
- **Kind**: ux / bug
- **Where**: `src/manpages.py:20` (`RELEASES_PATTERN`), `src/manpages.py:37-38`
- **Evidence**: `releases="noble,🔧,😀"` was accepted; only `noble` was extracted, and the raw string `"noble,\U0001F527,\U0001F600"` was still passed through to `MANPAGES_RELEASES` in the Pebble layer. No warning logged.
- **Impact**: Typos in codenames (`focal` for `fossa`, `jam` for `jammy`) are silently dropped rather than flagged; the Go app will eventually fail or time out fetching a nonexistent release, with no upfront feedback to the operator.
- **Fix**: Compare extracted-token count to the raw `releases.split(",")` count and warn about discarded tokens, or validate tokens against a known codename set / the Launchpad API before accepting.
- **Linter rule**: not mechanically checkable.

### 3. Unused Python dependencies bloat the charm
- **Severity**: medium
- **Kind**: lint / performance
- **Where**: `pyproject.toml:8-11`
- **Evidence**:
  ```
  dependencies = [
      "ops",
      "launchpadlib",     # never imported
      "pydantic",          # used only by the ingress library's own PYDEPS
      "httplib2>=0.32.0",  # never imported (transitive dep of launchpadlib)
      "jinja2>=3.1.6",     # never imported (transitive dep of launchpadlib)
  ]
  ```
  `grep -r "launchpadlib\|httplib2\|jinja2" src/ lib/ tests/` returns zero matches; the Go app (`internal/launchpad/launchpad.go`) handles Launchpad calls directly.
- **Impact**: Unnecessary packages inflate the charm's venv, build time, and package size.
- **Fix**: Remove `launchpadlib`, `httplib2`, `jinja2` from `pyproject.toml`. Verify whether `pydantic` is still needed as a top-level dependency once the ingress library's own `PYDEPS` is resolved at build time.
- **Linter rule**: "dependency listed in `pyproject.toml` but never imported in `src/`, `lib/`, or `tests/`" — mechanically checkable via `grep` + manifest parsing.

### 4. Ingress `ready` event fails to fire after re-adding relation
- **Severity**: medium
- **Kind**: bug
- **Where**: `lib/charms/traefik_k8s/v2/ingress.py` (LIBPATCH=19), `src/charm.py:43-44`
- **Evidence**: After removing and re-adding the ingress relation (ubuntu-manpages rev 62, traefik-k8s rev 377), `ingress-relation-created`/`-joined`/`-changed` all fired within 1 second, but `ingress.ready` — the only event the charm observes to trigger `_on_config_changed` and the Pebble replan — had not fired after 60 seconds. The Pebble plan still showed the unit-IP URL.
- **Impact**: An operator who removes and re-adds ingress sees stale URLs (sitemaps, JSON-LD, nav links) for an extended period. Initial integration worked correctly, so this is specific to the re-integration path.
- **Fix**: Update the ingress library to match traefik-k8s rev 377's expected version; consider also observing `ingress-relation-changed` as a fallback trigger for `_replan_workload` when ingress data is present but `ready` hasn't fired.
- **Linter rule**: not mechanically checkable in general; a library-version consistency check against the latest published `PYDEPS`/lib version is a reasonable proxy.

### 5. Storage definitions lack a minimum size
- **Severity**: medium
- **Kind**: ux / bug
- **Where**: `charmcraft.yaml:83-88`
- **Evidence**:
  ```yaml
  storage:
    manpages:
      type: filesystem
      location: /app/www/manpages
    manpages-gz:
      type: filesystem
      location: /app/www/manpages.gz
  ```
  No `minimum` size on either. The README documents ~9.4 GiB for 4 releases. On the test cluster storage used the 261G host overlay filesystem, masking the issue.
- **Impact**: Default K8s storage size can be far smaller than what the workload needs, leading to a confusing "low disk space" health-check failure rather than a clear deployment-time error.
- **Fix**: Add `minimum: 10G` (or higher, based on the documented 9.4 GiB for 4 releases) to both storage definitions.
- **Linter rule**: "storage defined without `minimum` when README documents disk usage exceeding platform default" — checkable if the linter can cross-reference README size data.

### 6. Broad `except Exception` in `_fetch_health_error` swallows unexpected errors
- **Severity**: low
- **Kind**: bug
- **Where**: `src/manpages.py:157`
- **Evidence**:
  ```python
  except urllib.error.HTTPError as e:
      ...
  except Exception:
      return "health check failed"
  ```
- **Impact**: Catches `KeyboardInterrupt`, `SystemExit`, `MemoryError`, etc. that should propagate. Low risk in a hook context.
- **Fix**: Narrow to `(urllib.error.URLError, OSError, json.JSONDecodeError)`.
- **Linter rule**: "bare `except Exception` with no re-raise" — mechanically checkable (ruff `TRY002`).

### 7. `_on_pebble_check_failed` silently ignores failures when `health_error()` returns `None`
- **Severity**: low
- **Kind**: bug
- **Where**: `src/charm.py:78-80`
- **Evidence**:
  ```python
  def _on_pebble_check_failed(self, event: ops.PebbleCheckFailedEvent):
      if event.info.name == "ready":
          if err := self._manpages.health_error():
              self.unit.status = ops.MaintenanceStatus(err)
  ```
- **Impact**: If the `ready` check is failing but `health_error()` returns `None` (e.g. `get_checks()` at `src/manpages.py:141` fails to reach Pebble), unit status is never updated — a previously `ActiveStatus` unit can stay `Active` despite a real failure.
- **Fix**: Set `MaintenanceStatus("health check failed")` when `health_error()` returns `None` but the event indicates a failure.
- **Linter rule**: "pebble check failed handler that conditionally sets status may leave status unchanged when the condition is falsy" — checkable with flow analysis.

### 8. `update-manpages` action bound to `_on_config_changed` — unnecessary server restart
- **Severity**: low
- **Kind**: ux / maintainability / performance
- **Where**: `src/charm.py:31`
- **Evidence**:
  ```python
  framework.observe(self.on.update_manpages_action, self._on_config_changed)
  ```
  `_on_config_changed` calls `_replan_workload()`, which always does:
  ```python
  container.add_layer("manpages", layer, combine=True)
  container.replan()
  ```
  `replan()` restarts all services whose plan changed, including the `manpages` server, not just `ingest`. Observed: the action completed in ~3 seconds with a brief server interruption even though the Pebble layer content hadn't actually changed.
- **Impact**: Every `update-manpages` invocation briefly interrupts the web server. The handler name is also misleading for an action.
- **Fix**: Factor the ingest-restart-and-purge logic into its own method called by the action handler (`container.restart("ingest")` + `purge_unused_manpages()`), separate from the full config-changed replan.
- **Linter rule**: not mechanically checkable.

### 9. `_get_external_url` always executes blocking `socket.getfqdn()`
- **Severity**: low
- **Kind**: bug / performance
- **Where**: `src/charm.py:109`
- **Evidence**:
  ```python
  external_url = f"http://{socket.getfqdn()}:{PORT}"  # always executed
  if binding := self.model.get_binding("juju-info"):
      unit_ip = str(binding.network.bind_address)
      external_url = f"http://{unit_ip}:{PORT}"        # always overwrites on k8s
  ```
- **Impact**: `socket.getfqdn()` can block for seconds on hosts with misconfigured DNS; on K8s the binding branch always overwrites the result, making the call dead weight.
- **Fix**: Move the `getfqdn()` call into an `else` branch, or default `external_url` to the binding IP directly.
- **Linter rule**: "`socket.getfqdn()` called unconditionally in K8s charm hook code" — checkable with a targeted warning.

### 10. Go config loads `.env` from working directory, silently overriding Pebble env vars
- **Severity**: low
- **Kind**: bug / security
- **Where**: `internal/config/config.go:33-34`, `internal/config/config.go:149-153`
- **Evidence**:
  ```go
  func Load() *Config {
      loadDotEnv()  // reads .env from cwd, os.Setenv for each key
      cfg := &Config{
          Site: envOrDefault("MANPAGES_SITE", "https://manpages.ubuntu.com"),
          ...
  ```
  `loadDotEnv()` opens `.env` from the working directory and overwrites env vars via `os.Setenv`, running before Pebble's own env vars are read.
- **Impact**: Low in practice (minimal image, controlled working directory), but it's a second, undocumented channel that can silently override `MANPAGES_SITE`, `MANPAGES_ARCHIVE`, `MANPAGES_RELEASES`, etc. — unnecessary surface area for a production binary.
- **Fix**: Gate `.env` loading behind a dev-only flag (e.g. `MANPAGES_DEV=true`), or only set values via `.env` when the key isn't already set rather than overriding.
- **Linter rule**: not mechanically checkable.

### 11. Dead code in `tests/spread/common.sh` — pre-rewrite systemd/nginx references
- **Severity**: nit
- **Kind**: lint
- **Where**: `tests/spread/common.sh:1-10`
- **Evidence**:
  ```bash
  cleanup_manpages() {
      systemctl stop nginx || true
      systemctl stop fcgiwrap || true
      systemctl stop update-manpages.service || true
      rm -rf /app
      rm -rf /etc/systemd/system/update-manpages.service
      apt-get purge -y nginx-full fcgiwrap jq curl w3m
      systemctl daemon-reload
  }
  ```
  `grep -r common.sh tests/spread/` returns no matches — the file is never sourced. The current charm is K8s-only with no systemd/nginx/fcgiwrap.
- **Impact**: Confusing leftover from the pre-rewrite machine-charm era; no functional effect since it's dead.
- **Fix**: Delete `common.sh`.
- **Linter rule**: "reference to `systemctl` in a repo with no machine-charm metadata" — mechanically checkable.

### 12. Workload container lacks curl/wget for debugging
- **Severity**: nit
- **Kind**: ux
- **Where**: `rockcraft.yaml`
- **Evidence**: Stage packages are only `ca-certificates` and `mandoc` — no `curl`/`wget`.
- **Impact**: Troubleshooting HTTP issues from inside the container requires adding tools externally. Low priority since `kubectl exec` with custom tooling is always available.
- **Fix**: Add `curl` to stage packages, or document a `kubectl`-based debugging approach in CONTRIBUTING.md.
- **Linter rule**: not mechanically checkable.

## Worth copying

- **Status precedence in `_compute_status`** (`src/charm.py:99-104`): health errors outrank "Updating manpages", which outranks Active — the correct urgency order, confirmed by `test_update_status_preserves_health_error_over_updating`.
- **Filesystem-based search index with in-memory caching** (`internal/search/fs_searcher.go:30-90`): index built eagerly at startup, held behind an `RWMutex`, rebuildable on demand. Four-tier matching (exact → prefix → contains → fuzzy, Damerau-Levenshtein with early bailout). No external search database needed.
- **Concurrency-controlled package fetching with retries** (`internal/fetcher/fetcher.go:81-170`): global semaphore bounds concurrent requests, retries with linear backoff, context cancellation for clean aborts — a reusable `doWithRetry` pattern.
- **Check-then-remove in storage writes** (`internal/storage/storage_fs.go:50-51`): removes any existing file/symlink before writing, avoiding stale symlinks from previous package versions.
- **Disk-space guard in health checks** (`internal/pipeline/diskspace.go`): verifies 100 MiB free and 1000 free inodes, handling filesystems that report `Files=0` (btrfs/zfs). Surfaced by the charm as `MaintenanceStatus` via `health_error()`.
- **Pebble health-check integration**: `up` (TCP, level=alive) vs `ready` (HTTP, level=unset); the charm only acts on `ready` failures, letting `alive` serve Juju's own use, confirmed by `test_pebble_check_failed_ignores_other_checks`.
- **OCI image with stripped Go binaries** (`rockcraft.yaml:35-38`): `-trimpath -ldflags="-s -w"`, combined with a minimal base image (only `ca-certificates`, `mandoc`).
- **Comprehensive scenario-based unit tests** (`tests/unit/test_charm.py`): 11 tests using `ops.testing.Context` + `State` + `Container` — current best practice.
- **Static asset ETag caching** (`internal/web/server.go`): content-hash ETags, 24h `Cache-Control`, `304 Not Modified` support, explicit MIME typing so minimal containers without `/etc/mime.types` still serve CSS/JS correctly.
- **Gzip response compression** (`internal/web/server.go`): conditional on `Accept-Encoding` and content type, correctly drops `Content-Length` when compressing.
- **Checksum fallback chain** (`internal/fetcher/fetcher.go: parsePackages()`): prefers SHA512 → SHA256 → SHA1 → MD5sum since archive pockets vary; used only as a change-detection fingerprint, so the fallback is safe.
- **Eager failure-log creation** (`internal/pipeline/pipeline.go: runRelease()`): creates `{release}-failures.log` before processing starts, appends with `O_APPEND`, letting operators `tail -f` during long ingests.

## Common-practice notes

- **Scenario testing**: `ops.testing.Context` + `State` — modern, good practice.
- **`PYTHONPATH` setup**: `Makefile` exports `PYTHONPATH=.:lib:src`, but `pyproject.toml` doesn't configure `pythonpath` for pytest, so running `pytest` directly fails with `ModuleNotFoundError`. Many projects now set `[tool.pytest.ini_options].pythonpath`.
- **uv for Python deps**: modern and recommended, no `requirements.txt` or `tox`.
- **Go + Python charm split**: the Python layer is a thin (~120 line) wrapper over a Go workload — a good choice for CPU-intensive rendering.
- **`.github/copilot-instructions.md` as `CLAUDE.md` symlink**: creative but fragile; target file holds useful Go-app documentation for AI assistants.
- **No terraform module**: common for single-charm repos.
- **`spread.yaml` uses `concierge`**: fine, but not the newest pattern (`spread` snap directly).
- **Library version**: only `lib/charms/traefik_k8s/v2/ingress.py` at LIBPATCH=19 is shipped. The `strip-prefix` schema warning and the re-integration `ready`-event delay both point to this library being stale relative to traefik-k8s. See Finding 4.
- **Python dependency hygiene**: three unused dependencies (`launchpadlib`, `httplib2`, `jinja2`) — see Finding 3.

## Tests

### Python unit tests
11 tests in `tests/unit/test_charm.py`, all passing (0.20s).
- Coverage: `src/charm.py` 89% (misses the pebble-check-failed error path and the `_get_external_url` FQDN branch); `src/manpages.py` 50% (misses the `ValueError` path, purge error paths, `health_error` error paths, and `_fetch_health_error` body parsing).
- `PYTHONPATH=src:lib:.` must be set, or `make unit` used; running `pytest tests/unit` directly fails.

### Python integration tests
Two `jubilant`-based modules: `tests/integration/test_charm.py` (deploy + server response + manpages downloading) and `tests/integration/test_ingress.py` (deploy with traefik + ingress URL + HTTP through ingress). Both assert real HTTP responses, not just active/idle. Run via `spread`; could not run locally (no jubilant/juju integration environment on this VM).

### Go tests
Could not run — Go 1.24+ not installed on this VM (unverified against this revision). CI runs `go test -v -race ./...`. `*_test.go` files exist alongside most packages: config, fetcher, launchpad, pipeline (converter, diskspace, paths), search (distance, fs_searcher), sitemap, storage, transform (doc, links, meta, structure, title, toc), web server.

### Spread tests
Two tasks, `deploy-charm` and `ingress`, using LXD VMs with concierge (LXD and github-ci backends). `tests/spread/common.sh` is dead code (Finding 11).

### Lint
- `uv run ruff check src/ tests/`: all checks passed, zero warnings.
- `charmcraft analyse`: not available on this VM.

### Coverage gaps relative to risk
- **High**: no unit test for the `ValueError` on empty/invalid releases (Finding 1), and no test for a would-be `except ValueError` branch in `_replan_workload`.
- **Medium**: no unit test for `_fetch_health_error` on non-JSON or 503-without-body responses; none for `purge_unused_manpages` error paths; none for `_on_pebble_check_failed` when `health_error()` returns `None` (Finding 7).
- **Low**: no integration test for the `update-manpages` action; none for ingress re-integration after revoke (Finding 4); Go `-race` test results unverified on this revision (couldn't run locally).

### CI workflows
`.github/workflows/`: `pull-request.yaml` triggers `build-and-test.yaml` on PRs (ruff + go vet, Python unit tests, Go tests with `-race`, rockcraft build, charm pack, spread on LXD). `release.yaml` on push to `main`: full build-and-test → publish rock to ghcr.io → upload to charmhub `latest/edge`. `promote.yaml`: manual dispatch to promote edge → stable. `zizmor.yaml`: Actions security analysis. Well-structured with caching, matrix strategies, and artifact passing; no gaps beyond those noted above.

## Docs

- **README.md**: excellent — covers what the charm does, Go app architecture (three binaries, config env vars, ingest pipeline, web server), deployment instructions, ingress integration, and observed resource requirements (9.4 GiB for 4 releases). Deployment example shows realistic `juju status` output.
- **CONTRIBUTING.md**: thorough Go/Python dev workflows, workshop alternative, spread testing, troubleshooting.
- **SECURITY.md**: present with clear reporting instructions.
- **Charmhub description**: concise, links to the live site.
- **Doc/reality match**: README's default releases (`questing, plucky, oracular, noble, jammy`) match `charmcraft.yaml`.
- **`tests/spread/integration/ingress/task.yaml:1`** describes the test as "manpages and haproxy" but the test actually uses traefik-k8s — minor doc discrepancy.

## Open questions

1. **Go test results**: `go test ./...` (with `-race`) could not be run on this VM. Worth confirming a clean pass on this revision.
2. **TLS**: served plain HTTP on 8080 by design, TLS terminated at ingress; admin port 9090 is localhost-only. No charm-level TLS option — matches the documented design.
3. **Release validation**: any string matching `[a-z]+` is accepted as a release codename with no check against real Ubuntu codenames — see Finding 2. Worth validating against a known set or the Launchpad API.
4. **Ingest-on-success**: the `ingest` service has `on-success: ignore`, so once ingestion completes it stays dead until manually re-triggered. No scheduled re-ingestion exists — would a periodic restart make sense in production?
5. **Ingress library staleness**: LIBPATCH=19 may lag behind traefik-k8s rev 377 (see Finding 4). What LIBPATCH does the latest traefik-k8s ingress library ship, and would updating resolve the re-integration delay?
</content>
