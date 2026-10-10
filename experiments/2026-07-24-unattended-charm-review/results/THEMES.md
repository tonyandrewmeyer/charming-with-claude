# Cross-charm themes

_136 reviews as of 2026-08-27._ (One further review, `identity-saml-provider-operator`,
is code-only — no deployment was performed — and is flagged separately where cited.)

This file synthesizes only what is stated in `/home/ubuntu/charm-review/reviews/*.md`. No
charm was re-reviewed to produce it. Counts are "N of 136" unless a review explicitly
covers multiple charms (e.g. `kfp-operators.md`, `mysql-operators.md`), in which case the
review file is still counted once as one data point.

## Recurring defects

Ordered by frequency × severity.

### 1. Invalid config crashes the hook into `error` state instead of producing `BlockedStatus` (42 of 136 charms)

The single most common defect in the corpus. A config value that fails validation —
bad YAML, an out-of-range int, an invalid enum, a malformed secret URI — is fed straight
into a constructor, `yaml.safe_load()`, or a pydantic model without a try/except, so the
hook raises, Juju marks the unit `error`, and Juju holds all further hooks (including the
`config-changed` that would fix it) until the operator runs `juju resolve`. Confirmed
live, not just read from code, in most of these:

- `alertmanager-k8s-operator.md` (`src/charm.py:422`, unguarded `yaml.safe_load`) and again at `lib/charms/alertmanager_k8s/v0/alertmanager_remote_configuration.py:207`
- `traefik-k8s-operator.md` (`src/charm.py:1950`, invalid `routing_mode` raises in `__init__`, critical)
- `kafka-connect-k8s-operator.md` (`src/charm.py:65`, pydantic `ValidationError` on `log_level=TRACE`, critical)
- `opentelemetry-collector-k8s-operator.md` (`src/config_manager.py:624`, uncaught `yaml.YAMLError` on bad `processors`, critical — and the sibling method 80 lines away already has the right try/except, `src/config_manager.py:705-708`)
- `istio-k8s-operator.md` (`src/charm.py:216-237`, no try/except around `_reconcile`)
- `zookeeper-k8s-operator.md`, `zookeeper-operator.md`, `kafka-k8s-operator.md`, `kafka-operator.md`, `kafka-benchmark-operator.md`, `kafka-connect-operator.md`, `karapace-operator.md` — pydantic `ValidationError` propagating uncaught, several noting the crash surfaces on an unrelated later hook (e.g. `kafka-k8s-operator.md`: crash appears on `secret-changed`, not `config-changed`, because every hook re-runs `__init__`)
- `postgresql-k8s-operator.md` (`experimental_max_connections` has no `Field` bound; `1000000000` reaches Patroni and PostgreSQL FATALs, crash-looping Pebble so no hook can run to fix it)
- `blackbox-exporter-operator.md`, `blackbox-exporter-k8s-operator.md`, `prometheus-scrape-config-k8s-operator.md`, `prometheus-scrape-target-k8s-operator.md`, `script-exporter-operator.md`, `snmp-exporter-operator.md`, `sloth-k8s-operator.md`, `litmus-operators.md`, `kubeflow-dashboard-operator.md`, `dex-auth-operator.md`, `livepatch-k8s-operator.md`, `grafana-agent-operator.md`, `cos-coordinated-workers.md` (unguarded `yaml.safe_load` on relation/config data)
- `envoy-operator.md`, `mlflow-operator.md`, `mongodb-k8s-operator.md`, `mysql-operators.md`, `notary-k8s-operator.md`, `openfga-operator.md`, `opensearch-dashboards-operator.md`, `spark-integration-hub-k8s-operator.md`, `synapse-operator.md`, `tempo-operators.md`, `temporal-admin-k8s-operator.md`, `temporal-worker-k8s-operator.md`, `tenant-service-operator.md`, `trino-k8s-operator.md`, `ubuntu-manpages-operator.md`, `user-verification-service-operator.md`, `wordpress-k8s-operator.md`, `content-cache-k8s-operator.md`, `airbyte-k8s-operator.md`, `cos-proxy-operator.md`, `datahub-k8s-operator.md`, `hive-metastore-k8s-operator.md`, `istio-beacon-k8s-operator.md`, `kfp-operators.md`, `kyuubi-k8s-operator.md`, `loki-k8s-operator.md`, `maas-site-manager-k8s-operator.md`

**Why it keeps happening**: config validation is scattered — some charms validate in
`__init__` (crashes before any status can be set), some in a `config-changed` handler
that only some paths route through, some rely on a pydantic model's `Field` constraints
which several reviews found silently ignored (`postgresql-k8s-operator.md`: "All
`Annotated[..., Field(ge=…)]` numeric bounds are silently ignored — pydantic v1
incompatibility"). Juju's own `config.yaml`/`charmcraft.yaml` type system has no
enum/range constraint, so a `string`-typed option accepts anything, and there is no
tooling that mechanically confirms every `self.config[...]` read is validated before use.

**What would stop it**: a linter rule flagging any `yaml.safe_load()`, `json.loads()`, or
pydantic model construction fed by `self.config`/relation data that is not wrapped in a
try/except that converts the failure into `BlockedStatus`, plus a convention that no
charm should perform config-dependent object construction inside `__init__` (several
reviews — `traefik-k8s-operator.md`, `kafka-connect-k8s-operator.md` — separately note
that a Scenario-style unit test that constructs a fresh charm per event would have caught
this, whereas `Harness`, which reuses one charm instance, does not).

### 2. `postgresql-k8s` cannot be deployed on Juju 4.x, blocking full-stack testing of dependents (33 of 136 reviews)

Every `14/stable`, `14/edge`, and `16/stable` channel of `postgresql-k8s` declares
`assumes: juju < 4.0.0` and refuses to deploy on a Juju 4.x controller. This is not a bug
in any one charm — it is a single upstream dependency that gates the ecosystem. Reviews
that hit it and had to fall back to standalone/`Blocked`-status-only testing:
`airbyte-k8s-operator.md`, `airflow-coordinator-k8s-operator.md`,
`airflow-core-operators.md`, `authentik-ldap-outpost-operator.md`,
`authentik-worker-operator.md`, `charmed-canonical-cla.md`,
`cos-registration-server-k8s-operator.md`, `data-integrator.md`,
`discourse-k8s-operator.md`, `forgejo-k8s-operator.md`, `gatus-k8s-operator.md`,
`glauth-k8s-operator.md`, `hive-metastore-k8s-operator.md`, `hook-service-operator.md`,
`hydra-operator.md`, `identity-platform-admin-ui-operator.md`,
`identity-platform-login-ui-operator.md`, `identity-saml-provider-operator.md`,
`jimm-k8s-operator.md`, `kratos-operator.md`, `kyuubi-k8s-operator.md`,
`maas-site-manager-k8s-operator.md`, `maubot-operator.md`, `openfga-operator.md`,
`pgbouncer-k8s-operator.md`, `ranger-k8s-operator.md`, `superset-k8s-operator.md`,
`synapse-operator.md`, `temporal-admin-k8s-operator.md`, `temporal-k8s-operator.md`,
`temporal-ui-k8s-operator.md`, `tenant-service-operator.md`,
`ubuntu-insights-k8s-operator.md`. `postgresql-k8s-operator.md` itself confirms the root
cause — `charmcraft.yaml`'s `assumes: <4.0.0` block, "Repo CI tests against Juju 3.6 only,"
and cites open issue #1615 as evidence this is a known, unresolved pain point.

**Why it keeps happening**: it is one charm's decision, but because `postgresql-k8s` is
the de facto standard relational-database backend for the whole Canonical charm
ecosystem, its Juju-version ceiling becomes every dependent's ceiling. No dependent charm
reviewed can fully exercise its database-backed code paths against Juju 4.x today.

**What would stop it**: this cannot be fixed by any of the dependent charms — it needs
`postgresql-k8s` to ship a Juju-4.x-compatible revision. Until then, dependent charms
should (a) not imply Juju 4.x readiness in their own `assumes` block if their only
database option doesn't support it (`tenant-service-operator.md` calls its own
`assumes: [juju >= 3.0.2]` "technically correct but... misleading as a practical
minimum"), and (b) document the limitation explicitly rather than leaving operators to
discover it via a failed `juju deploy`.

### 3. Dead or crash-looping workload is not detected — charm keeps reporting `active` (≈22 of 136 charms)

`_on_update_status` (or the reconciler's status logic) sets `ActiveStatus` without
checking that the Pebble service is actually running or that the workload is reachable.
Confirmed live in:

- `alertmanager-k8s-operator.md` (`src/charm.py:508-558`; `pebble stop alertmanager` leaves charm `active/idle` for 30+ seconds with no detection; `kill -TERM` auto-restart also unnoticed)
- `kafka-operator.md` (`_determine_unit_status`, `machine/src/charm.py:214-237` and `k8s/src/charm.py:195-213` — "does not check workload health — false-positive active", critical)
- `opensearch-operator.md` (`health.py:85-125`, `health_manager` reports `active` when workload is unreachable, critical)
- `mlflow-operator.md` (`src/charm.py:1196`; a non-idempotent DB migration on refresh leaves the charm `active` while the workload crash-loops, critical)
- `mongos-k8s-operator.md`, `catalogue-k8s-operator.md`, `cos-registration-server-k8s-operator.md`, `envoy-operator.md`, `falco-operators.md`, `forgejo-k8s-operator.md`, `grafana-k8s-operator.md`, `parca-agent-operator.md`, `prometheus-k8s-operator.md`, `spark-integration-hub-k8s-operator.md`, `temporal-ui-k8s-operator.md`, `temporal-worker-k8s-operator.md`, `valkey-operator.md`, `kratos-operator.md` (Pebble-check race), `airflow-core-operators.md`, `maas-site-manager-k8s-operator.md`, `notebook-operators.md`, `oathkeeper-operator.md`, `oidc-gatekeeper-operator.md`, `ranger-k8s-operator.md`, `resource-dispatcher.md`, `wordpress-k8s-operator.md`

**Why it keeps happening**: `ops`'s Pebble abstraction makes it easy to fire-and-forget a
layer update and set `ActiveStatus` immediately, without a follow-up check that the
service reached `active`/`running` state or that a `pebble-check-failed` event is
observed. Writing a correct health probe requires workload-specific knowledge (an HTTP
endpoint, a CLI healthcheck, a log pattern) that generic Pebble status doesn't give for
free.

**What would stop it**: a lint/review rule — "charm sets `ActiveStatus` in a status
handler without first checking `container.get_service(name).is_running()` or an
equivalent live check" — is mechanically checkable for the Pebble-service case (as
`alertmanager-k8s-operator.md` proposes), though the "unreachable but technically
running" case (opensearch, mlflow) needs an actual health probe and is not.

### 4. Missing or incomplete `relation_departed`/`relation_broken` handling leaves stale state (≈20 of 136 charms)

A charm observes `relation_joined`/`relation_changed` on a relation but not
`relation_departed`/`relation_broken`, or observes it but the handler doesn't actually
clear derived state. Confirmed patterns:

- `alertmanager-k8s-operator.md` (`src/charm.py:264-267`; no peer `relation_departed` → stale `--cluster.peer=` args, stale self-scrape targets, open cluster port, indefinite log-spam after scale-down)
- `jenkins-agent-k8s-operator.md` (`src/charm.py:93-97`, high severity: `relation_departed` doesn't stop the agent, it keeps running against the departing server's credentials)
- `landscape-debarchive-operator.md` ("No relation-broken/relation-departed handlers for any of the three relations", `src/charm.py:34-60`, confirmed live: old DB credentials survive relation removal)
- `wazuh-server-operator.md` (bundled `loki_push_api` library's `_on_relation_departed` crashes both units trying to stop a service that was never started — critical, `lib/charms/loki_k8s/v1/loki_push_api.py:1776`)
- `wordpress-k8s-operator.md`, `livepatch-k8s-operator.md`, `kubeflow-dashboard-operator.md`, `kubeflow-tensorboards-operator.md`, `openfga-operator.md`, `kratos-operator.md`, `notary-k8s-operator.md`, `parca-agent-operator.md`, `github-runner-operator.md`, `grafana-agent-k8s-operator.md`, `identity-platform-admin-ui-operator.md`, `kafka-connect-operator.md`, `kafka-k8s-operator.md`, `notebook-operators.md`, `prometheus-scrape-config-k8s-operator.md`, `synapse-operator.md`, `catalogue-k8s-operator.md`, `gatus-k8s-operator.md`

**Why it keeps happening**: `relation_joined`/`relation_changed` are the events every
tutorial and library example wires up first; the departure/removal path is symmetric in
principle but asymmetric in how much code most libraries and charms actually write for
it, and it's the path least exercised by "deploy and check active" integration tests.

**What would stop it**: mechanically checkable — "charm/library observes
`relation_joined` or `relation_changed` on a relation without also observing
`relation_departed`/`relation_broken` on the same endpoint" (as
`alertmanager-k8s-operator.md` and `landscape-debarchive-operator.md` both propose
independently). Does not catch the harder case where the handler exists but is a no-op or
crashes (wazuh, jenkins-agent) — that needs a relation-removal integration test.

### 5. Deprecated `ops.testing.Harness` still used in unit tests (39 of 136 charms, mid-migration in most)

`Harness` is deprecated in current `ops` but remains the primary or sole unit-test
mechanism in 39 reviewed charms: `catalogue-k8s-operator.md`,
`content-cache-k8s-operator.md`, `cos-proxy-operator.md`, `envoy-operator.md`,
`grafana-cloud-integrator.md`, `istio-ingress-k8s-operator.md`, `kfp-operators.md`,
`kubeflow-tensorboards-operator.md`, `oathkeeper-operator.md`,
`oidc-gatekeeper-operator.md`, `pgbouncer-operator.md`, `postgresql-k8s-operator.md`,
`postgresql-single-kernel-library.md`, `prometheus-scrape-target-k8s-operator.md`,
`pvcviewer-operator.md`, `resource-dispatcher.md`, `synapse-operator.md`,
`test_observer.md`, and 21 more found by `grep -il "Harness"`. 41 charms mix `Harness`
and the newer Scenario-style `ops.testing.Context`/`State` API in the same test suite
(e.g. `alertmanager-k8s-operator.md`: "mixes ops Harness ... with newer Scenario-based
tests ... understandable mid-migration"). Nowhere in the corpus is this rated above
`low`/`nit` severity on its own — but see Recurring Defect #1: `traefik-k8s-operator.md`
and `kafka-connect-k8s-operator.md` both specifically note that `Harness`'s instance
reuse across events *masked* the `__init__`-crash bug, because a fresh-charm-per-event
Scenario test would have caught it immediately. The migration is not merely stylistic.

**Why it keeps happening**: `Harness`-based suites are large (hundreds of tests in some
charms) and rewriting them is a multi-week project with no functional payoff unless it
happens to expose a latent bug like the one above; teams migrate opportunistically.

**What would stop it**: "unit test file imports `ops.testing.Harness`" is mechanically
checkable (several reviews note this directly), but a blanket lint failure would be
disruptive given how widespread it still is; better framed as a tracked migration debt
metric than a blocking rule, with the exception that any charm doing config-dependent
`__init__` work (Defect #1) should prioritize migrating specifically to catch that class
of bug.

### 6. No Juju actions defined even where the charm has state that operators need to inspect or trigger (38 of 136 charms)

`airbyte-k8s-operator.md`, `airflow-core-operators.md` ("no actions on any of 4 charms"),
`authentik-ldap-outpost-operator.md`, `authentik-worker-operator.md`,
`blackbox-exporter-operator.md`, `cos-proxy-operator.md`, `dex-auth-operator.md`,
`falco-operators.md`, `glauth-k8s-operator.md`, `grafana-agent-operator.md`,
`grafana-cloud-integrator.md`, `hive-metastore-k8s-operator.md`,
`identity-platform-login-ui-operator.md`, `istio-beacon-k8s-operator.md`,
`istio-ingress-k8s-operator.md` (open issue #108 explicitly requests a
`show-proxied-endpoints` action), `jenkins-agent-k8s-operator.md`, `katib-operators.md`,
`kiali-k8s-operator.md`, `kserve-operators.md` (all four charms), `kubeflow-dashboard-operator.md`,
`kubeflow-profiles-operator.md`, `loki-k8s-operator.md`, `minio-operator.md`,
`notary-k8s-operator.md`, `oidc-gatekeeper-operator.md`, `opencti-operator.md` (docs
reference an actions page that doesn't exist), `otel-ebpf-profiler-operator.md`,
`parca-scrape-target-operator.md`, `prometheus-pushgateway-k8s-operator.md`,
`prometheus-scrape-config-k8s-operator.md`, `pyroscope-operators.md` (both charms),
`resource-dispatcher.md`, `script-exporter-operator.md`, `sloth-k8s-operator.md`,
`spark-history-server-k8s-operator.md`, `user-verification-service-operator.md`,
`wazuh-server-operator.md`.

**Why it keeps happening**: actions are optional and add maintenance surface; many of
these charms are thin wrappers or sidecars where "no actions" is a defensible design
choice, and several reviews rate this only `low`. But a sizeable minority note concrete
operator pain: no way to force reconciliation, dump effective config, or rotate a
credential without `juju ssh`.

**What would stop it**: mechanically checkable ("charm has no `actions.yaml`/`actions:`
block") but needs judgement on whether it matters for a given charm — flag it, don't
block on it, and weight severity by whether the charm has config/relation error paths an
operator would otherwise have to diagnose via `juju ssh`.

### 7. Bare `except Exception` / silently-swallowed errors (35 of 136 charms)

Broad exception handlers that catch everything and either log-and-continue or discard
the error, hiding the actual failure from the operator and from `juju debug-log`.
Present in `airbyte-k8s-operator.md` (`src/relations/minio.py:131`,
`src/s3_helpers.py:38`, `src/charm_helpers.py:267,295`), `airflow-coordinator-k8s-operator.md`,
`authentik-ldap-outpost-operator.md`, `blackbox-exporter-operator.md`,
`charm-microceph.md`, `discourse-k8s-operator.md`, `envoy-operator.md`,
`feast-operators.md`, `gatus-k8s-operator.md`, `grafana-k8s-operator.md`,
`istio-k8s-operator.md`, `jimm-k8s-operator.md`, `kafka-benchmark-operator.md`,
`kafka-connect-k8s-operator.md`, `katib-operators.md`, `kubeflow-dashboard-operator.md`,
`kubeflow-volumes-operator.md`, `kyuubi-k8s-operator.md`,
`landscape-debarchive-operator.md`, `litmus-operators.md`, `livepatch-k8s-operator.md`,
`maas-site-manager-k8s-operator.md`, `mediawiki-k8s-operator.md`, `minio-operator.md`,
`mlflow-operator.md`, `opencti-operator.md`, `otel-ebpf-profiler-operator.md`,
`spark-integration-hub-k8s-operator.md`, `sysbench-operator.md`,
`temporal-admin-k8s-operator.md`, `temporal-worker-k8s-operator.md`,
`tenant-service-operator.md`, `test_observer.md`, `ubuntu-insights-k8s-operator.md`,
`ubuntu-manpages-operator.md`.

**Why it keeps happening**: broad `except Exception` is the easiest way to keep a hook
from crashing when the author hasn't enumerated every exception type a library call can
raise — it trades a debuggable crash for a silent partial failure.

**What would stop it**: `ruff` already has a rule for this (`BLE001` /
bare-except-style lints) but multiple reviews note it is not enabled or not in CI for
their charm — see Linter rules below.

### 8. `ubuntu@26.04`-only HEAD tracks are undeployable on any tested controller (10 of 136 charms)

Several COS/observability charms' HEAD/edge tracks have moved to `ubuntu@26.04` bases
while every controller used in this programme (`concierge-k8s-3`, `concierge-k8s-4`) only
supports up to `ubuntu@24.04`. Reviewers had to test an older, sometimes materially
different, stable/edge revision instead of HEAD: `alertmanager-k8s-operator.md` ("the
charm defined bases ubuntu@26.04 not supported — neither controller supports 26.04"),
`blackbox-exporter-k8s-operator.md`, `catalogue-k8s-operator.md`,
`cos-configuration-k8s-operator.md`, `loki-k8s-operator.md`, `parca-k8s-operator.md`,
`prometheus-k8s-operator.md`, `prometheus-scrape-config-k8s-operator.md`,
`prometheus-scrape-target-k8s-operator.md`, `tempo-operators.md` ("unavailable on any
Juju 4.x controller lacking ubuntu@26.04 — worth flagging to users even if not fixable
quickly"; also notes `2/stable` "predates the coordinated-workers split", i.e. the only
deployable track is architecturally stale).

**Why it keeps happening**: base migrations happen on the maintainers' own schedule,
decoupled from what test infrastructure exists; this is an infrastructure/tooling gap in
the review programme as much as a charm defect (see "What the reviews are not covering").

**What would stop it**: not a per-charm fix. Either the review programme needs a
26.04-capable controller, or maintainers need to keep a 24.04-buildable track alongside
HEAD until reviewers' tooling catches up.

### 9. Shared libraries (`coordinated_workers`, `loki_push_api`, `tls_certificates_interface`) propagate one bug to every consumer

`cos-coordinated-workers.md` reviews the PyPI library directly and finds an unguarded
`update-ca-certificates` call that "cascades across every worker on any topology
change" plus TLS lifecycle gaps; `tempo-operators.md` and `pyroscope-operators.md`
independently hit consequences of the same library (`tempo-operators.md`:
"unhandled exception in the `coordinated_workers` library validating an empty databag",
`coordinated_workers/coordinator.py:1118-1125` producing duplicated nginx config blocks;
`pyroscope-operators.md`: `is_recommended` check and `_on_collect_unit_status` issues
traced to the same library). Separately, `wazuh-server-operator.md` and
`alertmanager-k8s-operator.md` both hit bugs inside the bundled `loki_push_api` /
`tls_certificates_interface` libraries rather than in charm-authored code.

**Why it keeps happening**: charm libraries are vendored copies (`lib/charms/.../vN/`)
pinned per-charm, so a fix in one consumer doesn't propagate until every other consumer
bumps its `LIBPATCH`; the coordinated-workers case is worse because it's a PyPI package
version pin, invisible to `charmcraft.yaml`'s library-version tooling entirely.

**What would stop it**: not mechanically fixable per-charm. Worth tracking library/PyPI
package versions across the fleet centrally and flagging when N consumers are still on
an old, bug-confirmed revision.

## Linter rules worth building

Ranked by (charms caught × severity). "Charms caught" is the count from Recurring
Defects above, cited once here.

| Rule | Fires on | Charms caught | False-positive risk | Checkable? |
|---|---|---|---|---|
| **No try/except around `yaml.safe_load()`/`json.loads()`/pydantic model construction fed by `self.config` or relation data, without a path to `BlockedStatus`** | Any parse of user/relation-supplied structured data | 42 (Defect #1) — directly proposed independently in `alertmanager-k8s-operator.md`, `opentelemetry-collector-k8s-operator.md`, `blackbox-exporter-operator.md`, `prometheus-scrape-target-k8s-operator.md` | Low — the pattern (parse call, no except, propagates to hook boundary) is syntactically identifiable | Mechanically checkable (static call-graph / AST match), per multiple reviews |
| **Config-dependent object construction inside `__init__` that can raise on invalid config** | `__init__` calling a property/function that parses `self.config[...]` before any status is set | ~8+ of the 42 in Defect #1 are specifically `__init__`-time crashes (`traefik-k8s-operator.md:1950`, `kafka-connect-k8s-operator.md:65`, `istio-k8s-operator.md:216-237`, `envoy-operator.md`) | Medium — some `__init__`-time work is legitimate (e.g. constructing typed-config wrappers); needs to distinguish "parses and may raise" from "stores unparsed" | Partially checkable via call-graph analysis (as `traefik-k8s-operator.md` notes) |
| **Relation endpoint observed for `relation_joined`/`relation_changed` but not `relation_departed`/`relation_broken`** | Charm or library `self.framework.observe()` calls | 20 (Defect #4) | Low-medium — some relations are legitimately fire-and-forget, but asymmetric observation is itself a signal worth a warning | Mechanically checkable (static analysis of `observe()` call sites), proposed independently in `alertmanager-k8s-operator.md` and `landscape-debarchive-operator.md` |
| **`ActiveStatus` set in a status/reconcile handler without checking `container.get_service(name).is_running()` (or equivalent) first** | Status-setting code paths | ~10 of the 22 in Defect #3 are specifically the Pebble-service-not-running case (the rest need a workload-specific health probe, not mechanically checkable) | Medium — many charms genuinely have nothing more to check; rule should require presence of a Pebble service before firing | Mechanically checkable for the Pebble case; not for reachability-only failures |
| **Unit test suite imports `ops.testing.Harness`** | Test files | 39 (Defect #5) directly, but real payoff is the subset that also does config-dependent `__init__` work (Defect #1 overlap) | High as a hard gate (Harness is still valid, if deprecated); low as a tracked-debt metric | Mechanically checkable by import scan |
| **Bare `except Exception`/`except:` with no re-raise or specific handling** | Exception handlers | 35 (Defect #7) | Medium — some broad catches at a hook's outermost boundary are intentional "fail into BlockedStatus" patterns; needs to distinguish outermost-boundary catches from mid-function swallowing | Already available via `ruff` (`BLE001`); several reviews note it isn't enabled |
| **Charm has no `actions:` block** | `charmcraft.yaml` | 38 (Defect #6) | High as a hard rule (many charms legitimately need none) | Mechanically checkable; needs judgement to act on |
| **`container.push()` to a path matching `*.key.pem`/`*secret*` without a subsequent permission restriction, or an action handler that returns file contents matching a key/secret pattern unfiltered** | Filesystem writes and action return values | Directly confirmed in `alertmanager-k8s-operator.md` (0644 key file, `show-config` leaks it) and echoed by "world-readable"/"leak" findings in ~10 other charms via TLS/secret file handling (see `feast-operators.md`, `mlflow-operator.md`'s password-in-argv finding, `postgresql-single-kernel-library.md`'s password-in-SQL findings) | Low | Mechanically checkable (path/name pattern match) |
| **`README`/docs contain `juju run-action ... --wait`** (removed Juju 3.x syntax) | Documentation | 3 confirmed by grep (`alertmanager-k8s-operator.md`, `charm-rabbitmq-k8s.md`, `katib-operators.md`); likely undercounted since this wasn't searched exhaustively across all docs prose | None | Mechanically checkable via grep, trivial to add to CI |
| **`assumes: juju >= X` claims a Juju version floor that the charm's mandatory relation partner doesn't itself support** | `charmcraft.yaml` cross-referenced against a dependency's own `assumes` | Would have flagged the `postgresql-k8s`/Juju-4.x gap (Defect #2) for the 33 dependents, had it existed before deployment | Low, but requires the linter to have access to the dependency charm's metadata, not just the charm under review | Not mechanically checkable from a single charm's source alone — needs fleet-level metadata |

## Patterns worth copying

- **Single reconciler / holistic-handler entry point.** `alertmanager-k8s-operator.md`'s
  `_common_exit_hook()` (`src/charm.py:508-558`) and the same pattern under different
  names in `authentik-ldap-outpost-operator.md` (`_holistic_handler`),
  `airflow-core-operators.md` (exception-based status + no-`defer()` reconciler,
  explicitly called "a strong example for the ecosystem"), and
  `identity-saml-provider-operator.md` (`_holistic_handler` gated by `NOOP_CONDITIONS`
  tuples) all funnel every event through one function that recomputes desired state from
  scratch. This is easier to reason about and test than N independent per-event handlers,
  and directly avoids Defect #4 (asymmetric relation-event observation) when done
  consistently — though `alertmanager-k8s-operator.md` shows the pattern still needs every
  triggering event wired up correctly, or the same class of staleness bug recurs.
- **`ConfigFileSystemState`** (`alertmanager-k8s-operator.md`, `src/alertmanager.py:30-69`):
  desired filesystem state expressed as `path → content | None`, with `has_changes()` and
  `apply()` — a clean, idempotent, diffable config-push abstraction that several other
  reviews' "worth copying" sections independently praise in different charms under names
  like "config-change idempotency" (`airflow-core-operators.md`, `hive-metastore-k8s-operator.md`).
- **Passing callables, not computed values, into long-lived worker objects.**
  `alertmanager-k8s-operator.md` explicitly diagnoses the *inverse* of this as the root
  cause of five separate bugs (frozen `peer_netlocs`, `web_external_url`, `cafile`), while
  noting the same charm does it correctly for `tls_enabled` via a lambda — the fix pattern
  is proven to work in the same codebase, just inconsistently applied.
- **`CollectStatusEvent`/`collect_unit_status` for status aggregation** — used correctly in
  46 of 136 reviews as the modern replacement for setting `self.unit.status` ad hoc across
  handlers (e.g. `authentik-ldap-outpost-operator.md`: "correct modern ops pattern";
  `blackbox-exporter-k8s-operator.md`: "modern `collect_app_status` pattern"). Charms still
  setting status directly from arbitrary handlers are more prone to Defect #3 because
  there's no single place to check workload health before reporting `active`.
- **Dedicated Terraform module per charm, with CI validation.** Present in 97 of 136
  reviews; `blackbox-exporter-operator.md` calls out `terraform fmt`/`validate`/`test` in
  CI plus terraform-docs generation as the standard worth matching; `jimm-k8s-operator.md`
  ships both a per-charm and a full-stack Terraform module.
- **`jubilant`-based integration tests with real functional assertions**, not just
  active/idle polling. `airbyte-k8s-operator.md`'s `deploy_full_stack()` runs an actual
  sync job; `karapace-operator.md`'s suite does login-flow, cluster-API, and
  password-rotation HTTP assertions with `successes=N` stability checks;
  `cos-registration-server-k8s-operator.md` asserts specific relation-data content rather
  than presence/truthiness only (while also noting, self-critically, which flows its own
  suite does *not* cover — see Divergence below).
- **Fluent config-builder pattern.** `alertmanager-k8s-operator.md`'s `ConfigBuilder`
  (`src/config_builder.py`) with chained `.set_config().set_tls_server_config()...build()`
  producing a frozen dataclass — cleanly separates config generation from Pebble-layer
  lifecycle.
- **Graceful degradation on optional relations.** `blackbox-exporter-k8s-operator.md`:
  "certificates, tracing, and logging relations are all optional and don't error when
  absent; only the database relation blocks" — worth contrasting with the many charms in
  Defect #1 that crash on absent-but-optional integration data instead.

## Divergence in common practice

- **Testing framework: `Harness` vs Scenario (`ops.testing.Context`/`State`), and
  `pytest-operator` vs `jubilant` for integration tests.** 80 of 136 reviews mention
  `Harness` still in use, 65 mention Scenario-style tests, and 41 charms mix both in the
  same suite. For integration tests, 60 reviews mention `jubilant` and 39 mention
  `pytest-operator`, with 19 charms apparently using or discussing both. The evidence
  favours Scenario/`jubilant`: two separate reviews (`traefik-k8s-operator.md`,
  `kafka-connect-k8s-operator.md`) show `Harness`'s charm-instance reuse across events
  actively concealed a real `__init__`-crash bug that a fresh-per-event Scenario test would
  have caught, and no review anywhere argues the reverse. This is not fully settled only in
  the sense that no review claims the migration is complete or mandatory-by-policy across
  the fleet — it is clearly in progress, unevenly, charm by charm.
- **Config validation library: pydantic/`TypedCharmBase` vs hand-rolled `self.config.get()`
  checks.** 78 of 136 reviews mention pydantic; 25 explicitly use `TypedCharmBase`/
  `ConfigBase`-style structured config. The evidence does not clearly favour pydantic on
  its own — `postgresql-k8s-operator.md` found pydantic v1-style `Field(ge=…)` bounds
  silently ignored in production, and `kafka-connect-k8s-operator.md`'s crash is pydantic
  raising `ValidationError` *uncaught* at `__init__` time rather than being converted to
  `BlockedStatus`. Structured config only helps if paired with the try/except discipline
  from Defect #1's fix — the library choice is secondary to whether validation failures
  are actually caught.
- **Status handling: single reconciler with `CollectStatusEvent` vs scattered
  `self.unit.status =` assignments across handlers.** The reconciler pattern is described
  as "worth adopting" or similar in at least 5 reviews (`alertmanager-k8s-operator.md`,
  `authentik-ldap-outpost-operator.md`, `airflow-core-operators.md`, and others under
  "Reconciler pattern"/"Holistic handler pattern" in `/tmp/worth_copying.txt`), and no
  review argues for the scattered-assignment style. This is close to settled in the
  corpus's own judgement, even though a majority of charms still don't use it purely.
- **Charm library layout: vendored `lib/charms/<charm>/v<N>/` files vs PyPI packages
  (`coordinated_workers`, `mongo-charms-single-kernel`, `ops-sunbeam`).** Both exist
  side-by-side; the PyPI-package approach (`cos-coordinated-workers.md`) means a single
  version bump can fix every consumer at once in principle, but in practice (Recurring
  Defect #9) consumers pin different revisions and inherit different bug sets anyway — the
  evidence doesn't settle which layout is actually better in practice, only that both leak
  bugs to consumers when the underlying library has one.
- **Upgrade-path testing: some charms test same-track `juju refresh` explicitly, most
  don't test cross-base/cross-track upgrades at all.** 23 of 136 reviews report upgrade
  paths as skipped, untested, or broken (`alertmanager-k8s-operator.md`'s entire
  `test_upgrade_charm.py`/`test_persistence.py` suites are `pytest.mark.skip`;
  `maas-site-manager-k8s-operator.md`'s `juju refresh` rev 50→53 was rejected outright on
  Juju 4.x). No review presents a charm with comprehensive upgrade coverage as a
  counter-example to hold up as the standard — this is an open gap, not a settled
  disagreement.

## Deployability

133 of 136 reviews report a successful deploy of at least one charm/configuration
(possibly requiring a workaround or limited to a subset of integrations); 1
(`identity-saml-provider-operator.md`) recorded no deployment attempt at all (a deploy
plan was written but not executed — that review's findings are code-only and are flagged
as such above); 2 (`karapace-k8s-operator.md`, `sunbeam-charms.md`) report only partial
success, unable to reach a fully working stack in this environment.

Common failure modes, in order of how many charms they affected:

1. **Dependency-chain Juju-version mismatch** (Defect #2): 33 reviews report the charm
   itself deploying fine on Juju 4.x but the stack being untestable end-to-end because
   `postgresql-k8s` won't deploy there. This is overwhelmingly the largest deployability
   blocker in the corpus and is entirely attributable to one upstream charm.
2. **Base/channel mismatches** (Defect #8): 10 reviews had to fall back to an older,
   sometimes architecturally different, revision because HEAD requires
   `ubuntu@26.04` and no available controller supports it.
3. **Charm-specific install-hook or runtime failures on Juju 4.x specifically**: a smaller
   but real set — `kafka-k8s-operator.md` (`OSError: [Errno 19] No such device`),
   `snmp-exporter-operator.md` (fails in install hook on k8s/Juju 4.0.12),
   `cos-proxy-operator.md` (charm-store UUID parsing bug on Juju 4.0.12),
   `kafka-operator.md` (K8s controller timeout, 3 attempts), `jimm-k8s-operator.md`
   (required a manual K8s RBAC workaround before the install hook would succeed on Juju
   4.0.12).
4. **Undeclared out-of-band dependencies**: `airbyte-k8s-operator.md`'s charm never
   reaches `active` without a separately-deployed Temporal instance and a manually-created
   namespace, none of which is enforced through a relation or surfaced in status —
   effectively a deployability failure disguised as a config problem.

What this says about the ecosystem: the charms themselves are, on the whole, reasonably
deployable — most reach `active` with a single `juju deploy` and standard channel. The
programme's deployability problems are concentrated at the edges of the dependency graph
(one shared database charm) and at the leading edge of base support (26.04), not spread
evenly across individual charms' own install logic. That said, once a full stack is up,
Recurring Defects #1, #3, and #4 mean many of these same charms are fragile to config
changes, workload crashes, and relation churn after the initial deploy — "deploys cleanly"
and "operates robustly" are different bars, and this corpus shows the ecosystem clears the
first much more consistently than the second.

## What the reviews are not covering

- **Substrate skew toward k8s.** 92 of 136 reviews are pure k8s charms; only 8 are pure
  `machine`, 8 are `machine (LXD)`, and the rest are mixed/dual-substrate. Machine-charm-
  specific failure modes (snap upgrades, systemd unit management, storage pool quirks) are
  proportionally under-sampled relative to how much of the real charm ecosystem is
  machine-based.
- **No public-cloud substrate testing.** Every deployment in the corpus runs on
  `concierge-k8s-3`/`-4` or `concierge-lxd`/`-4` — local Juju controllers. No review
  deploys against AWS, Azure, GCP, OpenStack, or MAAS-managed bare metal, despite several
  charms (`postgresql-operator.md`, `postgresql-k8s-operator.md`, `charmed-etcd-operator.md`,
  `opensearch-operator.md`, `minio-operator.md`, `spark-history-server-k8s-operator.md`,
  `mlflow-operator.md`, `synapse-operator.md`, `cassandra-operator.md`,
  `kfp-operators.md`) mentioning S3/object-storage or cloud-specific integrations in
  passing. S3 backends were exercised as relations (e.g. against a mocked/local endpoint)
  but not against a real cloud object store.
- **No multi-controller/cross-model relation testing at scale.** Cross-model relations
  (`juju offer`/`juju consume`) are mentioned as Terraform-module capabilities (e.g.
  `authentik-ldap-outpost-operator.md`'s `juju_offer` resource) but no review actually
  exercises a live cross-model relation — everything is single-model.
  `airflow-coordinator-k8s-operator.md` and others test multi-charm stacks, but always
  within one model.
- **No long-running/soak testing.** Every review is a bounded session (deploy, exercise,
  tear down). Slow leaks (`parca-agent-operator.md`'s "parca-agent snap is pinned to a
  version with a known memory leak" was found by reading changelogs/issues, not by running
  long enough to observe it), certificate-rotation-over-weeks, or storage growth over time
  are out of scope for the whole programme as currently run.
- **No adversarial/security-focused testing beyond what falls out of functional
  exercise.** Secret/key-leak findings (Defect-adjacent, e.g.
  `alertmanager-k8s-operator.md`'s `show-config` leaking a private key,
  `mlflow-operator.md`'s password-in-`argv`, `postgresql-single-kernel-library.md`'s
  password-in-SQL-string findings) were discovered incidentally while testing normal
  functionality, not through a dedicated pass looking for credential handling, RBAC
  over-permissioning, or injection issues. `katib-operators.md`'s note about an "orphaned
  Juju-substrate ClusterRole with `*/*:*/*` permissions" is the closest thing to a
  deliberate RBAC check, and it's a single finding in a single review.
- **Windows/other non-Ubuntu bases**: not applicable to this charm set, but worth naming
  as fully unaddressed — every charm in the corpus targets an Ubuntu base.
- **The one review with no deployment** (`identity-saml-provider-operator.md`) is a
  reminder that this programme's evidentiary bar itself varies: 135 of 136 reviews are
  backed by a live deployment, but the process apparently permits a code-only review to be
  filed when deployment isn't attempted, without that being flagged in the file list
  itself — only readable by opening the file. A completeness convention (e.g. a required
  "Deployed: no" banner surfaced in an index) would make this easier to audit at scale.
