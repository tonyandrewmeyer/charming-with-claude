# penpot-operator review — working notes

## Setup
- Repo: /home/ubuntu/charm-review/work/penpot-operator/repo
- Commit: 85243e0 @ 2026-07-21
- Local HEAD: 85243e0 (no delta from charmhub rev 80)

## Phase 1 — Orientation
- Single charm: `penpot` (k8s)
- charmcraft.yaml: base ubuntu@24.04, juju >= 3.4, uses ops 3.7.0
- Holistic reconciliation pattern — single `_reconcile` triggered by 20+ events
- Pytest test invocation broken without PYTHONPATH=.:lib

## Phase 2 — Deployment attempts

### concierge-k8s-4 (Juju 4.0.12) — RBAC failure
All charms including penpot failed on the first attempt:
```
hook "penpot_peer-relation-created" failed: saving content for secret "...": 
attempt count exceeded: secrets "...-1" is forbidden: 
User "system:serviceaccount:rv-penpot-1:juju-secret-consumer-..." 
cannot patch resource "secrets" in API group "" in the namespace "rv-penpot-1"
```
This is an RBAC issue in the cluster, not a charm bug. Multiple charms affected.
The juju-secret-consumer service accounts lack `patch` on secrets in the namespace.
Confirmed: `kubectl auth can-i patch secrets --as=system:serviceaccount:...` → "no"

### concierge-k8s-3 (Juju 3.6.25) — partial success
Model: rv-penpot-3

#### postgresql-k8s wrong revision
- `latest/stable` = rev 20 → provides `pgsql` interface (NOT `postgresql_client`)
- penpot requires `postgresql_client` interface
- `juju relate penpot:postgresql postgresql-k8s:database` → ERROR: no relations found
- Confirmed by reading charm metadata from the operator pod:
  `/var/lib/juju/agents/unit-postgresql-k8s-0/charm/metadata.yaml`
  ```
  provides:
    db: interface: pgsql
    db-admin: interface: pgsql
  ```
- Removed postgresql-k8s, redeployed with `--channel 14/stable --revision 774`
- Correct revision: provides `database` endpoint with `postgresql_client` interface
- `juju integrate penpot:postgresql postgresql-k8s:database` → success

#### traefik-k8s failure
- Cluster has no LoadBalancer provisioner
- traefik-k8s tries to create `traefik-k8s-lb` service → fails
- traefik-k8s RBAC issue: `User "system:serviceaccount:rv-penpot-3:traefik-k8s" cannot list resource "services" at cluster scope`
- traefik-k8s stuck in error state: `hook "config-changed" failed: exit status 1`
- Pebble readiness check returns HTTP 418
- Setting `external_hostname="penpot.example.com"` does not fix it
- This is an environment limitation, not a charm bug

#### s3-integrator
- Blocked: "Missing parameters: ['access-key', 'secret-key']"
- s3-integrator needs credentials via `sync-s3-credentials` action (from AWS)
- No MinIO in this environment
- Not a charm bug

#### smtp-integrator
- Blocked: "invalid configuration: host"
- Not configured with host
- Can configure with `host="invalid..hostname" port="99999"` → blocked on port
- Not a charm bug

#### penpot status
- Blocked: "waiting for ingress, s3"
- postgresql ✓ (related with rev 774)
- redis ✓ (related)
- ingress ✗ (traefik-k8s in error)
- s3 ✗ (no credentials)

### Hook sequence observed (from container-agent log)
```
21:20:27 install
21:20:28 penpot_peer-relation-created     ← peer relation created BEFORE leadership
21:20:29 leader-elected                 ← leadership acquired AFTER peer relation
21:20:30 penpot-pebble-ready
21:20:32 config-changed
21:20:34 start
21:20:36 penpot_peer-relation-changed   ← leader wrote secret to peer relation
21:24:22 redis-relation-created
21:24:22 redis-relation-joined
21:24:23 redis-relation-changed (×3)
21:25:09 update-status                   ← no handler, charm does nothing
21:30:01 postgresql-relation-created
21:30:02 postgresql-relation-joined
21:30:05 postgresql:10: database created ← from container-agent log
21:30:02 postgresql-relation-changed (×3)
21:31:00 update-status
21:31:17 ingress-relation-created
```

## Phase 3 — Failure injection

### Remove redis relation
- `juju remove-relation penpot redis-k8s`
- Status changed to "waiting for ingress, redis, s3" — correctly detected
- Re-added: `juju integrate penpot:redis redis-k8s` → status restored ✓

### Remove postgresql relation (CRITICAL)
- `juju remove-relation penpot postgresql-k8s`
- Status changed to "waiting for ingress, postgresql, s3" within 5 seconds ✓
- No traceback, clean BlockedStatus propagation ✓
- Restored: `juju integrate penpot:postgresql postgresql-k8s:database` → status restored ✓

### Action execution while blocked
- `juju run penpot/0 create-profile email="test@example.com"` → "penpot is not ready" ✓
- `juju run penpot/0 delete-profile email="test@example.com"` → "penpot is not ready" ✓
- Graceful failure, no traceback ✓

### Bad smtp-integrator config
- `juju config smtp-integrator host="invalid..hostname" port="99999"`
- smtp-integrator blocked with "invalid configuration: port" ✓
- Penpot unaffected (SMTP is optional without OAuth)

### smtp-from-address bad config
- `juju config penpot smtp-from-address="not-an-email"` → accepted without error
- Charm passes this through to the backend as PENPOT_SMTP_DEFAULT_FROM
- No validation at charm level (intentional — Penpot validates it)
- Not a bug

### traefik-k8s with external_hostname
- `juju config traefik-k8s external_hostname="penpot.example.com"`
- traefik-k8s still in error (LoadBalancer unavailable)
- Penpot still blocked on ingress

## Phase 4 — Code review additions

### CRITICAL CORRECTION: exporter PENPOT_SECRET_KEY
My earlier finding was WRONG. The exporter DOES have `**self._get_penpot_secret_key()`.
Reading `src/charm.py:231`:
```python
"exporter": {
    "environment": {
        "PENPOT_PUBLIC_URI": "http://127.0.0.1:8080",
        "PLAYWRIGHT_BROWSERS_PATH": "/opt/penpot/exporter/browsers",
        **self._get_penpot_secret_key(),   # PRESENT AT LINE 231
        **self._get_redis_credentials(),
    },
},
```
The unit test `test_penpot_pebble_layer` also deletes `PENPOT_SECRET_KEY` from the exporter:
```python
del plan["services"]["exporter"]["environment"]["PENPOT_SECRET_KEY"]
```
This confirms it exists. REMOVE this finding from the review.

### _get_penpot_exporter_unit race condition
Called from `_reconcile` → `_gen_pebble_plan` → `_get_penpot_exporter_uri` → `_get_penpot_exporter_unit`
In observed practice, peer relation is created BEFORE leadership, so `get_relation` always returns a valid relation.
BUT: `upgrade_charm` or `config_changed` could theoretically fire before peer relation. Not tested.
Risk: LOW in practice, MEDIUM for test coverage.

### _check_ready not observed in blocked state
When penpot is blocked, `_check_ready` is called on every hook. The blocked message correctly shows unfulfilled requirements.
The `_check_ready` check `"https enabled on ingress": not public_uri or public_uri.startswith("https://")` 
correctly blocks non-HTTPS ingress URLs.

### Unit test coverage gaps
- `_get_local_resolver` — no test
- `_get_kubernetes_cluster_domain` — no test
- `_check_penpot_backend_ready` — not tested (only monkeypatched)
- `_check_ready` — no direct test of the blocked path
- No test for missing peer relation
- `_get_oauth` — not tested
- `_get_penpot_oauth_config` — not tested

### Charm libraries reviewed
- `data_platform_libs v0/s3.py`: S3Requirer.get_s3_connection_info() returns empty dict if no credentials
- `data_platform_libs v0/data_interfaces.py`: fetch_relation_field reads direct from databag (no JSON decode for endpoints)
- `traefik_k8s v2/ingress.py`: IngressPerAppRequirer.url returns None if not ready
- `hydra v0/oauth.py`: ClientConfig.validate() raises ClientConfigError for invalid URL format
- `smtp_integrator v0/smtp.py`: SmtpRequirer.get_relation_data() returns Optional[SmtpRelationData]

### Dispatch script in packed charm
The packed charm (`penpot_amd64.charm`) has a correct dispatch script:
```sh
export PYTHONPATH="${dispatch_path}/lib:${dispatch_path}/src"
exec "${python_path}" "${dispatch_path}/src/charm.py"
```
The `charmcraft analyze` tool reports `Cannot find the entrypoint file: '${dispatch_path}/src/charm.py'` — this is a 
charmcraft analyze tool limitation with modern uv-plugin charms, not a charm bug.

### Rock run-user
`penpot_rock/rockcraft.yaml` has `run-user: _daemon_`. The pebble services will run as uid 584792 (_daemon_).
This matches the file ownership of /opt/penpot/* directories (verified in container).

## Phase 5 — Linting
- `ruff check src/` → 0 errors ✓
- `ruff check lib/` → 228 errors (all in charm libraries, not the charm itself)
  - UP032 f-strings (`.format()` calls)
  - B006 mutable defaults
  - S101 `assert` statements
  - Various other issues in `loki_k8s`, `prometheus_k8s`, `smtp_integrator`, `traefik_k8s`, `redis_k8s`
- `mypy src/charm.py` → Success: no issues found ✓
- `codespell src/` → 0 issues ✓

## Phase 6 — Tests
- `PYTHONPATH=.:lib .venv/bin/pytest tests/unit/test_charm.py -v` → 13 passed, 21 warnings
- Coverage: 76% of src/charm.py
- Missing: _check_ready blocked path, _check_penpot_backend_ready, _get_local_resolver, 
  _get_kubernetes_cluster_domain, reconcile timeout path, _get_penpot_exporter_unit without peer relation,
  _get_oauth, _get_penpot_oauth_config

## Key findings summary
1. ~~exporter missing PENPOT_SECRET_KEY~~ → WRONG, REMOVE
2. Unit tests require PYTHONPATH=.:lib → HIGH
3. _reconcile 120s busy-wait → HIGH
4. postgresql-k8s interface incompatibility → CRITICAL (wrong revision deployed by default)
5. traefik-k8s LoadBalancer unavailable → environment limitation, not bug
6. README nginx-ingress-integrator vs traefik-k8s → MEDIUM
7. Integration test revision pins not documented → MEDIUM
8. No update_status handler → LOW
9. _get_penpot_exporter_unit None access → MEDIUM (theoretical)
10. TimeoutError shadowing → LOW
11. combine=True always → LOW
12. search=True on FQDN → LOW

## New failure injection findings
- Critical relation (postgresql) removal: clean BlockedStatus, no traceback ✓
- Action execution while blocked: "penpot is not ready" ✓
- Bad SMTP config: smtp-integrator blocks, penpot unaffected ✓
- No juju refresh available: charm already at latest edge ✓
- traefik-k8s RBAC issue at cluster scope → environment limitation