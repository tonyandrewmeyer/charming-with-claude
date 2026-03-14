# Charm Anti-Patterns: Searchable Patterns

Concrete grep patterns to find bugs in charm code. For each pattern: what to search for, how to distinguish bugs from false positives, and the correct fix.

## Contents
- Configuration and Types (AP-001 to AP-005)
- Pebble and Container Management (AP-006 to AP-010)
- Relations and Events (AP-011 to AP-015)
- TLS and Security (AP-016 to AP-021)
- Grafana and Observability (AP-022 to AP-025)
- URL and Network (AP-026 to AP-028)
- Status Management (AP-029 to AP-032)
- Database (AP-033 to AP-035)
- Error Handling (AP-036 to AP-039, AP-044 to AP-046)
- Build and Packaging (AP-040 to AP-043)
- Logic and Data Flow (AP-048 to AP-069)

---

## Configuration and Types

### AP-001: Truthiness check on config values
- **Search:** `if self\.config\[` or `if self\.config\.get\(`
- **Bug:** `if self.config['port']:` treats port 0 as "not set"
- **False positive:** When the value genuinely cannot be 0, empty, or False (e.g., required name field)
- **Fix:** `if self.config['port'] is not None:`

### AP-002: Missing f-string prefix
- **Search:** Look for strings containing `{self.` or `{event.` or `{model.` without `f` prefix
- **Bug:** `'value={self.name}'` produces literal text
- **False positive:** Regex patterns, `.format()` strings, log format strings with `%s`
- **Fix:** Add `f` prefix: `f'value={self.name}'`

### AP-003: Boolean from environment variable
- **Search:** `bool(os.getenv` or `bool(os.environ`
- **Bug:** `bool(os.getenv('FLAG', ''))` returns True for "false", "0", "no"
- **False positive:** None
- **Fix:** `os.getenv('FLAG', '').lower() in ('true', '1', 'yes')`

### AP-004: Config type mismatch
- **Search:** Compare `config.yaml` type declarations with usage in `src/charm.py`
- **Bug:** Config declared as `string` but `int()` cast missing in code, or declared as `int` but compared as string
- **False positive:** When type is correctly matched
- **Fix:** Ensure `config.yaml` type matches code usage; add explicit casts

### AP-005: None or non-string values in environment dicts
- **Search:** `environment` in Layer definitions, trace dict values for possible None or non-string types (bool, int)
- **Bug:** `{key: value}` where value can be None or is a Python bool/int causes Pebble to reject the layer or produce wrong values. `True` becomes `"True"` (capital T) which may not match what Go/shell expects.
- **False positive:** When None values are filtered with `if v is not None` and non-strings are explicitly cast
- **Fix:** `{k: str(v) if v is not None else None for k, v in env.items() if v is not None}` or use lowercase string booleans: `"true"` / `"false"`

---

## Pebble and Container Management

### AP-006: Missing can_connect() check
- **Search:** `container.push` or `container.restart` or `container.replan` or `container.exec`
- **Bug:** Pebble operations without checking container readiness
- **False positive:** When wrapped in `try/except ConnectionError` or preceded by `can_connect()`
- **Fix:** Add `if not container.can_connect(): event.defer(); return`

### AP-007: Direct plan mutation
- **Search:** `plan.services[` followed by assignment
- **Bug:** Modifying plan object in-place does not persist
- **False positive:** When used read-only for comparison
- **Fix:** Create new Layer and use `container.add_layer(..., combine=True)`

### ~~AP-008: Unconditional replan~~ (REMOVED)
> Removed after human review (rounds 5-6). Pebble internally compares plans before restarting services during `replan()`. The charm-side plan comparison is unnecessary overhead. It is better to let Pebble handle idempotency than have the charm pull the plan and compare.

### AP-009: Container name assumption
- **Search:** `self.meta.name` used as container name, or `container_name = self.app.name`
- **Bug:** Container name may differ from charm/app name
- **False positive:** When they genuinely match per metadata.yaml
- **Fix:** Read from `self.meta.containers` dynamically

### AP-010: Missing ChangeError handling on restart
- **Search:** `container.restart(` without nearby `except.*ChangeError`
- **Bug:** Unhandled ChangeError from Pebble rate limiting crashes charm
- **False positive:** When wrapped in try/except
- **Fix:** `try: container.restart(...) except ChangeError as e: ...`

---

## Relations and Events

### AP-011: relation_departed doing full cleanup
- **Search:** `_on_.*relation_departed` handler body doing cleanup (deleting config, stopping services)
- **Bug:** Premature cleanup when only one unit left, not the entire relation
- **False positive:** When departed is used for per-unit scaling logic
- **Fix:** Move full cleanup to `relation_broken`

### AP-012: Missing relation_broken handler
- **Search:** Compare `relation_joined` and `relation_changed` handlers against `relation_broken` handlers
- **Bug:** No cleanup when critical relations are removed
- **False positive:** When the relation is purely informational
- **Fix:** Add `relation_broken` handler that cleans up and sets BlockedStatus

### AP-013: Relation data overwrite in loop
- **Search:** `for.*relation.*in.*self.model.relations` with assignment (not append/extend) in body
- **Bug:** Variable assigned inside loop overwrites previous iterations' results
- **False positive:** When only one relation is expected (check `limit` in metadata.yaml)
- **Fix:** Use `.append()` or `.extend()` to accumulate results

### ~~AP-014: event.relation.app is None~~ (REMOVED)
> Removed after human review (rounds 5-6). Modern versions of the ops library guarantee that `event.relation.app` and `relation.app` are always non-None, even during relation teardown. This was historically an issue but has been fixed in the framework.

### AP-015: Missing leader guard on app data write
- **Search:** `data[self.app]` assignment without `is_leader()` check in same function
- **Bug:** Non-leader units get ModelError writing app relation data
- **False positive:** When the function is only called after leader check
- **Fix:** Add `if not self.unit.is_leader(): return` guard

---

## TLS and Security

### AP-016: Stale TLS flag in relation data
- **Search:** `relation_data` containing `tls` or `mtls` as a stored boolean/string flag
- **Bug:** TLS flags become stale when leader changes or relation is removed
- **False positive:** None observed
- **Fix:** Check relation existence: `self.model.get_relation("certificates") is not None`

### AP-017: CA chain as string instead of list
- **Search:** `ca_chain` with type annotation `Optional[str]` instead of `Optional[list[str]]`
- **Bug:** Libraries expect list[str] for CA chain
- **False positive:** When the consumer explicitly handles both formats
- **Fix:** `ca_chain: Optional[list[str]]`

### AP-018: Credential logging
- **Search:** `logger.info` or `logger.debug` near `password`, `secret`, `credential`, `token`
- **Bug:** Passwords/secrets logged in plaintext
- **False positive:** When logging the key name, not the value; when logging redacted/masked value
- **Fix:** Remove the log statement or mask the value

### AP-019: World-readable credential files
- **Search:** `open(` writing files near `password`, `secret`, `credential` without `chmod` or `mode=0o600`
- **Bug:** Config files with credentials created with default (world-readable) permissions
- **False positive:** When the file contains no sensitive data
- **Fix:** `path.touch(mode=0o600)` before writing, or `os.chmod(path, 0o600)` after

### AP-020: Credentials in CLI arguments
- **Search:** `subprocess.run` or `subprocess.call` with password/credential in argument list
- **Bug:** Passwords visible in `ps` output and `/proc`
- **False positive:** When the tool has no env var or config file alternative
- **Fix:** Use environment variables or config files for credentials

### AP-021: Incomplete input validation regex
- **Search:** `re.match` with `\w` or missing `^` and `$` anchors
- **Bug:** `\w` includes underscore; missing anchors allow partial matches and injection
- **False positive:** When underscore is intentionally allowed and partial matching is desired
- **Fix:** Use explicit character classes with `^` and `$` anchors

---

## Grafana and Observability

### AP-022: Wrong datasource variable
- **Search:** `DS_PROMETHEUS` or `$datasource` or `DS_LOKI` in dashboard JSON files
- **Bug:** Dashboard uses non-COS-standard datasource variable
- **False positive:** None in COS context
- **Fix:** Replace with `${prometheusds}` or `${lokids}`

### AP-023: Hardcoded datasource UID
- **Search:** `"uid":` with a long alphanumeric string in dashboard JSON
- **Bug:** Dashboard uses local datasource UID instead of template variable
- **False positive:** None
- **Fix:** Replace with `${prometheusds}`

### AP-024: Wrong rate interval
- **Search:** `$__interval` inside `rate(` or `increase(` in dashboard JSON
- **Bug:** `$__interval` instead of `$__rate_interval` causes under-counting
- **False positive:** When used outside of rate/increase functions
- **Fix:** Use `$__rate_interval` in all rate/increase calls

### AP-025: Overly broad alert expression
- **Search:** Alert rules with `{}` empty label matchers, or `for: 0m`
- **Bug:** Alerts match disabled/inactive resources; `for: 0m` fires on flapping
- **False positive:** When broad matching is intentional
- **Fix:** Add state/status label filters; increase `for:` duration

---

## URL and Network

### AP-026: urljoin path loss
- **Search:** `urljoin` calls
- **Bug:** `urljoin("http://host/api/v1", "/endpoint")` drops `/api/v1`
- **False positive:** When the path argument never starts with `/`
- **Fix:** `f"{base.rstrip('/')}/{path.lstrip('/')}"`

### AP-027: Hardcoded http scheme
- **Search:** `"http://"` string concatenation for URLs where TLS may be enabled
- **Bug:** URL uses http:// when TLS is configured
- **False positive:** When TLS is never used for this connection
- **Fix:** `scheme = "https" if tls_enabled else "http"`

### AP-028: Missing port in URL
- **Search:** URL construction that omits port or uses wrong default
- **Bug:** URL works in dev (default ports) but fails in production (custom ports)
- **False positive:** When the service always uses the default port
- **Fix:** Always include configured port in URL

---

## Status Management

### AP-029: ActiveStatus set before all subsystems ready
- **Search:** `ActiveStatus()` set in individual event handlers
- **Bug:** One handler sets Active while another subsystem (DB, TLS, Pebble) is not ready
- **False positive:** When using collect_unit_status to reconcile
- **Fix:** Centralize status logic in `_update_status()` or `collect_unit_status`

### AP-030: Missing status on early return
- **Search:** `return` statements in event handlers without preceding `self.unit.status =`
- **Bug:** Early return leaves stale status from previous event
- **False positive:** When collect_unit_status handles reconciliation
- **Fix:** Set appropriate status before returning

### AP-031: Blocked vs Waiting confusion
- **Search:** `BlockedStatus("Waiting` or `WaitingStatus("Please`
- **Bug:** Blocked means user action needed; Waiting means automatic resolution expected
- **False positive:** Wording matters -- check if the message matches the status type
- **Fix:** Use BlockedStatus for user-action-required, WaitingStatus for automatic-resolution

### AP-032: Status message with stale variable reference
- **Search:** Status messages containing `{` but not preceded by `f`
- **Bug:** `BlockedStatus("Missing config: {config_name}")` produces literal text
- **False positive:** When `{` is part of a JSON example in the message
- **Fix:** Add `f` prefix

---

## Database

### AP-033: Connection string not refreshed on failover
- **Search:** Connection string stored as instance variable, not re-read from relation data
- **Bug:** After database failover, charm connects to old primary
- **False positive:** When relation_changed handler updates the stored value
- **Fix:** Read connection info from relation data on each use, or update in relation_changed

### AP-034: TLS toggle race
- **Search:** TLS enable/disable logic that doesn't coordinate with database restart
- **Bug:** Charm and database disagree on TLS state, connections fail silently
- **False positive:** When TLS state is coordinated via relation data handshake
- **Fix:** Implement two-phase TLS toggle with status coordination

### AP-035: Missing database readiness check
- **Search:** Database operations without checking if the database relation is established
- **Bug:** Operations fail with cryptic errors when DB relation is not yet available
- **False positive:** When relation check is done by caller
- **Fix:** Check `self.model.get_relation("database")` before operations

---

## Error Handling

### AP-036: Narrow except clause
- **Search:** `except ApiError` or single-type except blocks around external calls
- **Bug:** Other exception types (TypeError, AttributeError, ConnectionError) not caught
- **False positive:** When only one exception type is possible
- **Fix:** Catch all reasonable exception types, or use broader base class

### AP-037: Bare except swallowing errors
- **Search:** `except Exception: pass` or `except: pass`
- **Bug:** Hides real errors that should be logged
- **False positive:** Intentional error suppression (rare)
- **Fix:** `except Exception as e: logger.error("...", e)`

### AP-038: Exception in loop without continue
- **Search:** Try/except inside a `for` loop without `continue` in the except block
- **Bug:** Exception handling doesn't resume the loop; may re-raise or fall through
- **False positive:** When the except block intentionally breaks the loop
- **Fix:** Add `continue` after logging the error

### AP-039: Printf-style exception constructor
- **Search:** `raise.*Error(".*%s` or `raise.*Error(".*%d`
- **Bug:** `TypeError("msg %s", val)` passes val as a separate arg, not formatted
- **False positive:** None
- **Fix:** `raise TypeError(f"msg {val}")` or `raise TypeError("msg %s" % val)`

### AP-044: Missing return after event.fail()
- **Search:** `event.fail(` without `return` on the next line or same block
- **Bug:** After `event.fail()`, execution continues and performs the success path (logging success, setting results with None)
- **False positive:** When `event.fail()` is the last statement before a natural block end
- **Fix:** Add `return` immediately after `event.fail(...)`

### AP-045: next() without default on relation/config data
- **Search:** `next(` without a second argument, especially on generators over relation data, config lists, or parsed output
- **Bug:** `next(x for x in items if condition)` raises `StopIteration` when no match, which is unhandled and can silently terminate generators
- **False positive:** When the condition is guaranteed to match (e.g., iterating over a known-populated list)
- **Fix:** `next((x for x in items if condition), None)` followed by a None check

### AP-046: Shell-style $VAR in Python f-strings
- **Search:** `f"$` or `f'$` in Python source files
- **Bug:** `f"${self.path}/logs"` produces a literal `$` in the output because `$` is not a Python interpolation character; only `{...}` is
- **False positive:** When `$` is intentionally part of the output (e.g., shell scripts, regex)
- **Fix:** Remove the `$`: `f"{self.path}/logs"`

### AP-047: Contradictory unit vs app status
- **Search:** Compare `event.add_status(BlockedStatus(` with `self.app.status = WaitingStatus(` (or vice versa) for the same condition
- **Bug:** Unit and app status types disagree -- one says user action needed (Blocked), the other says automatic resolution (Waiting)
- **False positive:** When the unit and app intentionally have different status semantics
- **Fix:** Use the same status type for unit and app when they describe the same condition

---

## Build and Packaging

### AP-040: Requirements pointing to git branch
- **Search:** `git+` or `@main` or `@master` in `requirements.txt`
- **Bug:** Unpinned git dependency changes unexpectedly
- **False positive:** Intentional development dependency
- **Fix:** Pin to specific version or commit hash

### AP-041: Missing dependency in charmcraft.yaml
- **Search:** Import statements in src/ vs dependencies in charmcraft.yaml or requirements.txt
- **Bug:** Import works in dev but fails in packed charm
- **False positive:** Standard library imports
- **Fix:** Add missing dependency to charmcraft.yaml

### AP-042: OCI image tag instead of digest
- **Search:** `image:` with `:latest` or version tag without `@sha256:`
- **Bug:** Image tag can change, causing inconsistent deployments
- **False positive:** When image is internally controlled
- **Fix:** Use `image@sha256:...` digest

### AP-043: GitHub Actions workflow referencing wrong branch
- **Search:** `@master` or `@main` in workflow `uses:` statements
- **Bug:** Branch rename (master -> main) breaks CI
- **False positive:** When the referenced repo still uses master
- **Fix:** Update to current default branch name, or pin to tag/commit

---

## Logic and Data Flow

### AP-048: exec() without wait()
- **Search:** `container.exec(` where the return value is not assigned or `.wait()` / `.wait_output()` is not called
- **Bug:** `container.exec(["find", dir, "-delete"])` runs asynchronously. If subsequent code writes files to the same directory, the still-running command may delete them.
- **False positive:** When the exec command has no side effects on files that are subsequently used
- **Fix:** `container.exec([...]).wait()` or `process = container.exec([...]); process.wait()`

### AP-049: Hardcoded string slicing for file extensions
- **Search:** `path.name[:\d+]` or `filename[:\d+]` -- hardcoded slice indices on filenames
- **Bug:** `path.name[:5]` to strip `.cert` only works for exactly 5-character basenames. Longer or shorter names produce wrong results, causing valid certs to be deleted or stale certs retained.
- **False positive:** None observed
- **Fix:** Use `path.stem`, `path.name.removesuffix(".cert")`, or `os.path.splitext()`

### AP-050: Status set by helper overwritten by caller
- **Search:** Helper methods that set `self.unit.status = BlockedStatus(...)` or `WaitingStatus(...)` and return without a flag, where the caller continues to set a different status
- **Bug:** Helper sets `BlockedStatus("misconfigured")` and returns, but the calling `_update()` method proceeds to set `MaintenanceStatus("replanning")`, silently hiding the error condition from operators.
- **False positive:** When the caller explicitly checks the helper's return value before continuing
- **Fix:** Have the helper return a bool/enum indicating whether the caller should abort, or raise an exception

### AP-051: Inverted boolean condition
- **Search:** `if.*is False:` or `if not.*:` near warning/error logging about the same variable being True
- **Bug:** `if skip_verify is False: logger.warning("configured to skip verification")` -- logs the warning when verification is ENABLED, not when it's skipped
- **False positive:** When the condition and message genuinely describe the same state
- **Fix:** Invert the condition to match the message semantics

### AP-052: Wrong config key name (silent miss)
- **Search:** Compare config key strings in Python code against keys defined in `config.yaml` or `charmcraft.yaml`
- **Bug:** `self.config.get("pki_ca_allowed_domains")` when the actual key is `pki_allowed_domains`. `.get()` returns `None`/default silently, causing validation to be bypassed.
- **False positive:** When the key is dynamically constructed or comes from a library
- **Fix:** Use the exact key name from config.yaml; consider using constants for config keys

### AP-053: Missing return after event.set_results()
- **Search:** `event.set_results(` without `return` in subsequent lines, where execution can continue to a second `event.set_results()` or `event.fail()` call
- **Bug:** Similar to AP-044. `event.set_results()` does not stop execution. If the code falls through to a second call path, results may be overwritten or contradictory actions taken.
- **False positive:** When `event.set_results()` is the last statement before a natural block end
- **Fix:** Add `return` immediately after `event.set_results(...)` when it represents an early-exit case

### AP-054: String comparison of numeric counter values
- **Search:** Comparison operators (`>`, `<`, `>=`, `<=`) on values from relation data that represent counters or sequence numbers, without `int()` conversion
- **Bug:** `if relation_counter > counter:` does lexicographic comparison. `"9" > "10"` is `True` because `"9"` > `"1"`. All relation data values are strings, so numeric comparison requires explicit `int()` conversion.
- **False positive:** When the compared values are genuinely strings (names, UUIDs)
- **Fix:** `if int(relation_counter) > int(counter):`

### AP-055: None value in f-string URL interpolation
- **Search:** f-strings containing `{self.` where the property can return `None`, especially URL construction like `f"{self.external_url}/path"`
- **Bug:** When the property is `None`, the f-string produces `"None/path"` -- a valid-looking but broken URL that won't cause an immediate crash but silently does the wrong thing.
- **False positive:** When the property is guaranteed non-None by preceding guards
- **Fix:** Use a property that always returns a fallback value, or add a None guard before the f-string

### AP-056: Action handler missing event.fail() on error path
- **Search:** Action handlers (`_on_*_action`) that catch exceptions or detect errors but only `logger.error()` without calling `event.fail()`
- **Bug:** The action completes with success status but returns no data, misleading the user and automation scripts.
- **False positive:** When the error is truly non-fatal and partial success is acceptable
- **Fix:** Add `event.fail("error message")` before `return` in error paths

### AP-057: os.path.join for URL construction
- **Search:** `os.path.join(` or `from os.path import join` used with URL-like arguments (containing `http`, `://`, or URL path segments)
- **Bug:** `os.path.join` is for filesystem paths, not URLs. On Linux it works by coincidence for simple cases, but if the second argument starts with `/`, it discards the base URL entirely. Also breaks on Windows (backslash separators).
- **False positive:** When actually constructing filesystem paths
- **Fix:** Use `urllib.parse.urljoin`, `yarl.URL`, or `f"{base.rstrip('/')}/{path.lstrip('/')}"`

### AP-058: model.get_secret(id=None)
- **Search:** `model.get_secret(id=` where the id comes from `.get()` or can otherwise be `None`
- **Bug:** `secret_id = peer_data.get("secret-id"); self.model.get_secret(id=secret_id)` crashes when secret_id is None (before leader has set it). `.get()` returns None for missing keys.
- **False positive:** When there's an explicit None check before the call
- **Fix:** Add `if secret_id is None: return None` before calling `get_secret()`

### AP-059: Comparison operator instead of assignment for status
- **Search:** `self.unit.status ==` (note double equals)
- **Bug:** `self.unit.status == WaitingStatus(msg)` compares instead of assigning. Status is never set. The comparison expression is evaluated and discarded.
- **False positive:** None -- `==` on status is always a bug (there's no reason to compare and discard)
- **Fix:** `self.unit.status = WaitingStatus(msg)` (single `=`)

### AP-060: Operator precedence bug with ternary in expressions
- **Search:** `or.*if.*else` on a single line, especially in function arguments
- **Bug:** `port = value or 443 if tls else 80` parses as `(value or 443) if tls else 80`, not `value or (443 if tls else 80)`. When `tls` is False, the result is always `80` regardless of `value`.
- **False positive:** When the `or` short-circuit is actually intended
- **Fix:** Add parentheses: `value or (443 if tls else 80)`

### AP-061: Glob pattern in exec without shell
- **Search:** `container.exec([` with `*` in arguments
- **Bug:** `container.exec(["rm", "-f", "dir/*.yaml"])` passes `*` as a literal character because Pebble's exec does not invoke a shell. No files match the literal filename `dir/*.yaml`, so nothing is deleted.
- **False positive:** When the `*` is part of a fixed filename, not a glob
- **Fix:** Use shell: `container.exec(["/bin/sh", "-c", "rm -f dir/*.yaml"])` or use `container.list_files()` + `container.remove_path()`

### AP-062: DeepDiff `is not None` instead of truthiness
- **Search:** `DeepDiff(` followed by `is not None`
- **Bug:** `DeepDiff()` always returns a DeepDiff object (never None). `if diff is not None:` is always True. The correct check is `if diff:` (truthiness), which is False when there are no differences.
- **False positive:** None
- **Fix:** `if diff:` or `if bool(diff):`

### AP-063: Unescaped external data interpolated into config language
- **Search:** f-strings or `.format()` that embed relation data, secrets, or config values into PHP, YAML, TOML, INI, SQL, or shell script strings
- **Bug:** If the interpolated value contains syntax-significant characters (quotes, backslashes, newlines), the generated config file has a syntax error or, worse, allows code injection. Common with database passwords in `wp-config.php`, YAML config files, or shell scripts.
- **False positive:** When the value is guaranteed to be alphanumeric (e.g., auto-generated hex tokens)
- **Fix:** Use language-appropriate escaping: `shlex.quote()` for shell, proper serialisers for YAML/JSON, escape sequences for PHP/SQL strings

### AP-064: Missing None guard on version field from relation data
- **Search:** `.split(".")` on values from `fetch_relation_field` or `databag.get` that are not in the None check
- **Bug:** Version field may not yet be set in relation data. If the None guard checks `endpoint`, `user`, `password` but omits `version`, calling `version.split(".")` raises `AttributeError`.
- **False positive:** When version is included in the None check
- **Fix:** Include version in the None guard: `if None in [endpoint, user, password, version]: return None`

### AP-065: Implicit None return used as valid value
- **Search:** Functions with `-> str` return type that have code paths with no explicit `return`
- **Bug:** A function iterates over options and returns a value when found, but has no return statement after the loop. Callers use the result in f-strings or `.add()`, producing `"None:30123"` or adding `None` to sets.
- **False positive:** When callers explicitly check for None before using the result
- **Fix:** Add explicit `return None` after the loop and add a None guard in the caller

### AP-066: lstrip/rstrip used as removeprefix/removesuffix
- **Search:** `lstrip(` or `rstrip(` with a multi-character string argument (not single char)
- **Bug:** `path.lstrip("s3://bucket/")` removes individual *characters* `s`, `3`, `:`, `/`, `b`, `u`, `c`, `k`, `e`, `t` from the left, not the prefix string. This silently corrupts the result when leading characters of the remainder overlap with characters in the argument.
- **False positive:** When the argument is a single character (e.g., `lstrip("/")`) — single-char lstrip is correct
- **Fix:** Use `str.removeprefix()` / `str.removesuffix()` (Python 3.9+), or `if s.startswith(prefix): s = s[len(prefix):]`

### AP-067: Missing initialisation guard in early-lifecycle event handlers
- **Search:** `_on_leader_elected`, `_on_.*relation_created`, `_on_.*relation_joined` handlers that call workload methods (database queries, cluster operations, API calls) without checking initialisation state
- **Bug:** Events like `leader-elected` and `relation-created` fire very early in the charm lifecycle, before the workload is fully initialised. Handlers that assume the workload is ready will crash or produce wrong results.
- **False positive:** When the handler explicitly checks initialisation state (peer data flags, `unit_initialized()`, cluster membership) before calling workload methods
- **Fix:** Add initialisation guards and either `return` early or `event.defer()` when the workload is not yet ready

### AP-068: Config-derived relation data not re-sent on config_changed
- **Search:** Relation data providers that set data in `relation_joined`/`relation_changed` but are not called from `_on_config_changed`
- **Bug:** When relation data depends on config values (e.g., gateway name, external hostname, port), changing the config does not trigger re-sending updated data to related applications. Related apps retain stale information.
- **False positive:** When the relation data is config-independent, or when a centralised reconciler already handles all events
- **Fix:** Call the relation data update method from `_on_config_changed` as well as from relation handlers

### AP-069: Exception message or traceback leaks credentials
- **Search:** `logger.exception(` or `exc_info=` near code that calls external tools with credentials in arguments or connection strings
- **Bug:** `logger.exception(f"Failed: {e.message}", exc_info=e)` logs the full traceback, which may include the command line or connection string containing passwords. Unlike AP-018 (explicitly logging credentials), this leak is implicit through exception details.
- **False positive:** When the exception cannot contain credential data (e.g., pure Python logic errors)
- **Fix:** Use `logger.error()` with a sanitised message instead of `logger.exception()`. Do not include `e.message` or `exc_info=` when the exception may contain credentials
