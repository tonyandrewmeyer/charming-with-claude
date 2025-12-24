# Example Usage of the Charmcraft Skill

This document demonstrates how Claude uses the charmcraft skill in practice.

## Example 1: Creating a New Charm

**User Query**: "I want to create a new Kubernetes charm for a Flask web application"

**Claude's Response** (using the charmcraft skill):

I'll help you create a new Kubernetes charm for a Flask application. We'll use the flask-framework profile which sets up the charm with Flask-specific configuration.

```bash
charmcraft init --profile=flask-framework --name=my-flask-app --author="Your Name"
```

This creates a charm with:
- Pre-configured Flask application structure
- charmcraft.yaml with Flask extension
- Example charm code in src/charm.py
- Unit and integration test templates
- Requirements.txt with ops framework

After initialization, you'll need to:

1. **Update charmcraft.yaml** - Review the bases, add any relations your app needs:
```yaml
requires:
  database:
    interface: postgresql_client
    optional: true
  ingress:
    interface: ingress
    optional: true
```

2. **Implement src/charm.py** - Add your Flask app's specific configuration:
   - Database connection setup
   - Environment variable management
   - Container configuration via Pebble

3. **Add your Flask app code** - The charm expects your Flask app at a specific location configured in the extension.

Would you like me to help with any of these customization steps?

---

## Example 2: Building and Publishing

**User Query**: "Build my charm and publish it to Charmhub on the edge channel"

**Claude's Response** (using the charmcraft skill):

I'll help you build and publish your charm. First, let's build and analyze it:

```bash
# Build the charm
charmcraft pack

# Analyze to check for issues
charmcraft analyse ./my-charm_ubuntu-22.04-amd64.charm
```

The analysis will check for:
- Missing or malformed metadata
- File permission issues
- Missing required files
- Deprecated patterns

If the analysis passes, we can proceed with publishing:

```bash
# Login to Charmhub (if not already logged in)
charmcraft login

# Upload and release to edge channel
charmcraft upload ./my-charm_ubuntu-22.04-amd64.charm --release=edge

# Verify the release
charmcraft status my-charm
```

Best practices for publishing:
1. ✅ Always test on edge first
2. ✅ Run integration tests against the edge deployment
3. ✅ Progress through channels: edge → beta → candidate → stable
4. ✅ Never skip channel testing

To test the edge release:
```bash
juju deploy my-charm --channel=edge
juju status
# Run your integration tests
```

---

## Example 3: Managing Charm Libraries

**User Query**: "I need to add PostgreSQL database support to my charm"

**Claude's Response** (using the charmcraft skill):

I'll help you add PostgreSQL support using the official data platform library. This is the recommended approach for database integration.

1. **Add the library to charmcraft.yaml**:

```yaml
charm-libs:
  - lib: data_platform_libs.data_interfaces
    version: "0"
```

2. **Fetch the library**:

```bash
charmcraft fetch-libs
```

This downloads the library to `lib/charms/data_platform_libs/v0/data_interfaces.py`

3. **Update src/charm.py to use the library**:

```python
from charms.data_platform_libs.v0.data_interfaces import DatabaseRequires

class MyCharm(CharmBase):
    def __init__(self, *args):
        super().__init__(*args)

        # Set up database relation
        self.database = DatabaseRequires(
            self,
            relation_name="database",
            database_name="myapp",
        )

        # Observe database events
        self.framework.observe(
            self.database.on.database_created,
            self._on_database_created
        )

    def _on_database_created(self, event):
        """Handle database creation."""
        if not event.database:
            return

        # Get connection details
        connection_string = event.database

        # Configure your app with the database
        # ...
```

4. **Add the relation to charmcraft.yaml**:

```yaml
requires:
  database:
    interface: postgresql_client
    optional: true  # Always include this!
```

5. **Test the integration**:

```bash
# Pack and deploy
charmcraft pack
juju deploy ./my-charm.charm
juju deploy postgresql-k8s
juju integrate my-charm postgresql-k8s

# Verify connection
juju status
```

The data_interfaces library handles all the complexity of database provisioning, credentials, and connection management.

---

## Example 4: Troubleshooting Build Issues

**User Query**: "I'm getting an error when running charmcraft pack: 'Failed to build charm: missing required file'"

**Claude's Response** (using the charmcraft skill):

Let's diagnose this build issue. The "missing required file" error usually means one of the essential charm files is not found.

First, let's check your directory structure:

```bash
# Verify all required files exist
ls -la src/charm.py
ls -la charmcraft.yaml
ls -la requirements.txt  # Or pyproject.toml
```

Required files for a charm:
- ✅ `charmcraft.yaml` - Build configuration
- ✅ `src/charm.py` - Main charm code
- ✅ `requirements.txt` OR `pyproject.toml` - Python dependencies

Common causes and solutions:

**1. Missing src/charm.py**
```bash
# Create the file if it doesn't exist
mkdir -p src
touch src/charm.py
# Then implement your charm class
```

**2. Wrong directory structure**
```bash
# Ensure you're in the charm root directory
pwd
ls -la charmcraft.yaml  # Should exist here
```

**3. Missing requirements.txt**
```bash
# Create if missing
echo "ops >= 2.0" > requirements.txt
```

**4. Invalid charmcraft.yaml syntax**
```bash
# Validate YAML syntax
python3 -c "import yaml; yaml.safe_load(open('charmcraft.yaml'))"
```

After fixing, try building again:

```bash
# Clean previous build attempts
charmcraft clean

# Build with verbose output to see details
charmcraft -v pack
```

If you're still getting errors, please share:
1. The complete error message
2. Your directory structure (`ls -la`)
3. Your charmcraft.yaml file

---

## Example 5: Using the Quick Start Script

**User Query**: "Can you help me quickly set up a new machine charm project with all the recommended files?"

**Claude's Response** (using the charmcraft skill):

I can use the quick-start helper script to set up a complete charm project with all recommended files and best practices.

Let me use the script from the charmcraft skill:

```bash
# Run the quick-start script
./scripts/quick-start.sh -n my-machine-charm -p machine -a "Your Name"
```

This script will:

1. ✅ Create the charm directory structure
2. ✅ Run `charmcraft init` with the specified profile
3. ✅ Create additional recommended files:
   - `SECURITY.md` - Security reporting process
   - `CODE_OF_CONDUCT.md` - Community guidelines
   - `CHANGELOG.md` - Version history tracking
   - `TUTORIAL.md` - Basic usage guide
4. ✅ Set up comprehensive `.gitignore`
5. ✅ Configure pre-commit hooks
6. ✅ Initialize git repository with initial commit

After the script completes, your project structure will look like:

```
my-machine-charm/
├── charmcraft.yaml
├── CHANGELOG.md
├── CODE_OF_CONDUCT.md
├── CONTRIBUTING.md
├── LICENSE
├── README.md
├── SECURITY.md
├── TUTORIAL.md
├── pyproject.toml
├── requirements.txt
├── src/
│   ├── charm.py
│   └── workload.py
├── tests/
│   ├── integration/
│   │   └── test_charm.py
│   └── unit/
│       └── test_charm.py
├── tox.ini
├── uv.lock
└── .pre-commit-config.yaml
```

Next steps:
1. Review `charmcraft.yaml` and customize for your workload
2. Implement charm logic in `src/charm.py`
3. Update `README.md` with charm-specific documentation
4. Install pre-commit hooks: `pre-commit install`
5. Start developing!

---

## Example 6: Understanding charmcraft.yaml Configuration

**User Query**: "What should I put in the charmcraft.yaml for a charm that needs database and ingress integrations?"

**Claude's Response** (using the charmcraft skill):

For a charm that needs database and ingress integrations, your charmcraft.yaml should look like this:

```yaml
name: my-webapp
type: charm
title: My Web Application
summary: A web application charm with database and ingress support

description: |
  This charm deploys a web application with:
  - PostgreSQL database integration
  - Ingress (reverse proxy) support
  - Automatic TLS certificate management

bases:
  - build-on:
      - name: ubuntu
        channel: "22.04"
    run-on:
      - name: ubuntu
        channel: "22.04"

# Kubernetes charm configuration
containers:
  webapp:
    resource: webapp-image

resources:
  webapp-image:
    type: oci-image
    description: "Web application container image"

# Relations
provides:
  metrics-endpoint:
    interface: prometheus_scrape
    optional: true

requires:
  database:
    interface: postgresql_client
    optional: true  # ALWAYS include!

  ingress:
    interface: ingress
    optional: true  # ALWAYS include!
    limit: 1        # Only one ingress relation

  certificates:
    interface: tls-certificates
    optional: true

# Configuration options
config:
  options:
    port:
      type: int
      description: "Application port"
      default: 8080

    external-hostname:
      type: string
      description: "External hostname for ingress"
      default: ""

# Build configuration
parts:
  charm:
    plugin: charm
    source: .

# Libraries for database and ingress
charm-libs:
  - lib: data_platform_libs.data_interfaces
    version: "0"
  - lib: nginx_ingress_integrator.ingress
    version: "0"
  - lib: tls_certificates_interface.tls_certificates
    version: "0"

# Links
links:
  documentation: https://discourse.charmhub.io/...
  issues: https://github.com/yourorg/my-webapp/issues
  source: https://github.com/yourorg/my-webapp
```

Key points for your configuration:

1. **Relations** - Define clear interfaces:
   - `database`: Uses `postgresql_client` for PostgreSQL
   - `ingress`: Uses standard `ingress` interface
   - `certificates`: For TLS/SSL support
   - All marked `optional: true` (required!)

2. **Charm libraries** - Pre-built integrations:
   - `data_interfaces`: Database connection handling
   - `ingress`: Reverse proxy configuration
   - `tls_certificates`: Certificate management

3. **Container configuration** - For Kubernetes:
   - Define container and corresponding OCI image resource
   - Application runs in this container

4. **Config options** - User-configurable settings:
   - Application-specific configuration
   - External access settings

To use these relations in your charm:

```python
from charms.data_platform_libs.v0.data_interfaces import DatabaseRequires
from charms.nginx_ingress_integrator.v0.ingress import IngressRequires

class MyCharm(CharmBase):
    def __init__(self, *args):
        super().__init__(*args)

        # Database relation
        self.database = DatabaseRequires(
            self, "database", "myapp"
        )

        # Ingress relation
        self.ingress = IngressRequires(
            self,
            {
                "service-hostname": self.config["external-hostname"],
                "service-port": self.config["port"],
            }
        )
```

Would you like help implementing the charm logic for these integrations?

---

## How the Skill Helps

In all these examples, the charmcraft skill provides:

1. **Accurate command syntax** - Correct charmcraft commands with proper flags
2. **Best practices** - Following Canonical charm development standards
3. **Complete workflows** - End-to-end guidance from init to deployment
4. **Troubleshooting** - Solutions for common issues
5. **Configuration examples** - Real-world charmcraft.yaml patterns
6. **Integration patterns** - Using charm libraries correctly

The skill ensures Claude provides consistent, accurate, and production-ready guidance for all charmcraft operations.
