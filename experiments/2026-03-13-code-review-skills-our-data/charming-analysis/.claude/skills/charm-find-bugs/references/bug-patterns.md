# Charm Bug Patterns Reference

Derived from analysis of 6,116 bug fixes across 134 Juju charm repositories.

## Contents
- Pebble and Container Management
- Relations and Events
- TLS and Certificate Lifecycle
- Configuration Handling
- Status Management
- Ingress and Networking
- Observability and Grafana
- Database Interaction
- Auth and Identity
- Upgrade and Migration
- Juju Interaction
- Exception Handling
- Security

---

## Pebble and Container Management

199 fixes across 61 repos. 5 high severity.

### Missing can_connect() guard

Pebble operations without checking container readiness crash the charm when the workload container is not yet ready or temporarily unavailable.

**Before (buggy):**
```python
def _on_config_changed(self, event):
    container = self.unit.get_container("workload")
    container.push("/etc/config.yaml", config_content)
    container.replan()
```

**After (fixed):**
```python
def _on_config_changed(self, event):
    container = self.unit.get_container("workload")
    if not container.can_connect():
        event.defer()
        return
    container.push("/etc/config.yaml", config_content)
    container.replan()
```

**Repos affected:** alertmanager-k8s, grafana-k8s, loki-k8s, prometheus-k8s, tempo-coordinator-k8s, discourse-k8s, synapse, many more.

### Unconditional replan

Calling `container.replan()` on every event causes unnecessary service restarts, potentially dropping in-flight requests.

**Before (buggy):**
```python
def _on_config_changed(self, event):
    layer = self._build_layer()
    container.add_layer("app", layer, combine=True)
    container.replan()  # Restarts even when nothing changed
```

**After (fixed):**
```python
def _on_config_changed(self, event):
    layer = self._build_layer()
    container.add_layer("app", layer, combine=True)
    plan = container.get_plan()
    if plan.services != layer.services:
        container.replan()
```

### Direct plan mutation

Modifying `plan.services[name].environment` in-place does not persist changes. The plan object is a snapshot.

**Before (buggy):**
```python
plan = container.get_plan()
plan.services["app"].environment["NEW_VAR"] = "value"
# Change is lost -- plan is a snapshot, not a live reference
```

**After (fixed):**
```python
new_layer = Layer({
    "services": {"app": {"environment": {"NEW_VAR": "value"}}}
})
container.add_layer("app", new_layer, combine=True)
container.replan()
```

### Missing ChangeError handling on restart

`container.restart()` can raise `ChangeError` (e.g., HTTP 429 rate limit from Pebble). Unhandled, this crashes the charm.

**Before (buggy):**
```python
container.restart("workload")
```

**After (fixed):**
```python
try:
    container.restart("workload")
except ChangeError as e:
    logger.warning("Failed to restart: %s", e)
    event.defer()
```

### None or non-string values in Pebble environment dicts

Pebble rejects None values and may mishandle non-string values in service environment dictionaries. Python `bool` values become `"True"`/`"False"` (capital) which may not match what Go expects (`"true"`/`"false"` lowercase).

**Before (buggy):**
```python
env = {
    "DB_HOST": self._get_db_host(),  # May return None
    "TRACING_ENABLED": True,  # Python bool, becomes "True" not "true"
}
layer = Layer({"services": {"app": {"environment": env}}})
```

**After (fixed):**
```python
env = {k: v for k, v in {
    "DB_HOST": self._get_db_host(),
    "TRACING_ENABLED": "true",  # Explicit lowercase string
}.items() if v is not None}
```

**Repos affected:** hydra-operator (bool in env dict), many SD-Core charms (None from _get_pod_ip()).

---

## Relations and Events

59 fixes across 39 repos. 4 high severity.

### relation_departed vs relation_broken confusion

`relation_departed` fires when a single unit leaves; `relation_broken` fires when the entire relation is removed. Using departed for full cleanup causes premature resource removal while other units remain.

**Before (buggy):**
```python
def _on_db_relation_departed(self, event):
    # Wrong: removes DB config even when other DB units remain
    self._clear_database_config()
    self.unit.status = BlockedStatus("Database removed")
```

**After (fixed):**
```python
def _on_db_relation_broken(self, event):
    self._clear_database_config()
    self.unit.status = BlockedStatus("Database relation removed")
```

### Missing relation_broken handler

When `relation_joined`/`relation_changed` sets up resources, a missing `relation_broken` handler leaves stale configuration.

**How to detect:** Search for relations with `relation_joined` or `relation_changed` handlers but no corresponding `relation_broken`.

### event.relation.app is None

In some events (e.g., during relation teardown), `event.relation.app` can be None. Accessing `.data[event.relation.app]` raises KeyError.

**Before (buggy):**
```python
def _on_relation_changed(self, event):
    remote_data = event.relation.data[event.relation.app]
```

**After (fixed):**
```python
def _on_relation_changed(self, event):
    if event.relation.app is None:
        event.defer()
        return
    remote_data = event.relation.data[event.relation.app]
```

### Relation data overwrite in loop

When iterating over multiple relations, overwriting (instead of appending) loses data from all but the last relation.

**Before (buggy):**
```python
for relation in self.model.relations["database"]:
    connection_info = self._get_connection(relation)
    # Overwrites previous iteration's result
```

**After (fixed):**
```python
connections = []
for relation in self.model.relations["database"]:
    connections.append(self._get_connection(relation))
```

---

## TLS and Certificate Lifecycle

299 fixes across 67 repos. 10 high severity.

### Stale TLS flags in relation data

Storing `tls_enabled: true` in relation data instead of checking relation existence. When leadership changes or the TLS relation is removed, the flag becomes stale.

**Before (buggy):**
```python
if self._get_relation_data("peer").get("tls_enabled") == "true":
    self._configure_tls()
```

**After (fixed):**
```python
if self.model.get_relation("certificates") is not None:
    self._configure_tls()
```

### CA chain type mismatch

TLS libraries expect `ca_chain` as `list[str]`, but some charms store it as a single concatenated string.

**Before (buggy):**
```python
ca_chain: Optional[str] = certificate_data.get("ca_chain")
```

**After (fixed):**
```python
ca_chain: Optional[list[str]] = certificate_data.get("ca_chain")
```

### Certificate renewal not triggering config update

When a certificate is renewed, the charm must regenerate config files and restart the workload. Missing this handler causes the workload to use expired certificates.

**How to detect:** Check if `certificate_available` or `certificate_expiring` handlers trigger workload config update.

### Missing certificate revocation cleanup

When TLS is removed, old certificates and keys must be deleted from the workload container. Missing cleanup leaves stale credentials.

---

## Configuration Handling

210 fixes across 79 repos. 6 high severity.

### Truthiness check on config values

Using `if self.config["port"]:` treats port 0 as "not configured". This is the single most pervasive bug pattern across all charm repos.

**Before (buggy):**
```python
port = self.config.get("port")
if port:  # Fails for port 0
    self._configure_port(port)
```

**After (fixed):**
```python
port = self.config.get("port")
if port is not None:
    self._configure_port(port)
```

**Repos affected:** Appears in virtually every team. The Observability team alone fixed this 12+ times.

### Config type mismatch

Config declared as `type: string` in `config.yaml` but used as `int` in Python code (or vice versa).

**How to detect:** Compare `config.yaml` type declarations with how values are used in `src/charm.py`.

### Missing f-string prefix

Format strings missing the `f` prefix produce literal `{variable}` in output.

**Before (buggy):**
```python
logger.info("Connecting to {self.config['host']}:{self.config['port']}")
```

**After (fixed):**
```python
logger.info(f"Connecting to {self.config['host']}:{self.config['port']}")
```

### Boolean from environment variable

`bool(os.getenv('FLAG', ''))` returns True for string "false", "0", "no".

**Before (buggy):**
```python
debug = bool(os.getenv("DEBUG_MODE", ""))
```

**After (fixed):**
```python
debug = os.getenv("DEBUG_MODE", "").lower() in ("true", "1", "yes")
```

---

## Status Management

243 fixes across 79 repos. 14 high severity.

### Status set in wrong handler

Setting `ActiveStatus` in one handler when another subsystem is not ready. Status should reflect the aggregate state of all subsystems.

**Before (buggy):**
```python
def _on_config_changed(self, event):
    self._apply_config()
    self.unit.status = ActiveStatus()
    # But database might not be related yet!
```

**After (fixed):**
```python
def _on_config_changed(self, event):
    self._apply_config()
    self._update_status()

def _update_status(self):
    if not self._database_ready():
        self.unit.status = BlockedStatus("Waiting for database relation")
    elif not self._container_ready():
        self.unit.status = WaitingStatus("Waiting for container")
    else:
        self.unit.status = ActiveStatus()
```

### Missing status on early return

Event handlers that `return` early without setting status leave the charm in the previous status, which may be stale.

**Before (buggy):**
```python
def _on_relation_changed(self, event):
    if not self.unit.is_leader():
        return  # Status unchanged -- may show "Active" when actually waiting
```

**After (fixed):**
```python
def _on_relation_changed(self, event):
    if not self.unit.is_leader():
        self.unit.status = ActiveStatus()  # Or appropriate status for non-leader
        return
```

### Blocked vs Waiting confusion

`BlockedStatus` means user action required. `WaitingStatus` means the charm is waiting for an automatic event (relation, Pebble ready). Using the wrong one misleads operators.

### Contradictory unit vs app status

Setting `BlockedStatus` on the unit but `WaitingStatus` on the app (or vice versa) for the same condition sends mixed signals to operators. `juju status` shows both, and they should agree.

**Before (buggy):**
```python
event.add_status(BlockedStatus("Waiting for MetalLB"))
self.app.status = WaitingStatus("Waiting for MetalLB")  # Contradicts unit!
```

**After (fixed):**
```python
event.add_status(BlockedStatus("Waiting for MetalLB to be enabled"))
self.app.status = BlockedStatus("Waiting for MetalLB to be enabled")
```

**Repos affected:** sdcore-amf-operator.

---

## Ingress and Networking

278 fixes across 46 repos. 10 high severity.

### urljoin path loss

`urllib.parse.urljoin(base, path)` drops the base path if `path` starts with `/`.

**Before (buggy):**
```python
url = urljoin("http://host/api/v1", "/endpoint")
# Result: "http://host/endpoint" -- lost /api/v1
```

**After (fixed):**
```python
url = f"{base_url.rstrip('/')}/{path.lstrip('/')}"
```

### External URL not updated on config change

When `external-hostname` or `site-url` config changes, Pebble env vars and ingress relation data must both be updated. Missing one causes split-brain between what the charm advertises and what the workload uses.

### Hardcoded scheme (http vs https)

Constructing URLs with hardcoded `http://` when TLS may be enabled.

**Before (buggy):**
```python
url = f"http://{self._hostname}:{self._port}"
```

**After (fixed):**
```python
scheme = "https" if self._tls_enabled else "http"
url = f"{scheme}://{self._hostname}:{self._port}"
```

---

## Observability and Grafana

648 fixes across 88 repos. 44 high severity.

### Wrong datasource variable in dashboards

COS uses `${prometheusds}` and `${lokids}` for datasource template variables. Dashboards exported from standalone Grafana use `${DS_PROMETHEUS}` or hardcoded UIDs.

**How to detect:** Search dashboard JSON for `DS_PROMETHEUS`, `$datasource`, or hardcoded `uid` values.

### Wrong rate interval

`$__interval` instead of `$__rate_interval` in `rate()` or `increase()` calls causes under-counting.

**How to detect:** Search dashboard JSON for `$__interval` inside `rate(` or `increase(`.

### Alert expression matches disabled resources

Alert rules with broad label matchers (`{}`) fire for disabled/inactive components.

**How to detect:** Check alert expressions for missing state/status filters.

### Scrape job topology labels

Missing `juju_model`, `juju_application`, or `juju_unit` labels in scrape job metadata breaks COS multi-tenant filtering.

---

## Database Interaction

546 fixes across 41 repos. 41 high severity.

### Connection string not updated on failover

Database charms provide connection info via relations. When the primary changes (failover), the consuming charm must update its connection string. Missing the `relation_changed` handler for this causes connections to the old primary.

### TLS toggle race condition

Enabling/disabling TLS on a database requires coordinated restart. If the charm and database disagree on TLS state, connections fail silently.

**Repos affected:** kafka-operator, mongodb-operator, mysql-k8s-operator, postgresql-k8s-operator.

### Backup during maintenance

Backup operations that don't check for ongoing maintenance or upgrade can produce inconsistent snapshots.

---

## Auth and Identity

204 fixes across 45 repos. 22 high severity.

### Credential logging

Logging passwords, tokens, or secrets in plaintext.

**Before (buggy):**
```python
logger.info("Connecting with password: %s", password)
```

**After (fixed):**
```python
logger.info("Connecting to database (password length: %d)", len(password))
```

### World-readable credential files

Config files containing credentials created with default permissions.

**Before (buggy):**
```python
with open("/etc/app/config.yaml", "w") as f:
    yaml.dump({"password": secret}, f)
```

**After (fixed):**
```python
config_path = Path("/etc/app/config.yaml")
config_path.touch(mode=0o600)
with open(config_path, "w") as f:
    yaml.dump({"password": secret}, f)
```

### Method vs property confusion in auth libraries

Auth library methods that changed from methods to properties (or vice versa) across versions cause AttributeError or return the method object instead of the value.

---

## Upgrade and Migration

54 fixes across 26 repos. 2 high severity.

### Missing pre-upgrade-check

Upgrade handlers that don't verify prerequisites (e.g., all units healthy, backups complete) before proceeding.

### Upgrade not idempotent

Upgrade handlers that fail partway through and can't be safely re-run.

---

## Juju Interaction

314 fixes across 92 repos. 6 high severity.

### Missing leader guard

Writing to app relation data or peer data without checking `self.unit.is_leader()`. Non-leader units get `ModelError` on app data writes.

**Before (buggy):**
```python
def _on_relation_changed(self, event):
    event.relation.data[self.app]["key"] = "value"
```

**After (fixed):**
```python
def _on_relation_changed(self, event):
    if not self.unit.is_leader():
        return
    event.relation.data[self.app]["key"] = "value"
```

### Secret access without owner check

Accessing a secret that the charm doesn't own raises `SecretNotFoundError`.

### Action without fail path

Actions that don't call `event.fail()` on error leave the action hanging until timeout.

### Missing return after event.fail()

Calling `event.fail()` does not stop execution. Without a `return`, the handler continues to the success path, potentially calling `event.set_results()` with None values or logging contradictory success messages.

**Before (buggy):**
```python
def _on_delete_action(self, event):
    if not (result := self._cli.delete(client_id)):
        event.fail("Delete failed")
    # Falls through to success path!
    event.log("Successfully deleted")
    event.set_results({"id": result})  # result is None
```

**After (fixed):**
```python
def _on_delete_action(self, event):
    if not (result := self._cli.delete(client_id)):
        event.fail("Delete failed")
        return
    event.log("Successfully deleted")
    event.set_results({"id": result})
```

**Repos affected:** hydra-operator, and likely other charms with complex action handlers.

### next() without default on data lookups

`next()` without a default argument raises `StopIteration` when no match is found. In generator contexts, this silently terminates iteration rather than raising an error.

**Before (buggy):**
```python
endpoint = next(
    e for e in relation_data.endpoints
    if e.name == "SingleSignOnService"
)  # Raises StopIteration if no match
```

**After (fixed):**
```python
endpoint = next(
    (e for e in relation_data.endpoints
     if e.name == "SingleSignOnService"),
    None,
)
if endpoint is None:
    logger.warning("Expected endpoint not found in relation data")
    return
```

**Repos affected:** discourse-k8s-operator (SAML endpoint lookup).

---

## Exception Handling

Pervasive across all teams. 60% of instances are high severity.

### Narrow except clause

Catching only one exception type when the operation can raise others.

**Before (buggy):**
```python
try:
    result = client.get(Service, name=name, namespace=ns)
except ApiError:
    return None
# TypeError, AttributeError from service without external IP not caught
```

**After (fixed):**
```python
try:
    result = client.get(Service, name=name, namespace=ns)
except (ApiError, TypeError, AttributeError):
    return None
```

### Bare except swallowing errors

`except Exception: pass` hiding real errors that should be logged or propagated.

### Missing exception in loop

An exception in one iteration of a loop kills the entire loop. Subsequent items are never processed.

**Before (buggy):**
```python
for model_name in model_names:
    model = await controller.get_model(model_name)
    status = await model.get_status()  # Failure kills entire loop
```

**After (fixed):**
```python
for model_name in model_names:
    try:
        model = await controller.get_model(model_name)
        status = await model.get_status()
    except Exception as e:
        logger.error("Failed for model %s: %s", model_name, e)
        continue
```

---

## Security

69 fixes across 45+ repos. All high or critical severity.

### Credentials in CLI arguments

Passing passwords as command-line arguments exposes them in `ps` output and `/proc`.

**Before (buggy):**
```python
subprocess.run(["mysql", "-p", password, "-e", query])
```

**After (fixed):**
```python
subprocess.run(["mysql", "-e", query], env={**os.environ, "MYSQL_PWD": password})
```

### Command injection via unsanitized input

Using `os.system()` or `subprocess.run(shell=True)` with user-controlled input.

### Incomplete input validation regex

Using `\w` (includes underscore) or missing anchors (`^`, `$`) in validation patterns.

**Before (buggy):**
```python
if re.match(r'\w+', user_input):  # Passes "valid; rm -rf /"
```

**After (fixed):**
```python
if re.match(r'^[a-zA-Z0-9-]+$', user_input):
```

---

## Logic and Data Flow

### exec() without wait() -- race condition

`container.exec()` returns a Process object. If discarded without calling `.wait()`, the command runs asynchronously and may race with subsequent operations on the same files.

**Before (buggy):**
```python
def _clear_all_configs(self):
    self._container.exec(["find", CONFIG_DIR, "-name", "*.yaml", "-delete"])
    # Immediately push new configs -- racing with the still-running find
    self._container.push(f"{CONFIG_DIR}/new.yaml", content)
```

**After (fixed):**
```python
def _clear_all_configs(self):
    self._container.exec(["find", CONFIG_DIR, "-name", "*.yaml", "-delete"]).wait()
    self._container.push(f"{CONFIG_DIR}/new.yaml", content)
```

**Repos affected:** traefik-k8s-operator (dynamic config cleanup races with config push).

### Status set by helper overwritten by caller

Helper methods that set `BlockedStatus` or `WaitingStatus` and return, but the caller ignores the status and continues processing. The status intended to inform the operator is silently overwritten.

**Before (buggy):**
```python
def _handle_tls(self):
    if not self._is_frontend:
        self.unit.status = BlockedStatus("TLS not supported for this service")
        return  # Returns, but caller keeps going

def _update(self):
    self._handle_tls()  # Sets BlockedStatus and returns, but...
    container.push(config_path, config)  # ...continues anyway
    container.replan()
    self.unit.status = MaintenanceStatus("replanning")  # Overwrites BlockedStatus!
```

**After (fixed):**
```python
def _handle_tls(self) -> bool:
    if not self._is_frontend:
        self.unit.status = BlockedStatus("TLS not supported for this service")
        return False
    return True

def _update(self):
    if not self._handle_tls():
        return  # Stop processing
    container.push(config_path, config)
    container.replan()
```

**Repos affected:** temporal-k8s-operator (_handle_frontend_tls sets BlockedStatus but _update continues).

### Hardcoded string slicing for file extensions

Using `path.name[:N]` with a hardcoded integer to extract the basename from a filename. This only works for basenames of exactly the expected length.

**Before (buggy):**
```python
for path in cert_dir.iterdir():
    hostname = path.name[:5]  # Only correct for 5-char hostnames!
    if hostname not in valid_hosts:
        path.unlink()
```

**After (fixed):**
```python
for path in cert_dir.iterdir():
    hostname = path.name.removesuffix(".cert")
    if hostname not in valid_hosts:
        path.unlink()
```

**Repos affected:** traefik-k8s-operator (certificate cleanup uses hardcoded slices).

### Wrong config key name (silent miss)

Using a config key name that doesn't exist in `config.yaml` / `charmcraft.yaml`. `self.config.get()` silently returns None, and `self.config[]` raises KeyError only at runtime.

**Before (buggy):**
```python
if not allowed_domains_config_is_valid(
    self.config.get("pki_ca_allowed_domains")  # Key doesn't exist!
):  # Validator receives None, returns True, validation bypassed
```

**After (fixed):**
```python
if not allowed_domains_config_is_valid(
    self.config.get("pki_allowed_domains")  # Correct key name
):
```

**Repos affected:** vault-k8s-operator (pki_ca_allowed_domains vs pki_allowed_domains).

### Inverted boolean condition in warning

Boolean condition is inverted relative to its associated warning message. The warning fires on the safe path and is silent on the dangerous path.

**Before (buggy):**
```python
if skip_verify is False:  # Fires when verification is ENABLED
    logger.warning("configured to skip SSL verification")
```

**After (fixed):**
```python
if skip_verify:  # Fires when verification is SKIPPED
    logger.warning("configured to skip SSL verification")
```

**Repos affected:** vault-k8s-operator (S3 client SSL verification warning).

### String comparison of numeric counter values

Relation data values are always strings. Comparing counter or sequence values with `>` / `<` without `int()` conversion does lexicographic comparison, which produces wrong results for multi-digit numbers.

**Before (buggy):**
```python
# get_primary_cluster() -- string comparison
if relation_promoted_cluster_counter > promoted_cluster_counter:
    # "9" > "10" is True lexicographically!
    primary_cluster = relation_cluster_name
```

**After (fixed):**
```python
if int(relation_promoted_cluster_counter) > int(promoted_cluster_counter):
    primary_cluster = relation_cluster_name
```

**Repos affected:** postgresql-k8s-operator (async replication primary selection after 10+ promotions).

### None in f-string URL interpolation

When a property that returns `Optional[str]` is used in an f-string for URL construction, `None` is rendered as the literal string `"None"`.

**Before (buggy):**
```python
api_endpoints = {
    key: f"{self.external_url}{path}"  # external_url can be None
    for key, path in endpoints.items()
}
# Produces: {"query": "None/api/v1/query"}
```

**After (fixed):**
```python
base_url = self.external_url or self._internal_url
api_endpoints = {
    key: f"{base_url}{path}"
    for key, path in endpoints.items()
}
```

**Repos affected:** prometheus-k8s-operator (catalogue API endpoints with None external_url).

### Action handler missing event.fail() on error path

Action handlers that catch exceptions and log errors but don't call `event.fail()` leave the action in a success state with no results, misleading operators and automation.

**Before (buggy):**
```python
def _on_get_primary(self, event: ActionEvent):
    try:
        primary = self._patroni.get_primary()
        event.set_results({"primary": primary})
    except RetryError as e:
        logger.error(f"failed to get primary: {e}")
        # Action completes as "success" with empty results!
```

**After (fixed):**
```python
def _on_get_primary(self, event: ActionEvent):
    try:
        primary = self._patroni.get_primary()
        event.set_results({"primary": primary})
    except RetryError as e:
        event.fail(f"Failed to get primary: {e}")
```

**Repos affected:** postgresql-k8s-operator (get-primary action), indico-operator (add-admin action silently does nothing when container not ready).

### os.path.join for URL construction

Using `os.path.join()` to build URLs works on Linux by coincidence but is semantically wrong. If the second argument starts with `/`, it discards the base URL entirely.

**Before (buggy):**
```python
from os.path import join

redirect_uri = join(
    str(public_url),
    f"self-service/methods/oidc/callback/{provider.id}",
)
```

**After (fixed):**
```python
redirect_uri = f"{str(public_url).rstrip('/')}/self-service/methods/oidc/callback/{provider.id}"
```

**Repos affected:** kratos-operator (OIDC callback URL construction).
