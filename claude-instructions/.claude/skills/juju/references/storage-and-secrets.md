# Storage and Secrets in Juju

## Storage

Juju storage provides persistent data volumes that survive unit removal and can be reattached. Storage is defined in the charm's `charmcraft.yaml` and provisioned at deploy time or added later.

### Storage in charmcraft.yaml

```yaml
storage:
  data:
    type: filesystem
    description: Persistent data directory
    minimum-size: 1G
    location: /var/lib/myapp/data
  logs:
    type: filesystem
    description: Log storage
    minimum-size: 500M
    location: /var/log/myapp
    read-only: false
    multiple:
      range: 1-5          # Allow 1 to 5 storage instances
```

**Storage types:**
- `filesystem` — mounted directory (most common)
- `block` — raw block device

### Deploying with Storage

```bash
# Attach storage at deploy time
juju deploy myapp --storage data=10G
juju deploy myapp --storage data=ebs,20G           # Specific pool + size
juju deploy myapp --storage data=ebs,20G,2          # 2 instances of 20G

# K8s storage
juju deploy myapp-k8s --storage data=kubernetes,10G
```

### Managing Storage

```bash
# List all storage instances
juju storage

# Show details of a specific instance
juju show-storage data/0

# Add storage to an existing unit
juju add-storage myapp/0 data=10G

# Detach storage (preserves data)
juju detach-storage data/0

# Reattach to a different unit
juju attach-storage myapp/1 data/0

# Remove storage (destroys data)
juju remove-storage data/0

# Force remove
juju remove-storage data/0 --force
```

### Storage Pools

Storage pools abstract the underlying cloud storage provider.

```bash
# List available pools
juju storage-pools

# Create a custom pool
juju create-storage-pool fast-ebs ebs volume-type=io1 iops=10000

# Use the pool
juju deploy myapp --storage data=fast-ebs,50G

# Remove a pool
juju remove-storage-pool fast-ebs
```

**Built-in pools by cloud:**

| Cloud | Pool Name | Backend |
|-------|-----------|---------|
| Kubernetes | `kubernetes` | PersistentVolumeClaim |
| AWS | `ebs`, `ebs-ssd` | EBS volumes |
| GCE | `gce` | Persistent Disks |
| Azure | `azure` | Managed Disks |
| LXD | `lxd`, `lxd-zfs` | LXD storage |
| MAAS | `maas` | MAAS storage |

### Storage Lifecycle

1. **Provisioned** — storage created when unit is deployed with `--storage` or `juju add-storage`
2. **Attached** — storage mounted to a unit; charm receives `storage-attached` event
3. **Detached** — storage unmounted; charm receives `storage-detaching` event; data is preserved
4. **Reattached** — detached storage attached to a new unit
5. **Removed** — storage destroyed permanently

**Key point:** Detached storage retains data. Use `juju detach-storage` before removing a unit if you want to preserve data.

### Storage with `--destroy-storage`

When removing applications or models, decide whether to keep or destroy storage:

```bash
# Remove app, keep storage
juju remove-application myapp

# Remove app AND storage
juju remove-application myapp --destroy-storage

# Destroy model AND all storage
juju destroy-model mymodel --destroy-storage -y
```

**Without `--destroy-storage`**, persistent storage becomes detached and orphaned — it persists in the cloud and may incur costs.

## Secrets

Juju secrets provide secure storage for sensitive data (passwords, API keys, certificates). Secrets are access-controlled and tracked.

### User-Managed Secrets

Created and managed via the Juju CLI:

```bash
# Create a secret with key-value pairs
juju add-secret my-db-creds username=admin password=s3cr3t

# Create from a file
juju add-secret my-tls-cert cert-file=/path/to/cert.pem

# Grant access to an application
juju grant-secret my-db-creds myapp

# Revoke access
juju revoke-secret my-db-creds myapp
```

### Viewing Secrets

```bash
# List all secrets in the model
juju secrets

# Show metadata (not content)
juju show-secret my-db-creds

# Show content
juju show-secret my-db-creds --reveal

# Show a specific revision
juju show-secret my-db-creds --revision 2 --reveal
```

### Updating Secrets

```bash
# Update content
juju update-secret my-db-creds password=new-s3cr3t

# Add new keys
juju update-secret my-db-creds api-key=abc123

# Update label
juju update-secret <secret-id> --label new-label
```

### Removing Secrets

```bash
# Remove a secret
juju remove-secret my-db-creds

# Remove a specific revision
juju remove-secret my-db-creds --revision 2
```

### Secret Backends

Secrets can be stored in external backends (Vault, etc.) instead of the Juju database:

```bash
# List secret backends
juju secret-backends

# Add a Vault backend
juju add-secret-backend vault vault \
  endpoint=https://vault.example.com:8200 \
  token=<token>

# Set model default backend
juju model-config secret-backend=vault

# Remove a backend
juju remove-secret-backend vault
```

### Charm-Managed Secrets

Charms can create and manage secrets programmatically via the Ops framework. These appear in `juju secrets` but are owned by the charm, not the user.

**How charms use secrets:**
1. Charm creates a secret (e.g., generated password)
2. Charm grants the secret to related applications via relation data
3. Consumer charms access the secret content via the secret ID
4. Owner charm can rotate/update the secret; consumers receive `secret-changed` events

**As an operator, you typically don't need to manage charm-owned secrets directly**, but you can inspect them:

```bash
# List all secrets including charm-owned
juju secrets

# Show who owns and has access to a secret
juju show-secret <secret-id>
```

### Secret Access Control

| Actor | Can Create | Can Read | Can Update | Can Delete |
|-------|-----------|----------|-----------|-----------|
| Model admin | Yes | Yes (--reveal) | Yes | Yes |
| Granted app | No | Yes (via charm) | No | No |
| Other apps | No | No | No | No |
| Charm owner | Yes | Yes | Yes | Yes |

### Troubleshooting Secrets

**"permission denied" when accessing a secret:**
```bash
# Grant access to the application
juju grant-secret <secret-name> <app>
```

**Secret not found:**
```bash
# List all secrets to find correct name/ID
juju secrets

# Secrets may be in a different model
juju secrets -m <controller>:<model>
```

**Secret content not updating in charm:**
- The charm receives a `secret-changed` event when a secret it observes is updated
- Check charm logs for handling of this event
- Verify the update: `juju show-secret <name> --reveal`
