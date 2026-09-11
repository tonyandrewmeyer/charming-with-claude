# cos-proxy

A mature machine charm that bridges legacy LMA observability interfaces to Kubernetes-based COS: it aggregates Prometheus scrape targets, alert rules, Grafana dashboards, and NRPE checks from machine-model charms and forwards them via `downstream-prometheus-scrape`, `downstream-grafana-dashboard`, `downstream-logging`, or `cos-agent`. It ships its own `nrpe_exporter` and `vector` binaries and leans on stored state to amortise `relation-get` costs at scale.

The core reconciler (`MetricsEndpointAggregator`), status precedence, and integration tests are solid, but the charm has real operational holes: `config-changed` can crash into a cascading, manually-unrecoverable error loop when a downstream relation is stale relative to stored state; vector is never stopped or cleaned up on removal; a typo leaves a stale nrpe-exporter systemd unit file behind on teardown; and the published revision (170) cannot be deployed at all on Juju 4.0 due to a charm-store UUID bug. `forward_alert_rules=False` also silently fails to suppress alert rules pushed via `cos-agent`, contradicting its own config description. A maintainer should fix the config-changed crash first — it's the only finding that turns into unrecoverable state in production — then land vector cleanup and the `_on_stop` typo, then chase the Juju 4.0 deploy blocker with the Juju team.

On Juju 3.6, end-to-end integration (NRPE + grafana-agent via `cos-agent`) works cleanly, including relation removal/recovery and process-kill recovery within ~5s via systemd.

| | |
|---|---|
| Repo | canonical/cos-proxy-operator @ `64e6b81` (2026-07-13) |
| Charms | cos-proxy, monitors-provider, scrape-consumer |
| Substrate | machine |
| Deployed | yes — active on Juju 3.6.27 (concierge-lxd) via `3.0/edge` rev 170; failed to deploy on Juju 4.0.12 (concierge-lxd-4) due to a charm-store UUID parsing bug |
| Reviewed | 2026-08-12 |

## What it does

cos-proxy sits in a machine model and collects observability telemetry from legacy (LMA) charms via `requires` relations: `prometheus-target` (HTTP scrape targets), `prometheus-rules` (alert rules), `monitors` (NRPE checks), `general-info`, `dashboards` (Grafana dashboards), `prometheus` (prometheus-manual), and `filebeat` (elastic-beats logs). It provides downstream relations to COS: `downstream-prometheus-scrape`, `downstream-grafana-dashboard`, `downstream-logging` (via `loki_push_api`), `cos-agent` (Grafana Agent / OpenTelemetry Collector), and `filebeat`. It bundles `nrpe_exporter` (converts NRPE checks to Prometheus metrics on port 9275) and `vector` (log forwarding and host-metric export on port 9090). Config options: `forward_alert_rules` (bool, default true) and `nrpe_alert_on_warning` (bool, default false).

## Deployment log

### Deployment 1: concierge-lxd-4 (Juju 4.0.12) — FAILED

```
juju add-model rv-cosproxya -c concierge-lxd-4
juju deploy cos-proxy --channel 3.0/edge   # revision 170, ubuntu@24.04
# cos-proxy stuck at "agent initialising" indefinitely
# debug-log: ERROR failed to resolve charm download: parsing present uuid in metadata: id "": not valid
# asynccharmdownloader retries in a loop but never succeeds
# Same result with 3.0/stable (also rev 170)
# self-signed-certificates deployed fine on the same controller
```

This looks specific to cos-proxy rev 170 rather than Juju 4.0 in general — a normal charm deployed fine on the same controller.

### Deployment 2: concierge-lxd (Juju 3.6.27) — primary test model

```
juju add-model rv-cosproxyb -c concierge-lxd
juju deploy cos-proxy --channel 3.0/edge   # revision 170, ubuntu@24.04
# → blocked: "Add at least one incoming relation" (~2m)
juju deploy self-signed-certificates --channel 1/edge
juju deploy grafana-agent --channel 2/edge
juju deploy nrpe --channel latest/stable
# grafana-agent and nrpe are subordinates; need juju-info to deploy
juju relate grafana-agent:juju-info cos-proxy:juju-info
juju relate nrpe:general-info cos-proxy:juju-info
juju relate cos-proxy:monitors nrpe:monitors
# → cos-proxy: blocked "Missing ['cos-agent']|['downstream-prometheus-scrape'] for monitors"
juju relate cos-proxy:cos-agent grafana-agent:cos-agent
# → cos-proxy: active; grafana-agent remains blocked (needs cloud-config/send-remote-write)
#
# nrpe_exporter and vector installed automatically on monitors join:
#   nrpe-exporter :9275 (~11MB RSS), vector :9090/:5044/:8686 (~73MB RSS)
#
# vector logs an enrich-nrpe transform error on startup, before NRPE data arrives:
#   "all array items must be strings"
```

### Failure injection on rv-cosproxyb

```
# Kill and recovery:
lxc exec ... -- killall vector          # recovers in ~5s via systemd Restart=always
lxc exec ... -- killall nrpe-exporter   # recovers in ~5s

# Config changes:
juju config cos-proxy forward_alert_rules=false  # active, works
juju config cos-proxy forward_alert_rules=true   # active, works
juju config cos-proxy forward_alert_rules="not-a-bool"  # Juju rejects before charm sees it

# Relation removal + re-add:
juju remove-relation cos-proxy:monitors nrpe:monitors  # → blocked "Add at least one incoming relation"
# vector (~73MB RSS) and nrpe-exporter (~11MB RSS) both keep running — by design (vector never stops)
juju relate cos-proxy:monitors nrpe:monitors  # → active again, clean recovery

# Scale:
juju add-unit cos-proxy -n 1  # → unit/1 deploys, blocked (no cos-agent on machine 2)
juju remove-unit cos-proxy/1   # → clean teardown
```

### What could not be tested

* **Test charms** (`monitors-provider`, `scrape-consumer`): built for ubuntu@22.04; containers provision but Juju agents never install — infrastructure limitation, not a charm defect.
* **TLS / `receive-ca-cert`**: relation exists in repo HEAD (commit `3e063ae`) but is absent from published rev 170's `metadata.yaml`.
* **Juju 4.0**: cos-proxy rev 170 cannot deploy due to the charm-store UUID bug above.
* **`juju refresh`**: `3.0/stable` and `3.0/edge` are the same commit (`e6f880c`), differing only in base — no upgrade path exists to test.

## Observed behaviour

* **Deploy to blocked** (no relations): ~2m on Juju 3.6, no workload processes running — binaries are not installed until a relation triggers them.
* **Deploy to active** (monitors + cos-agent via NRPE + grafana-agent): ~5m, transiting blocked (no incoming) → blocked (missing outgoing) → active as relations join.
* **Charm size on disk**: nrpe_exporter 17MB, vector 125MB, total charm ~142MB — vector dominates.
* **Memory at idle** (active, NRPE + cos-agent, 3 NRPE checks): jujud unit agent ~130MB RSS, vector ~73MB RSS, nrpe-exporter ~11MB RSS; ~215MB RSS total on the host. Vector starts at ~45MB and grows to ~73MB.
* **`nrpe_exporter`**: listens on port 9275, exposes Go runtime metrics; binary at `/usr/local/bin/nrpe-exporter` (`src/charm.py:429`), compiled with Go 1.16.4.
* **`vector` v0.44.0**: listens on `:9090` (Prometheus metrics via host_metrics + internal_metrics), `:5044` (logstash TCP), `:8686` (Vector API); exposes 1,798 Prometheus metrics. Enrichment file at `/etc/vector/nrpe_lookup.csv` is populated with NRPE check details.
* **vector enrich-nrpe transform error**: on startup, before NRPE data arrives, vector logs `"all array items must be strings"` from the `enrich-nrpe` remap transform (journald `fields.address` arrives as a non-string type). Rate-limited after the first occurrence and does not prevent forwarding once real NRPE data arrives.
* **Binaries installed on relation join**: `_setup_nrpe_exporter()` runs on `monitors_relation_joined` or `general_info_relation_joined`; `_start_vector()` runs on those plus `filebeat_relation_joined`. Until then `/usr/local/bin/` is empty and no systemd services run.
* **rsyslog removal**: `_on_install` removes the `rsyslog` package to prevent disk fill. Confirmed: rsyslog left in `rc` (removed, config retained) state.
* **Config-changed hook count**: a single `config-changed` hook fires per change; `_set_status` runs on `collect_unit_status`, so hooks stay minimal when nothing is broken.
* **Vector started but never stopped**: once started, vector runs forever, even after the relations that triggered it are removed. `src/charm.py:718` explicitly acknowledges: "NOTE: We never stop vector once started." Removing the monitors relation leaves both vector and nrpe-exporter running.
* **Recovery from process kill**: vector and nrpe-exporter both restart within ~5s via systemd `Restart=always` (`Type=exec`).
* **Status messages**: informative — "Add at least one incoming relation" and the `MandatoryRelationPairs` output ("Missing ['cos-agent']|['downstream-prometheus-scrape'] for monitors") are both actionable. Blocked status correctly toggles between the two depending on which side is missing.
* **Relation lifecycle**: removing the only incoming relation correctly sets blocked; re-adding restores active within one hook cycle. Both subordinates (NRPE, grafana-agent) deploy correctly on cos-proxy's machine.
* **NRPE subordinate deployment quirk**: NRPE is a subordinate requiring `juju-info` to deploy onto a machine; cos-proxy's docs don't mention this, so an operator deploying NRPE alone would see 0 units and no progress.
* **Juju 3.6 vs 4.0**: deployment succeeds on 3.6, fails outright on 4.0 (charm-store UUID bug above). A previously-reported Juju 4.0 `config-changed` crash with `ModelError: permission denied` on stale relations could not be re-confirmed here since the charm cannot even deploy on 4.0 — noted as `(unverified)` on 4.0 specifically, though the same class of crash was reproduced independently on 3.6 (see Findings).
* **No actions defined**: no way for an operator to manually trigger reconciliation, inspect state, or force a re-sync.
* **`receive-ca-cert` relation**: present in repo `charmcraft.yaml:129` (added in commit `3e063ae`, charm tracing support) but absent from published rev 170's `metadata.yaml`, confirmed via `juju show-application cos-proxy` showing no such binding.

## Findings

### `config-changed` can crash into a cascading, unrecoverable error loop when a downstream relation is stale

- **Severity**: critical
- **Kind**: bug
- **Where**: `src/metrics_endpoint_aggregator.py:198-201` (and the same pattern at lines 303, 373, 443, 512, 584, 612)
- **Evidence**:
  ```python
  # metrics_endpoint_aggregator.py:198-201
  else:
      relations = self.model.relations[self._prometheus_relation]
  for rel in relations:
      rel.data[self._charm.app]["scrape_jobs"] = json.dumps(jobs)
  ```
  `config-changed` → `update_alerts` → `_set_prometheus_rel_data_from_stored_state` iterates `self.model.relations["downstream-prometheus-scrape"]` and writes to `rel.data[self._charm.app]` with no guard. If the remote side has never joined or has departed, `relation-get`/`relation-set` returns non-zero and ops raises an uncaught `ModelError("ERROR permission denied (unauthorized access)")`.
- **Impact**: On the observed environment this produced a cascading failure: `config-changed` crashes, `juju resolve` retriggers it, it crashes again, and subsequent hooks sharing the same code path (e.g. `cos-agent-relation-joined` via `COSAgentProvider` refresh events) also fail. The unit enters an error loop that required manual model destruction to clear. An operator who relates a downstream charm that hasn't finished deploying, then changes config, can brick the unit.
- **Fix**: guard relation-data access, e.g.:
  ```python
  for rel in relations:
      if not rel.units:  # remote side hasn't joined
          continue
      try:
          rel.data[self._charm.app]["scrape_jobs"] = json.dumps(jobs)
      except ops.model.ModelError:
          logger.warning("Cannot write to relation %s", rel.id)
  ```
  Apply the same fix at the other five call sites listed above.
- **Linter rule**: flag `for rel in model.relations[X]: rel.data[...]` without a preceding `can_connect`-style guard or surrounding try/except `ModelError`.

### Cannot deploy on Juju 4.0: charm-store UUID parsing bug

- **Severity**: high
- **Kind**: bug
- **Where**: not in this repo — observed on Juju 4.0.12 deploying `cos-proxy` rev 170
- **Evidence**:
  ```
  ERROR juju.worker.asynccharmdownloader failed to resolve charm download:
    putting charm: putting blob and check hash: adding path ... :
    parsing present uuid in metadata: id "": not valid
  ```
  Reproduced with both `3.0/edge` and `3.0/stable` (same rev 170). `self-signed-certificates` deployed fine on the same controller, so this is specific to cos-proxy's published artifact or its interaction with the Juju 4.0 charm-store client, not a blanket Juju 4.0 incompatibility.
- **Impact**: operators on Juju 4.0 cannot deploy the published cos-proxy at all, despite the charm claiming `juju >= 3.6` support.
- **Fix**: investigate the charm-store UUID mismatch in the published artifact vs. Juju 4.0's asynccharmdownloader. Workaround: `charmcraft pack` + `juju deploy ./local.charm` (packing took 5+ minutes in this test).
- **Linter rule**: not mechanically checkable in the charm source — release/publish pipeline issue.

### Typo in `_on_stop` leaves a stale nrpe-exporter systemd unit file behind

- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:429`
- **Evidence**:
  ```python
  files = ["/usr/local/bin/nrpe-exporter", "/etc/systemd/systemd/nrpe-exporter.service"]
  ```
  The path written at install (`src/charm.py:483`) is `/etc/systemd/system/nrpe-exporter.service`; the stop handler targets `systemd/systemd/`, a typo.
- **Impact**: on `juju remove-application`, the binary is removed and the service stopped, but the real unit file at `/etc/systemd/system/nrpe-exporter.service` persists on the host.
- **Fix**: change the stop-handler path to `/etc/systemd/system/nrpe-exporter.service`.
- **Linter rule**: flag path-string mismatches between symmetrical install/cleanup blocks.

### Vector is never stopped or cleaned up on charm removal

- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:424-433` (missing cleanup), `src/charm.py:542` (service install), `src/charm.py:718` (comment)
- **Evidence**: `_on_stop` only handles nrpe-exporter. Vector is entirely absent from cleanup — no `service_stop("vector.service")`, no removal of `/usr/local/bin/vector`, `/etc/systemd/system/vector.service`, `/etc/vector/`, or `/var/lib/vector/`. The code says so explicitly:
  ```python
  # src/charm.py:718
  # NOTE: We never stop vector once started.
  ```
  Confirmed live: removing the `monitors` relation left both vector (~73MB RSS) and nrpe-exporter (~11MB RSS) running.
- **Impact**: on charm removal the vector process (and 125MB binary) remains on disk and running indefinitely. In a fan-in deployment with many cos-proxy units this is a real resource leak.
- **Fix**: add vector cleanup to `_on_stop` — stop the service, remove the binary, service file, and data/config directories.
- **Linter rule**: flag a systemd service installed in one handler with no corresponding stop/removal in `_on_stop`/`on.remove`.

### `forward_alert_rules=False` does not suppress `cos-agent`'s own built-in alert rules

- **Severity**: medium
- **Kind**: bug
- **Where**: `lib/charms/grafana_agent/v0/cos_agent.py:726-742`
- **Evidence**:
  ```python
  alert_rules.add_path(self._metrics_rules, recursive=self._recursive)  # always runs
  alert_rules.add(generic_alert_groups.application_rules, ...)          # always runs
  rules["groups"] = _dedupe_list(rules["groups"] + alert_rules.as_dict()["groups"])
  ```
  The charm's `_get_stored_alert_groups` correctly returns `{"groups": []}` when `forward_alert_rules` is False, but `COSAgentProvider` independently loads `src/prometheus_alert_rules/vector_restarted.rule` and generic alert rules regardless. Confirms open issue #220.
- **Impact**: an operator setting `forward_alert_rules=false` to stop rule forwarding still gets rules forwarded via the `cos-agent` path — the config only controls the `downstream-prometheus-scrape` path. Doc/reality mismatch.
- **Fix**: either wire `forward_alert_rules` through to `COSAgentProvider`, or document explicitly that the option only affects `downstream-prometheus-scrape`.
- **Linter rule**: not mechanically checkable — requires semantic understanding of config options.

### `_modify_enrichment_file` vulnerable to `StopIteration` on malformed endpoint data

- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:572-581`, `src/charm.py:595-599`
- **Evidence**:
  ```python
  # 572-573
  target = (
      f"{endpoint['target'][next(iter(endpoint['target']))]['hostname']}_"
      + f"{endpoint['additional_fields']['updates']['params']['command'][0]}"
  )
  # 577-581
  unit_name = next(
      filter(lambda d: "target_label" in d and d["target_label"] == "juju_unit",
             endpoint["additional_fields"]["relabel_configs"]),
  )["replacement"]
  # 595-599
  unit = next(iter([c["replacement"] for c in endpoint["additional_fields"]["relabel_configs"]
                     if c["target_label"] == "juju_unit"]))
  ```
  None of these `next()` calls have a default; all raise `StopIteration` on an empty container. NRPE always generates well-formed data, but a malformed `monitors` relation from a third-party charm would crash the reconciler.
- **Impact**: a single malformed relation data bag could crash `_on_nrpe_targets_changed` → `_modify_enrichment_file`, blocking all NRPE processing until the bad relation is removed.
- **Fix**: use `next(..., default=None)` with explicit None checks and warning logs; consider a helper that safely navigates the nested dict path.
- **Linter rule**: flag `next()` called without a default on a generator/iterator (partially mechanical).

### No `upgrade_charm` handler: binary updates deferred until the next relation event

- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py` (handler absent)
- **Evidence**: only `install`, `stop`, and `collect_unit_status` are observed:
  ```python
  self.framework.observe(self.on.install, self._on_install)
  self.framework.observe(self.on.stop, self._on_stop)
  self.framework.observe(self.on.collect_unit_status, self._set_status)
  ```
  `_setup_nrpe_exporter`/`_start_vector` only run from relation-joined hooks (`monitors`, `general-info`, `filebeat`).
- **Impact**: on `juju refresh`, new charm code deploys but old binaries keep running until a relation event fires — a charm with no active relations never updates its binaries.
- **Fix**: add an `_on_upgrade_charm` handler that checks installed binary versions against what the charm ships, and re-runs `_setup_nrpe_exporter()`/`_start_vector()` if relations already exist.
- **Linter rule**: flag charms that install binaries only from relation hooks with no `upgrade_charm` handler.

### `StoredState` used as source of truth for relation existence can go stale

- **Severity**: medium
- **Kind**: bug
- **Where**: `src/charm.py:738-755`
- **Evidence**: `_set_status` builds `active_relations` from `self._stored.have_*` booleans rather than checking `self.model.relations`, per a comment explaining this is for performance (open issues #56, #203). The crash in the "config-changed cascading failure" finding above shows stored state can drift from reality once a relation is removed.
- **Impact**: any hook that decides whether to touch relation data based on stored flags rather than live relation state is exposed to the same class of crash, not just the one code path already confirmed.
- **Fix**: reconcile stored state against actual relations at least on `upgrade_charm` and in `_set_status`; `relation-list` is cheap even though `relation-get` (triggered by accessing `relation.data`) is the expensive call the current design is avoiding.
- **Linter rule**: not mechanically checkable.

### Constant alert rules added twice per reconciliation via in-place-mutate-then-extend

- **Severity**: low
- **Kind**: bug
- **Where**: `src/metrics_endpoint_aggregator.py:240` (caller), `:210-226` (callee)
- **Evidence**:
  ```python
  groups = [] + _type_convert_stored(self._stored.alert_rules)
  groups.extend(self._add_constant_alerts(groups))  # line 242
  ```
  ```python
  def _add_constant_alerts(self, groups):
      groups.extend(alert_rules.as_dict()["groups"])  # mutates in place, line 224
      return groups                                    # returns same object, line 226
  ```
  The callee mutates `groups` in place and returns it; the caller then extends that return value into the same list, appending constant alerts twice. `_dedupe_list` (line 249) masks the duplication, so there is no user-visible bug today.
- **Impact**: wasted work each reconciliation, and a latent correctness bug if `_dedupe_list` is ever removed or refactored.
- **Fix**: don't mutate the argument — `return groups + alert_rules.as_dict()["groups"]`, and reassign at the call site: `groups = self._add_constant_alerts(groups)`.
- **Linter rule**: flag a function that both mutates a list argument in place and returns it.

### Unsorted iteration over `event.certificates` (a set) produces non-deterministic on-disk content

- **Severity**: low
- **Kind**: bug
- **Where**: `src/charm.py:345`
- **Evidence**:
  ```python
  certs = "\n\n".join(event.certificates)
  CA_CERT_PATH.write_text(certs + "\n")
  ```
  `event.certificates` is `Set[str]` (`lib/charms/certificate_transfer_interface/v1/certificate_transfer.py:508`); iterating a set is non-deterministic. Matches open issue #245.
- **Impact**: unnecessary file churn on every write, which can trigger spurious downstream re-reads if anything watches the CA cert file for changes.
- **Fix**: `certs = "\n\n".join(sorted(event.certificates))`.
- **Linter rule**: flag unsorted iteration over a set used to build file/serialized output (mechanically checkable, e.g. flaplint).

### `_write_vector_config` collects `loki_endpoints` but never uses them

- **Severity**: low
- **Kind**: bug
- **Where**: `src/charm.py:630-636`
- **Evidence**:
  ```python
  loki_endpoints = []
  for relation in self.model.relations["downstream-logging"]:
      if not relation.units:
          continue
      for unit in relation.units:
          if endpoint := relation.data[unit].get("endpoint", ""):
              loki_endpoints.append(json.loads(endpoint)["url"])
  config = self.vector.config
  ```
  `loki_endpoints` is never passed anywhere; the actual Loki sink config comes from `VectorProvider.config` (`src/vector.py:169`), which independently iterates the same relations.
- **Impact**: wasted work on every vector config write; minor.
- **Fix**: remove the dead code block.
- **Linter rule**: unused-variable check (ruff catches simple cases; may miss this one at function scope).

### Charm ships a very large vector binary (125MB) inside the package

- **Severity**: low
- **Kind**: performance
- **Where**: `charmcraft.yaml:49-58`
- **Evidence**: vector is downloaded at build time and embedded via the `dump` plugin, producing a ~142MB total charm. Open issue #222.
- **Impact**: slower deploys / more bandwidth, noticeable on slow networks or with many units.
- **Fix**: consider downloading vector at runtime (as `_setup_nrpe_exporter` already does) or shipping it as a resource/snap. nrpe_exporter at 17MB is more reasonable.
- **Linter rule**: flag charm packages exceeding a size threshold (mechanically checkable).

### Unit tests use deprecated `ops.testing.Harness`

- **Severity**: low
- **Kind**: lint
- **Where**: `tests/unit/test_charm.py:195`, `tests/unit/test_endpoint_aggregator.py:135`, and others
- **Evidence**: multiple test files still use `Harness`, deprecated in ops 2.x in favor of the Scenario `State`/`Context` API; `test_alerts.py` and `test_charm_scenario.py` already use Scenario.
- **Impact**: `Harness` will eventually be removed; these tests will break.
- **Fix**: migrate remaining `Harness`-based tests to Scenario.
- **Linter rule**: flag use of deprecated `Harness` (ruff can catch this).

### `receive-ca-cert` relation exists in HEAD but is absent from the published `metadata.yaml`

- **Severity**: low
- **Kind**: bug
- **Where**: `charmcraft.yaml:129` (repo HEAD) vs. deployed `metadata.yaml` (rev 170)
- **Evidence**: `charmcraft.yaml` declares `receive-ca-cert` (interface `certificate_transfer`), added in commit `3e063ae` ("feat: add charm tracing support"). Published rev 170 (commit `e6f880c`) has no such relation; confirmed via `juju show-application cos-proxy` showing no such binding.
- **Impact**: the tracing/CA-cert-transfer code path (`_on_cert_transfer_available`, `src/charm.py:342`) exists but is unreachable in the published charm; operators on the edge channel cannot use it.
- **Fix**: release a new revision that includes the relation — a release-process fix, not a code fix.
- **Linter rule**: flag relations declared in `charmcraft.yaml` but missing from the published charm's `metadata.yaml`.

### Pydantic V2 deprecation warnings in `cos_agent.py`

- **Severity**: low
- **Kind**: lint
- **Where**: `lib/charms/grafana_agent/v0/cos_agent.py:690` (`.json()`), `:430` (`.__fields__`)
- **Evidence**:
  ```python
  relation.data[self._charm.unit][data.KEY] = data.json()          # line 690, deprecated
  if k in {(f.alias or n) for n, f in cls.__fields__.items()}       # line 430, deprecated
  ```
  72 warnings surface in the unit test suite from this; `__fields__` fires on every cos-agent data validation, `.json()` on every relation write.
- **Impact**: when Pydantic V3 removes these attributes, the cos-agent integration breaks outright.
- **Fix**: update the vendored `cos_agent` library to use `model_dump_json()` and `model_fields`. Tracked in open issue #236.
- **Linter rule**: flag deprecated Pydantic V2 attribute/method usage (ruff PYD001/PYD002).

### Ambiguous `requires-python = "~=3.8"` specifier

- **Severity**: low
- **Kind**: lint
- **Where**: `pyproject.toml:5`
- **Evidence**: `requires-python = "~=3.8"`. `uv` warns this is interpreted as `>=3.8, <4`, not "3.8.x only". The test environment actually runs Python 3.14.
- **Impact**: confusing for anyone reading the pin as a strict 3.8 requirement.
- **Fix**: change to `>=3.8` (explicit intent) or pin a specific minor version if 3.8 is actually required.
- **Linter rule**: flag ambiguous tilde specifiers without a patch version (mechanically checkable via `pyproject.toml` parsing).

### `vector` enrich-nrpe transform logs errors on startup before NRPE data arrives

- **Severity**: low
- **Kind**: bug
- **Where**: `src/vector.py:87-108` (VRL transform); observed in systemd logs
- **Evidence**:
  ```
  ERROR transform enrich-nrpe: Mapping failed with event.
  error="function call error for \"join\" at (65:109): all array items must be strings"
  ```
  The `enrich-nrpe` transform calls `join!([fields.address, "_", fields.command])`, but `fields.address` from journald sometimes arrives as a non-string type. Rate-limited after the first occurrence (`internal_log_rate_limit=true`); cosmetic once real NRPE data populates the enrichment table.
- **Impact**: benign in steady state, but if this error event itself gets log-forwarded it adds noise to Loki.
- **Fix**: coerce the type before `join!`, e.g. `address = to_string!(fields.address) ?? "unknown"`, or guard against non-string `fields.address`.
- **Linter rule**: not mechanically checkable — requires semantic understanding of VRL.

## Worth copying

1. **Clean reconciler with `ScrapeJobContext`/`AlertRuleContext`** (`src/metrics_endpoint_aggregator.py:590-680`): `set_target_job_and_alert_rule_data_batch` uses dataclass-based contexts to apply batched additions/removals to relation data, avoiding O(n²) rebuilds when multiple NRPE targets change.
2. **`MandatoryRelationPairs` for status messages** (`deps/cosl/mandatory_relation_pairs.py`): declares incoming→outgoing relation requirements and produces human-readable status like `"Missing ['cos-agent']|['downstream-prometheus-scrape'] for monitors"`. Reusable across charms with paired relation requirements.
3. **Well-structured integration tests with retries** (`tests/integration/`): `tenacity` retry decorators for eventual consistency, specific assertions on alert rule content and trace propagation across real charms (telegraf → cos-proxy → opentelemetry-collector), including relation removal. `test_charm_tracing.py` triggers `update-status` hooks and asserts traces appear in collector logs.
4. **`_reconcile_charm_tracing`** (`src/charm.py:318-327`): called from multiple hooks and idempotent — returns early if no endpoint is available. Clean pattern for scattered tracing setup.
5. **`collect_unit_status` for performance** (`src/charm.py:735`): the stored-state-vs-real-time tradeoff is explicit and documented in a comment.
6. **`pyproject.toml` exclusions are explained**: `vector.py` is excluded from pyright with a comment about `$` interpolation in YAML templates — most projects exclude files with no explanation at all.

## Common-practice notes

* **Library versioning**: all `lib/charms/` libraries follow the standard `v<N>/` convention. Embedded `nrpe_exporter.py`/`vector.py` in `src/` use `LIBID = "0xdeadbeef"` (not real charm libraries, not on charmhub) — fine for internal modules.
* **`charmcraft.yaml` layout**: uses the `uv` plugin with `build-snaps: [astral-uv]`, and separate `parts` for charm/nrpe-exporter/vector with custom `override-pull` for binary downloads. `platforms` covers `ubuntu@20.04/22.04/24.04:amd64` — wide, though 20.04 is EOL for standard support.
* **`src/` layout**: `charm.py` is ~800 lines; `metrics_endpoint_aggregator.py` is ~700 lines, a forked and significantly modified copy of a charm library (moved out of `charms.prometheus_k8s.v0.prometheus_scrape` because the fork diverged too much from upstream, per code comment).
* **`pyproject.toml` caution**: `requires-python = "~=3.8"` is ambiguous; pins on `markupsafe==2.0.1` and `jinja2<3` are old transitive dependencies from older charm libraries.
* **Dual-path architecture**: the charm supports both direct downstream relations and `cos-agent`. README/INTEGRATING.md both recommend `cos-agent` when possible, but the charm must still support both — the `forward_alert_rules` discrepancy above is a direct consequence of that complexity.
* **`justfile` integration**: uses `just` with an imported `charms.just` file — standardised tooling.

## Tests

* **Unit tests**: 57/57 passing (0.98s). Mix of `Harness` (deprecated) and Scenario tests.
  ```
  PYTHONPATH=.:lib:src uv run --frozen --isolated --extra=dev pytest tests/unit -v
  ```
  72 warnings: 42 from deprecated `Harness` usage, 28 from Pydantic V2 deprecations in `cos_agent.py`, 2 scenario runtime warnings about unset remote unit IDs. Two tests (`test_cos_agent_with_downstream_prometheus`, `test_only_cos_agent`) log INFO-level cos-agent relation-data validation failures — expected given an empty databag during setup, non-fatal.

  Coverage (`coverage run --source=src -m pytest tests/unit`):
  | Module | Coverage |
  |---|---|
  | `charm.py` | 65% (`_on_stop`, `_on_install`, vector config, cert transfer, dashboard file ops uncovered) |
  | `metrics_endpoint_aggregator.py` | 90% |
  | `nrpe_exporter.py` | 76% |
  | `scrape_config.py` | 100% |
  | `vector.py` | 51% (`config` property, `DEFAULT_VECTOR_CONFIG`, relation change handlers uncovered) |
  | **Overall** | **77%** |

* **Coverage gaps** map directly onto findings above:
  * `_on_stop` (0%, lines 424-433) — the `_on_stop` typo has no test coverage.
  * `_on_install` (0%, lines 420-422) — rsyslog removal and workload version setting untested.
  * `_modify_enrichment_file` (0% branch coverage) — the `StopIteration` risk has no malformed-data test.
  * `_write_vector_config` — the dead `loki_endpoints` code path is untested.
  * `_on_cert_transfer_*` handlers — certificate non-determinism untested; cert transfer only covered by `test_cert_transfer_writes_certificates`.
  * `_on_upgrade_charm` — doesn't exist, so untestable.
  * `nrpe_alert_on_warning` — referenced correctly at `nrpe_exporter.py:474` but has no dedicated end-to-end test.

* **Lint**:
  * `ruff`: 7 errors, all in vendored `lib/charms/...` libraries, none in `src/`. 6 auto-fixable (RET505, I001), 1 docstring issue (D417).
  * `pyright`: 0 errors, 0 warnings (`src/vector.py` excluded — see Open questions).
  * `codespell`: 3 minor issues — `fpr`→`for` in `apt.py:1189-1190`, `dependant`→`dependent` in `metrics_endpoint_aggregator.py:212`.

* **Integration tests** (`tests/integration/`, using `jubilant` + `pytest-bdd` + `tenacity`):
  * `test_alert_rules.py` — deploys telegraf → cos-proxy → opentelemetry-collector; tests alert rule propagation and `forward_alert_rules` toggle.
  * `test_scrape_jobs.py` — scrape job propagation and removal.
  * `test_charm_tracing.py` — end-to-end charm tracing with collector log inspection.
  * Go beyond status checks — assert rule content, log patterns, config file absence. Could not be run on this infrastructure (require `charmcraft pack`, ubuntu@22.04 telegraf, and possibly k8s for opentelemetry-collector).

* **Manual test charms**: `monitors-provider`/`scrape-consumer` in `tests/manual/charms/` are focused test doubles (emit configurable NRPE monitor data / display received scrape jobs and alert rules). Useful for manual/benchmark testing but not wired into CI. `tests/manual/juju_monitors_benchmark.py` benchmarks the monitors fan-in pattern at scale.

## Docs

* **README.md**: comprehensive, with concrete `juju` commands, cross-model relation examples, and a full status-output example. A new operator could follow it successfully.
* **INTEGRATING.md**: mermaid diagrams for two topologies; states clearly that cos-proxy is transitional and `grafana-agent` is preferred; references `tests/manual/topologies/README.md` for exportable bundles.
* **Charmhub description** (`charmcraft.yaml`): good summary and feature list, links to the docs site.
* **Docs/reality mismatches**:
  * `forward_alert_rules` is described as "Toggle forwarding of alert rules" with no qualification, but it only affects the `downstream-prometheus-scrape` path (see Findings).
  * README doesn't mention the ~142MB charm size or the ~125MB vector binary.

## Open questions

1. Why is vector pinned to v0.44.0 (Jan 2025) when newer releases exist? Open issue #222.
2. Does `_modify_enrichment_file`'s dedup handle the composite-key duplication from issue #60? It filters `(composite_key, juju_unit)` against current targets but doesn't dedupe historical CSV entries sharing the same key — apparently still open.
3. Why is `src/vector.py` excluded from pyright entirely (`pyproject.toml:101`)? The stated reason is `$` interpolation in YAML templates, but excluding the whole file also hides real type errors in `VectorProvider`.
4. Is the missing `upgrade_charm` handler worth fixing now, or is it acceptable given expected relate/dissolve refresh workflows?
5. Is the Juju 4.0 charm-store UUID bug in the cos-proxy artifact or in Juju itself? Other charms deploy fine on the same controller — needs investigation on the Juju side.
6. Does `nrpe_alert_on_warning` work end-to-end? It correctly flips `>` to `>=` in the alert expression at `nrpe_exporter.py:474`, but there's no integration test asserting the resulting rule content.
7. Are the old `markupsafe==2.0.1`/`jinja2<3` pins in `pyproject.toml` still required, or vestigial from older charm libraries?
