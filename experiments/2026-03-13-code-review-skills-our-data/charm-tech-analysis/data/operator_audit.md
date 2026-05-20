# Code Audit: canonical/operator (Current HEAD) - Supplementary Findings

**Date:** 2026-03-14
**Auditor:** Automated pattern-based audit (supplementary pass)
**Scope:** Core ops library and testing frameworks
**Method:** Cross-referencing patterns from CROSS_REPO_PATTERNS.md sections 3 and 5 against current source code
**Note:** This report covers NEW findings only. See `/home/ubuntu/operator-analysis/CURRENT_CODE_AUDIT.md` for previously-identified bugs.

---

## Executive Summary

This supplementary audit identified **7 new findings**: 2 high severity, 3 medium severity, and 2 low severity.

The most critical findings are:
1. **`Service.to_dict()` and `Service._merge()` silently drop `user-id: 0` and `group-id: 0`** due to falsy value confusion, meaning services intended to run as root via explicit UID/GID 0 lose that configuration during serialization or layer merging.
2. **`Framework._event_context()` lacks try/finally**, so if an event handler raises an exception, `backend._hook_is_running` is never restored, corrupting framework state for subsequent operations in the same process.

---

## High Severity Findings

### H-1: `Service.to_dict()` and `Service._merge()` drop `user-id: 0` and `group-id: 0` (falsy value confusion)

| Property | Value |
|---|---|
| **File** | `/home/ubuntu/charm-tech-analysis/operator/ops/pebble.py` |
| **Lines** | 1011 (`to_dict`), 1021 (`_merge`) |
| **Pattern** | Falsy value confusion (pattern 3.5 in CROSS_REPO_PATTERNS.md) |
| **Severity** | High |

**Code (`to_dict`):**
```python
# Line 986-1012
def to_dict(self) -> ServiceDict:
    fields = [
        ...
        ('user-id', self.user_id),   # Can be 0 (root)
        ('group-id', self.group_id), # Can be 0 (root)
        ...
        ('backoff-factor', self.backoff_factor),  # Can be 0 or 0.0
        ...
    ]
    dct = {name: value for name, value in fields if value}  # Line 1011: drops 0!
    return typing.cast('ServiceDict', dct)
```

**Code (`_merge`):**
```python
# Line 1014-1028
def _merge(self, other: Service):
    for name, value in other.__dict__.items():
        if not value or name == 'name':  # Line 1021: skips 0!
            continue
        ...
```

**Why this is a real bug:**

`user-id` and `group-id` default to `None` (lines 974, 976) and are typed as `int | None`. The value `0` is a valid Unix UID/GID representing the root user/group. Pebble's documentation explicitly supports `user-id: 0`. When a service is configured with `user-id: 0`:

- `to_dict()` omits it from the output (because `0` is falsy), so `to_yaml()` produces YAML that lacks the `user-id` field entirely.
- `_merge()` skips it during layer merging, so a higher-priority layer that sets `user-id: 0` is silently ignored.
- `__eq__()` delegates to `to_dict()`, so `Service(name='s', raw={'user-id': 0})` would incorrectly compare equal to `Service(name='s', raw={})`.

The same issue affects `backoff-factor` which defaults to `None` and could legitimately be set to `0.0`.

The `Check._merge()` method at line 1216 has the same `if not value` pattern, but the developers left a comment acknowledging the issue for `threshold` (line 1213-1215), noting it is "valid but inconsistently applied and not of any actual use." No such comment exists for the Service fields.

**Suggested fix:**
```python
# In to_dict():
dct = {name: value for name, value in fields if value is not None and value != ''}

# In _merge():
if (not value and value is not None and value != 0) or name == 'name':
    continue
```

Or more precisely, use `value is not None` for fields that default to `None`, and `value != ''` for string fields.

---

### H-2: `Framework._event_context()` context manager lacks try/finally

| Property | Value |
|---|---|
| **File** | `/home/ubuntu/charm-tech-analysis/operator/ops/framework.py` |
| **Lines** | 948-956 |
| **Pattern** | Context manager safety (pattern 9) |
| **Severity** | High |

**Code:**
```python
@contextmanager
def _event_context(self, event_name: str):
    backend: _ModelBackend | None = self.model._backend if self.model else None
    if not backend:
        yield
        return

    old_event_name = self._event_name
    self._event_name = event_name

    old_hook_is_running = backend._hook_is_running
    backend._hook_is_running = event_name
    yield                                            # Line 953: no try/finally!
    backend._hook_is_running = old_hook_is_running   # Line 954: skipped on exception
    self._event_name = old_event_name                # Line 956: skipped on exception
```

**Why this is a real bug:**

If the code inside the `with _event_context(...)` block raises an exception, the lines after `yield` (lines 954-956) are never executed. This means:

1. `backend._hook_is_running` permanently retains the event name from the failed event.
2. `self._event_name` permanently retains the failed event name.

This context manager is used in production at `framework.py:1019` (during event dispatch), at `_main.py:317` (during charm init), and at `harness.py:437` (during Harness charm init). The `_hook_is_running` flag controls access to relation data (the `RelationDataContent` class checks it to enforce access rules). If a charm's `__init__` or event handler raises and the framework catches the exception (e.g., Harness), subsequent operations would incorrectly believe a hook is still running, allowing writes to relation data that should be prohibited, or blocking writes that should be allowed.

Compare with the `_prevent_recursion()` context manager at line 3555-3560 which correctly uses try/finally.

**Suggested fix:**
```python
old_event_name = self._event_name
self._event_name = event_name

old_hook_is_running = backend._hook_is_running
backend._hook_is_running = event_name
try:
    yield
finally:
    backend._hook_is_running = old_hook_is_running
    self._event_name = old_event_name
```

---

## Medium Severity Findings

### M-1: Scenario `secret_get()` returns internal dict without copy (test/production divergence)

| Property | Value |
|---|---|
| **File** | `/home/ubuntu/charm-tech-analysis/operator/testing/src/scenario/mocking.py` |
| **Lines** | 484, 486 |
| **Pattern** | Testing/production divergence + mutability (patterns 3.1, 3.2) |
| **Severity** | Medium |

**Code:**
```python
def secret_get(self, *, id=None, label=None, refresh=False, peek=False):
    secret = self._get_secret(id, label)
    ...
    if peek or refresh:
        ...
        return secret.latest_content   # Line 484: direct reference!

    return secret.tracked_content       # Line 486: direct reference!
```

**Why this is a real bug:**

In production, `Secret.get_content()` at `ops/model.py:1475` returns `self._content.copy()`. The Scenario mock returns the Secret's internal dict directly. If a charm mutates the returned dict (e.g., `content = secret.get_content(); content['new_key'] = 'val'`), in production this is harmless (the copy is modified), but in Scenario it would corrupt the Secret dataclass's `tracked_content` or `latest_content` field. This could cause:

- Subsequent `secret_get()` calls to return the mutated data
- State assertions after the test run to see corrupted secret content
- Tests that pass in Scenario but fail in production (or vice versa)

This is exactly the pattern from commit `be090122` which fixed the same issue for `relation_get` in Scenario.

**Suggested fix:**
```python
return secret.latest_content.copy()   # Line 484
return secret.tracked_content.copy()   # Line 486
```

---

### M-2: Scenario `action_get()` returns internal params dict without copy

| Property | Value |
|---|---|
| **File** | `/home/ubuntu/charm-tech-analysis/operator/testing/src/scenario/mocking.py` |
| **Line** | 653 |
| **Pattern** | Testing/production divergence + mutability (patterns 3.1, 3.2) |
| **Severity** | Medium |

**Code:**
```python
def action_get(self):
    action = self._event.action
    if not action:
        raise ActionMissingFromContextError(...)
    return action.params   # Direct reference to internal dict!
```

**Why this is a real bug:**

In production, `_ModelBackend.action_get()` at `ops/model.py:3782` calls `hookcmds.action_get()` which returns fresh data from Juju each time. In Harness, `action_get()` at `harness.py:2651-2659` builds a new dict each time from defaults and parameters.

In Scenario, `action.params` is a `Mapping[str, AnyJson]` field on a frozen `_Action` dataclass. While `_deepcopy_mutable_fields` creates a deep copy at initialization, the returned reference allows the charm to mutate the dict, corrupting the `_Action` object's `params` field for subsequent `action_get()` calls or post-test assertions.

**Suggested fix:**
```python
return dict(action.params)
```

---

### M-3: Scenario `Container._render_services()` mutates Layer's Service objects in place

| Property | Value |
|---|---|
| **File** | `/home/ubuntu/charm-tech-analysis/operator/testing/src/scenario/state.py` |
| **Lines** | 1087-1095 |
| **Pattern** | Mutability / test-production divergence (patterns 3.1, 3.2) |
| **Severity** | Medium |

**Code:**
```python
def _render_services(self):
    services: dict[str, pebble.Service] = {}
    for layer in self.layers.values():
        for name, service in layer.services.items():
            if name in services and service.override == 'merge':
                services[name]._merge(service)      # Line 1092: mutates layer's Service!
            else:
                services[name] = service             # Line 1094: stores reference!
    return services
```

**Why this is a real bug:**

When a Container has multiple layers with merge-mode services:
1. Line 1094 stores a direct reference to Layer 1's Service object in `services`.
2. Line 1092 calls `_merge()` on that referenced object, which extends lists (`after`, `before`, `requires`) and updates dicts (`environment`, `on_check_failure`) in-place on the Layer 1 Service.
3. On the next call to `.plan` (or `.services`), the Layer 1 Service already has the merged values, and the merge is applied again, causing list fields to accumulate duplicates.

Since `Container` is a frozen dataclass and `_deepcopy_mutable_fields` only copies dict/list fields (not the `Layer` objects nested inside), the Layer's Service objects are shared by reference.

Example: if Layer 1 has `after: [db]` and Layer 2 merges `after: [cache]`:
- First `.plan` call: Layer 1 Service now has `after: [db, cache]`
- Second `.plan` call: Layer 1 Service now has `after: [db, cache, cache]`
- Third `.plan` call: `after: [db, cache, cache, cache]`

The same issue exists in `_render_checks()` (line 1097-1105) and `_render_log_targets()` (line 1107-1115).

The same pattern exists in Harness at `harness.py:3459-3474` but is less severe there because layers are typically pre-merged at `add_layer()` time.

This is a variant of the bug fixed in commit `3dda5b5f` ("Pebble layer merging in Harness mutated the original layer objects").

**Suggested fix:**
```python
def _render_services(self):
    services: dict[str, pebble.Service] = {}
    for layer in self.layers.values():
        for name, service in layer.services.items():
            if name in services and service.override == 'merge':
                services[name]._merge(service)
            else:
                services[name] = copy.deepcopy(service)  # Deep copy to avoid mutation
    return services
```

---

## Low Severity Findings

### L-1: `Plan.services`, `Plan.checks`, and `Plan.log_targets` return internal dicts without copy

| Property | Value |
|---|---|
| **File** | `/home/ubuntu/charm-tech-analysis/operator/ops/pebble.py` |
| **Lines** | 844, 852, 860 |
| **Pattern** | Mutability (pattern 3.1) |
| **Severity** | Low |

**Code:**
```python
@property
def services(self) -> dict[str, Service]:
    """This plan's services mapping (maps service name to Service).

    This property is currently read-only.
    """
    return self._services   # Line 844: direct reference to internal dict
```

**Why this is a real bug:**

The docstring says "currently read-only" but the returned dict is fully mutable. A charm calling `plan = container.get_plan(); plan.services['foo'] = new_service` or `del plan.services['foo']` would modify the Plan's internal state. While `get_plan()` creates a new Plan object each time in production (so the risk is limited), in testing contexts (Scenario's `get_plan` at `mocking.py:837` returns `self._container.plan` which itself creates a new Plan each time), modifying the returned dict could cause subtle issues.

This is the same class of bug that led to commit `3dda5b5f` and the defensive copying patterns established throughout the codebase.

**Suggested fix:**
```python
return dict(self._services)
```

---

### L-2: `Check._merge_exec()` and `Check._merge_tcp()` silently skip falsy values

| Property | Value |
|---|---|
| **File** | `/home/ubuntu/charm-tech-analysis/operator/ops/pebble.py` |
| **Lines** | 1166, 1202 |
| **Pattern** | Falsy value confusion (pattern 3.5) |
| **Severity** | Low |

**Code (`_merge_exec`):**
```python
def _merge_exec(self, other: ExecDict) -> None:
    if self.exec is None:
        self.exec = {}
    for name, value in other.items():
        if not value:       # Line 1166: skips falsy values
            continue
        ...
```

**Code (`_merge_tcp`):**
```python
def _merge_tcp(self, other: HttpDict) -> None:
    ...
    for name, value in other.items():
        if not value:       # Line 1202: skips falsy values
            continue
        self.tcp[name] = value
```

**Why this is a concern:**

For exec and tcp check configs, the values are typically strings and dicts, so `0` or `False` values are unlikely. However, the pattern is inconsistent with best practices and could cause issues if Pebble adds new numeric fields to exec or tcp check configs in the future. The `if not value` check would silently drop `0` or `False` values.

**Suggested fix:**
```python
if value is None:
    continue
```

---

## Summary Table

| ID | Severity | Pattern | File | Line(s) | Status |
|----|----------|---------|------|---------|--------|
| H-1 | **High** | Falsy value confusion | `ops/pebble.py` | 1011, 1021 | Bug: `user-id: 0` and `group-id: 0` silently dropped |
| H-2 | **High** | Context manager safety | `ops/framework.py` | 948-956 | Bug: state not restored on exception |
| M-1 | Medium | Mutability / test divergence | `testing/src/scenario/mocking.py` | 484, 486 | Bug: secret_get returns reference |
| M-2 | Medium | Mutability / test divergence | `testing/src/scenario/mocking.py` | 653 | Bug: action_get returns reference |
| M-3 | Medium | Mutability / test divergence | `testing/src/scenario/state.py` | 1087-1095 | Bug: layer merge mutates originals |
| L-1 | Low | Mutability | `ops/pebble.py` | 844, 852, 860 | Risk: Plan exposes internal dicts |
| L-2 | Low | Falsy value confusion | `ops/pebble.py` | 1166, 1202 | Risk: future falsy value issues |

### Pattern Distribution

| Bug Pattern | Count | Severity Range |
|-------------|-------|---------------|
| Falsy value confusion | 2 | High-Low |
| Mutability / no-copy return | 3 | Medium-Low |
| Testing/production divergence | 3 | Medium |
| Context manager safety | 1 | High |
