# 🤖 Copilot CLI Session

> [!NOTE]
> - **Session ID:** `5b07a4a6-de82-4619-a2af-36e1ee754188`  
> - **Started:** 4/2/2026, 3:47:49 AM  
> - **Duration:** 14m 57s  
> - **Exported:** 4/2/2026, 4:02:47 AM  

---

<sub>⏱️ 5s</sub>

### 👤 User

ops 2.15.0 added pebble-check-failed and pebble-check-recovered events that allow K8s charms to react when Pebble health checks fail or recover, replacing manual check polling patterns. The charm at https://github.com/canonical/kratos-operator already uses this feature -- look at how they did it and update this charm similarly.

---

<sub>⏱️ 22s</sub>

### ✅ `task`

**Explore kratos-operator pebble check events**

<details>
<summary>Arguments</summary>

```json
{
  "name": "explore-kratos",
  "agent_type": "explore",
  "description": "Explore kratos-operator pebble check events",
  "prompt": "Look at https://github.com/canonical/kratos-operator and find how they implemented pebble-check-failed and pebble-check-recovered events. Specifically:\n1. Find all uses of pebble_check_failed and pebble_check_recovered event handlers in src/charm.py\n2. Find how checks are defined in pebble layers (look for \"checks\" in layer definitions)\n3. Find any existing check polling patterns that were replaced\n4. Show the relevant code snippets with file paths and line numbers\n\nSearch the GitHub repository directly using the github-mcp-server-get_file_contents tool for the owner=canonical, repo=kratos-operator.",
  "mode": "background"
}
```

</details>

```
Agent started in background with agent_id: explore-kratos. You can use read_agent tool with this agent_id to check status and retrieve results. Instruct the user to use /tasks to manage the background agent.
```


---

<sub>⏱️ 22s</sub>

### ✅ `task`

**Explore current indico charm pebble checks**

<details>
<summary>Arguments</summary>

```json
{
  "name": "explore-indico",
  "agent_type": "explore",
  "description": "Explore current indico charm pebble checks",
  "prompt": "In the repository at /tmp/ops-upgrade-experiment/indico-operator__pebble-check-events__C3, find:\n1. All pebble layer definitions (look for \"checks\" in layer YAML/dict definitions) - show full layer content\n2. Any existing check polling or status update patterns \n3. How _on_config_changed, _on_pebble_ready, and similar handlers work\n4. The full content of src/charm.py focusing on: pebble layer definitions, status setting logic, container readiness checks\n5. Any existing _check_* or check-related methods\n\nShow the file content with line numbers for the relevant sections.",
  "mode": "background"
}
```

</details>

```
Agent started in background with agent_id: explore-indico. You can use read_agent tool with this agent_id to check status and retrieve results. Instruct the user to use /tasks to manage the background agent.
```


---

<sub>⏱️ 1m 31s</sub>

### ✅ `read_agent`

**Explore agent (Explore kratos-operator pebble check events)**

<details>
<summary>Arguments</summary>

```json
{
  "agent_id": "explore-kratos",
  "wait": true,
  "timeout": 60
}
```

</details>

```
Agent is still running after waiting 60s. agent_id: explore-kratos, agent_type: explore, status: running, description: Explore kratos-operator pebble check events, elapsed: 69s, total_turns: 0, tool_calls_completed: 25, (timed out waiting for completion) You will be automatically notified when this agent completes — no need to poll.
```


---

<sub>⏱️ 1m 32s</sub>

### ✅ `read_agent`

**Explore agent (Explore current indico charm pebble checks)**

<details>
<summary>Arguments</summary>

```json
{
  "agent_id": "explore-indico",
  "wait": true,
  "timeout": 60
}
```

</details>

```
Agent is still running after waiting 60s. agent_id: explore-indico, agent_type: explore, status: running, description: Explore current indico charm pebble checks, elapsed: 69s, total_turns: 0, tool_calls_completed: 28, (timed out waiting for completion) You will be automatically notified when this agent completes — no need to poll.
```


---

<sub>⏱️ 1m 47s</sub>

### 💬 Copilot

I'll wait for both explorations to complete.

---

<sub>⏱️ 1m 55s</sub>

### ✅ `read_agent`

**Explore agent (Explore kratos-operator pebble check events)**

<details>
<summary>Arguments</summary>

```json
{
  "agent_id": "explore-kratos",
  "timeout": 60,
  "wait": true
}
```

</details>

<details>
<summary>117 lines</summary>

````
Agent completed. agent_id: explore-kratos, agent_type: explore, status: completed, description: Explore kratos-operator pebble check events, elapsed: 92s, total_turns: 0, duration: 92s

Perfect! Now I have all the information. Let me create a comprehensive summary with all findings:

## Summary: Pebble Check Events Implementation in kratos-operator

I found a complete implementation of pebble-check-failed and pebble-check-recovered events in the canonical/kratos-operator repository. Here are the key findings:

---

### **1. Event Handler Registrations and Implementation** 
**File: `src/charm.py`**

**Lines 279-281** - Event observer registration:
```python
self.framework.observe(self.on.kratos_pebble_check_failed, self._on_pebble_check_failed)
self.framework.observe(
    self.on.kratos_pebble_check_recovered, self._on_pebble_check_recovered
)
```

**Lines 777-782** - Event handler implementations:
```python
def _on_pebble_check_failed(self, event: PebbleCheckFailedEvent) -> None:
    if event.info.name == PEBBLE_READY_CHECK_NAME:
        logger.warning("The service is not running")

def _on_pebble_check_recovered(self, event: PebbleCheckRecoveredEvent) -> None:
    if event.info.name == PEBBLE_READY_CHECK_NAME:
        logger.info("The service is online again")
```

**Imports (Lines 60-61):**
```python
from ops import (
    ...
    PebbleCheckFailedEvent,
    PebbleCheckRecoveredEvent,
    ...
)
```

---

### **2. Pebble Layer with Checks Definition**
**File: `src/services.py`, lines 28-47**

```python
PEBBLE_LAYER_DICT = {
    "summary": "pebble layer",
    "description": "pebble layer for kratos",
    "services": {
        WORKLOAD_SERVICE: {
            "override": "replace",
            "summary": "entrypoint of the kratos image",
            "command": f"kratos serve all --config {CONFIG_FILE_PATH}",
            "startup": "disabled",
        }
    },
    "checks": {
        PEBBLE_READY_CHECK_NAME: {
            "override": "replace",
            "level": "ready",
            "http": {"url": f"http://localhost:{KRATOS_ADMIN_PORT}/admin/health/ready"},
        },
        "alive": {
            "override": "replace",
            "level": "alive",
            "http": {"url": f"http://localhost:{KRATOS_ADMIN_PORT}/admin/health/alive"},
        },
    },
}
```

**Check name constant (src/constants.py, line 10):**
```python
PEBBLE_READY_CHECK_NAME = "ready"
```

---

### **3. Replaced Polling Patterns**

Instead of using a polling-based approach in `update_status`, the implementation now:

**Old Pattern (polling in update_status):** 
The `_on_update_status` method at **line 587-588** now just delegates:
```python
def _on_update_status(self, event: UpdateStatusEvent) -> None:
    self._holistic_handler(event)
```

**New Pattern (event-driven):**
- Status checks happen in `_on_collect_status` (lines 491-540)
- The check mechanism uses pebble check failure tracking instead of periodic polling
- `WorkloadService.is_failing()` method (src/services.py, lines 98-103) queries the check failures:
```python
def is_failing(self) -> bool:
    """Checks whether the service has crashed."""
    if not self.get_service():
        return False

    if not (c := self._container.get_checks().get(PEBBLE_READY_CHECK_NAME)):
        return False

    return c.failures > 0
```

**Status check integration (src/charm.py, lines 532-536):**
```python
if can_connect and self._workload_service.is_failing():
    event.add_status(
        BlockedStatus(
            f"Failed to start the service, please check the {WORKLOAD_CONTAINER} container logs"
        )
    )
```

---

### **4. Check Status Monitoring**

**Running status check (src/services.py, lines 88-95):**
```python
def is_running(self) -> bool:
    """Checks whether the service is running."""
    if not (service := self.get_service()):
        return False

    if not service.is_running():
        return False

    c = self._container.get_checks().get(PEBBLE_READY_CHECK_NAME)
    return c.status == CheckStatus.UP
```

---

### **Key Design Points:**

1. **Two HTTP checks defined:**
   - `ready` (level: ready) - checks `/admin/health/ready` endpoint on port 4434
   - `alive` (level: alive) - checks `/admin/health/alive` endpoint on port 4434

2. **Event-driven architecture:** Replaced poll-based status updates with pebble check events that fire automatically

3. **Minimal logging:** Events only log if the check name matches `PEBBLE_READY_CHECK_NAME`

4. **Check failure tracking:** Uses `check.failures` counter to determine if service is degraded
````

</details>


---

<sub>⏱️ 1m 50s</sub>

### ✅ `read_agent`

**Explore agent (Explore current indico charm pebble checks)**

<details>
<summary>Arguments</summary>

```json
{
  "agent_id": "explore-indico",
  "timeout": 60,
  "wait": true
}
```

</details>

<details>
<summary>353 lines</summary>

````
Agent completed. agent_id: explore-indico, agent_type: explore, status: completed, description: Explore current indico charm pebble checks, elapsed: 87s, total_turns: 0, duration: 87s

Now let me compile the complete analysis with all the information I've gathered:

## Summary: Pebble Layers, Checks, and Handler Patterns

### 1. **All Pebble Layer Definitions (with Checks)**

I found **6 pebble layer configuration methods** in `src/charm.py`. Here are the complete definitions:

#### **A. Logrotate Layer** (Lines 270-289)
```python
def _get_logrotate_config(self) -> ops.pebble.LayerDict:
    """Generate logrotate pebble layer."""
    layer = {
        "summary": "Logrotate service",
        "description": "Logrotate service",
        "services": {
            "logrotate": {
                "override": "replace",
                "command": 'bash -c "while :; '
                "do sleep 3600; logrotate /srv/indico/logrotate.conf; "
                'done"',
                "startup": "enabled",
            },
        },
    }
    return typing.cast(ops.pebble.LayerDict, layer)
```
**No checks defined.**

#### **B. Indico Layer with TCP Ready Check** (Lines 291-323)
```python
def _get_indico_pebble_config(self, container: Container) -> ops.pebble.LayerDict:
    """Generate pebble config for the indico container."""
    indico_env_config = self._get_indico_env_config(container)
    indico_env_config["INDICO_LOGGING_CONFIG_FILE"] = "indico.logging.yaml"
    layer = {
        "summary": "Indico layer",
        "description": "Indico layer",
        "services": {
            "indico": {
                "override": "replace",
                "summary": "Indico service",
                "command": "/srv/indico/start-indico.sh",
                "startup": "enabled",
                "user": "indico",
                "environment": indico_env_config,
            },
        },
        "checks": {                                    # ← CHECK DEFINITION
            "indico-ready": {
                "override": "replace",
                "level": "ready",                      # ← Level: "ready"
                "tcp": {"port": 8081},                 # ← TCP check on port 8081
            },
        },
    }
    return typing.cast(ops.pebble.LayerDict, layer)
```

#### **C. Celery Layer with Exec Alive Check** (Lines 325-362)
```python
def _get_celery_pebble_config(self, container: Container) -> ops.pebble.LayerDict:
    """Generate pebble config for the celery container."""
    indico_env_config = self._get_indico_env_config(container)
    indico_env_config["INDICO_LOGGING_CONFIG_FILE"] = "celery.logging.yaml"
    layer = {
        "summary": "Indico celery layer",
        "description": "Indico celery layer",
        "services": {
            "celery": {
                "override": "replace",
                "summary": "Indico celery",
                "command": "/usr/bin/indico celery worker -B -E",
                "startup": "enabled",
                "user": "indico",
                "environment": indico_env_config,
            },
        },
        "checks": {                                    # ← CHECK DEFINITION
            "ready": {
                "override": "replace",
                "level": "alive",                      # ← Level: "alive"
                "period": "120s",                      # ← Check every 120 seconds
                "timeout": "119s",                     # ← Timeout after 119 seconds
                "exec": {                              # ← Exec check
                    "command": "/usr/bin/indico celery inspect ping",
                    "environment": indico_env_config,
                },
            },
        },
    }
    return typing.cast(ops.pebble.LayerDict, layer)
```

#### **D. Nginx Layer with HTTP Alive Check** (Lines 364-389)
```python
def _get_nginx_pebble_config(self, _) -> ops.pebble.LayerDict:
    """Generate pebble config for the indico-nginx container."""
    layer = {
        "summary": "Indico nginx layer",
        "description": "Indico nginx layer",
        "services": {
            "indico-nginx": {
                "override": "replace",
                "summary": "Nginx service",
                "command": "/usr/sbin/nginx",
                "startup": "enabled",
            },
        },
        "checks": {                                    # ← CHECK DEFINITION
            "nginx-ready": {
                "override": "replace",
                "level": "alive",                      # ← Level: "alive"
                "http": {"url": "http://localhost:8080/health"},  # ← HTTP GET check
            },
        },
    }
    return typing.cast(ops.pebble.LayerDict, layer)
```

#### **E. Celery Prometheus Exporter Layer with HTTP Alive Check** (Lines 426-460)
```python
def _get_celery_prometheus_exporter_pebble_config(self, container) -> ops.pebble.LayerDict:
    """Generate pebble config for the celery-prometheus-exporter container."""
    indico_env_config = self._get_indico_env_config(container)
    layer = {
        "summary": "Celery prometheus exporter",
        "description": "Prometheus exporter for celery",
        "services": {
            "celery-exporter": {
                "override": "replace",
                "summary": "Celery Exporter",
                "command": (
                    "celery-exporter"
                    f" --broker-url={self._get_redis_url('redis-broker')}"
                    " --retry-interval=5"
                ),
                "environment": indico_env_config,
                "startup": "enabled",
            },
        },
        "checks": {                                    # ← CHECK DEFINITION
            "celery-exporter-up": {
                "override": "replace",
                "level": "alive",                      # ← Level: "alive"
                "http": {"url": "http://localhost:9808/health"},  # ← HTTP GET check
            },
        },
    }
    return typing.cast(ops.pebble.LayerDict, layer)
```

#### **F. Nginx Prometheus Exporter Layer with HTTP Alive Check** (Lines 462-490)
```python
def _get_nginx_prometheus_exporter_pebble_config(self, _) -> ops.pebble.LayerDict:
    """Generate pebble config for the nginx-prometheus-exporter container."""
    layer = {
        "summary": "Nginx prometheus exporter",
        "description": "Prometheus exporter for nginx",
        "services": {
            "nginx-prometheus-exporter": {
                "override": "replace",
                "summary": "Nginx Exporter",
                "command": (
                    "nginx-prometheus-exporter"
                    " -nginx.scrape-uri=http://localhost:9080/stub_status"
                ),
                "startup": "enabled",
            },
        },
        "checks": {                                    # ← CHECK DEFINITION
            "nginx-exporter-up": {
                "override": "replace",
                "level": "alive",                      # ← Level: "alive"
                "http": {"url": "http://localhost:9113/metrics"},  # ← HTTP GET check
            },
        },
    }
    return typing.cast(ops.pebble.LayerDict, layer)
```

#### **G. Statsd Prometheus Exporter Layer with HTTP Alive Check** (Lines 492-517)
```python
def _get_statsd_prometheus_exporter_pebble_config(self, _) -> ops.pebble.LayerDict:
    """Generate pebble config for the statsd-prometheus-exporter container."""
    layer = {
        "summary": "Statsd prometheus exporter",
        "description": "Prometheus exporter for statsd",
        "services": {
            "statsd-exporter": {
                "override": "replace",
                "summary": "Statsd Exporter",
                "command": ("statsd_exporter"),
                "startup": "enabled",
            },
        },
        "checks": {                                    # ← CHECK DEFINITION
            "statsd-exporter-up": {
                "override": "replace",
                "level": "alive",                      # ← Level: "alive"
                "http": {"url": "http://localhost:9102/metrics"},  # ← HTTP GET check
            },
        },
    }
    return typing.cast(ops.pebble.LayerDict, layer)
```

---

### 2. **Check Types and Patterns Used**

The charm uses **three types of checks**:

| Check Type | Layer | Details |
|-----------|-------|---------|
| **TCP** | Indico | Port 8081, level: "ready" (used for container readiness) |
| **HTTP GET** | Nginx, Celery Exporter, Nginx Exporter, Statsd Exporter | Health endpoints, level: "alive" |
| **Exec** | Celery | `/usr/bin/indico celery inspect ping` command, level: "alive", period: 120s |

---

### 3. **Event Handlers: How They Work**

#### **A. `_on_pebble_ready` Handler** (Lines 213-268)
```python
def _on_pebble_ready(self, event: PebbleReadyEvent) -> None:
    """Handle the on pebble ready event for the containers.
    
    Args:
        event: Event triggering the pebble ready handler.
    """
    if not self._are_relations_ready(event) or not event.workload.can_connect():
        event.defer()  # ← Defer if relations not ready or container not accessible
        return
    self._config_pebble(event.workload)  # ← Configure pebble layers
```

**Flow:**
1. Fires when container pebble service is ready (mapped in metadata.yaml for `indico` and `indico-nginx` containers)
2. Checks relations and container connectivity
3. Defers event if dependencies not met
4. Calls `_config_pebble()` to add layers

#### **B. `_config_pebble` Handler** (Lines 224-268)
```python
def _config_pebble(self, container: Container) -> None:
    """Apply pebble configurations to a container."""
    self.unit.status = MaintenanceStatus(f"Adding {container.name} layer to pebble")
    if container.name == "indico":
        plugins = (
            typing.cast(str, self.config["external_plugins"]).split(",")
            if self.config["external_plugins"]
            else []
        )
        self._install_plugins(container, plugins)  # ← Install external plugins
        container.add_layer(container.name, self._get_logrotate_config(), combine=True)
        indico_config = self._get_indico_pebble_config(container)
        container.add_layer(container.name, indico_config, combine=True)
        # ... (celery and statsd layers)
    if container.name == "indico-nginx":
        nginx_config = self._get_nginx_pebble_config(container)
        container.add_layer(container.name, nginx_config, combine=True)
        # ... (nginx exporter layer)
    self.unit.status = MaintenanceStatus(f"Starting {container.name} container")
    container.pebble.replan_services()  # ← Restart services with new config
    if self._are_pebble_instances_ready():
        self.unit.set_workload_version(self._get_indico_version())
        self.unit.status = ActiveStatus()  # ← Final success status
    else:
        self.unit.status = WaitingStatus("Waiting for pebble")
```

**Key Features:**
- Sets `MaintenanceStatus` during configuration
- Installs plugins before adding indico layer
- Uses `combine=True` to merge layers instead of replacing
- Calls `replan_services()` to apply changes
- Sets `ActiveStatus` only when all pebble instances are ready

#### **C. `_on_config_changed` Handler** (Lines 680-697)
```python
def _on_config_changed(self, event: HookEvent) -> None:
    """Handle changes in configuration."""
    if not self._are_relations_ready(event):
        return
    if not self._are_pebble_instances_ready():  # ← Check pebble readiness
        self.unit.status = WaitingStatus("Waiting for pebble")
        return
    self.model.unit.status = MaintenanceStatus("Configuring pod")
    is_valid, error = self._is_configuration_valid()
    if not is_valid:
        self.model.unit.status = BlockedStatus(error)  # ← Invalid config blocks unit
        return
    for container_name in self.model.unit.containers:
        self._config_pebble(self.unit.get_container(container_name))
```

**Key Features:**
- Fired when config changes or relations are updated
- Validates configuration before applying
- Blocks unit if config is invalid
- Reconfigures pebble for all containers

---

### 4. **Container Readiness Checks**

#### **A. `_are_pebble_instances_ready()` Method** (Lines 144-153)
```python
def _are_pebble_instances_ready(self) -> bool:
    """Check if all pebble instances are up and containers available.
    
    Returns:
        If the containers are up and available.
    """
    return all(
        self.unit.get_container(container_name).can_connect()
        for container_name in self.model.unit.containers  # ← Checks: "indico" and "indico-nginx"
    )
```

**What it does:** Uses `can_connect()` to verify pebble socket connectivity for all containers defined in metadata.

#### **B. `_are_relations_ready()` Method** (Lines 196-211)
```python
def _are_relations_ready(self, _) -> bool:
    """Check if the needed relations are established.
    
    Returns:
        If the needed relations have been established.
    """
    if self.redis_broker.relation_data is None:
        self.unit.status = WaitingStatus("Waiting for redis-broker availability")
        return False
    if self.redis_cache.relation_data is None:
        self.unit.status = WaitingStatus("Waiting for redis-cache availability")
        return False
    if self.database.uri is None:
        self.unit.status = WaitingStatus("Waiting for database availability")
        return False
    return True
```

**What it does:** Checks three required relations are established before proceeding.

---

### 5. **Status Setting Logic**

The charm uses a state machine for unit status transitions:

```python
# During initialization/blocking configuration
self.unit.status = ops.BlockedStatus(exc.msg)  # Line 84

# Waiting for relations
self.unit.status = WaitingStatus("Waiting for redis-broker availability")  # Line 203
self.unit.status = WaitingStatus("Waiting for redis-cache availability")   # Line 206
self.unit.status = WaitingStatus("Waiting for database availability")      # Line 209

# During pebble configuration
self.unit.status = MaintenanceStatus(f"Adding {container.name} layer to pebble")  # Line 230
self.unit.status = MaintenanceStatus(f"Starting {container.name} container")      # Line 262

# When pebble not ready yet
self.unit.status = WaitingStatus("Waiting for pebble")  # Lines 268, 689

# Configuration updates
self.model.unit.status = MaintenanceStatus("Configuring pod")           # Line 691
self.model.unit.status = BlockedStatus(error)                           # Line 694

# Final success
self.unit.status = ActiveStatus()  # Line 266
```

---

### 6. **No Existing Check Event Handlers**

**Important Finding:** There are **NO check-related event handlers** in the charm:
- No `_on_pebble_check_*` methods
- No `CheckEvent` references
- No check status monitoring
- Checks are defined in layers but not explicitly monitored by charm

The checks are **passive** - Pebble manages them and the charm relies on overall `can_connect()` to determine readiness.

---

### 7. **Container Configuration in metadata.yaml** (Lines 34-46)

```yaml
containers:
  indico:
    resource: indico-image
  indico-nginx:
    resource: indico-nginx-image
```

Two containers with pebble layers applied to each during `_on_pebble_ready` event.
````

</details>


---

<sub>⏱️ 1m 55s</sub>

### ℹ️ Notification

Background agent "Explore current indico charm pebble checks" (explore) completed

<details>
<summary>Detail</summary>

In the repository at /tmp/ops-upgrade-experiment/indico-operator__pebble-check-events__C3, find:
1. All pebble layer definitions (look for "checks" in layer YAML/dict definitions) - show full layer content
2. Any existing check polling or status update patterns 
3. How _on_config_changed, _on_pebble_ready, and similar handlers work
4. The full content of src/charm.py focusing on: pebble layer definitions, status setting logic, container readiness checks
5. Any existing _check_* or check-related methods

Show the file content with line numbers for the relevant sections.

</details>

---

<sub>⏱️ 1m 55s</sub>

### ℹ️ Notification

Background agent "Explore kratos-operator pebble check events" (explore) completed

<details>
<summary>Detail</summary>

Look at https://github.com/canonical/kratos-operator and find how they implemented pebble-check-failed and pebble-check-recovered events. Specifically:
1. Find all uses of pebble_check_failed and pebble_check_recovered event handlers in src/charm.py
2. Find how checks are defined in pebble layers (look for "checks" in layer definitions)
3. Find any existing check polling patterns that were replaced
4. Show the relevant code snippets with file paths and line numbers

Search the GitHub repository directly using the github-mcp-server-get_file_contents tool for the owner=canonical, repo=kratos-operator.

</details>

---

<sub>⏱️ 2m 25s</sub>

### 💬 Copilot

Now I have a clear picture. Let me read the relevant parts of `src/charm.py` to make precise edits.

---

<sub>⏱️ 2m 25s</sub>

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/indico-operator__pebble-check-events__C3/src/charm.py.**

/tmp/ops-upgrade-experiment/indico-operator__pebble-check-events__C3/src/charm.py (lines 1-120)

<details>
<summary>120 lines</summary>

```
1. #!/usr/bin/env python3
2. 
3. # Copyright 2025 Canonical Ltd.
4. # See LICENSE file for licensing details.
5. 
6. """Charm for Indico on kubernetes."""
7. 
8. # pylint: disable=too-many-lines
9. 
10. import logging
11. import os
12. import secrets
13. import typing
14. from re import findall
15. from typing import Any, Dict, Iterator, List, Optional, Tuple
16. from urllib.parse import urlparse
17. 
18. import charms.loki_k8s.v0.loki_push_api
19. import ops
20. from charms.grafana_k8s.v0.grafana_dashboard import GrafanaDashboardProvider
21. from charms.loki_k8s.v0.loki_push_api import LogProxyConsumer
22. from charms.nginx_ingress_integrator.v0.nginx_route import require_nginx_route
23. from charms.prometheus_k8s.v0.prometheus_scrape import MetricsEndpointProvider
24. from charms.redis_k8s.v0.redis import RedisRelationCharmEvents, RedisRequires
25. from ops.charm import ActionEvent, CharmBase, HookEvent, PebbleReadyEvent, RelationDepartedEvent
26. from ops.jujuversion import JujuVersion
27. from ops.main import main
28. from ops.model import ActiveStatus, BlockedStatus, Container, MaintenanceStatus, WaitingStatus
29. from ops.pebble import ExecError
30. 
31. from database_observer import DatabaseObserver
32. from s3_observer import S3Observer
33. from saml_observer import SamlObserver
34. from smtp_observer import SmtpObserver
35. from state import CharmConfigInvalidError, ProxyConfig, State
36. 
37. logger = logging.getLogger(__name__)
38. 
39. CELERY_PROMEXP_PORT = "9808"
40. DATABASE_NAME = "indico"
41. EMAIL_LIST_MAX = 50
42. EMAIL_LIST_SEPARATOR = ","
43. INDICO_CUSTOMIZATION_DIR = "/srv/indico/custom"
44. NGINX_PROMEXP_PORT = "9113"
45. PORT = 8080
46. STATSD_PROMEXP_PORT = "9102"
47. SAML_GROUPS_PLUGIN_NAME = "saml_groups"
48. 
49. UWSGI_TOUCH_RELOAD = "/srv/indico/indico.wsgi"
50. 
51. 
52. class InvalidRedisNameError(Exception):
53.     """Represents invalid redis name error."""
54. 
55. 
56. class IndicoOperatorCharm(CharmBase):  # pylint: disable=too-many-instance-attributes
57.     """Charm for Indico on kubernetes.
58. 
59.     Attrs:
60.         on: Redis relation charm events.
61.     """
62. 
63.     on = RedisRelationCharmEvents()
64. 
65.     def __init__(self, *args):
66.         """Construct.
67. 
68.         Args:
69.             args: Arguments passed to the CharmBase parent constructor.
70.         """
71.         super().__init__(*args)
72.         self.database = DatabaseObserver(self)
73.         self.s3 = S3Observer(self)
74.         self.smtp = SmtpObserver(self)
75.         self.saml = SamlObserver(self)
76.         try:
77.             self.state = State.from_charm(
78.                 self,
79.                 s3_relation_data=self.s3.s3.get_s3_connection_info(),
80.                 smtp_relation_data=self.smtp.smtp.get_relation_data(),
81.                 saml_relation_data=self.saml.saml.get_relation_data(),
82.             )
83.         except CharmConfigInvalidError as exc:
84.             self.unit.status = ops.BlockedStatus(exc.msg)
85.             return
86.         self.framework.observe(self.on.config_changed, self._on_config_changed)
87.         self.framework.observe(self.on.leader_elected, self._on_leader_elected)
88.         self.framework.observe(self.on.indico_pebble_ready, self._on_pebble_ready)
89.         self.framework.observe(self.on.indico_nginx_pebble_ready, self._on_pebble_ready)
90.         self.framework.observe(
91.             self.on.refresh_external_resources_action, self._refresh_external_resources_action
92.         )
93.         # self.framework.observe(self.on.update_status, self._refresh_external_resources)
94.         self.framework.observe(self.on.add_admin_action, self._add_admin_action)
95.         self.framework.observe(self.on.anonymize_user_action, self._anonymize_user_action)
96.         self.redis_broker = RedisRequires(self, "redis-broker")
97.         self.framework.observe(
98.             self.redis_broker.charm.on.redis_relation_updated, self._on_config_changed
99.         )
100.         self.redis_cache = RedisRequires(self, "redis-cache")
101.         self.framework.observe(
102.             self.redis_cache.charm.on.redis_relation_updated, self._on_config_changed
103.         )
104.         self.framework.observe(
105.             self.on["indico-peers"].relation_departed, self._on_peer_relation_departed
106.         )
107.         self._require_nginx_route()
108. 
109.         self._metrics_endpoint = MetricsEndpointProvider(
110.             self,
111.             jobs=[
112.                 {
113.                     "static_configs": [
114.                         {
115.                             "targets": [
116.                                 f"*:{NGINX_PROMEXP_PORT}",
117.                                 f"*:{STATSD_PROMEXP_PORT}",
118.                                 f"*:{CELERY_PROMEXP_PORT}",
119.                             ]
120.                         }
```

</details>


---

<sub>⏱️ 2m 30s</sub>

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/indico-operator__pebble-check-events__C3/src/charm.py.**

/tmp/ops-upgrade-experiment/indico-operator__pebble-check-events__C3/src/charm.py (lines 120-230)

<details>
<summary>111 lines</summary>

```
120.                         }
121.                     ]
122.                 }
123.             ],
124.         )
125.         self._grafana_dashboards = GrafanaDashboardProvider(self)
126.         # port 9080 conflicts with the nginx exporter
127.         charms.loki_k8s.v0.loki_push_api.HTTP_LISTEN_PORT = 9090
128.         self._logging = LogProxyConsumer(
129.             self,
130.             relation_name="logging",
131.             log_files="/srv/indico/log/*",
132.             container_name="indico",
133.         )
134. 
135.     def _require_nginx_route(self) -> None:
136.         """Require nginx ingress."""
137.         require_nginx_route(
138.             charm=self,
139.             service_hostname=self._get_external_hostname(),
140.             service_name=self.app.name,
141.             service_port=8080,
142.         )
143. 
144.     def _are_pebble_instances_ready(self) -> bool:
145.         """Check if all pebble instances are up and containers available.
146. 
147.         Returns:
148.             If the containers are up and available.
149.         """
150.         return all(
151.             self.unit.get_container(container_name).can_connect()
152.             for container_name in self.model.unit.containers
153.         )
154. 
155.     def _is_configuration_valid(self) -> Tuple[bool, str]:
156.         """Validate charm configuration.
157. 
158.         Returns:
159.             Tuple containing as first element whether the configuration is valid.
160.             and a string with the error, if any, as second element.
161.         """
162.         site_url = typing.cast(str, self.config["site_url"])
163.         if site_url and not urlparse(site_url).hostname:
164.             return False, "Configuration option site_url is not valid"
165.         return True, ""
166. 
167.     def _get_external_hostname(self) -> str:
168.         """Extract and return hostname from site_url or default to [application name].local.
169. 
170.         Returns:
171.             The site URL defined as part of the site_url configuration or a default value.
172.         """
173.         site_url = typing.cast(str, self.config["site_url"])
174.         if not site_url or not (hostname := urlparse(site_url).hostname):
175.             return f"{self.app.name}.local"
176.         return hostname
177. 
178.     def _get_external_scheme(self) -> str:
179.         """Extract and return schema from site_url.
180. 
181.         Returns:
182.             The HTTP schema.
183.         """
184.         site_url = typing.cast(str, self.config["site_url"])
185.         return urlparse(site_url).scheme if site_url else "http"
186. 
187.     def _get_external_port(self) -> Optional[int]:
188.         """Extract and return port from site_url.
189. 
190.         Returns:
191.             The port number.
192.         """
193.         site_url = typing.cast(str, self.config["site_url"])
194.         return urlparse(site_url).port
195. 
196.     def _are_relations_ready(self, _) -> bool:
197.         """Check if the needed relations are established.
198. 
199.         Returns:
200.             If the needed relations have been established.
201.         """
202.         if self.redis_broker.relation_data is None:
203.             self.unit.status = WaitingStatus("Waiting for redis-broker availability")
204.             return False
205.         if self.redis_cache.relation_data is None:
206.             self.unit.status = WaitingStatus("Waiting for redis-cache availability")
207.             return False
208.         if self.database.uri is None:
209.             self.unit.status = WaitingStatus("Waiting for database availability")
210.             return False
211.         return True
212. 
213.     def _on_pebble_ready(self, event: PebbleReadyEvent) -> None:
214.         """Handle the on pebble ready event for the containers.
215. 
216.         Args:
217.             event: Event triggering the pebble ready handler.
218.         """
219.         if not self._are_relations_ready(event) or not event.workload.can_connect():
220.             event.defer()
221.             return
222.         self._config_pebble(event.workload)
223. 
224.     def _config_pebble(self, container: Container) -> None:
225.         """Apply pebble configurations to a container.
226. 
227.         Args:
228.             container: Container to be configured by Pebble.
229.         """
230.         self.unit.status = MaintenanceStatus(f"Adding {container.name} layer to pebble")
```

</details>


---

<sub>⏱️ 2m 37s</sub>

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/indico-operator__pebble-check-events__C3/src/charm.py.**

/tmp/ops-upgrade-experiment/indico-operator__pebble-check-events__C3/src/charm.py (lines 230-330)

<details>
<summary>101 lines</summary>

```
230.         self.unit.status = MaintenanceStatus(f"Adding {container.name} layer to pebble")
231.         if container.name == "indico":
232.             # Plugins need to be installed before adding the layer so that
233.             # they are included in the corresponding env vars
234.             plugins = (
235.                 typing.cast(str, self.config["external_plugins"]).split(",")
236.                 if self.config["external_plugins"]
237.                 else []
238.             )
239.             self._install_plugins(container, plugins)
240.             container.add_layer(container.name, self._get_logrotate_config(), combine=True)
241.             indico_config = self._get_indico_pebble_config(container)
242.             container.add_layer(container.name, indico_config, combine=True)
243.             peer_relation = self.model.get_relation("indico-peers")
244.             if (
245.                 not peer_relation
246.                 or peer_relation.data[self.app].get("celery-unit") == self.unit.name
247.             ):
248.                 celery_config = self._get_celery_pebble_config(container)
249.                 container.add_layer("celery", celery_config, combine=True)
250.                 celery_exporter_config = self._get_celery_prometheus_exporter_pebble_config(
251.                     container
252.                 )
253.                 container.add_layer("celery-exporter", celery_exporter_config, combine=True)
254.             statsd_config = self._get_statsd_prometheus_exporter_pebble_config(container)
255.             container.add_layer("statsd", statsd_config, combine=True)
256.             self._download_customization_changes(container)
257.         if container.name == "indico-nginx":
258.             nginx_config = self._get_nginx_pebble_config(container)
259.             container.add_layer(container.name, nginx_config, combine=True)
260.             nginx_exporter_config = self._get_nginx_prometheus_exporter_pebble_config(container)
261.             container.add_layer("nginx", nginx_exporter_config, combine=True)
262.         self.unit.status = MaintenanceStatus(f"Starting {container.name} container")
263.         container.pebble.replan_services()
264.         if self._are_pebble_instances_ready():
265.             self.unit.set_workload_version(self._get_indico_version())
266.             self.unit.status = ActiveStatus()
267.         else:
268.             self.unit.status = WaitingStatus("Waiting for pebble")
269. 
270.     def _get_logrotate_config(self) -> ops.pebble.LayerDict:
271.         """Generate logrotate pebble layer.
272. 
273.         Returns:
274.             The logrotate pebble layer configuration.
275.         """
276.         layer = {
277.             "summary": "Logrotate service",
278.             "description": "Logrotate service",
279.             "services": {
280.                 "logrotate": {
281.                     "override": "replace",
282.                     "command": 'bash -c "while :; '
283.                     "do sleep 3600; logrotate /srv/indico/logrotate.conf; "
284.                     'done"',
285.                     "startup": "enabled",
286.                 },
287.             },
288.         }
289.         return typing.cast(ops.pebble.LayerDict, layer)
290. 
291.     def _get_indico_pebble_config(self, container: Container) -> ops.pebble.LayerDict:
292.         """Generate pebble config for the indico container.
293. 
294.         Args:
295.             container: Indico container that has the target configuration.
296. 
297.         Returns:
298.             The pebble configuration for the container.
299.         """
300.         indico_env_config = self._get_indico_env_config(container)
301.         indico_env_config["INDICO_LOGGING_CONFIG_FILE"] = "indico.logging.yaml"
302.         layer = {
303.             "summary": "Indico layer",
304.             "description": "Indico layer",
305.             "services": {
306.                 "indico": {
307.                     "override": "replace",
308.                     "summary": "Indico service",
309.                     "command": "/srv/indico/start-indico.sh",
310.                     "startup": "enabled",
311.                     "user": "indico",
312.                     "environment": indico_env_config,
313.                 },
314.             },
315.             "checks": {
316.                 "indico-ready": {
317.                     "override": "replace",
318.                     "level": "ready",
319.                     "tcp": {"port": 8081},
320.                 },
321.             },
322.         }
323.         return typing.cast(ops.pebble.LayerDict, layer)
324. 
325.     def _get_celery_pebble_config(self, container: Container) -> ops.pebble.LayerDict:
326.         """Generate pebble config for the celery container.
327. 
328.         Args:
329.             container: Celery container that has the target configuration.
330.
```

</details>


---

<sub>⏱️ 2m 51s</sub>

### 💬 Copilot

Now let me look at the existing tests to understand the test structure:

---

<sub>⏱️ 2m 51s</sub>

### ✅ `bash`

**List test files**

$ ls /tmp/ops-upgrade-experiment/indico-operator__pebble-check-events__C3/tests/unit/ && echo "---" && ls /tmp/ops-upgrade-experiment/indico-operator__pebble-check-events__C3/tests/unit_harness/ | head -20

<details>
<summary>14 lines</summary>

```
__init__.py  conftest.py  test_on_leader_elected.py
---
__init__.py
conftest.py
pre_run_script.sh
test_actions.py
test_base.py
test_core.py
test_database_observer.py
test_s3_observer.py
test_saml_observer.py
test_smtp_observer.py
test_state.py
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 2m 51s</sub>

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/indico-operator__pebble-check-events__C3/src/charm.py.**

/tmp/ops-upgrade-experiment/indico-operator__pebble-check-events__C3/src/charm.py (lines 670-710)

<details>
<summary>41 lines</summary>

```
670.             Map containing the HTTP_PROXY environment variables.
671.         """
672.         if proxy:
673.             return {
674.                 "HTTP_PROXY": str(proxy.http_proxy),
675.                 "HTTPS_PROXY": str(proxy.https_proxy),
676.                 "NO_PROXY": str(proxy.no_proxy),
677.             }
678.         return {}
679. 
680.     def _on_config_changed(self, event: HookEvent) -> None:
681.         """Handle changes in configuration.
682. 
683.         Args:
684.             event: Event triggering the configuration change handler.
685.         """
686.         if not self._are_relations_ready(event):
687.             return
688.         if not self._are_pebble_instances_ready():
689.             self.unit.status = WaitingStatus("Waiting for pebble")
690.             return
691.         self.model.unit.status = MaintenanceStatus("Configuring pod")
692.         is_valid, error = self._is_configuration_valid()
693.         if not is_valid:
694.             self.model.unit.status = BlockedStatus(error)
695.             return
696.         for container_name in self.model.unit.containers:
697.             self._config_pebble(self.unit.get_container(container_name))
698. 
699.     def _get_current_customization_url(self) -> str:
700.         """Get the current remote repository for the customization changes.
701. 
702.         Returns:
703.             The customization URL.
704.         """
705.         indico_container = self.unit.get_container("indico")
706.         process = indico_container.exec(
707.             ["git", "config", "--get", "remote.origin.url"],
708.             working_dir=INDICO_CUSTOMIZATION_DIR,
709.             user="indico",
710.         )
```

</details>


---

<sub>⏱️ 2m 56s</sub>

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/indico-operator__pebble-check-events__C3/tests/unit/conftest.py.**

/tmp/ops-upgrade-experiment/indico-operator__pebble-check-events__C3/tests/unit/conftest.py

<details>
<summary>34 lines</summary>

```
1. # Copyright 2025 Canonical Ltd.
2. # See LICENSE file for licensing details.
3. 
4. """Fixtures for unit tests."""
5. 
6. import pytest
7. from ops import pebble, testing
8. 
9. 
10. @pytest.fixture(scope="function", name="base_state")
11. def base_state_fixture():
12.     """State with container and config file set."""
13.     pebble_layer = pebble.Layer(
14.         {
15.             "summary": "indico layer",
16.             "description": "pebble config layer for indico",
17.             "services": {
18.                 "indico": {},
19.             },
20.         }
21.     )
22.     yield {
23.         "leader": True,
24.         "containers": {
25.             # mypy throws an error because it validates against ops.Container.
26.             testing.Container(  # type: ignore[call-arg]
27.                 name="indico",
28.                 can_connect=True,
29.                 layers={"indico": pebble_layer},
30.                 service_statuses={"indico": pebble.ServiceStatus.ACTIVE},
31.             )
32.         },
33.     }
34.
```

</details>


---

<sub>⏱️ 2m 57s</sub>

### ✅ `bash`

**Look at existing unit test structure**

$ head -80 /tmp/ops-upgrade-experiment/indico-operator__pebble-check-events__C3/tests/unit/test_on_leader_elected.py

<details>
<summary>26 lines</summary>

```
# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

"""Indico charm unit tests."""

from unittest.mock import MagicMock, patch

import ops
from ops import testing

from charm import IndicoOperatorCharm


@patch.object(ops.JujuVersion, "from_environ")
def test_on_leader_elected_when_secrets_supported(mock_juju_env, base_state: dict):
    """
    arrange: charm created, leader selected and secrets supported
    act: re-trigger the leader elected event
    assert: the peer relation containers the secret-key
    """
    mock_juju_env.return_value = MagicMock(has_secrets=True)
    base_state["relations"] = [testing.PeerRelation("indico-peers")]
    state = testing.State(**base_state)
    context = testing.Context(
        charm_type=IndicoOperatorCharm,
    )

    state = context.run(context.on.leader_elected(), state)

    secret_id = state.get_relations("indico-peers")[0].local_app_data["secret-id"]
    context.run(context.on.leader_elected(), state)

    assert state.get_relations("indico-peers")[0].local_app_data["secret-id"]
    assert secret_id == state.get_relations("indico-peers")[0].local_app_data["secret-id"]
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 3m 19s</sub>

### ✅ `bash`

**Check ops version**

$ cd /tmp/ops-upgrade-experiment/indico-operator__pebble-check-events__C3 && grep "^ops" requirements.txt && pip show ops 2>/dev/null | grep Version || pip3 show ops 2>/dev/null | grep Version

```
ops>=2.0.0,<3.0.0
Version: 3.7.0
<exited with exit code 0>
```


---

<sub>⏱️ 3m 44s</sub>

### ✅ `bash`

**Verify imports available**

$ python3 -c "from ops import PebbleCheckFailedEvent, PebbleCheckRecoveredEvent; print('OK')"

```
OK
<exited with exit code 0>
```


---

<sub>⏱️ 4m 12s</sub>

### 💬 Copilot

Good. Now I have everything I need. Let me implement the changes:

---

<sub>⏱️ 4m 12s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/indico-operator__pebble-check-events__C3/src/charm.py.**

/tmp/ops-upgrade-experiment/indico-operator__pebble-check-events__C3/src/charm.py

```
File /tmp/ops-upgrade-experiment/indico-operator__pebble-check-events__C3/src/charm.py updated with changes.
```


---

<sub>⏱️ 4m 39s</sub>

### 💬 Copilot

Now add the event observer registrations after the existing pebble_ready observers:

---

<sub>⏱️ 4m 39s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/indico-operator__pebble-check-events__C3/src/charm.py.**

/tmp/ops-upgrade-experiment/indico-operator__pebble-check-events__C3/src/charm.py

```
File /tmp/ops-upgrade-experiment/indico-operator__pebble-check-events__C3/src/charm.py updated with changes.
```


---

<sub>⏱️ 5m 5s</sub>

### 💬 Copilot

Now add the handler methods. Let me find a good place to insert them — right after `_on_pebble_ready`:

---

<sub>⏱️ 5m 5s</sub>

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/indico-operator__pebble-check-events__C3/src/charm.py.**

/tmp/ops-upgrade-experiment/indico-operator__pebble-check-events__C3/src/charm.py (lines 220-245)

<details>
<summary>26 lines</summary>

```
220.             If the needed relations have been established.
221.         """
222.         if self.redis_broker.relation_data is None:
223.             self.unit.status = WaitingStatus("Waiting for redis-broker availability")
224.             return False
225.         if self.redis_cache.relation_data is None:
226.             self.unit.status = WaitingStatus("Waiting for redis-cache availability")
227.             return False
228.         if self.database.uri is None:
229.             self.unit.status = WaitingStatus("Waiting for database availability")
230.             return False
231.         return True
232. 
233.     def _on_pebble_ready(self, event: PebbleReadyEvent) -> None:
234.         """Handle the on pebble ready event for the containers.
235. 
236.         Args:
237.             event: Event triggering the pebble ready handler.
238.         """
239.         if not self._are_relations_ready(event) or not event.workload.can_connect():
240.             event.defer()
241.             return
242.         self._config_pebble(event.workload)
243. 
244.     def _config_pebble(self, container: Container) -> None:
245.         """Apply pebble configurations to a container.
```

</details>


---

<sub>⏱️ 5m 37s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/indico-operator__pebble-check-events__C3/src/charm.py.**

/tmp/ops-upgrade-experiment/indico-operator__pebble-check-events__C3/src/charm.py

```
File /tmp/ops-upgrade-experiment/indico-operator__pebble-check-events__C3/src/charm.py updated with changes.
```


---

<sub>⏱️ 6m 1s</sub>

### 💬 Copilot

Now let me add the unit tests. First check the existing test file pattern more carefully:

---

<sub>⏱️ 6m 1s</sub>

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/indico-operator__pebble-check-events__C3/tests/unit/test_on_leader_elected.py.**

/tmp/ops-upgrade-experiment/indico-operator__pebble-check-events__C3/tests/unit/test_on_leader_elected.py

<details>
<summary>35 lines</summary>

```
1. # Copyright 2025 Canonical Ltd.
2. # See LICENSE file for licensing details.
3. 
4. """Indico charm unit tests."""
5. 
6. from unittest.mock import MagicMock, patch
7. 
8. import ops
9. from ops import testing
10. 
11. from charm import IndicoOperatorCharm
12. 
13. 
14. @patch.object(ops.JujuVersion, "from_environ")
15. def test_on_leader_elected_when_secrets_supported(mock_juju_env, base_state: dict):
16.     """
17.     arrange: charm created, leader selected and secrets supported
18.     act: re-trigger the leader elected event
19.     assert: the peer relation containers the secret-key
20.     """
21.     mock_juju_env.return_value = MagicMock(has_secrets=True)
22.     base_state["relations"] = [testing.PeerRelation("indico-peers")]
23.     state = testing.State(**base_state)
24.     context = testing.Context(
25.         charm_type=IndicoOperatorCharm,
26.     )
27. 
28.     state = context.run(context.on.leader_elected(), state)
29. 
30.     secret_id = state.get_relations("indico-peers")[0].local_app_data["secret-id"]
31.     context.run(context.on.leader_elected(), state)
32. 
33.     assert state.get_relations("indico-peers")[0].local_app_data["secret-id"]
34.     assert secret_id == state.get_relations("indico-peers")[0].local_app_data["secret-id"]
35.
```

</details>


---

<sub>⏱️ 6m 1s</sub>

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/indico-operator__pebble-check-events__C3/tests/unit/conftest.py.**

/tmp/ops-upgrade-experiment/indico-operator__pebble-check-events__C3/tests/unit/conftest.py

<details>
<summary>34 lines</summary>

```
1. # Copyright 2025 Canonical Ltd.
2. # See LICENSE file for licensing details.
3. 
4. """Fixtures for unit tests."""
5. 
6. import pytest
7. from ops import pebble, testing
8. 
9. 
10. @pytest.fixture(scope="function", name="base_state")
11. def base_state_fixture():
12.     """State with container and config file set."""
13.     pebble_layer = pebble.Layer(
14.         {
15.             "summary": "indico layer",
16.             "description": "pebble config layer for indico",
17.             "services": {
18.                 "indico": {},
19.             },
20.         }
21.     )
22.     yield {
23.         "leader": True,
24.         "containers": {
25.             # mypy throws an error because it validates against ops.Container.
26.             testing.Container(  # type: ignore[call-arg]
27.                 name="indico",
28.                 can_connect=True,
29.                 layers={"indico": pebble_layer},
30.                 service_statuses={"indico": pebble.ServiceStatus.ACTIVE},
31.             )
32.         },
33.     }
34.
```

</details>


---

<sub>⏱️ 6m 27s</sub>

### ✅ `bash`

**Check how pebble check events work in ops testing**

$ python3 -c "import ops.testing; help(ops.testing.Context.on)" 2>&1 | grep -i "check" | head -20

```

<exited with exit code 0>
```


---

<sub>⏱️ 6m 58s</sub>

### ✅ `bash`

**Find pebble check event methods**

$ python3 -c "import ops.testing; t = dir(ops.testing.Context.on); print([x for x in t if 'check' in x.lower() or 'pebble' in x.lower()])"

```
Traceback (most recent call last):
  File "<string>", line 1, in <module>
AttributeError: type object 'Context' has no attribute 'on'
<exited with exit code 1>
```


---

<sub>⏱️ 6m 58s</sub>

### ✅ `bash`

**Check pebble_check_failed signature**

$ python3 -c "from ops import testing, pebble; help(testing.Context.on.pebble_check_failed)" 2>&1 | head -30

```
Traceback (most recent call last):
  File "<string>", line 1, in <module>
AttributeError: type object 'Context' has no attribute 'on'
<exited with exit code 0>
```


---

<sub>⏱️ 7m 30s</sub>

### ✅ `bash`

**Find check event API**

$ python3 -c "
from ops import testing, pebble
ctx = testing.Context.__new__(testing.Context)
print([x for x in dir(ctx.on) if 'check' in x.lower() or 'pebble' in x.lower()])
" 2>&1 || python3 -c "from ops import testing; import inspect; print([m for m in dir(testing) if 'check' in m.lower() or 'Check' in m])"

```
Traceback (most recent call last):
  File "<string>", line 4, in <module>
AttributeError: 'Context' object has no attribute 'on'
['CheckInfo']
<exited with exit code 0>
```


---

<sub>⏱️ 7m 53s</sub>

### ✅ `bash`

**Check CheckInfo signature**

$ python3 -c "from ops import testing; help(testing.CheckInfo)" 2>&1 | head -30

<details>
<summary>30 lines</summary>

```
Help on class CheckInfo in module scenario.state:

class CheckInfo(builtins.object)
 |  CheckInfo(name: 'str', *, level: 'pebble.CheckLevel | str | None' = None, startup: 'pebble.CheckStartup' = <CheckStartup.ENABLED: 'enabled'>, status: 'pebble.CheckStatus' = <CheckStatus.UP: 'up'>, successes: 'int | None' = 0, failures: 'int' = 0, threshold: 'int' = 3, change_id: 'pebble.ChangeID | None' = None)
 |
 |  A health check for a Pebble workload container.
 |
 |  Methods defined here:
 |
 |  __delattr__(self, name)
 |      Implement delattr(self, name).
 |
 |  __eq__(self, other)
 |      Return self==value.
 |
 |  __hash__(self) -> 'int'
 |      Return hash(self).
 |
 |  __init__(self, name: 'str', *, level: 'pebble.CheckLevel | str | None' = None, startup: 'pebble.CheckStartup' = <CheckStartup.ENABLED: 'enabled'>, status: 'pebble.CheckStatus' = <CheckStatus.UP: 'up'>, successes: 'int | None' = 0, failures: 'int' = 0, threshold: 'int' = 3, change_id: 'pebble.ChangeID | None' = None)
 |      Initialize self.  See help(type(self)) for accurate signature.
 |
 |  __repr__(self)
 |      Return repr(self).
 |
 |  __setattr__(self, name, value)
 |      Implement setattr(self, name, value).
 |
 |  ----------------------------------------------------------------------
 |  Data descriptors defined here:
 |
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 7m 53s</sub>

### ✅ `bash`

**Find pebble check event source**

$ python3 -c "
from ops import testing
# Look for how to fire pebble check events
import inspect
src = inspect.getsource(testing)
# Find pebble_check
idx = src.find('pebble_check')
print(src[max(0,idx-200):idx+500])
" 2>&1 | head -60

<details>
<summary>13 lines</summary>

```
# Copyright 2024 Canonical Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the sp
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 8m 22s</sub>

### ✅ `bash`

**Find how to emit pebble_check_failed**

$ python3 -c "
from ops import testing
import inspect
# Look at the CharmEvents class or on-attribute of Context
src = inspect.getsource(testing)
# Find pebble_check_failed
idx = src.find('pebble_check_failed')
print(src[max(0,idx-100):idx+600])
" 2>&1 | head -50

<details>
<summary>15 lines</summary>

```
# Copyright 2024 Canonical Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Framework for unit tes
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 8m 52s</sub>

### ✅ `bash`

**Find pebble check in ops testing source**

$ python3 -c "
import ops.testing._ops_testing as ot
import inspect
src = inspect.getsource(ot)
idx = src.find('pebble_check')
print(src[max(0,idx-100):idx+800])
" 2>&1 | head -60

```
Traceback (most recent call last):
  File "<string>", line 2, in <module>
ModuleNotFoundError: No module named 'ops.testing._ops_testing'; 'ops.testing' is not a package
<exited with exit code 0>
```


---

<sub>⏱️ 9m 27s</sub>

### ✅ `bash`

**Find in scenario module**

$ python3 -c "
import scenario
import inspect
src = inspect.getsource(scenario)
idx = src.find('pebble_check_failed')
print(src[max(0,idx-200):idx+600])
" 2>&1 | head -60

<details>
<summary>11 lines</summary>

```
# Copyright 2023 Canonical Ltd.
# See LICENSE file for licensing details.

"""Charm state-transition testing SDK for Ops charms.

Write tests that declaratively define the Juju state all at once, define the
Juju context against which to test the charm, and fire a single event on the
charm to execute its logic. The tests can then assert that the Juju state has
changed as expected.

These tests are 'state-transition' tests, a way to test isolated units of charm
functionality (how the state changes in reaction to events). They are not
necessarily tests of individual methods or functions (but mig
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 9m 27s</sub>

### ✅ `bash`

**Find ops package location**

$ python3 -c "
import ops
print(ops.__file__)
import os, glob
pkg_dir = os.path.dirname(ops.__file__)
print(glob.glob(pkg_dir + '/**/*.py', recursive=True))
" 2>&1 | head -20

```
/home/ubuntu/.local/lib/python3.12/site-packages/ops/__init__.py
['/home/ubuntu/.local/lib/python3.12/site-packages/ops/jujuversion.py', '/home/ubuntu/.local/lib/python3.12/site-packages/ops/_main.py', '/home/ubuntu/.local/lib/python3.12/site-packages/ops/log.py', '/home/ubuntu/.local/lib/python3.12/site-packages/ops/pebble.py', '/home/ubuntu/.local/lib/python3.12/site-packages/ops/jujucontext.py', '/home/ubuntu/.local/lib/python3.12/site-packages/ops/storage.py', '/home/ubuntu/.local/lib/python3.12/site-packages/ops/model.py', '/home/ubuntu/.local/lib/python3.12/site-packages/ops/version.py', '/home/ubuntu/.local/lib/python3.12/site-packages/ops/charm.py', '/home/ubuntu/.local/lib/python3.12/site-packages/ops/testing.py', '/home/ubuntu/.local/lib/python3.12/site-packages/ops/main.py', '/home/ubuntu/.local/lib/python3.12/site-packages/ops/__init__.py', '/home/ubuntu/.local/lib/python3.12/site-packages/ops/framework.py', '/home/ubuntu/.local/lib/python3.12/site-packages/ops/lib/__init__.py', '/home/ubuntu/.local/lib/python3.12/site-packages/ops/_private/timeconv.py', '/home/ubuntu/.local/lib/python3.12/site-packages/ops/_private/harness.py', '/home/ubuntu/.local/lib/python3.12/site-packages/ops/_private/yaml.py', '/home/ubuntu/.local/lib/python3.12/site-packages/ops/_private/__init__.py', '/home/ubuntu/.local/lib/python3.12/site-packages/ops/hookcmds/_relation.py', '/home/ubuntu/.local/lib/python3.12/site-packages/ops/hookcmds/_storage.py', '/home/ubuntu/.local/lib/python3.12/site-packages/ops/hookcmds/_state.py', '/home/ubuntu/.local/lib/python3.12/site-packages/ops/hookcmds/_status.py', '/home/ubuntu/.local/lib/python3.12/site-packages/ops/hookcmds/_action.py', '/home/ubuntu/.local/lib/python3.12/site-packages/ops/hookcmds/_other.py', '/home/ubuntu/.local/lib/python3.12/site-packages/ops/hookcmds/_types.py', '/home/ubuntu/.local/lib/python3.12/site-packages/ops/hookcmds/_secret.py', '/home/ubuntu/.local/lib/python3.12/site-packages/ops/hookcmds/_port.py', '/home/ubuntu/.local/lib/python3.12/site-packages/ops/hookcmds/__init__.py', '/home/ubuntu/.local/lib/python3.12/site-packages/ops/hookcmds/_utils.py']
<exited with exit code 0>
```


---

<sub>⏱️ 9m 48s</sub>

### ❌ `bash`

**Find pebble check in ops testing**

$ grep -n "pebble_check" /home/ubuntu/.local/lib/python3.12/site-packages/ops/testing.py | head -30

```
Permission denied and could not request permission from user
```


---

<sub>⏱️ 10m 22s</sub>

### ✅ `bash`

**Find scenario package location**

$ pip show ops-scenario 2>/dev/null | head -5; python3 -c "import scenario; print(scenario.__file__)"

<details>
<summary>7 lines</summary>

```
Name: ops-scenario
Version: 8.7.0
Summary: Python library providing a state-transition testing API for Operator Framework charms.
Home-page: 
Author: 
/home/ubuntu/.local/lib/python3.12/site-packages/scenario/__init__.py
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 10m 52s</sub>

### ❌ `bash`

**Find pebble check failed in scenario**

$ grep -n "pebble_check" /home/ubuntu/.local/lib/python3.12/site-packages/scenario/_context.py 2>/dev/null | head -20; grep -rn "pebble_check_failed" /home/ubuntu/.local/lib/python3.12/site-packages/scenario/ 2>/dev/null | head -20

```
Permission denied and could not request permission from user
```


---

<sub>⏱️ 11m 21s</sub>

### ✅ `bash`

**Find pebble check failed in scenario context**

$ python3 -c "
import scenario._context as ctx
import inspect
src = inspect.getsource(ctx)
idx = src.find('pebble_check_failed')
print(src[max(0,idx-100):idx+600] if idx >= 0 else 'NOT FOUND')
"

```
Traceback (most recent call last):
  File "<string>", line 2, in <module>
ModuleNotFoundError: No module named 'scenario._context'
<exited with exit code 1>
```


---

<sub>⏱️ 11m 51s</sub>

### ✅ `bash`

**List scenario public API**

$ python3 -c "
import scenario
mods = [x for x in dir(scenario) if not x.startswith('_')]
print(mods)
"

```
['ActionFailed', 'ActiveStatus', 'Address', 'AnyJson', 'BindAddress', 'BlockedStatus', 'CharmEvents', 'CharmType', 'CheckInfo', 'CloudCredential', 'CloudSpec', 'Container', 'Context', 'DeferredEvent', 'ErrorStatus', 'Exec', 'ICMPPort', 'JujuLogLine', 'MaintenanceStatus', 'Manager', 'Model', 'Mount', 'Network', 'Notice', 'PeerRelation', 'Port', 'RawDataBagContents', 'RawSecretRevisionContents', 'Relation', 'RelationBase', 'Resource', 'Secret', 'State', 'StateValidationError', 'Storage', 'StoredState', 'SubordinateRelation', 'TCPPort', 'UDPPort', 'UnitID', 'UnknownStatus', 'WaitingStatus', 'annotations', 'context', 'errors', 'layer_from_rockcraft', 'logger', 'state']
<exited with exit code 0>
```


---

<sub>⏱️ 12m 22s</sub>

### ✅ `bash`

**Find context methods related to pebble checks**

$ python3 -c "
import scenario
ctx = scenario.Context.__new__(scenario.Context)
print([x for x in dir(ctx) if 'check' in x.lower() or 'pebble' in x.lower()])
"

```
[]
<exited with exit code 0>
```


---

<sub>⏱️ 12m 54s</sub>

### ✅ `bash`

**Check ops.testing for pebble check API**

$ python3 -c "
import ops.testing as ot
print([x for x in dir(ot) if 'check' in x.lower() or 'pebble' in x.lower()])
"

```
['CheckInfo', 'pebble']
<exited with exit code 0>
```


---

<sub>⏱️ 13m 35s</sub>

### ✅ `bash`

**Check Context methods for pebble checks**

$ python3 -c "
from ops import testing
# How to fire pebble check events - look at Context event methods
import inspect
ctx_methods = [m for m in dir(testing.Context) if 'pebble' in m.lower() or 'check' in m.lower()]
print('Context methods:', ctx_methods)
# Check the on property  
c = testing.Context.__new__(testing.Context)
"

```
Context methods: []
<exited with exit code 0>
```


---

<sub>⏱️ 13m 55s</sub>

### ✅ `bash`

**Look at ops testing source**

$ python3 -c "
from ops import testing
import inspect
# Look at source of testing module 
src = inspect.getsource(testing)
print(src[:3000])
"

<details>
<summary>89 lines</summary>

```
# Copyright 2024 Canonical Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Framework for unit testing charms in a simulated Juju environment.

The module includes:

- :class:`ops.testing.Context`, :class:`ops.testing.State`, and other classes
  to represent the simulated Juju environment for state-transition testing.
  These are available when the `ops[testing]` optional extra is installed.
- :class:`ops.testing.Harness`, a deprecated class to set up the simulated environment,
  that provides:

  - :meth:`~ops.testing.Harness.add_relation` method, to declare a relation
    (integration) with another app.
  - :meth:`~ops.testing.Harness.begin` and :meth:`~ops.testing.Harness.cleanup`
    methods to start and end the testing lifecycle.
  - :meth:`~ops.testing.Harness.evaluate_status` method, which aggregates the
    status of the charm after test interactions.
  - :attr:`~ops.testing.Harness.model` attribute, which exposes e.g. the
    :attr:`~ops.Model.unit` attribute for detailed assertions on the unit's state.

.. note::
    Unit testing is only one aspect of a comprehensive testing strategy. For more
    on testing charms, see `Testing <https://documentation.ubuntu.com/ops/latest/explanation/testing/>`_.
"""

# ruff: noqa: F401 (unused import)
# pyright: reportUnusedImport=false

from __future__ import annotations

from . import charm, framework, model, pebble, storage
from ._private.harness import (
    ActionFailed,
    ActionOutput,
    AppUnitOrName,
    CharmType,
    ExecArgs,
    ExecHandler,
    ExecResult,
    Harness,
    ReadableBuffer,
    YAMLStringOrFile,
)
from .charm import CharmBase, CharmMeta, RelationRole
from .model import RelationNotFoundError
from .pebble import ExecProcess

# The Harness unit testing framework.
__all__ = [
    'ActionFailed',
    'ActionOutput',
    'AppUnitOrName',
    'CharmType',
    'ExecArgs',
    'ExecHandler',
    'ExecResult',
    'Harness',
    'ReadableBuffer',
    'YAMLStringOrFile',
]

# If the 'ops.testing' optional extra is installed, make those
# names available in this namespace.
try:
    from scenario import (
        ActiveStatus,
        Address,
        AnyJson,
        BindAddress,
        BlockedStatus,
        CharmEvents,
        CheckInfo,
        CloudCredential,
        CloudSpec,
        Container,
        Context,
        DeferredEvent,
        ErrorStatus,
        Exec,
        ICMPPort,
        JujuLogLine,
        MaintenanceStatus,
        Manager,
        Model,
        Mount,
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 14m 25s</sub>

### ✅ `bash`

**Find pebble_check in testing source**

$ python3 -c "
from ops import testing
import inspect
src = inspect.getsource(testing)
idx = src.find('pebble_check')
print(src[max(0,idx-200):idx+500] if idx >= 0 else 'not found')
"

```
not found
<exited with exit code 0>
```


---

<sub>⏱️ 14m 57s</sub>

### ℹ️ Info

Operation cancelled by user

---

<sub>Generated by [GitHub Copilot CLI](https://github.com/features/copilot/cli)</sub>
