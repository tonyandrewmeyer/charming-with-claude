# Cross-Repository Bug Patterns in Juju Charm Operators

## 1. Executive Summary

This analysis covers **6,116 bug fix commits** across **134 Juju charm repositories** maintained by **10 teams** (MLOps, Data, Observability, IS, Telco, Identity, Commercial Systems, K8s, BootStack, Charm-Tech).

### Severity Distribution
| Severity | Count | Percentage |
|----------|-------|------------|
| Low      | 3,047 | 49.8%      |
| Medium   | 2,840 | 46.4%      |
| High     | 229   | 3.7%       |

### Fix Type Distribution
| Type           | Count | Percentage |
|----------------|-------|------------|
| config         | 2,240 | 36.6%      |
| test-fix       | 1,575 | 25.7%      |
| api-contract   | 540   | 8.8%       |
| edge-case      | 535   | 8.7%       |
| other          | 439   | 7.2%       |
| docs-fix       | 308   | 5.0%       |
| logic-error    | 195   | 3.2%       |
| type-error     | 74    | 1.2%       |
| performance    | 72    | 1.2%       |
| security       | 69    | 1.1%       |
| race-condition | 39    | 0.6%       |
| crash          | 25    | 0.4%       |
| data-loss      | 5     | 0.1%       |

### Top Bug Areas (by fix count)
1. CI/Build (1,111 fixes, 128 repos)
2. Testing (1,062 fixes, 123 repos)
3. Observability (648 fixes, 88 repos)
4. Database (546 fixes, 41 repos)
5. Packaging (446 fixes, 83 repos)
6. Juju Interaction (314 fixes, 92 repos)
7. TLS/Certificates (299 fixes, 67 repos)
8. Ingress/Networking (278 fixes, 46 repos)
9. Status Management (243 fixes, 79 repos)
10. Config Handling (210 fixes, 79 repos)

### Key Finding
**High-severity bugs concentrate in two areas: observability (44) and database (41).** These account for 37% of all high-severity fixes. Security bugs (69 total) are the most common high-severity type, followed by race conditions (39) and config errors (35). The Data team produces the most high-severity bugs (78), driven by TLS lifecycle complexity in Kafka/MongoDB operators.

---

## 2. Universal Patterns (Appearing Across 3+ Teams)

### 2.1. Missing or Incomplete Exception Handling

**Description:** Calls to external services, K8s APIs, Pebble containers, or Juju secrets lack adequate try/except blocks. The charm crashes or enters error state when the remote resource is unavailable, returns unexpected data, or raises an exception type not covered by the except clause.

**Affected repos/teams:** 15+ repos across BootStack, K8s, Data, Identity, Telco, MLOps, Observability
- prometheus-juju-exporter, hardware-observer-operator (BootStack)
- charm-microk8s, cinder-csi-operator (K8s)
- kafka-operator, kafka-k8s-operator (Data)
- glauth-k8s-operator (Identity)
- sdcore-amf-operator (Telco)
- dex-auth-operator (MLOps)

**Severity distribution:** ~60% high, ~40% medium

**Before (buggy):**
```python
# Only catches one exception type; other failures crash the charm
try:
    result = client.get(Service, name=self._service_name, namespace=self._namespace)
except ApiError:
    return None
# Missing: TypeError, AttributeError when service exists but has no external IP
```

```python
# No exception handling at all on Juju model connection
async def collect_metrics(self):
    for model_name in model_names:
        model = await self.controller.get_model(model_name)
        status = await model.get_status()
        # If model is broken, entire collection loop crashes
```

**After (fixed):**
```python
try:
    result = client.get(Service, name=self._service_name, namespace=self._namespace)
except (ApiError, TypeError, AttributeError):
    return None
```

```python
async def collect_metrics(self):
    for model_name in model_names:
        try:
            model = await self.controller.get_model(model_name)
            status = await model.get_status()
        except Exception as e:
            logger.error("Failed to collect from model %s: %s", model_name, e)
            continue  # Other models still collected
```

**What to search for:**
```
grep -rn "client\.\(get\|create\)(Service" --include="*.py"
grep -rn "except ApiError:" --include="*.py"
grep -rn "container\.restart(" --include="*.py"
grep -rn "await self\.controller\.get_model" --include="*.py"
grep -rn "except ValidationError:$" --include="*.py"
```

**Root cause:** Developers handle the "happy path" exception but miss less obvious failure modes. K8s API calls can raise TypeError/AttributeError when resources exist in unexpected states. Juju secrets can raise ModelError, SecretNotFoundError, or TypeError depending on timing.

---

### 2.2. Truthiness vs. Explicit Comparison

**Description:** Using Python truthiness (`if value:`) instead of explicit comparisons (`if value is not None:`), causing 0, empty strings, empty lists, or False to be treated as missing. Also includes treating any non-empty string as True for boolean flags.

**Affected repos/teams:** 8+ repos across Commercial Systems, K8s, Data, IS, Identity
- superset-k8s-operator, temporal-k8s-operator, ranger-k8s-operator (Commercial Systems)
- discourse-k8s-operator (IS)
- kafka-operator (Data)

**Severity distribution:** ~50% high, ~50% medium

**Before (buggy):**
```python
# Zero is a valid value but is falsy in Python
if self.config['max-content-length']:
    superset_config['MAX_CONTENT_LENGTH'] = self.config['max-content-length']
# Bug: max-content-length of 0 is treated as "not set"
```

```python
# Any non-empty string is truthy, including "False"
if relation_data.get('tls') or relation_data.get('tls-external'):
    use_tls = True
# Bug: tls="False" evaluates to True
```

```python
# String truthiness in environment check
if current_env["DISCOURSE_USE_S3"]:
    # Always true for any non-empty string, including "false"
```

**After (fixed):**
```python
if self.config['max-content-length'] is not None:
    superset_config['MAX_CONTENT_LENGTH'] = self.config['max-content-length']
```

```python
if relation_data.get('tls') == 'True':
    use_tls = True
```

```python
if current_env["DISCOURSE_USE_S3"] == "true":
```

**What to search for:**
```
grep -rn "if self\.config\[" --include="*.py" | grep -v "is not None" | grep -v "=="
grep -rn "relation_data\.get(.*) or " --include="*.py"
grep -rn 'bool(os\.getenv' --include="*.py"
```

**Root cause:** Python's truthiness semantics are a footgun for configuration values. Developers use idiomatic `if value:` checks without considering that 0, "", and False are legitimate config values. String-encoded booleans from relation data and environment variables compound the problem.

---

### 2.3. Missing Container/Pebble Readiness Checks

**Description:** Charm code calls `container.push()`, `container.restart()`, `container.replan()`, or other Pebble operations without first verifying the container is connectable via `container.can_connect()`. This causes unhandled exceptions during early lifecycle events.

**Affected repos/teams:** 10+ repos across MLOps, Identity, IS, Data, Telco, Observability
- admission-webhook-operator, dex-auth-operator (MLOps)
- hydra-operator (Identity)
- flask-k8s-operator, discourse-k8s-operator (IS)
- kafka-k8s-operator (Data)
- sdcore-amf-operator (Telco)

**Severity distribution:** ~60% high, ~40% medium

**Before (buggy):**
```python
def _upload_certs_to_container(self):
    container = self.unit.get_container("webhook")
    container.push("/certs/cert.pem", cert_data)
    container.push("/certs/key.pem", key_data)
    # Crashes if container is not yet ready
```

**After (fixed):**
```python
def _upload_certs_to_container(self, event):
    container = self.unit.get_container("webhook")
    if not container.can_connect():
        event.defer()
        return
    container.push("/certs/cert.pem", cert_data)
    container.push("/certs/key.pem", key_data)
```

**What to search for:**
```
grep -rn "container\.push\|container\.restart\|container\.replan\|container\.exec" --include="*.py" | grep -v can_connect
```

**Root cause:** Pebble container readiness is asynchronous. The container may not be connectable during `install`, `config-changed`, or even `pebble-ready` events. Developers assume the container is always available once the charm starts.

---

### 2.4. Grafana Dashboard Datasource Mismatch

**Description:** Grafana dashboard JSON files ship with hardcoded datasource UIDs or non-standard variable names (`${DS_PROMETHEUS}`, `$datasource`, hardcoded hex UIDs) instead of the COS-standard variables (`${prometheusds}`, `${lokids}`). Dashboards show "No data" when deployed through the Juju COS stack.

**Affected repos/teams:** 5+ repos across BootStack, Observability, IS
- hardware-observer-operator (BootStack)
- cos-proxy-operator, alertmanager-k8s-operator (Observability)
- discourse-k8s-operator, flask-k8s-operator (IS)

**Severity distribution:** ~70% high, ~30% medium

**Before (buggy):**
```json
{
  "datasource": {
    "type": "prometheus",
    "uid": "${DS_PROMETHEUS}"
  }
}
```
```json
{
  "datasource": {
    "type": "prometheus",
    "uid": "P4A9D415038E2E9E7"
  }
}
```

**After (fixed):**
```json
{
  "datasource": {
    "type": "prometheus",
    "uid": "${prometheusds}"
  }
}
```

**What to search for:**
```
grep -rn '\${DS_PROMETHEUS}' --include="*.json"
grep -rn '"uid": "\$datasource"' --include="*.json"
grep -rn '"uid": "[A-Z0-9]\{16,\}"' --include="*.json"
grep -rn '\$__interval[^_]' --include="*.json"
```

**Root cause:** Dashboards are copied from upstream Grafana exports or community sources. Grafana exports use local datasource UIDs and `${DS_*}` syntax, but the Juju COS integration requires `${prometheusds}` and `${lokids}`. There is no automated validation for this.

---

### 2.5. TLS Certificate Lifecycle Bugs

**Description:** TLS state management bugs spanning certificate chain ordering, stale TLS flags in relation data, missing cert file checks, failure to reload services after cert changes, and StoredState for cert tracking lost on pod recreation.

**Affected repos/teams:** 12+ repos across Data, Identity, Telco, Observability, BootStack
- kafka-operator, kafka-k8s-operator, mongodb-k8s-operator (Data)
- glauth-k8s-operator, hydra-operator, identity-platform-admin-ui-operator (Identity)
- manual-tls-certificates-operator, sdcore-amf-operator (Telco)
- alertmanager-k8s-operator, catalogue-k8s-operator (Observability)

**Severity distribution:** ~55% high, ~45% medium

**Before (buggy):**
```python
# Checking a relation data flag instead of relation existence
@property
def tls_enabled(self):
    return self.relation_data.get("tls") == "enabled"
# Bug: flag becomes stale when leader is removed
```

```python
# CA chain type mismatch
ca_chain: Optional[str] = certificate.ca_chain
# Bug: cert transfer integration expects Optional[list[str]]
```

```python
# Checking cert object truthiness instead of file existence
if self.server_cert.cert:
    scheme = "https"
# Bug: cert object can be truthy before file is written to disk
```

```python
# Swapped variable names in chain validation
for ca_cert, cert in zip(ca_chain, ca_chain[1:]):
    if not cert_is_signed_by(ca_cert, cert):  # Arguments swapped!
```

**After (fixed):**
```python
@property
def tls_enabled(self):
    relation = self.model.get_relation("certificates")
    return relation is not None and relation.active
```

```python
ca_chain: Optional[list[str]] = certificate.ca_chain.split('\n\n')
```

```python
if self.server_cert.enabled and self.workload.exists(CERT_PATH):
    scheme = "https"
```

```python
for cert, ca_cert in zip(ca_chain, ca_chain[1:]):
    if not cert_is_signed_by(cert, ca_cert):
```

**What to search for:**
```
grep -rn 'relation_data.get("tls").*=="enabled"' --include="*.py"
grep -rn 'ca_chain.*Optional\[str\]' --include="*.py"
grep -rn 'self\.server_cert\.cert' --include="*.py" | grep -v exists
grep -rn 'for.*in zip(ca_chain' --include="*.py"
```

**Root cause:** TLS state is distributed across peer relation data, Juju secrets, certificate relations, and the container filesystem. Each storage mechanism has different lifecycle semantics (relation data is cleared on relation-broken, secrets need refresh=True, files are lost on pod recreation). The lack of a unified TLS state machine means each component can get out of sync.

---

### 2.6. Missing Leader Guard on Leader-Only Operations

**Description:** Operations that should only run on the leader unit (database migrations, secret generation, relation data writes, cluster management) execute on all units, causing race conditions, duplicate operations, or errors on non-leader units.

**Affected repos/teams:** 8+ repos across Commercial Systems, K8s, Identity, Data
- ranger-k8s-operator, temporal-k8s-operator (Commercial Systems)
- charm-microk8s (K8s)
- hydra-operator, identity-platform-admin-ui-operator (Identity)
- kafka-operator (Data)

**Severity distribution:** ~40% high, ~60% medium

**Before (buggy):**
```python
def _on_run_migration_action(self, event):
    # Any unit can trigger migration -- should be leader only
    self._run_database_migration()
```

```python
def _on_config_changed(self, event):
    password = generate_password()
    self._state.truststore_password = password
    # Every unit generates a different password
```

**After (fixed):**
```python
def _on_run_migration_action(self, event):
    if not self.unit.is_leader():
        event.fail("Only the leader unit can run the database migration")
        return
    self._run_database_migration()
```

```python
def _on_config_changed(self, event):
    if self.unit.is_leader():
        password = generate_password()
        self._state.truststore_password = password
```

**What to search for:**
```
grep -rn "def _on_.*action" --include="*.py" -A5 | grep -v is_leader
grep -rn "generate_password\|_state\.\w*password" --include="*.py" | grep -v is_leader
grep -rn "relation_data\[self.app\]" --include="*.py" | grep -v is_leader
```

**Root cause:** Juju dispatches events to all units, but only the leader can write app-level relation data or should perform cluster-wide operations. Developers forget that their handler runs on non-leader units too.

---

### 2.7. Wrong Relation Event Type

**Description:** Using the wrong Juju relation lifecycle event (e.g., `relation-departed` instead of `relation-broken`), or not handling `relation-broken` at all. `departed` fires when any unit leaves but the relation still exists; `broken` fires when the entire relation is removed. Using the wrong one causes premature cleanup or missing cleanup.

**Affected repos/teams:** 7+ repos across K8s, Commercial Systems, Identity, Telco, IS
- charm-microk8s (K8s)
- temporal-k8s-operator (Commercial Systems)
- identity-platform-admin-ui-operator, hydra-operator (Identity)
- sdcore-amf-operator (Telco)

**Severity distribution:** ~60% high, ~40% medium

**Before (buggy):**
```python
# Workers leave cluster on ANY unit departure, not just full relation teardown
self.framework.observe(self.on.microk8s_relation_departed, self._on_leave_cluster)
```

```python
# No handler for relation-broken; charm stays Active with stale endpoints
# (missing handler entirely)
```

**After (fixed):**
```python
self.framework.observe(self.on.microk8s_relation_broken, self._on_leave_cluster)
```

```python
self.framework.observe(self.on.hydra_endpoints_relation_broken, self._on_config_changed)
self.framework.observe(self.on.kratos_info_relation_broken, self._on_config_changed)
```

**What to search for:**
```
grep -rn "relation_departed" --include="*.py" | grep -v test
grep -rn "relation_broken" --include="*.py" # Check: are all critical relations covered?
```

**Root cause:** The Juju event model distinguishes between unit departure and relation removal, but the distinction is subtle. `relation-departed` still has access to relation data; `relation-broken` does not. Choosing the wrong event leads to either premature resource cleanup or orphaned resources.

---

### 2.8. Stale Variable References After Refactoring

**Description:** After renaming a variable, method, class, or event handler, some references still use the old name. Python does not catch this at compile time, so the bug only manifests at runtime.

**Affected repos/teams:** 8+ repos across Charm-Tech, IS, K8s, Commercial Systems, Data
- juju-sdk-tutorial-k8s, test-charms (Charm-Tech)
- flask-k8s-operator (IS)
- charm-microk8s (K8s)
- ranger-k8s-operator (Commercial Systems)
- kafka-operator (Data)

**Severity distribution:** ~30% high, ~70% medium

**Before (buggy):**
```python
def fetch_postgres_relation_data(self):
    for data in relation_data:
        host = val['endpoints']      # 'val' was renamed to 'data'
        user = val['username']       # NameError at runtime
        password = val['password']
```

```python
# Event handler name doesn't match observe() registration
self.framework.observe(self.on.secret_changed, self._on_secret_change)
# But the method is named _on_secret_changed (or vice versa)
```

**After (fixed):**
```python
def fetch_postgres_relation_data(self):
    for data in relation_data:
        host = data['endpoints']
        user = data['username']
        password = data['password']
```

**What to search for:**
```
grep -rn "self\.framework\.observe" --include="*.py"  # Check handler names match methods
```

**Root cause:** Python's dynamic typing means renamed variables compile successfully. Without comprehensive test coverage hitting every code path, stale references survive until runtime. This is especially common with event handler names which may never be directly called in tests.

---

### 2.9. Status Management Anti-Patterns

**Description:** Scattered and inconsistent status-setting logic where status is set in multiple event handlers without centralized computation, leading to stale status, premature ActiveStatus, or status being overwritten by subsequent event handlers.

**Affected repos/teams:** 8+ repos across Data, K8s, Identity, Commercial Systems, Telco
- kafka-operator, kafka-k8s-operator (Data)
- charm-microk8s (K8s)
- hydra-operator (Identity)
- sdcore-amf-operator (Telco)

**Severity distribution:** ~30% high, ~70% medium

**Before (buggy):**
```python
def _on_install(self, event):
    if not kafka_installed:
        event.defer()
        self.unit.status = WaitingStatus("Waiting for Kafka")
        return
    self.unit.status = ActiveStatus()  # Premature: other preconditions not checked

def _on_config_changed(self, event):
    # May overwrite the correct Waiting status from install
    self.unit.status = ActiveStatus()
```

**After (fixed):**
```python
def _get_status(self):
    """Centralized status computation."""
    if not kafka_installed:
        return WaitingStatus("Waiting for Kafka")
    if not self.healthy:
        return BlockedStatus("Kafka unhealthy")
    return ActiveStatus()

def _on_install(self, event):
    self._do_install()
    self.unit.status = self._get_status()

def _on_config_changed(self, event):
    self._do_config()
    self.unit.status = self._get_status()
```

**What to search for:**
```
grep -rn "self\.unit\.status = ActiveStatus" --include="*.py"
grep -rn "self\.unit\.status = " --include="*.py" | sort | uniq -c | sort -rn
```

**Root cause:** Each event handler independently sets status without awareness of the full system state. The correct pattern is either a centralized `_get_status()` method or using `collect_unit_status` / `collect_app_status` events.

---

### 2.10. Incorrect String/Name References (Typos in String Literals)

**Description:** Typos in string constants used as relation data keys, service names, K8s resource keys, environment variable names, or config property names. These are silent errors that only manifest at runtime when the wrong key is read/written.

**Affected repos/teams:** 10+ repos across all teams

**Severity distribution:** ~40% high, ~60% medium

**Before (buggy):**
```python
# Typo: "cluser" instead of "cluster"
if self.relation_data.get("peer-cluser-rotate"):
    # Never True; always returns None

# Wrong service name
for dependent in ["broker", "balancer"]:  # Should be "kafka", not "broker"

# Wrong K8s resource key
resources = {"cpu": "100m", "mem": "200Mi"}  # "mem" is not valid; should be "memory"

# Wrong env var name
db_uri = os.environ.get("MYSQL_DB_CONNECT_URI")  # Charm sets _CONNECT_STRING
```

**After (fixed):**
```python
if self.relation_data.get("peer-cluster-rotate"):

for dependent in ["kafka", "balancer"]:

resources = {"cpu": "100m", "memory": "200Mi"}

db_uri = os.environ.get("MYSQL_DB_CONNECT_STRING")
```

**What to search for:**
```
grep -rn '"mem":' --include="*.py" --include="*.yaml"
grep -rn "peer-cluser" --include="*.py"
grep -rn "CONNECT_URI" --include="*.py"
```

**Root cause:** String-keyed APIs provide no compile-time validation. Typos in dictionary keys, relation data fields, and environment variable names are only caught when the specific code path is exercised at runtime.

---

### 2.11. Missing f-string Prefix

**Description:** Strings containing `{variable}` interpolation braces that lack the `f` prefix, causing literal `{variable_name}` to appear in output instead of the variable's value.

**Affected repos/teams:** 4+ repos across Data, Observability
- kafka-operator, kafka-k8s-operator (Data)

**Severity distribution:** ~80% high, ~20% medium

**Before (buggy):**
```python
# Missing f-prefix: literal "{listener.name}" written to Kafka config
jaas_config = 'oauth.config.id="{listener.name}"'
```

**After (fixed):**
```python
jaas_config = f'oauth.config.id="{listener.name}"'
```

**What to search for:**
```
grep -rn "'{.*self\.\|{listener\.\|{client\.\|{broker\.\|{state\." --include="*.py" | grep -v "^.*f'"
```

**Root cause:** Python does not warn when a non-f-string contains braces with valid identifier names. The string is syntactically valid, so the bug is invisible without runtime testing. Especially dangerous in configuration templates.

---

### 2.12. Unnecessary Service Restarts / Replans

**Description:** The charm unconditionally restarts or replans the workload on every event, even when configuration has not changed. This causes unnecessary downtime, especially for stateful workloads.

**Affected repos/teams:** 5+ repos across Identity, Telco, Data, IS
- glauth-k8s-operator, hydra-operator (Identity)
- sdcore-amf-operator (Telco)
- kafka-k8s-operator (Data)

**Severity distribution:** ~20% high, ~80% medium

**Before (buggy):**
```python
def _on_config_changed(self, event):
    container = self.unit.get_container("app")
    container.add_layer("app", self._pebble_layer, combine=True)
    container.replan()  # Always restarts, even if nothing changed
```

**After (fixed):**
```python
def _on_config_changed(self, event):
    container = self.unit.get_container("app")
    new_layer = self._pebble_layer
    current_plan = container.get_plan()
    if current_plan.services != new_layer["services"]:
        container.add_layer("app", new_layer, combine=True)
        container.replan()
```

**What to search for:**
```
grep -rn "container\.replan()" --include="*.py"
grep -rn "add_layer.*combine=True" --include="*.py"
```

**Root cause:** Developers default to "always reconfigure" for simplicity. Stateless web apps tolerate this, but stateful workloads (databases, message brokers) suffer from unnecessary restarts. The Pebble API does not provide a built-in "replan only if changed" operation.

---

### 2.13. Pebble Plan Mutation Instead of add_layer

**Description:** Code directly mutates the plan object's services dictionary in-place instead of using `container.add_layer()` with `combine=True`. Direct mutation does not persist -- the changes are lost.

**Affected repos/teams:** 3+ repos across IS, MLOps
- flask-k8s-operator (IS)
- Various K8s charms

**Severity distribution:** ~70% high, ~30% medium

**Before (buggy):**
```python
plan = container.get_plan()
plan.services["flask"].environment.update({"DB_URI": db_uri})
# Bug: changes to plan object are NOT persisted to Pebble
```

**After (fixed):**
```python
plan = container.get_plan()
service_dict = plan.services["flask"].to_dict()
service_dict["environment"]["DB_URI"] = db_uri
new_layer = {"services": {"flask": service_dict}}
container.add_layer("flask-db", new_layer, combine=True)
container.replan()
```

**What to search for:**
```
grep -rn "plan\.services\[.*\]\.environment" --include="*.py"
```

**Root cause:** The plan object returned by `get_plan()` looks like a mutable data structure, but modifications to it are not automatically persisted. The API requires explicit `add_layer()` calls.

---

### 2.14. Action API Misuse

**Description:** Charm actions report failures using `event.set_results()` with error fields instead of calling `event.fail()`, or pass wrong argument types to action methods. Juju marks such actions as "completed" even though they failed.

**Affected repos/teams:** 4+ repos across BootStack, IS, Commercial Systems
- charm-apt-mirror (BootStack)
- discourse-k8s-operator (IS)

**Severity distribution:** ~50% high, ~50% medium

**Before (buggy):**
```python
def _on_snapshot_action(self, event):
    if not valid:
        event.set_results({'ReturnCode': 1, 'Stderr': 'Invalid snapshot'})
        return  # Juju still marks this as "completed" (success)
```

```python
event.set_results(email)  # TypeError: expects dict, got str
```

**After (fixed):**
```python
def _on_snapshot_action(self, event):
    if not valid:
        event.fail('Invalid snapshot name')
        return
```

```python
event.set_results({"email": email})
```

**What to search for:**
```
grep -rn "event\.set_results.*ReturnCode\|event\.set_results.*[Ee]rror\|event\.set_results.*[Ff]ail" --include="*.py"
grep -rn "event\.set_results([^{]" --include="*.py"
```

**Root cause:** The ops framework allows `set_results()` with arbitrary dicts, so setting an error field is syntactically valid but semantically wrong. Only `event.fail()` triggers Juju's action failure status.

---

### 2.15. self.charm vs self Attribute Confusion

**Description:** Accessing attributes via `self.charm` when the code is in the charm class itself (should be `self`), or vice versa. Common when code is moved between the charm class and helper/relation objects.

**Affected repos/teams:** 4+ repos across Commercial Systems, K8s, Identity
- ranger-k8s-operator, temporal-worker-k8s-operator (Commercial Systems)
- cinder-csi-operator (K8s)

**Severity distribution:** ~40% high, ~60% medium

**Before (buggy):**
```python
class MyCharm(CharmBase):
    def _on_config_changed(self, event):
        db = self.charm.state.database_connection  # AttributeError: charm class has no self.charm
        # Should be self.state.database_connection
```

**After (fixed):**
```python
class MyCharm(CharmBase):
    def _on_config_changed(self, event):
        db = self.state.database_connection
```

**What to search for:**
```
grep -rn "self\.charm\._state\|self\.charm\.state\." --include="*.py"
```

**Root cause:** When refactoring code from a helper class (where `self.charm` is correct) into the charm class itself, developers forget to remove the `charm.` prefix. The reverse also happens.

---

## 3. Team-Specific Patterns

### 3.1. Data Team

**TLS lifecycle complexity (Kafka):** 10+ TLS-related fixes. TLS state is distributed across peer relation data, secrets, and certificate relations. Internal TLS, client mTLS, and peer-cluster TLS rotation each have independent state machines that interact in subtle ways. The team has been migrating from relation-data flags (`tls=enabled`) to checking relation existence directly.

**Relation data / secrets race conditions:** RuntimeError from mutating dicts during iteration in `RelationState.update()`. Secrets not propagated when broker and controller are related immediately after deployment. Custom secret group classes with `setattr` hacks were brittle.

**Multi-role charm complexity:** Kafka supports broker, balancer, and controller roles in a single codebase. Bugs arise from code running in the wrong role context (e.g., `rebalance` action triggered on non-balancer, client relation data updated from shard role).

**Cross-substrate code sharing:** Kafka VM and K8s variants share code. VM-specific operations (`chown`, `chmod`) fail on K8s. StorageEvent handling has different semantics across substrates.

**Upgrade backward compatibility:** New code expects state not present in previous revisions (missing broker_capacities, missing TLS chain in peer data). Requires explicit `apply_backwards_compatibility_fixes()`.

### 3.2. Identity Team

**Method-vs-property confusion:** `self._workload_service.is_running` (property access, always truthy) instead of `self._workload_service.is_running()` (method call). Appeared in 3 repos (hydra, glauth, admin-ui), suggesting code was copied between charms.

**K8s resource key typo `mem` vs `memory`:** Appeared in 3 repos identically (glauth, hydra, admin-ui). Memory limits silently not applied to pods.

**Config change detection iteration:** The team went through 5+ iterations: no detection -> file comparison -> hash-based StoredState -> remove StoredState (lost on pod recreation) -> read from container directly.

**Pydantic v1/v2 compatibility:** The LDAP library needed extensive compatibility shims. Multiple follow-up fixes for field_serializer, ValidationError API changes. Charm libraries using pydantic face version compatibility issues.

### 3.3. MLOps Team

**Juju storage removal for stateless operations:** admission-webhook and envoy charms removed Juju storage declarations, replacing with direct `container.push()` to hardcoded paths. Storage provisioning delays were a class of bugs.

**Cross-charm K8s resource coordination:** Kubeflow charms share K8s resources (CRDs, Secrets, ConfigMaps) with naming conventions from upstream manifests. Wrong secret names, duplicate CRDs, and missing ConfigMap fields cause silent integration failures.

**Duplicate CRD ownership:** Multiple charms deployed the same CRDs (ScheduledWorkflow, Viewer), causing conflicts during installation and removal.

**Webhook scope too broad:** MutatingWebhookConfiguration used objectSelector with NotIn that could still match system pods. Fixed by switching to namespaceSelector.

### 3.4. Observability Team

**URL construction errors:** The #1 bug source. `urljoin` replaces the entire path if base lacks trailing `/`. Manual URL construction drops ports, mishandles paths, or confuses internal vs external URLs. 7+ URL-related fixes in alertmanager and blackbox-exporter.

**Internal vs external URL confusion:** Behind Traefik, using external URL for internal communication causes redirect loops. Charms must use internal URLs for self-scraping and only expose external URLs to consumers.

**Multi-relation data aggregation:** When iterating over multiple relations of the same interface, `result = process(relation)` overwrites previous results instead of `result.extend(process(relation))`.

**Prometheus relabeling complexity:** Converting Juju topology to Prometheus labels via relabeling rules is error-prone. Nagios host context prefixes contaminate juju_application labels.

### 3.5. K8s Team

**Relation interface naming mismatches:** charm-microk8s underwent multiple interface renames (`microk8s` -> `control_plane`). Event handlers referencing stale names completely broke cluster formation.

**Subprocess call errors:** Wrong function (`check_call` vs `check_output`), wrong binary paths, wrong argument syntax. Hard to catch in unit tests that mock subprocess.

**Filtered-out node lookup on departure:** When a unit departs, hostname looked up from a filtered peer list that already excludes departed units, returning None and silently skipping removal.

### 3.6. Telco Team

**Config type friction:** Juju config types don't map cleanly to Python types. Multiple charms needed explicit type casts between string/int declarations and actual usage.

**K8s API call idempotency:** Using `client.create()` instead of `client.apply()` for services, failing on charm restart when the resource already exists.

**MetalLB dependency:** Charm assumed external LoadBalancer always has an IP, but without MetalLB the IP is never assigned, causing crashes.

### 3.7. BootStack Team

**Hardware monitoring reliability:** False alerts from disabled drives, flapping (for: 0m), missing credential validation for BMC/Redfish, wrong architecture checksums for RAID tools.

**Silent test failures:** Misspelled mock methods (`accept_called` instead of `assert_called`) that silently pass. 10+ test assertions were not checking anything.

**File I/O correctness:** World-readable credential files, buffering issues with `os.fdopen`, incorrect path handling in snapshot operations.

### 3.8. IS Team

**Pebble lifecycle complexity:** Repeated issues with layer updates, service plan mutations, container naming, and exec command construction.

**Build tooling schema churn:** Significant fixes for charmcraft.yaml migration (`metadata.yaml` -> `charmcraft.yaml`, `display-name` -> `title`, `architectures` -> `platforms`).

**Environment variable mismatches:** Variable names set by the charm don't match what the application expects (`_CONNECT_URI` vs `_CONNECT_STRING`).

---

## 4. Severity Analysis

### What Makes Charm Bugs High-Severity?

High-severity bugs share common characteristics:

1. **Silent failures** (42% of high-severity): The charm appears healthy but functionality is broken. Examples: missing f-string prefix writes literal `{variable}` to config; `is_running` property access always returns truthy; truthiness check treats valid-zero as "not set".

2. **Security implications** (30% of high-severity): Credential leaks in logs, world-readable config files with passwords, incorrect certificate chain validation, ACLs not cleaned up on user removal, ReDoS vulnerabilities.

3. **Cascading failures** (18% of high-severity): One broken component takes down the entire system. Examples: one broken Juju model crashes the entire metrics collection loop; wrong relation event causes all workers to leave the cluster.

4. **Unrecoverable states** (10% of high-severity): The charm enters a state that cannot be recovered without manual intervention. Examples: database relation reset to `{}` instead of `{db: None}`, making re-relation impossible; StoredState lost on pod recreation with no config file recovery.

### Areas With Highest Concentration of Critical Bugs

| Area              | High-Severity Count | % of Area Fixes |
|-------------------|--------------------:|----------------:|
| Observability     | 44                  | 6.8%            |
| Database          | 41                  | 7.5%            |
| CI/Build          | 26                  | 2.3%            |
| Auth/Identity     | 22                  | 10.8%           |
| Testing           | 18                  | 1.7%            |
| Status Management | 14                  | 5.8%            |
| TLS/Certificates  | 10                  | 3.3%            |
| Ingress/Networking| 10                  | 3.6%            |

### Top 5 Repos by High-Severity Fixes
1. **opensearch-operator** (25) -- Data team
2. **tempo-k8s-operator** (17) -- Observability
3. **etcd-operator** (12) -- K8s
4. **mysql-k8s-operator** (12) -- Data
5. **postgresql-operator** (10) -- Data

---

## 5. Conventional Commit Adoption

| Team               | Conventional % | Total Commits | Assessment        |
|--------------------|---------------:|:-------------:|-------------------|
| Identity           | 96%            | 649           | Excellent         |
| MLOps              | 88%            | 1,413         | Strong            |
| BootStack          | 85%            | 77            | Strong            |
| Telco              | 84%            | 710           | Strong            |
| IS                 | 83%            | 795           | Strong            |
| Data               | 69%            | 1,224         | Moderate          |
| Observability      | 69%            | 939           | Moderate          |
| Charm-Tech         | 65%            | 20            | Moderate (small N)|
| Commercial Systems | 62%            | 150           | Moderate          |
| K8s                | 35%            | 139           | Low               |

### Impact on Bug Tracking

Teams with high conventional commit adoption (Identity at 96%, MLOps at 88%) have more consistent `fix:` prefixes, making automated bug tracking and classification straightforward. The `fix(area):` pattern allows instant identification of what area was affected.

Teams with lower adoption (K8s at 35%, Commercial Systems at 62%) use freeform messages that require NLP-based classification, introducing noise. The K8s team's low adoption correlates with their repos being older (charm-microk8s has history from 2020) predating conventional commit conventions.

**Recommendation:** Enforce conventional commits via pre-commit hooks. The `fix:`, `feat:`, `chore:` prefixes with optional scope (`fix(tls):`, `fix(status):`) are sufficient for automated analysis.

---

## 6. Temporal Trends

### Bug Fix Volume by Year
| Year | Total Fixes | Top 3 Types                          |
|------|-------------|--------------------------------------|
| 2020 | 101         | config(45), test-fix(15), docs-fix(14)|
| 2021 | 378         | config(157), test-fix(88), api-contract(42)|
| 2022 | 837         | config(274), test-fix(246), api-contract(95)|
| 2023 | 1,563       | config(534), test-fix(426), edge-case(163)|
| 2024 | 1,493       | config(539), test-fix(411), edge-case(137)|
| 2025 | 1,287       | config(523), test-fix(299), edge-case(106)|
| 2026 | 346         | config(151), test-fix(73), api-contract(39)|

### Key Trends

1. **Config bugs dominate and are growing:** Config-type fixes went from 45 (2020) to 539 (2024). This reflects the growing complexity of charm configuration as more integrations and config options are added.

2. **Security awareness increased in 2025:** Security-type fixes jumped from 7 (2024) to 26 (2025), suggesting increased security focus or tooling (CVE scanning, trivy).

3. **Race conditions emerged in 2023:** Race-condition fixes appeared in 2023 (9) and grew to 16 in 2024, correlating with the adoption of more complex multi-unit and multi-relation patterns, especially in Kafka and MongoDB operators.

4. **Edge cases are persistent:** Edge-case fixes have been consistently high since 2022, reflecting the variety of deployment environments (VM vs K8s, with/without ingress, with/without TLS, etc.).

5. **Test fixes track code growth:** Test-fix volume closely tracks overall code growth, peaking at 426 in 2023. This suggests tests are being maintained actively but also breaking frequently.

6. **Data-loss bugs are rare but persistent:** Only 5 total, but they appeared in 2017, 2023, 2024, and 2025, indicating this class of bug is not eliminated by process improvements.

---

## 7. Anti-Pattern Catalogue

### 7.1. Configuration and Types

#### AP-001: Truthiness Check on Config Values
- **Search:** `grep -rn "if self\.config\[" --include="*.py" | grep -v "is not None" | grep -v "=="`
- **Bug:** `if self.config['port']:` treats port 0 as "not set"
- **False positive:** When the value genuinely cannot be 0, empty, or False
- **Fix:** `if self.config['port'] is not None:`

#### AP-002: Missing f-string Prefix
- **Search:** `grep -Prn "(?<!')'{[a-z_]+\." --include="*.py" | grep -v "f'" | grep -v '"""'`
- **Bug:** `'value={self.name}'` produces literal `{self.name}` in output
- **False positive:** Regex patterns, format strings used with `.format()`
- **Fix:** Add `f` prefix: `f'value={self.name}'`

#### AP-003: Boolean from Environment Variable
- **Search:** `grep -rn "bool(os\.getenv" --include="*.py"`
- **Bug:** `bool(os.getenv('FLAG', ''))` returns True for "false", "0", "no"
- **False positive:** None
- **Fix:** `os.getenv('FLAG', '').lower() in ('true', '1', 'yes')`

#### AP-004: Config Type Mismatch
- **Search:** `grep -rn "model\.config\.get\|model\.config\[" --include="*.py"`
- **Bug:** Using config value as int when declared as string, or vice versa
- **False positive:** When type is correctly matched in config.yaml
- **Fix:** Ensure config.yaml type matches code usage; add explicit casts

#### AP-005: None Values in Environment Dicts
- **Search:** `grep -rn "Dict\[str, Optional\[str\]\]" --include="*.py"`
- **Bug:** `{key: value for key, value in data.items()}` passes None values to Pebble env
- **False positive:** When None values are filtered before use
- **Fix:** `{k: v for k, v in data.items() if v is not None}`

### 7.2. Pebble and Container Management

#### AP-006: Missing can_connect() Check
- **Search:** `grep -rn "container\.push\|container\.restart\|container\.replan\|container\.exec" --include="*.py"`
- **Bug:** Pebble operations without checking container readiness
- **False positive:** When wrapped in try/except or preceded by can_connect()
- **Fix:** Add `if not container.can_connect(): event.defer(); return`

#### AP-007: Direct Plan Mutation
- **Search:** `grep -rn "plan\.services\[.*\]\.environment" --include="*.py"`
- **Bug:** Modifying plan object in-place does not persist changes
- **False positive:** When used read-only (e.g., for comparison)
- **Fix:** Create new layer dict and use `container.add_layer(..., combine=True)`

#### AP-008: Unconditional Replan
- **Search:** `grep -rn "container\.replan()" --include="*.py"`
- **Bug:** Replan on every event causes unnecessary service restarts
- **False positive:** When preceded by a plan comparison check
- **Fix:** Compare `plan.services` to new layer before replanning

#### AP-009: Container Name Assumption
- **Search:** `grep -rn "self\.meta\.name.*container\|container_name.*=.*self\.app\.name" --include="*.py"`
- **Bug:** Assuming container name equals charm name
- **False positive:** When they genuinely match
- **Fix:** Read from `self.meta.containers` dynamically

#### AP-010: Missing ChangeError Handling on Restart
- **Search:** `grep -rn "container\.restart(" --include="*.py" | grep -v "except.*ChangeError"`
- **Bug:** Unhandled ChangeError (e.g., HTTP 429) crashes the charm
- **False positive:** When wrapped in try/except
- **Fix:** `try: container.restart(...) except ChangeError as e: ...`

### 7.3. Relations and Events

#### AP-011: relation-departed vs relation-broken
- **Search:** `grep -rn "relation_departed" --include="*.py" | grep -v test`
- **Bug:** Using departed for cleanup that should happen on broken
- **False positive:** When departed is intentionally used (e.g., scaling logic)
- **Fix:** Use `relation_broken` for full relation teardown cleanup

#### AP-012: Missing relation-broken Handler
- **Search:** Compare `grep -rn "relation_joined\|relation_changed" --include="*.py"` against `grep -rn "relation_broken" --include="*.py"` for each relation
- **Bug:** No cleanup when critical relations are removed
- **False positive:** When the relation is purely informational
- **Fix:** Add `relation_broken` handler that transitions to BlockedStatus

#### AP-013: Relation Data Overwrite in Loop
- **Search:** `grep -rn "for.*relation.*in.*self\.model\.relations" --include="*.py" -A2 | grep "= self\._process\|= self\._get"`
- **Bug:** `result = process(relation)` inside loop overwrites previous results
- **False positive:** When only one relation is expected
- **Fix:** `result.extend(process(relation))`

#### AP-014: event.relation.app is None
- **Search:** `grep -rn "event\.relation\.app\." --include="*.py" | grep -v "app is None\|app is not None"`
- **Bug:** Accessing app data without null check causes AttributeError
- **False positive:** When in an event where app is guaranteed non-None
- **Fix:** `if event.relation.app is None: event.defer(); return`

#### AP-015: Missing Leader Guard
- **Search:** Compare `grep -rn "def _on_.*action" --include="*.py"` with `grep -rn "is_leader" --include="*.py"`
- **Bug:** Leader-only operations run on all units
- **False positive:** When the operation is intentionally for all units
- **Fix:** `if not self.unit.is_leader(): event.fail("Leader only"); return`

### 7.4. TLS and Security

#### AP-016: Relation Data TLS Flag Instead of Relation Check
- **Search:** `grep -rn "relation_data.*tls.*enabled\|relation_data.*mtls" --include="*.py"`
- **Bug:** TLS flags in relation data become stale when leader changes
- **False positive:** None observed
- **Fix:** Check relation existence: `self.model.get_relation("certificates") is not None`

#### AP-017: CA Chain Type Mismatch
- **Search:** `grep -rn "ca_chain.*Optional\[str\]" --include="*.py"`
- **Bug:** String instead of list[str] for CA chain
- **False positive:** When the consumer expects a concatenated string
- **Fix:** `ca_chain: Optional[list[str]]`

#### AP-018: Credential Logging
- **Search:** `grep -rn "logger\.\(info\|debug\).*password\|logger\.\(info\|debug\).*secret\|logger\.\(info\|debug\).*credential\|logger\.\(info\|debug\).*token" --include="*.py"`
- **Bug:** Passwords/secrets logged in plaintext
- **False positive:** When logging the key name, not the value
- **Fix:** Remove the log statement or mask the value

#### AP-019: World-Readable Credential Files
- **Search:** `grep -rn "open(.*'w'.*encoding" --include="*.py" | grep -v chmod | grep -v "0o600\|0o640"`
- **Bug:** Config files with credentials created with default permissions
- **False positive:** When the file contains no sensitive data
- **Fix:** `path.touch(mode=0o600)` before writing, or `os.chmod(path, 0o600)` after

#### AP-020: Incomplete Input Validation Regex
- **Search:** `grep -rn "re\.match.*\\\\w" --include="*.py"`
- **Bug:** `\w` includes underscore; missing anchors allow partial matches
- **False positive:** When underscore is intentionally allowed
- **Fix:** Use explicit character classes with `^` and `$` anchors

#### AP-021: ReDoS Vulnerable Regex
- **Search:** `grep -Prn "re\.(match|search)\(.*\(.+\+\).+\+" --include="*.py"`
- **Bug:** Nested quantifiers allow catastrophic backtracking
- **False positive:** Simple non-nested patterns
- **Fix:** Split input and validate parts individually, or use non-backtracking patterns

### 7.5. Grafana and Observability

#### AP-022: Wrong Datasource Variable
- **Search:** `grep -rn '\${DS_PROMETHEUS}\|\$datasource' --include="*.json"`
- **Bug:** Dashboard uses non-COS-standard datasource variable
- **False positive:** None in COS context
- **Fix:** Replace with `${prometheusds}` or `${lokids}`

#### AP-023: Hardcoded Datasource UID
- **Search:** `grep -Prn '"uid":\s*"[A-Z0-9]{16,}"' --include="*.json"`
- **Bug:** Dashboard uses local datasource UID instead of template variable
- **False positive:** None
- **Fix:** Replace with `${prometheusds}`

#### AP-024: Wrong Rate Interval
- **Search:** `grep -rn '\$__interval[^_]' --include="*.json"`
- **Bug:** `$__interval` instead of `$__rate_interval` in `rate()` calls
- **False positive:** When used outside of `rate()` or `increase()`
- **Fix:** Use `$__rate_interval`

#### AP-025: Overly Broad Alert Expression
- **Search:** `grep -rn "expr:.*{[^}]*}.*> 0\|for: 0m" --include="*.yaml" --include="*.py"`
- **Bug:** Alert matches disabled/inactive resources; `for: 0m` triggers on flapping
- **False positive:** When broad matching is intentional
- **Fix:** Add state/status filters; increase `for:` duration

### 7.6. URL and Network

#### AP-026: urljoin Path Loss
- **Search:** `grep -rn "urljoin" --include="*.py"`
- **Bug:** `urljoin("http://host/base", "/api")` discards `/base`
- **False positive:** When the base URL has trailing `/` and path has no leading `/`
- **Fix:** Ensure base ends with `/` and path does not start with `/`

#### AP-027: Missing Port in Address
- **Search:** `grep -rn "external_url\.hostname[^}]" --include="*.py"`
- **Bug:** Using only hostname without port for scrape targets
- **False positive:** When port is default (80/443)
- **Fix:** Include port: `f"{hostname}:{port}"`

#### AP-028: Internal vs External URL Confusion
- **Search:** `grep -rn "web_external_url=self\._external_url" --include="*.py"`
- **Bug:** Using external URL for internal communication causes redirect loops behind ingress
- **False positive:** When there is no ingress
- **Fix:** Use internal URL for self-communication; external URL only for consumers

### 7.7. Testing

#### AP-029: Misspelled Mock Assertions
- **Search:** `grep -rn "accept_called\|accept_not_called\|accept_called_with" --include="*.py"`
- **Bug:** `mock.accept_called()` is not a real method; silently does nothing
- **False positive:** None
- **Fix:** Use `mock.assert_called()`, `mock.assert_not_called()`, etc.

#### AP-030: Assert with Comma Instead of Equality
- **Search:** `grep -rn "assert .*,\s*\w*Status(" --include="*.py"`
- **Bug:** `assert status, ActiveStatus()` is a tuple (always truthy), not a comparison
- **False positive:** When the comma is intentionally providing an assertion message
- **Fix:** `assert status == ActiveStatus()`

#### AP-031: Asserting Input State Instead of Output
- **Search:** `grep -rn "ctx\.run" --include="*.py" -A5 | grep "assert container\." | grep -v "state_out"`
- **Bug:** Scenario tests check input container object instead of `state_out.get_container()`
- **False positive:** When intentionally checking input state
- **Fix:** `state_out = ctx.run(...); assert state_out.get_container(name)...`

#### AP-032: asyncio.gather with Deploy and Wait
- **Search:** `grep -rn "asyncio\.gather.*model\.deploy" --include="*.py"`
- **Bug:** `gather(deploy(), wait_for_idle())` races -- wait may start before deploy registers
- **False positive:** None
- **Fix:** Sequential: `await deploy()` then `await wait_for_idle()`

#### AP-033: Missing trust=True in Integration Tests
- **Search:** `grep -rn "model\.deploy(" --include="*.py" | grep "channel=" | grep -v "trust"`
- **Bug:** Charms requiring RBAC permissions deployed without `trust=True`
- **False positive:** When the charm does not need trust
- **Fix:** Add `trust=True` to deploy calls for charms that manage K8s resources

### 7.8. Kubernetes Resources

#### AP-034: create() vs apply() for K8s Resources
- **Search:** `grep -rn "client\.create(" --include="*.py"`
- **Bug:** `create()` fails if resource exists; not idempotent across charm restarts
- **False positive:** When the resource is guaranteed to not exist
- **Fix:** Use `client.apply(resource, field_manager="charm-name")`

#### AP-035: K8s Memory Resource Key Typo
- **Search:** `grep -rn '"mem":' --include="*.py" --include="*.yaml"`
- **Bug:** `"mem"` is not a valid K8s resource name; silently ignored
- **False positive:** None in K8s context
- **Fix:** Use `"memory"`

#### AP-036: Container Image Tag + Digest
- **Search:** `grep -rn "upstream-source:.*:.*@sha256:" --include="*.yaml"`
- **Bug:** Combining both tag and digest in OCI reference is invalid for some runtimes
- **False positive:** None
- **Fix:** Use digest only: `image@sha256:...`

### 7.9. Build and Packaging

#### AP-037: Missing Build Packages for Native Deps
- **Search:** `grep -rn "build-packages" charmcraft.yaml` (check if present when native deps are used)
- **Bug:** `charmcraft pack` fails in clean environment when Python packages need C/Rust compilation
- **False positive:** When all deps are pure Python
- **Fix:** Add `parts.charm.build-packages` with required native build dependencies

#### AP-038: Deprecated charmcraft.yaml Schema
- **Search:** `grep -rn "display-name:\|^architectures:" charmcraft.yaml`
- **Bug:** Old schema keys rejected by newer charmcraft versions
- **False positive:** None
- **Fix:** Migrate to current schema (`title`, `platforms`, `links`)

### 7.10. Charm Library and Framework

#### AP-039: StoredState for K8s Charms
- **Search:** `grep -rn "_stored = StoredState" --include="*.py"`
- **Bug:** StoredState is lost on pod recreation, causing state tracking to reset
- **False positive:** When StoredState is used for truly ephemeral data
- **Fix:** Read actual state from the container/workload instead of tracking in StoredState

#### AP-040: Wrong Import Path After Charm Rename
- **Search:** `grep -rn "from charms\." --include="*.py"` and compare with actual lib directory
- **Bug:** Import references old charm name after rename
- **False positive:** None
- **Fix:** Update all imports and move library files to match new charm name

#### AP-041: Deprecated open_port vs set_ports
- **Search:** `grep -rn "open_port(protocol=" --include="*.py"`
- **Bug:** `open_port()` does not clean up stale ports
- **False positive:** None
- **Fix:** Use `self.unit.set_ports(port)` (declarative, handles cleanup)

#### AP-042: Event Base Class Mismatch
- **Search:** `grep -rn "class.*Event(RelationEvent)" --include="*.py" | grep -v "snapshot"`
- **Bug:** Custom events extending RelationEvent without implementing snapshot/restore
- **False positive:** When default RelationEvent serialization is sufficient
- **Fix:** Use EventBase with custom `__init__`, `snapshot()`, and `restore()` methods

#### AP-043: Dict Mutation During Iteration
- **Search:** `grep -rn "for.*in.*dict.*:.*\.pop\|for.*in.*:.*\.pop(" --include="*.py"`
- **Bug:** Modifying dict while iterating causes RuntimeError
- **False positive:** When iterating over a copy
- **Fix:** Iterate over `.items()` or a copy of the keys

---

*This document was generated from analysis of 6,116 bug fix commits across 134 Juju charm repositories. It serves as the foundation for automated bug detection tooling.*
