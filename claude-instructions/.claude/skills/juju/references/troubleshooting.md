# Juju Troubleshooting Guide

Systematic approaches to diagnosing and resolving common Juju issues.

## General Diagnostic Strategy

For any issue, follow this order:

1. **Read the status message** — `juju status` often tells you exactly what is wrong
2. **Check the logs** — `juju debug-log --tail --level ERROR`
3. **Inspect the unit** — `juju ssh <app>/<unit>` or `juju ssh --container <c> <app>/<unit>`
4. **Check the model events** — `juju debug-log --tail --include unit-<app>-<n>`

## Unit in Error State

**Symptoms:** `juju status` shows `error` for workload or agent status.

**Diagnosis:**
```bash
# See what hook failed
juju status --format json | python3 -c "
import sys, json
s = json.load(sys.stdin)
for app, info in s.get('applications', {}).items():
    for unit, u in info.get('units', {}).items():
        if u.get('agent-status', {}).get('current') == 'error':
            print(f'{unit}: {u[\"agent-status\"].get(\"message\", \"\")}')
"

# Check logs for the failing unit
juju debug-log --tail --level ERROR --include unit-<app>-<n>
```

**Resolution:**
```bash
# Once the underlying issue is fixed, retry the failed hook
juju resolved <app>/<unit>

# If the charm itself needs updating
charmcraft pack
juju refresh <app> --path ./<charm>.charm

# Then resolve
juju resolved <app>/<unit>
```

**Common causes:**
- Missing relation data (integrate the required charm)
- Configuration error (check `juju config <app>`)
- Resource not available (check container images, snap channels)
- Permission denied (try `juju trust <app>`)
- Network connectivity (check cloud/provider networking)

## Unit Stuck in Waiting/Blocked

**Symptoms:** Unit stays in `waiting` or `blocked` with a message.

**Diagnosis:**
```bash
# Read the status message carefully — charms SHOULD tell you what they need
juju status

# Check what relations exist vs what the charm requires
juju status --relations
juju info <charm>  # Shows required/optional relations
```

**Common causes and fixes:**
- **"Waiting for database relation"** → `juju integrate <app> postgresql-k8s`
- **"Waiting for certificates relation"** → `juju integrate <app> self-signed-certificates`
- **"Blocked: missing trust"** → `juju trust <app> --scope=cluster`
- **"Waiting for leader to set..."** → Check leader unit status; it may be the one with the issue

## Deploy Fails

**Symptoms:** `juju deploy` returns an error or unit never reaches active.

**Check these first:**
```bash
# Is the charm name correct?
juju info <charm-name>

# Is the channel valid?
juju info <charm-name>  # Lists available channels

# Are resources provided?
juju charm-resources <charm-name>

# For local charms, did charmcraft analyse pass?
charmcraft analyse ./<charm>.charm
```

**Common issues:**

| Error | Cause | Fix |
|-------|-------|-----|
| `charm not found` | Wrong name or channel | Check `juju find <query>` |
| `base not supported` | Charm doesn't support this base | Check `juju info <charm>` for supported bases |
| `cannot deploy to machine model` | K8s charm on LXD controller | Switch to K8s controller |
| `cannot deploy to k8s model` | Machine charm on K8s controller | Switch to LXD controller |
| `resource not found` | OCI image not specified | Add `--resource <name>=<image>` |

## Integration (Relation) Issues

**Symptoms:** Relation doesn't form, apps don't communicate.

**Diagnosis:**
```bash
# Check relation status
juju status --relations

# Check endpoint compatibility
juju info <app1>  # Look at provides/requires
juju info <app2>  # Endpoints must match interface names

# Use jhack for detailed relation data (if installed)
jhack show-relation <app1> <app2>
```

**Common issues:**
- **Interface mismatch** — endpoints must share the same interface name
- **Wrong endpoint names** — use explicit endpoints: `juju integrate app1:ep1 app2:ep2`
- **Relation limit reached** — some endpoints only allow one relation
- **Cross-model not set up** — need `juju offer` and `juju consume` first

## Model Stuck / Cannot Destroy

**Symptoms:** `juju destroy-model` hangs or fails.

**Resolution (escalating force):**
```bash
# Standard destroy
juju destroy-model <model> --destroy-storage -y

# Force (skips clean shutdown)
juju destroy-model <model> --destroy-storage --force -y

# Force + no-wait (immediate)
juju destroy-model <model> --destroy-storage --force --no-wait -y
```

**If model is completely stuck:**
```bash
# Check what's blocking
juju status -m <controller>:<model>

# Check for lingering resources
juju storage -m <controller>:<model>
juju machines -m <controller>:<model>
```

## Hook Debugging

**For interactive debugging of hook execution:**

```bash
# This intercepts the next hook and drops you into a tmux session
juju debug-hooks <app>/<unit>

# In the tmux session:
# - The hook name appears in the tmux window title
# - Run the hook manually to see what fails
# - Exit the tmux window to let the hook proceed
# - Use Ctrl-a d to detach without proceeding
```

**For programmatic debugging:**
```bash
# Set verbose logging for a specific unit
juju model-config logging-config="unit.<app>.<n>=TRACE"

# Watch the specific unit's logs
juju debug-log --tail --include unit-<app>-<n>
```

## Kubernetes-Specific Issues

### Pod Not Starting

```bash
# Check the K8s-level status
juju ssh --container <container> <app>/<unit> -- pebble services

# If you can't SSH, check K8s directly
kubectl -n <model-name> get pods
kubectl -n <model-name> describe pod <app>-0
kubectl -n <model-name> logs <app>-0 -c charm
kubectl -n <model-name> logs <app>-0 -c <workload-container>
```

### Pebble Not Ready

**Symptoms:** Charm logs show "pebble not ready" or connection refused.

**Causes:**
- Workload container still starting — wait and check `juju status --watch 2s`
- OCI image pull failure — check image reference and registry access
- Container crash-looping — check `kubectl logs`

### Storage Issues on K8s

```bash
# Check storage status
juju storage -m <controller>:<model>

# Check PVCs in Kubernetes
kubectl -n <model-name> get pvc
kubectl -n <model-name> describe pvc <name>

# Common fix: ensure storage class exists
kubectl get storageclass
```

## Machine-Specific Issues

### Machine Not Provisioning

```bash
# Check machine status
juju machines

# Check for cloud-level issues
juju show-machine <id>

# For LXD
lxc list
lxc info <container-name>
```

### Agent Not Connected

**Symptoms:** Agent status shows `lost` or `not connected`.

```bash
# Check if machine is reachable
juju ssh <machine-id> -- hostname

# Check agent process
juju ssh <machine-id> -- systemctl status jujud-machine-<id>

# Check agent logs
juju ssh <machine-id> -- journalctl -u jujud-machine-<id> --no-pager -n 50
```

## Performance Issues

### Slow Status Updates

```bash
# Check update-status interval (default 5m)
juju model-config update-status-hook-interval

# Reduce for faster feedback during development
juju model-config update-status-hook-interval=30s

# Reset to default when done
juju model-config update-status-hook-interval=5m
```

### Command Timeout

Most commands accept `--timeout` or complete within a reasonable time. If commands hang:

```bash
# Add debug output
juju status --debug --verbose

# Check controller connectivity
juju controllers

# Check the controller model health
juju status -m controller
```

## Secrets Issues

```bash
# Permission denied on secret
juju grant-secret <secret-name> <app>

# Secret not found
juju secrets  # List all to find the correct name/ID

# Secret content not updating
juju show-secret <name> --reveal  # Check current content
juju update-secret <name> key=newvalue
```

## Useful Diagnostic One-Liners

```bash
# Show all units not in active/idle
juju status --format json | python3 -c "
import sys, json
s = json.load(sys.stdin)
for app, info in s.get('applications', {}).items():
    for unit, u in info.get('units', {}).items():
        ws = u.get('workload-status', {})
        as_ = u.get('agent-status', {})
        if ws.get('current') != 'active' or as_.get('current') != 'idle':
            print(f'{unit}: workload={ws.get(\"current\")} agent={as_.get(\"current\")} msg={ws.get(\"message\",\"\")}')"

# Show all relations
juju status --relations --format json | python3 -c "
import sys, json
s = json.load(sys.stdin)
for r in s.get('relations', []):
    print(f'{r[\"key\"]}: status={r.get(\"status\", \"?\")}')"

# Count units per application
juju status --format json | python3 -c "
import sys, json
s = json.load(sys.stdin)
for app, info in s.get('applications', {}).items():
    units = len(info.get('units', {}))
    print(f'{app}: {units} unit(s), status={info.get(\"application-status\", {}).get(\"current\", \"?\")}')"
```
