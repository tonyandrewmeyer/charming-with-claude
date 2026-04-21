# Cross-Model Relations (CMR)

Cross-model relations allow applications in different models to integrate with each other. This is essential for multi-model architectures where shared services (databases, observability, ingress) live in a separate model from consuming applications.

## Concepts

- **Offer** — an application endpoint published for consumption by other models
- **Consumer** — an application in another model that connects to an offer
- **Offer URL** — the address of an offer: `<controller>:<user>/<model>.<app>`

## Creating an Offer

In the model that hosts the shared service:

```bash
# Switch to the provider model
juju switch <controller>:<provider-model>

# Create an offer for a specific endpoint
juju offer <app>:<endpoint>

# Create a named offer
juju offer <app>:<endpoint> <offer-name>

# Example: offer PostgreSQL's database endpoint
juju offer postgresql-k8s:database

# Example: offer with custom name
juju offer postgresql-k8s:database shared-postgres
```

## Listing and Finding Offers

```bash
# List offers in current model
juju offers

# List offers across all models
juju find-offers

# Show details of a specific offer
juju show-offer <offer-name>

# Find offers on a specific controller
juju find-offers --interface postgresql_client
```

## Consuming an Offer

In the model that wants to use the shared service:

```bash
# Switch to the consumer model
juju switch <controller>:<consumer-model>

# Consume the offer (same controller)
juju consume <user>/<provider-model>.<offer-name>

# Consume with a local alias
juju consume <user>/<provider-model>.<offer-name> <local-alias>

# Consume from a different controller
juju consume <controller>:<user>/<provider-model>.<offer-name>
```

## Integrating with a Consumed Offer

Once consumed, the offer appears as a remote application in `juju status`:

```bash
# Integrate with the consumed offer
juju integrate <local-app> <consumed-offer-name>

# Example
juju consume admin/shared.postgresql-k8s pg
juju integrate myapp pg
```

## Complete Workflow Example

### Scenario: Shared PostgreSQL for multiple applications

**Step 1: Set up the database model**
```bash
juju add-model shared-services
juju deploy postgresql-k8s --channel 14/stable --trust
juju wait-for application postgresql-k8s --query='status=="active"' --timeout=10m
```

**Step 2: Create the offer**
```bash
juju offer postgresql-k8s:database
```

**Step 3: Deploy consumer in a different model**
```bash
juju add-model my-application
juju deploy ./my-charm.charm
```

**Step 4: Consume and integrate**
```bash
# In the consumer model
juju consume admin/shared-services.postgresql-k8s shared-db
juju integrate my-charm shared-db
```

**Step 5: Verify**
```bash
juju status --relations
# Should show the cross-model relation with the offer URL
```

## Managing Offers

### Controlling Access

```bash
# Grant a user access to an offer
juju grant <user> consume <offer-name>

# Revoke access
juju revoke <user> consume <offer-name>
```

### Removing Offers

```bash
# Remove an offer (must have no active relations)
juju remove-offer <offer-name>

# Force-remove (breaks existing relations)
juju remove-offer <offer-name> --force
```

### Removing Consumed Offers

```bash
# Remove a consumed offer from the consumer model
juju remove-saas <consumed-name>
```

## Monitoring Cross-Model Relations

```bash
# In the consumer model, status shows remote applications
juju status
# Remote applications appear with their offer URL

# Check relation status
juju status --relations

# Suspend a cross-model relation (maintenance)
juju suspend-relation <relation-id>

# Resume it
juju resume-relation <relation-id>
```

## Troubleshooting CMR

**Relation not forming:**
- Verify the offer exists: `juju offers` (in provider model)
- Verify it's consumed: `juju status` (in consumer model) — look for SAAS section
- Check interface compatibility: both sides must use the same interface

**Data not flowing:**
- Check relation status: `juju status --relations`
- Check if relation is suspended: look for `suspended` status
- Inspect relation data with jhack: `jhack show-relation <local-app> <consumed-name>`

**Offer not found:**
- Check the offer URL format: `<user>/<model>.<app-or-offer-name>`
- Verify you have access: `juju find-offers`
- Check controller connectivity if cross-controller

**Performance:**
- Cross-controller CMR adds network latency
- Same-controller CMR is preferred when possible
- Monitor with `juju status --watch 2s` to see relation event timing
