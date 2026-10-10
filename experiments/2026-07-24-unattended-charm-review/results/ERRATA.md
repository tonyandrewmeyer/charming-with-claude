# Second-reader errata — corpus audit 2026-08-30

Every finding in the corpus re-read against the source it cites. This asks one
question only — *does the cited code support the claim* — and deliberately not
whether the review found everything it should have. Judged from the cited
excerpts alone, with no other access to the repository, so a finding whose
excerpt could not settle the point is marked `unverifiable` rather than guessed.


**136 reviews adjudicated, 2414 findings.**

| verdict | findings | share |
|---|---:|---:|
| supported | 1226 | 50.8% |
| contradicted | 34 | 1.4% |
| miscited | 184 | 7.6% |
| runtime | 257 | 10.6% |
| unverifiable | 713 | 29.5% |

## Reviews ranked by adjudicated errors

| repo | findings | contradicted | miscited | runtime | unverifiable |
|---|---:|---:|---:|---:|---:|
| superset-k8s-operator | 20 | 0 | 9 | 0 | 4 |
| kubeflow-dashboard-operator | 33 | 2 | 5 | 4 | 9 |
| discourse-k8s-operator | 21 | 0 | 6 | 1 | 4 |
| catalogue-k8s-operator | 15 | 2 | 3 | 1 | 0 |
| charmed-etcd-operator | 8 | 0 | 5 | 0 | 2 |
| kafka-operator | 15 | 2 | 3 | 1 | 3 |
| zookeeper-k8s-operator | 15 | 0 | 5 | 1 | 2 |
| zookeeper-operator | 24 | 2 | 3 | 2 | 5 |
| authentik-worker-operator | 13 | 0 | 4 | 1 | 5 |
| mysql-operators | 18 | 0 | 4 | 4 | 6 |
| ranger-k8s-operator | 19 | 2 | 2 | 2 | 3 |
| resource-dispatcher | 20 | 0 | 4 | 5 | 9 |
| script-exporter-operator | 21 | 3 | 1 | 3 | 6 |
| airbyte-k8s-operator | 20 | 1 | 2 | 0 | 8 |
| alertmanager-k8s-operator | 26 | 1 | 2 | 1 | 11 |
| blackbox-exporter-operator | 17 | 0 | 3 | 0 | 7 |
| cassandra-operator | 14 | 0 | 3 | 3 | 3 |
| cos-coordinated-workers | 24 | 0 | 3 | 5 | 4 |
| cos-registration-server-k8s-operator | 21 | 0 | 3 | 1 | 4 |
| feast-operators | 28 | 0 | 3 | 0 | 17 |
| grafana-k8s-operator | 23 | 0 | 3 | 0 | 7 |
| identity-platform-admin-ui-operator | 19 | 2 | 1 | 4 | 4 |
| kiali-k8s-operator | 18 | 0 | 3 | 2 | 7 |
| sysbench-operator | 20 | 0 | 3 | 1 | 9 |
| testflinger | 34 | 0 | 3 | 1 | 14 |
| vault-k8s-operator | 13 | 0 | 3 | 4 | 3 |
| wordpress-k8s-operator | 12 | 0 | 3 | 0 | 1 |
| airflow-coordinator-k8s-operator | 13 | 1 | 1 | 1 | 3 |
| authentik-ldap-outpost-operator | 20 | 1 | 1 | 0 | 4 |
| authentik-server-operator | 15 | 0 | 2 | 1 | 4 |
| charm-microceph | 16 | 0 | 2 | 2 | 3 |
| charm-rabbitmq-k8s | 9 | 0 | 2 | 0 | 1 |
| charmed-canonical-cla | 19 | 0 | 2 | 2 | 1 |
| cos-proxy-operator | 17 | 0 | 2 | 3 | 1 |
| envoy-operator | 21 | 1 | 1 | 1 | 13 |
| falco-operators | 22 | 0 | 2 | 3 | 7 |
| gatus-k8s-operator | 15 | 0 | 2 | 1 | 5 |
| grafana-agent-k8s-operator | 12 | 0 | 2 | 0 | 1 |
| hydra-operator | 22 | 0 | 2 | 0 | 6 |
| identity-saml-provider-operator | 5 | 0 | 2 | 0 | 1 |
| istio-beacon-k8s-operator | 23 | 0 | 2 | 5 | 6 |
| istio-ingress-k8s-operator | 19 | 0 | 2 | 1 | 7 |
| jenkins-k8s-operator | 15 | 0 | 2 | 2 | 8 |
| karapace-k8s-operator | 20 | 0 | 2 | 5 | 2 |
| kfp-operators | 12 | 0 | 2 | 0 | 6 |
| kratos-operator | 14 | 0 | 2 | 0 | 7 |
| kserve-operators | 20 | 2 | 0 | 6 | 6 |
| kubeflow-profiles-operator | 19 | 1 | 1 | 3 | 1 |
| kyuubi-k8s-operator | 13 | 0 | 2 | 1 | 1 |
| litmus-operators | 24 | 0 | 2 | 1 | 5 |
| mlflow-operator | 13 | 0 | 2 | 1 | 3 |
| notary-k8s-operator | 10 | 0 | 2 | 2 | 2 |
| parca-k8s-operator | 16 | 0 | 2 | 4 | 0 |
| parca-scrape-target-operator | 12 | 1 | 1 | 1 | 0 |
| pgbouncer-operator | 13 | 0 | 2 | 1 | 1 |
| postgresql-k8s-operator | 24 | 0 | 2 | 6 | 8 |
| self-signed-certificates-operator | 9 | 0 | 2 | 3 | 1 |
| sloth-k8s-operator | 15 | 2 | 0 | 1 | 2 |
| tempo-operators | 14 | 0 | 2 | 4 | 3 |
| test_observer | 14 | 0 | 2 | 0 | 5 |
| traefik-k8s-operator | 16 | 0 | 2 | 0 | 0 |
| wazuh-server-operator | 18 | 0 | 2 | 1 | 4 |
| blackbox-exporter-k8s-operator | 21 | 0 | 1 | 2 | 3 |
| cos-configuration-k8s-operator | 20 | 0 | 1 | 3 | 6 |
| data-integrator | 23 | 0 | 1 | 3 | 7 |
| glauth-k8s-operator | 17 | 0 | 1 | 4 | 2 |
| grafana-agent-operator | 16 | 0 | 1 | 5 | 0 |
| hive-metastore-k8s-operator | 24 | 1 | 0 | 1 | 10 |
| hook-service-operator | 19 | 0 | 1 | 0 | 2 |
| jenkins-agent-k8s-operator | 10 | 1 | 0 | 1 | 4 |
| k6-k8s-operator | 13 | 0 | 1 | 2 | 2 |
| kafka-benchmark-operator | 26 | 0 | 1 | 4 | 4 |
| kafka-connect-k8s-operator | 12 | 0 | 1 | 2 | 4 |
| kafka-connect-operator | 23 | 0 | 1 | 2 | 7 |
| kafka-k8s-operator | 22 | 0 | 1 | 2 | 6 |
| kafka-ui-k8s-operator | 22 | 0 | 1 | 2 | 3 |
| kubeflow-volumes-operator | 16 | 0 | 1 | 2 | 8 |
| livepatch-k8s-operator | 24 | 1 | 0 | 1 | 8 |
| maas-site-manager-k8s-operator | 25 | 0 | 1 | 3 | 3 |
| mediawiki-k8s-operator | 18 | 1 | 0 | 4 | 8 |
| notebook-operators | 19 | 0 | 1 | 3 | 4 |
| oathkeeper-operator | 23 | 0 | 1 | 4 | 5 |
| oidc-gatekeeper-operator | 19 | 0 | 1 | 3 | 7 |
| opentelemetry-collector-integrator-operator | 14 | 0 | 1 | 1 | 4 |
| opentelemetry-collector-k8s-operator | 12 | 1 | 0 | 1 | 2 |
| otel-ebpf-profiler-operator | 13 | 0 | 1 | 2 | 2 |
| prometheus-k8s-operator | 18 | 1 | 0 | 4 | 3 |
| prometheus-pushgateway-k8s-operator | 19 | 0 | 1 | 3 | 5 |
| prometheus-scrape-config-k8s-operator | 18 | 0 | 1 | 2 | 3 |
| pyroscope-operators | 12 | 0 | 1 | 4 | 4 |
| snmp-exporter-operator | 17 | 0 | 1 | 1 | 3 |
| spark-history-server-k8s-operator | 22 | 0 | 1 | 2 | 8 |
| spark-integration-hub-k8s-operator | 18 | 0 | 1 | 4 | 1 |
| sunbeam-charms | 19 | 0 | 1 | 0 | 7 |
| temporal-admin-k8s-operator | 26 | 0 | 1 | 2 | 8 |
| temporal-k8s-operator | 15 | 0 | 1 | 1 | 4 |
| temporal-ui-k8s-operator | 20 | 0 | 1 | 0 | 6 |
| temporal-worker-k8s-operator | 15 | 0 | 1 | 1 | 6 |
| tenant-service-operator | 23 | 1 | 0 | 1 | 6 |
| ubuntu-insights-k8s-operator | 18 | 1 | 0 | 1 | 4 |
| user-verification-service-operator | 15 | 0 | 1 | 0 | 4 |
| airflow-core-operators | 19 | 0 | 0 | 0 | 10 |
| content-cache-k8s-operator | 18 | 0 | 0 | 1 | 6 |
| datahub-k8s-operator | 10 | 0 | 0 | 1 | 3 |
| dex-auth-operator | 8 | 0 | 0 | 0 | 3 |
| forgejo-k8s-operator | 15 | 0 | 0 | 3 | 4 |
| github-runner-operator | 20 | 0 | 0 | 2 | 6 |
| grafana-cloud-integrator | 19 | 0 | 0 | 3 | 5 |
| identity-platform-login-ui-operator | 26 | 0 | 0 | 1 | 14 |
| istio-k8s-operator | 14 | 0 | 0 | 5 | 3 |
| jimm-k8s-operator | 32 | 0 | 0 | 4 | 12 |
| karapace-operator | 20 | 0 | 0 | 4 | 2 |
| katib-operators | 19 | 0 | 0 | 0 | 13 |
| kubeflow-tensorboards-operator | 19 | 0 | 0 | 2 | 17 |
| landscape-debarchive-operator | 16 | 0 | 0 | 0 | 6 |
| loki-k8s-operator | 22 | 0 | 0 | 3 | 9 |
| maubot-operator | 14 | 0 | 0 | 3 | 8 |
| minio-operator | 23 | 0 | 0 | 5 | 11 |
| mongodb-k8s-operator | 8 | 0 | 0 | 1 | 7 |
| mongos-k8s-operator | 25 | 0 | 0 | 8 | 13 |
| mysql-router-operators | 11 | 0 | 0 | 1 | 2 |
| opencti-operator | 15 | 0 | 0 | 0 | 3 |
| openfga-operator | 18 | 0 | 0 | 4 | 2 |
| opensearch-dashboards-operator | 14 | 0 | 0 | 1 | 13 |
| opensearch-operator | 17 | 0 | 0 | 0 | 17 |
| parca-agent-operator | 20 | 0 | 0 | 1 | 5 |
| pgbouncer-k8s-operator | 11 | 0 | 0 | 3 | 1 |
| postgresql-operator | 9 | 0 | 0 | 0 | 2 |
| postgresql-single-kernel-library | 23 | 0 | 0 | 1 | 7 |
| prometheus-scrape-target-k8s-operator | 16 | 0 | 0 | 2 | 3 |
| pvcviewer-operator | 18 | 0 | 0 | 0 | 9 |
| redis-k8s-operator | 12 | 0 | 0 | 1 | 5 |
| synapse-operator | 25 | 0 | 0 | 2 | 10 |
| trino-k8s-operator | 17 | 0 | 0 | 2 | 5 |
| ubuntu-manpages-operator | 12 | 0 | 0 | 1 | 4 |
| valkey-operator | 13 | 0 | 0 | 0 | 5 |

## Every contradicted or miscited finding

### superset-k8s-operator

*Several findings cite code that supports the general claim but at line numbers that don't match the quoted text, and two findings cite no source at all, suggesting the automated review's line attribution is unreliable even when its underlying claims are plausible.*

- **miscited** (high) — 2. Root cause confirmed in `run-server.sh`
  - Where: `superset_rock/startup-scripts/run-server.sh:26-27`
  - Second reader: The quoted --bind line is at line 24 in the excerpt, not lines 26-27 as cited (those are --error-logfile/--workers).
- **miscited** (high) — 6. `app` charm-function mode runs Flask in development mode
  - Where: `superset_rock/startup-scripts/k8s-bootstrap.sh:55-56`
  - Second reader: The flask run --debugger line is at line 54 in the excerpt, not lines 55-56 as cited (which is the app-gunicorn branch).
- **miscited** (high) — 7. `container.get_check()` called without a connection guard
  - Where: `src/charm.py:206`
  - Second reader: container.get_check("up") appears at line 210 in the excerpt, not line 206 as cited (which is self._update(event)).
- **miscited** (high) — 8. Charm stays "maintenance" for up to 5 minutes after becoming healthy
  - Where: `src/charm.py:518` (`MaintenanceStatus("replanning application")`)
  - Second reader: Line 518 in the excerpt is a closing parenthesis, not a MaintenanceStatus('replanning application') call; that text is absent from the shown range.
- **miscited** (medium) — 10. `_on_update_status` re-runs Trino sync and self-registration checks every 5 minutes
  - Where: `src/charm.py:215-217` (`_on_update_status`), `src/relations/trino_catalog.py:115-117`
  - Second reader: charm.py:215-217 matches the Trino sync call, but trino_catalog.py:115-117 is a docstring, not the _should_sync/ready_to_start logic the claim describes.
- **miscited** (high) — 14. Celery worker explicitly runs as root (`--uid 0`)
  - Where: `superset_rock/startup-scripts/k8s-bootstrap.sh:49`
  - Second reader: The --uid 0 celery worker line is at line 48 in the excerpt, not line 49 as cited (which is the elif beat branch).
- **miscited** (high) — 15. Config file permissions inconsistent with `run_user`
  - Where: `src/utils.py:56` (`0o744`), `superset_rock/rockcraft.yaml` (`run_user: _daemon_`)
  - Second reader: Line 56 in the excerpt is a docstring 'Args:' line, not the 0o744 permission (which is at line 61); rockcraft.yaml claim has no excerpt.
- **miscited** (high) — 17. `nginx-route` interface incompatible with `traefik-k8s`
  - Where: `charmcraft.yaml:29` (`nginx_ingress_integrator.v0.nginx_route`), `src/charm.py:132-140`
  - Second reader: charmcraft.yaml line 29 is data_platform_libs.data_interfaces, not the nginx_route lib entry, which is actually at line 37.
- **miscited** (medium) — 19. `superset_api.py` hardcodes port 8088 and admin username
  - Where: `src/superset_api.py:70`, `src/relations/trino_catalog.py:240`
  - Second reader: superset_api.py:70 matches the base_url default, but trino_catalog.py:240 is a docstring for _use_ssl, not the admin_username/password call (actually near lines 271-273).

### kubeflow-dashboard-operator

*Several core code-level bug claims (port capture, remove/re-raise, missing relation-broken handlers) are well supported by the cited excerpts, but multiple line-citations are mismatched to unrelated code (miscited), some lint/tool-output claims look contradicted by the visible code, and many test-gap/runtime findings have no citation at all to verify.*

- **miscited** (high) — `KubernetesServicePatch` library deprecated, removal due October 2025
  - Where: `lib/charms/observability_libs/v1/kubernetes_service_patch.py` (header docstring), `src/charm.py:103`
  - Second reader: Citation only shows src/charm.py; the library docstring text supposedly proving deprecation is not included in any excerpt.
- **miscited** (medium) — Negative/out-of-range port accepted silently, no validation
  - Where: `config.yaml` (no `min`/`max`), `src/charm.py:92`
  - Second reader: config.yaml (the claimed missing min/max) was not included; only charm.py's int cast is shown, which doesn't establish the config schema claim.
- **miscited** (high) — No tests for `ingress-relation-broken` / `_handle_ingress` no-ingress path
  - Where: `tests/unit/test_operator.py`
  - Second reader: Line 347 in the excerpt is inside _get_dashboard_links, not the _handle_ingress 'if interfaces["ingress"]' branch described.
- **miscited** (high) — Non-leader units show `waiting`/`Waiting for leadership`
  - Where: `src/charm.py:356-357` (`_check_leader` raises `CheckFailed` with `WaitingStatus`)
  - Second reader: Lines 356-357 in the shown excerpt are _get_data_from_profiles_interface, not _check_leader (which is at ~234-236 and not shown here).
- **miscited** (medium) — Pyright: 8 type errors in charm source
  - Where: `src/charm.py`, `src/dashboard_links.py`
  - Second reader: Line 68 shown is 'self.status = status_type(self.msg)', unrelated to the claimed self._container/None-call error; other sub-claims (197, 255/257) do match shown code.
- **contradicted** (medium) — Import block in `src/charm.py` unsorted
  - Where: `src/charm.py:5-41`
  - Second reader: The shown import block already appears alphabetically sorted with serialized_data_interface last among third-party imports, undermining the 'unsorted' claim.
- **contradicted** (medium) — Unused `# noqa E501` directives
  - Where: `src/charm.py:57`, `src/charm.py:220`
  - Second reader: Line 57 is a very long URL comment clearly exceeding typical line-length limits, so the noqa E501 there is plausibly necessary, not unused as claimed.

### discourse-k8s-operator

*Several findings are well-supported by the cited code, but multiple citations point to the wrong line ranges or unrelated code blocks (findings 3,4,13,16,20,21), and some findings rely entirely on unavailable or runtime-only evidence.*

- **miscited** (high) — Database migrations run on every unit, not just the leader
  - Where: `src/charm.py:449-451` (in `_set_up_discourse`); confirmed by observing unit 1 running the same Pebble service set as unit 0
  - Second reader: Cited lines 449-451 show pod_config/redis code, not _set_up_discourse or the migration-idempotency comment referenced.
- **miscited** (high) — `NO_PROXY` from Pebble-inherited environment leaks into workload despite charm setting empty proxy vars
  - Where: `src/charm.py:385-391` (charm setting) vs observed Pebble plan at runtime, confirmed across two deployments
  - Second reader: Cited lines 385-391 show S3 env dict, not the proxy-setting code (actual proxy code appears elsewhere, e.g. ~493-502).
- **miscited** (medium) — juju refresh triggers pod recreation and full setup even when no code changed
  - Where: `src/charm.py:148-149` (`_on_upgrade_charm`), `src/charm.py:180-185` (`_on_rolling_restart`)
  - Second reader: Cited line ranges (148-149, 180-185) don't correspond to _on_upgrade_charm (130-136) or _on_rolling_restart (193-199); runtime claims also unverifiable from source.
- **miscited** (medium) — RollingOpsManager emits acquire_lock on upgrade but callback runs full setup
  - Where: `src/charm.py:148-149` (`_on_upgrade_charm`), `src/charm.py:180-185` (`_on_rolling_restart`)
  - Second reader: Cited lines (148-149, 180-185) don't match actual locations of _on_upgrade_charm (130-136) and _on_rolling_restart (193-199), though functions are supported elsewhere in same excerpt.
- **miscited** (high) — DB password visible in plain text in the Pebble plan
  - Where: `src/charm.py:412-418` (Pebble layer construction in `_start_service`); confirmed at runtime
  - Second reader: Cited lines 412-418 show redis relation retrieval code, not the Pebble layer/env dict containing DISCOURSE_DB_PASSWORD.
- **miscited** (high) — Deprecated library warnings at runtime
  - Where: `lib/charms/rolling_ops/v0/rollingops.py:28` (deprecation warning in `RollingOpsManager.__init__`); `lib/charms/data_platform_libs/v0/data_interfaces.py:1176` (uses deprecated `JujuVersion.from_environ()`)
  - Second reader: Cited rollingops.py line 28 is a YAML doc example, not a deprecation warning; data_interfaces.py line shows deprecated API use but not the warning text itself.

### catalogue-k8s-operator

*Most findings are well-grounded in the provided code, but a few line citations are off (pointing to unrelated code) and two nginx-config findings are directly contradicted by the cited excerpt itself.*

- **contradicted** (high) — 4. Nginx config lacks access_log and error_log directives — Pebble log forwarding silent (deployed rev113)
  - Where: `charm/src/nginx_config.py:19-44` (HTTP_SERVICE), `charm/src/nginx_config.py:50-73` (HTTPS_SERVICE) — track/2 (rev113)
  - Second reader: The cited excerpt already contains access_log/error_log directives in both HTTP_SERVICE and HTTPS_SERVICE, contradicting the claim they are absent.
- **miscited** (medium) — 5. Nginx config advertises deprecated TLSv1 and TLSv1.1
  - Where: `charm/src/nginx_config.py:72` (rev113; same in HEAD)
  - Second reader: ssl_protocols line with TLSv1/1.1 is at line 58, not line 72 as cited; cited line is unrelated __init__ code.
- **miscited** (medium) — 7. Unsorted items cause unnecessary nginx restarts (flapping)
  - Where: `charm/src/charm.py:173` (items used unsorted), config comparison in `_update_catalogue_config` (line 246)
  - Second reader: Cited excerpt only shows _on_items_changed calling _configure(event.items); the referenced comparison logic at line 246 is not in the shown excerpt.
- **contradicted** (medium) — 9. Dead `upstream self` block in HTTP nginx config (deployed rev113)
  - Where: `charm/src/nginx_config.py:33-35` (rev113/track-2)
  - Second reader: Cited lines 33-35 don't contain the upstream block (it's at 24-26), and the excerpt shows it still present, contradicting 'Removed in HEAD'.
- **miscited** (medium) — 10. ubuntu@26.04 base requirement blocks deployment on current infrastructure
  - Where: `charm/charmcraft.yaml:45`
  - Second reader: platforms: ubuntu@26.04 line is at line 36, not line 45 as cited; line 45 is an unrelated override-build directive.

### charmed-etcd-operator

*Several findings cite line ranges that do not correspond to the code they describe, undermining confidence in the review's citation accuracy despite plausible underlying claims.*

- **miscited** (high) — 1. etcdctl/etcdutl subprocess timeout is too short for some operations
  - Where: `src/common/client.py:271` and `src/common/client.py:323`
  - Second reader: Cited lines 271 and 323 show is_healthy and create_database_snapshot code, not the subprocess.run(timeout=10) call.
- **miscited** (medium) — 2. `_exists_preventing_reason` returns `bool` but callers treat it as `str`
  - Where: `src/events/external_clients.py:79` and `src/events/external_clients.py:149`
  - Second reader: Excerpt only shows calls to _exists_preventing_reason(), not its definition/type annotation, so the '-> bool' claim is unverified here.
- **miscited** (high) — 6. `SNAP_USER` and `SNAP_GROUP` are hardcoded numeric/literal values
  - Where: `src/literals.py:16-17`
  - Second reader: Lines 16-17 are SNAP_LOG_PATH/SNAP_ARCHIVE_PATH; SNAP_USER and SNAP_GROUP are actually at lines 19 and 21.
- **miscited** (medium) — 7. `config_properties` can leave `http://` in `initial-cluster` during TLS transition
  - Where: `src/managers/config.py:68`
  - Second reader: Cited line 68 pertains to restore-verify logic, not the http/https initial-cluster issue which appears at line 75 and further TLS code not shown.
- **miscited** (high) — 8. `is_reachable` retries without first checking if etcd is alive
  - Where: `src/workload.py:64-76`
  - Second reader: Cited lines 64-76 show the install() method; is_reachable's retry loop is actually at lines 87-98.

### kafka-operator

*Several findings cite line ranges that don't match the described code (miscited), and a few code-only claims are directly contradicted by the very code shown, so the review's citations should be verified individually rather than trusted wholesale.*

- **contradicted** (high) — 1. `_determine_unit_status` does not check workload health — false-positive `active`
  - Where: `machine/src/charm.py:214-237` and `k8s/src/charm.py:195-213` (`_determine_unit_status`)
  - Second reader: The cited code itself calls self.workload.active() inside _determine_unit_status (line 239/210), contradicting the claim it 'never' checks workload health.
- **miscited** (medium) — 2. K8s scale-up triggers spurious `charm_refresh` cycle, permanently blocks new units
  - Where: `k8s/src/charm.py:92-98` (refresh init), `common/single_kernel_kafka/events/broker.py:156-158` (`_on_start` early return), `common/single_kernel_kafka/events/refresh.py:70-76` (`run_pre_refresh_checks_after_1_unit_refreshed`)
  - Second reader: Cited broker.py:156-158 and refresh.py:70-76 do not correspond to the described early-return or StatefulSet-partition logic; the shown run_pre_refresh_checks method contains no partition logic at all.
- **contradicted** (high) — 6. `_broker_status` reads bootstrap-controller from wrong relation in combined mode
  - Where: `common/single_kernel_kafka/core/cluster.py:551` (`_broker_status`), `common/single_kernel_kafka/core/cluster.py:157` (`peer_cluster` property)
  - Second reader: When runs_broker and runs_controller are both true, extra_kwargs (including correct local bootstrap_controller) is merged via **extra_kwargs into the broker-branch PeerCluster, so the claimed empty value is not the code's actual behavior.
- **miscited** (medium) — 11. machine LXD deployments produce sysctl warnings and an uncaught crash path
  - Where: `common/single_kernel_kafka/health.py`
  - Second reader: health.py:191 is _check_memory_maps(), unrelated to the 'unit not connected to controller' message which originates from a separate check in broker.py, so the causal link cited doesn't hold.
- **miscited** (medium) — 15. `_on_roles_changed` handler duplicated between machine and k8s `charm.py`
  - Where: `machine/src/charm.py:119-133` and `k8s/src/charm.py:148-162`
  - Second reader: Cited line ranges (machine 119-133, k8s 148-162) do not correspond to the actual _on_roles_changed method locations shown in the excerpts (142-159 and 124-141 respectively).

### zookeeper-k8s-operator

*Several findings cite plausible-sounding but wrong line numbers (miscited) or rest on unverifiable runtime behaviour, though the core pydantic-crash and TLS/k8s error-handling findings are well supported by the code shown.*

- **miscited** (medium) — `_on_cluster_relation_changed` is an over-wide catch-all handler
  - Where: `src/charm.py:225`
  - Second reader: Excerpt (charm.py 190-260) shows the handler body and noqa but not the six framework.observe() registrations quoted in the evidence.
- **miscited** (medium) — `apply_service` swallows critical k8s API errors
  - Where: `src/managers/k8s.py:41-50`
  - Second reader: charm.py:189 is a comment in the FALSE/remove_service branch, not the SERVICE_UNAVAILABLE-setting lines (194/198) the claim refers to.
- **miscited** (medium) — `loadbalancer-extra-annotations` config is dead — defined but never read
  - Where: `config.yaml:26-28` (defined), never referenced in `src/` or `lib/`
  - Second reader: Cited lines 26-28 describe certificate-include-ip-sans/expose-external, not loadbalancer-extra-annotations, which is defined at lines 31-33.
- **miscited** (medium) — TLS certificate files left on disk after relation removal
  - Where: `src/events/tls.py:139-140` — no cleanup on `certificates_broken`
  - Second reader: Cited lines 139-140 belong to _on_certificate_expiring, not _on_certificates_broken (lines 159-173), which actually does call remove_stores().
- **miscited** (high) — `_on_zookeeper_pebble_ready` ignores which event fired it
  - Where: `src/charm.py:330`
  - Second reader: Line 330 is inside _on_secret_changed's docstring, not _on_zookeeper_pebble_ready (which starts at line 344).

### zookeeper-operator

*Several findings are well supported by exact code matches, but a notable subset cite line ranges whose actual content contradicts or fails to substantiate the claim, and multiple findings lack any supplied source excerpt.*

- **miscited** (medium) — New unit crashes on `upgrade-relation-changed` due to wrong relation as data source
  - Where: `lib/charms/data_platform_libs/v0/upgrade.py:1087,1130` (`on_upgrade_changed`), `src/events/upgrade.py`
  - Second reader: excerpt shows peer_relation.data[top_unit] usage but never defines peer_relation as the upgrade relation vs cluster peer relation, and the ops/model.py citation is explicitly unresolved.
  - Unresolved citations: ops/model.py:1817 (no such file in the checkout)
- **miscited** (high) — `set-tls-private-key` crashes with an uncaught `RuntimeError` when no certificates relation exists
  - Where: `src/events/tls.py:97` (`_set_tls_private_key` → `_on_certificate_expiring`)
  - Second reader: line 97 in the excerpt falls inside _on_certificates_joined, not _set_tls_private_key or _on_certificate_expiring as the finding claims; those methods appear later and are not shown here.
- **contradicted** (high) — Blocking `time.sleep(5)` in the restart handler
  - Where: `src/charm.py:225` (`_restart`)
  - Second reader: the cited charm.py lines 190-260 contain no time.sleep(5) call or _restart method; line 225 is blank, refuting the specific citation.
- **contradicted** (high) — `endpoints_external` retry adds up to 15s delay to client relation hooks
  - Where: `src/core/cluster.py:127` (`endpoints_external`)
  - Second reader: cluster.py line 127 in the excerpt is the 'clients' property decorator, not endpoints_external, and no retry decorator appears in the shown code.
- **miscited** (high) — `subprocess.CalledProcessError` not handled in `workload.exec()` callers
  - Where: `src/workload.py:62–66` (`exec`), `src/events/backup.py` (`restore_snapshot`)
  - Second reader: lines 62-66 in the excerpt correspond to the end of read() and start of write(), not exec(), which is actually at lines 74-82.

### authentik-worker-operator

*Several findings rely on runtime/deployment observations or citations that do not match the claimed content or location, so many are unverifiable or miscited despite plausible underlying claims.*

- **miscited** (medium) — `mypy` configured in `pyproject.toml` but not run in CI
  - Where: `tox.ini:lint`, `pyproject.toml:[tool.mypy]`
  - Second reader: Citation only shows services.py type usage; the key claim about tox.ini lint config and mypy CI omission is not shown.
- **miscited** (high) — `TracingData.to_env_vars()` can emit an empty OTEL endpoint if relation data is valid but incomplete
  - Where: `src/integrations.py:21–24`
  - Second reader: Cited lines 21-24 cover AuthentikClusterIntegration.__init__, not the TracingData.load()/is_ready()/get_endpoint() logic the finding describes.
- **miscited** (medium) — `worker_threads` semantically unvalidated despite documented recommendation
  - Where: `charmcraft.yaml` config, `src/configs.py:31`
  - Second reader: Cited line 31 is the postgresql_disable_server_side_cursors mapping, not the worker_threads mapping (line 26) the finding discusses.
- **miscited** (high) — Charmhub links typo
  - Where: `charmcraft.yaml:6–7`
  - Second reader: Finding cites lines 6-7 (title/summary) but the actual typoed URLs appear at lines 11-12 in the shown excerpt.

### mysql-operators

*Several findings cite code that is present but at slightly wrong line numbers or the wrong function, and many rest on unverifiable runtime/deployment observations not backed by any supplied excerpt, so overall citation precision is inconsistent.*

- **miscited** (high) — Snap wrapper defeats systemd auto-restart; charm's own restart bypasses it but is gated
  - Where: snap `charmed-mysql` rev 215 wrapper script (external, not in repo — observed via `systemctl status`, `start-mysqld.sh` line 21); charm restart at `machines/src/charm.py:525-533`
  - Second reader: The cited lines 525-533 are _execute_manual_rejoin's docstring/lookup, not the snap_service_operation restart call, which actually appears at lines 511-513 in the same excerpt.
- **miscited** (medium) — Subprocess-based background dispatchers (`juju-exec` pattern) are fragile
  - Where: `src/services/managers/log_rotate_manager.py:68-77`, `src/services/managers/self_healing_manager.py:56-65`, `scripts/log_rotate_dispatcher.py`, `scripts/self_healing_dispatcher.py`
  - Second reader: The excerpts show subprocess.Popen invoking a local python3 dispatcher script, not the claimed 'juju-exec -u <unit> JUJU_DISPATCH_PATH=...' command; that detail isn't shown.
- **miscited** (high) — Config validation error leaves the unit hook-failed instead of `BlockedStatus`
  - Where: `src/config.py:113-118` (pydantic validator), `src/charm.py:1147` (entry point, no try/except)
  - Second reader: config.py:113-118 is max_connections_validator (not logs_audit_policy), and charm.py:1147 is inside _set_app_status, not a config-changed entry point lacking try/except.
- **miscited** (medium) — 24-hour kill-delay hides mysqld startup failures
  - Where: `src/charm.py:269`
  - Second reader: The 'kill-delay': '24h' line is actually at line 261 in the shown excerpt, not line 269 as cited (line 269 is part of the log-tail service block).

### ranger-k8s-operator

*Several findings are well-supported by the cited code, but a few misquote or overstate behavior not shown in the excerpt (e.g., wrong context variables, unused-resource claim contradicted by containers section), and multiple findings rest on unverifiable runtime behavior.*

- **miscited** (high) — 6. Jinja template variable mismatches in usersync config
  - Where: `src/charm.py:285-320`, `templates/ranger-usersync-config.jinja`
  - Second reader: Cited charm.py lines show _configure_ranger_admin, not the usersync template or its variable names referenced in the finding.
- **miscited** (high) — 7. None values rendered as literal "None" string in config files
  - Where: `src/charm.py:302-312`, `templates/admin-config.jinja:86-92`
  - Second reader: Cited context dict contains OPENSEARCH_* keys, not the audit_elasticsearch_* variables quoted in the evidence.
- **contradicted** (high) — 15. Unused `ranger-image` resource forces a large image pull
  - Where: `charmcraft.yaml:94-96`
  - Second reader: charmcraft.yaml explicitly references ranger-image under containers, showing it is used, not unused as the title claims.
- **contradicted** (medium) — 18. Password validation silently skipped when state is not ready
  - Where: `src/charm.py:439-444`
  - Second reader: The elif branch in _validate_password compares password to config for all units regardless of leadership, so non-leaders do validate once a password exists, contradicting 'never validate'.

### resource-dispatcher

*Several findings rely on citations that don't actually contain the quoted/claimed code (wrong line ranges or missing files), and multiple high-severity claims are runtime observations rather than source-verifiable facts.*

- **miscited** (high) — Rev 547's `KubernetesManifestsProvider` library crashes when a requirer sends manifests via Juju secrets
  - Where: `lib/charms/resource_dispatcher/v0/kubernetes_manifests.py` (rev 547, 355 lines, no `is_secret_enabled()`); `src/charm.py:237` (`_update_manifests` → `get_manifests`)
  - Second reader: Cited charm.py:237 is actually _on_install, not _update_manifests/get_manifests, and no library file excerpt is provided to support the JSON crash claim.
- **miscited** (high) — `except ApiError` does not catch `LoadResourceError`
  - Where: `src/charm.py:165` (`_deploy_k8s_resources`)
  - Second reader: Cited range (lines 130-200) does not contain the quoted try/except ApiError block, which actually sits at lines 226-232.
- **miscited** (medium) — `provide-cmr-mesh` declared in metadata but never implemented
  - Where: `metadata.yaml:11–17`; `src/charm.py` (no handler code)
  - Second reader: metadata.yaml excerpt confirms the interface declarations, but no src/charm.py excerpt is given to verify the claimed absence of handler code.
- **miscited** (high) — `_deploy_k8s_resources` has no leader check
  - Where: `src/charm.py:161–173` (`_on_install`); `src/charm.py:174` (`_on_upgrade_charm`)
  - Second reader: Cited lines 161-173/174 are property definitions, not _on_install/_on_upgrade_charm (actually at ~line 237-245 per other excerpts), and the shown range never reaches _deploy_k8s_resources.

### script-exporter-operator

*Several findings are well supported by the charm.py excerpts (missing exception handling, unregistered port, path traversal, dead code), but some code-behavior claims are contradicted by the very excerpts shown (double decode, statuses accumulation), and many findings cite no source at all.*

- **contradicted** (medium) — `_statuses` list accumulates across hook invocations
  - Where: `src/charm.py:37` (`self._statuses = []`), `src/charm.py:175-179` (`_on_collect_unit_status`)
  - Second reader: ops charms are re-instantiated (running __init__, resetting _statuses=[]) on each hook dispatch, so accumulation across separate hook invocations as described does not occur.
- **contradicted** (high) — `_insert_full_path_in_command` re-decodes `scripts_archive` twice per config-changed
  - Where: `src/charm.py:113` (`_on_config_changed`), `src/charm.py:231` (`_insert_full_path_in_command`)
  - Second reader: The excerpt shows _insert_full_path_in_command uses self._script_names (already computed), not a fresh call to _retrieve_script_names().
- **contradicted** (medium) — `_retrieve_script_names` re-parses `scripts_archive` on every call, no caching
  - Where: `src/charm.py:239-252`
  - Second reader: Other excerpts show _retrieve_script_names is called once in _on_config_changed and _insert_full_path_in_command reuses self._script_names, not re-calling it.
- **miscited** (high) — Deprecated `charms.operator_libs_linux.v1.systemd` library
  - Where: `src/charm.py:14-17` (import)
  - Second reader: Cited lines 14-17 are the lzma import, not the systemd import (which is at lines 26-32 in the same excerpt).

### airbyte-k8s-operator

*Several findings rely on unavailable or mismatched excerpts (esp. literals.py:46 and NONE AVAILABLE citations), and one causal claim about check-status handling is directly contradicted by the shown code, so the review's citation accuracy is mixed.*

- **miscited** (high) — Temporal dependency is undeclared and blocks the charm from reaching active
  - Where: `charmcraft.yaml` (no temporal relation), `src/charm.py` (`reconcile`), `src/literals.py:46` (`TEMPORAL_HOST` default)
  - Second reader: Cited literals.py:46 is LOGS_BUCKET_CONFIG, not TEMPORAL_HOST; no TEMPORAL_HOST appears anywhere in the shown excerpt.
- **contradicted** (medium) — Stopped services not detected; charm stays `active` with dead processes
  - Where: `src/charm.py:255-290` (`_on_update_status`)
  - Second reader: The get_check call is not wrapped by _validate_pebble_plan's try/except (which only catches KeyError/ConnectionError); a failed check instead sets MaintenanceStatus per lines 277-281, not silently continuing as claimed.
- **miscited** (medium) — Bare `except Exception` in multiple locations
  - Where: `src/relations/minio.py:131`, `src/s3_helpers.py:38`, `src/charm_helpers.py:267,295`
  - Second reader: minio.py:131 and s3_helpers.py:38 bare except Exception are confirmed, but charm_helpers.py:267,295 are cited without any supporting excerpt.

### alertmanager-k8s-operator

*Several core code-level claims (YAML/amtool handling, frozen init values, missing peer-departed handler, exit-hook status logic) are well supported by the cited excerpts, but a few citations are truncated or point away from the actual mechanism (e.g. findings 6, 13), one finding is contradicted by the code shown (finding 4), and roughly half the findings supply no excerpt at all and are unverifiable.*

- **contradicted** (medium) — TLS private key material generated and pushed to the workload even with no TLS relation configured
  - Where: `src/charm.py:96` (key path constant), `src/charm.py:463-466` (unconditional `set_tls_server_config` call in `_render_manifest`)
  - Second reader: Cited manifest code explicitly maps _key_path to None when tls_config is falsy, contradicting the claim that the key is written unconditionally without any TLS relation.
- **miscited** (medium) — TLS private key not deleted when the certificates relation is removed
  - Where: `src/charm.py:472-480` (key path mapping in `_render_manifest`), `src/charm.py:96`, `src/charm.py:630` (`_update_ca_certs`)
  - Second reader: Citation shows manifest mapping key path to None but not the apply()/remove_path logic that is central to the 'fails to remove' claim.
- **miscited** (high) — Invalid Go template syntax causes a hook error, not `BlockedStatus`
  - Where: `src/charm.py:436-449` (`_get_raw_config_and_templates`), `src/config_builder.py:71-76` (`set_templates` called unconditionally)
  - Second reader: The config_builder.py excerpt is truncated before reaching the cited lines 71-76 that supposedly show unconditional set_templates call.

### blackbox-exporter-operator

*Several findings rest on solid code evidence (missing exception handling, literal log placeholders, pinned dependencies), but multiple 'Where' citations point to the wrong lines (e.g., findings 3, 8, 9), and some design/behavioral claims (cascade bug, missing charmcraft config) lack supporting excerpts.*

- **miscited** (high) — `_push_config` does not reset `BlockedStatus` when returning early with a valid config
  - Where: `src/charm.py:142–148`
  - Second reader: Cited lines 142-148 are the snap() method/docstring, not the early-return logic (lines 156-158) that actually lacks the status reset.
- **miscited** (high) — Dead log placeholders in snap install and restart
  - Where: `src/charm.py:207`, `src/charm.py:162`
  - Second reader: Line 207 confirms the literal placeholder, but line 162 (cited as the 'correct f-string' example) is unrelated code (DEFAULT_CONFIG_FILE assignment), not the restart log line.
- **miscited** (high) — `_restart_snap` failure is invisible to operators
  - Where: `src/charm.py:160–163`
  - Second reader: Cited lines 160-163 belong to _push_config's default-config logic, not _restart_snap (lines 222-227), where the described behavior actually occurs.

### cassandra-operator

*Several findings are well-supported by direct code excerpts (esp. restore swallow-error and copyright year), but a number rely on runtime-only evidence or cite code that doesn't actually show the claimed detail.*

- **miscited** (medium) — `_on_resource_entity_permissions_changed` can let ValueError propagate on invalid permissions
  - Where: `src/events/provider.py:169` (`_on_resource_entity_requested`/`_on_resource_entity_permissions_changed`)
  - Second reader: Excerpt shows the Permissions() call inside _on_resource_entity_requested's loop at line 174, not inside _validate_entity_permissions, and not in _on_resource_entity_permissions_changed as titled.
- **miscited** (medium) — Unnecessary Cassandra restart on unchanged profile config
  - Where: `src/events/cassandra.py:280` (`_on_config_changed`), `render_env` at line 301
  - Second reader: Excerpt shows render_env's call site but not its implementation, so the claim that it returns True unconditionally is unsupported by the citation.
- **miscited** (medium) — Typo: "proivded" in error message
  - Where: `src/events/backup.py:196` (draft text) / notes cite line 55 for the same string — location not fully reconciled, treat as `src/events/backup.py`
  - Second reader: Excerpt shows BackupMessages.NOT_READY used in logging but not its string value, so the 'proivded' typo is not shown.

### cos-coordinated-workers

*Most code-level claims (missing exception handling, private-attribute/API coupling) are accurately sourced, but several findings rely on unverifiable runtime observations or contain line-number miscitations.*

- **miscited** (medium) — 4. Non-deterministic relation data ordering causes unnecessary hook churn
  - Where: `src/coordinated_workers/coordinator.py:620-632` (`_upstream_loki_endpoints_by_unit`), `src/coordinated_workers/interfaces/cluster.py:216-228` (`gather_addresses_by_role`)
  - Second reader: coordinator.py citation matches _upstream_loki_endpoints_by_unit, but cluster.py:216-228 shows grant_privkey/publish_data, not gather_addresses_by_role.
- **miscited** (high) — 18. CI only tests against Juju 3.6, not 4.x
  - Where: `.github/workflows/pull-request.yaml:49-50`
  - Second reader: Cited lines 49-50 show the unit-test job; the actual CONCIERGE_JUJU_CHANNEL: 3.6/stable line is at line 69 in the same excerpt.
- **miscited** (high) — 23. Tester charm logs `ERROR` on every hook execution
  - Where: `tests/integration/testers/worker/src/charm.py:39`
  - Second reader: logging.error('WorkerCharm __init__') is at line 22 in the excerpt, not line 39 as cited (line 39 is part of the pebble layer dict).

### cos-registration-server-k8s-operator

*Most citations accurately reflect the quoted code, but a few (7, 16, 18) cite lines that don't contain the described logic/text, and several findings blend verifiable code facts with unverifiable runtime observations.*

- **miscited** (medium) — `_cleanup_certificate_requests` unconditionally removes and re-adds all CSRs
  - Where: `src/tls_certificates_devices.py:86` (call site in `_configure`), `:256` (definition; notes cite `258-260`)
  - Second reader: Excerpt shows only the call site (line 86); the cited definition lines 256-260 describing unconditional removal/logging are not shown.
- **miscited** (medium) — `AuthDevicesKeysConsumer` fires a spurious changed event on first run
  - Where: `src/auth_devices_keys.py:169-171`
  - Second reader: Excerpt cuts off before the comparison logic (coerced_data vs databag) that would demonstrate the spurious-event claim.
- **miscited** (high) — CONTRIBUTING.md references a non-existent `static` tox environment
  - Where: `CONTRIBUTING.md:15`
  - Second reader: Cited line 15 is descriptive text, not the 'tox run -e static' line, which actually appears at line 20 in the same excerpt.

### feast-operators

*Several findings cite real, matching code (supported), but many rely on runtime/test evidence with no excerpt provided (marked unverifiable), and a few citations point to the wrong file or wrong line for the claimed content (miscited).*

- **miscited** (medium) — 12. Temporary file leak on feast-ui charm host
  - Where: `charms/feast-ui/src/charm.py:119–124`
  - Second reader: Cited lines 119-124 show unrelated depends_on code; the actual tempfile.NamedTemporaryFile(delete=False) call is at lines 156-159, elsewhere in the shown window.
- **miscited** (high) — 14. feast-ui has no runtime configuration options
  - Where: no `config.yaml` in either charm directory
  - Second reader: Cited excerpt is charms/feast-integrator/src/charm.py, not feast-ui/src/charm.py where INGRESS_PATH_MATCHED_PREFIX is defined; wrong file entirely.
- **miscited** (medium) — 15. PodDefault `FEAST_FS_YAML_FILE_PATH` may not match container path
  - Where: `charms/feast-integrator/src/templates/feature_store_poddefault.yaml.j2:15` vs. `charms/feast-ui/src/charm.py:32`
  - Second reader: Cited line 32 is an unrelated import; DEST_PATH is actually at line 38 in the same excerpt, and the poddefault template file (the other half of the comparison) isn't shown at all.

### grafana-k8s-operator

*Most findings are well-supported by the cited code, but several config-validation findings (4, 5, 12) cite unrelated properties, and a few HA/test/deprecation claims rely on unverifiable external or unshown evidence.*

- **miscited** (high) — 4. No config validation for `log_level` option
  - Where: `charmcraft.yaml` (`log_level` definition), `src/charm.py:282` (`_pebble_env`)
  - Second reader: Cited lines 280-283 show internal_url property, unrelated to log_level or _pebble_env validation.
- **miscited** (high) — 5. No config validation for `admin_user` (empty string accepted)
  - Where: `src/charm.py:285` (`_pebble_env`)
  - Second reader: Cited line 285 shows external_url property, not admin_user handling.
- **miscited** (high) — 12. `log_level` config accepts unbounded strings, can exceed Pebble plan limits
  - Where: `src/charm.py:282` (`_pebble_env`), `charmcraft.yaml` (`log_level` definition)
  - Second reader: Cited lines 280-283 again show internal_url property, unrelated to log_level length validation.

### identity-platform-admin-ui-operator

*Several findings rest on unverifiable runtime/log observations, a few contain clear citation errors (wrong line numbers or lists that contradict the shown NOOP_CONDITIONS tuple), and three findings have no supplied source at all.*

- **miscited** (medium) — 6. Charm reports `active` while critical integration data is empty
  - Where: `src/utils.py:61` (`integration_existence` only checks relation count), `src/charm.py:517-538` (`_pebble_layer`)
  - Second reader: is_ready() call is at integrations.py:217 not 235, and integration_existence's relation check is at utils.py:47 not 61; cited lines don't show the referenced code.
- **contradicted** (medium) — 10. `charmcraft.yaml` `optional` mismatch with charm behaviour
  - Where: `charmcraft.yaml:38-41` (only `pg-database` marked `optional: false`) vs `src/utils.py:113-118` (7 integrations are NOOP_CONDITIONS), `src/charm.py:413-438` (7 integrations block status)
  - Second reader: NOOP_CONDITIONS actually lists database_integration_exists, not smtp_integration_exists, contradicting the finding's specific list of 7 integrations.
- **contradicted** (high) — 11. SMTP hard requirement blocks deployment without an ecosystem SMTP charm
  - Where: `src/utils.py:118` (SMTP in NOOP_CONDITIONS), `src/charm.py:437-438`
  - Second reader: The cited NOOP_CONDITIONS tuple (lines 101-109 in the shown excerpt) does not include smtp_integration_exists, directly contradicting the citation claim.

### kiali-k8s-operator

*Several findings are well-grounded in the cited charm.py/charmcraft.yaml/pyproject.toml excerpts, but many test-gap and lint claims cite the wrong file (source instead of tests) or lack any excerpt at all.*

- **miscited** (medium) — `TempoMissingError` not in `StatusManager`'s default status map
  - Where: `src/charm.py:160`, `_get_tempo_api` (raises at ~line 431), `deps/observability_charm_tools/status_handling/status_manager.py`
  - Second reader: Citation only shows charm.py; the quoted DEFAULT_STATUS_MAP code from status_manager.py is not present in the excerpt.
- **miscited** (medium) — Unit tests don't cover the empty-datasources branch of `_get_tempo_datasource_uid`
  - Where: `tests/unit/test_charm.py`
  - Second reader: Citation shows charm.py source code, not the test file tests/unit/test_charm.py, so it cannot establish the described test gap.
- **miscited** (medium) — Unit tests don't cover the grafana relation-with-data branch
  - Where: `tests/unit/test_charm.py::test_kiali_config`
  - Second reader: Citation shows the source branch in charm.py but not the test file test_kiali_config, so coverage claims aren't verifiable from this excerpt.

### sysbench-operator

*Most critical/high findings are directly grounded in the shown code, but several lower-severity findings cite specific line numbers that don't match the quoted content, and multiple findings have no supplied source excerpt at all.*

- **miscited** (medium) — No pydantic constraints on `threads`/`duration`, and validation errors are swallowed
  - Where: `src/constants.py:105–113`, `src/relation_manager.py:71–75`
  - Second reader: constants.py 105-113 matches SysbenchExecutionModel exactly, but the quoted try/except in relation_manager.py is actually at lines 79-84, not the cited 71-75.
- **miscited** (medium) — `DATABASE_NAME` is a hardcoded TODO constant
  - Where: `src/constants.py:28`
  - Second reader: DATABASE_NAME with the TODO comment is actually at line 22 in the excerpt, not line 28 as cited (line 28 is class SysbenchError).
- **miscited** (medium) — `refresh_events=[]` has no effect
  - Where: `src/charm.py:53`
  - Second reader: refresh_events=[] actually appears at line 68 in the excerpt, not the cited charm.py:53 (line 53 is an unrelated observe call); the library citation at 673 is accurate.

### testflinger

*Most findings are well-grounded in the provided excerpts, but several citations point to unrelated code or lines outside the discussed range, and many findings (especially runtime/observability and missing-test claims) lack any supplied excerpt.*

- **miscited** (high) — HIGH: `on_update_testflinger_action` crashes with uncaught `FileNotFoundError`
  - Where: `agent/charms/testflinger-agent-host-charm/src/charm.py:305` (`on_update_testflinger_action`), `charm.py:91–105` (`update_testflinger_repo`)
  - Second reader: Second citation (charm.py:91-105) shows unrelated server/charm __init__ code, not update_testflinger_repo/create_virtualenv/clone_repo.
- **miscited** (medium) — MEDIUM: Machine charm default `config-dir` is empty — charm blocks immediately on start
  - Where: `agent/charms/testflinger-agent-host-charm/src/charm.py:134`, `charmcraft.yaml`
  - Second reader: Cited line 134 is unrelated (used_ports set); default config-dir/config-repo values aren't shown in this excerpt.
- **miscited** (high) — MEDIUM: Machine charm `write_file` parent-directory-not-exists case untested
  - Where: `agent/charms/testflinger-agent-host-charm/src/common.py:28–37`
  - Second reader: Lines 28-37 in the excerpt are run_with_logged_errors, not write_file's pre-try tempfile section (which is ~61-69).

### vault-k8s-operator

*Several findings cite code that doesn't match the specific claim (wrong function or missing key lines), and many findings lack any source excerpt, resting on runtime observations or absent evidence.*

- **miscited** (high) — TLSManager does not observe `pebble-ready` in TLS integration mode
  - Where: `vault-package/vault/vault_managers.py:391` — `_configure_tls_integration` returns early when `workload.is_accessible()` is `False`
  - Second reader: Cited line 391 and surrounding code belong to _configure_self_signed_certificates, not _configure_tls_integration as claimed.
- **miscited** (medium) — S3 backup actions ignore `path` from the S3 relation
  - Where: `vault-package/vault/vault_managers.py:1892` (`_get_s3_parameters`), `:1785` (`create_backup`), `:1821` (`list_backups`)
  - Second reader: Only _get_s3_parameters (1892) is shown; create_backup (1785) and list_backups (1821) usage of Naming without path is not in the excerpt.
- **miscited** (medium) — `_sync_vault_pki` runs on non-leader units without a call-site leader guard
  - Where: `k8s/src/charm.py:511` (call site), `:771` (method definition, no leader check)
  - Second reader: Excerpt only shows the call site; it doesn't show _sync_vault_pki's or sibling methods' internal leader-guard logic needed to support the comparison.

### wordpress-k8s-operator

*Most findings citing exact snippet text match the code, but several 'Where' line ranges are off by many lines from the actual quoted evidence, and one runtime-heavy finding cites unrelated code.*

- **miscited** (high) — Killing Apache parent causes cascading failure to pod restart with charm oblivious throughout
  - Where: `src/charm.py:600-605` (`_start_server`, no pebble check observation), `src/charm.py:540-545` (pebble layer with `level: alive` check)
  - Second reader: Cited lines show _run_cli/_run_wp_cli helpers, not _start_server or a pebble layer with a 'level: alive' check as claimed.
- **miscited** (high) — Config change during Apache zombie window crashes the charm (uncaught `pebble.start` ChangeError)
  - Where: `src/charm.py:608` (`_start_server` → `container.start()`, no error handling)
  - Second reader: Cited lines 573-643 show _run_wp_cli/_wrapped_run_wp_cli, not _start_server or container.start(), so claim about line 608 is unsupported by this excerpt.
- **miscited** (high) — Architecture doc outdated: claims WordPress 6.4.3 on Ubuntu 20.04
  - Where: `docs/reference/charm-architecture.md:80-83`
  - Second reader: Cited lines 80-83 discuss install triggers, not the version claim; the actual '6.4.3/Ubuntu 20.04' text is at line 86, outside the cited range.

### airflow-coordinator-k8s-operator

*Most findings are well-supported by the cited code, but one (database naming) is actually contradicted by the same code, and one (non-leader status) cites the wrong line range.*

- **contradicted** (high) — 3. Database name collision between multiple coordinators (open issue #42)
  - Where: `src/charm.py:64`
  - Second reader: database_name includes model.uuid, so coordinators in different models get distinct db names, contradicting the claimed collision across models.
- **miscited** (high) — 8. Non-leader units never set status (confirmed live at scale 2)
  - Where: `src/charm.py:617-618`
  - Second reader: Cited lines 617-618 correspond to config-provider call arguments, not the leadership check which is actually at lines 586-587.

### authentik-ldap-outpost-operator

*Most findings are well-supported by the cited code, though a few citations are miscited, unverifiable due to missing excerpts, or contradicted by control-flow narrowing in the source.*

- **contradicted** (medium) — `model.config.get()` for peer data access at `src/charm.py:290` — None not handled
  - Where: `src/charm.py:290`
  - Second reader: secret_id is narrowed/reassigned to a definite str via if/else before being passed to _read_outpost_token_secret, so it isn't Optional at that call site.
- **miscited** (medium) — traefik-route template rendered with insecure Proxy Protocol v2
  - Where: `templates/traefik-route.json.j2`, `src/integrations.py:155`
  - Second reader: Citation is integrations.py, not the referenced template file; no evidence of proxyProtocol insecure setting is shown.

### authentik-server-operator

*Most findings accurately quote the cited code, but several (3, 6) cite excerpts that do not actually contain the quoted evidence, and multiple findings blend verified code facts with unverifiable runtime/external claims.*

- **miscited** (medium) — "running database migrations" shown for non-migration failures
  - Where: `src/services.py:162` — `WorkloadService.check_health`
  - Second reader: Excerpt confirms check_health() unconditionally calls check_migrations() on DOWN, but the quoted ExecError/MigrationPendingError code (likely in cli.py) is not shown in the cited services.py excerpt.
- **miscited** (high) — No unit test for "traefik-route not secure" blocking pebble layer application
  - Where: `tests/unit/test_charm.py` and `tests/unit/conftest.py:133`
  - Second reader: Cited conftest.py lines 98-168 show relation fixtures, not the claimed all_satisfied_conditions/traefik_route_is_secure fixture.

### charm-microceph

*Several findings are well-supported by the cited code, but a few misattribute the specific cited line/file, and multi-location or output-based claims often rest on unverified runtime observations.*

- **miscited** (medium) — `ceph_rgw.py`: `TypeError` when `default-pool-size` config is `None`
  - Where: `src/ceph_rgw.py:57`
  - Second reader: The osd_count < config.get("default-pool-size") comparison is at line 62 in the excerpt, not line 57 which is a blank line.
- **miscited** (high) — `snap-channel=""` produces a confusing error message
  - Where: `src/charm.py:654` (`can_upgrade_charm_payload`)
  - Second reader: charm.py:654 shows upgrade_dispatch/configure_app_leader, unrelated to the 'Cannot upgrade from X to Y' message, which actually appears in cluster.py per finding 5's excerpt.

### charm-rabbitmq-k8s

*Most findings are grounded in the shown code, but two citations point to the wrong lines within the correct files (mismatched method/section), and one finding lacks any source excerpt.*

- **miscited** (high) — Notifier service runs as root
  - Where: `src/charm.py:315-324` (Pebble layer, NOTIFIER_SERVICE section)
  - Second reader: Cited lines 315-324 show _on_config_changed body, not the NOTIFIER_SERVICE pebble layer definition (which appears later, around lines 398-406).
- **miscited** (high) — `PeersConnectedEvent`/`ReadyPeersEvent` type annotations use base `EventBase`
  - Where: `src/interface_rabbitmq_peers.py:127-129`, `src/charm.py:559`
  - Second reader: Cited lines 127-129 show on_created's self.on.connected.emit(), not on_changed's self.on.ready.emit(event.unit.name), which is actually at line 146.

### charmed-canonical-cla

*Most findings are well-supported by the exact cited lines, but a few blend legitimate runtime observations with source claims, and a couple of citations (grafana dashboards, lint nits) don't actually show the code needed to substantiate the claim.*

- **miscited** (medium) — `GrafanaDashboardProvider` sends empty dashboards (directory not found)
  - Where: `src/charm.py:56–57` (`GrafanaDashboardProvider` init); `lib/charms/grafana_k8s/v0/grafana_dashboard.py:977`
  - Second reader: Excerpt only shows the default dashboards_path parameter and docstring; the claimed exception-catching/no-reassignment logic is not shown in the cited lines.
- **miscited** (medium) — Unused imports and minor formatting issues
  - Where: `src/charm.py:5` (unused `Optional`), `:154,159` (f-strings without placeholders), `:137` (blank line after docstring)
  - Second reader: Only lines 1-40 are shown, confirming the Optional import exists but not proving it's unused, and lines 154,159,137 are not included in the excerpt at all.

### cos-proxy-operator

*Most findings are well-grounded in the cited code, but several conflate code-level analysis with unverified runtime/deployment observations, and a couple of line-number citations are slightly off.*

- **miscited** (medium) — Pydantic V2 deprecation warnings in `cos_agent.py`
  - Where: `lib/charms/grafana_agent/v0/cos_agent.py:690` (`.json()`), `:430` (`.__fields__`)
  - Second reader: .json() usage at line 690 is confirmed, but no excerpt was provided for the second cited location (line 430, __fields__) to verify that claim.
- **miscited** (medium) — Ambiguous `requires-python = "~=3.8"` specifier
  - Where: `pyproject.toml:5`
  - Second reader: The 'requires-python = "~=3.8"' text is on line 6 per the shown excerpt, not line 5 as cited.

### envoy-operator

*Several findings cite real code accurately (1,11,15,19,20), but many rely on missing citations or runtime logs that source code alone cannot confirm, and one (finding 2) misstates the dependency graph shown in its own citation.*

- **contradicted** (medium) — Non-leader units permanently stuck in `WaitingStatus` after scale-out
  - Where: `src/charm.py:46-58` (all 6 components depend on `leadership_gate`)
  - Second reader: Excerpt shows istio_relations_conflict_detector has no depends_on, so not all 6 components depend on leadership_gate as claimed.
- **miscited** (high) — `metadata.yaml` UID/GID comment misleading after rock migration
  - Where: `metadata.yaml:17`
  - Second reader: Cited line 17 is the upstream-source line, not the uid/gid comment which appears at lines 9-11 in the same excerpt.

### falco-operators

*Several findings are well-supported by the provided code excerpts, but a number rely on unverifiable live-deployment evidence or cite files/attributes not actually present in the excerpts, so overall reliability is mixed.*

- **miscited** (high) — 16. `no_reload_on_change` is always `False` — reload never attempted
  - Where: `falcosidekick-k8s-operator/src/workload.py:58–65`
  - Second reader: The excerpt shows Template.install() with no reload logic, but no attribute named 'no_reload_on_change' appears anywhere in the shown code.
- **miscited** (medium) — 17. Config validation error messages lose specificity
  - Where: `falcosidekick-k8s-operator/src/state.py:77–81`, `config.py:40–41`
  - Second reader: Cited config.py excerpt is falco-operator's CharmConfig (repo URL validation), not the falcosidekick-k8s-operator port validator described in the finding.

### gatus-k8s-operator

*Several findings cite files/lines that do not exist in the checkout (miscited), while others citing src/charm.py are reasonably well supported by the shown code, though runtime/juju-behavior claims can't be settled from source alone.*

- **miscited** (medium) — 7. `config-changed` fires twice per config change (triple `_create_charm_state()` per hook)
  - Where: `deps/paas_charm/charm.py:728` (`restart()`), `deps/paas_charm/charm.py:586` (`is_ready()`), `deps/paas_charm/go/charm.py:79` (`_create_app()`)
  - Second reader: Shown excerpt is unrelated secret-retrieval code, not restart()/is_ready()/_create_app() at the cited lines, so it does not demonstrate the double-hook claim.
  - Unresolved citations: deps/paas_charm/charm.py:728 (file has only 241 lines); deps/paas_charm/charm.py:586 (file has only 241 lines)
- **miscited** (medium) — 11. `restart()` does not catch all exceptions from `is_ready()`'s call chain
  - Where: `src/charm.py:237` (`restart()`); `deps/paas_charm/charm.py:728` (`restart()`)
  - Second reader: Cited src/charm.py:237 is is_ready(), not restart(); the restart() method and its exception handling are not shown in the excerpt.
  - Unresolved citations: deps/paas_charm/charm.py:728 (file has only 241 lines)

### grafana-agent-k8s-operator

*Most findings are grounded in directly shown code, but a few citations point to line ranges that don't include the specific evidence claimed, and several findings blend legitimate code observations with unverifiable runtime deployment claims.*

- **miscited** (high) — K8s resource patch failure status overwritten by mandatory relations check
  - Where: `src/grafana_agent.py:741,756` (`_update_config` clearing status) and `src/grafana_agent.py:648-650` (`_on_k8s_patch_failed`)
  - Second reader: Cited lines 741/756 for _update_config's status-clearing behavior are not shown; excerpt only covers up to line 685.
- **miscited** (medium) — Integration test `test_kubectl_delete_pod` marked `xfail`
  - Where: `tests/integration/test_kubectl_delete.py:26`
  - Second reader: xfail decorator is at line 31, not line 26 as cited, a 5-line discrepancy in the excerpt.

### hydra-operator

*Most findings are well-grounded in the provided charm.py/cli.py/oauth.py excerpts, but several test-gap and external-library claims (1,4,6,9,14,17) lack supporting excerpts, and two citations (18,21) point to the wrong code section.*

- **miscited** (high) — No validation on `cpu`/`memory` config
  - Where: `charmcraft.yaml:184-196`
  - Second reader: Cited lines 184-196 show action parameters (grant-types etc.), not the cpu/memory config section the finding is about.
- **miscited** (medium) — `create-oauth-client` action bypasses grant type validation
  - Where: `src/charm.py:710-718`, `src/cli.py:72-74`
  - Second reader: charm.py confirms direct OAuthClient(**event.params) construction, but the cli.py citation (lines 72-74) shows unrelated kv-parsing code, not the claimed absence of a grant_types validator.

### identity-saml-provider-operator

*Several findings cite line ranges that, when expanded, do not actually contain the code described (NOOP_CONDITIONS, _on_collect_status, _on_public_route_changed), undermining citation accuracy despite plausible claims.*

- **miscited** (high) — `oauth` relation not gated in the holistic handler
  - Where: `src/charm.py:217-230` (`_holistic_handler` / `NOOP_CONDITIONS`); `src/charm.py:233-278` (`_on_collect_status`); `src/integrations.py:152` (`OAuthIntegration.to_env_vars`); `src/charm.py:192` (`_pebble_layer`)
  - Second reader: Excerpts never show NOOP_CONDITIONS or _on_collect_status; only OAuthIntegration.to_env_vars and part of _pebble_layer are visible, not enough to confirm the gating claim.
- **miscited** (high) — `_on_public_route_changed` mutates a library object's private attribute
  - Where: `src/charm.py:264`
  - Second reader: Shown excerpt (lines 229-299) contains no _on_public_route_changed method or any reference to public_route_requirer._relation.

### istio-beacon-k8s-operator

*Several findings are well-supported by directly quoted code, but many rely on runtime/deployment observations or citations to nonexistent/unrelated files, and a few cite NONE AVAILABLE sources entirely.*

- **miscited** (medium) — 2. Remove hook crashes on Juju 3.x when Istio CRDs are absent, blocking scale-down and teardown
  - Where: published rev 74 `_on_remove` (no `planned_units()` guard, unlike HEAD `src/charm.py:225-228`); `deps/canonical_service_mesh/k8s/resource_manager/_resource_manager.py:179-186` (`get_deployed_resources()`)
  - Second reader: HEAD's _on_remove guard is shown correctly, but the core failure mechanism relies on a resource_manager.py path that does not exist in the checkout.
  - Unresolved citations: deps/canonical_service_mesh/k8s/resource_manager/_resource_manager.py:179 (no such file in the checkout)
- **miscited** (medium) — 14. Metrics-proxy pebble service silently skipped
  - Where: `src/charm.py:173-175` (definition), `src/charm.py:233` (call site) — open issue #42
  - Second reader: Line 233 shown in the excerpt is inside _on_remove, not the _setup_proxy_pebble_service call site (which is actually around line 339 per other excerpts).

### istio-ingress-k8s-operator

*Several findings cite source that matches the code well (2,7,9-partial,11,12,16,17), but two citations point to nonexistent files and others cite the wrong line or omit the evidence needed, and multiple findings have no source at all.*

- **miscited** (medium) — Deprecated `cert_handler` v1 library in use, past its own deprecation deadline
  - Where: `lib/charms/observability_libs/v1/cert_handler.py`, used at `src/charm.py:305`
  - Second reader: Cited line 305 is an unrelated conditional check; actual CertHandler instantiation is at line 311, and no library file is shown to substantiate the deprecation warning.
- **miscited** (high) — `tox.ini` static check for library version bumps is broken
  - Where: `tox.ini:55`
  - Second reader: Line 55 cited is just the [testenv:static] header; the actual diff command is on line 62, and the commented-out lib_path line is not shown at all.

### jenkins-k8s-operator

*Several findings rely on unavailable source excerpts or deployment-only observations that cannot be verified from code, and a couple of specific line citations are off by a few lines from the quoted text.*

- **miscited** (high) — 12. `check_now_within_bound_hours` uses deprecated `datetime.utcnow()`
  - Where: `src/timerange.py:82`
  - Second reader: Excerpt shows datetime.utcnow() at line 80, not line 82 as cited; line 82 is the 'if start > end:' check.
- **miscited** (medium) — 14. Spelling error in docstring
  - Where: `src/state.py:124`
  - Second reader: Cited line 124 is 'return None'; the quoted double-period docstring actually appears at line 149 within the shown context.

### karapace-k8s-operator

*Most code-based findings are well supported by the excerpts, but several runtime/ecosystem claims lack any citation and two low-severity findings cite line numbers that don't match the quoted code.*

- **miscited** (high) — 12. `planned_units()` called as a method on an int property — latent TypeError
  - Where: `src/events/provider.py:91`
  - Second reader: The offending planned_units() call appears at line 86 in the excerpt, not line 91 as cited; line 91 is an unrelated is_leader() check.
- **miscited** (medium) — 13. Hardcoded salt for password hashing
  - Where: `src/literals.py:27`
  - Second reader: SALT is defined at literals.py line 25 (not 27, which is SECRETS_APP) and mkpasswd() is at workload.py lines 96-98 (not line 89, which is inside get_version()).

### kfp-operators

*Several findings (2,3,5,11,12) cite no source at all and are unverifiable, while two citations (9,10) point to line ranges that do not contain the quoted/claimed code, making them miscited; the remaining findings are well-supported by matching source excerpts.*

- **miscited** (medium) — All charms use the deprecated `kubernetes_service_patch` v1 library
  - Where: e.g. `charms/kfp-api/src/charm.py:62-66`; used across multiple charms
  - Second reader: Cited lines 62-66 show CONFIG_DIR/SAMPLE_CONFIG constants, not the kubernetes_service_patch import which is actually at line 38.
- **miscited** (medium) — `kfp-api` uses `serialized_data_interface` directly instead of the chisme abstraction
  - Where: `charms/kfp-api/src/charm.py:45-51`
  - Second reader: Cited lines 45-51 show lightkube resource imports, not the serialized_data_interface import which is at lines 53-59.

### kratos-operator

*Several findings are well supported by the cited code, but two citations point to the wrong lines/functions (12,13) and multiple findings lack any real source excerpt, undermining overall citation reliability.*

- **miscited** (medium) — `PeerData.__getitem__` returns `{}` instead of `None` for missing keys
  - Where: `integrations.py:63-67`
  - Second reader: Cited lines 63-67 correspond to __setitem__/pop, not the __getitem__ method (lines 54-59) that actually returns {}.
- **miscited** (high) — `run-migration` action returns an empty error message on Juju 4.x
  - Where: `charm.py:899-900` (action error formatting), `clients.py:56-58`
  - Second reader: Cited charm.py:899-900 and clients.py:56-58 are inside _on_delete_identity_action and get_identity, unrelated to the run-migration action error path.

### kserve-operators

*Several findings are well-supported by precise code citations (2,9,10,16,17), but two are contradicted by the cited code itself (5,15), many rely entirely on unverifiable or runtime evidence with no real citation (3,4,6,7,8,11-14,18-20), so the review's reliability is mixed and requires careful per-finding verification.*

- **contradicted** (high) — 5. Issue #131 (kserve-controller fails to remove) — still active
  - Where: `charms/kserve-controller/src/charm.py:851–873` (`_on_remove`); `charms/kserve-controller/src/charm.py:856–858` (handler init); `charms/kserve-controller/src/charm.py:323` (lazily-created `k8s_resource_handler` property)
  - Second reader: _on_remove uses the k8s_resource_handler/cm_resource_handler *properties*, which lazily instantiate on access, so they cannot be None when passed to _delete_managed_resources.
- **contradicted** (medium) — 15. Pebble layer `level: ready` checks with threshold=3 — confusing startup behaviour
  - Where: `charms/kserve-controller/src/charm.py:194` (`_controller_pebble_layer`); `charms/lws-controller/src/charm.py:186`
  - Second reader: lws-controller excerpt shows the ready/alive checks with no 'threshold' field at all, and the kserve-controller citation (line 194) points to an unrelated observer-list line, not the pebble layer checks.

### kubeflow-profiles-operator

*Most findings are well-supported by the cited code, but several conflate code structure with unverifiable runtime/Juju-dispatch behavior, one has a line-citation mismatch, and one is contradicted by the provider's own observer wiring.*

- **miscited** (medium) — `ingress` relation declared but not implemented — hook is a no-op
  - Where: `metadata.yaml:35-39` (declares `ingress` as `requires`, interface `ingress`) vs `src/charm.py` (no implementation)
  - Second reader: metadata.yaml lines 35-39 are part of provide-cmr-mesh description, not the ingress declaration which actually appears at lines 63-68 in the same excerpt.
- **contradicted** (medium) — `VeleroBackupProvider` logs a warning on every `config-changed` when no relation exists
  - Where: `src/charm.py:151-159`
  - Second reader: profiles_backup is instantiated without refresh_event (lines 152-157), so per VeleroBackupProvider's observers (Finding 10) it does not fire on config_changed/update_status as claimed.

### kyuubi-k8s-operator

*Most findings are well supported by the cited code, but a few (statuses ordering with is_serving_requests, ServiceManager DNS lookup, and the pydantic crash) overreach beyond what the excerpts show, mixing runtime claims with static citations.*

- **miscited** (medium) — Blocked status while workload is running
  - Where: `src/charm.py:201-203` (`_collect_domain_statuses`)
  - Second reader: Cited excerpt never shows is_serving_requests or its ordering relative to BlockedStatus checks, and HTTP 200 observation is runtime.
- **miscited** (medium) — `_collect_domain_statuses` exceeds complexity threshold
  - Where: `src/charm.py:182` (`# noqa: C901`)
  - Second reader: Excerpt shows K8sManager/IntegrationHubManager creation and noqa C901 but not ServiceManager instantiation or its DNS lookup as claimed.

### litmus-operators

*Most code-level findings are accurately cited and verifiable, but several (2, 3, 8, 9, 16, 21, 23) rely on external evidence, runtime behavior, or files not included in the citations.*

- **miscited** (high) — mongodb-k8s uses literal `relation-N` as DB username on relation re-add
  - Where: `auth/src/litmus_auth.py` (receives bad credentials); `deps/litmus_libs/models.py:19` (`DatabaseConfig`); root cause in `mongodb-k8s`
  - Second reader: Cited file only defines DatabaseConfig fields; it says nothing about mongodb-k8s username generation or relation-N behavior.
- **miscited** (high) — Auth unit fails to self-heal after mongodb relation removal and re-add
  - Where: `auth/src/charm.py` (uniter behaviour); `deps/litmus_libs/models.py:19`
  - Second reader: Cited file (models.py) has no bearing on uniter relation-processing behavior claimed in the finding.

### mlflow-operator

*Several findings are well supported by the provided code excerpts, but a few key citations (e.g., update_status wiring, _on_upgrade_charm, _remove_service internals) are not actually shown in the excerpts despite being cited, and several findings lack any excerpt at all.*

- **miscited** (medium) — 2. Scaling down deletes the app's Kubernetes Service, and the charm never restores it
  - Where: `lib/charms/observability_libs/v1/kubernetes_service_patch.py:105` (`self.framework.observe(charm.on.remove, self._remove_service)`) + `:264-288` (`_remove_service`), used from `src/charm.py:352-385` (`def _create_service(self):`)
  - Second reader: Excerpt only shows the observe() registration (70-140); the cited _remove_service body (264-288), _is_patched (216-232) and _patch (165-199) behavior are not shown.
- **miscited** (medium) — 7. `SET PERSIST` and S3 `head_bucket` run on every hook, including every 5-minute `update_status`
  - Where: `src/charm.py:610-658` (`def _ensure_trigger_creation_allowed(self, backend_store_uri: str) -> None:`), `src/charm.py:1162` (`self._ensure_trigger_creation_allowed(self._get_backend_store_uri())`), `src/charm.py:185` (`self.framework.observe(self.on.update_status, self._on_event)`), `src/charm.py:907` (`def _ensure_bucket_exists(self) -> None:`)
  - Second reader: Excerpt for lines '150-220' is truncated at line ~169, never reaching line 185 where update_status is claimed to be bound to _on_event.

### notary-k8s-operator

*Several findings are well-supported by direct code citations (4,7,8), but others rely on runtime/deployment observations or cite files/absences not included in the excerpts, weakening verifiability.*

- **miscited** (medium) — 2. Default channel is ~22 months stale; CI publishes to `0/edge`, not `latest/edge`
  - Where: `.github/workflows/main.yaml` `publish-charm` job (`destination_channel: 0/edge`); `.github/workflows/integration-test.yaml:46` (`juju-channel: 3.6/stable`)
  - Second reader: Excerpt only shows integration-test.yaml (juju-channel 3.6/stable); no excerpt given for main.yaml's destination_channel:0/edge, the key claim.
- **miscited** (medium) — 5. Rejected/revoked CSRs are never reported to the requirer when no cert was issued
  - Where: `src/charm.py:304-321`
  - Second reader: The tls_certificates lib citation is confirmed nonexistent by the review itself, and full-file absence of set_relation_error can't be confirmed from a partial excerpt.
  - Unresolved citations: deps/charmlibs/interfaces/tls_certificates/_tls_certificates.py:3473 (no such file in the checkout)

### parca-k8s-operator

*Code-level claims about charm.py/nginx.py logic are generally well-supported by the excerpts, but several findings rely on live deployment observations (runtime) or cite files/lines that don't actually contain the claimed evidence (miscited).*

- **miscited** (medium) — 10. Non-deterministic nginx config due to `Set` return type
  - Where: `src/nginx.py:167` (call site) and `src/nginx.py:213-216` (`_upstreams_to_addresses` returns `Dict[str, Set[str]]`)
  - Second reader: Key supporting citation (_config.py:487) is explicitly noted as unresolved/nonexistent in the checkout.
  - Unresolved citations: _config.py:487 (no such file in the checkout)
- **miscited** (medium) — 11. Unnecessary full reconcile on every update-status hook
  - Where: `src/charm.py:148` (`reconcile()` called unconditionally from `__init__`)
  - Second reader: Cited lines 113-183 are provider setup in __init__, not the reconcile() call site or update-status handler that the claim is about.

### parca-scrape-target-operator

*Most findings are accurately grounded in the cited code, but one (Finding 7) quotes code absent from its citation and one (Finding 10) attributes a mechanism not supported by the shown validation logic; two findings rightly rest on runtime observations.*

- **miscited** (medium) — Library silently drops units with a missing address; validator is dead code
  - Where: `lib/charms/parca_k8s/v0/parca_scrape.py:798` (and `:803`)
  - Second reader: The quoted 'if unit_name and unit_address: hosts.update(...)' logic does not appear in the cited lines 763-833; only _set_unit_ip and _is_valid_unit_address are shown.
- **contradicted** (medium) — Unreachable targets are silently dropped and misreported as "no targets specified"
  - Where: `src/charm.py:198`
  - Second reader: _validated_address only checks address format (netloc/port), performing no reachability check, so a syntactically valid but unreachable target would not be dropped as claimed.

### pgbouncer-operator

*Most findings are well-supported by their citations, but two (5 and 10) cite line ranges that don't contain the quoted code, and finding 1's core evidence is an observed deployment scenario rather than something source alone confirms.*

- **miscited** (high) — Snap `hold()` has no timeout
  - Where: `src/charm.py:1038–1043` (`_install_snap_packages`)
  - Second reader: Cited lines 1038-1043 show the unit_ip property, not the hold()/ensure() calls which actually appear around lines 1003-1006 in this excerpt.
- **miscited** (high) — Hardcoded version `"3"` instead of a named constant
  - Where: `src/upgrade.py:43`
  - Second reader: Lines 8-78 of upgrade.py show only the DependencyModel class definitions, no such 'version': '3' string; that data appears to live in dependency.json, not this file/line.

### postgresql-k8s-operator

*Several findings are well-supported by directly matching code excerpts, but many rely on unverifiable runtime/deployment claims or lack any cited source at all, and one citation points to the wrong file entirely.*

- **miscited** (high) — `create_user` concatenates password into SQL via f-string (same class of bug as `update_user_password`)
  - Where: `lib/charms/postgresql_k8s/v0/postgresql.py:325,330`
  - Second reader: Citation shows charm.py:1259-1329, not lib/charms/postgresql_k8s/v0/postgresql.py:325,330 (create_user), so the quoted code is absent.
- **miscited** (medium) — `on_deployed_without_trust` status may be overwritten (partial mitigation exists)
  - Where: `src/charm.py:2513-2531` (`get_available_resources`), callers at `src/charm.py:598` and `src/charm.py:680`
  - Second reader: Excerpt only covers lines 2478-2566 (get_available_resources/on_deployed_without_trust); the cited caller lines 598 and 680 are not shown to verify the overwrite claim.

### self-signed-certificates-operator

*Several findings are well-supported by the cited code, but a couple misidentify line numbers and others rest on unverifiable runtime behavior.*

- **miscited** (high) — `_push_ca_cert_to_container` uses "container" terminology but there is no container
  - Where: `src/constants.py:9`, `src/charm.py:424-428`
  - Second reader: Cited constants.py:9 doesn't exist (file has 7 lines) and charm.py:424-428 shows an unrelated method, not CA_CERT_PATH or _push_ca_cert_to_container.
  - Unresolved citations: src/constants.py:9 (file has only 7 lines)
- **miscited** (high) — `_send_ca_cert` creates a new `CertificateTransferProvides` instance on every call
  - Where: `src/charm.py:340`
  - Second reader: Line 340 in the shown excerpt is a logger.info call, not the CertificateTransferProvides instantiation claimed.

### sloth-k8s-operator

*Several findings are well-supported by the cited code, but at least two citations (findings 4 and 6) actually conflict with what the excerpt shows, and a couple of others (3, 7, 15) rest on runtime evidence or missing citations.*

- **contradicted** (medium) — Missing sloth binary leaves charm active but non-functional
  - Where: `sloth.py:344-349` (`version`), `charm.py:212` (`_on_collect_unit_status`), `charm.py:118-147` (`reconcile`)
  - Second reader: Cited reconcile() catches generic Exception at ERROR level around self.sloth.reconcile(), not an ExecError caught at WARNING as claimed, and _generate_rules_from_slo does not appear in the excerpt.
- **contradicted** (high) — Ingress relation declared but never handled
  - Where: `charmcraft.yaml:100-105` (declares `requires: ingress: interface: ingress`), no handler in `charm.py`, `lib/charms/traefik_k8s/v0/traefik_route.py` (447 lines, never imported)
  - Second reader: Cited charmcraft.yaml lines 100-105 show the peers and config sections, not an ingress relation declaration as claimed.

### tempo-operators

*Several findings are well supported by code excerpts, but a number rely entirely on unavailable citations or runtime/log observations, and one finding (13) partially miscites the coordinator location.*

- **miscited** (high) — Duplicate `map` blocks in generated nginx config
  - Where: `coordinated_workers/coordinator.py:1118-1125` (external package), triggered from `coordinator/src/charm.py:276-279`
  - Second reader: The review itself states the cited coordinator.py:1118 file/line does not exist in the checkout; charm.py excerpt shown is unrelated to nginx map duplication.
  - Unresolved citations: coordinated_workers/coordinator.py:1118 (no such file in the checkout)
- **miscited** (medium) — metrics-generator gets ActiveStatus instead of BlockedStatus when remote-write is missing (`all` role)
  - Where: `coordinator/src/charm.py:306-311`, `worker/src/charm.py:58-63`
  - Second reader: Worker excerpt supports the worker ActiveStatus/BlockedStatus split, but the cited coordinator/src/charm.py:306-311 excerpt shows unrelated AppPolicy code, not any ActiveStatus for metrics-generator.

### test_observer

*Most findings are well-grounded in the cited excerpts, but two citations (8 and 11) point to unrelated lines, and several findings rely entirely on unsupplied or runtime evidence.*

- **miscited** (high) — Bare `except Exception` in `version` property
  - Where: `backend/charm/src/charm.py:680`
  - Second reader: Line 680 in the shown excerpt is part of _celery_pebble_layer, not the version property's except-Exception block, which is absent from the excerpt.
- **miscited** (high) — Frontend charm: `_api_url` triggers a side effect from a property
  - Where: `frontend/charm/src/charm.py:143`
  - Second reader: Line 143 is a blank line between unrelated methods; the actual _api_url property with the side effect is defined elsewhere (around line 226+), not shown here.

### traefik-k8s-operator

*Most findings are well-supported by the cited excerpts, but two (9 and 14) cite line ranges that show unrelated code rather than the loop they describe, and several critical/deployment-confirmed claims mix in unverifiable runtime behaviour.*

- **miscited** (high) — `_wipe_ingress_for_all_relations` raises `KeyError` when no ingress relations exist
  - Where: `src/charm.py:1926` (draft cites `1785`; kept as noted, both locations point to the same loop)
  - Second reader: Cited lines 1891-1961 show ingressed_address/_routing_mode properties, not the model.relations[...] loop the finding describes (that loop appears elsewhere, ~line 1785).
- **miscited** (high) — `_wipe_ingress_for_all_relations` misses `traefik-route` relations
  - Where: `src/charm.py:1926`
  - Second reader: Cited lines 1891-1961 don't contain the ingress/ingress-per-unit relations loop; that code is elsewhere (~line 1785 per other excerpts).

### wazuh-server-operator

*Most code-level claims about charm.py, state.py, and certificates_observer.py are well supported by the excerpts, but several loki_push_api.py and cross-class claims cite lines not included in the excerpts, and some findings explicitly rest on unverifiable live/runtime behavior.*

- **miscited** (medium) — `LogProxyConsumer` emits an undefined event, crashing both units on the logging relation
  - Where: `lib/charms/loki_k8s/v1/loki_push_api.py:1742` (also `:1668`, `:1607`, `:1402`)
  - Second reader: Excerpt confirms the emit() call at 1742 but does not show LogProxyEvents/LokiPushApiEvents definitions (1607/1668/1402) needed to prove the missing-attribute claim.
- **miscited** (medium) — `external_hostname` accessed on `CharmBaseWithState` without declaration
  - Where: `src/certificates_observer.py:94`
  - Second reader: Excerpt shows external_hostname usage but not the CharmBaseWithState class declaration proving the attribute is undeclared there.

### blackbox-exporter-k8s-operator

*Most findings are well-grounded in the cited excerpts, but one citation (Finding 2) points to the wrong line for its key claim, and a few findings rely on unshown code or live deployment behavior that source alone cannot confirm.*

- **miscited** (high) — Invalid `probes_file` causes error state instead of blocked
  - Where: `src/scrape_config_builder.py:85`, `src/charm.py:295-301`
  - Second reader: The cited yaml.safe_load call is actually at line 70, not line 85 as claimed; line 85 is an unrelated relabel_configs entry.

### cos-configuration-k8s-operator

*Most findings are well-supported by the cited charm.py/library/test excerpts, but several rest on unverifiable or runtime-only observations (missing excerpts, log-output counts, external tool behavior), and one citation (finding 17) points to the wrong line.*

- **miscited** (medium) — `_common_exit_hook` complexity suppressed with `noqa: C901`
  - Where: `src/charm.py:177`
  - Second reader: Cited line 177 is unrelated code (LokiPushApiConsumer instantiation); the actual noqa: C901 line is 204, within the shown range but not the cited line.

### data-integrator

*Most concrete src/charm.py and lib/data_interfaces.py findings are well-supported by the cited excerpts, but several findings citing deps/dpcharmlibs paths are miscited (files don't exist) and a few runtime-timing claims are treated as static-code facts.*

- **miscited** (high) — `is_topic_value_acceptable` only checks the first 3 characters of a Kafka topic name
  - Where: `deps/dpcharmlibs/interfaces/models.py:507–512`; used at `src/charm.py:301`
  - Second reader: models.py:507-512 doesn't exist in checkout, and cited charm.py:301 is get_status(), not the is_topic_value_acceptable call site (actually line 320).
  - Unresolved citations: deps/dpcharmlibs/interfaces/models.py:507 (no such file in the checkout)

### glauth-k8s-operator

*Most code-structure claims are accurately cited, but several findings blend source evidence with unverifiable runtime observations (timings, logs, live relation data) or cite files not actually included in the excerpts.*

- **miscited** (medium) — 10. MetricsEndpointProvider non-functional — no metrics endpoint configured
  - Where: `src/charm.py:183-185`, `templates/glauth.cfg.j2:52-53`
  - Second reader: Only charm.py instantiation lines were shown; the key evidence citation templates/glauth.cfg.j2:52-53 (api enabled=false) was not provided in the excerpts.

### grafana-agent-operator

*Several findings correctly cite code demonstrating structural issues, but multiple findings blend runtime-only observations (restarts, hook crashes, test failures, deployment paths) into code citations, and a couple citations point to unrelated code sections.*

- **miscited** (high) — `GrafanaAgentCharm` cannot be instantiated directly — undocumented
  - Where: `src/grafana_agent.py:193` (`__new__`)
  - Second reader: Cited lines 158-228 show __init__ logic (PrometheusRemoteWriteConsumer setup), not a __new__ method or TypeError raise as claimed.

### hive-metastore-k8s-operator

*Most findings are plausible and several are directly supported by the cited code, but a few (notably Finding 4) are contradicted by the very excerpt provided, and several other findings lack any cited source at all.*

- **contradicted** (high) — `promote_charm.yaml` is missing `secrets: inherit`
  - Where: `.github/workflows/promote_charm.yaml:23` (`promote-charm` job)
  - Second reader: Line 27 of the cited excerpt explicitly shows 'secrets: inherit' present in promote_charm.yaml.

### hook-service-operator

*Most findings are well-supported by direct code quotes; a few (test-gap findings, and the teardown-path finding) rely on material not present in the given excerpts.*

- **miscited** (medium) — 19. Remove-application path triggers an unnecessary migration check
  - Where: `src/charm.py:480-497` (`_holistic_handler` invoked from relation-broken/stop hooks)
  - Second reader: Cited range shows generic _holistic_handler/_ensure_database_migration logic but not the relation-broken/stop hook invocation claimed in the title.

### jenkins-agent-k8s-operator

*Most findings are plausible but rely heavily on unprovided deployment/test excerpts; one citation (finding 7) misattributes a decorator to the wrong function, and several 'confirmed in deployment' claims are runtime evidence not verifiable from the given source.*

- **contradicted** (high) — 7. `download_jenkins_agent` retry predicate is dead code
  - Where: `src/server.py:50`
  - Second reader: The quoted retry_if_result predicate belongs to server_is_ready (lines 47-53), not download_jenkins_agent, which uses retry_if_exception_type(AgentJarDownloadError) at lines 73-79.

### k6-k8s-operator

*Most findings are grounded in directly-quoted code, but several (esp. 1, 4, 7) blend runtime/deployment claims or cite files/lines not actually shown, reducing overall citation precision.*

- **miscited** (medium) — 4. Unit tests don't cover `K6Api` or `_start_test_if_ready`
  - Where: `src/k6.py:38-49` (`K6Api._request`), `src/k6.py:52-55` (`K6Api.resume`), `src/k6.py:322-337` (`_start_test_if_ready`)
  - Second reader: Claim is about coverage reports and test file mocking behaviour, but only src/k6.py source lines are cited, not the coverage report or test files.

### kafka-benchmark-operator

*Most findings are well-supported by directly quoted code, but a few (notably #1's template evidence and #6's data_models.py citation) point to excerpts that don't actually show what's claimed, and several no-citation runtime/absence findings can't be verified from source alone.*

- **miscited** (medium) — 6. Unhandled `pydantic.ValidationError` on invalid config
  - Where: `lib/charms/data_platform_libs/v0/data_models.py:156` → `src/models.py:77` → `src/charm.py:540`
  - Second reader: cited data_models.py:156 is an unrelated import line, not the self.config_type(**translated_keys) call the finding describes; no code shows the exception path.

### kafka-connect-k8s-operator

*Several findings are well supported by matching code excerpts, but two citations have mismatched line numbers relative to the quoted code, and multiple findings rely on unverifiable runtime observations or missing evidence.*

- **miscited** (high) — Config diff mechanism uses set symmetric difference, causing false-positive restarts
  - Where: `src/charm.py:198-201`
  - Second reader: Lines 198-201 actually contain TLS cert-expiry emit/update code, not the set-diff logic; the quoted diff code is at lines 205-209 in the same excerpt.

### kafka-connect-operator

*Most findings are well-supported by the cited code, but a few rely on runtime/deployment behavior not verifiable from source, and two citations have incorrect line numbers or unsupported files.*

- **miscited** (high) — 21. `metadata.yaml` uses deprecated `series` attribute
  - Where: `metadata.yaml:18`
  - Second reader: Cited line 18 is 'peers:' in the excerpt; the 'series: - noble' lines are actually 15-16.

### kafka-k8s-operator

*Most findings citing concrete code (bugs, dead code, typos, deprecated calls) are well-supported, but several findings blend runtime/deployment/coverage claims with code citations that don't actually show the runtime behavior or absence claimed.*

- **miscited** (medium) — Dead `_on_peer_cluster_broken` handler — never registered
  - Where: `src/events/peer_cluster.py:182-226` (`meta.properties` removal at line 199)
  - Second reader: Citation shows the dead _on_peer_cluster_broken method but not the __init__ event registrations needed to prove it's never wired up.

### kafka-ui-k8s-operator

*Most findings are well-supported by direct code excerpts, but several rely on unprovided sources (finding 2, 3, 11, 12) or on unverifiable runtime/deployment observations (6, 7).*

- **miscited** (low) — `tox -e static` is a no-op; pyright finds 40 real errors
  - Where: `tox.ini` (no `[testenv:static]` section defined)
  - Second reader: tox.ini not cited at all; tls.py:307/389 citations explicitly noted as unresolved (wrong line count), undermining the core claims.
  - Unresolved citations: tls.py:307 (file has only 174 lines); tls.py:389 (file has only 174 lines)

### kubeflow-volumes-operator

*The review mixes legitimate code-level observations with runtime/tool-execution claims that the provided source excerpts cannot settle, and at least one citation (finding 4) points to the wrong line.*

- **miscited** (high) — Non-leader units in a scaled deployment are permanently idle with no workload
  - Where: `src/charm.py:41` — `KubeflowVolumesPebbleService` depends on `leadership_gate`, executed only for the leader unit
  - Second reader: Cited charm.py:41 shows only a constant definition, not the leadership_gate dependency for KubeflowVolumesPebbleService; that dependency appears elsewhere in the file.

### livepatch-k8s-operator

*Most code-level findings are well supported by the cited excerpts, but several rely on unresolved or missing citations (pgsql client.py, state.py line ranges, utils.py internals) and one (finding 14) is directly contradicted by the shown code.*

- **contradicted** (high) — `_on_tracing_endpoint_changed` and `_on_otel_metrics_relation_created` missing null checks
  - Where: `src/charm.py:886` and `src/charm.py:894`
  - Second reader: Cited lines 886 and 894 only call _update_workload_container_config/otel_metrics.publish(); no reference to '.reqeuirer.requesting_protocols' or '.requester' exists in the excerpt.

### maas-site-manager-k8s-operator

*Most code-level findings are directly supported by the cited excerpts, but several findings resting on runtime/deployment observations or missing citations (Findings 1, 2, 4, 5, 17, 18, 20) cannot be fully verified from source alone.*

- **miscited** (medium) — Certificate transfer library v0 fallback is incompatible with `self-signed-certificates`
  - Where: `lib/charms/certificate_transfer_interface/v1/certificate_transfer.py:667-676`; `ProviderUnitDataV0` at line 294
  - Second reader: Excerpt shows fallback uses .chain, not a 'certificate' field, and the cited ProviderUnitDataV0 definition (line 294) is not included.

### mediawiki-k8s-operator

*Several findings rely on unavailable citations or on deployment/runtime observations that source code alone cannot confirm; a few code-based claims are directly supported, and one (finding 6) appears contradicted by the shown self-clearing logic.*

- **contradicted** (medium) — `_check_and_clear_force_reconciliation_flag` race on new unit join
  - Where: `src/charm.py:561` (`_check_and_clear_force_reconciliation_flag`), lines ~582, 589, 596
  - Second reader: The code's `if not app_flag` branch self-clears a unit's own stale flag on its next run, undermining the claim that the flag 'is never read again and persists'.

### notebook-operators

*Most findings are well grounded in the provided code excerpts, but several (runtime behaviors, missing citations, and one clearly mis-pointed line range) weaken overall reliability.*

- **miscited** (medium) — MEDIUM — jupyter-controller: non-conflict K8s ApiErrors propagate as unhandled exceptions
  - Where: `charms/jupyter-controller/src/charm.py:329-353` (`_apply_k8s_resources`), `charms/jupyter-controller/src/charm.py:355-367` (`_on_event`)
  - Second reader: Cited lines 329-353 actually show _on_remove/_on_update_status/_on_event, not _apply_k8s_resources where the GenericCharmRuntimeError wrapping occurs.

### oathkeeper-operator

*Most code-structural claims (missing restart/status calls, hardcoded scheme, regex bug, retry decorators) are well supported by the cited excerpts, but several findings rely on unshown runtime behavior or misattributed line numbers, and three findings have no citation at all.*

- **miscited** (medium) — `_on_forward_auth_relation_removed` unconditionally sets ActiveStatus
  - Where: `src/charm.py:626-627`
  - Second reader: Cited lines 626-627 correspond to _on_forward_auth_proxy_set, not _on_forward_auth_relation_removed (actually at 629-632); second citation 613-614 is also unrelated (inside _on_get_rule_action).

### oidc-gatekeeper-operator

*Several findings are well-supported by directly cited code, but a number rely on runtime logs/observations or lack any source excerpt, and one (Finding 12) cites a range missing the key evidence.*

- **miscited** (medium) — 12. `service_environment` calls `_check_secret()` redundantly
  - Where: `src/charm.py:223` (`self.service_environment` access inside `_oidc_layer`)
  - Second reader: Cited range (188-258) omits both the _check_secret() call inside service_environment (~line176) and the main() call (~line111) needed to show the redundant call.

### opentelemetry-collector-integrator-operator

*Several findings are well-supported by matching code excerpts, but a few misattribute function/line references or rely on unshown code/deployment behavior, and three findings lack any citation at all.*

- **miscited** (medium) — Integrator doesn't validate that secret keys exist — silent relation failure
  - Where: `src/charm.py:84` (`_grant_config_secrets`) and `lib/charms/opentelemetry_collector_integrator/v0/opentelemetry_collector_integrator.py:385-401` (`SecretURI.from_uri`)
  - Second reader: Line 84 in charm.py is inside _create_relation_data, not _grant_config_secrets as claimed; lib excerpt doesn't show the actual key-existence check logic.

### opentelemetry-collector-k8s-operator

*Most code-structural findings are well supported by the cited excerpts, but several findings blend unverifiable runtime/deployment claims or cite missing evidence (charmcraft.yaml, issue tracker) that the excerpts don't cover.*

- **contradicted** (medium) — Dashboard filename accumulation (open #237)
  - Where: `src/integrations.py:429-454`
  - Second reader: Cited code builds a single deterministic filename and opens it in 'w' mode (overwrite), showing no mechanism for prefix accumulation as claimed.

### otel-ebpf-profiler-operator

*Most findings are grounded in directly-quoted code and are accurate, but a few (1, 2, 6, 9) blend runtime/deployment evidence or rely on unresolved external citations, weakening their verifiability from source alone.*

- **miscited** (medium) — Pydantic `__fields__` deprecation in vendored and dependency code
  - Where: `lib/charms/grafana_agent/v0/cos_agent.py:427` and `deps/cosl/interfaces/utils.py:55`
  - Second reader: cos_agent.py:427 __fields__ usage is confirmed, but the cosl/interfaces/utils.py:55 citation could not be resolved, undermining the 'live path' half of the claim.
  - Unresolved citations: deps/cosl/interfaces/utils.py:55 (no such file in the checkout); cosl/interfaces/utils.py:55 (no such file in the checkout)

### prometheus-k8s-operator

*Most code-level claims are verifiable and accurate, but several high-severity findings rely heavily on unverifiable runtime/deployment observations, and one finding (14) is directly contradicted by its own cited code.*

- **contradicted** (high) — 14. `GrafanaSourceProvider` instantiated with `external_url` then re-pointed to `internal_url`
  - Where: `src/charm.py:251` and `src/charm.py:695`
  - Second reader: Cited code shows GrafanaSourceProvider instantiated with unit_datasource_url=self.most_external_url, not source_url=self.external_url as claimed.

### prometheus-pushgateway-k8s-operator

*Several findings are well-supported by directly quoted code (esp. the boolean bug and config-omission issues), but some blend in runtime-only evidence (logs, deployment observations) or cite locations that don't actually contain the specific evidence claimed.*

- **miscited** (medium) — 9. Zombie `prometheus-pushgateway` Pebble service from OCI image never cleaned up
  - Where: `src/charm.py:304-318`; OCI image `ubuntu/prometheus-pushgateway`
  - Second reader: Cited charm.py lines only show layer merge logic, not evidence of a third 'prometheus-pushgateway' service from the OCI image.

### prometheus-scrape-config-k8s-operator

*Most findings tie directly to the cited charm.py logic and are well supported, but a few rely on unshown files, external issue trackers, or runtime-only behavior that the code excerpts cannot confirm.*

- **miscited** (medium) — Test runner requires manual PYTHONPATH setup
  - Where: `tests/unit/conftest.py:11`; `tox.ini`; `charms.just`
  - Second reader: Citation only covers conftest.py; claims about tox.ini and justfile PYTHONPATH content are not shown in the excerpt.

### pyroscope-operators

*Several findings rely on unresolved file citations or unshown excerpts (esp. coordinated_workers/coordinator.py and worker.py), and multiple claims are inherently runtime/deployment observations not verifiable from static code alone.*

- **miscited** (medium) — 7. `Coordinator.__init__` early-return bypassed by charm-level reconcile
  - Where: `coordinated_workers/coordinator.py:429-453`; `coordinator/src/charm.py:132`
  - Second reader: charm.py:132 excerpt confirms unconditional observe_events call, but the library's early-return logic (coordinator.py:429-453) is unresolved/not shown.
  - Unresolved citations: coordinated_workers/coordinator.py:429 (no such file in the checkout)

### snmp-exporter-operator

*Most findings citing charm.py are accurately quoted and structurally verifiable, but findings relying on the missing certificate_transfer library file or unsupplied excerpts (3, 12, 15, 17) are miscited or unverifiable, and deployment-timing claims (4) require runtime confirmation.*

- **miscited** (high) — `CertificateTransferRequires` v1 library vs `send-ca-cert` v0 provider: protocol incompatibility
  - Where: `src/charm.py:24` (`CA_CERT_PATH`); `deps/charmlibs/interfaces/certificate_transfer/_certificate_transfer.py:577-595` (v1 try block swallows v0 fallback)
  - Second reader: The library file cited (deps/charmlibs/.../_certificate_transfer.py) does not exist in the checkout per the review's own note; charm.py excerpt only shows imports/instantiation, not the incompatibility.
  - Unresolved citations: deps/charmlibs/interfaces/certificate_transfer/_certificate_transfer.py:577 (no such file in the checkout)

### spark-history-server-k8s-operator

*Most findings are well-supported by the shown excerpts, but a few citations point to the wrong code block (esp. Finding 1's core claim about update()), and several findings rely on unverifiable runtime observations or missing excerpts.*

- **miscited** (high) — `HistoryServerManager.update()` restarts the workload on every hook — non-idempotent, with a confirmed crash on relation removal
  - Where: `src/managers/history_server.py:126-128` (and `:208-236`), `src/workload.py:85-103`
  - Second reader: Cited lines 126-128 (shown 91-163) are the _s3_conf/_azure_storage_conf properties, not the update() method which actually appears at lines 208-236 in other findings.

### spark-integration-hub-k8s-operator

*Most code-based findings are well supported by their excerpts, but several findings rely on runtime observations or citations that don't fully cover the claimed evidence.*

- **miscited** (medium) — 8. Inconsistent K8s labels: manifests use `generated-by`, secrets use `managed-by`
  - Where: `src/common/utils.py:99,120` vs `src/managers/k8s.py:76`
  - Second reader: Cited k8s.py excerpt doesn't show the INTEGRATION_HUB_LABEL value or the common/utils.py 'generated-by' label the finding relies on.

### sunbeam-charms

*Most cited findings with actual excerpts are accurately quoted and supported, but many findings (CI config, test files, lint tool output) have no source excerpt at all and cannot be verified.*

- **miscited** (medium) — `ironic-conductor-k8s` top-level `import glanceclient` breaks unit test collection
  - Where: `charms/ironic-conductor-k8s/src/api_utils.py:17`
  - Second reader: The cited line 17 is a docstring line; the actual `import glanceclient` is at line 21 in the same excerpt.

### temporal-admin-k8s-operator

*Several findings are well-supported by the cited code (state/relation-write ordering, missing config-changed observer, broad excepts, action result gaps), but a few rely on unverifiable ops/tooling internals, miscite unrelated lines, or lack any citation at all.*

- **miscited** (high) — 6. `TemporalHostInfoRequirer` library has the same unguarded `relation.data[app]` access pattern
  - Where: `lib/charms/temporal_k8s/v0/temporal_host_info.py:146-147`, `:163-164`
  - Second reader: Cited lines 146-147 and 163-164 are docstring/__init__ text, not the .host/.port properties or _on_host_info_relation_changed method described.

### temporal-k8s-operator

*Most findings are well-grounded in the provided code excerpts, but several (esp. #2, #3, #13) cite lines that don't actually contain the claimed behavior, and a few rest on unverifiable runtime or absent-code claims.*

- **miscited** (medium) — `create-authorization-model` action is unusable with JSON — CLI parsing failure
  - Where: `actions.yaml` (`model` parameter), `src/relations/openfga.py:159-160`
  - Second reader: Cited lines 159-160 are from the relation-broken handler, not the action handler at 175-183 where model parsing actually occurs; actions.yaml (central to the claim) isn't shown.

### temporal-ui-k8s-operator

*Most findings are grounded in directly-cited charm.py logic and are well supported, but several rely on unverifiable runtime observations or missing citations (docs/tests), and one citation (finding 8) points to the wrong line.*

- **miscited** (high) — Charmhub docs mismatch — discourse topic #9232 describes admin-tools, not web UI
  - Where: `metadata.yaml:17` → `docs: https://discourse.charmhub.io/t/temporal-ui-documentation-overview/9232`
  - Second reader: Line 17 in metadata.yaml is the maintainers field, not the docs link; the docs URL is actually on line 19 per the same excerpt.

### temporal-worker-k8s-operator

*Several findings are well-supported by direct code excerpts (status/exception handling bugs), but a number of findings cite no source at all or reference files/lines not included in the excerpt, and some runtime/version-specific claims are unverifiable from code alone.*

- **miscited** (medium) — No `WaitingStatus` while waiting for database credentials
  - Where: `src/relations/postgresql.py:33-49`, `src/charm.py:456-465,508-510`
  - Second reader: Only postgresql.py excerpt provided; the charm.py:456-465,508-510 lines central to the 'overwritten status' claim are not included.

### tenant-service-operator

*Most findings are well-supported by the cited code, but a few (notably #17's Grafana citation) point to the wrong line, and several low/medium test- or tooling-based findings have no excerpt to verify at all.*

- **contradicted** (high) — 17. Grafana dashboards directory missing — repeated warnings
  - Where: `src/charm.py:149` (`GrafanaDashboardProvider` initialisation)
  - Second reader: Line 149 in the cited excerpt is DatabaseRequires initialization, not GrafanaDashboardProvider; no such provider appears in the shown range.

### ubuntu-insights-k8s-operator

*Most findings are well-grounded in the cited charm.py excerpts, but a few (migrate/web-port interaction, k8s service ports, web-host disuse, conftest collision) rely on claims the given excerpts don't actually demonstrate.*

- **contradicted** (medium) — `migrate: false` + `web-port=0` silently corrupts the Pebble layer
  - Where: `src/charm.py:185-205` (layer write at `src/charm.py:354`)
  - Second reader: set_ports() at line 202 is called unconditionally regardless of the 'migrate' config value, contradicting the claim that migrate:false causes a different code path/behavior for web-port handling.

### user-verification-service-operator

*Most findings are well-supported by the cited code, but two findings (9 and 11) cite line ranges that don't actually contain the quoted evidence, and several findings lack any source excerpt at all.*

- **miscited** (medium) — `_on_resource_patch_failed` sets unit status directly, bypassing `_on_collect_status`
  - Where: `src/charm.py:235-237`
  - Second reader: Cited lines 235-237 correspond to _on_kratos_webhook_ready/_on_ui_ready, not _on_resource_patch_failed which is actually at lines 230-232.

