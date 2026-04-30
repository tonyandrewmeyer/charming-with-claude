# Juju CLI Command Reference

Complete reference for Juju CLI commands, organised by category. All commands support `--help` for detailed usage.

## Controller Management

| Command | Description |
|---------|-------------|
| `juju bootstrap <cloud> <name>` | Create a new controller on a cloud |
| `juju controllers` | List all known controllers |
| `juju show-controller <name>` | Show controller details |
| `juju controller-config` | View/set controller configuration |
| `juju switch <controller>` | Switch active controller |
| `juju upgrade-controller` | Upgrade the controller agent |
| `juju enable-ha` | Make the controller highly available |
| `juju destroy-controller <name>` | Remove a controller and all its models |
| `juju kill-controller <name>` | Force-remove a controller (last resort) |
| `juju register <url>` | Register an external controller |
| `juju unregister <name>` | Remove a controller registration (local only) |

### Bootstrap Examples

```bash
# LXD (local machine containers)
juju bootstrap localhost my-controller

# MicroK8s
juju bootstrap microk8s my-k8s-controller

# With constraints
juju bootstrap aws/us-east-1 prod --bootstrap-constraints "cores=2 mem=4G root-disk=50G"

# With debug (keeps broken machine for inspection)
juju bootstrap localhost test --debug --verbose --keep-broken
```

## Model Management

| Command | Description |
|---------|-------------|
| `juju add-model <name>` | Create a new model |
| `juju models` | List all models on active controller |
| `juju show-model <name>` | Show model details |
| `juju switch <controller>:<model>` | Switch active model |
| `juju model-config [key[=value]]` | View/set model configuration |
| `juju model-defaults [key[=value]]` | View/set model defaults |
| `juju model-constraints` | View model-level constraints |
| `juju set-model-constraints` | Set model-level constraints |
| `juju destroy-model <name>` | Destroy a model and all its contents |
| `juju export-bundle` | Export current model as a bundle |

### Key Model Config Options

```bash
juju model-config logging-config="<root>=WARNING;unit=DEBUG"
juju model-config update-status-hook-interval=5m
juju model-config automatically-retry-hooks=true
juju model-config default-base=ubuntu@24.04
```

## Application Deployment

| Command | Description |
|---------|-------------|
| `juju deploy <charm> [app-name]` | Deploy a charm |
| `juju refresh <app>` | Upgrade to a new charm revision |
| `juju config <app> [key=value]` | View/set application config |
| `juju constraints <app>` | View application constraints |
| `juju set-constraints <app>` | Set application constraints |
| `juju trust <app>` | Grant cloud credential access |
| `juju bind <app>` | Bind application endpoints to spaces |
| `juju remove-application <app>` | Remove an application |

### Deploy Examples

```bash
# Charmhub (bare name or ch: prefix)
juju deploy postgresql-k8s --channel 14/stable --trust
juju deploy ch:ubuntu --base ubuntu@24.04 -n 3

# Local charm
juju deploy ./my-charm_ubuntu-22.04-amd64.charm

# With OCI resource
juju deploy ./my-charm.charm --resource oci-image=registry/image:tag

# Bundle (remote)
juju deploy ch:kubernetes-core

# Bundle (local YAML)
juju deploy ./bundle.yaml

# Dry run
juju deploy postgresql-k8s --dry-run
```

### Refresh (Upgrade) Examples

```bash
# Upgrade to latest in channel
juju refresh <app>

# Switch channel
juju refresh <app> --channel 15/stable

# Upgrade from local charm
juju refresh <app> --path ./my-charm.charm

# With new resource
juju refresh <app> --resource oci-image=registry/image:newtag
```

## Unit and Machine Management

| Command | Description |
|---------|-------------|
| `juju add-unit <app> [-n count]` | Add units (machine models) |
| `juju remove-unit <app>/<n>` | Remove a specific unit |
| `juju scale-application <app> <n>` | Scale to N units (K8s models) |
| `juju machines` | List machines |
| `juju show-machine <id>` | Show machine details |
| `juju add-machine` | Add an empty machine |
| `juju remove-machine <id>` | Remove a machine |
| `juju resolved <app>/<n>` | Retry a failed hook |

## Integration (Relations)

| Command | Description |
|---------|-------------|
| `juju integrate <app1> <app2>` | Create a relation |
| `juju integrate <a1>:<ep> <a2>:<ep>` | Relate specific endpoints |
| `juju remove-relation <app1> <app2>` | Remove a relation |
| `juju suspend-relation <id>` | Suspend a relation |
| `juju resume-relation <id>` | Resume a suspended relation |

**Note:** `juju relate` is an alias for `juju integrate`.

## Cross-Model Relations (Offers)

| Command | Description |
|---------|-------------|
| `juju offer <app>:<endpoint>` | Create a cross-model offer |
| `juju offers` | List offers in current model |
| `juju find-offers` | Search for available offers |
| `juju consume <offer-url>` | Consume a remote offer |
| `juju remove-offer <name>` | Remove an offer |

See [cross-model-relations.md](cross-model-relations.md) for detailed workflows.

## Actions and Operations

| Command | Description |
|---------|-------------|
| `juju actions <app>` | List actions defined by a charm |
| `juju run <app>/<n> <action>` | Run an action on a unit |
| `juju operations` | List recent operations |
| `juju show-operation <id>` | Show operation details |
| `juju show-task <id>` | Show task details |
| `juju cancel-task <id>` | Cancel a running task |

### Action Examples

```bash
# Run and wait for result
juju run mysql/0 backup --wait=10m

# Run with parameters
juju run postgresql/leader create-backup type=physical

# Run on leader unit
juju run <app>/leader <action>

# List operations for an app
juju operations --actions --applications <app>
```

## SSH and Remote Access

| Command | Description |
|---------|-------------|
| `juju ssh <app>/<n>` | SSH into a unit |
| `juju ssh --container <c> <app>/<n>` | SSH into a K8s container |
| `juju scp <src> <dst>` | Copy files to/from a unit |
| `juju exec --all -- <cmd>` | Run command on all units |
| `juju exec --application <app> -- <cmd>` | Run on all units of an app |
| `juju ssh-keys` | List authorised SSH keys |
| `juju add-ssh-key <key>` | Add an SSH key |
| `juju remove-ssh-key <key>` | Remove an SSH key |
| `juju import-ssh-key <id>` | Import key from GitHub/Launchpad |

## Debugging and Logs

| Command | Description |
|---------|-------------|
| `juju debug-log` | Stream model logs |
| `juju debug-log --tail` | Tail latest logs |
| `juju debug-log --level ERROR` | Filter by level |
| `juju debug-log --include unit-<app>-<n>` | Filter by unit |
| `juju debug-hooks <app>/<n>` | Interactive hook debugging (tmux) |
| `juju debug-code <app>/<n>` | Attach debugger to unit |
| `juju show-status-log <app>/<n>` | Show status history |

### Debug-Log Filtering

```bash
# Multiple includes (OR logic)
juju debug-log --tail --include unit-myapp-0 --include unit-myapp-1

# Exclude noisy modules
juju debug-log --tail --exclude module-juju.worker

# Show last N lines
juju debug-log --tail --lines 100

# Replay from beginning
juju debug-log --replay --level WARNING
```

## Storage

| Command | Description |
|---------|-------------|
| `juju storage` | List storage instances |
| `juju show-storage <id>` | Show storage details |
| `juju add-storage <app>/<n> <store>=<spec>` | Add storage to a unit |
| `juju attach-storage <app>/<n> <id>` | Attach existing storage |
| `juju detach-storage <id>` | Detach storage from a unit |
| `juju remove-storage <id>` | Remove a storage instance |
| `juju storage-pools` | List storage pools |
| `juju create-storage-pool <name> <provider>` | Create a storage pool |
| `juju remove-storage-pool <name>` | Remove a storage pool |

See [storage-and-secrets.md](storage-and-secrets.md) for detailed workflows.

## Secrets

| Command | Description |
|---------|-------------|
| `juju secrets` | List secrets |
| `juju add-secret <name> key=value` | Create a secret |
| `juju show-secret <name>` | Show secret metadata |
| `juju show-secret <name> --reveal` | Show secret content |
| `juju update-secret <name> key=value` | Update a secret |
| `juju remove-secret <name>` | Remove a secret |
| `juju grant-secret <name> <app>` | Grant access |
| `juju revoke-secret <name> <app>` | Revoke access |

## Networking

| Command | Description |
|---------|-------------|
| `juju expose <app>` | Expose an application |
| `juju expose <app> --to-cidrs <cidr>` | Expose to specific CIDRs |
| `juju expose <app> --to-spaces <space>` | Expose to specific spaces |
| `juju unexpose <app>` | Remove exposure |
| `juju spaces` | List network spaces |
| `juju add-space <name> [cidrs...]` | Create a network space |
| `juju subnets` | List subnets |
| `juju firewall-rules` | List firewall rules |
| `juju set-firewall-rule <service> --allowlist <cidrs>` | Set firewall rule |

## Cloud and Credential Management

| Command | Description |
|---------|-------------|
| `juju clouds` | List known clouds |
| `juju show-cloud <name>` | Show cloud details |
| `juju add-cloud <name>` | Add a cloud definition |
| `juju remove-cloud <name>` | Remove a cloud definition |
| `juju credentials` | List credentials |
| `juju add-credential <cloud>` | Add a credential |
| `juju remove-credential <cloud> <name>` | Remove a credential |
| `juju autoload-credentials` | Detect and add credentials |
| `juju add-k8s <name>` | Add a Kubernetes cloud |
| `juju remove-k8s <name>` | Remove a Kubernetes cloud |

## User and Access Management

| Command | Description |
|---------|-------------|
| `juju whoami` | Show current user/controller/model |
| `juju users` | List users |
| `juju add-user <name>` | Add a user |
| `juju remove-user <name>` | Remove a user |
| `juju grant <user> <access> [model]` | Grant access |
| `juju revoke <user> <access> [model]` | Revoke access |
| `juju login` | Log in to a controller |
| `juju logout` | Log out |
| `juju change-user-password` | Change password |

**Access levels:** `read` → `write` → `admin` (model), `login` → `add-model` → `superuser` (controller)

## Charmhub Discovery

| Command | Description |
|---------|-------------|
| `juju find <query>` | Search Charmhub |
| `juju info <charm>` | Show charm metadata and channels |
| `juju download <charm>` | Download a charm file |
| `juju charm-resources <charm>` | List charm resources |

### Info Example

```bash
# See channels, bases, relations, config
juju info postgresql-k8s

# JSON for parsing
juju info postgresql-k8s --format json
```

## Bundles

| Command | Description |
|---------|-------------|
| `juju deploy <bundle>` | Deploy a bundle |
| `juju export-bundle` | Export current model as bundle |
| `juju diff-bundle <bundle>` | Compare model to a bundle |

## Lifecycle Commands

| Command | Description |
|---------|-------------|
| `juju wait-for application <app>` | Wait until app reaches target state |
| `juju wait-for model <model>` | Wait until model reaches target state |
| `juju wait-for unit <app>/<n>` | Wait until unit reaches target state |

### Wait-For Examples

```bash
# Wait for app to be active
juju wait-for application myapp --query='status=="active"' --timeout=10m

# Wait for unit to be idle
juju wait-for unit myapp/0 --query='agent-status=="idle"' --timeout=5m
```

## Global Flags

These flags work with most commands:

| Flag | Description |
|------|-------------|
| `-m <controller>:<model>` | Target a specific model |
| `--format json\|yaml\|tabular` | Output format |
| `--debug` | Enable debug logging |
| `--verbose` | Enable verbose output |
| `-o <file>` | Write output to file |
| `--no-color` | Disable coloured output |
