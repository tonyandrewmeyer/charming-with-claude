"""Configuration settings."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "review.db"
HOST = "0.0.0.0"
PORT = 8000

# Round -> repo mapping for auto-detection
ROUND_MAP = {
    1: ["grafana-k8s-operator", "kafka-k8s-operator"],
    2: [
        "discourse-k8s-operator",
        "hydra-operator",
        "opensearch-operator",
        "sdcore-amf-operator",
    ],
    3: [
        "traefik-k8s-operator",
        "temporal-k8s-operator",
        "vault-k8s-operator",
        "mongodb-k8s-operator",
    ],
    4: [
        "postgresql-k8s-operator",
        "indico-operator",
        "prometheus-k8s-operator",
        "kratos-operator",
    ],
    5: [
        "loki-k8s-operator",
        "wordpress-k8s-operator",
        "pgbouncer-k8s-operator",
        "oathkeeper-operator",
    ],
    6: [
        "tempo-coordinator-k8s-operator",
        "redis-k8s-operator",
        "synapse-operator",
        "alertmanager-k8s-operator",
        "postgresql-operator",
        "grafana-agent-operator",
        "zookeeper-k8s-operator",
        "seldon-core-operator",
    ],
    7: [
        "pgbouncer-operator",
        "trino-k8s-operator",
        "cos-proxy-operator",
        "mlflow-operator",
    ],
    8: [
        "identity-platform-admin-ui-operator",
        "cos-configuration-k8s-operator",
        "superset-k8s-operator",
        "sdcore-nms-operator",
    ],
    9: [
        "self-signed-certificates-operator",
        "gunicorn-k8s-operator",
        "openfga-operator",
        "mimir-coordinator-k8s-operator",
    ],
    10: [
        "hardware-observer-operator",
        "kubeflow-profiles-operator",
        "nginx-ingress-integrator-operator",
        "content-cache-k8s-operator",
    ],
}

# Filename -> repo name mapping
FILE_REPO_MAP = {
    "skill_validation_grafana.md": "grafana-k8s-operator",
    "skill_validation_kafka.md": "kafka-k8s-operator",
    "skill_validation_discourse.md": "discourse-k8s-operator",
    "skill_validation_hydra.md": "hydra-operator",
    "skill_validation_opensearch.md": "opensearch-operator",
    "skill_validation_sdcore_amf.md": "sdcore-amf-operator",
    "skill_validation_loki.md": "loki-k8s-operator",
    "skill_validation_wordpress.md": "wordpress-k8s-operator",
    "skill_validation_pgbouncer.md": "pgbouncer-k8s-operator",
    "skill_validation_oathkeeper.md": "oathkeeper-operator",
    "skill_validation_traefik.md": "traefik-k8s-operator",
    "skill_validation_temporal.md": "temporal-k8s-operator",
    "skill_validation_vault.md": "vault-k8s-operator",
    "skill_validation_mongodb.md": "mongodb-k8s-operator",
    "skill_validation_postgresql.md": "postgresql-k8s-operator",
    "skill_validation_indico.md": "indico-operator",
    "skill_validation_prometheus.md": "prometheus-k8s-operator",
    "skill_validation_kratos.md": "kratos-operator",
    "skill_validation_tempo_coordinator.md": "tempo-coordinator-k8s-operator",
    "skill_validation_redis.md": "redis-k8s-operator",
    "skill_validation_synapse.md": "synapse-operator",
    "skill_validation_alertmanager.md": "alertmanager-k8s-operator",
    "skill_validation_postgresql_vm.md": "postgresql-operator",
    "skill_validation_grafana_agent.md": "grafana-agent-operator",
    "skill_validation_zookeeper.md": "zookeeper-k8s-operator",
    "skill_validation_seldon.md": "seldon-core-operator",
    "skill_validation_pgbouncer_vm.md": "pgbouncer-operator",
    "skill_validation_trino.md": "trino-k8s-operator",
    "skill_validation_cos_proxy.md": "cos-proxy-operator",
    "skill_validation_mlflow.md": "mlflow-operator",
    "skill_validation_identity_admin_ui.md": "identity-platform-admin-ui-operator",
    "skill_validation_cos_configuration.md": "cos-configuration-k8s-operator",
    "skill_validation_superset.md": "superset-k8s-operator",
    "skill_validation_sdcore_nms.md": "sdcore-nms-operator",
    "skill_validation_self_signed_certs.md": "self-signed-certificates-operator",
    "skill_validation_gunicorn.md": "gunicorn-k8s-operator",
    "skill_validation_openfga.md": "openfga-operator",
    "skill_validation_mimir_coordinator.md": "mimir-coordinator-k8s-operator",
    "skill_validation_hardware_observer.md": "hardware-observer-operator",
    "skill_validation_kubeflow_profiles.md": "kubeflow-profiles-operator",
    "skill_validation_nginx_ingress.md": "nginx-ingress-integrator-operator",
    "skill_validation_content_cache.md": "content-cache-k8s-operator",
}
