# Charm Logging — Examples Catalogue

Real-world do/don't examples for every guideline in the charm logging skill.

---

## Log Levels

### DEBUG — detailed troubleshooting information

```python
# ✅ Executed commands and internal values
logger.debug("executed pebble replan for service %s", service_name)
logger.debug("TLS certificate expiry: %s", cert.not_after)

# ✅ Raw API responses (redact secrets)
logger.debug("workload status response: %s", response.json())

# ✅ Configuration values for troubleshooting
logger.debug("charm config: port=%d, tls_enabled=%s", port, tls_enabled)
```

### INFO — normal operation record

```python
# ✅ Service lifecycle
logger.info("starting alertmanager service")
logger.info("alertmanager service started on port %d", port)

# ✅ Successful action completion
logger.info("backup completed, stored at %s", backup_path)

# ✅ Significant milestones
logger.info("initial cluster formation completed with %d nodes", node_count)
```

### WARNING — potential issues

```python
# ✅ Recoverable errors
logger.warning("connection to %s failed, retrying in %ds", endpoint, delay)

# ✅ Missing config with defaults
logger.warning("log-level config not set, using default 'info'")

# ✅ Deprecation (prefer warnings.warn for this)
import warnings
warnings.warn("'legacy-mode' config is deprecated, use 'mode' instead", DeprecationWarning)
```

### ERROR — partial failure

```python
# ✅ Non-essential resource failure
logger.error("failed to update alert rules: %s", err)

# ✅ Validation preventing user action
logger.error("invalid TLS certificate: subject mismatch for %s", hostname)

# ✅ State mismatch
logger.error(
    "config-changed: relation databag validation failed for %s: %s",
    relation.name, err
)

# ✅ With exception info
try:
    client.configure(config)
except APIError:
    logger.exception("failed to apply workload configuration")
```

### CRITICAL — core service broken

```python
# ✅ Workload failed to start
logger.critical("workload failed to start: pebble returned exit code %d", code)

# ✅ Unknown failure
logger.critical("workload is down, health endpoint unreachable after %d retries", retries)

# ✅ Missing crucial configuration
logger.critical("database connection string not provided and no fallback available")
```

---

## Message Formatting: Capitalisation and Punctuation

```python
# ✅ Let the renderer decide
logger.info("restarting service %s", self._service_name)
logger.error("failed to obtain status: server returned HTTP 503")

# ⚠️ Avoid: capitalisation and trailing punctuation
logger.info("Restarting service %s.", self._service_name)
logger.error("Failed to obtain status: server returned HTTP 503.")
```

---

## Verb Tense: Before an Action

```python
# ✅ Future simple before executing
logger.info("alertmanager service will be restarted")
logger.info("certificates will be renewed for %s", hostname)

# ✅ "going to" construct is also acceptable
logger.info("alertmanager service is going to be restarted")
```

## Verb Tense: After an Action

```python
# ✅ Past simple after completion
logger.info("alertmanager service restarted")
logger.info("certificates renewed for %s", hostname)

# ⚠️ Avoid: ambiguous present continuous after completion
logger.info("restarting service alertmanager")
# Did it restart? Is it still restarting? Will it restart?
```

## Verb Tense: Present Continuous (Sequences Only)

```python
# ✅ Guaranteed follow-up with clear reference
logger.info("updating ingress for relation 'ingress:10'")
# ... work happens ...
logger.info("ingress for relation 'ingress:10' updated; config file: %s", filename)

# ⚠️ Avoid: present continuous without follow-up
logger.debug("updating certificates in /etc/ssl/certs...")
# No completion message — reader cannot tell if it succeeded

# ⚠️ Avoid: follow-up without reference to the original
logger.debug("updating certificates in /etc/ssl/certs...")
logger.debug("146 added, 0 removed; done.")
# If another log line appears between these, context is lost
```

---

## Self-Contained Messages

```python
# ✅ Self-contained — useful on its own
logger.debug(
    "ingress for relation 'ingress:10' updated; "
    "dynamic configuration file: juju_ingress_ingress_10_alertmanager.yaml"
)

# ⚠️ Avoid: meaning depends on previous lines
logger.debug("updating ingress for relation 'ingress:10'")
logger.debug("publishing external url for alertmanager: http://192.168.1.244/cos-alertmanager")
logger.debug("updated dynamic configuration file: juju_ingress_ingress_10_alertmanager.yaml")
# Third line only makes sense if you saw the first line
```

---

## Cause and Effect

```python
# ✅ Explains what happened AND why
logger.error(
    "failed processing ingress relation %s: provider is not ready, "
    "ingress for %s wiped",
    relation, related_app
)

# ⚠️ Avoid: effect without cause
logger.error("the setup of some ingress relation failed, see previous logs")
# Unhelpful — requires scrolling back through logs

# ⚠️ Avoid: unclear cause
logger.error("failed to obtain status: bad response")
# What does "bad response" mean? What should the admin do?

# ✅ Actionable context
logger.error("failed to obtain status: server returned HTTP 503, retrying in %ds", delay)
```

---

## Relevant Identifiers

```python
# ✅ Include unit names, operation IDs, resource paths
logger.error("unit mysql/1 failed health check: probe timed out after %ds", timeout)
logger.info("relation %s (id=%d) data updated for %s", relation.name, relation.id, app.name)

# ⚠️ Avoid: missing identifiers
logger.debug("updating ingress for relation 'ingress-per-unit:7'")
# Only shows relation id — not obvious which charm is on the other side

# ✅ Include enough to identify both sides
logger.debug(
    "updating ingress for relation 'ingress-per-unit:7' with %s",
    remote_app_name
)
```

---

## Avoiding Duplication and Noise

```python
# ⚠️ Avoid: repeated identical messages
logger.info("ingress:9: no relation: certificates")
logger.info("ingress:9: no relation: certificates")

# ✅ Log once, or track state to avoid repeats
if not self._logged_missing_cert_relation:
    logger.info("ingress:9: no relation: certificates")
    self._logged_missing_cert_relation = True

# ⚠️ Avoid: logging what Juju already logs
logger.info("config-changed event fired")  # Juju logs this

# ✅ Log the charm's response to the event, not the event itself
logger.info("applying new port configuration: %d", new_port)
```
