# Concierge Configuration Reference

Complete YAML configuration schema and examples for concierge.

## Overview

Concierge can be configured through:
1. **Presets** - Built-in configurations (`-p dev`)
2. **YAML file** - Custom configuration (`concierge.yaml`)
3. **Flags** - Command-line overrides (`--juju-channel=4.0/edge`)
4. **Environment variables** - Environment overrides (`CONCIERGE_JUJU_CHANNEL=4.0/edge`)

**Priority order** (highest to lowest):
1. Command-line flags
2. Environment variables
3. YAML configuration file
4. Preset defaults
5. Built-in defaults

## Configuration File

### Location

By default, concierge looks for `concierge.yaml` in the current working directory.

```bash
# Uses ./concierge.yaml
concierge prepare

# Uses specific file
concierge prepare -c /path/to/config.yaml
```

### File Naming

- Default: `concierge.yaml` in current directory
- Custom: Any path specified with `-c` flag
- Format: YAML

## Complete YAML Schema

```yaml
# Juju configuration
juju:
  channel: "3.6/stable"              # Snap channel for Juju
  agent_version: "3.6.0"             # Specific agent version (optional)
  bootstrap_constraints:             # Constraints for bootstrap
    cores: 4                         # CPU cores
    mem: 8G                          # Memory
    root-disk: 20G                   # Disk space
  model_defaults:                    # Default model configuration
    logging-config: "<root>=INFO"    # Logging configuration
    automatically-retry-hooks: true  # Auto-retry failed hooks
    update-status-hook-interval: 5m  # Status update frequency

# Provider configuration
providers:
  # MicroK8s provider
  microk8s:
    enable: true                     # Install and configure
    bootstrap: true                  # Bootstrap Juju controller
    channel: "1.31-strict/stable"    # Snap channel

  # LXD provider
  lxd:
    enable: true                     # Install and configure
    bootstrap: true                  # Bootstrap Juju controller
    channel: "5.21/stable"           # Snap channel

  # Kubernetes (upstream) provider
  k8s:
    enable: true                     # Install and configure
    bootstrap: true                  # Bootstrap Juju controller
    channel: "1.31/stable"           # Snap channel

  # Google Cloud provider
  gcloud:
    enable: false                    # Install gcloud tools
    bootstrap: false                 # Bootstrap Juju on GCP
    credential_file: ""              # Path to GCP credentials

# Host package installation
host:
  snaps:                             # Snap packages to install
    - name: jhack                    # Package name
      channel: latest/stable         # Snap channel
      classic: false                 # Classic confinement

    - name: charmcraft
      channel: latest/stable
      classic: true                  # Required for craft tools

    - name: astral-uv
      channel: latest/edge
      classic: true
      connections:                   # Snap connections (optional)
        - home                       # Connect home interface

  debs:                              # Debian packages to install
    - build-essential
    - python3-dev
    - python3-tox
    - git
```

## Field Reference

### Juju Section

Controls Juju installation and configuration.

#### `juju.channel`

**Type:** String
**Default:** `"3.6/stable"` (preset-dependent)
**Examples:** `"3.6/stable"`, `"4.0/edge"`, `"2.9/stable"`

Snap channel for Juju installation.

```yaml
juju:
  channel: "4.0/edge"  # Install latest 4.0 edge build
```

**Environment variable:** `CONCIERGE_JUJU_CHANNEL`
**Flag:** `--juju-channel`

#### `juju.agent_version`

**Type:** String
**Default:** Not set (uses channel default)
**Examples:** `"3.6.0"`, `"4.0.1"`

Specific Juju agent version to use. Rarely needed.

```yaml
juju:
  agent_version: "3.6.0"
```

#### `juju.bootstrap_constraints`

**Type:** Object
**Default:** Not set

Resource constraints for Juju controller bootstrap.

```yaml
juju:
  bootstrap_constraints:
    cores: 4           # Minimum CPU cores
    mem: 8G            # Minimum memory
    root-disk: 20G     # Minimum disk
    arch: amd64        # Architecture
    container: lxd     # Container type
```

See [Juju constraints](https://documentation.ubuntu.com/juju/3.6/reference/juju-cli/constraint/) for all options.

#### `juju.model_defaults`

**Type:** Object
**Default:** Not set

Default configuration for all models.

```yaml
juju:
  model_defaults:
    logging-config: "<root>=INFO;unit=DEBUG"
    automatically-retry-hooks: true
    update-status-hook-interval: 5m
    development: true
```

See [Juju model configuration](https://documentation.ubuntu.com/juju/3.6/reference/juju-cli/model-config-keys/) for all keys.

---

### Providers Section

Controls which providers to install and bootstrap.

#### `providers.microk8s`

MicroK8s provider configuration.

```yaml
providers:
  microk8s:
    enable: true                    # Install MicroK8s
    bootstrap: true                 # Bootstrap Juju controller
    channel: "1.31-strict/stable"   # Snap channel
```

**Fields:**
- `enable` (bool): Install and configure MicroK8s
- `bootstrap` (bool): Bootstrap Juju controller on MicroK8s
- `channel` (string): Snap channel for MicroK8s

**Environment variable:** `CONCIERGE_MICROK8S_CHANNEL`
**Flag:** `--microk8s-channel`

#### `providers.lxd`

LXD provider configuration.

```yaml
providers:
  lxd:
    enable: true               # Install LXD
    bootstrap: true            # Bootstrap Juju controller
    channel: "5.21/stable"     # Snap channel
```

**Fields:**
- `enable` (bool): Install and configure LXD
- `bootstrap` (bool): Bootstrap Juju controller on LXD
- `channel` (string): Snap channel for LXD

**Environment variable:** `CONCIERGE_LXD_CHANNEL`
**Flag:** `--lxd-channel`

**Note:** In `k8s` and `microk8s` presets, LXD is enabled but NOT bootstrapped (only for charmcraft build backend).

#### `providers.k8s`

Kubernetes (upstream) provider configuration.

```yaml
providers:
  k8s:
    enable: true            # Install K8s
    bootstrap: true         # Bootstrap Juju controller
    channel: "1.31/stable"  # Snap channel
```

**Fields:**
- `enable` (bool): Install and configure K8s snap
- `bootstrap` (bool): Bootstrap Juju controller on K8s
- `channel` (string): Snap channel for K8s

**Environment variable:** `CONCIERGE_K8S_CHANNEL`
**Flag:** `--k8s-channel`

#### `providers.gcloud`

Google Cloud provider configuration.

```yaml
providers:
  gcloud:
    enable: true                           # Install gcloud tools
    bootstrap: false                       # Bootstrap on GCP
    credential_file: ~/gcloud-creds.json   # Credentials path
```

**Fields:**
- `enable` (bool): Install Google Cloud SDK
- `bootstrap` (bool): Bootstrap Juju controller on GCP
- `credential_file` (string): Path to GCP service account credentials

**Environment variable:** `CONCIERGE_GOOGLE_CREDENTIAL_FILE`
**Flag:** `--google-credential-file`

---

### Host Section

Controls package installation on the host machine.

#### `host.snaps`

Snap packages to install.

```yaml
host:
  snaps:
    - name: jhack
      channel: latest/stable
      classic: false

    - name: astral-uv
      channel: latest/edge
      classic: true
      connections:
        - home
        - removable-media
```

**Fields per snap:**
- `name` (string, required): Snap package name
- `channel` (string): Snap channel (default: `latest/stable`)
- `classic` (bool): Use classic confinement (default: `false`)
- `connections` (array): Snap interface connections to make

**Environment variable:** `CONCIERGE_EXTRA_SNAPS` (comma-separated: `jhack,astral-uv/latest/edge`)
**Flag:** `--extra-snaps`

#### `host.debs`

Debian packages to install from Ubuntu archive.

```yaml
host:
  debs:
    - build-essential
    - python3-dev
    - python3-tox
    - git
    - make
```

**Type:** Array of strings
**Values:** Package names from Ubuntu repos

**Environment variable:** `CONCIERGE_EXTRA_DEBS` (comma-separated: `build-essential,python3-dev`)
**Flag:** `--extra-debs`

---

## Example Configurations

### Full Development Environment

```yaml
# Complete dev setup with custom tools
juju:
  channel: "3.6/stable"
  model_defaults:
    logging-config: "<root>=INFO;unit=DEBUG"
    automatically-retry-hooks: true

providers:
  lxd:
    enable: true
    bootstrap: true
    channel: "5.21/stable"

  k8s:
    enable: true
    bootstrap: true
    channel: "1.31/stable"

host:
  snaps:
    - name: charmcraft
      channel: latest/stable
      classic: true

    - name: snapcraft
      channel: latest/stable
      classic: true

    - name: rockcraft
      channel: latest/stable
      classic: true

    - name: jhack
      channel: latest/stable

    - name: astral-uv
      channel: latest/edge
      classic: true

  debs:
    - build-essential
    - python3-dev
    - python3-tox
    - git
    - make
```

### Machine Charm Development

```yaml
# Optimised for machine charms only
juju:
  channel: "3.6/stable"

providers:
  lxd:
    enable: true
    bootstrap: true
    channel: "5.21/stable"

host:
  snaps:
    - name: charmcraft
      channel: latest/stable
      classic: true

    - name: snapcraft
      channel: latest/stable
      classic: true

    - name: jhack
      channel: latest/stable

  debs:
    - python3-tox
```

### Kubernetes Development (MicroK8s)

```yaml
# Lightweight K8s development
juju:
  channel: "3.6/stable"
  model_defaults:
    update-status-hook-interval: 1m

providers:
  microk8s:
    enable: true
    bootstrap: true
    channel: "1.31-strict/stable"

  lxd:
    enable: true
    bootstrap: false  # Only for charmcraft backend
    channel: "5.21/stable"

host:
  snaps:
    - name: charmcraft
      channel: latest/stable
      classic: true

    - name: rockcraft
      channel: latest/stable
      classic: true

    - name: kubectl
      channel: latest/stable
      classic: true
```

### CI/CD Build Environment

```yaml
# Build tools only, no Juju
juju:
  channel: ""  # Disable Juju installation

providers:
  lxd:
    enable: true
    bootstrap: false  # No controller needed
    channel: "5.21/stable"

host:
  snaps:
    - name: charmcraft
      channel: latest/stable
      classic: true

    - name: snapcraft
      channel: latest/stable
      classic: true

    - name: rockcraft
      channel: latest/stable
      classic: true

    - name: astral-uv
      channel: latest/edge
      classic: true

  debs:
    - build-essential
    - make
```

**Note:** For build-only, the `crafts` preset is simpler than custom YAML.

### Mixed K8s Providers

```yaml
# Both upstream K8s and MicroK8s
juju:
  channel: "3.6/stable"

providers:
  k8s:
    enable: true
    bootstrap: true
    channel: "1.31/stable"

  microk8s:
    enable: true
    bootstrap: true
    channel: "1.31-strict/stable"

  lxd:
    enable: true
    bootstrap: false
    channel: "5.21/stable"

host:
  snaps:
    - name: charmcraft
      channel: latest/stable
      classic: true

    - name: rockcraft
      channel: latest/stable
      classic: true
```

**Result:** Two K8s controllers (`k8s` and `microk8s`) available for testing.

### Google Cloud Integration

```yaml
# GCP-enabled development
juju:
  channel: "3.6/stable"

providers:
  gcloud:
    enable: true
    bootstrap: true
    credential_file: ~/gcp-credentials.json

  lxd:
    enable: true
    bootstrap: true

host:
  snaps:
    - name: charmcraft
      channel: latest/stable
      classic: true
```

---

## Configuration Patterns

### Team Configuration

**Commit to version control** for team consistency:

```bash
# .gitignore
.claude/settings.local.json

# Include in repo
concierge.yaml
```

**Team workflow:**
```bash
# Each developer
git clone team-repo
cd team-repo
concierge prepare  # Uses committed concierge.yaml
```

### Per-Developer Overrides

Use environment variables for personal preferences:

```bash
# In ~/.bashrc or ~/.zshrc
export CONCIERGE_JUJU_CHANNEL="4.0/edge"  # Personal preference
export CONCIERGE_EXTRA_SNAPS="jhack,yq"

# Team config still used, but with overrides
concierge prepare
```

### CI/CD Pattern

Use flags in CI for explicit configuration:

```yaml
# GitHub Actions
- name: Setup environment
  run: |
    sudo snap install --classic concierge
    concierge prepare -p dev \
      --juju-channel=3.6/stable \
      --extra-snaps=astral-uv/latest/edge \
      --extra-debs=python3-tox
```

**Benefit:** Clear, auditable configuration in CI logs.

### Multi-Environment Setup

Different configs for different purposes:

```bash
# Development
concierge prepare -c dev-config.yaml

# CI/CD
concierge prepare -c ci-config.yaml

# Testing
concierge prepare -c test-config.yaml
```

---

## Environment Variables

All configuration options have environment variable equivalents.

### Naming Convention

Flag `--option-name` becomes `CONCIERGE_OPTION_NAME`:

| Flag | Environment Variable |
|------|----------------------|
| `--juju-channel` | `CONCIERGE_JUJU_CHANNEL` |
| `--lxd-channel` | `CONCIERGE_LXD_CHANNEL` |
| `--k8s-channel` | `CONCIERGE_K8S_CHANNEL` |
| `--microk8s-channel` | `CONCIERGE_MICROK8S_CHANNEL` |
| `--charmcraft-channel` | `CONCIERGE_CHARMCRAFT_CHANNEL` |
| `--snapcraft-channel` | `CONCIERGE_SNAPCRAFT_CHANNEL` |
| `--rockcraft-channel` | `CONCIERGE_ROCKCRAFT_CHANNEL` |
| `--extra-snaps` | `CONCIERGE_EXTRA_SNAPS` |
| `--extra-debs` | `CONCIERGE_EXTRA_DEBS` |
| `--google-credential-file` | `CONCIERGE_GOOGLE_CREDENTIAL_FILE` |
| `--disable-juju` | `CONCIERGE_DISABLE_JUJU` |

### Environment Variable Examples

```bash
# Set channels
export CONCIERGE_JUJU_CHANNEL="4.0/edge"
export CONCIERGE_MICROK8S_CHANNEL="1.31/stable"

# Install extras
export CONCIERGE_EXTRA_SNAPS="jhack,yq,jq"
export CONCIERGE_EXTRA_DEBS="build-essential,python3-dev"

# Use preset with overrides
concierge prepare -p dev
```

---

## Configuration Validation

### Testing Configuration

```bash
# Dry-run (not supported, but can validate manually)
# Review what would be installed
cat concierge.yaml

# Prepare with verbose output
concierge prepare -c concierge.yaml -v

# Check status
concierge status
```

### Common Validation Errors

**Invalid YAML syntax:**
```bash
# Error: yaml: line 5: mapping values are not allowed in this context
```

**Solution:** Check YAML indentation and syntax.

**Missing channel:**
```yaml
# Wrong
providers:
  lxd:
    enable: true
    channel:  # Empty!
```

**Solution:** Provide a channel value.

**Invalid snap name:**
```yaml
host:
  snaps:
    - name: non-existent-snap
```

**Solution:** Verify snap exists: `snap find <name>`

---

## Advanced Configuration

### Snap Connections

Connect snap interfaces automatically:

```yaml
host:
  snaps:
    - name: astral-uv
      channel: latest/edge
      classic: true
      connections:
        - home              # Read/write home directory
        - removable-media   # Access USB drives
        - network-bind      # Bind network ports
```

### Bootstrap Constraints

Resource guarantees for controllers:

```yaml
juju:
  bootstrap_constraints:
    cores: 4
    mem: 8G
    root-disk: 20G
    arch: amd64
    tags: controller,prod
    spaces: mgmt
```

### Model Defaults

Set consistent model configuration:

```yaml
juju:
  model_defaults:
    # Logging
    logging-config: "<root>=INFO;unit=DEBUG"

    # Behaviour
    automatically-retry-hooks: true
    update-status-hook-interval: 5m

    # Development
    development: true

    # Resources
    default-series: jammy
```

---

## Troubleshooting Configuration

### Configuration Not Applied

**Check precedence:**
```bash
# Flags override everything
concierge prepare -c config.yaml --juju-channel=4.0/edge

# Environment variables override YAML
export CONCIERGE_JUJU_CHANNEL="3.6/stable"
concierge prepare -c config.yaml  # Uses 3.6, not config value
```

### Which Config Was Used?

```bash
# Run with verbose
concierge prepare -v

# Check installed versions
snap list | grep -E 'juju|charmcraft|lxd'

# Check controllers
juju controllers
```

### Config File Not Found

```bash
# Error: config file not found

# Check current directory
ls -la concierge.yaml

# Use absolute path
concierge prepare -c /home/user/configs/concierge.yaml
```

---

## Summary

- **YAML config** for team-shared configuration
- **Environment variables** for per-developer overrides
- **Flags** for explicit CI/CD configuration
- **Presets** for quick standard setups

**Precedence:** Flags > Environment > YAML > Preset > Default

Choose the configuration method that best suits your workflow.
