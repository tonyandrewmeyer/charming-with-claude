# charmcraft.yaml Reference

Complete reference for the `charmcraft.yaml` configuration file.

## File Structure

```yaml
# Required fields
name: string              # Charm name (lowercase, hyphens, no spaces)
type: charm | bundle      # Always "charm"

# Recommended fields
title: string             # Human-readable title
summary: string           # Short description (< 100 chars)
description: |           # Full description (supports markdown)
  Multi-line description
  of your charm.

# Base configuration (required for charms)
bases:
  - build-on:
      - name: ubuntu
        channel: "22.04"
        architectures: [amd64]
    run-on:
      - name: ubuntu
        channel: "22.04"
        architectures: [amd64]

# Build configuration (required)
parts:
  charm:
    plugin: uv
    source: .
    build-snaps:
      - astral-uv

# Optional but recommended
extensions: []           # List of extensions to use
charm-libs: []          # Library dependencies
links:                  # Links shown on Charmhub
  documentation: https://discourse.charmhub.io/...
  issues: https://github.com/...
  source: https://github.com/...
  website: https://...

# Advanced configuration
config:                 # Configuration options schema
  options:
    my-option:
      type: string
      description: "Description"
      default: "value"

actions:               # Available actions
  my-action:
    description: "Action description"
    params:
      param1:
        type: string
        description: "Parameter description"
    required: [param1]
    additionalProperties: false
assumes:              # Juju features required
  - juju >= 3.1

containers:           # For Kubernetes charms
  my-container:
    resource: my-image

devices:              # Device requirements
  gpu:
    type: gpu

extra-bindings:       # Extra network bindings

peers:                # Peer relations
  cluster:
    interface: cluster

provides:             # Provided relations
  website:
    interface: http

requires:             # Required relations
  database:
    interface: postgresql
    optional: true    # Always include this field!

resources:            # External resources
  my-image:
    type: oci-image
    description: "Container image"

storage:              # Storage requirements
  data:
    type: filesystem
    location: /var/lib/data
```

## Field Details

### name
- Required
- Must be unique on Charmhub
- Lowercase letters, numbers, hyphens only
- No spaces or underscores
- Must match registered name on Charmhub

### type
- Required
- Always `charm`

### title
- Recommended
- Human-readable display name
- Can include spaces and capital letters

### summary
- Recommended
- Short one-line description
- Appears in search results and listings
- Keep under 100 characters

### description
- Recommended
- Full description supporting markdown
- Appears on charm's Charmhub page
- Can be multi-line using `|` syntax

### bases
- Required for charms
- Defines what OS/versions the charm runs on
- `build-on`: Where charm is built
- `run-on`: Where charm can be deployed
- Can specify multiple bases for cross-platform support

Example multi-base:
```yaml
bases:
  - build-on:
      - name: ubuntu
        channel: "22.04"
    run-on:
      - name: ubuntu
        channel: "22.04"
      - name: ubuntu
        channel: "20.04"
  - build-on:
      - name: ubuntu
        channel: "24.04"
    run-on:
      - name: ubuntu
        channel: "24.04"
```

### parts
- Required
- Defines how to build the charm
- Most charms use the `uv` plugin
- Can include additional parts for bundled resources

Common patterns:
```yaml
# Standard charm
parts:
  charm:
    plugin: uv
    source: .
    build-snaps:
      - astral-uv

# Charm with bundled binary
parts:
  charm:
    plugin: uv
    source: .
    build-snaps:
      - astral-uv

  my-tool:
    plugin: go
    source: ./tools/my-tool
    build-snaps: [go]
```

### extensions
- Optional
- Simplify configuration for common frameworks
- Available: `django`, `fastapi`, `flask`, `go`, `spring-boot`
- Use `charmcraft list-extensions` to see all available

Example:
```yaml
extensions:
  - django
```

### charm-libs
- Only use when the charm library is not available from PyPI
- Define library dependencies
- Fetched with `charmcraft fetch-libs`
- Version can be major only ("0") or major.minor ("0.57")

Example:
```yaml
charm-libs:
  - lib: postgresql.postgres_client
    version: "0"
  - lib: mysql.client
    version: "0.57"
  - lib: operator_libs_linux.apt
    version: "0"
```

### config
- Optional
- Defines configuration options for the charm
- Users set via `juju config`

Types: `string`, `int`, `float`, `boolean`, `secret`

Example:
```yaml
config:
  options:
    port:
      type: int
      description: "Port to listen on"
      default: 8080
    enable-tls:
      type: boolean
      description: "Enable TLS/SSL"
      default: false
    server-name:
      type: string
      description: "Server hostname"
      default: "localhost"
```

### actions
- Optional
- Define operations users can run
- Executed via `juju run`

Example:
```yaml
actions:
  backup:
    description: "Create a backup"
    params:
      destination:
        type: string
        description: "Backup destination path"
    required: [destination]
    additionalProperties: false
  restore:
    description: "Restore from backup"
    params:
      source:
        type: string
        description: "Backup source path"
    required: [source]
    additionalProperties: false
```

### provides, requires, peers
- Optional
- Define relation endpoints
- ALWAYS include `optional: true` or `optional: false` for relations, *never* rely on the default

Interfaces examples:
- `http`: Web interface
- `postgresql`: PostgreSQL database
- `mysql`: MySQL database
- `mongodb`: MongoDB database
- `ingress`: Ingress/reverse proxy
- `certificates`: TLS certificates

Example:
```yaml
provides:
  website:
    interface: http

requires:
  database:
    interface: postgresql
    optional: true

  ingress:
    interface: ingress
    optional: true
    limit: 1  # Only one relation allowed

peers:
  cluster:
    interface: cluster
```

### resources
- Optional
- External files needed by charm
- OCI images for Kubernetes charms
- Binary files for machine charms

Example:
```yaml
resources:
  # For Kubernetes charms
  my-image:
    type: oci-image
    description: "Application container image"

  # For machine charms
  my-binary:
    type: file
    description: "Application binary"
    filename: my-app
```

### storage
- Optional
- Define storage requirements
- Types: `filesystem`, `block`

Example:
```yaml
storage:
  data:
    type: filesystem
    description: "Application data"
    location: /var/lib/myapp
    minimum-size: 1G

  cache:
    type: filesystem
    description: "Cache directory"
    location: /var/cache/myapp
    multiple:
      range: 0-10  # Can have 0 to 10 cache volumes
```

### containers
- Required for Kubernetes charms
- Defines sidecar containers
- Each container needs a corresponding resource

Example:
```yaml
containers:
  my-app:
    resource: my-image
    mounts:
      - storage: data
        location: /data

resources:
  my-image:
    type: oci-image
    description: "Application image"
```

### assumes
- Optional
- Declare required Juju features/versions
- Prevents deployment on incompatible Juju

Example:
```yaml
assumes:
  - juju >= 3.1
  - k8s-api
```

### devices
- Optional
- Declare hardware device requirements

Example:
```yaml
devices:
  gpu:
    type: gpu
    description: "GPU for ML workloads"
    countmin: 1
    countmax: 4
```

### links
- Recommended
- Shown on Charmhub page
- Helps users find documentation and support

Example:
```yaml
links:
  documentation: https://discourse.charmhub.io/t/my-charm-docs/12345
  issues: https://github.com/canonical/my-charm/issues
  source: https://github.com/canonical/my-charm
  website: https://myapp.example.com
```

## Complete Example

```yaml
name: postgresql-k8s
type: charm
title: PostgreSQL on Kubernetes
summary: Charmed PostgreSQL operator for Kubernetes

description: |
  PostgreSQL is a powerful, open source object-relational database system.

  This charm deploys and operates PostgreSQL on Kubernetes using the
  Charmed Operator Framework.

bases:
  - build-on:
      - name: ubuntu
        channel: "22.04"
    run-on:
      - name: ubuntu
        channel: "22.04"

parts:
  charm:
    plugin: uv
    source: .
    build-snaps:
      - astral-uv
charm-libs:
  - lib: data_platform_libs.v0.data_interfaces
    version: "0"
  - lib: observability_libs.v0.kubernetes_service_patch
    version: "0"

assumes:
  - juju >= 3.1
  - k8s-api

containers:
  postgresql:
    resource: postgresql-image

resources:
  postgresql-image:
    type: oci-image
    description: "PostgreSQL container image"

config:
  options:
    profile:
      type: string
      description: "Resource allocation profile (testing/production)"
      default: "production"

provides:
  database:
    interface: postgresql_client

  metrics-endpoint:
    interface: prometheus_scrape

requires:
  certificates:
    interface: tls-certificates
    optional: true

  s3-parameters:
    interface: s3
    optional: true
    limit: 1

peers:
  database-peers:
    interface: postgresql_peers

storage:
  pgdata:
    type: filesystem
    location: /var/lib/postgresql/data
    minimum-size: 5G

actions:
  get-primary:
    description: "Get the primary database unit"
    additionalProperties: false

  create-backup:
    description: "Create a database backup"
    params:
      s3-path:
        type: string
        description: "S3 path for backup"
    required: [s3-path]
    additionalProperties: false
links:
  documentation: https://discourse.charmhub.io/t/postgresql-k8s-docs/9308
  issues: https://github.com/canonical/postgresql-k8s-operator/issues
  source: https://github.com/canonical/postgresql-k8s-operator
  website: https://postgresql.org
```

## Validation

Charmcraft validates `charmcraft.yaml` automatically during:
- `charmcraft pack`
- `charmcraft analyse`
- `charmcraft init`

Common validation errors:
- Missing required fields
- Invalid base configuration
- Malformed YAML syntax
- Invalid charm name format
- Missing parts configuration

## Migration from metadata.yaml

Older charms used separate files:
- `metadata.yaml` - charm metadata
- `config.yaml` - configuration options
- `actions.yaml` - action definitions

Modern charms consolidate everything into `charmcraft.yaml`.

To migrate:
1. Create `charmcraft.yaml` with `name`, `type`, `title`, `summary`
2. Copy base/requires/provides/peers from `metadata.yaml`
3. Copy config options from `config.yaml` to `config:` section
4. Copy actions from `actions.yaml` to `actions:` section
5. Add `parts:` section with charm plugin
6. Test with `charmcraft pack`
7. Remove old files once working

## Best Practices

1. **Always include `optional: true` or `optional: false`** for `requires` relations
2. **Use semantic naming** for relations (database, not db)
3. **Provide good descriptions** for all config/actions
4. **Include links** to documentation and source
5. **Use charm-libs** for common integrations, but prefer versions from PyPI
6. **Keep description comprehensive** - it's your Charmhub page
7. **Test multiple bases** if supporting them
8. **Version lock libraries** when stable (use major.minor not just major)
9. **Document breaking changes** in charm description
10. **Use assumes** to prevent deployment on incompatible Juju
11. Always include `additionalProperties: false` in action definitions
