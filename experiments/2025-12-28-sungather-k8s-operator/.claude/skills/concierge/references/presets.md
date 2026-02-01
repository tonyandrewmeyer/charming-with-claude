# Concierge Presets Reference

Comprehensive guide to concierge's five built-in presets for charm development environments.

## Overview

Presets provide pre-configured environments optimised for specific charm development workflows. Each preset installs a specific set of tools and providers.

## Quick Comparison

| Preset | Juju | LXD | K8s | MicroK8s | Charmcraft | Snapcraft | Rockcraft | Jhack | Use Case |
|--------|------|-----|-----|----------|------------|-----------|-----------|-------|----------|
| **dev** | ✓ | ✓† | ✓† | — | ✓ | ✓ | ✓ | ✓ | Full-featured development |
| **machine** | ✓ | ✓† | — | — | ✓ | ✓ | — | — | Traditional machine charms |
| **k8s** | ✓ | ✓* | ✓† | — | ✓ | — | ✓ | — | Kubernetes charms |
| **microk8s** | ✓ | ✓* | — | ✓† | ✓ | — | ✓ | — | Lightweight K8s |
| **crafts** | — | ✓ | — | — | ✓ | ✓ | ✓ | — | Build-only |

**Legend:**
- ✓ = Installed and configured
- ✓† = Installed AND bootstrapped with Juju controller
- ✓* = Installed but NOT bootstrapped (only for charmcraft build backend)
- — = Not included

## Detailed Preset Descriptions

### Dev Preset

**Command:** `concierge prepare -p dev`

**Purpose:** Complete, full-featured charm development environment suitable for most developers.

**What's Included:**
- **Juju** - Orchestration engine
- **LXD** - Container/VM provider (bootstrapped)
- **K8s** - Kubernetes provider (bootstrapped)
- **Charmcraft** - Charm building and testing
- **Snapcraft** - Snap package building
- **Rockcraft** - OCI image building
- **Jhack** - Development utilities

**Bootstrapped Controllers:**
- `lxd` controller on LXD provider
- `k8s` controller on K8s provider

**Best For:**
- New developers starting with charm development
- Teams working on both machine and K8s charms
- Development machines where disk space isn't a concern
- Learning and experimentation

**Considerations:**
- Largest installation footprint
- Longest setup time
- Most disk space required (~10GB+)
- All-in-one solution

**Example Usage:**
```bash
# Standard setup
concierge prepare -p dev

# With additional tools
concierge prepare -p dev --extra-snaps=astral-uv/latest/edge

# Custom Juju version
concierge prepare -p dev --juju-channel=4.0/edge
```

**After Setup:**
```bash
# Verify controllers
juju controllers

# Expected output:
# - lxd (ready)
# - k8s (ready)

# Test LXD deployment
juju add-model test-lxd lxd
juju deploy ./my-machine-charm.charm

# Test K8s deployment
juju add-model test-k8s k8s
juju deploy ./my-k8s-charm.charm
```

---

### Machine Preset

**Command:** `concierge prepare -p machine`

**Purpose:** Optimised for traditional machine charm development without Kubernetes overhead.

**What's Included:**
- **Juju** - Orchestration engine
- **LXD** - Container/VM provider (bootstrapped)
- **Charmcraft** - Charm building and testing
- **Snapcraft** - Snap package building (for workload packaging)

**Bootstrapped Controllers:**
- `lxd` controller on LXD provider

**Best For:**
- Machine charm development only
- Teams not working with Kubernetes
- CI/CD pipelines for machine charms
- Resource-constrained environments
- Traditional infrastructure focus

**Considerations:**
- No Kubernetes capability
- Lighter than `dev` preset
- Faster setup time
- No rockcraft (K8s images not needed)

**Example Usage:**
```bash
# Standard machine charm setup
concierge prepare -p machine

# With custom channels
concierge prepare -p machine \
  --juju-channel=3.6/stable \
  --lxd-channel=5.21/stable

# With development tools
concierge prepare -p machine --extra-snaps=jhack
```

**After Setup:**
```bash
# Verify controller
juju controllers

# Expected: lxd controller only

# Typical workflow
cd my-machine-charm
charmcraft pack
juju deploy ./my-charm.charm
juju status
```

---

### K8s Preset

**Command:** `concierge prepare -p k8s`

**Purpose:** Kubernetes charm development with upstream K8s snap.

**What's Included:**
- **Juju** - Orchestration engine
- **K8s** - Kubernetes provider (bootstrapped)
- **LXD** - NOT bootstrapped (charmcraft build backend only)
- **Charmcraft** - Charm building and testing
- **Rockcraft** - OCI image building

**Bootstrapped Controllers:**
- `k8s` controller on K8s provider

**Important:** LXD is installed but NOT bootstrapped. It's only available for charmcraft's build backend (for packing charms inside LXD containers).

**Best For:**
- Pure Kubernetes charm development
- Cloud-native development teams
- Testing with upstream K8s
- Production-like K8s environments

**Considerations:**
- No LXD controller (can't deploy machine charms)
- Upstream K8s (not MicroK8s)
- Heavier than microk8s preset
- More production-representative

**Example Usage:**
```bash
# Standard K8s setup
concierge prepare -p k8s

# Specific K8s version
concierge prepare -p k8s --k8s-channel=1.31/stable

# With additional tools
concierge prepare -p k8s --extra-snaps=kubectl,helm
```

**After Setup:**
```bash
# Verify controller
juju controllers

# Expected: k8s controller only

# Typical workflow
cd my-k8s-charm
charmcraft pack
juju deploy ./my-charm.charm
kubectl get pods
```

---

### MicroK8s Preset

**Command:** `concierge prepare -p microk8s`

**Purpose:** Lightweight Kubernetes charm development with MicroK8s.

**What's Included:**
- **Juju** - Orchestration engine
- **MicroK8s** - Lightweight Kubernetes (bootstrapped)
- **LXD** - NOT bootstrapped (charmcraft build backend only)
- **Charmcraft** - Charm building and testing
- **Rockcraft** - OCI image building

**Bootstrapped Controllers:**
- `microk8s` controller on MicroK8s provider

**Important:** LXD is installed but NOT bootstrapped. It's only available for charmcraft's build backend.

**Best For:**
- Lightweight K8s development
- Laptops and resource-constrained machines
- Quick K8s testing
- Local development environments
- Learning Kubernetes charms

**Considerations:**
- Faster startup than full K8s
- Lower resource usage
- MicroK8s-specific behaviour (may differ from production K8s)
- No LXD controller

**Example Usage:**
```bash
# Standard MicroK8s setup
concierge prepare -p microk8s

# Specific MicroK8s version
concierge prepare -p microk8s --microk8s-channel=1.31/stable

# Enable MicroK8s addons after setup
microk8s enable dns storage
```

**After Setup:**
```bash
# Verify controller
juju controllers

# Expected: microk8s controller only

# Check MicroK8s status
microk8s status

# Typical workflow
cd my-k8s-charm
charmcraft pack
juju deploy ./my-charm.charm
microk8s kubectl get pods
```

---

### Crafts Preset

**Command:** `concierge prepare -p crafts`

**Purpose:** Build tools only, no Juju or controller bootstrap.

**What's Included:**
- **LXD** - Container/VM provider (NOT bootstrapped)
- **Charmcraft** - Charm building
- **Snapcraft** - Snap package building
- **Rockcraft** - OCI image building

**Bootstrapped Controllers:** None (Juju not installed)

**Best For:**
- Build servers and CI/CD
- Building charms/snaps/rocks only
- Machines that don't need to run Juju
- Minimal footprint requirements
- Packaging workflows

**Considerations:**
- Cannot deploy charms (no Juju)
- Cannot test charms (no controllers)
- Smallest installation footprint
- Fastest setup time
- Build-only workflow

**Example Usage:**
```bash
# Standard build-only setup
concierge prepare -p crafts

# With specific tool versions
concierge prepare -p crafts \
  --charmcraft-channel=4.0/edge \
  --rockcraft-channel=latest/edge

# CI/CD usage
concierge prepare -p crafts --extra-debs=build-essential
```

**After Setup:**
```bash
# Verify tools installed
charmcraft version
snapcraft --version
rockcraft --version

# Juju NOT available
juju controllers  # Command not found

# Typical workflow
cd my-charm
charmcraft pack
# Ship .charm file to deployment environment

cd ../my-rock
rockcraft pack
# Ship .rock file to registry
```

---

## Choosing the Right Preset

### Decision Tree

```
Do you need to test/deploy charms?
├─ No → Use 'crafts' preset
└─ Yes → Do you work with Kubernetes?
    ├─ No → Use 'machine' preset
    ├─ Yes, K8s only → Need production-like K8s?
    │   ├─ Yes → Use 'k8s' preset
    │   └─ No → Use 'microk8s' preset
    └─ Yes, both K8s and machine → Use 'dev' preset
```

### By Use Case

| Use Case | Recommended Preset | Reason |
|----------|-------------------|--------|
| New to charm development | `dev` | Everything included, can try all charm types |
| CI/CD build pipeline | `crafts` | No runtime overhead, just build tools |
| Machine charm only | `machine` | No K8s bloat |
| K8s charm on laptop | `microk8s` | Lighter than full K8s |
| K8s charm for production | `k8s` | Upstream K8s behaviour |
| Mixed charm development | `dev` | Both machine and K8s support |
| Learning environment | `dev` | Full feature set for exploration |
| Build server | `crafts` | Minimal installation |
| Testing environment | `dev` or `k8s` | Depends on charm type |

### By Resource Constraints

| Resources | Recommended Preset | Notes |
|-----------|-------------------|-------|
| High (desktop, server) | `dev` | No constraints, install everything |
| Medium (laptop) | `microk8s` or `machine` | Choose based on charm type |
| Low (CI runner) | `crafts` | Build only, no runtime |
| Very constrained | `crafts` | Absolute minimum |

## Customising Presets

You can start with a preset and customise:

```bash
# Start with dev, add tools
concierge prepare -p dev --extra-snaps=jhack,astral-uv/latest/edge

# Start with machine, change versions
concierge prepare -p machine --juju-channel=4.0/stable

# Start with k8s, add packages
concierge prepare -p k8s --extra-debs=build-essential,python3-tox
```

## Preset Combinations

**You cannot combine presets**, but you can use YAML config to build custom combinations:

```yaml
# Custom: Machine + MicroK8s
juju:
  channel: "3.6/stable"

providers:
  lxd:
    enable: true
    bootstrap: true
  microk8s:
    enable: true
    bootstrap: true

host:
  snaps:
    - name: charmcraft
      channel: latest/stable
      classic: true
    - name: snapcraft
      channel: latest/stable
      classic: true
```

## Upgrading Between Presets

To switch presets:

```bash
# Option 1: Restore then prepare new preset
concierge restore
concierge prepare -p k8s

# Option 2: Add missing tools manually
# (if currently on 'machine' and want 'dev' features)
sudo snap install rockcraft --classic
juju bootstrap k8s
```

**Warning:** `restore` removes everything. Only use if you understand the implications.

## Preset Maintenance

### Updating Installed Tools

```bash
# Refresh all snaps
sudo snap refresh

# Refresh specific snap
sudo snap refresh juju --channel=4.0/stable

# Do NOT re-run prepare to update
# (It's not idempotent and may cause issues)
```

### Checking What's Installed

```bash
# Check concierge status
concierge status

# List snaps
snap list | grep -E 'juju|charmcraft|lxd|k8s|microk8s'

# Check controllers
juju controllers
```

## Troubleshooting Presets

### Wrong Preset Chosen

```bash
# Remove everything
concierge restore

# Prepare with correct preset
concierge prepare -p <correct-preset>
```

### Preset Fails to Install

```bash
# Try with verbose logging
concierge prepare -p dev -v

# Or trace logging
concierge prepare -p dev --trace

# Check disk space
df -h

# Check internet connectivity
ping -c 3 snapcraft.io
```

### Missing Tools After Prepare

```bash
# Verify status
concierge status

# Check which preset was used
# (no built-in way, check your command history)
history | grep "concierge prepare"

# Manually install missing tool
sudo snap install <missing-tool> --classic
```

---

## Summary

- **dev**: Everything for everyone
- **machine**: Traditional machine charms only
- **k8s**: Upstream Kubernetes charms
- **microk8s**: Lightweight Kubernetes charms
- **crafts**: Building only, no deployment

Choose based on your workflow, then customise as needed with flags or YAML config.
