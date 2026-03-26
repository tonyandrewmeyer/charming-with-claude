---
name: charm-logging
description: Canonical charm logging guidelines. Use when adding logging to charms or reviewing charm log messages. Covers log levels, message formatting, tense, and common pitfalls.
argument-hint: [topic]
license: default
compatibility: universal
allowed-tools: Read Grep Glob
---

# Charm Logging Guidelines

These guidelines standardise logging patterns across the charm ecosystem, ensuring logs are useful at development time and during production operation. Logging levels follow the Python `logging` module.

Based on spec OB061.

For full do/don't examples of every guideline, see [examples.md](examples.md).

---

## Log Levels

### DEBUG
**Purpose**: detailed information for debugging or troubleshooting.

- Default Juju `debug-log` level is INFO, so DEBUG messages are **typically not seen**
- Do not assume DEBUG messages are used for alert rules
- Do not assume DEBUG messages are stored long-term
- **Note**: logs are still sent to Juju which filters by level config — do not assume expensive DEBUG logging is free

**Examples**:
- Executed commands, functions, methods; internal variable values
- Raw responses from external services or API calls (**redact secrets**)
- Configuration values for troubleshooting

### INFO
**Purpose**: record of the **normal operation** of the charm. This is the default Juju `debug-log` level.

**Examples**:
- Starting or stopping a service
- Successful completion of an action
- Important milestones or significant events
- System health checks or status reports

### WARNING
**Purpose**: potential issues that may lead to errors if not addressed.

**Examples**:
- Errors the application can recover from without significant impact
- Missing config file, using defaults
- Retrying a failed connection

### ERROR
**Purpose**: a failure preventing part of the workload from working properly, without completely breaking its core service.

**Examples**:
- Failed to create/update a non-essential resource (config file, certificates, alert rules)
- Validation error preventing user action
- Mismatch between workload state and charm model data
- Caught exceptions signalling non-transient issues (consider `logger.exception`)
- Network communication errors (timeouts, DNS failures)
- External API/service failures

### CRITICAL
**Purpose**: a severe error breaking the charm's core service, requiring immediate attention.

**Examples**:
- Workload failed to start; upgrade failed
- Workload is down for unknown reasons
- Crucial configuration missing without fallback defaults
- Health endpoint reports internal error

### Deprecation warnings
Use `warnings.warn` rather than `logging.warn` — both appear in Juju logs, but `warnings` provides more control and is designed for this use case.

---

## Message Formatting Guidelines

### Be clear, direct, and concise
Avoid ambiguity. Messages should be understood without additional context.

```python
# BAD — unclear what "bad response" means
logger.error("failed to obtain status: bad response")

# GOOD — actionable context
logger.error("failed to obtain status: server returned HTTP 503")
```

### Let the renderer determine capitalisation and punctuation
```python
# GOOD
logger.info("restarting service %s", self._service_name)

# BAD
logger.info("Restarting service %s.", self._service_name)
```

### Verb tense

| When | Tense | Example |
|------|-------|---------|
| Before an action | Future simple | `"alertmanager service will be restarted"` |
| After an action | Past simple | `"alertmanager service restarted"` |
| During an action (sequence) | Present continuous | `"updating ingress for relation 'ingress:10'"` — **only if** a follow-up message is guaranteed |

**Avoid** present continuous unless it is part of a guaranteed sequence with a clear reference between start and end messages.

### Make each message self-contained
The meaning of a log line should **not depend** on previous or subsequent lines. Include enough context to be useful during debugging or auditing.

### Include cause and effect
Explain not only what happened, but **why**:
```python
# BAD
logger.error("the setup of some ingress relation failed, see previous logs")

# GOOD
logger.error("failed processing ingress relation %s: provider is not ready", relation)
```

### Include relevant identifiers
Operation IDs, unit names, resource paths:
```
"unit mysql/1 failed health check: probe timed out"
```

### Avoid duplication and noise
- Do not log the same information repeatedly
- Do not log what Juju already logs (e.g. that an event is running)
- Each message should add value
