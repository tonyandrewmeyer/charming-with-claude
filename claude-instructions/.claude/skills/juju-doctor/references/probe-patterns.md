# juju-doctor Probe Patterns Reference

Comprehensive patterns for writing juju-doctor probes, organised by validation category.

## Artifact Data Structures

### Status Artifact (`juju status --format=yaml`)

The `status` function receives `dict[str, dict]` where keys are model names:

```python
{
    "mymodel": {
        "model": {
            "name": "mymodel",
            "type": "iaas",  # or "caas" for K8s
            "controller": "lxd",
            "cloud": "localhost",
            "region": "localhost",
            "version": "3.6.0",
        },
        "machines": {
            "0": {
                "juju-status": {"current": "started"},
                "hostname": "juju-abc123-0",
                "ip-addresses": ["10.0.0.1"],
                "instance-id": "juju-abc123-0",
                "series": "jammy",
            }
        },
        "applications": {
            "myapp": {
                "charm": "myapp",
                "charm-origin": "local",
                "charm-rev": 1,
                "application-status": {
                    "current": "active",
                    "message": "Ready",
                },
                "relations": {
                    "database": ["postgresql"],
                },
                "units": {
                    "myapp/0": {
                        "workload-status": {
                            "current": "active",
                            "message": "Ready",
                        },
                        "juju-status": {
                            "current": "idle",
                        },
                        "machine": "0",
                        "leader": True,
                        "open-ports": ["8080/tcp"],
                    }
                },
            }
        },
    }
}
```

### Bundle Artifact (`juju export-bundle`)

The `bundle` function receives `dict[str, dict]`:

```python
{
    "mymodel": {
        "applications": {
            "myapp": {
                "charm": "myapp",
                "num_units": 1,
                "options": {"port": 8080},
                "constraints": "cores=2 mem=4G",
                "to": ["0"],
            }
        },
        "machines": {"0": {}},
        "relations": [
            ["myapp:database", "postgresql:db"],
        ],
    }
}
```

### Show-Unit Artifact (`juju show-unit --format=yaml`)

The `show_unit` function receives `dict[str, dict]`:

```python
{
    "mymodel": {
        "myapp/0": {
            "machine": "0",
            "workload-status": {
                "current": "active",
                "message": "Ready",
            },
            "juju-status": {"current": "idle"},
            "leader": True,
            "relation-info": [
                {
                    "endpoint": "database",
                    "related-endpoint": "db",
                    "related-units": {
                        "postgresql/0": {
                            "in-scope": True,
                            "data": {
                                "host": "10.0.0.2",
                                "port": "5432",
                            },
                        }
                    },
                }
            ],
        }
    }
}
```

## Probe Patterns by Category

### Health Checks

#### All Units Active and Idle

```python
def status(juju_statuses: dict[str, dict]):
    """Every unit must be active/idle."""
    errors = []
    for model, data in juju_statuses.items():
        for app, app_data in data.get("applications", {}).items():
            for unit, unit_data in app_data.get("units", {}).items():
                ws = unit_data.get("workload-status", {})
                agent = unit_data.get("juju-status", {})
                if ws.get("current") != "active":
                    errors.append(
                        f"{unit}: workload is {ws.get('current')} "
                        f"({ws.get('message', 'no message')})"
                    )
                if agent.get("current") != "idle":
                    errors.append(
                        f"{unit}: agent is {agent.get('current')}"
                    )
    if errors:
        raise Exception("\n".join(errors))
```

#### No Blocked or Error Status

```python
def status(juju_statuses: dict[str, dict]):
    """No application should be blocked or in error."""
    errors = []
    for model, data in juju_statuses.items():
        for app, app_data in data.get("applications", {}).items():
            app_status = app_data.get("application-status", {})
            current = app_status.get("current", "")
            if current in ("blocked", "error"):
                msg = app_status.get("message", "no message")
                errors.append(f"{app}: {current} — {msg}")
            for unit, unit_data in app_data.get("units", {}).items():
                ws = unit_data.get("workload-status", {})
                if ws.get("current") in ("blocked", "error"):
                    msg = ws.get("message", "no message")
                    errors.append(f"{unit}: {ws['current']} — {msg}")
    if errors:
        raise Exception("\n".join(errors))
```

#### Machines Started

```python
def status(juju_statuses: dict[str, dict]):
    """All machines must be in 'started' state."""
    for model, data in juju_statuses.items():
        for machine_id, machine in data.get("machines", {}).items():
            state = machine.get("juju-status", {}).get("current", "")
            if state != "started":
                raise Exception(
                    f"Machine {machine_id} in {model}: {state}"
                )
```

### Relation Checks

#### Required Relations Present

```python
REQUIRED_RELATIONS = {
    "myapp": {"database", "ingress"},
    "postgresql": {"db"},
}

def status(juju_statuses: dict[str, dict]):
    """Check that required relations are established."""
    for model, data in juju_statuses.items():
        for app, app_data in data.get("applications", {}).items():
            required = REQUIRED_RELATIONS.get(app, set())
            if not required:
                continue
            actual = set(app_data.get("relations", {}).keys())
            missing = required - actual
            if missing:
                raise Exception(
                    f"{app} in {model}: missing relations: {missing}"
                )
```

#### Relation Data Populated

```python
def show_unit(juju_show_units: dict[str, dict]):
    """Check that relation data bags are populated."""
    for model, units in juju_show_units.items():
        for unit_name, unit_data in units.items():
            for rel in unit_data.get("relation-info", []):
                endpoint = rel.get("endpoint", "")
                for related_unit, rel_data in rel.get(
                    "related-units", {}
                ).items():
                    data = rel_data.get("data", {})
                    if not data:
                        raise Exception(
                            f"{unit_name}/{endpoint}: "
                            f"{related_unit} has empty data bag"
                        )
```

### Configuration Checks

#### Required Config Options Set

```python
REQUIRED_CONFIG = {
    "myapp": ["external-hostname", "tls-secret-name"],
}

def bundle(juju_bundles: dict[str, dict]):
    """Check that required config options are present."""
    for model, bundle_data in juju_bundles.items():
        for app, app_data in bundle_data.get("applications", {}).items():
            required = REQUIRED_CONFIG.get(app, [])
            options = app_data.get("options", {})
            for key in required:
                if key not in options or not options[key]:
                    raise Exception(
                        f"{app} in {model}: missing config '{key}'"
                    )
```

### Scale and Resource Checks

#### Minimum Unit Count

```python
MIN_UNITS = {
    "postgresql": 3,
    "myapp": 2,
}

def status(juju_statuses: dict[str, dict]):
    """Check applications have minimum required units."""
    for model, data in juju_statuses.items():
        for app, app_data in data.get("applications", {}).items():
            minimum = MIN_UNITS.get(app)
            if minimum is None:
                continue
            units = app_data.get("units", {})
            if len(units) < minimum:
                raise Exception(
                    f"{app} in {model}: has {len(units)} units, "
                    f"needs at least {minimum}"
                )
```

#### Open Ports Validation

```python
EXPECTED_PORTS = {
    "myapp": {"8080/tcp"},
    "nginx": {"80/tcp", "443/tcp"},
}

def status(juju_statuses: dict[str, dict]):
    """Check expected ports are open."""
    for model, data in juju_statuses.items():
        for app, app_data in data.get("applications", {}).items():
            expected = EXPECTED_PORTS.get(app)
            if expected is None:
                continue
            for unit, unit_data in app_data.get("units", {}).items():
                ports = set(unit_data.get("open-ports", []))
                missing = expected - ports
                if missing:
                    raise Exception(
                        f"{unit}: missing ports: {missing}"
                    )
```

### K8s-Specific Checks

#### Container Status (K8s Charms)

```python
def status(juju_statuses: dict[str, dict]):
    """Check K8s charm containers are running."""
    for model, data in juju_statuses.items():
        if data.get("model", {}).get("type") != "caas":
            continue
        for app, app_data in data.get("applications", {}).items():
            for unit, unit_data in app_data.get("units", {}).items():
                subordinates = unit_data.get("subordinates", {})
                # Check for container readiness indicators
                ws = unit_data.get("workload-status", {})
                if "pebble" in ws.get("message", "").lower() and \
                   ws.get("current") == "waiting":
                    raise Exception(
                        f"{unit}: Pebble not ready — {ws.get('message')}"
                    )
```

## Ruleset Patterns

### Basic Solution Ruleset

```yaml
name: my-solution
probes:
  - type: scriptlet
    url: file://probes/check_health.py
  - type: scriptlet
    url: file://probes/check_relations.py
  - type: scriptlet
    url: file://probes/check_config.py
```

### Composing Rulesets

```yaml
name: full-validation
probes:
  # Base checks (reusable)
  - type: ruleset
    url: file://rulesets/base-health.yaml
  # Solution-specific checks
  - type: scriptlet
    url: file://probes/solution_specific.py
  # Remote checks from charm repo
  - type: scriptlet
    url: github://canonical/my-charm//probes/validate.py
```

## Error Reporting Patterns

### Collect All Errors (Recommended)

Rather than raising on the first failure, collect all errors and report them together:

```python
def status(juju_statuses: dict[str, dict]):
    errors = []
    for model, data in juju_statuses.items():
        # ... validation logic ...
        if problem:
            errors.append(f"{context}: {description}")
    if errors:
        raise Exception(f"Found {len(errors)} issues:\n" + "\n".join(errors))
```

### Include Context in Errors

Always include:
- Model name
- Application/unit name
- Current state vs expected state
- Any relevant status messages

```python
raise Exception(
    f"{unit} in {model}: workload is {actual} "
    f"(expected active), message: {message}"
)
```
