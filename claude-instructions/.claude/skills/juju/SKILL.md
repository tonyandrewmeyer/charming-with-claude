---
name: juju
description: Operate a Juju controller — deploy, configure, integrate, scale, debug, and manage charms on Kubernetes and machine models. Use when asked to "deploy a charm", "add a model", "check status", "debug a unit", "integrate applications", "scale up/down", "manage secrets", "configure an app", "run an action", "destroy a model", or any Juju CLI operation. Keywords include juju, deploy, integrate, relate, model, controller, status, debug-log, config, action, expose, storage, secrets, ssh, scale.
allowed-tools: Bash(juju:*), Bash(charmcraft pack:*), Bash(charmcraft analyse:*), Read, Grep, Glob
---

# Juju Operations Assistant

Operate a live Juju environment: deploy charms, manage models, configure applications, integrate services, debug issues, and manage the full lifecycle.

## Live Environment

Current controller: !`juju whoami --format=json 2>/dev/null || echo '{"error": "not connected"}'`
Controllers: !`juju controllers --format=tabular 2>/dev/null | head -15 || echo "No controllers found"`
Active model status: !`juju status --format=short 2>/dev/null | head -20 || echo "No active model"`

## Session Setup

When starting work that requires a Juju model, always:

1. **Choose the right controller** for the substrate:
   ```bash
   juju switch concierge-lxd   # Machine charms
   juju switch concierge-k8s   # Kubernetes charms
   ```

If the controllers were not set up by Concierge, they will have different names, and you will need to refer to the "cloud" field in `juju status`.

2. **Create a dedicated model** with a recognisable, unique name:
   ```bash
   juju add-model claude-<descriptive-id>
   ```

3. **Immediately tell the user** how to observe the model — print this right after model creation, and again at the end of the session:
   ```
   Model created: <controller>:<model>

   To watch status:
     juju status -m <controller>:<model> --watch 2s

   To stream logs:
     juju debug-log -m <controller>:<model> --tail
   ```

## Core Workflows

### Deploy a Charm

```bash
# From Charmhub
juju deploy postgresql-k8s --channel 14/stable --trust
juju deploy ubuntu --base ubuntu@24.04 -n 3

# From a local .charm file (pack first)
charmcraft pack
charmcraft analyse ./*.charm
juju deploy ./<name>.charm --resource <name>=<image>

# With configuration
juju deploy mysql-k8s --channel 8.0/stable --config profile=testing

# With constraints
juju deploy app-k8s --constraints "mem=4G cores=2"

# With storage
juju deploy postgresql-k8s --storage pgdata=kubernetes,10G
```

**Key flags:**
- `--trust` — grant the charm access to cloud credentials (required by many charms)
- `--channel` — specify the risk channel (e.g., `14/stable`, `latest/edge`)
- `--base` — target OS for machine charms (e.g., `ubuntu@22.04`)
- `-n` — number of units to deploy
- `--config` — pass key=value or a YAML config file
- `--constraints` — resource requirements (mem, cores, root-disk, virt-type, arch)
- `--resource` — attach OCI images or files
- `--storage` — attach storage (format: `<store>=<pool>,<size>`)

### Configure Applications

```bash
# View current config
juju config <app>

# Set values
juju config <app> key1=value1 key2=value2

# Set from YAML file
juju config <app> --file config.yaml

# Reset to default
juju config <app> --reset key1,key2

# View a single key
juju config <app> key1
```

### Integrate (Relate) Applications

```bash
# Auto-match endpoints
juju integrate <app1> <app2>

# Explicit endpoints
juju integrate <app1>:endpoint1 <app2>:endpoint2

# Remove a relation
juju remove-relation <app1> <app2>

# View relations
juju status --relations
```

**Common integration patterns:**
- Database: `juju integrate myapp postgresql-k8s`
- Ingress: `juju integrate myapp traefik-k8s`
- TLS: `juju integrate myapp self-signed-certificates`
- Logging: `juju integrate myapp grafana-agent-k8s`

### Scale Applications

```bash
# Kubernetes — set target scale
juju scale-application <app> <count>

# Machine — add units
juju add-unit <app> -n <count>

# Machine — remove specific unit
juju remove-unit <app>/<unit-number>
```

### Run Actions

```bash
# List available actions
juju actions <app>

# Run an action (waits for result)
juju run <app>/<unit> <action-name>

# Run with parameters
juju run <app>/<unit> <action-name> param1=value1 param2=value2

# Run with timeout
juju run <app>/<unit> <action-name> --wait=5m

# List past operations
juju operations --actions
```

### Expose / Network Access

```bash
# Expose to all (use with caution)
juju expose <app>

# Expose to specific CIDRs
juju expose <app> --to-cidrs 10.0.0.0/24

# Expose to specific spaces
juju expose <app> --to-spaces public

# Remove exposure
juju unexpose <app>
```

## Status and Monitoring

### Reading Status

```bash
# Human-readable
juju status
juju status --relations            # Include relation info
juju status --watch 2s             # Continuous refresh, not available in Juju 4, use the `watch` CLI tool instead
juju status --format json          # Machine-parseable

# Specific application
juju show-application <app>
juju show-unit <app>/<unit>
```

**Status interpretation:**
- **active** — charm is healthy (the text part of the status may indicate degraded performance)
- **waiting/idle** — charm is waiting for something (often a relation)
- **blocked/idle** — charm needs user intervention (read the status message!)
- **maintenance** — charm is performing an operation
- **error** — a hook failed; check logs and use `juju resolved`

### Streaming Logs

```bash
# Tail all logs
juju debug-log --tail

# Filter by unit
juju debug-log --tail --include unit-<app>-<n>

# Filter by log level
juju debug-log --tail --level ERROR

# Include specific modules
juju debug-log --tail --include <app>

# Set logging verbosity on the model
juju model-config logging-config="<root>=WARNING;unit=DEBUG"
```

### SSH and Exec

```bash
# SSH into a unit
juju ssh <app>/<unit>

# Run a command on a unit
juju ssh <app>/<unit> -- <command>

# SSH into a K8s workload container
juju ssh --container <container-name> <app>/<unit>

# Copy files
juju scp <local-path> <app>/<unit>:<remote-path>
juju scp <app>/<unit>:<remote-path> <local-path>

# Run command across all units
juju exec --all -- <command>
juju exec --application <app> -- <command>
```

## Model Management

```bash
# List models
juju models

# Create a model
juju add-model <name>
juju add-model <name> --config logging-config="<root>=INFO"

# Switch between controllers/models
juju switch <controller>
juju switch <controller>:<model>

# View model config
juju model-config
juju model-config <key>
juju model-config <key>=<value>

# Set model-wide constraints
juju set-model-constraints cores=2 mem=4G
```

## Secrets Management

```bash
# Create a secret
juju add-secret <name> key1=value1 key2=value2

# Grant a secret to an application
juju grant-secret <name> <app>

# Revoke access
juju revoke-secret <name> <app>

# List secrets
juju secrets

# Show secret details (not content)
juju show-secret <name>

# Show secret content
juju show-secret <name> --reveal

# Update a secret
juju update-secret <name> key1=newvalue

# Remove a secret
juju remove-secret <name>
```

## Debugging Workflows

When a unit is in error state:

1. **Read the status message** — it often tells you what is wrong:
   ```bash
   juju status --format json | python3 -c "
   import sys, json
   s = json.load(sys.stdin)
   for app, info in s.get('applications', {}).items():
       for unit, u in info.get('units', {}).items():
           ws = u.get('workload-status', {})
           if ws.get('current') in ('error', 'blocked'):
               print(f'{unit}: {ws[\"current\"]} — {ws.get(\"message\", \"\")}')
   "
   ```

2. **Check the logs** for the failing unit:
   ```bash
   juju debug-log --tail --level ERROR --include unit-<app>-<n>
   ```

3. **Retry the failed hook** once the issue is understood:
   ```bash
   juju resolved <app>/<unit>
   ```

4. **For deeper inspection**, SSH in:
   ```bash
   juju ssh <app>/<unit>                               # Machine charm
   juju ssh --container <container> <app>/<unit>       # K8s workload
   ```

5. **Interactive hook debugging** (drops you into a tmux session when hook fires):
   ```bash
   juju debug-hooks <app>/<unit>
   ```

**For comprehensive troubleshooting, see [references/troubleshooting.md](references/troubleshooting.md)**

## Cleanup and Teardown

**Always clean up models when done.** Follow this order:

```bash
# Remove specific applications first (optional, for partial cleanup)
juju remove-application <app> --destroy-storage

# Destroy the entire model (preferred for full cleanup)
juju destroy-model <controller>:<model> --destroy-storage -y

# Force-destroy if stuck (last resort)
juju destroy-model <controller>:<model> --destroy-storage --force --no-wait -y
```

**Safety rules:**
- **Never** destroy a controller unless the user explicitly asks
- **Never** destroy a model that you did not create unless the user explicitly asks
- **Never** remove packages installed by Concierge unless explicitly asked
- **Always** use `--destroy-storage` to avoid orphaned volumes
- **Always** use `-m <controller>:<model>` for destructive commands to avoid accidents

## Working with Both Substrates

The environment may have one or both of Kubernetes and LXD controllers. Choose based on the charm type. If the environment was set up by Concierge, then the controllers will be named `concierge-k8s` and `concierge-lxd`, and the model in both cases will be named `testing`.

| | Kubernetes | Machine/LXD |
|---|---|---|
| **Charm type** | K8s charms (sidecar pattern) | Machine charms |
| **Workload** | OCI images via Pebble | Debs, snaps, binaries |
| **Scale** | `juju scale-application` | `juju add-unit` / `juju remove-unit` |
| **SSH to workload** | `juju ssh --container <c> <u>` | `juju ssh <u>` (needs a key configured in Juju 4 and above) |
| **Storage** | `kubernetes` pool | `lxd` pool |

## Best Practices

1. **Always use `-m controller:model`** for commands that modify state — avoids acting on the wrong model
2. **Use `--format json`** when parsing output programmatically — human-readable format changes between versions
3. **Check `juju status`** after deploy/integrate/config changes — don't assume success
4. **Use `--trust`** when deploying charms that need cloud API access
5. **Set `logging-config`** early: `juju model-config logging-config="<root>=WARNING;unit=DEBUG"`
6. **Wait for operations** — use `watch -n2 juju status` or poll with `juju status --format json` rather than guessing timing
7. **Read charm documentation** before deploying: `juju info <charm>` shows metadata, channels, and supported bases

## Additional References

When you need detailed information:
- **Full command reference by category**: See [references/command-reference.md](references/command-reference.md)
- **Troubleshooting guide**: See [references/troubleshooting.md](references/troubleshooting.md)
- **Cross-model relations and offers**: See [references/cross-model-relations.md](references/cross-model-relations.md)
- **Storage and secrets deep-dive**: See [references/storage-and-secrets.md](references/storage-and-secrets.md)
- **Juju documentation**: https://documentation.ubuntu.com/juju/latest/
- **Juju CLI reference**: https://documentation.ubuntu.com/juju/latest/reference/juju-cli/
- **CLI command output format**: can be found in the [Jubilant code](https://github.com/canonical/jubilant)
