## Bug Review: operator repo (ops/pebble.py, ops/framework.py, testing/src/scenario/mocking.py)

### Summary
- **Findings**: 9 (3 High, 5 Medium, 1 Low)
- **Code areas reviewed**: Pebble layer/service/check configuration, Framework event context management, Scenario testing backend (mocking), secrets, actions, data mutability, falsy value checks, context manager safety, datetime handling
- **Repos affected**: operator

### Findings

#### [BUG-001] Context Manager Safety -- `_event_context` missing try/finally (High)
- **Location**: `ops/framework.py:922-956`
- **Pattern**: Context managers: yield without try/finally
- **Issue**: The `_event_context` context manager sets `backend._hook_is_running` and `self._event_name` before the `yield`, but restores them after the `yield` without a `try/finally` block. If the body of the `with` statement raises an exception, the old values are never restored.
- **Impact**: After an unhandled exception during event dispatch, `backend._hook_is_running` and `self._event_name` remain set to the failed event's name. This causes the Harness and Scenario backends to incorrectly believe they are still inside a hook execution, which can affect subsequent behavior in testing and event re-emission.
- **Evidence**:
  ```python
  @contextmanager
  def _event_context(self, event_name: str):
      # ...
      old_event_name = self._event_name
      self._event_name = event_name

      old_hook_is_running = backend._hook_is_running
      backend._hook_is_running = event_name
      yield
      backend._hook_is_running = old_hook_is_running  # skipped on exception

      self._event_name = old_event_name  # skipped on exception
  ```
- **Recommended fix**:
  ```python
  @contextmanager
  def _event_context(self, event_name: str):
      # ...
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
- **Historical precedent**: Referenced in `references/bug-patterns.md` as a current bug. Compare with `hooks_disabled()` in `ops/_private/harness.py:765-784` which correctly uses `try/finally`.

---

#### [BUG-002] Falsy Value -- `Service.to_dict()` drops zero-valued fields (High)
- **Location**: `ops/pebble.py:1011`
- **Pattern**: Falsy value: if value / if not value
- **Issue**: `Service.to_dict()` uses `{name: value for name, value in fields if value}` to filter out unset fields. This drops any field whose value is falsy, including `user-id: 0` (root) and `group-id: 0` (root group), `backoff-factor: 0`, and `threshold: 0` for checks.
- **Impact**: A Pebble service configured to run as root (`user-id: 0` or `group-id: 0`) will silently lose those fields when serialized to dict/YAML, causing the service to run as a different user. This is both a correctness and a potential security issue.
- **Evidence**:
  ```python
  # ops/pebble.py:986-1012
  def to_dict(self) -> ServiceDict:
      fields = [
          # ...
          ('user-id', self.user_id),   # user_id=0 is falsy
          ('group-id', self.group_id), # group_id=0 is falsy
          ('backoff-factor', self.backoff_factor),  # backoff_factor=0 is falsy
          # ...
      ]
      dct = {name: value for name, value in fields if value}  # drops 0 values
  ```
- **Recommended fix**:
  ```python
  dct = {name: value for name, value in fields if value is not None and value != ''}
  ```
  Or use a sentinel to distinguish "not set" from "set to 0".
- **Historical precedent**: Referenced in `references/bug-patterns.md` as a current bug.

---

#### [BUG-003] Falsy Value -- `Service._merge()` skips zero-valued fields (High)
- **Location**: `ops/pebble.py:1020-1021`
- **Pattern**: Falsy value: if not value
- **Issue**: `Service._merge()` uses `if not value` to skip fields, which means numeric fields set to `0` (e.g., `user_id=0`, `group_id=0`, `backoff_factor=0`) in the merging layer are silently ignored.
- **Impact**: When merging Pebble layers, a layer that explicitly sets `user-id: 0` or `group-id: 0` will not apply those settings, leaving the original layer's value in place.
- **Evidence**:
  ```python
  def _merge(self, other: Service):
      for name, value in other.__dict__.items():
          if not value or name == 'name':  # skips user_id=0, group_id=0
              continue
  ```
- **Recommended fix**:
  ```python
  for name, value in other.__dict__.items():
      if name == 'name':
          continue
      if value is None or (isinstance(value, str) and value == ''):
          continue
  ```
- **Historical precedent**: Referenced in `references/bug-patterns.md` as a current bug.

---

#### [BUG-004] Falsy Value -- `Check.to_dict()` and sub-merge methods drop zero values (Medium)
- **Location**: `ops/pebble.py:1142, 1166, 1184, 1202`
- **Pattern**: Falsy value: if value / if not value
- **Issue**: `Check.to_dict()` uses `{name: value for name, value in fields if value}` which drops `threshold: 0`. The `_merge_exec`, `_merge_http`, and `_merge_tcp` sub-merge methods all use `if not value` to skip fields, which would drop `port: 0` in TCP checks or `user-id: 0` in exec checks.
- **Impact**: A check with `threshold: 0` would lose that field in serialization. Exec checks with `user-id: 0` (root) would lose the user-id during merge. TCP checks with port 0 (unlikely but valid as "any available port") would lose the port. The `Check._merge` comment at line 1213-1215 acknowledges this for threshold but dismisses it as "not of any actual use", which is debatable.
- **Evidence**:
  ```python
  # Check.to_dict() line 1142
  dct = {name: value for name, value in fields if value}

  # _merge_exec line 1166
  if not value:
      continue

  # _merge_tcp line 1202
  if not value:
      continue
  ```
- **Recommended fix**: Use `if value is not None and value != ''` or a similar guard that preserves zero values.

---

#### [BUG-005] Falsy Value -- `LogTarget.to_dict()` and `_merge()` drop empty-but-valid values (Medium)
- **Location**: `ops/pebble.py:1280, 1301`
- **Pattern**: Falsy value: if value / if not value
- **Issue**: Same pattern as Service and Check: `to_dict()` uses `if value` and `_merge()` uses `if not value`, which would drop any fields that are falsy.
- **Impact**: Lower impact for LogTarget since fields are mostly strings and lists, but the pattern is inconsistent with correct handling.
- **Evidence**:
  ```python
  # to_dict() line 1280
  dct = {name: value for name, value in fields if value}

  # _merge() line 1301
  if not value or name == 'name':
      continue
  ```
- **Recommended fix**: Same as BUG-002/003.

---

#### [BUG-006] Mutability -- `Plan.services`, `.checks`, `.log_targets` return internal dicts (Medium)
- **Location**: `ops/pebble.py:838-860`
- **Pattern**: Mutability: returning internal state
- **Issue**: The `Plan` class properties `services`, `checks`, and `log_targets` return internal `self._services`, `self._checks`, and `self._log_targets` dicts directly. The docstrings say "This property is currently read-only" but there is no enforcement. Callers can mutate these dicts (add, remove, or modify entries), corrupting the Plan's internal state.
- **Impact**: A caller doing `plan.services['svc'] = new_service` or `del plan.services['svc']` would modify the Plan object's internal state, leading to incorrect `to_dict()` / `to_yaml()` output. The Scenario `Container.plan` property directly assigns rendered services into `plan.services` (state.py:1131), which is the intended mutation path, but external callers could do the same unexpectedly.
- **Evidence**:
  ```python
  @property
  def services(self) -> dict[str, Service]:
      """This property is currently read-only."""
      return self._services  # returns mutable reference
  ```
- **Recommended fix**:
  ```python
  @property
  def services(self) -> dict[str, Service]:
      return dict(self._services)
  ```
  Or use `types.MappingProxyType`.
- **Historical precedent**: Referenced in `references/bug-patterns.md` as a current bug.

---

#### [BUG-007] Mutability -- Scenario `_render_services` / `_render_checks` / `_render_log_targets` mutate layer objects in place (Medium)
- **Location**: `testing/src/scenario/state.py:1087-1115`
- **Pattern**: Mutability: layer merging mutation (variant of commit `3dda5b5f`)
- **Issue**: When rendering the plan, `_render_services()` stores a direct reference to the layer's Service object (line 1094: `services[name] = service`). When a subsequent layer merges into it (line 1092: `services[name]._merge(service)`), the `_merge` method mutates the original layer's Service object in place, calling `.extend()` on its list fields (`after`, `before`, `requires`) and `.update()` on dict fields (`environment`, `on_check_failure`). Calling `.plan` a second time doubles the list entries.
- **Impact**: Repeated access to `container.plan` produces progressively incorrect plans with duplicated list entries. For example, if a service has `after: ["svc1"]` in layer 1 and `override: merge` in layer 2, the first call to `.plan` gives `after: ["svc1"]` but the second gives `after: ["svc1", "svc1"]`. Same issue exists in `_render_checks` and `_render_log_targets`, and also in the Harness version at `ops/_private/harness.py:3459-3494`.
- **Evidence**:
  ```python
  def _render_services(self):
      services: dict[str, pebble.Service] = {}
      for layer in self.layers.values():
          for name, service in layer.services.items():
              if name in services and service.override == 'merge':
                  services[name]._merge(service)  # mutates original layer's service
              else:
                  services[name] = service  # stores reference, not copy
      return services
  ```
- **Recommended fix**:
  ```python
  services[name] = copy.deepcopy(service)  # store a copy, not a reference
  ```
- **Historical precedent**: Referenced in `references/bug-patterns.md` as a current bug, variant of commit `3dda5b5f`.

---

#### [BUG-008] Testing Divergence -- Scenario `action_get` returns internal dict without copy (Medium)
- **Location**: `testing/src/scenario/mocking.py:647-653`
- **Pattern**: Testing: return without copy
- **Issue**: `_MockModelBackend.action_get()` returns `action.params` directly. Although `_Action` is a frozen dataclass and `_deepcopy_mutable_fields` deep-copies mutable fields in `__post_init__`, the returned `params` dict is still the internal reference. A caller mutating the returned dict would modify the `_Action` object's `params` field. In contrast, production `action_get` calls `hookcmds.action_get()` which returns freshly-parsed JSON each time.
- **Impact**: A charm that modifies the dict returned by `action_get()` would see the modification persist across multiple calls in testing, but not in production. This testing/production divergence could mask bugs or create false confidence in tests.
- **Evidence**:
  ```python
  def action_get(self):
      action = self._event.action
      if not action:
          raise ActionMissingFromContextError(...)
      return action.params  # returns internal reference
  ```
- **Recommended fix**:
  ```python
  return dict(action.params)
  ```
- **Historical precedent**: Referenced in `references/bug-patterns.md`. Similar fix was applied to `relation_get` in commit `be09012`.

---

#### [BUG-009] Datetime -- `datetime.now()` without timezone (Low)
- **Location**: `testing/src/scenario/mocking.py:815`, `testing/src/scenario/state.py:342`, `ops/_private/harness.py:2866,3183,3224`, `ops/model.py:539`
- **Pattern**: Datetime: missing timezone
- **Issue**: Multiple locations use `datetime.datetime.now()` without a timezone argument, creating naive datetimes. These are used for Pebble change timestamps, secret expiry calculations, and rotation times.
- **Impact**: Naive datetimes can cause comparison issues with timezone-aware datetimes from Juju/Pebble (parsed via `timeconv.parse_rfc3339` which returns aware datetimes). In production (`ops/model.py:539`), a naive datetime is computed and passed to `hookcmds.secret_add` which converts it to RFC3339, potentially losing timezone information. The impact is limited because Juju typically interprets datetimes as UTC, and most systems run in UTC, but on systems with non-UTC timezone this could cause incorrect expiry times.
- **Evidence**:
  ```python
  # ops/model.py:539
  return datetime.datetime.now() + expire  # naive datetime for secret expiry

  # testing/src/scenario/mocking.py:815
  now = datetime.datetime.now()  # used for Pebble Change timestamps

  # ops/_private/harness.py:2866
  rotates = datetime.datetime.now() + datetime.timedelta(days=1)
  ```
- **Recommended fix**:
  ```python
  datetime.datetime.now(tz=datetime.timezone.utc)
  ```
- **Historical precedent**: `8e94a4c9` (operator), `be1fdf06` (operator)

---

### Confirmed Safe

1. **`Plan.to_dict()` filter `if value`** (line 872): This filters top-level sections (services, checks, log-targets) which are dicts. An empty dict is falsy but also means "no entries", so filtering it out is correct behavior -- an empty `services: {}` section should not appear in output.

2. **`Layer.to_dict()` filter `if value`** (line 940): Same reasoning as Plan.to_dict() -- top-level sections where empty means "absent".

3. **`_MockModelBackend.secret_get` return values**: `secret.tracked_content` and `secret.latest_content` are deep-copied in `Secret.__post_init__` via `_deepcopy_mutable_fields`. However, `secret_get` still returns the internal dict reference. But since the Secret dataclass is frozen and the content dicts are the deep-copied versions, the impact is limited to the caller being able to mutate their own copy of the secret's internal state (which could still be problematic if the same Secret object is accessed again). This is borderline but the `_deepcopy_mutable_fields` provides a layer of protection that makes this less severe than it initially appears.

4. **`_MockModelBackend.relation_get` returns `.copy()`** (line 257): This was correctly fixed.

5. **`_MockModelBackend.config_get` copies state config** (line 314): Uses `.copy()` to avoid mutating state.

6. **`_MockModelBackend.is_leader` returns `self._state.leader`**: Returns a `bool` (immutable).

7. **`_MockModelBackend.planned_units` returns `self._state.planned_units`**: Returns an `int` (immutable).

8. **`CheckInfo.from_dict` change_id check `if not change_id`** (line 1511): `change_id` is a `ChangeID(str)` or `None`. An empty string ChangeID is falsy and correctly treated as "no change ID".

9. **`ExecError.__str__` uses `self.command[0]!r`** (line 561): Already fixed to only show executable name, not full arguments.

10. **`action_set` stores `results` directly** (mocking.py:631): `self._context.action_results = results` stores the caller's dict without copy. However, this matches production behavior where `action-set` sends the data to Juju immediately and the in-memory dict is not reused. The `_format_action_result_dict` validation happens on the original dict. Borderline but intentional for "testing ease" per the comment.
