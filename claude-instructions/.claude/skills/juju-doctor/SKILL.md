---
name: juju-doctor
description: Expert assistant for validating Juju deployments using juju-doctor. Use when running deployment diagnostics, writing probes, creating rulesets, validating deployment health, or debugging deployment issues offline. Keywords include juju-doctor, probe, ruleset, deployment validation, diagnostics, health check, offline validation, sosreport.
license: Apache-2.0
compatibility: Requires juju-doctor installed (uv pip install juju-doctor). Network access needed for live model checks.
allowed-tools: Bash(juju-doctor:*) Bash(juju:*) Read Grep Glob
---

# Juju Doctor Deployment Validation Assistant

Expert guidance for validating Juju deployments using juju-doctor — a probe-based diagnostic tool for checking deployment health.

## What is juju-doctor?

juju-doctor validates Juju deployments through configurable assertions called **probes**. It addresses a gap in the Juju ecosystem: traditional mechanisms (collect-status, update-status, Pebble checks) fail to provide holistic validity checks across an entire deployment.

Key use cases:
- **Offline validation** — Run probes against static artifact files from sosreport archives (useful when support teams lack live access)
- **Live deployment validation** — Run probes against one or more live Juju models
- **Solution rulesets** — Assemble multiple probes into a ruleset defining "the correct way" to deploy a solution

## Installation

```bash
# Install from PyPI
pip install juju-doctor

# Or with uv
uv pip install juju-doctor

# Development install
git clone https://github.com/canonical/juju-doctor.git
cd juju-doctor
uv sync --extra=dev && uv pip install -e .
```

## Core Concepts

### Artifacts

juju-doctor operates on three types of Juju artifacts:

| Artifact | Source Command | Description |
|----------|---------------|-------------|
| **status** | `juju status --format=yaml` | Unit status, application status, machine info |
| **bundle** | `juju export-bundle` | Deployed bundle configuration |
| **show-unit** | `juju show-unit --format=yaml` | Detailed unit information |

### Probe Types

**Scriptlet probes** (Python): Functions named after artifact types that receive data indexed by model name.

```python
from typing import Dict

def status(juju_statuses: Dict[str, Dict]):
    """Validate that all units are active/idle."""
    for model_name, status_data in juju_statuses.items():
        apps = status_data.get("applications", {})
        for app_name, app_data in apps.items():
            for unit_name, unit_data in app_data.get("units", {}).items():
                ws = unit_data.get("workload-status", {})
                if ws.get("current") != "active":
                    raise Exception(
                        f"{unit_name} in {model_name} is "
                        f"{ws.get('current')}, not active"
                    )
```

**Ruleset probes** (YAML): Declarative files that coordinate multiple probes.

```yaml
name: my-solution-ruleset
probes:
  - type: scriptlet
    url: file://probes/check_active.py
  - type: scriptlet
    url: file://probes/check_relations.py
  - type: ruleset
    url: file://rulesets/nested.yaml
  - type: scriptlet
    url: github://canonical/my-charm//probes/validate.py
```

## Core Workflows

### Running Probes Against Live Models

```bash
# Single model
juju-doctor check -p file://probes/check_active.py -m mymodel

# Multiple models
juju-doctor check -p file://probes/check_active.py -m model1 -m model2

# Multiple probes
juju-doctor check \
  -p file://probes/check_active.py \
  -p file://probes/check_relations.py \
  -m mymodel

# Using a ruleset
juju-doctor check -p file://rulesets/solution.yaml -m mymodel
```

### Running Probes Against Static Artifacts (Offline)

```bash
# From juju status output
juju status --format=yaml > status.yaml
juju-doctor check -p file://probes/check_active.py --status status.yaml

# From exported bundle
juju export-bundle > bundle.yaml
juju-doctor check -p file://probes/check_bundle.py --bundle bundle.yaml

# From show-unit output
juju show-unit myapp/0 --format=yaml > show-unit.yaml
juju-doctor check -p file://probes/check_unit.py --show-unit show-unit.yaml

# Combine multiple artifacts
juju-doctor check \
  -p file://probes/full_check.py \
  --status status.yaml \
  --bundle bundle.yaml \
  --show-unit show-unit.yaml
```

### Remote Probes from GitHub

```bash
# Load probes directly from a GitHub repository
juju-doctor check \
  -p github://canonical/my-charm//probes/validate.py \
  -m mymodel
```

### Viewing Output

```bash
# Default tree output
juju-doctor check -p file://probes/check.py -m mymodel

# Example output:
# Results
# ├── 🔴 probes_check_relations.py
# └── 🟢 probes_check_active.py
#
# Total: 🟢 1/2 🔴 1/2

# JSON output (for programmatic use)
juju-doctor check -p file://probes/check.py -m mymodel --format json

# Verbose output (shows probe details)
juju-doctor check -p file://probes/check.py -m mymodel -v
```

### Schema Inspection

```bash
# View the ruleset schema
juju-doctor schema

# View builtins schema
juju-doctor schema --builtins
```

## Writing Probes

### Scriptlet Probe Structure

A scriptlet probe is a Python file containing one or more functions named after artifact types:

```python
"""Probe: Validate deployment health."""
def status(juju_statuses: dict[str, dict]):
    """Check all units are active and idle."""
    for model_name, data in juju_statuses.items():
        for app_name, app in data.get("applications", {}).items():
            for unit_name, unit in app.get("units", {}).items():
                ws = unit.get("workload-status", {})
                agent = unit.get("juju-status", {})
                if ws.get("current") != "active":
                    raise Exception(
                        f"{unit_name}: workload is {ws.get('current')}"
                    )
                if agent.get("current") != "idle":
                    raise Exception(
                        f"{unit_name}: agent is {agent.get('current')}"
                    )


def bundle(juju_bundles: dict[str, dict]):
    """Validate bundle configuration."""
    for model_name, bundle_data in juju_bundles.items():
        apps = bundle_data.get("applications", {})
        if not apps:
            raise Exception(f"{model_name}: no applications in bundle")
```

**Rules:**
- Function names **must** match artifact types: `status`, `bundle`, `show_unit`
- Each function receives a `dict[str, dict]` indexed by model name
- Raise an `Exception` to signal failure (message becomes the error output)
- Return normally (or return `None`) to signal success
- A single probe file can contain multiple artifact functions

### Ruleset Probe Structure

```yaml
name: my-solution
probes:
  # Local scriptlet
  - type: scriptlet
    url: file://probes/check_active.py

  # Remote scriptlet from GitHub
  - type: scriptlet
    url: github://canonical/my-charm//probes/validate.py

  # Nested ruleset
  - type: ruleset
    url: file://rulesets/base-checks.yaml
```

### Common Probe Patterns

#### Check All Units Are Active/Idle

```python
def status(juju_statuses: dict[str, dict]):
    for model, data in juju_statuses.items():
        for app, app_data in data.get("applications", {}).items():
            for unit, unit_data in app_data.get("units", {}).items():
                ws = unit_data.get("workload-status", {})
                if ws.get("current") != "active":
                    raise Exception(f"{unit}: {ws.get('current')}")
```

#### Check Required Relations Exist

```python
def status(juju_statuses: dict[str, dict]):
    required = {"database", "ingress"}
    for model, data in juju_statuses.items():
        relations = set(data.get("relations", {}).keys())
        # Also check application-level relation info
        for app, app_data in data.get("applications", {}).items():
            for rel in app_data.get("relations", {}):
                relations.add(rel)
        missing = required - relations
        if missing:
            raise Exception(f"{model}: missing relations: {missing}")
```

#### Validate Bundle Configuration

```python
def bundle(juju_bundles: dict[str, dict]):
    for model, bundle_data in juju_bundles.items():
        apps = bundle_data.get("applications", {})
        for app_name, app in apps.items():
            # Check minimum units
            num_units = app.get("num_units", 1)
            if num_units < 1:
                raise Exception(f"{app_name}: has {num_units} units")
            # Check charm source
            charm = app.get("charm", "")
            if not charm:
                raise Exception(f"{app_name}: no charm specified")
```

#### Check for Blocked/Error Status

```python
def status(juju_statuses: dict[str, dict]):
    for model, data in juju_statuses.items():
        for app, app_data in data.get("applications", {}).items():
            app_status = app_data.get("application-status", {})
            if app_status.get("current") in ("blocked", "error"):
                msg = app_status.get("message", "no message")
                raise Exception(f"{app}: {app_status['current']} — {msg}")
```

## Project Organisation

When adding juju-doctor probes to a charm project:

```
probes/
├── check_active.py         # Unit health checks
├── check_relations.py      # Relation validation
├── check_config.py         # Configuration validation
└── rulesets/
    └── full-check.yaml     # Combined ruleset
```

## Best Practices

### Writing Probes

1. **One concern per probe** — Keep probes focused on a single validation
2. **Descriptive error messages** — Include the model name, unit name, and what went wrong
3. **Handle missing data gracefully** — Use `.get()` with defaults; not all fields are always present
4. **Use rulesets to compose** — Combine simple probes into comprehensive checks rather than writing monolithic probes
5. **Test offline first** — Capture artifacts with `juju status --format=yaml` and validate against those before running against live models

### Organising Probes

1. **Keep probes in version control** — Store alongside the charm they validate
2. **Use rulesets for solutions** — When multiple charms form a solution, create a ruleset that validates the whole deployment
3. **Share via GitHub** — Use `github://` URLs in rulesets for reusable probes
4. **Document expected state** — Comment probes to explain what "healthy" means

### Integration with Support Workflows

1. **Collect artifacts from sosreport** — Extract `juju status` and `juju export-bundle` output
2. **Run probes offline** — `juju-doctor check --status status.yaml --bundle bundle.yaml`
3. **Share results** — Use `--format json` for machine-readable output
4. **Build solution-specific rulesets** — Encode deployment requirements as probes

## Troubleshooting

### juju-doctor Not Found

```bash
# Check installation
pip show juju-doctor
# or
uv pip show juju-doctor

# Reinstall
pip install --upgrade juju-doctor
```

### Probe Fails to Load

- Check the URL format: `file://path/to/probe.py` (relative to working directory)
- Verify the Python file has valid syntax
- Ensure function names match artifact types (`status`, `bundle`, `show_unit`)

### Live Model Connection Issues

```bash
# Verify Juju connectivity
juju status
juju models

# Check model name matches exactly
juju-doctor check -p file://probe.py -m $(juju models --format=json | python3 -c "import sys,json; print(json.load(sys.stdin)['models'][0]['name'])")
```

### Unexpected Results

```bash
# Run with verbose output
juju-doctor check -p file://probe.py -m mymodel -v

# Capture the artifact and inspect manually
juju status --format=yaml > /tmp/status.yaml
python3 -c "import yaml; print(yaml.safe_load(open('/tmp/status.yaml')))"

# Then test the probe offline
juju-doctor check -p file://probe.py --status /tmp/status.yaml -v
```

## Command Reference

```bash
# Run probes
juju-doctor check [OPTIONS]
  --probe, -p     Probe URL (file://, github://) — repeatable
  --model, -m     Live model name — repeatable
  --status        Path to juju status YAML file
  --bundle        Path to juju bundle YAML file
  --show-unit     Path to juju show-unit YAML file
  --verbose, -v   Verbose output
  --format, -o    Output format: tree (default) or json

# Schema inspection
juju-doctor schema
juju-doctor schema --builtins

# General
juju-doctor --help
juju-doctor --version
```

## Resources

- **juju-doctor GitHub**: https://github.com/canonical/juju-doctor
- **juju-doctor on PyPI**: https://pypi.org/project/juju-doctor
- **Discourse discussion**: https://discourse.charmhub.io/t/juju-doctor-why-does-juju-need-it/17748
- **Juju docs**: https://documentation.ubuntu.com/juju/latest/

## Additional References

When you need detailed information:
- **Probe writing patterns**: See [references/probe-patterns.md](references/probe-patterns.md)

---

**Key reminders:**
- Probes raise `Exception` to signal failure, return normally for success
- Use `file://` URLs for local probes, `github://` for remote ones
- Always test probes offline with captured artifacts before running live
- Compose simple probes into rulesets rather than writing monolithic validators
- Install with `uv pip install juju-doctor` (prefer uv in this project)
