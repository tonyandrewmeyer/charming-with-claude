# data-integrator

**Verdict**: data-integrator is a thin credentials-proxy charm (relates to MySQL,
PostgreSQL, MongoDB, Kafka, ZooKeeper, OpenSearch, Kyuubi, etcd, Cassandra, Valkey;
provides `mongos`) whose own logic is small — most behaviour lives in the vendored
`data_platform_libs` and the `dpcharmlibs` dependency. It is deployable and works for
the happy path (relate → `get-credentials` → correct values), but it has two classes
of critical defect that a maintainer should fix before anything else: (1) several
common misconfigurations (`entity-type=INVALID`, `entity-type`/`extra-*-roles`
mismatches, malformed `entity-permissions`) crash the `config-changed` hook with an
uncaught `ValueError` and leave the unit in `error`, requiring manual `juju resolved`;
(2) the published edge revision (478) fails `upgrade-charm` outright with an
`ImportError` because the bundled `cryptography` wheel is missing its compiled Rust
extension, and the charm has no `_on_upgrade_charm` handler at all, so there is no
defined upgrade path even once that's fixed. Fix the packaging break and wrap/validate
the config-driven `DatabaseRequires` construction first; the rest (stale README,
Kafka topic validator, missing event handlers, typos) is real but secondary.

| | |
|---|---|
| Repo | canonical/data-integrator @ `f46441c` (2026-07-21) |
| Charms | data-integrator (machine), application (test-only) |
| Substrate | machine (also runs as a k8s sidecar on k8s controllers) |
| Deployed | yes — concierge-k8s-3 (rev 476, Juju 3.6.25), concierge-lxd-4 (rev 476, Juju 4.0.12), concierge-k8s-4 (rev 476, Juju 4.0.12); local HEAD is rev `f46441c` (stable) |
| Reviewed | 2026-08-27 |

## What it does

Receives credentials from data-platform provider charms via the `data_interfaces` /
`data_interfaces_v1` relation interface and exposes them through a single
`get-credentials` action (username, password, endpoints, TLS info, etc.), for use by
operators or external applications that cannot speak Juju relations. It enforces
immutability of the core resource identifier (database name, topic, index, keyspace,
prefix) after a relation is established by returning `BlockedStatus` if the config is
changed.

## Deployment log

### LXD (concierge-lxd-4, Juju 4.0.12)
1. `juju add-model rv-data-integrator --controller concierge-lxd-4` ✓
2. `juju deploy data-integrator --channel edge` → rev 476 ✓ (machine container)
3. Machine went `pending → started`; unit `allocating → blocked` ("Please specify
   either topic, index, database name, keyspace name, or prefix") ✓
4. `juju config data-integrator database-name=testdb` → one `config-changed` hook,
   status → "Please relate the data-integrator with the desired product" ✓
5. Tried `postgresql`/`mysql` (require Juju < 4.0.12) and `postgresql-k8s`/`mysql-k8s`
   (require k8s cloud) — **no compatible machine-database charm on this Juju 4.x LXD
   controller**.
6. `juju config data-integrator prefix-name=test-prefix` → `config-changed` fired
   twice (nested hook, no crash — Juju 4.0.12 has secrets, `self.etcd` initialized)

### k8s (concierge-k8s-3, Juju 3.6.25)
1. `juju add-model rv-di-k8s3 --controller concierge-k8s-3` ✓
2. `juju deploy data-integrator --channel edge` → rev 476, k8s sidecar pod ✓
3. `juju deploy mysql-k8s --channel 8.0/edge` → rev 441 ✓; `juju trust mysql-k8s
   --scope=cluster` ✓
4. `juju config data-integrator database-name=testdb` → blocked, "Please relate the
   data-integrator with the desired product" ✓
5. `juju relate data-integrator mysql-k8s` → `mysql-relation-changed` +
   `data-integrator-peers-relation-changed` fired; after ~1 minute `update-status`
   promoted the unit to `active` ✓
6. `juju run data-integrator/leader get-credentials` → valid MySQL credentials ✓
7. `juju config data-integrator topic-name="*"` → blocked, "Please pass an acceptable
   topic value" ✓
8. `juju config data-integrator topic-name=valid-topic` → back to `active` ✓
9. `juju remove-relation data-integrator mysql-k8s` → `mysql-relation-departed` +
   `mysql-relation-broken` + peer-relation-changed fired; unit briefly showed `active`
   then converged to `blocked` within seconds ✓
10. `juju run data-integrator/leader get-credentials` → failed with "The action can be
    run only after relation is created." (correct guard) ✓
11. Re-relate → blocked again, converged to `active` after ~60s via `update-status` ✓
12. `juju config data-integrator database-name=changed-db` (post-relation change) →
    immediately blocked, "To change database name: testdb, please remove relation and
    add it again" ✓ (mismatch detection works)
13. Reverted config → back to `active` ✓
14. `juju scale-application data-integrator 2` → new unit `maintenance → active` in
    ~30s; scaled back to 1 → unit `terminated` ✓
15. `juju deploy opensearch-k8s --channel 2/edge` → went `error` ("hook failed:
    install"), unrelated to data-integrator ✓
16. `juju refresh data-integrator` → "charm already up-to-date" ✓
17. `juju remove-application data-integrator` → clean teardown ✓ (left mysql-k8s and
    opensearch-k8s in model)
18. pydantic `UnsupportedFieldAttributeWarning` in every `get-credentials` output ✓

### k8s (concierge-k8s-4, Juju 4.0.12) — additional integrations
1. `juju deploy data-integrator --channel edge` → rev 476 ✓
2. `juju deploy kafka-k8s --channel 3/edge` → rev 83 ✓; `juju deploy zookeeper-k8s
   --channel 3/edge` ✓; scaled ZooKeeper to 3 units
3. `juju relate kafka-k8s zookeeper-k8s` → kafka-k8s stuck `waiting` ("zookeeper
   credentials not created yet"); ZooKeeper got stuck in `maintenance`. **Kafka
   integration test abandoned** — ZooKeeper charm issue, not data-integrator.

### k8s-3 refresh test (rv-di-fail)
1. `juju refresh data-integrator --revision 478` → downloaded rev 478 (edge, built for
   ubuntu@24.04/s390x per manifest) ✓
2. **Crash**: unit → `error: hook failed: "upgrade-charm"` ✓
3. Debug log: `ImportError: cryptography/hazmat/bindings/_rust.abi3.so: cannot open
   shared object file` — venv's `cryptography 50.0.0` is missing its compiled Rust
   extension ✓
4. Crash path: `dpcharmlibs.interfaces.diff` → `from cryptography.fernet import
   Fernet`, imported at package-init time before any charm code runs
5. **Recovery**: `juju refresh data-integrator --revision 476` → `maintenance →
   active` within ~30 seconds ✓

## Observed behaviour

### Hook firing
- Initial deploy (k8s sidecar): `install` → `peers-relation-created` →
  `leader-elected` → `config-changed` → `start`
- Each `juju config` change fires exactly one `config-changed` hook (except when
  nested — LXD machine container inside a k8s controller fires it twice, once per
  layer, no double-write observed)
- After relating: `mysql-relation-changed` fires twice — once before credentials are
  written (empty/partial diff), once after; `database_created` fires on the second
- `update-status` fires periodically (~5 min default)
- `relation-broken` → writes peer databag → `peer-relation-changed` fires →
  `_on_peer_relation_changed` → `get_status()` → status converges

### Status transitions

| State | Trigger |
|---|---|
| `blocked` — "Please specify either topic, index..." | No core config set |
| `blocked` — "Please relate the data-integrator with..." | Core config set, no relation |
| `blocked` — "Please pass an acceptable topic value" | `topic-name` contains `*` in first 3 chars |
| `blocked` — "To change X: Y, please remove relation..." | Config changed after relation established |
| `blocked` — "To change role info, please remove relation..." | `entity-type`/`extra-*` changed after relation |
| `active` | All required config set + credentials present |
| `active` (transient) | Briefly after `relation-broken`, before `_on_peer_relation_changed` runs |

### Timing
- Machine container creation on LXD: ~2–3 min to `blocked`
- k8s pod creation + agent init: ~2 min
- MySQL relation credential propagation: ~30–60s before `active` on initial deploy;
  ~60s on re-relation after removal
- Scale-up (k8s): ~30s from `maintenance` to `active`
- `get-credentials` action: < 5s
- Status convergence after `relation-broken`: ~5s via `_on_peer_relation_changed`

### Workload container
Machine charm running as a k8s sidecar; the "workload" is the charm agent itself.
Pebble (PID 1) manages the `container-agent` process; there is no separate
application container.

### Failure injection

- **`entity-type=INVALID`** (LXD, Juju 4.0.12): unit → `error: hook failed:
  "config-changed"`; debug log `ValueError: Invalid entity-type. Possible values are
  USER and GROUP`. Recovery: set `entity-type=USER` + `juju resolved`.
- **`entity-type=USER` + `extra-group-roles`**: same crash mode,
  `ValueError: Inconsistent entity information. Use extra_user_roles instead`.
- **`entity-type=GROUP` + `extra-user-roles`**: inverse crash,
  `ValueError: Inconsistent entity information. Use extra_group_roles instead`.
- **`entity-permissions={invalid json}`**: `error: hook failed: "config-changed"`,
  `ValueError: Invalid entity permissions format. It must be JSON format`.
- **`topic-name=foo*` / `topic-name=bar*`** (both LXD and k8s): accepted by charm
  validation (no `*` in first 3 characters); charm goes `blocked: Please relate the
  data-integrator with the desired product`. Would write an invalid topic to the
  databag and be rejected by Kafka if a relation existed.
- **`requested-entities-secret=secret:notexist`**: correctly `blocked: Unable to
  access requested-entities-secret`. Secret revocation after grant: no crash
  (provider creates its own secret).
- **Config mismatch after relation** (`database-name=changed-db`): immediate
  `blocked` within the same hook — no delay, unlike relation establishment.
- **Scale up/down (k8s)**: `scale-application 2` → second unit `maintenance → active`
  in ~30s; scale to 1 → unit terminated cleanly.
- **Relation removal (k8s)**: unit went `blocked` within seconds (transient `active`
  observed on one run, not on another — see finding below); `get-credentials`
  correctly fails with "The action can be run only after relation is created."
- **pydantic warnings**: two `UnsupportedFieldAttributeWarning` lines on every
  `juju run get-credentials` call. Source: pydantic 2.13.4 in the charm venv +
  `dpcharmlibs` models using `Field(default=None)` on Optional fields and
  `exclude=True` on a property.
- **Process kill (k8s)**: killing the `container-agent` PID inside the pod caused an
  immediate pod restart via Pebble; unit back to `active` within ~7 seconds. Correct
  behaviour (`on-failure: shutdown` policy).
- **Non-leader `get-credentials` (k8s, scale 3)**: returned identical credentials to
  the leader — correct, since `get-credentials` reads the shared relation databag,
  not unit-local state.
- **Scale to 3 / back to 1 (k8s)**: all units reached `active` within ~30s each; scale
  down terminated cleanly.
- **`entity-type=INVALID` baked in at initial deploy (unverified)**: draft notes state
  that if invalid config is present from the start, the unit goes to `error` during
  the *first* `config-changed` and needs manual `juju resolved`, with no warning
  before the crash. Not independently re-confirmed in the notes as a distinct run —
  `(unverified)`.
- **grafana-agent-k8s integration attempt**: `juju relate data-integrator
  grafana-agent-k8s` → `ERROR: no relations found`. Correct: `metadata.yaml` has no
  `metrics`/`logging`/`tracing`/`dashboards` relation; data-integrator exposes only
  liveness/readiness HTTP probes (port 65301), no `/metrics` endpoint.
  `grafana-agent-k8s` itself went `blocked` for missing its own required relations —
  unrelated to data-integrator.
- **No compatible data charm on Juju 4.x LXD**: `postgresql`/`mysql` stable channels
  need Juju < 4.0.12; `postgresql-k8s`/`mysql-k8s` need a k8s cloud. data-integrator
  on LXD cannot currently be relation-tested against any charmhub data charm on a
  Juju 4.x controller. Ecosystem gap, not a charm bug.

## Findings

### `upgrade-charm` hook fails with `ImportError` on published rev 478 (broken cryptography wheel)

- **Severity**: critical
- **Kind**: bug
- **Where**: `deps/dpcharmlibs/interfaces/__init__.py` → `deps/dpcharmlibs/interfaces/diff.py:20` (`from cryptography.fernet import Fernet`)
- **Evidence**: `juju refresh data-integrator --revision 478` on concierge-k8s-3
  (Juju 3.6) put the unit in `error: hook failed: "upgrade-charm"`. Debug log:
  `ImportError: .../cryptography/hazmat/bindings/_rust.abi3.so: cannot open shared
  object file`. Rev 478's manifest shows it was built for ubuntu@24.04/s390x; the
  venv contains `cryptography 50.0.0` (poetry.lock pins 49.0.0) with its compiled Rust
  extension missing. Crash path: `charm.py` → `dpcharmlibs.interfaces` →
  `diff.py` → `cryptography.fernet` → `_rust.abi3.so` missing → hook exits 1 → unit
  `error`. Recovery: `juju refresh --revision 476` → `maintenance → active` in ~30s.
- **Impact**: any operator refreshing to the latest edge revision bricks their
  data-integrator deployment until manually downgraded — a packaging/build failure
  that CI should have caught.
- **Fix**: fix the charmcraft build so `cryptography`'s Rust extension is correctly
  bundled; add a CI smoke test that imports `dpcharmlibs.interfaces.diff.Diff` in an
  isolated venv; or pin `cryptography<50` to avoid the Rust build requirement.
- **Linter rule**: none mechanical; a unit test importing the charm module in a clean
  venv would catch this.

---

### Invalid `entity-type` config crashes `config-changed` with uncaught `ValueError`

- **Severity**: critical
- **Kind**: bug
- **Where**: `src/charm.py:72–84` (`_setup_database_requirer`) via `DatabaseRequires` at `lib/charms/data_platform_libs/v0/data_interfaces.py:2107`
- **Evidence**: on concierge-lxd-4 (Juju 4.0.12), `juju config data-integrator
  entity-type=INVALID` → `error: hook failed: "config-changed"`; debug log
  `ValueError: Invalid entity-type. Possible values are USER and GROUP`. Same crash
  mode confirmed for `entity-permissions={invalid json}` (`ValueError: Invalid entity
  permissions format. It must be JSON format`). The exception is raised inside
  `DatabaseRequires.__init__`'s `_validate_entity_type`/`_validate_entity_permissions`
  and propagates through the `_setup_database_requirer` dict comprehension
  uncaught. Recovery requires a valid config value plus `juju resolved`.
- **Impact**: any operator who mistypes `entity-type` or `entity-permissions` crashes
  the charm's `config-changed` hook and needs manual intervention to recover.
- **Fix**: validate `entity-type`/`entity-permissions` before constructing
  `DatabaseRequires`, or wrap the construction in try/except and set
  `BlockedStatus` instead of letting the hook crash.
- **Linter rule**: none mechanical; the library should validate inputs before
  raising from a constructor called at charm-init time.

---

### `entity-type`/`extra-*-roles` mismatches crash the same way

- **Severity**: high
- **Kind**: bug
- **Where**: `lib/charms/data_platform_libs/v0/data_interfaces.py:2144` (`_validate_entity_type`)
- **Evidence**: `entity-type=USER extra-group-roles=custom` → `error: hook failed:
  "config-changed"`, `ValueError: Inconsistent entity information. Use
  extra_user_roles instead`. `entity-type=GROUP extra-user-roles=admin` → inverse
  crash, `ValueError: Inconsistent entity information. Use extra_group_roles
  instead`. Both confirmed on concierge-lxd-4.
- **Impact**: config options that appear combinable actually crash the hook when
  combined incorrectly; the error message also tells the operator to use the option
  they already avoided, which is confusing.
- **Fix**: same as the `entity-type=INVALID` finding — pre-validate before
  constructing `DatabaseRequires`, or catch in `_on_config_changed`.
- **Linter rule**: none mechanical.

---

### No `_on_upgrade_charm` handler — no upgrade path exists

- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py` (absent)
- **Evidence**: `grep -n "on_upgrade_charm\|_on_upgrade_charm" src/charm.py
  lib/charms/data_platform_libs/v0/data_interfaces.py` returns nothing. The charm
  does not observe `self.on.upgrade_charm`.
- **Impact**: even once the rev 478 packaging break is fixed, there is no defined
  behaviour for `upgrade-charm`. Any future need for relation-data migration or
  secret rotation across charm versions has nowhere to hook in; an operator who
  refreshes gets the new code but no migration runs.
- **Fix**: add an `_on_upgrade_charm` handler, e.g.:
  ```python
  self.framework.observe(self.on.upgrade_charm, self._on_upgrade_charm)

  def _on_upgrade_charm(self, event) -> None:
      self.unit.status = self.get_status()
      if self.unit.is_leader():
          self._on_config_changed(event)
  ```
- **Linter rule**: a test asserting every `self.on` event has at least one observer
  would catch this; `charmcraft analyse` may help.

---

### README omits five of ten supported relations

- **Severity**: high
- **Kind**: docs
- **Where**: `README.md:241–250`
- **Evidence**: the Relations section documents only `mongodb_client`,
  `mysql_client`, `postgresql_client`, `kafka_client`, `opensearch_client`. The charm
  supports ten interfaces per `metadata.yaml`/`literals.py`: mysql, postgresql,
  mongodb, kafka, zookeeper, opensearch, kyuubi, etcd, cassandra, valkey, plus the
  provided `mongos` interface. Cassandra, valkey, kyuubi, and zookeeper are entirely
  absent from the docs; `mongos` is not mentioned at all.
- **Impact**: an operator reading the README will not know Cassandra, Valkey,
  Kyuubi, ZooKeeper, or the mongos subordinate are supported.
- **Fix**: list all ten interfaces in the Relations section, add cassandra/valkey to
  the product table, add kyuubi/zookeeper to the overview, and document `mongos`.
- **Linter rule**: none mechanical; a test comparing `metadata.yaml` requires against
  README content would be fragile.

---

### Crash in `_on_config_changed_prefix` when etcd is not initialized (Juju without secrets)

- **Severity**: high
- **Kind**: bug
- **Where**: `src/charm.py:363–364` (guard), `src/charm.py:434` (crash), `src/charm.py:706` (`etcd_relation`)
- **Evidence**: `etcd_relation` (line 706) safely returns `None` when
  `has_secrets` is `False`, so `prefix_active` (line 761) falls through to valkey.
  But the guard at line 364 —
  `if self.prefix and (not self.prefix_active or self.mtls_client_cert):` — passes
  whenever `prefix_active` is `None`, regardless of `has_secrets`. That calls
  `_on_config_changed_prefix()`, which at line 434 does `for rel in
  self.etcd.relations:` — `AttributeError: 'NoneType' object has no attribute
  'relations'`, because `self.etcd` is only created when `has_secrets` is `True`
  (line 177). Triggers require: Juju pre-3.0 (no secrets), `prefix-name` set, and
  no etcd or valkey relation.
- **Impact**: Juju 2.9.x has no secrets support. The charm targets Ubuntu 22.04/24.04
  bases, which typically pair with Juju 3.x+, but no `min-juju-version` is declared,
  so a deployment on an old 2.9.x controller with a `prefix-name` set and no etcd/
  valkey relation crashes `config-changed` on every fire.
- **Fix**: add the `has_secrets` check to the guard:
  ```python
  if self.prefix and self.model.juju_version.has_secrets \
     and (not self.prefix_active or self.mtls_client_cert):
      self._on_config_changed_prefix()
  ```
- **Linter rule**: none mechanical; would need taint analysis to flag that a
  conditionally-created attribute may be `None` at a call site the guard doesn't
  cover.

---

### `is_topic_value_acceptable` only checks the first 3 characters of a Kafka topic name

- **Severity**: medium
- **Kind**: bug
- **Where**: `deps/dpcharmlibs/interfaces/models.py:507–512`; used at `src/charm.py:301`
- **Evidence**:
  ```python
  def is_topic_value_acceptable(value: str | None) -> str | None:
      if value and '*' in value[:3]:
          raise ValueError(...)
      return value
  ```
  Confirmed on both concierge-lxd-4 and concierge-k8s-3: `topic-name=foo*` and
  `topic-name=bar*` pass validation (no `*` in the first 3 characters) and the charm
  goes `blocked: Please relate the data-integrator with the desired product`.
- **Impact**: values that pass the charm's own check would still be rejected by
  Kafka if a relation existed, producing a confusing relation-shaped error for what
  is actually a topic-name problem.
- **Fix**: check for `*` anywhere in the value: `if value and '*' in value:`.
- **Linter rule**: none mechanical without encoding Kafka's naming rules.

---

### `authentication_updated` event from Cassandra/Valkey not handled

- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py` (absent); emitted at `deps/dpcharmlibs/interfaces/handlers.py:1243–1248`
- **Evidence**: `ResourceRequirerEventHandler._handle_event` emits
  `authentication_updated` when `secret-tls` is added/changed in relation data. The
  charm does not observe `self.cassandra.on.authentication_updated` or
  `self.valkey.on.authentication_updated`.
- **Impact**: a TLS certificate rotation by a Cassandra/Valkey provider goes
  unnoticed until the next `update-status`; a `get-credentials` call during that
  window returns a stale/revoked certificate.
- **Fix**: observe both events and route to `_on_config_changed` or an equivalent
  status refresh.
- **Linter rule**: none mechanical.

---

### Missing `endpoints_changed` / `read_only_endpoints_changed` handlers for Cassandra and Valkey

- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:204–217` (only `resource_created`/`resource_entity_created` handled)
- **Evidence**: `ResourceRequirerEventHandler` emits four events —
  `resource_created`, `resource_entity_created`, `endpoints_changed`,
  `read_only_endpoints_changed` — of which the charm only handles the first two.
  Confirmed on k8s that `get-credentials` reads the relation databag directly at
  action time, so it would return stale endpoints if a provider changed them and no
  hook fired since.
- **Impact**: a Cassandra/Valkey failover or scaling event that changes endpoints is
  not surfaced until the next `relation-changed`/`update-status`.
- **Fix**: observe `cassandra.on.endpoints_changed`/`valkey.on.endpoints_changed`
  (and the read-only variants) and route to the existing resource-created handler.
- **Linter rule**: none mechanical; would require cross-referencing library event
  definitions against observed handlers.

---

### `mongos` in `DATABASES` but not declared as a `requires` relation

- **Severity**: medium
- **Kind**: bug
- **Where**: `src/literals.py:11,19`; `metadata.yaml:21–54`
- **Evidence**: `literals.py:19` — `DATABASES = [MYSQL, MONGODB, POSTGRESQL, MONGOS,
  ZOOKEEPER, KYUUBI]`; `src/charm.py:107` creates a `DatabaseRequires` for every
  entry. `metadata.yaml` declares `mongos` only under `provides:`, not `requires:`,
  so Juju never assigns it a relation ID. No tests reference `mongos`.
- **Impact**: the `DatabaseRequires` created for `mongos` is dead code; an operator
  attempting to relate to a `mongos` provider cannot, because Juju doesn't offer the
  relation.
- **Fix**: either add `mongos` to `metadata.yaml requires:` (interface
  `mongos_client`), or remove it from `DATABASES`.
- **Linter rule**: a test comparing `metadata.yaml requires` keys against
  `literals.DATABASES` would catch this.

---

### Transient `active` status for ~5 seconds after `relation-broken`

- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:218–221` (`_on_relation_broken`); `src/charm.py:589–606` (`_on_peer_relation_changed`)
- **Evidence**: after `juju remove-relation data-integrator mysql-k8s`, the unit
  briefly showed `active` before `_on_peer_relation_changed` fired (via peer databag
  write) and called `get_status()`, converging to `blocked` within ~5 seconds. A
  later run of the same removal did not reproduce the transient state — the race
  window is narrow. Mechanism: `_on_relation_broken` writes `BROKEN` to the peer
  databag (line 583–585), which triggers `peer-relation-changed`, which updates
  status (line 601); there is a gap between those two steps.
- **Impact**: an observer of `juju status` during the gap sees a misleading `active`
  when the unit should be `blocked`; on multi-unit deployments non-leader units could
  show this longer.
- **Fix**: set status directly in `_on_relation_broken` before/alongside the peer
  databag write:
  ```python
  def _on_relation_broken(self, event) -> None:
      self.unit.status = self.get_status()
      self._update_relation_status(event.relation, Statuses.BROKEN.name)
  ```
- **Linter rule**: none mechanical.

---

### MySQL relation data doesn't surface TLS credentials as top-level fields

- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:522–524` (`_on_get_credentials_action`)
- **Evidence**: `juju show-unit data-integrator/0` for the MySQL relation shows
  `database`, `endpoints`, `read-only-endpoints`, `version`, `secret-user` — no
  `tls-ca`/`tls-cert` at the top level. TLS material is embedded in the `data`
  JSON field's `requested-secrets` array (`["tls", "tls-ca", ...]`), not as named
  values. `get-credentials` returns the relation data as-is.
- **Impact**: an operator using `get-credentials` to configure downstream TLS will
  not find `tls-ca` as a top-level field; the README's description of the credential
  structure doesn't mention this nesting.
- **Fix**: extract `tls-ca` from the embedded `data` JSON and surface it as a
  top-level field, or document the nesting clearly in the README.
- **Linter rule**: none mechanical.

---

### `dpcharmlibs.interfaces` imports `cryptography` at package-init time — hard, avoidable dependency

- **Severity**: medium
- **Kind**: bug
- **Where**: `deps/dpcharmlibs/interfaces/__init__.py` → `deps/dpcharmlibs/interfaces/diff.py:20`
- **Evidence**: `__init__.py` unconditionally imports from `diff.py`, which
  unconditionally imports `cryptography.fernet.Fernet`. `Fernet` is used only inside
  `diff.py`, `handlers.py`, and `repository_interfaces.py` for internal
  library encryption — it is never used by the charm's own source. This is exactly
  the import chain that broke in rev 478.
- **Impact**: any `cryptography` packaging problem crashes every hook via this import,
  even though the charm's functionality (proxying credentials) has no need for
  encryption.
- **Fix**: move the `cryptography.fernet` import inside the functions that use it
  (lazy import) instead of at module level.
- **Linter rule**: `ruff check deps/dpcharmlibs/` currently reports 11 errors; a rule
  flagging top-level `cryptography` imports in library packages would catch this
  specific case.

---

### README Tutorial uses stale revision numbers and an old Juju version

- **Severity**: medium
- **Kind**: docs
- **Where**: `README.md:159–220`
- **Evidence**: tutorial output shows `data-integrator rev 79` and `mongodb rev 99`,
  and example `juju status` output referencing Juju 2.9.34.
- **Impact**: new operators following the tutorial see revision numbers and a Juju
  version far from current, which is confusing.
- **Fix**: use generic placeholders (`NNN`) instead of hardcoded revisions, and
  update the Juju version in example output.
- **Linter rule**: none mechanical.

---

### Wrong-status gap (~60s) after initial relation establishment

- **Severity**: medium
- **Kind**: ux
- **Where**: interaction between `_on_config_changed`/`database_created` and `update-status`
- **Evidence**: after `juju relate data-integrator mysql-k8s`, the unit stayed
  `blocked` for ~60 seconds before `update-status` promoted it to `active`. The
  `database_created` event (confirmed to fire synchronously during
  `relation-changed` at `lib/charms/data_platform_libs/v0/data_interfaces.py:3914`)
  fires on the second `relation-changed`, once the provider has written credentials.
  On re-relation the delay was also ~60s, suggesting the provider (mysql-k8s) takes
  time to reprovision credentials rather than the charm being slow to react.
- **Impact**: operators see a misleading `blocked` status for up to a minute after a
  relation that is, in fact, healthy and progressing normally.
- **Fix**: document the expected delay in the README, or add a `relation-changed`
  observer that calls `get_status()` immediately to narrow the gap.
- **Linter rule**: none mechanical.

---

### `deps/dpcharmlibs` has 11 ruff violations

- **Severity**: low
- **Kind**: lint
- **Where**: `deps/dpcharmlibs/interfaces/` (multiple files)
- **Evidence**: `ruff check deps/dpcharmlibs/` reports: `unsorted-imports` in
  `diff.py`, `events.py`, `handlers.py`, `models.py`, `repository.py`,
  `repository_interfaces.py`, `secrets.py` (7); `complex-structure` in
  `handlers.py:509` (`_on_secret_changed_event`, McCabe 11), `handlers.py:1086`
  (`_on_relation_changed_event`, McCabe 13), `models.py:235` (`serialize_model`,
  McCabe 15) (3); `missing-copyright-notice` and `invalid-module-name` in
  `TCLIService/TCLIService.py` (1 each).
- **Impact**: `deps/` is checked-in dependency code in scope for this review; its
  lint failures are a quality gap.
- **Fix**: `ruff check --fix deps/` for import ordering; reduce complexity in the
  three flagged methods; add a copyright header to `TCLIService.py`.
- **Linter rule**: `ruff check deps/` currently fails with 11 errors.

---

### pydantic warning printed on every `get-credentials` call

- **Severity**: low
- **Kind**: bug
- **Where**: `deps/dpcharmlibs/interfaces/models.py:356–434, 443`
- **Evidence**: every `juju run get-credentials` emits two
  `UnsupportedFieldAttributeWarning` lines from pydantic 2.13.4 — one for
  `Field(default=None)` on 40+ Optional fields (a no-op in modern pydantic since
  Optional already defaults to `None`), one for `exclude=True` on the
  `original_field` property.
- **Impact**: pollutes action output, making it harder to parse credentials
  programmatically; surfaces as stderr noise to operators.
- **Fix**: remove redundant `default=None` from `Field()` calls on Optional fields
  in `dpcharmlibs`, or suppress/upgrade to avoid the warning.
- **Linter rule**: `ruff check deps/dpcharmlibs/` with pydantic plugin rules enabled
  would catch this; otherwise not checkable from the charm side.

---

### `lib/charms/data_platform_libs/v0/data_interfaces.py` has ruff format violations and shadows the pip package

- **Severity**: low
- **Kind**: lint
- **Where**: `lib/charms/data_platform_libs/v0/data_interfaces.py`
- **Evidence**: `ruff format --check lib/` fails (vendored copy would be
  reformatted); `ruff check lib/` reports `complex-structure` in two
  `_on_relation_*` methods (McCabe > 10); test runs show `DeprecationWarning:
  JujuVersion.from_environ() is deprecated, use self.model.juju_version instead`.
  The charm also declares the library as a poetry dependency in `pyproject.toml`,
  so the local `lib/` copy shadows the pip-installed version at import time.
- **Impact**: two copies of the same library exist; it's unclear which one is
  actually exercised at runtime, and the vendored copy carries its own lint and
  deprecation debt.
- **Fix**: remove `lib/charms/data_platform_libs/` and rely solely on the
  pip-installed dependency already declared in `pyproject.toml`.
- **Linter rule**: `ruff format --check lib/` currently fails.

---

### Typo: `cassandra_entity_permisions` should be `cassandra_entity_permissions`

- **Severity**: low
- **Kind**: lint
- **Where**: `src/charm.py:119` (usage), `src/charm.py:885` (definition)
- **Evidence**:
  ```python
  entity_permissions=self.cassandra_entity_permisions,   # line 119
  def cassandra_entity_permisions(self) -> list[EntityPermissionModel]:  # line 885
  ```
- **Impact**: purely cosmetic — the misspelling is used consistently so there's no
  runtime error — but confusing for anyone reading or extending the code. Codespell
  doesn't catch it because it only checks comments/strings, not identifiers.
- **Fix**: rename to `cassandra_entity_permissions` throughout.
- **Linter rule**: `codespell --check-identifiers` or a custom identifier rule.

---

### `requested_entities_secret_content` only returns the first key from a multi-entry secret

- **Severity**: low
- **Kind**: bug
- **Where**: `src/charm.py:649–659`
- **Evidence**:
  ```python
  content = secret.get_content(refresh=True)
  for key, val in content.items():
      return key, None if val == "None" else val
  ```
  Only the first entry (arbitrary dict order) is used.
- **Impact**: if an operator populates the secret with multiple entries, behaviour
  is silently incorrect for anything beyond the first.
- **Fix**: assert a single entry, or return a mapping if multiple entries are
  intended, and document the assumption.
- **Linter rule**: none mechanical.

---

### Typo: `_check_missmatch` should be `_check_mismatch`

- **Severity**: nit
- **Kind**: lint
- **Where**: `src/charm.py:251`
- **Evidence**: `def _check_missmatch(self) -> StatusBase:`
- **Impact**: cosmetic; the function works correctly.
- **Fix**: rename to `_check_mismatch`.
- **Linter rule**: none mechanical without a custom rule.

---

### `get-credentials` correctly guards against missing relations

- **Severity**: info (correct behaviour)
- **Kind**: good-practice
- **Where**: `src/charm.py:491–525`
- **Evidence**: run without an active relation, the action fails with "The action
  can be run only after relation is created." (`ok: false`). The action checks
  `is_database_related`/`is_kafka_related`/`is_opensearch_related`/
  `is_etcd_related`/`is_cassandra_related`/`is_valkey_related` before touching
  relation data.
- **Fix**: none needed.
- **Linter rule**: not applicable.

---

### Config-mismatch enforcement fires immediately (correct, not a bug)

- **Severity**: info (correct behaviour)
- **Kind**: good-practice
- **Where**: `src/charm.py:346–355` (`_on_config_changed` guards); `_check_missmatch()` at `src/charm.py:251`
- **Evidence**: after establishing a relation, `juju config database-name=changed-db`
  immediately (within the same `config-changed` hook) sets `BlockedStatus` with "To
  change database name: testdb, please remove relation and add it again."
- **Fix**: none needed.
- **Linter rule**: not applicable.

## Worth copying

- **Clean status precedence in `get_status()`** (`src/charm.py:299–340`) — an
  ordered chain of guard clauses returning early with `BlockedStatus` per problem
  class (secret → no config → bad config → no relation → mismatch → active). Easy to
  read and extend, better than nested conditionals.
- **Peer-databag reconciliation** (`src/charm.py:220–236`) — writing relation status
  to the peer databag via `_update_relation_status` and reacting in
  `_on_peer_relation_changed` is a solid leader-based cleanup pattern that avoids
  races (modulo the transient-status gap noted above).
- **Property-based config accessors** (`src/charm.py:607–700`) — every config option
  has a dedicated `@property`, abstracting `model.config.get()` and making the code
  readable and easy to extend.
- **`_changes_role_info()` short-circuit guards** (`src/charm.py:222–233`) — caching
  active values before comparison avoids repeated databag reads, and the
  `active_type and active_type != self.entity_type` guard avoids a `None != value`
  false positive.
- **Config-change guards in `_on_config_changed`** (`src/charm.py:346–355`) — only
  calls `update_relation_data` when the new value would actually change the
  databag, avoiding unnecessary writes.

## Common-practice notes

**Better than average:**
- Proper reconciler pattern for status (`get_status()`) instead of ad-hoc
  `set-status` calls scattered through handlers
- Comprehensive per-relation integration test coverage, one spread test per
  relation type
- Follows the `lib/charms/<name>/v<N>/` convention for charm libraries
- Poetry for dependency management, well-structured CI (`ci.yaml`,
  `integration_test.yaml`, `lib-check.yaml`, `release.yaml`)
- `make_secret`/`get_secret` abstraction over the peer databag is cleaner than raw
  `relation.data[self.app]` access
- Status precedence is well-ordered (most critical first)
- `get-credentials` correctly guards against every missing-relation case

**Drifts from convention / worse than average here:**
- Vendored `lib/charms/data_platform_libs/` shadows the pip-installed version at
  import time
- Dual test infrastructure (`spread.yaml` vs `tox -e integration` + pytest-operator)
  — bugs can slip through one framework and not the other
- No scenario/state-transition tests; unit test coverage is thin (5 tests, 61%
  line coverage of `src/charm.py`)
- No resources declared in metadata (could use resources for TLS certs)
- No `_on_upgrade_charm` handler — upgrade path is undefined
- `deps/dpcharmlibs/` has no version pin visible from the charm side, unclear which
  version is actually bundled versus what's checked into source
- `actions.yaml` only defines `get-credentials` — no credential-rotation or
  relation-health action
- No `min-juju-version` declared, despite code paths that behave differently on
  pre-3.0 Juju

## Tests

### Unit tests (`tests/unit/test_charm.py`)

5 tests, all pass in 0.15s (`PYTHONPATH=src:lib pytest tests/unit/test_charm.py -v`
→ 5 passed, 11 warnings). Coverage 61% of `src/charm.py`, 129 missing statements.

Covered: `test_on_start`, `test_action_failures`, `test_config_changed`,
`test_get_unit_status`, `test_relation_created`.

Not covered (confirmed via `pytest --cov`):
- `_on_update_status` (line 344) — the path that promotes the unit to `active`
- `_changes_role_info` (223), `_check_missmatch` (251)
- `is_kafka_related`/`is_opensearch_related`/`is_etcd_related`/
  `is_cassandra_related`/`is_valkey_related` individually
- `entity_type_active`, `entity_permissions_active`, `extra_user_roles_active`,
  `extra_group_roles_active`
- `mtls_client_cert` (base64/PEM path)
- `requested_entities_secret_content`
- `_on_config_changed_prefix` (429) and the `prefix_active` valkey fallback
- Leader vs. non-leader `set_secret` behaviour
- **Invalid config validation**: no unit tests for `entity-type=INVALID`,
  `entity-permissions={invalid json}`, or the `entity-type`/`extra-*-roles`
  mismatches — all of which crash the hook; tests would have caught this
- Config mismatch after relation established
- `_on_relation_broken` → `_update_relation_status` → `_on_peer_relation_changed`
  chain
- `cassandra_entity_permisions` (typo property)
- `get_status()` happy path (`ActiveStatus`) — only exercised in integration tests
- `_on_resource_created`/`_on_resource_entity_created` (Cassandra/Valkey)
- `_on_topic_created`, `_on_index_created`, `_on_entity_created`
- `etcd_relation` on Juju without secrets; `is_etcd_related`

### Integration tests (`tests/integration/`)

Per-relation files for all ten types (mysql, postgresql, mongodb, kafka,
zookeeper, opensearch, kyuubi, etcd, cassandra, valkey). Each: deploys
data-integrator + app charm + provider, configures + relates + waits for
`active`, calls `get-credentials`, performs a real operation via the app charm,
removes and re-adds the relation and verifies new credentials.

Notes:
- `test_kafka.py::test_topic_setting` only tests the `topic-name=*` (first-3-chars)
  case, not `foo*`
- `test_etcd.py` covers `mtls-cert`; `test_valkey.py` covers `prefix-name`;
  `test_cassandra.py` covers `keyspace-name` + `extra-user-roles`; `test_kyuubi.py`
  is k8s-only (`only_on_k8s` marker)
- Cassandra, OpenSearch, Kafka, ZooKeeper, Kyuubi have Juju 2.9 exclusion variants

Not covered:
- `entity-type=INVALID`, `entity-permissions={invalid json}`, or entity-type/
  extra-roles mismatches — all of which crash the hook
- `endpoints_changed`/`read_only_endpoints_changed`/`authentication_updated`
  (Cassandra/Valkey)
- `juju refresh`/`upgrade-charm` (no handler exists at all)
- Config changes while a relation is live (only remove/re-add is tested)
- `requested-entities-secret` config option
- `_on_update_status`

Not run during this review — would require a full k8s environment with providers
and a longer time budget.

### Spread tests (`tests/spread/`)
Thin shims running the corresponding `tests/integration/` files via tox, on both
`lxd-vm` and `github-ci` backends. `test_valkey/` has its own `task.yaml`; others
are `.py` files with inline `task.yaml`. Not run during this review.

### Lint
- `ruff check src/` — passes
- `ruff format --check src/` — passes
- `codespell src/ lib/` — passes
- `ruff check lib/` — 2 `complex-structure` errors in `data_interfaces.py` (library)
- `ruff format --check lib/` — fails (4 style differences, library only)
- `PYTHONPATH=src:lib pytest tests/unit/test_charm.py -v` — 5 passed, 11 warnings
- `pytest --cov=src --cov-report=term-missing` — 61% coverage, 129 missing statements

## Docs

**README.md** (12,407 bytes) — generally well-written: config-option table per
product, a full MongoDB tutorial, clear usage examples. Deficiencies:
- Omits Cassandra, Valkey, Kyuubi, ZooKeeper from the product table; `mongos` not
  mentioned at all
- Tutorial uses stale revision numbers and an old Juju version
- No troubleshooting section for common blocked states
- No example `get-credentials` output covering all supported products
- No note about the ~60s `update-status` delay after relation establishment
- No warning about invalid `entity-type`/`entity-permissions` crashing the hook

**CONTRIBUTING.md** (2,725 bytes) — adequate: `tox` workflow, build commands,
contributor agreement.

**Charmhub description** — matches `metadata.yaml`, sufficient.

**Terraform module** (`terraform/charm/data_integrator/`) — `main.tf`,
`outputs.tf`, `variables.tf` present; not reviewed in detail, but its existence is
notable and welcome.

## Open questions

1. Why does status only converge via `update-status` (~60s) after a relation is
   established, when `database_created` fires synchronously during
   `relation-changed`? Evidence points to the provider (mysql-k8s) taking time to
   provision credentials, but this hasn't been independently confirmed against the
   mysql-k8s codebase.
2. Should `lib/charms/data_platform_libs/` be removed from the repo in favour of the
   pip-installed dependency already declared in `pyproject.toml`?
3. What is the intended behaviour of `requested_entities_secret_content` for
   secrets with multiple entries? The code silently uses only the first.
4. Should `data_platform_libs`' `DatabaseRequires.__init__` return a validation
   error instead of raising, so charms can convert it to `BlockedStatus` without
   wrapping the constructor themselves?
5. Was `is_topic_value_acceptable`'s first-three-characters check intentional (e.g.,
   to allow `*` for namespacing later in the string), or a bug? Kafka itself doesn't
   support `*` in topic names at all, so the narrower check seems unintentional.
6. Should `mongos` be removed from `DATABASES` or added to `metadata.yaml
   requires:`? Currently it is neither usable nor absent.
7. Should the charm react to `endpoints_changed`/`read_only_endpoints_changed` from
   Cassandra/Valkey by re-reading the databag immediately, rather than waiting for
   the next hook?
8. Why does rev 478's bundled `cryptography` lack its compiled Rust extension —
   was the build environment properly isolated, given the venv shows 50.0.0 against
   a 49.0.0 pin in `poetry.lock`?
9. Should `dpcharmlibs.interfaces` lazy-import `cryptography.fernet`, since it's
   used only internally by the library and never by the charm itself?
