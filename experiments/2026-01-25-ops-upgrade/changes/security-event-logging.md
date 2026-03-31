# security-event-logging

## Version
ops 3.2.0

## Type
Feature (framework-internal)

## Summary
Ops now automatically emits structured security audit events (JSON at Juju TRACE log level) for crashes, reboots, authorisation failures, and disabled health checks. No charm code changes needed.

## Before
```python
# Before ops 3.2.0: no structured security events.
# A crash just logged a traceback to stderr and juju debug-log.
# Calling reboot() or stop_checks() had no security audit trail.
# Permission-denied errors from hook commands were not flagged
# as security events.
```

## After
```python
# No charm code changes required.
# Simply upgrading to ops >= 3.2.0 enables all security event logging.
# Events appear in `juju debug-log` at TRACE level as structured JSON:
#
# {"datetime": "2025-08-27T10:30:00+00:00", "level": "WARN",
#  "type": "security", "appid": "abc123-myapp/0",
#  "event": "sys_crash:KeyError",
#  "description": "Uncaught exception in charm code: KeyError('missing_key')."}
#
# View with: juju debug-log --level TRACE | grep '"type": "security"'
```

Events logged automatically:

| Event | Trigger | Level |
|-------|---------|-------|
| `sys_crash` | Uncaught exception in charm code | WARN |
| `sys_restart` | `unit.reboot()` is called | WARN |
| `authz_fail` | Hook command fails with "access denied" / "not the leader" | CRITICAL |
| `sys_monitor_disabled` | `container.stop_checks()` is called | WARN |

## Why Upgrade
- **Automatic**: no charm code changes needed — just upgrade ops.
- **Structured**: JSON format enables machine parsing and filtering.
- **Audit trail**: compliance and security monitoring teams can track security-relevant events.
- **Standards-based**: implements Canonical SEC0045, follows the OWASP Logging Vocabulary.

## Complexity
Trivial (no charm changes needed)

## Detection
Not applicable — this is automatic when upgrading to ops 3.2.0+.

## Exemplar Charms
Not applicable — this is a framework-level change with a private API. Charm authors do not call the security logging functions directly.

## Pitfalls
- The API is private (`_log_security_event`, `_SecurityEvent`, `_SecurityEventLevel`). Charms should not call it directly.
- Events are logged at Juju TRACE level, so they won't appear in default log output. Use `juju debug-log --level TRACE` to see them.
- This is an informational improvement. It doesn't change charm behaviour.
