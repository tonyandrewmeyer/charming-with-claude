# Gold-Standard Answers

These answers were sourced from the built documentation output on 2026-03-26, and were carefully reviewed by me (Tony).
They serve as the reference against which agent responses are scored.

---

## Q1: What parameters does `Container.add_layer` accept and what does each do?

**Signature:**
```python
add_layer(label: str, layer: str | LayerDict | Layer, *, combine: bool = False)
```

**Parameters:**

1. **`label`** (`str`) — Label for the new layer (and label of the layer to merge with if combining).

2. **`layer`** (`str | LayerDict | Layer`) — A YAML string, configuration layer dict, or `pebble.Layer` object containing the Pebble layer to add.

3. **`combine`** (`bool`, keyword-only, default `False`) — If `False` (the default), append the new layer as the top layer with the given label (must be unique). If `True` and the label already exists, the two layers are combined into a single one considering the layer override rules; if the layer doesn't exist, it is added as usual.

**Key fact:** Dynamically adds a new layer onto the Pebble configuration layers.

**Source:** ops API reference — `Container` class.

---

## Q2: How do you access relation data for a specific remote unit? Show the code.

Use the `.data` attribute on the `Relation` object, indexing by the unit whose data you want.

**Access the specific remote unit that triggered the event:**
```python
def _on_database_relation_changed(self, event: ops.RelationChangedEvent):
    remote_unit_data = event.relation.data[event.unit]
```

**Access all remote unit databags:**
```python
def _on_database_relation_changed(self, event: ops.RelationChangedEvent):
    remote_units_databags = {
        event.relation.data[unit]
        for unit in event.relation.units
        if unit.app is not self.app
    }
```

**Access the remote app (leader) databag:**
```python
remote_app_databag = event.relation.data[event.relation.app]
```

**Access local app and unit databags:**
```python
local_app_databag = event.relation.data[self.app]
local_unit_databag = event.relation.data[self.unit]
```

**Valid alternative, using Relation.load:**
```python
@dataclasses.dataclass
class MyData:
    foo: str
    bar: int

data = event.relation.load(MyData, event.app)
print(data.foo)
```

**Key facts:**
- `event.relation.data` is keyed by `Unit` or `Application` objects.
- `event.unit` is the specific remote unit that triggered the event.
- `event.relation.units` contains all remote units in the relation.
- Remote app databag is read-only; local app databag is writable only on the leader.
- Databags behave like dictionaries with string keys and string values.
- Pydantic models or standard library dataclasses can be used with `Relation.load` to get an onjeft representation.

**Source:** ops how-to guide — "Manage relations".

---

## Q3: What is the full list of hook events a charm can observe?

### Static events (on `CharmEvents` / `self.on`):

1. **`install`** — Charm is installed (`InstallEvent`)
2. **`start`** — Immediately after first configuration change (`StartEvent`)
3. **`stop`** — Charm is shut down (`StopEvent`)
4. **`remove`** — Unit is about to be terminated (`RemoveEvent`)
5. **`config_changed`** — Configuration change occurs (`ConfigChangedEvent`)
6. **`upgrade_charm`** — Request to upgrade the charm (`UpgradeCharmEvent`)
7. **`leader_elected`** — New leader has been elected (`LeaderElectedEvent`)
8. **`leader_settings_changed`** — Leader changes settings (`LeaderSettingsChangedEvent`) *[deprecated since 2.4.0]*
9. **`update_status`** — Periodic status update request from Juju (`UpdateStatusEvent`)
10. **`collect_app_status`** — Leader-only, end of every hook, collects app statuses (`CollectStatusEvent`)
11. **`collect_unit_status`** — Every unit, end of every hook, collects unit statuses (`CollectStatusEvent`)
12. **`collect_metrics`** — Juju metric collection (`CollectMetricsEvent`) *[deprecated]*
13. **`secret_changed`** — Secret owner changed contents (`SecretChangedEvent`) *[Juju 3.0+]*
14. **`secret_expired`** — Secret expiration time elapsed (`SecretExpiredEvent`) *[Juju 3.0+]*
15. **`secret_remove`** — Secret revision can be removed (`SecretRemoveEvent`) *[Juju 3.0+]*
16. **`secret_rotate`** — Secret rotation policy elapsed (`SecretRotateEvent`) *[Juju 3.0+]*
17. **`pre_series_upgrade`** / **`post_series_upgrade`** — Series upgrade lifecycle *[deprecated, removal in Juju 4.0]*

### Dynamically-named events (based on charm metadata):

**Relation events** (per endpoint `<name>`):
- `<name>_relation_created` (`RelationCreatedEvent`)
- `<name>_relation_joined` (`RelationJoinedEvent`)
- `<name>_relation_changed` (`RelationChangedEvent`)
- `<name>_relation_departed` (`RelationDepartedEvent`)
- `<name>_relation_broken` (`RelationBrokenEvent`)

**Storage events** (per storage `<name>`):
- `<name>_storage_attached` (`StorageAttachedEvent`)
- `<name>_storage_detaching` (`StorageDetachingEvent`)

**Container/Pebble events** (per container `<name>`):
- `<name>_pebble_ready` (`PebbleReadyEvent`)
- `<name>_pebble_custom_notice` (`PebbleCustomNoticeEvent`)
- `<name>_pebble_check_failed` (`PebbleCheckFailedEvent`)
- `<name>_pebble_check_recovered` (`PebbleCheckRecoveredEvent`)

**Action events** (per action `<name>`):
- `<name>_action` (`ActionEvent`)

**Source:** ops API reference — `CharmEvents` class and event class definitions.

---

## Q4: What's the difference between `ActionEvent.fail()` and raising an exception in an action handler?

**`ActionEvent.fail(message: str = '')`:**
- Reports that the action has failed with an optional message.
- **Does not interrupt code execution** — typically followed by a `return`.
- The failure message is sent back to the administrator who invoked the action.
- The action's status is set to "failed" with the message visible to the user.
- This is the **controlled, graceful** way to report action failure.

**Raising an exception:**
- An unhandled exception causes the charm to **crash and enter the error state**.
- Puts the entire unit into error state (not just the action).
- The user must use `juju resolve` to recover.
- Error details are only in the Juju log, not in the action output.

**Summary:** `event.fail()` is a graceful, controlled failure that reports a message to the user and lets you clean up; raising an exception is an uncontrolled crash that puts the entire unit into error state and requires manual intervention.

**Source:** ops API reference (`ActionEvent.fail`) and ops how-to guide ("Write and structure charm code").

---

## Q5: How do you use `ops.CollectStatusEvent` to set charm status? Show a complete example.

`CollectStatusEvent` is triggered at the end of every hook. The framework automatically picks the highest-priority status from all statuses added via `add_status()`.

**Priority order** (highest to lowest): `error` > `blocked` > `maintenance` > `waiting` > `active`

It is an error to call `add_status()` with `ErrorStatus` or `UnknownStatus`.

**Complete example:**
```python
class MyCharm(ops.CharmBase):
    def __init__(self, framework: ops.Framework):
        super().__init__(framework)
        framework.observe(self.on.collect_app_status, self._on_collect_app_status)
        framework.observe(self.on.collect_unit_status, self._on_collect_unit_status)

    def _on_collect_app_status(self, event: ops.CollectStatusEvent):
        # Triggered for the leader unit only.
        num_degraded = ...  # inspect peer databags
        if num_degraded:
            event.add_status(ops.ActiveStatus(f'degraded units: {num_degraded}'))
            return
        event.add_status(ops.ActiveStatus())

    def _on_collect_unit_status(self, event: ops.CollectStatusEvent):
        # Triggered for each unit.
        if not self.model.config.get('port'):
            event.add_status(ops.BlockedStatus('please set "port" config'))
            return
        event.add_status(ops.ActiveStatus())
```

**Key behaviours:**
- `collect_unit_status` fires for every unit after every hook.
- `collect_app_status` fires only on the leader unit.
- Multiple `add_status()` calls are allowed; ops picks the highest priority.
- Multiple handlers can observe the same event (e.g., component-based pattern).

**Source:** ops API reference (`CollectStatusEvent`) and ops how-to guide ("Write and structure charm code").

---

## Q6: Write a complete Pebble layer YAML that defines a service with an HTTP health check, custom environment variables, and a log target.

```yaml
summary: Example layer with service, health check, env vars, and log target

services:
    my-webapp:
        override: replace
        command: /usr/bin/my-webapp --port 8080
        startup: enabled
        environment:
            APP_ENV: production
            DB_HOST: localhost
            DB_PORT: "5432"
            LOG_LEVEL: info
        on-check-failure:
            http-check: restart

checks:
    http-check:
        override: replace
        level: ready
        period: 10s
        timeout: 3s
        threshold: 3
        http:
            url: http://localhost:8080/health
            headers:
                Accept: application/json

log-targets:
    my-loki:
        override: replace
        type: loki
        location: http://loki-host:3100/loki/api/v1/push
        services: [my-webapp]
        labels:
            env: production
```

**Key facts:**
- **Services:** `override` is required (`merge` or `replace`). `command` is required. `startup` defaults to `disabled`.
- **Checks:** Only one of `http`, `tcp`, or `exec` may be specified. HTTP check succeeds on 2xx status. `level` can be `alive` or `ready` (maps to K8s liveness/readiness probes) or not included (meaning it does not contribute to K8s probes but can be queried or used by Pebble). `period` defaults to 10s, `timeout` to 3s, `threshold` to 3.
- **Log targets:** `type` can be `loki`, `opentelemetry`, or `syslog`. For Loki, `location` must include the full push API URL. Pebble automatically adds a `pebble_service` label. Custom `labels` values may contain `$ENV_VARS`.
- **Linking checks to services:** Use `on-check-failure` in the service, mapping check names to actions (`restart`, `shutdown`, `success-shutdown`, `ignore`).

**Source:** Pebble reference — "Layer specification".

---

## Q7: How do Pebble notices work? What types are there and how does a charm observe them via ops?

**What notices are:** A subsystem for introspection of events in Pebble. Notices are saved to disk (persist across restarts) and expire after a defined interval.

**Identity and deduplication:** Each notice is uniquely identified by (user ID, type, key). Repeated occurrences increment a counter rather than creating new notices.

**Notice types:**

1. **`change-update`** — Recorded when a change is spawned or its status is updated. Key = change ID. Data includes the change `kind`.
2. **`custom`** — Client-reported via `pebble notify`. Key must be in `example.com/path` format. Key and data are user-provided.
3. **`warning`** — Pebble warnings. Key = human-readable warning message. Not relevant in a charming context.

**How a charm observes notices via ops:**
- When Pebble emits a `custom` notice, Juju detects it and dispatches a `pebble_custom_notice` event.
- The charm observes it with `self.on['<container>'].pebble_custom_notice`.
- The event object provides the notice's type, key, and data.

**API:** `GET /v1/notices` supports filtering by `types`, `keys`, `user-id`, `after` timestamp, and a `timeout` parameter for long-polling.

**CLI:** `pebble notices` (list), `pebble notice <id>` (get one), `pebble notify <key>` (record custom notice).

**Source:** Pebble reference — "Notices".

---

## Q8: What is the Pebble change/task model? How do you check if a long-running operation has completed?

**The model:** When Pebble performs a potentially long-running operation (starting/stopping services, etc.), it records a **change** containing one or more **tasks**. State is persisted to `$PEBBLE/.pebble.state`.

**Change structure:**
- `id`, `kind`, `summary`, `status`, `ready` (bool), `spawn-time`, `ready-time`
- `tasks`: array of task objects, each with `id`, `kind`, `summary`, `status`, `progress` (with `done`/`total` counters)

**How to check completion:**

1. **CLI:** `pebble changes` lists recent changes. `pebble tasks <change-id>` shows tasks within a change.
2. **API polling:** `GET /v1/changes/{id}` — check the `ready` boolean.
3. **API blocking wait:** `GET /v1/changes/{id}/wait` — blocks until change finishes. Accepts optional `timeout` query parameter.
4. **API filtering:** `GET /v1/changes?select=in-progress` — filter by state (`all`, `in-progress`, `ready`).
5. **Notices:** A `change-update` notice fires when a change is spawned or updated. Long-poll with `GET /v1/notices?types=change-update&timeout=30s`.
6. **Python client (ops):** Methods like `client.stop_services()` automatically wait for the change to finish.

**Source:** Pebble reference — "Changes and tasks".

---

## Q9: How do you configure Pebble log forwarding to Loki? Show the layer YAML and explain the protocol options.

**Layer YAML:**
```yaml
log-targets:
    my-loki-target:
        override: replace
        type: loki
        location: http://loki-host:3100/loki/api/v1/push
        services: [all]
        labels:
            env: production
            owner: user-$OWNER
```

**Required fields:** `override` (`merge` or `replace`), `type` (`loki`), `location` (full Loki push API URL).

**Optional fields:** `services` (list of service names or `all`), `labels` (key/value pairs, values may contain `$ENV_VARS`).

**Protocol options (the `type` field):**

| Type | Protocol | Location Format | Auto Label |
|---|---|---|---|
| `loki` | Grafana Loki | `http://<host>:3100/loki/api/v1/push` | `pebble_service` |
| `opentelemetry` | OTLP | `http://<host>:4318` (port only, no path) | `service.name` |
| `syslog` | Syslog (RFC 5424) | `tcp://<host>:<port>` or `udp://<host>:<port>` | APP-NAME field, SD-ID `pebble@28978` |

**Multiple targets** can be defined simultaneously to forward to different systems:
```yaml
log-targets:
    test:
        override: merge
        type: loki
        location: http://test-loki:3100/loki/api/v1/push
        services: [svc1, svc2]
    staging:
        override: merge
        type: loki
        location: http://staging-loki:3100/loki/api/v1/push
        services: [svc3, svc4]
```

**Source:** Pebble reference — "Log forwarding" and "Layer specification".

---

## Q10: How do you deploy a charm and wait for it to reach active/idle using jubilant? Show complete test code.

```python
import pytest
import jubilant


@pytest.fixture(scope='module')
def juju():
    with jubilant.temp_model() as juju:
        yield juju


def test_deploy(juju: jubilant.Juju):
    juju.deploy('my-charm')
    juju.wait(jubilant.all_active)
```

**To wait for both active and idle:**
```python
juju.wait(lambda status: jubilant.all_active(status) and jubilant.all_agents_idle(status))
```

**Key facts:**
- `jubilant.temp_model()` creates a randomly-named model and destroys it on exit.
- `juju.deploy()` takes a Charmhub name or a path to a `.charm` file (must start with `/` or `.`).
- `juju.wait(ready, error=..., timeout=..., successes=3)` polls `juju status`. The `ready` callable must return `True` for `successes` times in a row (default 3).
- `jubilant.all_active` checks all apps and all units have "active" status. Can filter by app name: `jubilant.all_active(status, 'my-app')`.
- `jubilant.all_agents_idle` checks that all unit agents are "idle".
- `error=jubilant.any_error` raises `WaitError` if any unit enters error state.

**Source:** jubilant tutorial ("Getting started") and API reference.

---

## Q11: How do you add a relation between two applications and verify data was exchanged, using jubilant?

**Adding a relation:**
```python
juju.integrate('app1', 'app2')
juju.wait(lambda status: jubilant.all_active(status, 'app1', 'app2'))
```

**Key facts:**
- `juju.integrate(app1, app2)` creates a relation. Each argument can be `<app>[:<endpoint>]`.
- `juju.remove_relation(app1, app2)` removes a relation.
- `via` parameter available for cross-model relations.

**Verifying data was exchanged:**

1. **Check relation exists via status:** `status.apps['myapp'].relations` is a `dict[str, list[AppStatusRelation]]` where each `AppStatusRelation` has `related_app`, `interface`, and `scope`.

2. **Wait for active status:** Charms typically go active only after receiving required relation data, so waiting for active implicitly confirms data exchange. This should not be relied on without specific knowledge that the interface works this way.

3. **Use actions:** Many charms expose actions (e.g., `get-password`) to retrieve data set via relations.

4. **CLI fallback:** `juju.cli('show-unit', 'myapp/0', '--format=json')` for raw relation data.

**Source:** jubilant API reference and tutorial.

---

## Q12: How do you run a Juju action on a unit and check its results using jubilant?

```python
result = juju.run('mysql/0', 'get-password')
assert result.results['username'] == 'USER0'
```

**Signature:** `juju.run(unit, action, params=None, wait=None) -> Task`
- `unit`: e.g., `mysql/0` or `mysql/leader`
- `action`: action name string
- `params`: optional `Mapping[str, Any]`
- `wait`: optional timeout in seconds (Juju default 60s)

**`Task` attributes:**
- `results`: `dict[str, Any]` — results from the charm (excludes `return-code`, `stdout`, `stderr`)
- `status`: `'aborted'`, `'cancelled'`, `'completed'`, `'error'`, or `'failed'`
- `success`: `bool` — whether the action succeeded
- `message`: failure message (if charm called `event.fail(message)`)
- `return_code`: `int` (default 0)
- `stdout` / `stderr`: strings
- `log`: `list[str]` of messages logged during the action
- `id`: task ID string

**Error handling:** `juju.run()` raises `TaskError` if the action failed, `ValueError` if the action/unit doesn't exist, `TimeoutError` if wait exceeded.

**Source:** jubilant API reference.

---

## Q13: How do you use the ingress library to provide ingress to your charm? Show the requires side.

The `ingress` interface (v1/v2) uses a provider/requirer pattern. The recommended library is `charms.traefik_k8s.v1.ingress` from the traefik-k8s-operator.

**What the requirer must provide (v2 schema):**

Application databag:
```yaml
application-data:
  name: '"app_name"'
  model: '"model_name"'
  port: '4242'
```

Unit databag:
```yaml
unit-data:
  host: '"hostname"'
```

The provider then publishes the ingress URL with default structure: `http://[ingress-hostname]:[port]/[model]-[unit]/`

**Note:** The charmlibs documentation covers interface specifications (data schemas and behavioural contracts) rather than library Python API. The actual library API (e.g., `IngressPerAppRequirer` class) is documented in the traefik-k8s-operator repository.

**Source:** charmlibs reference — "ingress" interface v2.

---

## Q14: What events does the TLS certificates library emit, and when should a charm request a new certificate?

The `tls-certificates` interface (v1) library is `charmlibs-interfaces-tls-certificates`. Install: `uv add 'charmlibs-interfaces-tls-certificates~=1.0'`. Import: `from charmlibs.interfaces import tls_certificates`.

**Interface contract (from the specification):**

Requirer:
- Must generate (or reuse) a private key
- Must provide a list of CSRs (Certificate Signing Requests)
- Must specify whether the request is for a CA
- Must use the appropriate databag (unit or application)
- Must **stop using a certificate when revoked by the Provider**

Provider:
- Provides CA certificate, CA chain, and certificate per processed CSR
- Reports errors in `request_errors` for CSRs that couldn't be processed

**When to request a new certificate:**
- When first relating to a TLS provider (initial setup)
- When a certificate is revoked by the provider
- When `request_errors` indicate the CSR needs adjustment (error codes: `ip_not_allowed` 101, `domain_not_allowed` 102, `wildcard_not_allowed` 103, `server_not_available` 201)

**Note:** The specific event names (e.g., `certificate_available`, `certificate_expiring`, `certificate_invalidated`) are part of the library's Python API, not the interface specification documented in charmlibs.

**Source:** charmlibs reference — "tls-certificates" interface v1.

---

## Q15: What is `charmlibs.pathops` and how do you use `ContainerPath` and `ensure_contents` to manage files in a workload container?

The `charmlibs.pathops` library provides a `pathlib`-like interface for working with both local and remote container filesystem paths. Install: `uv add charmlibs-pathops`. Import: `from charmlibs.pathops import ContainerPath, LocalPath, ensure_contents`.

**Key components:**

- **`PathProtocol`** — Protocol defining methods common to both local and container paths. Use for type annotations in code that works across K8s and machine charms.
- **`ContainerPath`** — Implementation for remote paths in workload containers, using the Pebble file API. Only supports absolute paths (raises `RelativePathError` for relative paths).
- **`LocalPath`** — Extends `pathlib.PosixPath` with enhanced file-creation arguments (`mode`, `user`, `group`).
- **`ensure_contents`** — Helper function that works with both path types.

**`ContainerPath` usage:**
```python
container = self.unit.get_container('c')
path = ContainerPath('/etc/myapp/config.yaml', container=container)

# Supports pathlib-like operations
path.read_text()
path.write_text('content', mode=0o640, user='app', group='app')
path.mkdir(parents=True, exist_ok=True)
path / 'subdir'  # join paths
path.exists()
path.iterdir()
path.glob('*.conf')
```

**`ensure_contents` signature:**
```python
ensure_contents(
    path: ContainerPath | LocalPath,
    source: str | bytes | ReadableBuffer,
    mode: int | None = None,
    user: str | None = None,
    group: str | None = None,
) -> bool
```

Ensures `path` exists, contains `source`, has the correct permissions and ownership. Returns `True` if any changes were made, `False` otherwise.

**Key facts:**
- `ContainerPath` operations raise `PebbleConnectionError` if the workload container is unreachable.
- Comparison methods only compare `ContainerPath` objects on the same `ops.Container`.
- `str(path)` returns the path string suitable for use in Pebble layers and system calls.
- Both `ContainerPath` and `LocalPath` support `read_text()`, `write_bytes()`, `mkdir()`, `iterdir()`, `glob()`.
- File write methods accept optional `mode`, `user`, `group` parameters.

**Source:** charmlibs reference — "charmlibs.pathops".

---

## Q16: What is the correct way to implement a provider side of a relation using charmlibs?

**General approach:**

1. Add a `provides` endpoint to `charmcraft.yaml` for the desired interface
2. Find the interface library in the [interface libraries listing](https://documentation.ubuntu.com/charmlibs/reference/interface-libs/)
3. Libraries are either:
   - **PyPI packages** (`charmlibs.interfaces.*` namespace) — add to dependencies
   - **Charmhub-hosted** (legacy) — fetch via `charmcraft fetch-lib`
4. Implement the provider behavioural contract from the interface specification

**Common provider-side patterns:**
- Respond to relation events (`relation-joined`, `relation-changed`)
- Write data to the **application** databag (not unit) for responses
- Use Juju Secrets for sensitive data when supported
- Provide the fields defined by the interface schema

**Note:** The charmlibs documentation focuses on interface specifications (schemas and contracts) rather than code tutorials. The Python API lives in the library source code.

**Source:** charmlibs explanation — "Charm libs".

---

## Q17: What is the structure of a `charmcraft.yaml` file for a Kubernetes charm? Show a complete example with all required fields.

**Required fields:** `name`, `type`, `base`, `platforms`, `summary`, `description`, `containers` (for K8s charms), plus `resources` (OCI image per container).

```yaml
name: my-k8s-app
type: charm
base: ubuntu@24.04
platforms:
  amd64:
summary: A Kubernetes charm for my application.
description: |
  This is a long description of the charm.
assumes:
  - k8s-api
  - juju >= 3.5
containers:
  super-app:
    resource: super-app-image
    mounts:
    - storage: logs
      location: /logs
resources:
  super-app-image:
    type: oci-image
    description: OCI image for the Super App (hub.docker.com/_/super-app)
```

**Full set of top-level keys:**
`name` (req), `type` (req), `base` (req), `platforms` (req), `summary` (req, max 78 chars), `description` (req), `containers` (req for K8s), `build-base`, `assumes`, `actions`, `analysis`, `charm-libs`, `charm-user`, `config`, `devices`, `extra-bindings`, `links`, `parts`, `peers`/`provides`/`requires`, `resources`, `storage`, `subordinate`, `terms`, `title`.

**Source:** charmcraft reference — "charmcraft.yaml file".

---

## Q18: How do you declare a relation endpoint in `charmcraft.yaml` and what fields does it support?

Endpoints are declared under `peers`, `provides`, or `requires`:

```yaml
peers:
  friend:
    interface: life
    limit: 150
    optional: true
    scope: container
provides:
  self:
    interface: identity
requires:
  parent:
    interface: birth
    limit: 2
    optional: false
    scope: global
```

**Supported fields:**

| Field | Status | Type | Notes |
|---|---|---|---|
| `interface` | **Required** | String | Interface name; cannot be `juju` or start with `juju-`; only `a-z` and `-` |
| `limit` | Optional | Integer | Maximum number of connections |
| `optional` | Optional | Boolean | Whether the relation is required; defaults to `false` |
| `scope` | Optional | String | `global` (default) or `container`; subordinates need at least one `requires` with `container` scope |

**Source:** charmcraft reference — "charmcraft.yaml file".

---

## Q19: How do you configure resource declarations for OCI images in `charmcraft.yaml`?

K8s charms **must** declare an `oci-image` resource for each container.

```yaml
containers:
  super-app:
    resource: super-app-image

resources:
  super-app-image:
    type: oci-image
    description: OCI image for the Super App (hub.docker.com/_/super-app)
```

**Resource fields:**
- `type`: `oci-image` (for container images) or `file` (for files)
- `description`: optional string description
- `filename`: path to resource (only for `file` type, not used for `oci-image`)

**Key rule:** The resource name under `resources` must match the `resource` field in the corresponding `containers` entry.

**Source:** charmcraft reference — "charmcraft.yaml file".

---

## Q20: What bases/platforms does charmcraft support and how do you specify multi-base builds?

**Supported bases:** `ubuntu@22.04`, `ubuntu@24.04`, `ubuntu@24.10`, `ubuntu@25.04`, `almalinux@9`. Also `ubuntu@devel` as `build-base`.

**Supported architectures:** `amd64`, `arm64`, `armhf`, `ppc64el`, `s390x`.

**Single-base (standard):**
```yaml
base: ubuntu@24.04
platforms:
  amd64:
```

**Multiple architectures:**
```yaml
base: ubuntu@24.04
platforms:
  amd64:
  arm64:
```

**Cross-compilation:**
```yaml
base: ubuntu@24.04
platforms:
  riscv64-cross:
    build-on: [amd64]
    build-for: [riscv64]
```

**Multi-base builds:** The `base` top-level key is **not** used. Instead, the base is embedded in each platform entry:

```yaml
platforms:
  ubuntu@22.04:amd64:
  ubuntu@24.04:amd64:
```

Or in long form:
```yaml
platforms:
  ubuntu-22.04-amd64:
    build-on: [ubuntu@22.04:amd64]
    build-for: [ubuntu@22.04:amd64]
  ubuntu-24.04-amd64:
    build-on: [ubuntu@24.04:amd64]
    build-for: [ubuntu@24.04:amd64]
```

Both produce two `.charm` files.

**Architecture-independent:**
```yaml
base: ubuntu@24.04
platforms:
  all:
    build-on: [amd64]
    build-for: [all]
```

**Source:** charmcraft reference — "Platforms" and "charmcraft.yaml file".

---

## S1: Minimal K8s charm with ActiveStatus on install and WaitingStatus if 'name' config is empty

**`src/charm.py`:**
```python
#!/usr/bin/env python3

import ops


class MinimalCharm(ops.CharmBase):
    def __init__(self, framework: ops.Framework):
        super().__init__(framework)
        framework.observe(self.on.collect_unit_status, self._on_collect_status)

    def _on_collect_status(self, event: ops.CollectStatusEvent):
        if not self.model.config.get('name'):
            event.add_status(ops.WaitingStatus('waiting for name config'))
            return
        event.add_status(ops.ActiveStatus())


if __name__ == '__main__':
    ops.main(MinimalCharm)
```

**`charmcraft.yaml`:**
```yaml
name: minimal-charm
type: charm
base: ubuntu@24.04
platforms:
  amd64:
summary: A minimal Kubernetes charm.
description: |
  A minimal charm that sets active status or waiting status
  based on whether the name config option is set.
assumes:
  - k8s-api
containers:
  app:
    resource: app-image
resources:
  app-image:
    type: oci-image
    description: OCI image for the application
config:
  options:
    name:
      type: string
      default: ""
      description: The name to greet.
```

**Scoring notes:**
- Must use `CollectStatusEvent` pattern (modern) rather than direct `self.unit.status =` (legacy but still valid).
- Both approaches are acceptable, but `CollectStatusEvent` is current best practice.
- Must have `containers` + `resources` for K8s charm.
- Config option must be declared in `charmcraft.yaml`.

---

## S2: Pebble-ready handler with config command, database relation env vars, and HTTP health check

```python
def _on_pebble_ready(self, event: ops.PebbleReadyEvent):
    container = event.workload

    # Get command from config
    command = self.model.config.get('command', '/usr/bin/app')

    # Get database connection details from relation
    env = {}
    db_relation = self.model.get_relation('database')
    if db_relation and db_relation.app:
        db_data = db_relation.data[db_relation.app]
        env['DB_HOST'] = db_data.get('endpoints', '')
        env['DB_NAME'] = db_data.get('database', '')
        # For secrets-based interfaces, credentials come via Juju secrets
        # For simple interfaces, they may be in the databag directly

    layer = {
        'summary': 'app layer',
        'services': {
            'app': {
                'override': 'replace',
                'command': command,
                'startup': 'enabled',
                'environment': env,
                'on-check-failure': {
                    'app-health': 'restart',
                },
            },
        },
        'checks': {
            'app-health': {
                'override': 'replace',
                'level': 'ready',
                'http': {
                    'url': 'http://localhost:8080/health',
                },
            },
        },
    }

    container.add_layer('app', layer, combine=True)
    container.replan()
```

**Scoring notes:**
- Must use `event.workload` to get the container.
- Must use `add_layer` with a valid layer dict.
- Must call `container.replan()` after adding the layer.
- Must access config via `self.model.config`.
- Must access relation data via `relation.data[relation.app]`.
- Health check must use `http` with a `url` field.
- `override: replace` is important.

---

## S3: Charm that provides data over a custom relation interface

```python
#!/usr/bin/env python3

import ops


class ProviderCharm(ops.CharmBase):
    def __init__(self, framework: ops.Framework):
        super().__init__(framework)
        framework.observe(
            self.on.my_service_relation_joined,
            self._on_relation_joined,
        )

    def _on_relation_joined(self, event: ops.RelationJoinedEvent):
        # Set the endpoint key in the relation data to this unit's FQDN
        # Unit databag is writable by the unit itself
        event.relation.data[self.unit]['endpoint'] = self._get_fqdn()

    def _get_fqdn(self) -> str:
        import socket
        return socket.getfqdn()


if __name__ == '__main__':
    ops.main(ProviderCharm)
```

With `charmcraft.yaml` including:
```yaml
provides:
  my-service:
    interface: my-service
```

**Scoring notes:**
- Must observe `relation_joined` (or `relation_changed`) — `relation_joined` is most appropriate for "when a remote app joins".
- Must write to `event.relation.data[self.unit]` (unit databag) since the task says "the unit's FQDN" — this is per-unit data.
- If writing app-level data, must check `self.unit.is_leader()` before writing to `event.relation.data[self.app]`.
- Getting the FQDN via `socket.getfqdn()` or `socket.getfqdn(self.unit.name)` are both valid.
- The `provides` endpoint must be declared in `charmcraft.yaml`.
