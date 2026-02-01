# Charmcraft Troubleshooting Guide

Common issues and solutions when working with charmcraft.

## Build Issues

### "charmcraft.yaml: not found"

**Problem**: Running charmcraft commands outside a charm directory.

**Solution**:
```bash
# Initialise a new charm first
charmcraft init

# Or navigate to an existing charm directory
cd /path/to/charm
```

### "Failed to build charm: missing required file"

**Problem**: Missing essential files like `src/charm.py`.

**Solution**:
```bash
# Ensure all required files exist:
# - charmcraft.yaml
# - src/charm.py
# - requirements.txt (or pyproject.toml)

# Check file structure
ls -la src/
cat charmcraft.yaml
```

### "Invalid charmcraft.yaml"

**Problem**: Syntax or validation errors in charmcraft.yaml.

**Solutions**:
```bash
# Check YAML syntax
python3 -c "import yaml; yaml.safe_load(open('charmcraft.yaml'))"

# Common issues:
# 1. Incorrect indentation (use spaces, not tabs)
# 2. Missing required fields (name, type, bases, parts)
# 3. Invalid values (e.g., uppercase in name)

# Validate by attempting to pack
charmcraft pack
```

### "Base not found" or "Base compatibility issue"

**Problem**: Specified base doesn't exist or isn't compatible.

**Solution**:
```yaml
# Use supported Ubuntu LTS versions in charmcraft.yaml:
bases:
  - build-on:
      - name: ubuntu
        channel: "22.04"  # Or "20.04", "24.04"
    run-on:
      - name: ubuntu
        channel: "22.04"
```

### "Failed to pull dependencies"

**Problem**: Python dependencies can't be installed.

**Solutions**:
```bash
# Check uv.lock or pyproject.toml syntax
cat pyproject.toml
uv lock

# Test dependencies locally
uv sync

# Common issues:
# 1. Package not available for architecture
# 2. Conflicting version requirements
# 3. Missing system dependencies

# For system dependencies, add them to charmcraft.yaml:
# parts:
#   charm:
#     plugin: charm
#     source: .
#     build-packages:
#       - libssl-dev
#       - pkg-config
```

### "Build timeout"

**Problem**: Build taking too long.

**Solutions**:
```bash
# Use destructive mode on Linux (faster, no container) - **ALWAYS CHECK BEFORE RUNNING THIS COMMAND**
charmcraft pack --destructive-mode

# Or use LXD instead of Multipass (faster on Linux)
charmcraft pack --use-lxd

# Reduce dependencies if possible
# Cache builds by not cleaning between rebuilds
```

### "Out of disk space"

**Problem**: Build containers running out of space.

**Solutions**:
```bash
# Clean old build artifacts
charmcraft clean

# For Multipass (default on macOS/Windows)
multipass delete <vm name> --purge  # **ALWAYS CHECK FIRST**
multipass list

# For LXD
lxc list
lxc delete <container-name> --force  # **ALWAYS CHECK FIRST**

# Free up local disk space
rm -f *.charm  # Remove old charm files -- **ALWAYS CHECK FIRST**
```

## Testing Issues

### "charmcraft test fails to start"

**Problem**: Test environment won't start.

**Solutions**:
```bash
# Ensure spread is properly configured
cat snapcraft.yaml  # or charmcraft.yaml test section

# Check test directory structure
ls -la tests/

# Run with verbose output
charmcraft test -v

# Try shell mode to debug
charmcraft test --shell
```

### "Integration tests timeout"

**Problem**: Tests taking too long or hanging.

**Solutions**:
```bash
# Increase timeout in test configuration
# Check Juju controller status
juju controllers
juju status

# Run tests with debugging
charmcraft test --debug

# Run specific test only
charmcraft test specific-test-name
```

### "Unit tests fail with import errors"

**Problem**: Can't import charm modules in tests.

**Solutions**:
```bash
# Ensure PYTHONPATH includes lib directory
export PYTHONPATH="${PYTHONPATH}:${PWD}/lib"

# Or configure in tox.ini:
# [testenv:unit]
# setenv =
#     PYTHONPATH = {toxinidir}/lib:{toxinidir}/src

# Fetch charm libraries
charmcraft fetch-libs
```

## Publishing Issues

### "Not authenticated" or "Login required"

**Problem**: Need to login to Charmhub.

**Solution**:
```bash
# Login to Charmhub
charmcraft login

# Verify login status
charmcraft whoami

# If still failing, logout and re-login
charmcraft logout
charmcraft login
```

### "Name not registered"

**Problem**: Charm name not registered on Charmhub.

**Solution**:
```bash
# Register the charm name
charmcraft register my-charm

# Check registered names
charmcraft names

# Name must match name in charmcraft.yaml
```

### "Upload failed: Invalid charm"

**Problem**: Charm file doesn't pass Charmhub validation.

**Solutions**:
```bash
# Analyse charm before uploading
charmcraft analyse ./my-charm_ubuntu-22.04-amd64.charm

# Fix all errors reported
# Common issues:
# 1. Missing metadata (summary, description)
# 2. Invalid file permissions
# 3. Missing required files
# 4. Security issues

# Repack after fixes
charmcraft pack
```

### "Revision already exists"

**Problem**: Trying to upload identical charm.

**Solution**:
This is informational, not an error. Charmhub detected the exact same charm content.

```bash
# Get the existing revision number from output
# Use that revision to release:
charmcraft release my-charm --revision=X --channel=edge

# If you made changes, ensure they're in the packed charm:
charmcraft clean
charmcraft pack
charmcraft upload ./my-charm.charm
```

### "Can't release to stable: no revisions in candidate"

**Problem**: Trying to skip channel progression.

**Solution**:
Follow proper channel progression:
```bash
# Always progress through channels:
# 1. Upload and release to edge
charmcraft upload ./my-charm.charm --release=edge

# 2. Test on edge, then promote to beta
charmcraft promote my-charm --from=edge --to=beta

# 3. Test on beta, then promote to candidate
charmcraft promote my-charm --from=beta --to=candidate

# 4. Test on candidate, then promote to stable
charmcraft promote my-charm --from=candidate --to=stable  # **ALWAYS CHECK FIRST**
```

## Library Issues

### "Library not found"

**Problem**: Can't fetch specified library.

**Solutions**:
```bash
# Check library name and version in charmcraft.yaml
# Format: charm-name.library-name
# Not: charms.charm_name.v0.library_name

# List available libraries
charmcraft list-lib postgresql  # Use the charm name

# Fix charmcraft.yaml:
charm-libs:
  - lib: postgresql.postgres_client  # Correct
    version: "0"
  # NOT: charms.postgresql.v0.postgres_client
```

### "Library version conflict"

**Problem**: Multiple libraries with incompatible versions.

**Solutions**:
```bash
# Check installed library versions
find lib/charms -name "*.py" -type f

# Update charmcraft.yaml to use compatible versions
# Can specify exact version to pin:
charm-libs:
  - lib: postgresql.postgres_client
    version: "0.57"  # Exact version, not just "0"

# Fetch updated libraries
charmcraft fetch-libs
```

### "Can't publish library: no changes"

**Problem**: Trying to publish unchanged library.

**Solution**:
No changes detected - this is expected.
```bash
# Only publish when you've made changes to the library
# Increment LIBPATCH in library file before publishing:

# In lib/charms/my_charm/v0/my_lib.py:
# LIBAPI = 0
# LIBPATCH = 5  # Increment this

# Then publish:
charmcraft publish-lib charms.my_charm.v0.my_lib
```

## Resource Issues

### "Resource not found"

**Problem**: Specified resource doesn't exist.

**Solutions**:
```bash
# List available resources
charmcraft resources my-charm

# Upload resource first
charmcraft upload-resource my-charm my-resource --filepath=./file.tar.gz

# Then attach to release
charmcraft release my-charm --revision=5 \
  --channel=edge \
  --resource=my-resource:1
```

### "Wrong resource type"

**Problem**: Resource type doesn't match charm expectation.

**Solution**:
```yaml
# In charmcraft.yaml, ensure resource type matches:
resources:
  my-image:
    type: oci-image      # For container images
  my-binary:
    type: file           # For regular files
```

### "Resource architecture mismatch"

**Problem**: Resource built for wrong architecture.

**Solutions**:
```bash
# Check resource architectures
charmcraft resource-revisions my-charm my-resource

# Set correct architectures
charmcraft set-resource-architectures my-charm my-resource \
  --revision=3 \
  --architecture=amd64 \
  --architecture=arm64

# Or build resource for multiple architectures
```

## Runtime/Deployment Issues

### "Charm fails to install"

**Problem**: Charm errors during Juju installation.

**Debug steps**:
```bash
# Check Juju logs
juju debug-log --replay

# Check specific unit logs
juju debug-log --include=my-charm/0

# SSH into unit for debugging
juju ssh my-charm/0

# Check charm container logs (Kubernetes)
juju ssh --container charm my-charm/0

# Re-run install hook manually (debug only!)
juju exec --unit my-charm/0 -- ./dispatch install
```

### "Charm stuck in waiting/blocked state"

**Problem**: Charm not progressing.

**Debug steps**:
```bash
# Check status and messages
juju status --format=json | jq '.applications."my-charm"'

# Common causes:
# 1. Missing required relation
# 2. Configuration error
# 3. Resource not attached
# 4. Permission issues

# Check if waiting for relation:
juju status  # Look at status message

# Try relating to required charm:
juju integrate my-charm postgresql
```

### "Pebble service won't start (Kubernetes charms)"

**Problem**: Container service failing to start.

**Debug steps**:
```bash
# Check Pebble logs
juju ssh --container my-container my-charm/0 -- \
  /charm/bin/pebble logs my-service

# Check Pebble plan
juju ssh --container my-container my-charm/0 -- \
  /charm/bin/pebble plan

# Verify service status
juju ssh --container my-container my-charm/0 -- \
  /charm/bin/pebble services

# Common issues:
# 1. Wrong command in Pebble layer
# 2. Missing environment variables
# 3. Container missing dependencies
# 4. Port already in use
```

## Performance Issues

### "Build is very slow"

**Solutions**:
```bash
# Use LXD instead of Multipass on Linux
charmcraft pack --use-lxd

# Cache dependencies (don't run clean)
# Just run pack multiple times

# Reduce dependencies in requirements.txt
# Split large dependencies into separate parts
```

### "Pack creates huge charm file"

**Solutions**:
```bash
# Check what's included
unzip -l my-charm.charm | less

# Add files to .gitignore and they'll be excluded:
# *.pyc
# __pycache__/
# .tox/
# venv/
# .pytest_cache/

# Use .jujuignore for charm-specific exclusions
echo "tests/" >> .jujuignore
echo "docs/" >> .jujuignore

# Check resulting size
ls -lh *.charm
```

## Development Workflow Issues

### "Changes not reflected in charm"

**Problem**: Modifications don't appear in deployed charm.

**Solution**:
```bash
# Always repack after changes
charmcraft clean
charmcraft pack

# Refresh the deployed charm
juju refresh my-charm --path=./my-charm_ubuntu-22.04-amd64.charm

# For Kubernetes charms, might need to wait for rollout
juju status --watch 1s
```

## Getting Help

### Enable verbose logging

```bash
# All charmcraft commands support verbose mode
charmcraft -v pack
charmcraft --verbose upload ./my-charm.charm
charmcraft --verbosity=debug test
```

### Collect debugging information

```bash
# Create debug bundle for reporting issues:

# 1. charmcraft.yaml
cat charmcraft.yaml

# 2. Verbose output
charmcraft -v pack 2>&1 | tee build.log

# 3. Analysis output
charmcraft analyse ./my-charm.charm --format=json > analysis.json

# 4. Environment info
charmcraft version
python3 --version
uname -a
```

### Community resources

- **Discourse**: https://discourse.charmhub.io/
- **Matrix chat**: https://matrix.to/#/#charmhub:ubuntu.com
- **GitHub issues**: Repository-specific issue trackers
- **Documentation**: https://documentation.ubuntu.com/charmcraft/

### Filing bug reports

Include:
1. charmcraft version (`charmcraft version`)
2. Operating system and version
3. Complete error message
4. Steps to reproduce
5. charmcraft.yaml (if relevant)
6. Verbose output (`-v` flag)

Report at: https://github.com/canonical/charmcraft/issues -- **ALWAYS ASK FIRST**
