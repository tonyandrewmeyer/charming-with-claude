---
name: charmcraft
description: Expert assistant for developing Juju charms using charmcraft. Use when initializing charm projects, building charms, managing charm libraries, publishing to Charmhub, running tests, or working with charmcraft.yaml configuration. Keywords include charmcraft, Juju, charm development, Charmhub publishing, charm libraries, pack, build, upload, release, init, extensions.
---

# Charmcraft Development Assistant

Expert guidance for developing, building, testing, and publishing Juju charms using charmcraft.

## When to Use This Skill

Use this skill when:
- Initializing new charm projects
- Building and packaging charms
- Managing charm libraries (fetch, create, publish)
- Publishing charms to Charmhub
- Working with charm extensions
- Running tests and quality checks
- Troubleshooting charm build or deployment issues

## Core Workflows

### 1. Project Initialization

#### Starting a New Charm Project

```bash
# Initialize with default Kubernetes profile
charmcraft init

# Initialize with specific profile
charmcraft init --profile=machine          # Machine charms
charmcraft init --profile=kubernetes       # Kubernetes charms (default)
charmcraft init --profile=django-framework # Django app charm
charmcraft init --profile=fastapi-framework # FastAPI app charm
charmcraft init --profile=flask-framework  # Flask app charm
charmcraft init --profile=go-framework     # Go app charm
charmcraft init --profile=spring-boot-framework # Spring Boot charm

# Custom name and author
charmcraft init --name=my-charm --author="Your Name"

# Force init in non-empty directory (won't overwrite existing files)
charmcraft init --force
```

**After initialization:**
1. Review and customize `charmcraft.yaml` - this defines your charm's metadata, bases, and build configuration
2. Edit `README.md` - this becomes the charm's documentation on Charmhub
3. Implement charm logic in `src/charm.py` using the Ops framework
4. Update tests in `tests/unit/` and `tests/integration/`

#### Understanding Extensions

Extensions simplify charm development for common frameworks by providing pre-configured settings.

```bash
# List available extensions for all supported bases
charmcraft list-extensions

# See what an extension does (expand it to see the generated config)
charmcraft expand-extensions
```

Add extensions in `charmcraft.yaml`:
```yaml
extensions:
  - django
```

### 2. Building and Packaging

#### Local Development Build Cycle

```bash
# Build the charm package
charmcraft pack

# Pack with specific output directory
charmcraft pack -o ./build/

# Pack for specific base configuration (if multiple bases defined)
charmcraft pack --bases-index=0

# Pack despite lint errors (use cautiously)
charmcraft pack --force

# Clean build artifacts
charmcraft clean

# Advanced: Individual build steps
charmcraft pull    # Download/retrieve artifacts
charmcraft build   # Build artifacts
charmcraft stage   # Stage to common area
charmcraft prime   # Prime artifacts
```

**Build lifecycle:**
1. `pack` is the main command - it handles all build stages automatically
2. Use individual steps (pull, build, stage, prime) only for debugging build issues
3. Always run `charmcraft analyse` after packing to catch issues

#### Analysing Charms

```bash
# Analyse a built charm
charmcraft analyse ./my-charm_ubuntu-22.04-amd64.charm

# Get JSON output
charmcraft analyse --format=json ./my-charm.charm

# Ignore specific linters
charmcraft analyse --ignore=missing-readme,language ./my-charm.charm
```

Run analysis before uploading to Charmhub to catch:
- Missing or malformed metadata
- File permission issues
- Missing required files
- Deprecated patterns

#### Remote Building

For charms that need to be built for multiple architectures:

```bash
# Build remotely on Launchpad
charmcraft remote-build

# Remote build with LXD
charmcraft remote-build --use-lxd
```

### 3. Testing

```bash
# Run integration tests
charmcraft test

# Run specific test expressions
charmcraft test backend:ubuntu-22.04

# Shell into test environment for debugging
charmcraft test --shell

# Shell into environment after test runs
charmcraft test --shell-after

# Debug mode (shell on failure)
charmcraft test --debug
```

**Best practices:**
- Run `tox -e unit` for unit tests (state transition tests using ops.testing)
- Run `tox -e integration` or `charmcraft test` for integration tests
- Always test before uploading to Charmhub
- Use `--shell` or `--debug` flags to troubleshoot failing tests

### 4. Publishing to Charmhub

#### Account Management

```bash
# Login to Charmhub (required before first upload)
charmcraft login

# Check login status
charmcraft whoami

# Logout
charmcraft logout

# List your registered charm names
charmcraft names

# Register a new charm name
charmcraft register my-awesome-charm

# Unregister a charm name (careful!)
charmcraft unregister my-charm
```

#### Upload and Release Workflow

```bash
# Upload a charm (creates a new revision)
charmcraft upload ./my-charm_ubuntu-22.04-amd64.charm

# Upload and immediately release to a channel
charmcraft upload ./my-charm.charm --release=edge

# Upload and release to multiple channels
charmcraft upload ./my-charm.charm --release=edge --release=beta

# Upload with a specific name (if different from local directory)
charmcraft upload ./my-charm.charm --name=my-charm

# Check revision history
charmcraft revisions my-charm

# Check current status and channel assignments
charmcraft status my-charm

# Release a specific revision to channels
charmcraft release my-charm --revision=5 --channel=stable
charmcraft release my-charm --revision=5 --channel=edge --channel=beta

# Promote from one channel to another
charmcraft promote my-charm --from=beta --to=stable

# Close a channel
charmcraft close my-charm edge
```

**Channel structure:**
- Channels follow the pattern: `[track/]risk[/branch]`
- Risks: `stable`, `candidate`, `beta`, `edge`
- Default track is `latest`
- Examples: `stable`, `edge`, `2.0/candidate`, `beta/hotfix-123`

**Publishing best practices:**
1. Always upload to `edge` first
2. Test thoroughly on `edge`
3. Promote through channels: `edge` → `beta` → `candidate` → `stable`
4. Use `charmcraft status` to verify channel assignments
5. Never skip testing on lower-risk channels

#### Managing Resources

Resources are external files (like container images or binaries) that charms use.

```bash
# List resources for a charm
charmcraft resources my-charm

# Upload a resource
charmcraft upload-resource my-charm my-resource --filepath=./resource-file.tar.gz

# List resource revisions
charmcraft resource-revisions my-charm my-resource

# Set architectures for a resource revision
charmcraft set-resource-architectures my-charm my-resource --revision=3 --architecture=amd64

# Release charm with specific resource revisions
charmcraft release my-charm --revision=5 --channel=stable --resource=my-resource:3
```

#### Track Management

Tracks allow publishing different major versions of your charm.

```bash
# Create a new track
charmcraft create-track my-charm 2.0
```

### 5. Library Management

Charm libraries enable code sharing between charms.

#### Using Libraries

```bash
# Define libraries in charmcraft.yaml
# charm-libs:
#   - lib: postgresql.postgres_client
#     version: "0"
#   - lib: mysql.client
#     version: "0.57"

# Fetch defined libraries
charmcraft fetch-libs

# List available libraries from a charm
charmcraft list-lib postgresql
```

Libraries are fetched into `lib/charms/{charm_name}/{version}/{lib_name}.py`

#### Publishing Libraries

```bash
# Create a new library
charmcraft create-lib my-charm my_library

# Publish library changes
charmcraft publish-lib charms.my_charm.v0.my_library

# Publish multiple libraries
charmcraft publish-lib charms.my_charm.v0.lib1 charms.my_charm.v1.lib2
```

**Library versioning:**
- Use `v0`, `v1`, etc. for breaking changes (API changes)
- Patch version auto-increments for non-breaking changes
- Always document breaking changes in library docstrings

## Important Files

### charmcraft.yaml

Core configuration file for your charm. Defines:
- `name`: Charm name on Charmhub
- `type`: `charm` (most common) or `bundle`
- `title` and `summary`: Display metadata
- `description`: Full charm description
- `bases`: Operating system bases the charm supports
- `parts`: Build configuration
- `extensions`: Framework extensions to use
- `charm-libs`: Libraries to fetch

Example structure:
```yaml
name: my-charm
type: charm
title: My Awesome Charm
summary: Does something useful
description: |
  Longer description of what the charm does.

bases:
  - build-on:
      - name: ubuntu
        channel: "22.04"
    run-on:
      - name: ubuntu
        channel: "22.04"

parts:
  charm:
    plugin: charm
    source: .

charm-libs:
  - lib: postgresql.postgres_client
    version: "0"
```

### metadata.yaml (deprecated)

Older charms may have `metadata.yaml` instead of `charmcraft.yaml`. New charms should use `charmcraft.yaml` exclusively.

### src/charm.py

Main charm implementation using the Ops framework. Contains:
- Configuration dataclasses (using `@dataclass`)
- Action dataclasses for each action
- Main charm class (subclass of `CharmBase`)
- Event observation setup
- Event handler methods

## Best Practices

### Development Workflow

1. **Start with tests**: Write integration tests showing desired behaviour
2. **Implement incrementally**: Get basic functionality working first
3. **Use quality tools**: Run `tox -e lint` and `tox -e format` frequently
4. **Test locally**: Use `charmcraft pack` and test with `juju deploy`
5. **Analyse before upload**: Run `charmcraft analyse` on every build

### Code Quality

```bash
# Format code
tox -e format  # Uses ruff format

# Lint and type check
tox -e lint    # Uses ruff check and pyright

# Run unit tests
tox -e unit

# Run integration tests
tox -e integration
```

### Documentation

Keep these files updated:
- `README.md`: Main documentation (appears on Charmhub)
- `CONTRIBUTING.md`: Development setup and workflow
- `CHANGELOG.md`: User-facing changes (use conventional commits)
- `SECURITY.md`: Security reporting process
- `TUTORIAL.md`: Basic usage tutorial

### Version Control

Always commit:
- `charmcraft.yaml` and all source code
- `uv.lock` (dependency lock file)
- `pyproject.toml` (Python project config)
- Tests and documentation

Add to `.gitignore`:
- `*.charm` (built packages)
- `__pycache__/`
- `.tox/`
- `venv/`
- `.claude/settings.local.json`

### Security

- Never commit credentials or secrets
- Use Juju secrets for sensitive configuration
- Review dependencies regularly
- Set up Dependabot for security updates
- Configure GitHub workflow security checks (Zizmor)

## Common Patterns

### Multi-Base Builds

Build for multiple Ubuntu versions:

```yaml
# In charmcraft.yaml
bases:
  - build-on:
      - name: ubuntu
        channel: "22.04"
    run-on:
      - name: ubuntu
        channel: "22.04"
  - build-on:
      - name: ubuntu
        channel: "24.04"
    run-on:
      - name: ubuntu
        channel: "24.04"
```

Then pack for specific base:
```bash
charmcraft pack --bases-index=0  # Ubuntu 22.04
charmcraft pack --bases-index=1  # Ubuntu 24.04
```

### Working with Plugins

Charmcraft supports various plugins in the `parts` section:

```yaml
parts:
  charm:
    plugin: charm     # Standard charm plugin
    source: .

  my-binary:
    plugin: go        # Build Go binaries
    source: ./binary-src/
```

Common plugins: `charm`, `nil`, `dump`, `go`, `python`, `npm`

## Troubleshooting

### Build Issues

**"Failed to build charm"**
- Check `charmcraft.yaml` syntax
- Ensure all required files exist (`src/charm.py`, `requirements.txt`, etc.)
- Verify Python dependencies in `requirements.txt`
- Check base compatibility

**"Linting errors found"**
- Run `charmcraft analyse` to see specific errors
- Fix errors or use `--force` to pack anyway (not recommended)

### Upload Issues

**"Not logged in"**
- Run `charmcraft login`
- Check with `charmcraft whoami`

**"Charm name not registered"**
- Run `charmcraft register my-charm`
- Names must be unique across Charmhub

**"Revision already exists"**
- This is expected - Charmhub will tell you the existing revision number
- Use `charmcraft release` to publish it to channels

### Runtime Issues

**"Charm won't deploy"**
- Check base compatibility with target system
- Verify all required resources are uploaded
- Check Juju logs: `juju debug-log`
- Analyse the charm: `charmcraft analyse ./my-charm.charm`

**"Library import errors"**
- Ensure libraries are fetched: `charmcraft fetch-libs`
- Check `charm-libs` in `charmcraft.yaml`
- Verify library version compatibility

## Advanced Usage

### Platform and Architecture Control

```bash
# Build for specific platform
charmcraft build --platform=ubuntu-22.04-amd64

# Build for specific architecture
charmcraft build --build-for=arm64
```

### Using LXD Containers

```bash
# Build in LXD container instead of Multipass
charmcraft pack --use-lxd

# Useful for development on Linux hosts
```

### Destructive Mode

```bash
# Build directly on host (no container)
charmcraft pack --destructive-mode

# Faster but affects host system
# Only use in controlled environments
```

### Debugging Builds

```bash
# Shell into build environment before step runs
charmcraft pack --shell

# Shell into build environment after step runs
charmcraft pack --shell-after

# Shell into environment on build failure
charmcraft pack --debug
```

### JSON Output

Many commands support JSON output for scripting:

```bash
charmcraft revisions my-charm --format=json
charmcraft status my-charm --format=json
charmcraft analyse ./my-charm.charm --format=json
```

## Quick Reference

### Essential Commands

```bash
# Setup
charmcraft init --profile=kubernetes
charmcraft login

# Development
charmcraft pack
charmcraft analyse ./my-charm.charm
charmcraft test

# Libraries
charmcraft fetch-libs
charmcraft create-lib my-charm my_library
charmcraft publish-lib charms.my_charm.v0.my_library

# Publishing
charmcraft upload ./my-charm.charm --release=edge
charmcraft status my-charm
charmcraft release my-charm --revision=5 --channel=stable
charmcraft revisions my-charm

# Resources
charmcraft upload-resource my-charm my-resource --filepath=./file.tar.gz
charmcraft resources my-charm

# Account
charmcraft whoami
charmcraft names
charmcraft register my-charm
```

### Channel Progression

```
edge → beta → candidate → stable
 ↑      ↑         ↑          ↑
Test  Feature  Pre-release Production
     complete   testing    ready
```

### Common Flags

- `-v, --verbose`: Show debug information
- `-q, --quiet`: Only show warnings and errors
- `--format=json`: Machine-readable output
- `-h, --help`: Show command help

## Integration with Juju

After building, test with Juju:

```bash
# Pack the charm
charmcraft pack

# Analyse to verify
charmcraft analyse ./my-charm_ubuntu-22.04-amd64.charm

# Deploy locally
juju deploy ./my-charm_ubuntu-22.04-amd64.charm

# Check status
juju status

# View logs
juju debug-log

# Run actions
juju run my-charm/0 my-action

# Scale
juju add-unit my-charm

# Remove
juju remove-application my-charm
```

## Resources

- **Charmcraft documentation**: https://documentation.ubuntu.com/charmcraft/stable/
- **Juju documentation**: https://juju.is/docs
- **Ops framework**: https://documentation.ubuntu.com/ops/latest/
- **Charmhub**: https://charmhub.io/
- **Publishing guide**: https://charmhub.io/publishing

## Notes

- Always use `charmcraft pack` for building production charms
- Test on `edge` channel before promoting to `stable`
- Keep `uv.lock` in version control for reproducible builds
- Use `tox` for local testing before running `charmcraft test`
- Run `charmcraft analyse` on every build to catch issues early
- Follow conventional commits for better changelogs
- Document breaking changes in `CHANGELOG.md`
