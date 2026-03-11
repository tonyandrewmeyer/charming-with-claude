# 🤖 Copilot CLI Session

> **Session ID:** `157f1aac-7235-4abb-a09f-6b5fa9d7b307`
> **Duration:** 9m 58s
> **Exported:** 3/11/2026, 4:02:17 PM

<sub>⏱️ 4s</sub>

### 👤 User

Upgrade this charm's ops usage. There is a skill available for this.

---

<sub>⏱️ 11s</sub>

### ✅ `bash`

**Check ops version and dependencies**

$ cd /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s && cat pyproject.toml

<details>
<summary>142 lines</summary>

```
# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

[project]
name = "discourse-k8s-operator"
version = "0.0.0"
description = "Discourse is the modern forum for your community."
readme = "README.md"
requires-python = ">=3.8"
classifiers = [
  "Programming Language :: Python :: 3 :: Only",
  "Programming Language :: Python :: 3.8",
  "Programming Language :: Python :: 3.9",
  "Programming Language :: Python :: 3.10",
  "Programming Language :: Python :: 3.11",
  "Programming Language :: Python :: 3.12",
  "Programming Language :: Python :: 3.13",
  "Programming Language :: Python :: 3.14",
]
dependencies = [
  "cosl==1.6.0",
  "jsonschema==4.23.0",
  "ops==2.23.2",
  "pydantic==2.10.6",
]

[dependency-groups]
fmt = [
  "ruff",
]
lint = [
  "boto3",
  "bs4",
  "codespell",
  "jubilant==1.7.0",
  "mypy",
  "pep8-naming",
  "psycopg2-binary",
  "pytest",
  "pytest-asyncio",
  "pytest-operator",
  "python-magic",
  "requests",
  "ruff",
  "types-pyyaml",
  "types-requests",
]
unit = [
  "coverage[toml]",
  "ops[testing]",
  "pytest",
]
coverage-report = [
  "coverage[toml]",
  "pytest",
]
static = [
  "bandit[toml]",
]
integration = [
  "allure-pytest>=2.8.18",
  "allure-pytest-collection-report @ git+https://github.com/canonical/data-platform-workflows@v24.0.0#subdirectory=python/pytest_plugins/allure_pytest_collection_report",
  "boto3",
  "bs4",
  "debugpy",
  "jubilant==1.7.0",
  "protobuf==5.29.6",
  "psycopg2-binary",
  "pytest",
  "requests",
  "saml-test-helper @ git+https://github.com/canonical/saml-test-idp.git",
]

[tool.uv]
package = false

[tool.ruff]
target-version = "py310"
line-length = 99

# enable ruff linters:
#   A flake8-builtins
#   B flake8-bugbear
# CPY flake8-copyright
#   D pydocstyle
# E/W pycodestyle
#   F Pyflakes
#   I isort
#   N pep8-naming
# RUF Ruff-specific rules
#   S flake8-bandit
# SIM flake8-simplify
#  TC flake8-type-checking
#  UP pyupgrade
lint.select = [ "A", "B", "C", "CPY", "D", "E", "F", "I", "N", "RUF", "S", "SIM", "TC", "UP", "W" ]
lint.ignore = [
  "B904",
  "D107",
  "D203",
  "D204",
  "D205",
  "D213",
  "D215",
  "D400",
  "D404",
  "D406",
  "D407",
  "D408",
  "D409",
  "D413",
  "E501",
  "S105",
  "S603",
  "TC002",
  "TC006",
  "UP006",
  "UP007",
  "UP035",
  "UP045",
]
lint.per-file-ignores."tests/*" = [ "B011", "D100", "D101", "D102", "D103", "D104", "D212", "D415", "D417", "S" ]
lint.flake8-copyright.author = "Canonical Ltd."
lint.flake8-copyright.min-file-size = 1
lint.flake8-copyright.notice-rgx = "Copyright\\s\\d{4}([-,]\\d{4})*\\s+"
lint.mccabe.max-complexity = 10
lint.pydocstyle.convention = "google"

[tool.codespell]
skip = "build,lib,venv,icon.svg,.tox,.git,.mypy_cache,.ruff_cache,.coverage,htmlcov,uv.lock,grafana_dashboards"

[tool.pytest.ini_options]
minversion = "6.0"
log_cli_level = "INFO"
pythonpath = [ "lib", "src" ]

[tool.coverage.run]
branch = true

[tool.coverage.report]
fail_under = 80
show_missing = true

[tool.mypy]
ignore_missing_imports = true
explicit_package_bases = true
namespace_packages = true
check_untyped_defs = true

[tool.bandit]
exclude_dirs = [ "/venv/" ]

[tool.bandit.assert_used]
skips = [ "*tests/*.py" ]
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 10s</sub>

### ✅ `glob`

**/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s**

"src/**/*.py" in /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s

```
/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s/src/database.py
/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s/src/charm.py
/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s/src/oauth_observer.py
/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s/src/constants.py
```


---

<sub>⏱️ 10s</sub>

### ✅ `glob`

**/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s**

"tests/**/*.py" in /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s

<details>
<summary>15 matches</summary>

```
/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s/tests/__init__.py
/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s/tests/unit_harness/__init__.py
/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s/tests/unit_harness/test_charm.py
/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s/tests/unit_harness/helpers.py
/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s/tests/unit/test_charm.py
/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s/tests/unit/conftest.py
/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s/tests/integration/test_saml.py
/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s/tests/integration/__init__.py
/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s/tests/integration/test_oauth.py
/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s/tests/integration/types.py
/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s/tests/integration/test_db_migration.py
/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s/tests/integration/test_charm.py
/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s/tests/integration/conftest.py
/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s/tests/integration/test_users.py
/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s/tests/conftest.py
```

</details>


---

<sub>⏱️ 16s</sub>

### ✅ `bash`

**Read main charm file**

$ cd /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s && cat src/charm.py

<details>
<summary>8 lines</summary>

```
Output too large to read at once (36.3 KB). Saved to: /tmp/copilot-tool-output-1773197554839-es0v70.txt
Consider using tools like grep (for searching), head/tail (for viewing start/end), view with view_range (for specific sections), or jq (for JSON) to examine portions of the output.

Preview (first 500 chars):
#!/usr/bin/env python3
# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

""
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 16s</sub>

### ✅ `bash`

**Read config.yaml**

$ cd /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s && cat config.yaml

<details>
<summary>151 lines</summary>

```
# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.
options:
  augment_cors_origin:
    type: boolean
    description: |
      Appends external_hostname (with http/https) and s3_cdn_url to the list of
      allowed CORS origins. Has no effect if 'cors_origin' is "*". 
      To rely only on automatic cors origins, set 'cors_origin' to an empty string.
    default: true
  cors_origin:
    type: string
    description: |
      Comma-separated list of allowed CORS origins. Defaults to "*", allowing all
      origins. To restrict access, provide specific origins or set to an empty string
      to rely solely on 'augment_cors_origin' if enabled.
    default: ""
  developer_emails:
    type: string
    description: "Comma delimited list of email addresses that should have developer level access."
    default: ""
  enable_cors:
    type: boolean
    description: "Enable Cross-origin Resource Sharing (CORS) at the application level (required for SSO)."
    default: true
  external_hostname:
    type: string
    description: "External hostname this discourse instance responds to. Defaults to application name."
    default: ""
  force_https:
    type: boolean
    description: Configure Discourse to use https.
    default: false
  force_saml_login:
    type: boolean
    description: "Force SAML login (full screen, no local database logins)."
    default: false
  max_category_nesting:
    type: int
    description: "Maximum category nesting allowed. Minimum is 2, maximum is 3."
    default: 2
  saml_sync_groups:
    type: string
    description: "Comma-separated list of groups to sync from SAML provider."
    default: ""
  smtp_address:
    type: string
    description: "Hostname / IP that should be used to send SMTP mail."
    default: ""
  smtp_authentication:
    type: string
    description: "Type of smtp authentication to use. Valid values: none, login, plain, cram_md5."
    default: "none"
  smtp_domain:
    type: string
    description: "Hostname that email sent by this discourse should appear to come from."
    default: ""
  smtp_enable_start_tls:
    type: string
    description: "Enable TLS encryption for smtp connections."
    default: "true"
  smtp_force_tls:
    type: string
    description: "Force implicit TLS as per RFC 8314 3.3."
    default: "false"
  smtp_openssl_verify_mode:
    type: string
    description: "Should discourse verify SSL certs."
    default: "none"
  smtp_password:
    type: string
    description: "Password to use when sending mail via SMTP."
    default: ""
  smtp_port:
    type: int
    description: "Port to use when connecting to SMTP server."
    default: 587
  smtp_username:
    type: string
    description: "Username to use when sending mail via SMTP."
    default: ""
  s3_access_key_id:
    type: string
    description: |
      The S3 access key ID to use.

      Sets DISCOURSE_S3_ACCESS_KEY_ID.
      Required if s3_enabled is true.
    default: ""
  s3_backup_bucket:
    type: string
    description: |
      The S3 bucket to use for backups.

      Sets DISCOURSE_S3_BACKUP_BUCKET.
      Also sets DISCOURSE_BACKUP_LOCATION=s3.
    default: ""
  s3_bucket:
    type: string
    description: |
      The S3 bucket to use.

      Sets DISCOURSE_S3_BUCKET.
      Required if s3_enabled is true.
    default: ""
  s3_cdn_url:
    type: string
    description: |
      The S3 Content Delivery Network URL.

      Sets DISCOURSE_S3_CDN_URL.
    default: ""
  s3_enabled:
    type: boolean
    description: |
      Store uploaded objects in an S3-compatible object storage service instead of a local directory.

      If true, sets DISCOURSE_USE_S3=true.
      Check https://meta.discourse.org/t/using-object-storage-for-uploads-s3-clones/148916 for more details.
    default: false
  s3_endpoint:
    type: string
    description: |
      The S3 endpoint to use.  This may be a non-Amazon S3-compatible endpoint.

      Sets DISCOURSE_S3_ENDPOINT
    default: "https://s3.amazonaws.com"
  s3_region:
    type: string
    description: |
      The S3 region to use.

      Sets DISCOURSE_S3_REGION.
      Required if s3_enabled is true.
    default: ""
  s3_secret_access_key:
    type: string
    description: |
      The S3 secret key to use.

      Sets DISCOURSE_S3_SECRET_ACCESS_KEY.
      Required if s3_enabled is true.
    default: ""
  s3_install_cors_rule:
    type: boolean
    description: |
      Will discourse set cors rule on the S3 bucket.

      Sets DISCOURSE_S3_INSTALL_CORS_RULE
    default: true
  throttle_level:
    type: string
    description: "Throttle level - blocks excessive usage by ip. Accepted values: none, permissive, strict."
    default: none
  sidekiq_max_memory:
    description: Maximum memory for sidekiq in megabytes. This configuration
      will set the UNICORN_SIDEKIQ_MAX_RSS environment variable.
    type: int
    default: 1000
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 16s</sub>

### ✅ `bash`

**Check for rockcraft.yaml**

$ cd /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s && ls discourse_rock/

```
bundler  patches  rockcraft.yaml  scripts
<exited with exit code 0>
```


---

<sub>⏱️ 20s</sub>

### ✅ `view`

**/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s/src/charm.py**

/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s/src/charm.py (lines 1-100)

<details>
<summary>100 lines</summary>

```
1. #!/usr/bin/env python3
2. # Copyright 2026 Canonical Ltd.
3. # See LICENSE file for licensing details.
4. 
5. """Charm for Discourse on kubernetes."""
6. 
7. import base64
8. import hashlib
9. import logging
10. import os.path
11. import secrets
12. import string
13. import typing
14. from collections import namedtuple
15. 
16. import ops
17. from charms.data_platform_libs.v0.data_interfaces import (
18.     DatabaseCreatedEvent,
19.     DatabaseEndpointsChangedEvent,
20. )
21. from charms.grafana_k8s.v0.grafana_dashboard import GrafanaDashboardProvider
22. from charms.loki_k8s.v0.loki_push_api import LogProxyConsumer
23. from charms.nginx_ingress_integrator.v0.nginx_route import require_nginx_route
24. from charms.prometheus_k8s.v0.prometheus_scrape import MetricsEndpointProvider
25. from charms.redis_k8s.v0.redis import RedisRelationCharmEvents, RedisRequires
26. from charms.rolling_ops.v0.rollingops import RollingOpsManager
27. from charms.saml_integrator.v0.saml import (
28.     DEFAULT_RELATION_NAME,
29.     SamlDataAvailableEvent,
30.     SamlRequires,
31. )
32. from ops.charm import ActionEvent, CharmBase, HookEvent, RelationBrokenEvent
33. from ops.main import main
34. from ops.model import ActiveStatus, BlockedStatus, MaintenanceStatus, WaitingStatus
35. from ops.pebble import ExecError, ExecProcess, Plan
36. 
37. from constants import (
38.     CONTAINER_APP_USERNAME,
39.     CONTAINER_NAME,
40.     DATABASE_RELATION_NAME,
41.     DISCOURSE_PATH,
42.     LOG_PATHS,
43.     MAX_CATEGORY_NESTING_LEVELS,
44.     OAUTH_RELATION_NAME,
45.     PROMETHEUS_PORT,
46.     REQUIRED_S3_SETTINGS,
47.     SCRIPT_PATH,
48.     SERVICE_NAME,
49.     SERVICE_PORT,
50.     SETUP_COMPLETED_FLAG_FILE,
51.     THROTTLE_LEVELS,
52. )
53. from database import DatabaseHandler
54. from oauth_observer import OAuthObserver
55. 
56. logger = logging.getLogger(__name__)
57. 
58. S3Info = namedtuple("S3Info", ["enabled", "region", "bucket", "endpoint"])
59. 
60. INVALID_CORS_MESSAGE = (
61.     "invalid CORS config, `augment_cors_origin` must be enabled or `cors_origin` must be non-empty"  # pylint: disable=line-too-long
62. )
63. 
64. 
65. class MissingRedisRelationDataError(Exception):
66.     """Custom exception to be raised in case of malformed/missing redis relation data."""
67. 
68. 
69. class DiscourseCharm(CharmBase):
70.     """Charm for Discourse on kubernetes."""
71. 
72.     # pylint: disable=too-many-instance-attributes
73.     # All attributes are necessary for the charm functionality
74. 
75.     on = RedisRelationCharmEvents()
76. 
77.     def __init__(self, *args):
78.         """Initialize defaults and event handlers."""
79.         super().__init__(*args)
80. 
81.         self._database = DatabaseHandler(self, DATABASE_RELATION_NAME)
82.         self._oauth = OAuthObserver(self, self._setup_and_activate, self._get_external_hostname)
83. 
84.         self.framework.observe(
85.             self._database.database.on.database_created, self._on_database_created
86.         )
87.         self.framework.observe(
88.             self._database.database.on.endpoints_changed, self._on_database_endpoints_changed
89.         )
90.         self.framework.observe(
91.             self.on[DATABASE_RELATION_NAME].relation_broken,
92.             self._on_database_relation_broken,
93.         )
94. 
95.         self._require_nginx_route()
96.         self.saml = SamlRequires(self)
97.         self.framework.observe(self.saml.on.saml_data_available, self._on_saml_data_available)
98. 
99.         self.framework.observe(self.on.start, self._on_start)
100.         self.framework.observe(self.on.upgrade_charm, self._on_upgrade_charm)
```

</details>


---

<sub>⏱️ 20s</sub>

### ✅ `bash`

**Check unit tests**

$ cd /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s && cat tests/unit/conftest.py && echo "---" && head -100 tests/unit/test_charm.py

<details>
<summary>170 lines</summary>

```
# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

"""Discourse K8s operator charm fixtures."""

import pytest
from ops import testing

from charm import CONTAINER_NAME
from constants import DATABASE_NAME


@pytest.fixture(name="base_state")
def base_state_fixture(discourse_container, postgresql_relation, redis_relation):
    input_state = {
        "leader": True,
        "config": {},
        "containers": {discourse_container},
        "relations": [postgresql_relation, redis_relation],
    }
    yield input_state


@pytest.fixture(name="discourse_container")
def discourse_container_fixture():
    """Discourse container fixture."""
    yield testing.Container(
        name=CONTAINER_NAME,
        can_connect=True,
        execs=[
            testing.Exec(
                command_prefix=[
                    "/srv/discourse/app/bin/bundle",
                    "exec",
                    "rake",
                    "--trace",
                    "db:migrate",
                ],
                return_code=0,
                stdout="Migration successful\n",
                stderr="",
            ),
            testing.Exec(
                command_prefix=["/srv/discourse/app/bin/rails", "runner"],
                return_code=0,
                stdout="successful\n",
                stderr="",
            ),
        ],
    )  # type: ignore[call-arg]


@pytest.fixture(name="postgresql_relation")
def postgresql_relation_fixture():
    """Postgresql relation fixture."""
    relation_data = {
        "database": DATABASE_NAME,
        "endpoints": "dbhost:5432,dbhost-2:5432",
        "password": "somepasswd",  # nosec
        "username": "someuser",
    }
    yield testing.Relation(
        endpoint="database",
        interface="postgresql_client",
        remote_app_data=relation_data,
    )


@pytest.fixture(name="redis_relation")
def redis_relation_fixture():
    """Redis relation fixture."""
    relation_data = {
        0: {
            "hostname": "redis-host",
            "port": "1010",
        },
    }
    yield testing.Relation(
        endpoint="redis",
        interface="redis",
        remote_app_name="redis",
        remote_units_data=relation_data,
        remote_app_data={"leader-host": "redis-host"},
    )
---
# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

"""Discourse K8s operator charm unit tests."""

import pytest
from ops import testing
from ops.model import ActiveStatus, BlockedStatus

from charm import (
    CONTAINER_NAME,
    INVALID_CORS_MESSAGE,
    OAUTH_RELATION_NAME,
    SERVICE_NAME,
    DiscourseCharm,
)


@pytest.mark.parametrize(
    "config, expected_origin, expected_status",
    [
        pytest.param(
            {
                "cors_origin": "*",
                "augment_cors_origin": True,
                "external_hostname": "example.com",
                "force_https": True,
                "s3_cdn_url": "https://cdn.test",
            },
            "*",
            ActiveStatus(),
            id="Wildcard disables augmentation",
        ),
        pytest.param(
            {
                "cors_origin": "",
                "augment_cors_origin": False,
                "external_hostname": "example.com",
                "force_https": True,
                "s3_cdn_url": "https://cdn.test",
            },
            "*",
            BlockedStatus(INVALID_CORS_MESSAGE),
            id="Raise error when invalid CORS config",
        ),
        pytest.param(
            {
                "cors_origin": "",
                "augment_cors_origin": True,
                "external_hostname": "example.com",
                "force_https": True,
                "s3_cdn_url": "",
            },
            "https://example.com",
            ActiveStatus(),
            id="Augment only with external_hostname (HTTPS)",
        ),
        pytest.param(
            {
                "cors_origin": "",
                "augment_cors_origin": True,
                "external_hostname": "",
                "force_https": True,
                "s3_cdn_url": "",
            },
            "https://discourse-k8s",
            ActiveStatus(),
            id="Augment with external_hostname not explicitly defined",
        ),
        pytest.param(
            {
                "cors_origin": "",
                "augment_cors_origin": True,
                "external_hostname": "example.com",
                "force_https": False,
                "s3_cdn_url": "https://cdn.test",
            },
            "http://example.com,https://cdn.test",
            ActiveStatus(),
            id="Augment with both external_hostname (HTTP) and s3_cdn_url",
        ),
        pytest.param(
            {
                "cors_origin": "https://custom.origin",
                "augment_cors_origin": False,
                "external_hostname": "example.com",
                "force_https": True,
                "s3_cdn_url": "https://cdn.test",
            },
            "https://custom.origin",
            ActiveStatus(),
            id="User-defined cors_origin, no augmentation",
        ),
        pytest.param(
            {
                "cors_origin": "https://custom.origin",
                "augment_cors_origin": True,
                "external_hostname": "example.com",
                "force_https": True,
                "s3_cdn_url": "https://cdn.test",
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 25s</sub>

### ✅ `view`

**/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s/src/charm.py**

/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s/src/charm.py (lines 100-300)

<details>
<summary>201 lines</summary>

```
100.         self.framework.observe(self.on.upgrade_charm, self._on_upgrade_charm)
101.         self.framework.observe(self.on.discourse_pebble_ready, self._on_discourse_pebble_ready)
102.         self.framework.observe(self.on.config_changed, self._on_config_changed)
103.         self.framework.observe(self.on.promote_user_action, self._on_promote_user_action)
104.         self.framework.observe(self.on.create_user_action, self._on_create_user_action)
105.         self.framework.observe(self.on.anonymize_user_action, self._on_anonymize_user_action)
106. 
107.         self.redis = RedisRequires(self)
108.         self.framework.observe(self.on.redis_relation_updated, self._redis_relation_changed)
109. 
110.         self._metrics_endpoint = MetricsEndpointProvider(
111.             self, jobs=[{"static_configs": [{"targets": [f"*:{PROMETHEUS_PORT}"]}]}]
112.         )
113.         self._logging = LogProxyConsumer(
114.             self, relation_name="logging", log_files=LOG_PATHS, container_name=CONTAINER_NAME
115.         )
116.         self._grafana_dashboards = GrafanaDashboardProvider(self)
117. 
118.         self.restart_manager = RollingOpsManager(
119.             charm=self, relation="restart", callback=self._on_rolling_restart
120.         )
121. 
122.     def _on_start(self, _: ops.StartEvent) -> None:
123.         """Handle start event.
124. 
125.         Args:
126.             event: Event triggering the start event handler.
127.         """
128.         self._setup_and_activate()
129. 
130.     def _on_upgrade_charm(self, _: ops.UpgradeCharmEvent) -> None:
131.         """Handle upgrade charm event.
132. 
133.         Args:
134.             event: Event triggering the upgrade charm event handler.
135.         """
136.         self.on[self.restart_manager.name].acquire_lock.emit()
137. 
138.     def _on_discourse_pebble_ready(self, _: ops.PebbleReadyEvent) -> None:
139.         """Handle discourse pebble ready event.
140. 
141.         Args:
142.             event: Event triggering the discourse pebble ready event handler.
143.         """
144.         self._setup_and_activate()
145. 
146.     def _redis_relation_changed(self, _: HookEvent) -> None:
147.         """Handle redis relation changed event.
148. 
149.         Args:
150.             event: Event triggering the redis relation changed event handler.
151.         """
152.         self._setup_and_activate()
153. 
154.     def _on_database_created(self, _: DatabaseCreatedEvent) -> None:
155.         """Handle database created.
156. 
157.         Args:
158.             event: Event triggering the database created handler.
159.         """
160.         self._setup_and_activate()
161. 
162.     def _on_database_endpoints_changed(self, _: DatabaseEndpointsChangedEvent) -> None:
163.         """Handle endpoints change.
164. 
165.         Args:
166.             event: Event triggering the endpoints changed handler.
167.         """
168.         self._execute_migrations()
169.         if self._are_relations_ready():
170.             self._activate_charm()
171. 
172.     def _on_database_relation_broken(self, _: RelationBrokenEvent) -> None:
173.         """Handle broken relation.
174. 
175.         Args:
176.             event: Event triggering the broken relation handler.
177.         """
178.         self.model.unit.status = WaitingStatus("Waiting for database relation")
179.         self._stop_service()
180. 
181.     def _on_config_changed(self, _: HookEvent) -> None:
182.         """Handle config change.
183. 
184.         Args:
185.             event: Event triggering the config change handler.
186.         """
187.         self._configure_pod()
188. 
189.     def _on_saml_data_available(self, _: SamlDataAvailableEvent) -> None:
190.         """Handle SAML data available."""
191.         self._configure_pod()
192. 
193.     def _on_rolling_restart(self, _: ops.EventBase) -> None:
194.         """Handle rolling restart event.
195. 
196.         Args:
197.             event: Event triggering the discourse rolling restart event handler.
198.         """
199.         self._setup_and_activate()
200. 
201.     def _setup_and_activate(self) -> None:
202.         """Set up discourse, configure the pod and eventually activate the charm."""
203.         if not self._is_setup_completed():
204.             self._set_up_discourse()
205.         self._configure_pod()
206.         if self._are_relations_ready():
207.             self._activate_charm()
208. 
209.     def _require_nginx_route(self) -> None:
210.         """Create minimal ingress configuration."""
211.         require_nginx_route(
212.             charm=self,
213.             service_hostname=self._get_external_hostname(),
214.             service_name=self.app.name,
215.             service_port=SERVICE_PORT,
216.             session_cookie_max_age=3600,
217.         )
218. 
219.     def _get_external_hostname(self) -> str:
220.         """Extract and return hostname from site_url or default to [application name].
221. 
222.         Returns:
223.             The site hostname defined as part of the site_url configuration or a default value.
224.         """
225.         return (
226.             typing.cast(str, self.config["external_hostname"])
227.             if self.config["external_hostname"]
228.             else self.app.name
229.         )
230. 
231.     def _get_cors_origin(self) -> str:
232.         """Return the combined CORS origins.
233. 
234.         Return the combined CORS origins from 'cors_origin' and, if enabled,
235.         'external_hostname' and 's3_cdn_url'. Skips augmentation if 'cors_origin' is '*'.
236. 
237.         Returns:
238.             Comma-separated CORS origins string.
239.         """
240.         user_value = str(self.config.get("cors_origin", "")).strip()
241.         if user_value == "*":
242.             # No need to augment if all origins allowed
243.             return "*"
244. 
245.         origins: set[str] = set()
246.         if user_value:
247.             origins.update(s for s in (o.strip() for o in user_value.split(",")) if s)
248. 
249.         if self.config.get("augment_cors_origin"):
250.             ext = self._get_external_hostname()
251.             if ext:
252.                 scheme = "https" if self.config.get("force_https") else "http"
253.                 origins.add(f"{scheme}://{ext}")
254. 
255.             cdn = str(self.config.get("s3_cdn_url"))
256.             if cdn:
257.                 origins.add(cdn)
258. 
259.         return ",".join(sorted(origins)) if origins else ""
260. 
261.     def _is_setup_completed(self) -> bool:
262.         """Check if the _set_up_discourse process has finished.
263. 
264.         Returns:
265.             True if the _set_up_discourse process has finished.
266.         """
267.         container = self.unit.get_container(CONTAINER_NAME)
268.         return container.can_connect() and container.exists(SETUP_COMPLETED_FLAG_FILE)
269. 
270.     def _set_setup_completed(self) -> None:
271.         """Mark the _set_up_discourse process as completed."""
272.         container = self.unit.get_container(CONTAINER_NAME)
273.         container.push(SETUP_COMPLETED_FLAG_FILE, "", make_dirs=True)
274. 
275.     def _is_config_valid(self) -> bool:
276.         """Check that the provided config is valid.
277. 
278.         Returns:
279.             If config is valid.
280.         """
281.         errors = []
282. 
283.         if (
284.             self.config.get("enable_cors")
285.             and self.config.get("cors_origin") == ""
286.             and not self.config.get("augment_cors_origin")
287.         ):
288.             errors.append(INVALID_CORS_MESSAGE)
289. 
290.         if self.config["throttle_level"] not in THROTTLE_LEVELS:
291.             errors.append(f"throttle_level must be one of: {' '.join(THROTTLE_LEVELS.keys())}")
292. 
293.         if (
294.             self.config["force_saml_login"]
295.             and self.model.get_relation(DEFAULT_RELATION_NAME) is None
296.         ):
297.             errors.append("force_saml_login cannot be true without a saml relation")
298.         if self.config["max_category_nesting"] not in MAX_CATEGORY_NESTING_LEVELS:
299.             errors.append(
300.                 "max_category_nesting must be one of: "
```

</details>


---

<sub>⏱️ 26s</sub>

### ✅ `bash`

**Check config access patterns**

$ cd /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s && grep -n "self\.config\[" src/charm.py | head -30 && echo "---" && grep -n "self\.config\.get(" src/charm.py | head -30

<details>
<summary>51 lines</summary>

```
226:            typing.cast(str, self.config["external_hostname"])
227:            if self.config["external_hostname"]
290:        if self.config["throttle_level"] not in THROTTLE_LEVELS:
294:            self.config["force_saml_login"]
298:        if self.config["max_category_nesting"] not in MAX_CATEGORY_NESTING_LEVELS:
304:            self.config["saml_sync_groups"]
311:            and not self.config["force_https"]
317:            and not self.config["force_https"]
327:                if not self.config[s3_config]
361:            "true" if self.config["force_saml_login"] else "false"
365:            for x in typing.cast(str, self.config["saml_sync_groups"]).split(",")
385:            "DISCOURSE_S3_ACCESS_KEY_ID": self.config["s3_access_key_id"],
386:            "DISCOURSE_S3_BUCKET": self.config["s3_bucket"],
388:            "DISCOURSE_S3_REGION": self.config["s3_region"],
389:            "DISCOURSE_S3_SECRET_ACCESS_KEY": self.config["s3_secret_access_key"],
397:            s3_env["DISCOURSE_S3_BACKUP_BUCKET"] = self.config["s3_backup_bucket"]
399:            s3_env["DISCOURSE_S3_CDN_URL"] = self.config["s3_cdn_url"]
461:            "DISCOURSE_DEVELOPER_EMAILS": self.config["developer_emails"],
462:            "DISCOURSE_ENABLE_CORS": str(self.config["enable_cors"]).lower(),
464:            "DISCOURSE_MAX_CATEGORY_NESTING": str(self.config["max_category_nesting"]),
469:            "DISCOURSE_SMTP_ADDRESS": self.config["smtp_address"],
470:            "DISCOURSE_SMTP_AUTHENTICATION": self.config["smtp_authentication"],
471:            "DISCOURSE_SMTP_DOMAIN": self.config["smtp_domain"],
472:            "DISCOURSE_SMTP_ENABLE_START_TLS": self.config["smtp_enable_start_tls"],
473:            "DISCOURSE_SMTP_FORCE_TLS": self.config["smtp_force_tls"],
474:            "DISCOURSE_SMTP_OPENSSL_VERIFY_MODE": self.config["smtp_openssl_verify_mode"],
475:            "DISCOURSE_SMTP_PASSWORD": self.config["smtp_password"],
476:            "DISCOURSE_SMTP_PORT": str(self.config["smtp_port"]),
477:            "DISCOURSE_SMTP_USER_NAME": self.config["smtp_username"],
479:            "UNICORN_SIDEKIQ_MAX_RSS": str(self.config["sidekiq_max_memory"]),
---
240:        user_value = str(self.config.get("cors_origin", "")).strip()
249:        if self.config.get("augment_cors_origin"):
252:                scheme = "https" if self.config.get("force_https") else "http"
255:            cdn = str(self.config.get("s3_cdn_url"))
284:            self.config.get("enable_cors")
285:            and self.config.get("cors_origin") == ""
286:            and not self.config.get("augment_cors_origin")
323:        if self.config.get("s3_enabled"):
387:            "DISCOURSE_S3_ENDPOINT": self.config.get("s3_endpoint", "s3.amazonaws.com"),
391:                self.config.get("s3_install_cors_rule", True)
395:        if self.config.get("s3_backup_bucket"):
398:        if self.config.get("s3_cdn_url"):
400:        if self.config.get("s3_enabled"):
485:        if self.config.get("s3_enabled"):
549:        result = self.config.get("s3_enabled") and (
554:                    s3info.enabled != self.config.get("s3_enabled")
555:                    or s3info.region != self.config.get("s3_region")
556:                    or s3info.bucket != self.config.get("s3_bucket")
557:                    or s3info.endpoint != self.config.get("s3_endpoint")
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 33s</sub>

### ✅ `view`

**/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s/src/charm.py**

/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s/src/charm.py (lines 300-600)

<details>
<summary>301 lines</summary>

```
300.                 "max_category_nesting must be one of: "
301.                 f"{', '.join(map(str, MAX_CATEGORY_NESTING_LEVELS))}"
302.             )
303.         if (
304.             self.config["saml_sync_groups"]
305.             and self.model.get_relation(DEFAULT_RELATION_NAME) is None
306.         ):
307.             errors.append("'saml_sync_groups' cannot be specified without a saml relation")
308. 
309.         if (
310.             self.model.get_relation(DEFAULT_RELATION_NAME) is not None
311.             and not self.config["force_https"]
312.         ):
313.             errors.append("A saml relation cannot be specified without 'force_https' being true")
314. 
315.         if (
316.             self.model.get_relation(OAUTH_RELATION_NAME) is not None
317.             and not self.config["force_https"]
318.         ):
319.             errors.append(
320.                 "An oauth relation cannot be established without 'force_https' being true"
321.             )
322. 
323.         if self.config.get("s3_enabled"):
324.             errors.extend(
325.                 f"'s3_enabled' requires '{s3_config}'"
326.                 for s3_config in REQUIRED_S3_SETTINGS
327.                 if not self.config[s3_config]
328.             )
329. 
330.         if errors:
331.             self.model.unit.status = BlockedStatus(", ".join(errors))
332.         return not errors
333. 
334.     def _get_saml_config(self) -> typing.Dict[str, typing.Any]:
335.         """Get SAML configuration.
336. 
337.         Returns:
338.             Dictionary with the SAML configuration settings.
339.         """
340.         relation_data = self.saml.get_relation_data()
341.         if relation_data is None:
342.             return {}
343. 
344.         saml_config = {}
345. 
346.         sso_redirect_endpoint = next(
347.             e
348.             for e in relation_data.endpoints
349.             if e.name == "SingleSignOnService"
350.             and e.binding == "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"
351.         )
352. 
353.         saml_config["DISCOURSE_SAML_TARGET_URL"] = str(sso_redirect_endpoint.url)
354.         certificate = relation_data.certificates[0]
355.         # discourse needs SHA1 fingerprint
356.         saml_config["DISCOURSE_SAML_CERT_FINGERPRINT"] = (
357.             hashlib.sha1(base64.b64decode(certificate)).digest().hex(":").upper()  # noqa: S324  # nosec
358.         )
359. 
360.         saml_config["DISCOURSE_SAML_FULL_SCREEN_LOGIN"] = (
361.             "true" if self.config["force_saml_login"] else "false"
362.         )
363.         saml_sync_groups = [
364.             x.strip()
365.             for x in typing.cast(str, self.config["saml_sync_groups"]).split(",")
366.             if x.strip()
367.         ]
368.         if saml_sync_groups:
369.             # Per https://github.com/discourse/discourse-saml setting this to `true`
370.             # means the assigned groups will be completely synced including adding
371.             # AND removing groups based on the SAML provider.
372.             saml_config["DISCOURSE_SAML_GROUPS_FULLSYNC"] = "false"
373.             saml_config["DISCOURSE_SAML_SYNC_GROUPS"] = "true"
374.             saml_config["DISCOURSE_SAML_SYNC_GROUPS_LIST"] = "|".join(saml_sync_groups)
375. 
376.         return saml_config
377. 
378.     def _get_s3_env(self) -> typing.Dict[str, typing.Any]:
379.         """Get the list of S3-related environment variables from charm's configuration.
380. 
381.         Returns:
382.             Dictionary with all the S3 environment settings.
383.         """
384.         s3_env = {
385.             "DISCOURSE_S3_ACCESS_KEY_ID": self.config["s3_access_key_id"],
386.             "DISCOURSE_S3_BUCKET": self.config["s3_bucket"],
387.             "DISCOURSE_S3_ENDPOINT": self.config.get("s3_endpoint", "s3.amazonaws.com"),
388.             "DISCOURSE_S3_REGION": self.config["s3_region"],
389.             "DISCOURSE_S3_SECRET_ACCESS_KEY": self.config["s3_secret_access_key"],
390.             "DISCOURSE_S3_INSTALL_CORS_RULE": str(
391.                 self.config.get("s3_install_cors_rule", True)
392.             ).lower(),
393.             "DISCOURSE_USE_S3": "true",
394.         }
395.         if self.config.get("s3_backup_bucket"):
396.             s3_env["DISCOURSE_BACKUP_LOCATION"] = "s3"
397.             s3_env["DISCOURSE_S3_BACKUP_BUCKET"] = self.config["s3_backup_bucket"]
398.         if self.config.get("s3_cdn_url"):
399.             s3_env["DISCOURSE_S3_CDN_URL"] = self.config["s3_cdn_url"]
400.         if self.config.get("s3_enabled"):
401.             # We force assets to be uploaded to S3
402.             # This should be considered as a workaround and revisited later
403.             s3_env["FORCE_S3_UPLOADS"] = "true"
404. 
405.         return s3_env
406. 
407.     def _get_redis_relation_data(self) -> typing.Tuple[str, int]:
408.         """Get the hostname and port from the redis relation data.
409. 
410.         Returns:
411.             Tuple with the hostname and port of the related redis
412.         Raises:
413.             MissingRedisRelationDataError if the some of redis relation data is malformed/missing
414.         """
415.         relation = self.model.get_relation(self.redis.relation_name)
416.         if not relation:
417.             raise MissingRedisRelationDataError("No redis relation data")
418.         relation_app_data = relation.data[relation.app]
419.         relation_unit_data = self.redis.relation_data
420. 
421.         try:
422.             redis_hostname = str(
423.                 relation_app_data["leader-host"]
424.                 if relation_app_data.get("leader-host")
425.                 else relation_unit_data["hostname"]
426.             )
427.             redis_port = int(relation_unit_data["port"])
428.         except (KeyError, ValueError) as exc:
429.             raise MissingRedisRelationDataError(
430.                 "Either 'leader-host' or 'hostname' and 'port' are mandatory"
431.             ) from exc
432. 
433.         logger.debug(
434.             "Got redis connection details from relation of %s:%s", redis_hostname, redis_port
435.         )
436.         return (redis_hostname, redis_port)
437. 
438.     def _create_discourse_environment_settings(self) -> typing.Dict[str, str]:
439.         """Create a layer config based on our current configuration.
440. 
441.         Returns:
442.             Dictionary with all the environment settings.
443.         """
444.         database_relation_data = self._database.get_relation_data()
445. 
446.         # The following could fail if the data is malformed.
447.         # We/don't catch it because we don't want to silently fail in those cases
448.         redis_relation_data = self._get_redis_relation_data()
449. 
450.         pod_config = {
451.             # Since pebble exec command doesn't copy the container env (envVars set in Dockerfile),
452.             # I need to take the required envVars for the application to work properly
453.             "CONTAINER_APP_NAME": CONTAINER_NAME,
454.             "CONTAINER_APP_ROOT": "/srv/discourse",
455.             "CONTAINER_APP_USERNAME": CONTAINER_APP_USERNAME,
456.             "DISCOURSE_CORS_ORIGIN": self._get_cors_origin(),
457.             "DISCOURSE_DB_HOST": database_relation_data["POSTGRES_HOST"],
458.             "DISCOURSE_DB_NAME": database_relation_data["POSTGRES_DB"],
459.             "DISCOURSE_DB_PASSWORD": database_relation_data["POSTGRES_PASSWORD"],
460.             "DISCOURSE_DB_USERNAME": database_relation_data["POSTGRES_USER"],
461.             "DISCOURSE_DEVELOPER_EMAILS": self.config["developer_emails"],
462.             "DISCOURSE_ENABLE_CORS": str(self.config["enable_cors"]).lower(),
463.             "DISCOURSE_HOSTNAME": self._get_external_hostname(),
464.             "DISCOURSE_MAX_CATEGORY_NESTING": str(self.config["max_category_nesting"]),
465.             "DISCOURSE_REDIS_HOST": redis_relation_data[0],
466.             "DISCOURSE_REDIS_PORT": str(redis_relation_data[1]),
467.             "DISCOURSE_REFRESH_MAXMIND_DB_DURING_PRECOMPILE_DAYS": "0",
468.             "DISCOURSE_SERVE_STATIC_ASSETS": "true",
469.             "DISCOURSE_SMTP_ADDRESS": self.config["smtp_address"],
470.             "DISCOURSE_SMTP_AUTHENTICATION": self.config["smtp_authentication"],
471.             "DISCOURSE_SMTP_DOMAIN": self.config["smtp_domain"],
472.             "DISCOURSE_SMTP_ENABLE_START_TLS": self.config["smtp_enable_start_tls"],
473.             "DISCOURSE_SMTP_FORCE_TLS": self.config["smtp_force_tls"],
474.             "DISCOURSE_SMTP_OPENSSL_VERIFY_MODE": self.config["smtp_openssl_verify_mode"],
475.             "DISCOURSE_SMTP_PASSWORD": self.config["smtp_password"],
476.             "DISCOURSE_SMTP_PORT": str(self.config["smtp_port"]),
477.             "DISCOURSE_SMTP_USER_NAME": self.config["smtp_username"],
478.             "RAILS_ENV": "production",
479.             "UNICORN_SIDEKIQ_MAX_RSS": str(self.config["sidekiq_max_memory"]),
480.         }
481.         pod_config.update(self._get_saml_config())
482.         # Add OIDC env vars if oauth relation is established
483.         pod_config.update(self._oauth.get_oidc_env())
484. 
485.         if self.config.get("s3_enabled"):
486.             pod_config.update(self._get_s3_env())
487. 
488.         # We only get valid throttle levels here, otherwise it would be caught
489.         # by `_is_config_valid()`.
490.         # self.config return an Any type
491.         pod_config.update(THROTTLE_LEVELS.get(self.config["throttle_level"]))  # type: ignore
492. 
493.         # Update environment with proxy settings
494.         pod_config["HTTP_PROXY"] = pod_config["http_proxy"] = (
495.             os.environ.get("JUJU_CHARM_HTTP_PROXY") or ""
496.         )
497.         pod_config["HTTPS_PROXY"] = pod_config["https_proxy"] = (
498.             os.environ.get("JUJU_CHARM_HTTPS_PROXY") or ""
499.         )
500.         pod_config["NO_PROXY"] = pod_config["no_proxy"] = (
501.             os.environ.get("JUJU_CHARM_NO_PROXY") or ""
502.         )
503. 
504.         return pod_config
505. 
506.     def _create_layer_config(self) -> ops.pebble.LayerDict:
507.         """Create a layer config based on our current configuration.
508. 
509.         Returns:
510.             Dictionary with the pebble configuration.
511.         """
512.         logger.info("Generating Layer config")
513.         layer_config = {
514.             "summary": "Discourse layer",
515.             "description": "Discourse layer",
516.             "services": {
517.                 SERVICE_NAME: {
518.                     "override": "replace",
519.                     "summary": "Discourse web application",
520.                     "command": f"{SCRIPT_PATH}/app_launch.sh",
521.                     "user": CONTAINER_APP_USERNAME,
522.                     "startup": "enabled",
523.                     "environment": self._create_discourse_environment_settings(),
524.                     "kill-delay": "20s",
525.                 }
526.             },
527.             "checks": {
528.                 "discourse-ready": {
529.                     "override": "replace",
530.                     "level": "ready",
531.                     "http": {"url": f"http://localhost:{SERVICE_PORT}/srv/status"},
532.                 },
533.             },
534.         }
535.         return typing.cast(ops.pebble.LayerDict, layer_config)
536. 
537.     def _should_run_s3_migration(
538.         self, current_plan: Plan, s3info: typing.Optional[S3Info]
539.     ) -> bool:
540.         """Determine if the S3 migration is to be run.
541. 
542.         Args:
543.             current_plan: Dictionary containing the current plan.
544.             s3info: S3Info object containing the S3 configuration options.
545. 
546.         Returns:
547.             If no services are planned yet (first run) or S3 settings have changed.
548.         """
549.         result = self.config.get("s3_enabled") and (
550.             not current_plan.services
551.             or (
552.                 s3info
553.                 and (
554.                     s3info.enabled != self.config.get("s3_enabled")
555.                     or s3info.region != self.config.get("s3_region")
556.                     or s3info.bucket != self.config.get("s3_bucket")
557.                     or s3info.endpoint != self.config.get("s3_endpoint")
558.                 )
559.             )
560.         )
561.         return bool(result)
562. 
563.     def _are_relations_ready(self) -> bool:
564.         """Check if the needed database relations are established.
565. 
566.         Returns:
567.             If the needed relations have been established.
568.         """
569.         if not self._database.is_relation_ready():
570.             self.model.unit.status = WaitingStatus("Waiting for database relation")
571.             self._stop_service()
572.             return False
573.         if not self.redis.relation_data:
574.             self.model.unit.status = WaitingStatus("Waiting for redis relation")
575.             self._stop_service()
576.             return False
577.         try:
578.             if (
579.                 self._get_redis_relation_data()[0] in ("", "None")
580.                 or self._get_redis_relation_data()[1] == 0
581.             ):
582.                 self.model.unit.status = WaitingStatus("Waiting for redis relation to initialize")
583.                 return False
584.         except MissingRedisRelationDataError:
585.             self.model.unit.status = WaitingStatus("Waiting for redis relation to initialize")
586.             return False
587.         return True
588. 
589.     def _execute_migrations(self) -> None:
590.         container = self.unit.get_container(CONTAINER_NAME)
591.         if not self._are_relations_ready() or not container.can_connect():
592.             logger.info("Not ready to execute migrations")
593.             return
594.         env_settings = self._create_discourse_environment_settings()
595.         self.model.unit.status = MaintenanceStatus("Executing migrations")
596.         # The rails migration task is idempotent and concurrent-safe, from
597.         # https://stackoverflow.com/questions/17815769/are-rake-dbcreate-and-rake-dbmigrate-idempotent
598.         # and https://github.com/rails/rails/pull/22122
599.         # Thus it's safe to run this task on all units to
600.         # avoid complications with how juju schedules charm upgrades
```

</details>


---

<sub>⏱️ 34s</sub>

### ✅ `bash`

**Check action params access**

$ cd /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s && grep -n "event\.params" src/charm.py | head -20

<details>
<summary>7 lines</summary>

```
789:        email = event.params["email"]
827:        email = event.params["email"]
835:        admin_flag = "Y" if event.params.get("admin") else "N"
857:            not event.params.get("admin")
858:            and event.params.get("active")
901:        username = event.params["username"]
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 34s</sub>

### ✅ `bash`

**Check rockcraft.yaml services**

$ cd /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s && cat discourse_rock/rockcraft.yaml | grep -A5 "services:"

```

<exited with exit code 1>
```


---

<sub>⏱️ 41s</sub>

### ✅ `view`

**/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s/src/charm.py**

/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s/src/charm.py (lines 770-930)

<details>
<summary>161 lines</summary>

```
770.         try:
771.             activate_process.wait_output()
772.             return True
773.         except ExecError as ex:
774.             if ex.exit_code == 2:
775.                 return False
776.             raise
777. 
778.     def _on_promote_user_action(self, event: ActionEvent) -> None:
779.         """Promote a user to a specific trust level.
780. 
781.         Args:
782.             event: Event triggering the promote_user action.
783.         """
784.         container = self.unit.get_container(CONTAINER_NAME)
785.         if not container.can_connect():
786.             event.fail("Unable to connect to container, container is not ready")
787.             return
788. 
789.         email = event.params["email"]
790. 
791.         if not self._user_exists(email):
792.             event.fail(f"User with email {email} does not exist")
793.             return
794. 
795.         process = container.exec(
796.             [
797.                 os.path.join(DISCOURSE_PATH, "bin/bundle"),
798.                 "exec",
799.                 "rake",
800.                 "admin:create",
801.             ],
802.             stdin=f"{email}\nn\nY\n",
803.             working_dir=DISCOURSE_PATH,
804.             user=CONTAINER_APP_USERNAME,
805.             environment=self._create_discourse_environment_settings(),
806.             timeout=60,
807.         )
808.         try:
809.             process.wait_output()
810.             event.set_results({"user": email})
811.         except ExecError as ex:
812.             event.fail(
813.                 f"Failed to make user with email {email} an admin: {ex.stdout}"  # type: ignore
814.             )
815. 
816.     def _on_create_user_action(self, event: ActionEvent) -> None:
817.         """Create a new user in Discourse.
818. 
819.         Args:
820.             event: Event triggering the create_user action.
821.         """
822.         container = self.unit.get_container(CONTAINER_NAME)
823.         if not container.can_connect():
824.             event.fail("Unable to connect to container, container is not ready")
825.             return
826. 
827.         email = event.params["email"]
828.         password = self._generate_password(16)
829. 
830.         if self._user_exists(email):
831.             event.fail(f"User with email {email} already exists")
832.             return
833. 
834.         # Admin flag is optional, if it is true, the user will be created as an admin
835.         admin_flag = "Y" if event.params.get("admin") else "N"
836. 
837.         process = container.exec(
838.             [
839.                 os.path.join(DISCOURSE_PATH, "bin/bundle"),
840.                 "exec",
841.                 "rake",
842.                 "admin:create",
843.             ],
844.             stdin=f"{email}\n{password}\n{password}\n{admin_flag}\n",
845.             working_dir=DISCOURSE_PATH,
846.             user=CONTAINER_APP_USERNAME,
847.             environment=self._create_discourse_environment_settings(),
848.             timeout=60,
849.         )
850.         try:
851.             process.wait_output()
852.         except ExecError as ex:
853.             event.fail(f"Failed to make user with email {email}: {ex.stdout}")  # type: ignore
854.             return
855. 
856.         if (
857.             not event.params.get("admin")
858.             and event.params.get("active")
859.             and not self._activate_user(email)
860.         ):
861.             event.fail(f"Could not find user {email} to activate")
862.             return
863. 
864.         event.set_results({"user": email, "password": password})
865. 
866.     def _generate_password(self, length: int) -> str:
867.         """Generate a random password.
868. 
869.         Args:
870.             length: Length of the password to generate.
871. 
872.         Returns:
873.             Random password.
874.         """
875.         choices = string.ascii_letters + string.digits
876.         password = "".join([secrets.choice(choices) for _ in range(length)])
877.         return password
878. 
879.     def _config_force_https(self) -> None:
880.         """Config Discourse to force_https option based on charm configuration."""
881.         container = self.unit.get_container(CONTAINER_NAME)
882.         force_bool = str(self.config["force_https"]).lower()
883.         process = container.exec(
884.             [
885.                 os.path.join(DISCOURSE_PATH, "bin/rails"),
886.                 "runner",
887.                 f"SiteSetting.force_https={force_bool}",
888.             ],
889.             working_dir=DISCOURSE_PATH,
890.             user=CONTAINER_APP_USERNAME,
891.             environment=self._create_discourse_environment_settings(),
892.         )
893.         process.wait_output()
894. 
895.     def _on_anonymize_user_action(self, event: ActionEvent) -> None:
896.         """Anonymize data from a user.
897. 
898.         Args:
899.             event: Event triggering the anonymize_user action.
900.         """
901.         username = event.params["username"]
902.         container = self.unit.get_container(CONTAINER_NAME)
903.         if not container.can_connect():
904.             event.fail("Unable to connect to container, container is not ready")
905.             return
906. 
907.         process = container.exec(
908.             [
909.                 os.path.join(DISCOURSE_PATH, "bin/bundle"),
910.                 "exec",
911.                 "rake",
912.                 f"users:anonymize[{username}]",
913.             ],
914.             working_dir=DISCOURSE_PATH,
915.             user=CONTAINER_APP_USERNAME,
916.             environment=self._create_discourse_environment_settings(),
917.         )
918.         try:
919.             process.wait_output()
920.             event.set_results({"user": f"{username}"})
921.         except ExecError as ex:
922.             event.fail(
923.                 # Parameter validation errors are printed to stdout
924.                 # Ignore mypy warning when formatting stdout
925.                 f"Failed to anonymize user with username {username}:{ex.stdout}"  # type: ignore
926.             )
927. 
928.     def _start_service(self):
929.         """Start discourse."""
930.         logger.info("Starting discourse")
```

</details>


---

<sub>⏱️ 41s</sub>

### ✅ `bash`

**Check actions.yaml**

$ cd /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s && cat actions.yaml

<details>
<summary>31 lines</summary>

```
# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.
anonymize-user:
  description: Anonymize a user.
  params:
    username:
      type: string
      description: The unique identifier of the user to anonymize.
  required: [username]
create-user:
  description: Create a new user.
  params:
    email:
      type: string
      description: User email.
    admin:
      type: boolean
      description: Whether the user should be an admin.
    active:
      type: boolean
      description: Whether the user should be email-verified and active.
      default: true
  required: [email]
promote-user:
  description: Promote a user to admin.
  params:
    email:
      type: string
      description: User email.
  required: [email]
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 41s</sub>

### ✅ `bash`

**Check if unit tests use layer_from_rockcraft or manual layers**

$ cd /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s && grep -n "layer_from_rockcraft\|pebble.Layer\|ops.pebble.Layer" tests/unit/test_charm.py | head -20

```

<exited with exit code 0>
```


---

<sub>⏱️ 53s</sub>

### ✅ `bash`

**Run unit tests to establish baseline**

$ cd /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s && tox -e unit 2>&1 | tail -30

<details>
<summary>29 lines</summary>

```
tests/unit_harness/test_charm.py::test_on_config_changed_when_valid
tests/unit_harness/test_charm.py::test_on_config_changed_when_valid
tests/unit_harness/test_charm.py::test_on_config_changed_when_valid
tests/unit_harness/test_charm.py::test_on_config_changed_when_valid
  /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s/lib/charms/saml_integrator/v0/saml.py:142: PydanticDeprecatedSince20: `parse_obj_as` is deprecated. Use `pydantic.TypeAdapter.validate_python` instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.10/migration/
    parse_obj_as(AnyHttpUrl, relation_data[f"{prefix}url"])

tests/unit_harness/test_charm.py::test_on_config_changed_when_valid
tests/unit_harness/test_charm.py::test_on_config_changed_when_valid
tests/unit_harness/test_charm.py::test_on_config_changed_when_valid
tests/unit_harness/test_charm.py::test_on_config_changed_when_valid
tests/unit_harness/test_charm.py::test_on_config_changed_when_valid
tests/unit_harness/test_charm.py::test_on_config_changed_when_valid
tests/unit_harness/test_charm.py::test_on_config_changed_when_valid
  /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s/lib/charms/saml_integrator/v0/saml.py:211: PydanticDeprecatedSince20: `parse_obj_as` is deprecated. Use `pydantic.TypeAdapter.validate_python` instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.10/migration/
    parse_obj_as(AnyHttpUrl, relation_data.get("metadata_url"))

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
======================= 55 passed, 106 warnings in 2.26s =======================
unit: commands[1]> coverage report
Name                    Stmts   Miss Branch BrPart  Cover   Missing
-------------------------------------------------------------------
src/charm.py              377     42     96     15    88%   170, 178-179, 191, 251->255, 299, 368->376, 400->405, 417, 609-611, 616-617, 629-631, 636-637, 649-651, 674-676, 714->exit, 773-776, 786-787, 811-812, 824-825, 852-854, 861-862, 904-905, 921-922, 932->exit, 946
src/constants.py           21      0      0      0   100%
src/database.py            29      1      8      1    95%   57
src/oauth_observer.py      54      8      8      2    84%   65, 80-81, 111, 114-123
-------------------------------------------------------------------
TOTAL                     481     51    112     18    88%
  unit: OK (2.97=setup[0.09]+cmd[2.80,0.08] seconds)
  congratulations :) (2.99 seconds)
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 1m 7s</sub>

### ✅ `bash`

**Read constants.py**

$ cd /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s && cat src/constants.py

<details>
<summary>48 lines</summary>

```
# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

"""Constants for Discourse charm."""

import typing
from collections import defaultdict

DATABASE_NAME = "discourse"
DISCOURSE_PATH = "/srv/discourse/app"
THROTTLE_LEVELS: typing.Dict = defaultdict(dict)
THROTTLE_LEVELS["none"] = {
    "DISCOURSE_MAX_REQS_PER_IP_MODE": "none",
    "DISCOURSE_MAX_REQS_RATE_LIMIT_ON_PRIVATE": "false",
}
THROTTLE_LEVELS["permissive"] = {
    "DISCOURSE_MAX_REQS_PER_IP_MODE": "warn+block",
    "DISCOURSE_MAX_REQS_PER_IP_PER_MINUTE": "1000",
    "DISCOURSE_MAX_REQS_PER_IP_PER_10_SECONDS": "100",
    "DISCOURSE_MAX_USER_API_REQS_PER_MINUTE": "3000",
    "DISCOURSE_MAX_ASSET_REQS_PER_IP_PER_10_SECONDS": "400",
    "DISCOURSE_MAX_REQS_RATE_LIMIT_ON_PRIVATE": "false",
    "DISCOURSE_MAX_USER_API_REQS_PER_DAY": "30000",
    "DISCOURSE_MAX_ADMIN_API_REQS_PER_KEY_PER_MINUTE": "3000",
}
THROTTLE_LEVELS["strict"] = {
    "DISCOURSE_MAX_REQS_PER_IP_MODE": "block",
    "DISCOURSE_MAX_REQS_PER_IP_PER_MINUTE": "200",
    "DISCOURSE_MAX_REQS_PER_IP_PER_10_SECONDS": "50",
    "DISCOURSE_MAX_USER_API_REQS_PER_MINUTE": "100",
    "DISCOURSE_MAX_ASSET_REQS_PER_IP_PER_10_SECONDS": "200",
    "DISCOURSE_MAX_REQS_RATE_LIMIT_ON_PRIVATE": "false",
}
LOG_PATHS = [
    f"{DISCOURSE_PATH}/log/production.log",
    f"{DISCOURSE_PATH}/log/unicorn.stderr.log",
    f"{DISCOURSE_PATH}/log/unicorn.stdout.log",
]
MAX_CATEGORY_NESTING_LEVELS = [2, 3]
PROMETHEUS_PORT = 3000
REQUIRED_S3_SETTINGS = ["s3_access_key_id", "s3_bucket", "s3_region", "s3_secret_access_key"]
SCRIPT_PATH = "/srv/scripts"
SERVICE_NAME = "discourse"
CONTAINER_NAME = "discourse"
CONTAINER_APP_USERNAME = "_daemon_"
SERVICE_PORT = 3000
SETUP_COMPLETED_FLAG_FILE = "/run/discourse-k8s-operator/setup_completed"
DATABASE_RELATION_NAME = "database"
OAUTH_RELATION_NAME = "oauth"
OAUTH_SCOPE = "openid email"
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 1m 7s</sub>

### ✅ `view`

**/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s/src/charm.py**

/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s/src/charm.py (lines 600-770)

<details>
<summary>171 lines</summary>

```
600.         # avoid complications with how juju schedules charm upgrades
601.         try:
602.             migration_process: ExecProcess = container.exec(
603.                 [f"{DISCOURSE_PATH}/bin/bundle", "exec", "rake", "--trace", "db:migrate"],
604.                 environment=env_settings,
605.                 working_dir=DISCOURSE_PATH,
606.                 user=CONTAINER_APP_USERNAME,
607.             )
608.             migration_process.wait_output()
609.         except ExecError as cmd_err:
610.             logger.exception("Executing migrations failed with code %d.", cmd_err.exit_code)
611.             raise
612. 
613.     def _set_workload_version(self) -> None:
614.         container = self.unit.get_container(CONTAINER_NAME)
615.         if not self._are_relations_ready() or not container.can_connect():
616.             logger.info("Not ready to set workload version")
617.             return
618.         env_settings = self._create_discourse_environment_settings()
619.         try:
620.             logger.info("Setting workload version")
621.             get_version_process = container.exec(
622.                 [f"{DISCOURSE_PATH}/bin/rails", "runner", "puts Discourse::VERSION::STRING"],
623.                 environment=env_settings,
624.                 working_dir=DISCOURSE_PATH,
625.                 user=CONTAINER_APP_USERNAME,
626.             )
627.             version, _ = get_version_process.wait_output()
628.             self.unit.set_workload_version(version)
629.         except ExecError as cmd_err:
630.             logger.exception("Setting workload version failed with code %d.", cmd_err.exit_code)
631.             raise
632. 
633.     def _run_s3_migration(self) -> None:
634.         container = self.unit.get_container(CONTAINER_NAME)
635.         if not self._are_relations_ready() or not container.can_connect():
636.             logger.info("Not ready to run S3 migration")
637.             return
638.         env_settings = self._create_discourse_environment_settings()
639.         self.model.unit.status = MaintenanceStatus("Running S3 migration")
640.         logger.info("Running S3 migration")
641.         try:
642.             process = container.exec(
643.                 [f"{DISCOURSE_PATH}/bin/bundle", "exec", "rake", "s3:upload_assets"],
644.                 environment=env_settings,
645.                 working_dir=DISCOURSE_PATH,
646.                 user=CONTAINER_APP_USERNAME,
647.             )
648.             process.wait_output()
649.         except ExecError as cmd_err:
650.             logger.exception("S3 migration failed with code %d.", cmd_err.exit_code)
651.             raise
652. 
653.     def _set_up_discourse(self) -> None:
654.         """Run Discourse migrations and recompile assets.
655. 
656.         Args:
657.             event: Event triggering the handler.
658.         """
659.         container = self.unit.get_container(CONTAINER_NAME)
660.         if not self._are_relations_ready() or not container.can_connect():
661.             logger.info("Pebble or relations not ready, not attempting to setup discourse")
662.             return
663.         logger.info(
664.             "Relations are ready and can connect to container, attempting to set up discourse."
665.         )
666.         try:
667.             logger.info("Discourse setup: about to execute migrations")
668.             self._execute_migrations()
669.             logger.info("Discourse setup: about to mark the discourse setup process as complete")
670.             self._set_setup_completed()
671.             logger.info("Discourse setup: about to set workload version")
672.             self._set_workload_version()
673.             logger.info("Discourse setup: completed")
674.         except ExecError as cmd_err:
675.             logger.exception("Setting up discourse failed with code %d.", cmd_err.exit_code)
676.             raise
677. 
678.     def _configure_pod(self) -> None:
679.         """Configure pod using pebble and layer generated from config.
680. 
681.         Args:
682.             event: Event triggering the handler.
683.         """
684.         container = self.unit.get_container(CONTAINER_NAME)
685.         if not self._are_relations_ready() or not container.can_connect():
686.             logger.info("Not ready to do config changed action")
687.             return
688.         if not self._is_config_valid():
689.             return
690. 
691.         # Get previous plan and extract env vars values to check is some S3 params has changed
692.         current_plan = container.get_plan()
693. 
694.         # Covers when there are no plan
695.         previous_s3_info = None
696.         if (
697.             current_plan.services
698.             and SERVICE_NAME in current_plan.services
699.             and current_plan.services[SERVICE_NAME]
700.         ):
701.             current_env = current_plan.services[SERVICE_NAME].environment
702.             previous_s3_info = S3Info(
703.                 current_env.get("DISCOURSE_USE_S3", ""),
704.                 current_env.get("DISCOURSE_S3_REGION", ""),
705.                 current_env.get("DISCOURSE_S3_BUCKET", ""),
706.                 current_env.get("DISCOURSE_S3_ENDPOINT", ""),
707.             )
708.         if self.model.unit.is_leader() and self._should_run_s3_migration(
709.             current_plan, previous_s3_info
710.         ):
711.             self._run_s3_migration()
712. 
713.         self._activate_charm()
714.         if container.can_connect():
715.             self._config_force_https()
716. 
717.     def _activate_charm(self) -> None:
718.         """Start discourse and mark the charm as active if the setup is completed."""
719.         # mypy has some trouble with dynamic attributes
720.         if not self._is_setup_completed():
721.             logger.info("Not starting the discourse server until discourse setup completed")
722.             return
723.         container = self.unit.get_container(CONTAINER_NAME)
724.         if self._is_config_valid() and container.can_connect():
725.             self._start_service()
726.             self.model.unit.status = ActiveStatus()
727. 
728.     def _user_exists(self, email: str) -> bool:
729.         """Check if a user with the given email exists.
730. 
731.         Args:
732.             email: Email of the user to check.
733. 
734.         Returns:
735.             True if the user exists, False otherwise.
736.         """
737.         container = self.unit.get_container(CONTAINER_NAME)
738.         user_exists = container.exec(
739.             [os.path.join(DISCOURSE_PATH, "bin/bundle"), "exec", "rake", f"users:exists[{email}]"],
740.             working_dir=DISCOURSE_PATH,
741.             user=CONTAINER_APP_USERNAME,
742.             environment=self._create_discourse_environment_settings(),
743.         )
744.         try:
745.             user_exists.wait_output()
746.             return True
747.         except ExecError as ex:
748.             if ex.exit_code == 2:
749.                 return False
750.             raise
751. 
752.     def _activate_user(self, email: str) -> bool:
753.         """Activate a user with the given email.
754. 
755.         Args:
756.             email: Email of the user to activate.
757.         """
758.         container = self.unit.get_container(CONTAINER_NAME)
759.         activate_process = container.exec(
760.             [
761.                 os.path.join(DISCOURSE_PATH, "bin/bundle"),
762.                 "exec",
763.                 "rake",
764.                 f"users:activate[{email}]",
765.             ],
766.             working_dir=DISCOURSE_PATH,
767.             user=CONTAINER_APP_USERNAME,
768.             environment=self._create_discourse_environment_settings(),
769.         )
770.         try:
```

</details>


---

<sub>⏱️ 2m 2s</sub>

### ✅ `bash`

**Check for testing upgrade opportunities**

$ cd /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s && grep -n "pebble\|Layer\|UncaughtCharm\|charm_spec" tests/unit/test_charm.py | head -20 && grep -n "pebble\|Layer\|UncaughtCharm\|charm_spec" tests/unit_harness/test_charm.py | head -20

<details>
<summary>23 lines</summary>

```
145:    state_out = ctx.run(ctx.on.pebble_ready(container), state_in)
180:    act: trigger pebble ready or relation changed.
47:    act: when pebble ready event is triggered
53:    harness.container_pebble_ready("discourse")
60:    act: when pebble ready event is triggered
188:    harness.container_pebble_ready(SERVICE_NAME)
195:    updated_plan = harness.get_container_pebble_plan(SERVICE_NAME).to_dict()
249:    harness.container_pebble_ready(SERVICE_NAME)
252:    updated_plan = harness.get_container_pebble_plan(SERVICE_NAME).to_dict()
404:    except ops.pebble.ExecError as e:
525:    act: trigger the pebble ready event on a leader unit
526:    assert: the pebble plan gets updated
531:    harness.container_pebble_ready(CONTAINER_NAME)
533:        harness.get_container_pebble_plan(CONTAINER_NAME).services["discourse"].environment
537:        harness.get_container_pebble_plan(CONTAINER_NAME).services["discourse"].environment
544:def test_handle_pebble_ready_event():
547:    act: trigger the pebble ready event on a leader unit
548:    assert: the pebble plan gets updated
553:    plan_before_event = harness.get_container_pebble_plan(CONTAINER_NAME)
554:    harness.container_pebble_ready(CONTAINER_NAME)
555:    plan_after_event = harness.get_container_pebble_plan(CONTAINER_NAME)
564:    act: trigger the pebble ready event on a leader unit
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 2m 2s</sub>

### ✅ `bash`

**Check available ops versions**

$ pip index versions ops 2>/dev/null | head -5 || pip install --dry-run "ops>=3.0" 2>&1 | head -10

```
ops (3.6.0)
Available versions: 3.6.0, 3.5.2, 3.5.1, 3.5.0, 3.4.0, 3.3.1, 3.3.0, 3.2.0, 3.1.0, 3.0.0, 2.23.2, 2.23.1, 2.23.0, 2.22.0, 2.21.1, 2.21.0, 2.20.0, 2.19.4, 2.19.0, 2.18.1, 2.18.0, 2.17.1, 2.17.0, 2.16.1, 2.16.0, 2.15.0, 2.14.1, 2.14.0, 2.13.0, 2.12.0, 2.11.0, 2.10.0, 2.9.0, 2.8.0, 2.7.0, 2.6.0, 2.5.1, 2.5.0, 2.4.1, 2.4.0, 2.3.0, 2.2.0, 2.1.1, 2.1.0, 2.0.0, 1.5.5, 1.5.4, 1.5.3, 1.5.2, 1.5.1, 1.5.0, 1.4.0, 1.3.0, 1.2.0, 1.1.0, 1.0.1, 1.0.0, 0.10.0, 0.9.0, 0.8.0, 0.7.0, 0.6.1, 0.6.0, 0.4.7, 0.4.6, 0.4.5, 0.4.4, 0.4.3, 0.4.2, 0.2.1, 0.2.0, 0.1.0
  INSTALLED: 2.23.2
  LATEST:    3.6.0
<exited with exit code 0>
```


---

<sub>⏱️ 3m 3s</sub>

### ✅ `bash`

**Check for remaining upgrade opportunities**

$ cd /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s && grep -rn "UncaughtCharmError\|SCENARIO_BARE_CHARM" tests/ && grep -n "os\.environ\|os\.getenv\|JUJU_" src/charm.py

```

<exited with exit code 1>
```


---

<sub>⏱️ 3m 3s</sub>

### ✅ `bash`

**Read tox config**

$ cd /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s && cat tox.toml

<details>
<summary>118 lines</summary>

```
# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

no_package = true
skip_missing_interpreters = true
env_list = [ "lint", "unit", "static", "coverage-report" ]

requires = [ "tox>=4.22", "tox-uv>=1.29.0" ]

[env_run_base]
pass_env = [
  "PYTHONPATH",
  "CHARM_BUILD_DIR",
  "MODEL_SETTINGS",
  "CHARM_FILE",
  "ROCK_IMAGE",
  "OCI_RESOURCE_NAME",
  "JUJU_DEPLOY_BASE",
  "TOX_CMD_PREFIX",
]
runner = "uv-venv-lock-runner"

[env_run_base.set_env]
PYTHONPATH = "{tox_root}{:}{tox_root}{/}lib{:}{tox_root}{/}{[vars]src_path}"
PYTHONBREAKPOINT = "ipdb.set_trace"
PY_COLORS = "1"

[env.fmt]
description = "Apply coding style standards to code"
commands = [
  [ "ruff", "check", "--fix", "--select", "I", { replace = "ref", of = [ "vars", "all_path" ], extend = true } ],
  [ "ruff", "format", { replace = "ref", of = [ "vars", "all_path" ], extend = true } ],
]
dependency_groups = [ "fmt" ]

[env.lint]
description = "Check code against coding style standards"
commands = [
  [ "codespell", "{tox_root}" ],
  [ "ruff", "format", "--check", "--diff", { replace = "ref", of = [ "vars", "all_path" ], extend = true } ],
  [ "ruff", "check", { replace = "ref", of = [ "vars", "all_path" ], extend = true } ],
  [ "mypy", { replace = "ref", of = [ "vars", "all_path" ], extend = true } ],
]
dependency_groups = [ "lint" ]

[env.unit]
description = "Run unit tests"
commands = [
  [
    "coverage",
    "run",
    "--source={[vars]src_path}",
    "-m",
    "pytest",
    "--ignore={[vars]tst_path}{/}integration",
    "-v",
    "--tb",
    "native",
    "-s",
    { replace = "posargs", extend = true },
  ],
  [ "coverage", "report" ],
]
dependency_groups = [ "unit" ]

[env.coverage-report]
description = "Create test coverage report"
commands = [ [ "coverage", "report" ] ]
dependency_groups = [ "coverage-report" ]

[env.static]
description = "Run static analysis tests"
commands = [ [ "bandit", "-c", "{tox_root}{/}pyproject.toml", "-r", "{[vars]src_path}", "{[vars]tst_path}" ] ]
dependency_groups = [ "static" ]

[env.integration]
description = "Run integration tests"
commands = [
  [
    "pytest",
    "-v",
    "--tb",
    "native",
    "--ignore={[vars]tst_path}{/}unit",
    "--ignore={[vars]tst_path}{/}unit_harness",
    "--log-cli-level=INFO",
    "-s",
    { replace = "posargs", extend = true },
  ],
]
dependency_groups = [ "integration" ]

[env.lint-docs]
description = "Check documentation links"
package = "skip"
runner = "uv-venv-runner"

allowlist_externals = [ "curl", "tar", "chmod", "echo", "sh", "{envtmpdir}{/}lychee" ]

commands_pre = [
  [ "echo", "Download URL: {[vars]lychee_download_url}" ],
  [ "curl", "-L", "{[vars]lychee_download_url}", "-o", "{envtmpdir}{/}lychee.tar.gz" ],
  [ "sh", "-c", "echo '{[vars]lychee_sha256}  {envtmpdir}{/}lychee.tar.gz' | sha256sum -c -" ],
  [ "tar", "-xzf", "{envtmpdir}{/}lychee.tar.gz", "-C", "{envtmpdir}" ],
  [ "chmod", "+x", "{envtmpdir}{/}lychee" ],
]
commands = [ [ "{envtmpdir}{/}lychee", "--max-concurrency", "2", "README.md", "{[vars]docs_path}" ] ]

[env.lint-fix]
description = "Apply coding style standards to code"
commands = [
  [
    "ruff",
    "check",
    "--fix",
    "--fix-only",
    { replace = "ref", of = [
      "vars",
      "all_path",
    ], extend = true },
  ],
]
dependency_groups = [ "lint" ]

[vars]
src_path = "src"
tst_path = "tests"
docs_path = "docs"
all_path = [ "src", "tests" ]
lychee_version = "0.19.1"
lychee_sha256 = "537bcfbb0f3bf997f4cbdab259cc5500f2804b69614140ac3edebb4de94b3574"
lychee_download_url = "https://github.com/lycheeverse/lychee/releases/download/lychee-v{[vars]lychee_version}/lychee-x86_64-unknown-linux-gnu.tar.gz"
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 3m 57s</sub>

### 💬 Copilot

Now I have a clear picture. I'll apply:
- **A: Config Classes** - Pydantic model + `load_config()` (Pydantic already a dep)
- **B: Action Classes** - dataclasses + `load_params()`
- **Ops version bump** to `ops\>=2.23.0`

---

<sub>⏱️ 3m 57s</sub>

### ✅ `sql`

**Create todos**

<details>
<summary>Arguments</summary>

```json
{
  "description": "Create todos",
  "query": "\nINSERT INTO todos (id, title, description, status) VALUES\n  ('config-class', 'Create DiscourseConfig Pydantic model', 'Create src/config.py with all config fields mirroring config.yaml', 'pending'),\n  ('charm-config', 'Update charm.py to use load_config', 'Import DiscourseConfig, add self._typed_config = self.load_config(DiscourseConfig) in __init__, replace all self.config[...] and self.config.get(...) with self._typed_config.<field>', 'pending'),\n  ('action-params', 'Add action param dataclasses + load_params', 'Add PromoteUserParams, CreateUserParams, AnonymizeUserParams dataclasses and use event.load_params() in action handlers', 'pending'),\n  ('version-bump', 'Bump ops version in pyproject.toml', 'Change ops==2.23.2 to ops>=2.23.0', 'pending'),\n  ('verify', 'Run tests and lint', 'Run tox -e lint and tox -e unit to verify changes', 'pending');\n"
}
```

</details>

```
5 row(s) inserted. Last inserted row ID: 5.
```


---

<sub>⏱️ 4m 8s</sub>

### ✅ `create`

**/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s/src/config.py**

/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s/src/config.py

```
Created file /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s/src/config.py with 1159 characters
```


---

<sub>⏱️ 4m 13s</sub>

### 💬 Copilot

Now let me update `charm.py`. I'll make all the changes in sequence:

---

<sub>⏱️ 4m 13s</sub>

### ✅ `view`

**/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s/src/charm.py**

/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s/src/charm.py (lines 1-57)

<details>
<summary>57 lines</summary>

```
1. #!/usr/bin/env python3
2. # Copyright 2026 Canonical Ltd.
3. # See LICENSE file for licensing details.
4. 
5. """Charm for Discourse on kubernetes."""
6. 
7. import base64
8. import hashlib
9. import logging
10. import os.path
11. import secrets
12. import string
13. import typing
14. from collections import namedtuple
15. 
16. import ops
17. from charms.data_platform_libs.v0.data_interfaces import (
18.     DatabaseCreatedEvent,
19.     DatabaseEndpointsChangedEvent,
20. )
21. from charms.grafana_k8s.v0.grafana_dashboard import GrafanaDashboardProvider
22. from charms.loki_k8s.v0.loki_push_api import LogProxyConsumer
23. from charms.nginx_ingress_integrator.v0.nginx_route import require_nginx_route
24. from charms.prometheus_k8s.v0.prometheus_scrape import MetricsEndpointProvider
25. from charms.redis_k8s.v0.redis import RedisRelationCharmEvents, RedisRequires
26. from charms.rolling_ops.v0.rollingops import RollingOpsManager
27. from charms.saml_integrator.v0.saml import (
28.     DEFAULT_RELATION_NAME,
29.     SamlDataAvailableEvent,
30.     SamlRequires,
31. )
32. from ops.charm import ActionEvent, CharmBase, HookEvent, RelationBrokenEvent
33. from ops.main import main
34. from ops.model import ActiveStatus, BlockedStatus, MaintenanceStatus, WaitingStatus
35. from ops.pebble import ExecError, ExecProcess, Plan
36. 
37. from constants import (
38.     CONTAINER_APP_USERNAME,
39.     CONTAINER_NAME,
40.     DATABASE_RELATION_NAME,
41.     DISCOURSE_PATH,
42.     LOG_PATHS,
43.     MAX_CATEGORY_NESTING_LEVELS,
44.     OAUTH_RELATION_NAME,
45.     PROMETHEUS_PORT,
46.     REQUIRED_S3_SETTINGS,
47.     SCRIPT_PATH,
48.     SERVICE_NAME,
49.     SERVICE_PORT,
50.     SETUP_COMPLETED_FLAG_FILE,
51.     THROTTLE_LEVELS,
52. )
53. from database import DatabaseHandler
54. from oauth_observer import OAuthObserver
55. 
56. logger = logging.getLogger(__name__)
57.
```

</details>


---

<sub>⏱️ 4m 17s</sub>

### ✅ `edit`

**/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s/src/charm.py**

/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s/src/charm.py

```
File /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s/src/charm.py updated with changes.
```


---

<sub>⏱️ 4m 23s</sub>

### ✅ `edit`

**/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s/src/charm.py**

/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s/src/charm.py

```
File /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s/src/charm.py updated with changes.
```


---

<sub>⏱️ 4m 27s</sub>

### 💬 Copilot

Now add action param dataclasses and update the `__init__` to load config. First, let me see what's between line 57 (logger) and the class definition:

---

<sub>⏱️ 4m 27s</sub>

### ✅ `view`

**/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s/src/charm.py**

/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s/src/charm.py (lines 57-85)

<details>
<summary>29 lines</summary>

```
57. 
58. logger = logging.getLogger(__name__)
59. 
60. S3Info = namedtuple("S3Info", ["enabled", "region", "bucket", "endpoint"])
61. 
62. INVALID_CORS_MESSAGE = (
63.     "invalid CORS config, `augment_cors_origin` must be enabled or `cors_origin` must be non-empty"  # pylint: disable=line-too-long
64. )
65. 
66. 
67. class MissingRedisRelationDataError(Exception):
68.     """Custom exception to be raised in case of malformed/missing redis relation data."""
69. 
70. 
71. class DiscourseCharm(CharmBase):
72.     """Charm for Discourse on kubernetes."""
73. 
74.     # pylint: disable=too-many-instance-attributes
75.     # All attributes are necessary for the charm functionality
76. 
77.     on = RedisRelationCharmEvents()
78. 
79.     def __init__(self, *args):
80.         """Initialize defaults and event handlers."""
81.         super().__init__(*args)
82. 
83.         self._database = DatabaseHandler(self, DATABASE_RELATION_NAME)
84.         self._oauth = OAuthObserver(self, self._setup_and_activate, self._get_external_hostname)
85.
```

</details>


---

<sub>⏱️ 4m 35s</sub>

### ✅ `edit`

**/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s/src/charm.py**

/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s/src/charm.py

```
File /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s/src/charm.py updated with changes.
```


---

<sub>⏱️ 4m 41s</sub>

### 💬 Copilot

Now update `_get_external_hostname` and `_get_cors_origin`:

---

<sub>⏱️ 4m 41s</sub>

### ✅ `edit`

**/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s/src/charm.py**

/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s/src/charm.py

```
File /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s/src/charm.py updated with changes.
```


---

<sub>⏱️ 4m 49s</sub>

### ✅ `edit`

**/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s/src/charm.py**

/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s/src/charm.py

```
File /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s/src/charm.py updated with changes.
```


---

<sub>⏱️ 4m 53s</sub>

### 💬 Copilot

Now update `_is_config_valid`:

---

<sub>⏱️ 4m 53s</sub>

### ✅ `view`

**/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s/src/charm.py**

/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s/src/charm.py (lines 295-360)

<details>
<summary>66 lines</summary>

```
295.         return container.can_connect() and container.exists(SETUP_COMPLETED_FLAG_FILE)
296. 
297.     def _set_setup_completed(self) -> None:
298.         """Mark the _set_up_discourse process as completed."""
299.         container = self.unit.get_container(CONTAINER_NAME)
300.         container.push(SETUP_COMPLETED_FLAG_FILE, "", make_dirs=True)
301. 
302.     def _is_config_valid(self) -> bool:
303.         """Check that the provided config is valid.
304. 
305.         Returns:
306.             If config is valid.
307.         """
308.         errors = []
309. 
310.         if (
311.             self.config.get("enable_cors")
312.             and self.config.get("cors_origin") == ""
313.             and not self.config.get("augment_cors_origin")
314.         ):
315.             errors.append(INVALID_CORS_MESSAGE)
316. 
317.         if self.config["throttle_level"] not in THROTTLE_LEVELS:
318.             errors.append(f"throttle_level must be one of: {' '.join(THROTTLE_LEVELS.keys())}")
319. 
320.         if (
321.             self.config["force_saml_login"]
322.             and self.model.get_relation(DEFAULT_RELATION_NAME) is None
323.         ):
324.             errors.append("force_saml_login cannot be true without a saml relation")
325.         if self.config["max_category_nesting"] not in MAX_CATEGORY_NESTING_LEVELS:
326.             errors.append(
327.                 "max_category_nesting must be one of: "
328.                 f"{', '.join(map(str, MAX_CATEGORY_NESTING_LEVELS))}"
329.             )
330.         if (
331.             self.config["saml_sync_groups"]
332.             and self.model.get_relation(DEFAULT_RELATION_NAME) is None
333.         ):
334.             errors.append("'saml_sync_groups' cannot be specified without a saml relation")
335. 
336.         if (
337.             self.model.get_relation(DEFAULT_RELATION_NAME) is not None
338.             and not self.config["force_https"]
339.         ):
340.             errors.append("A saml relation cannot be specified without 'force_https' being true")
341. 
342.         if (
343.             self.model.get_relation(OAUTH_RELATION_NAME) is not None
344.             and not self.config["force_https"]
345.         ):
346.             errors.append(
347.                 "An oauth relation cannot be established without 'force_https' being true"
348.             )
349. 
350.         if self.config.get("s3_enabled"):
351.             errors.extend(
352.                 f"'s3_enabled' requires '{s3_config}'"
353.                 for s3_config in REQUIRED_S3_SETTINGS
354.                 if not self.config[s3_config]
355.             )
356. 
357.         if errors:
358.             self.model.unit.status = BlockedStatus(", ".join(errors))
359.         return not errors
360.
```

</details>


---

<sub>⏱️ 5m 6s</sub>

### ✅ `edit`

**/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s/src/charm.py**

/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s/src/charm.py

```
File /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s/src/charm.py updated with changes.
```


---

<sub>⏱️ 5m 12s</sub>

### 💬 Copilot

Now update `_get_saml_config`:

---

<sub>⏱️ 5m 12s</sub>

### ✅ `edit`

**/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s/src/charm.py**

/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s/src/charm.py

```
File /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s/src/charm.py updated with changes.
```


---

<sub>⏱️ 5m 20s</sub>

### 💬 Copilot

Now update `_get_s3_env`:

---

<sub>⏱️ 5m 20s</sub>

### ✅ `edit`

**/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s/src/charm.py**

/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s/src/charm.py

```
File /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s/src/charm.py updated with changes.
```


---

<sub>⏱️ 5m 24s</sub>

### 💬 Copilot

Now update `_create_discourse_environment_settings`:

---

<sub>⏱️ 5m 24s</sub>

### ✅ `view`

**/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s/src/charm.py**

/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s/src/charm.py (lines 480-540)

<details>
<summary>61 lines</summary>

```
480.             "CONTAINER_APP_NAME": CONTAINER_NAME,
481.             "CONTAINER_APP_ROOT": "/srv/discourse",
482.             "CONTAINER_APP_USERNAME": CONTAINER_APP_USERNAME,
483.             "DISCOURSE_CORS_ORIGIN": self._get_cors_origin(),
484.             "DISCOURSE_DB_HOST": database_relation_data["POSTGRES_HOST"],
485.             "DISCOURSE_DB_NAME": database_relation_data["POSTGRES_DB"],
486.             "DISCOURSE_DB_PASSWORD": database_relation_data["POSTGRES_PASSWORD"],
487.             "DISCOURSE_DB_USERNAME": database_relation_data["POSTGRES_USER"],
488.             "DISCOURSE_DEVELOPER_EMAILS": self.config["developer_emails"],
489.             "DISCOURSE_ENABLE_CORS": str(self.config["enable_cors"]).lower(),
490.             "DISCOURSE_HOSTNAME": self._get_external_hostname(),
491.             "DISCOURSE_MAX_CATEGORY_NESTING": str(self.config["max_category_nesting"]),
492.             "DISCOURSE_REDIS_HOST": redis_relation_data[0],
493.             "DISCOURSE_REDIS_PORT": str(redis_relation_data[1]),
494.             "DISCOURSE_REFRESH_MAXMIND_DB_DURING_PRECOMPILE_DAYS": "0",
495.             "DISCOURSE_SERVE_STATIC_ASSETS": "true",
496.             "DISCOURSE_SMTP_ADDRESS": self.config["smtp_address"],
497.             "DISCOURSE_SMTP_AUTHENTICATION": self.config["smtp_authentication"],
498.             "DISCOURSE_SMTP_DOMAIN": self.config["smtp_domain"],
499.             "DISCOURSE_SMTP_ENABLE_START_TLS": self.config["smtp_enable_start_tls"],
500.             "DISCOURSE_SMTP_FORCE_TLS": self.config["smtp_force_tls"],
501.             "DISCOURSE_SMTP_OPENSSL_VERIFY_MODE": self.config["smtp_openssl_verify_mode"],
502.             "DISCOURSE_SMTP_PASSWORD": self.config["smtp_password"],
503.             "DISCOURSE_SMTP_PORT": str(self.config["smtp_port"]),
504.             "DISCOURSE_SMTP_USER_NAME": self.config["smtp_username"],
505.             "RAILS_ENV": "production",
506.             "UNICORN_SIDEKIQ_MAX_RSS": str(self.config["sidekiq_max_memory"]),
507.         }
508.         pod_config.update(self._get_saml_config())
509.         # Add OIDC env vars if oauth relation is established
510.         pod_config.update(self._oauth.get_oidc_env())
511. 
512.         if self.config.get("s3_enabled"):
513.             pod_config.update(self._get_s3_env())
514. 
515.         # We only get valid throttle levels here, otherwise it would be caught
516.         # by `_is_config_valid()`.
517.         # self.config return an Any type
518.         pod_config.update(THROTTLE_LEVELS.get(self.config["throttle_level"]))  # type: ignore
519. 
520.         # Update environment with proxy settings
521.         pod_config["HTTP_PROXY"] = pod_config["http_proxy"] = (
522.             os.environ.get("JUJU_CHARM_HTTP_PROXY") or ""
523.         )
524.         pod_config["HTTPS_PROXY"] = pod_config["https_proxy"] = (
525.             os.environ.get("JUJU_CHARM_HTTPS_PROXY") or ""
526.         )
527.         pod_config["NO_PROXY"] = pod_config["no_proxy"] = (
528.             os.environ.get("JUJU_CHARM_NO_PROXY") or ""
529.         )
530. 
531.         return pod_config
532. 
533.     def _create_layer_config(self) -> ops.pebble.LayerDict:
534.         """Create a layer config based on our current configuration.
535. 
536.         Returns:
537.             Dictionary with the pebble configuration.
538.         """
539.         logger.info("Generating Layer config")
540.         layer_config = {
```

</details>


---

<sub>⏱️ 5m 36s</sub>

### ✅ `edit`

**/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s/src/charm.py**

/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s/src/charm.py

```
File /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s/src/charm.py updated with changes.
```


---

<sub>⏱️ 5m 42s</sub>

### 💬 Copilot

Now update `_should_run_s3_migration`:

---

<sub>⏱️ 5m 42s</sub>

### ✅ `edit`

**/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s/src/charm.py**

/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s/src/charm.py

```
File /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s/src/charm.py updated with changes.
```


---

<sub>⏱️ 5m 46s</sub>

### 💬 Copilot

Now update `_config_force_https`:

---

<sub>⏱️ 5m 46s</sub>

### ✅ `edit`

**/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s/src/charm.py**

/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s/src/charm.py

```
File /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s/src/charm.py updated with changes.
```


---

<sub>⏱️ 5m 51s</sub>

### 💬 Copilot

Now update the action handlers:

---

<sub>⏱️ 5m 51s</sub>

### ✅ `edit`

**/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s/src/charm.py**

/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s/src/charm.py

```
No changes made: old_str and new_str are the same
```


---

<sub>⏱️ 5m 54s</sub>

### ✅ `view`

**/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s/src/charm.py**

/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s/src/charm.py (lines 806-940)

<details>
<summary>135 lines</summary>

```
806. 
807.         Args:
808.             event: Event triggering the promote_user action.
809.         """
810.         container = self.unit.get_container(CONTAINER_NAME)
811.         if not container.can_connect():
812.             event.fail("Unable to connect to container, container is not ready")
813.             return
814. 
815.         email = event.params["email"]
816. 
817.         if not self._user_exists(email):
818.             event.fail(f"User with email {email} does not exist")
819.             return
820. 
821.         process = container.exec(
822.             [
823.                 os.path.join(DISCOURSE_PATH, "bin/bundle"),
824.                 "exec",
825.                 "rake",
826.                 "admin:create",
827.             ],
828.             stdin=f"{email}\nn\nY\n",
829.             working_dir=DISCOURSE_PATH,
830.             user=CONTAINER_APP_USERNAME,
831.             environment=self._create_discourse_environment_settings(),
832.             timeout=60,
833.         )
834.         try:
835.             process.wait_output()
836.             event.set_results({"user": email})
837.         except ExecError as ex:
838.             event.fail(
839.                 f"Failed to make user with email {email} an admin: {ex.stdout}"  # type: ignore
840.             )
841. 
842.     def _on_create_user_action(self, event: ActionEvent) -> None:
843.         """Create a new user in Discourse.
844. 
845.         Args:
846.             event: Event triggering the create_user action.
847.         """
848.         container = self.unit.get_container(CONTAINER_NAME)
849.         if not container.can_connect():
850.             event.fail("Unable to connect to container, container is not ready")
851.             return
852. 
853.         email = event.params["email"]
854.         password = self._generate_password(16)
855. 
856.         if self._user_exists(email):
857.             event.fail(f"User with email {email} already exists")
858.             return
859. 
860.         # Admin flag is optional, if it is true, the user will be created as an admin
861.         admin_flag = "Y" if event.params.get("admin") else "N"
862. 
863.         process = container.exec(
864.             [
865.                 os.path.join(DISCOURSE_PATH, "bin/bundle"),
866.                 "exec",
867.                 "rake",
868.                 "admin:create",
869.             ],
870.             stdin=f"{email}\n{password}\n{password}\n{admin_flag}\n",
871.             working_dir=DISCOURSE_PATH,
872.             user=CONTAINER_APP_USERNAME,
873.             environment=self._create_discourse_environment_settings(),
874.             timeout=60,
875.         )
876.         try:
877.             process.wait_output()
878.         except ExecError as ex:
879.             event.fail(f"Failed to make user with email {email}: {ex.stdout}")  # type: ignore
880.             return
881. 
882.         if (
883.             not event.params.get("admin")
884.             and event.params.get("active")
885.             and not self._activate_user(email)
886.         ):
887.             event.fail(f"Could not find user {email} to activate")
888.             return
889. 
890.         event.set_results({"user": email, "password": password})
891. 
892.     def _generate_password(self, length: int) -> str:
893.         """Generate a random password.
894. 
895.         Args:
896.             length: Length of the password to generate.
897. 
898.         Returns:
899.             Random password.
900.         """
901.         choices = string.ascii_letters + string.digits
902.         password = "".join([secrets.choice(choices) for _ in range(length)])
903.         return password
904. 
905.     def _config_force_https(self) -> None:
906.         """Config Discourse to force_https option based on charm configuration."""
907.         container = self.unit.get_container(CONTAINER_NAME)
908.         force_bool = str(self._typed_config.force_https).lower()
909.         process = container.exec(
910.             [
911.                 os.path.join(DISCOURSE_PATH, "bin/rails"),
912.                 "runner",
913.                 f"SiteSetting.force_https={force_bool}",
914.             ],
915.             working_dir=DISCOURSE_PATH,
916.             user=CONTAINER_APP_USERNAME,
917.             environment=self._create_discourse_environment_settings(),
918.         )
919.         process.wait_output()
920. 
921.     def _on_anonymize_user_action(self, event: ActionEvent) -> None:
922.         """Anonymize data from a user.
923. 
924.         Args:
925.             event: Event triggering the anonymize_user action.
926.         """
927.         username = event.params["username"]
928.         container = self.unit.get_container(CONTAINER_NAME)
929.         if not container.can_connect():
930.             event.fail("Unable to connect to container, container is not ready")
931.             return
932. 
933.         process = container.exec(
934.             [
935.                 os.path.join(DISCOURSE_PATH, "bin/bundle"),
936.                 "exec",
937.                 "rake",
938.                 f"users:anonymize[{username}]",
939.             ],
940.             working_dir=DISCOURSE_PATH,
```

</details>


---

<sub>⏱️ 5m 58s</sub>

### ✅ `edit`

**/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s/src/charm.py**

/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s/src/charm.py

```
File /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s/src/charm.py updated with changes.
```


---

<sub>⏱️ 6m 6s</sub>

### ✅ `edit`

**/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s/src/charm.py**

/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s/src/charm.py

```
File /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s/src/charm.py updated with changes.
```


---

<sub>⏱️ 6m 11s</sub>

### ✅ `edit`

**/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s/src/charm.py**

/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s/src/charm.py

```
File /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s/src/charm.py updated with changes.
```


---

<sub>⏱️ 6m 15s</sub>

### 💬 Copilot

Now bump the ops version:

---

<sub>⏱️ 6m 15s</sub>

### ✅ `edit`

**/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s/pyproject.toml**

/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s/pyproject.toml

```
File /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s/pyproject.toml updated with changes.
```


---

<sub>⏱️ 6m 20s</sub>

### 💬 Copilot

Now let's run the tests:

---

<sub>⏱️ 6m 30s</sub>

### ✅ `bash`

**Run unit tests**

$ cd /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s && tox -e unit 2>&1 | tail -40

<details>
<summary>9 lines</summary>

```
unit: uv-sync> uv sync --locked --python-preference system --no-default-groups --group unit -p /home/ubuntu/.local/share/uv/tools/tox/bin/python
   Updating https://github.com/canonical/saml-test-idp.git (HEAD)
    Updated https://github.com/canonical/saml-test-idp.git (2bd21ece986f62fee50a73506f4e23bd287d38f0)
Resolved 176 packages in 8.85s
The lockfile at `uv.lock` needs to be updated, but `--locked` was provided. To update the lockfile, run `uv lock`.
unit: exit 1 (8.89 seconds) /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s> uv sync --locked --python-preference system --no-default-groups --group unit -p /home/ubuntu/.local/share/uv/tools/tox/bin/python pid=23122
  unit: FAIL code 1 (8.90 seconds)
  evaluation failed :( (8.91 seconds)
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 6m 37s</sub>

### ✅ `bash`

**Update lock file and run unit tests**

$ cd /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s && uv lock && tox -e unit 2>&1 | tail -40

<details>
<summary>41 lines</summary>

```
Using CPython 3.12.3 interpreter at: /usr/bin/python3
⠋ Resolving dependencies...                                                                                             ⠋ Resolving dependencies...                                                                                             ⠙ Resolving dependencies...                                                                                             ⠋ Resolving dependencies...                                                                                             ⠙ Resolving dependencies...                                                                                             ⠙ discourse-k8s-operator==0.0.0                                                                                         ⠙ discourse-k8s-operator==0.0.0                                                                                         ⠙ discourse-k8s-operator==0.0.0                                                                                         ⠙ discourse-k8s-operator==0.0.0                                                                                         ⠙ discourse-k8s-operator==0.0.0                                                                                         ⠙ discourse-k8s-operator==0.0.0                                                                                         ⠙ discourse-k8s-operator==0.0.0                                                                                         ⠙ allure-pytest-collection-report==0.1.0                                                                                ⠙ saml-test-helper==0.2.0                                                                                               ⠙ cosl==1.6.0                                                                                                           ⠙ jsonschema==4.23.0                                                                                                    ⠙ pydantic==2.10.6                                                                                                      ⠙ jubilant==1.7.0                                                                                                       ⠙ protobuf==5.29.6                                                                                                      ⠙ pydantic-core==2.27.2                                                                                                 ⠙ ops==2.23.2                                                                                                           ⠙ ops==2.23.2                                                                                                           ⠙ ops-scenario==7.23.2                                                                                                  Resolved 176 packages in 82ms
INFO     charm:charm.py:959 Starting discourse
INFO     charm:charm.py:538 Generating Layer config
DEBUG    charm:charm.py:460 Got redis connection details from relation of redis-host:1010
DEBUG    charm:charm.py:460 Got redis connection details from relation of redis-host:1010
DEBUG    charm:charm.py:460 Got redis connection details from relation of redis-host:1010
DEBUG    charm:charm.py:460 Got redis connection details from relation of redis-host:1010
INFO     charm:charm.py:959 Starting discourse
INFO     charm:charm.py:538 Generating Layer config
DEBUG    charm:charm.py:460 Got redis connection details from relation of redis-host:1010
DEBUG    charm:charm.py:460 Got redis connection details from relation of redis-host:1010
DEBUG    charm:charm.py:460 Got redis connection details from relation of redis-host:1010
INFO     charm:charm.py:959 Starting discourse
INFO     charm:charm.py:538 Generating Layer config
DEBUG    charm:charm.py:460 Got redis connection details from relation of redis-host:1010
DEBUG    charm:charm.py:460 Got redis connection details from relation of redis-host:1010
DEBUG    charms.grafana_k8s.v0.grafana_dashboard:grafana_dashboard.py:967 Processed dashboard '/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s/src/grafana_dashboards/discourse_service_health.json': replaced original uid '' with '2080bac9940d9de00fcad9af42614e4a99b1caa1'
DEBUG    charms.grafana_k8s.v0.grafana_dashboard:grafana_dashboard.py:967 Processed dashboard '/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s/src/grafana_dashboards/discourse.json': replaced original uid '' with '6f0532a9c282514f1e71ab89b4357454cfc2b51b'
=============================== warnings summary ===============================
tests/unit/test_charm.py: 11 warnings
tests/unit_harness/test_charm.py: 38 warnings
  /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s/lib/charms/data_platform_libs/v0/data_interfaces.py:1160: DeprecationWarning: JujuVersion.from_environ() is deprecated, use self.model.juju_version instead
    self._jujuversion = JujuVersion.from_environ()

tests/unit_harness/test_charm.py: 43 warnings
  /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s/tests/unit_harness/helpers.py:41: PendingDeprecationWarning: Harness is deprecated. For the recommended approach, see: https://documentation.ubuntu.com/ops/2.x/howto/write-unit-tests-for-a-charm.html
    harness = Harness(DiscourseCharm)

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ============================
FAILED tests/unit_harness/test_charm.py::test_on_config_changed_when_no_saml_target - AssertionError: assert ActiveStatus('') == BlockedStatus('force_saml_login ...
FAILED tests/unit_harness/test_charm.py::test_on_config_changed_when_saml_sync_groups_and_no_url_invalid - assert ActiveStatus('') == BlockedStatus("'saml_sync_groups' cannot be spec...
FAILED tests/unit_harness/test_charm.py::test_on_config_changed_when_throttle_mode_invalid - AssertionError: assert False
FAILED tests/unit_harness/test_charm.py::test_on_config_changed_when_s3_and_no_bucket_invalid - assert ActiveStatus('') == BlockedStatus("'s3_enabled' requires 's3_bucket'")
FAILED tests/unit_harness/test_charm.py::test_on_config_changed_when_valid_no_s3_backup_nor_cdn - assert False
FAILED tests/unit_harness/test_charm.py::test_on_config_changed_when_valid - assert False
FAILED tests/unit_harness/test_charm.py::test_sidekiq_env_variable - AssertionError: assert {'CONTAINER_APP_NAME': 'discourse', 'CONTAINER_APP_R...
================== 7 failed, 48 passed, 92 warnings in 1.90s ===================
unit: exit 1 (2.24 seconds) /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s> coverage run --source=src -m pytest --ignore=tests/integration -v --tb native -s pid=23280
  unit: FAIL code 1 (2.27=setup[0.02]+cmd[2.24] seconds)
  evaluation failed :( (2.28 seconds)
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 6m 48s</sub>

### ✅ `bash`

**Debug a failing harness test**

$ cd /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s && python -m pytest tests/unit_harness/test_charm.py::test_on_config_changed_when_valid -v --tb=long -s 2>&1 | tail -60

```
bash: python: command not found
<exited with exit code 0>
```


---

<sub>⏱️ 6m 54s</sub>

### ✅ `bash`

**Debug failing harness test with verbose output**

$ cd /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s && tox -e unit -- tests/unit_harness/test_charm.py::test_on_config_changed_when_valid -v --tb=long -s 2>&1 | tail -60

<details>
<summary>59 lines</summary>

```
tests/unit_harness/test_charm.py:250: AssertionError
------------------------------ Captured log call -------------------------------
INFO     charm:charm.py:968 Stopping discourse
INFO     charm:charm.py:712 Not ready to do config changed action
INFO     charm:charm.py:968 Stopping discourse
INFO     charm:charm.py:687 Pebble or relations not ready, not attempting to setup discourse
INFO     charm:charm.py:968 Stopping discourse
INFO     charm:charm.py:712 Not ready to do config changed action
INFO     charm:charm.py:968 Stopping discourse
INFO     charm:charm.py:968 Stopping discourse
INFO     charm:charm.py:687 Pebble or relations not ready, not attempting to setup discourse
INFO     charm:charm.py:968 Stopping discourse
INFO     charm:charm.py:712 Not ready to do config changed action
INFO     charm:charm.py:968 Stopping discourse
INFO     charms.data_platform_libs.v0.data_interfaces:data_interfaces.py:3906 database created at 2026-02-19 22:59:12.665069
INFO     charm:charm.py:968 Stopping discourse
INFO     charm:charm.py:687 Pebble or relations not ready, not attempting to setup discourse
INFO     charm:charm.py:968 Stopping discourse
INFO     charm:charm.py:712 Not ready to do config changed action
INFO     charm:charm.py:968 Stopping discourse
INFO     charm:charm.py:968 Stopping discourse
INFO     charm:charm.py:687 Pebble or relations not ready, not attempting to setup discourse
INFO     charm:charm.py:968 Stopping discourse
INFO     charm:charm.py:712 Not ready to do config changed action
INFO     charm:charm.py:968 Stopping discourse
INFO     charm:charm.py:968 Stopping discourse
INFO     charm:charm.py:687 Pebble or relations not ready, not attempting to setup discourse
INFO     charm:charm.py:968 Stopping discourse
INFO     charm:charm.py:712 Not ready to do config changed action
INFO     charm:charm.py:968 Stopping discourse
INFO     charm:charm.py:689 Relations are ready and can connect to container, attempting to set up discourse.
INFO     charm:charm.py:693 Discourse setup: about to execute migrations
INFO     charm:charm.py:695 Discourse setup: about to mark the discourse setup process as complete
INFO     charm:charm.py:697 Discourse setup: about to set workload version
INFO     charm:charm.py:646 Setting workload version
INFO     charm:charm.py:699 Discourse setup: completed
INFO     charm:charm.py:959 Starting discourse
INFO     charm:charm.py:538 Generating Layer config
INFO     charm:charm.py:959 Starting discourse
INFO     charm:charm.py:538 Generating Layer config
=============================== warnings summary ===============================
tests/unit_harness/test_charm.py::test_on_config_changed_when_valid
  /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s/tests/unit_harness/helpers.py:41: PendingDeprecationWarning: Harness is deprecated. For the recommended approach, see: https://documentation.ubuntu.com/ops/2.x/howto/write-unit-tests-for-a-charm.html
    harness = Harness(DiscourseCharm)

tests/unit_harness/test_charm.py::test_on_config_changed_when_valid
  /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s/lib/charms/data_platform_libs/v0/data_interfaces.py:1160: DeprecationWarning: JujuVersion.from_environ() is deprecated, use self.model.juju_version instead
    self._jujuversion = JujuVersion.from_environ()

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ============================
FAILED tests/unit_harness/test_charm.py::test_on_config_changed_when_valid - assert False
 +  where False = isinstance(BlockedStatus("A saml relation cannot be specified without 'force_https' being true"), ActiveStatus)
 +    where BlockedStatus("A saml relation cannot be specified without 'force_https' being true") = <ops.model.Unit discourse-k8s/0>.status
 +      where <ops.model.Unit discourse-k8s/0> = <ops.model.Model object at 0x78bf4964bb60>.unit
 +        where <ops.model.Model object at 0x78bf4964bb60> = <ops._private.harness.Harness object at 0x78bf49649070>.model
======================== 1 failed, 2 warnings in 0.47s =========================
unit: exit 1 (0.72 seconds) /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s> coverage run --source=src -m pytest --ignore=tests/integration -v --tb native -s tests/unit_harness/test_charm.py::test_on_config_changed_when_valid -v --tb=long -s pid=23418
  unit: FAIL code 1 (0.75=setup[0.02]+cmd[0.72] seconds)
  evaluation failed :( (0.76 seconds)
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 7m 1s</sub>

### ✅ `bash`

**Find test locations in harness test file**

$ cd /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s && grep -n "test_on_config_changed_when_valid\|test_on_config_changed_when_no_saml\|test_sidekiq\|test_on_config_changed_when_s3\|test_on_config_changed_when_throttle\|test_on_config_changed_when_saml_sync" tests/unit_harness/test_charm.py | head -20

<details>
<summary>8 lines</summary>

```
67:def test_on_config_changed_when_no_saml_target():
79:def test_on_config_changed_when_saml_sync_groups_and_no_url_invalid():
119:def test_on_config_changed_when_throttle_mode_invalid():
130:def test_on_config_changed_when_s3_and_no_bucket_invalid():
148:def test_on_config_changed_when_valid_no_s3_backup_nor_cdn():
219:def test_on_config_changed_when_valid():
522:def test_sidekiq_env_variable():
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 7m 6s</sub>

### ✅ `view`

**/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s/tests/unit_harness/test_charm.py**

/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s/tests/unit_harness/test_charm.py (lines 219-260)

<details>
<summary>42 lines</summary>

```
219. def test_on_config_changed_when_valid():
220.     """
221.     arrange: given a deployed discourse charm with all the required relations
222.     act: when a valid configuration is provided
223.     assert: the appropriate configuration values are passed to the pod and the unit
224.         reaches Active status.
225.     """
226.     harness = helpers.start_harness(
227.         with_config={
228.             "developer_emails": "user@foo.internal",
229.             "enable_cors": True,
230.             "external_hostname": "discourse.local",
231.             "force_saml_login": True,
232.             "saml_sync_groups": "group1",
233.             "smtp_address": "smtp.internal",
234.             "smtp_domain": "foo.internal",
235.             "smtp_password": "OBV10USLYF4K3",  # nosec B105
236.             "smtp_username": "apikey",
237.             "s3_access_key_id": "3|33+",
238.             "s3_backup_bucket": "back-bucket",
239.             "s3_bucket": "who-s-a-good-bucket?",
240.             "s3_cdn_url": "s3.cdn",
241.             "s3_enabled": True,
242.             "s3_endpoint": "s3.endpoint",
243.             "s3_region": "the-infinite-and-beyond",
244.             "s3_secret_access_key": "s|kI0ure_k3Y",  # nosec B105
245.             "force_https": True,
246.         },
247.         saml_fields=(True, "https://login.ubuntu.com", "fingerprint"),
248.     )
249.     harness.container_pebble_ready(SERVICE_NAME)
250.     assert isinstance(harness.model.unit.status, ActiveStatus)
251. 
252.     updated_plan = harness.get_container_pebble_plan(SERVICE_NAME).to_dict()
253.     updated_plan_env = updated_plan["services"][SERVICE_NAME]["environment"]
254.     assert updated_plan_env["DISCOURSE_BACKUP_LOCATION"] == "s3"
255.     assert updated_plan_env["DISCOURSE_CORS_ORIGIN"] == "https://discourse.local,s3.cdn"
256.     assert updated_plan_env["DISCOURSE_DB_HOST"] == "dbhost"
257.     assert updated_plan_env["DISCOURSE_DB_NAME"] == DATABASE_NAME
258.     assert updated_plan_env["DISCOURSE_DB_PASSWORD"] == "somepasswd"
259.     assert updated_plan_env["DISCOURSE_DB_USERNAME"] == "someuser"
260.     assert updated_plan_env["DISCOURSE_DEVELOPER_EMAILS"] == "user@foo.internal"
```

</details>


---

<sub>⏱️ 7m 6s</sub>

### ✅ `view`

**/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s/tests/unit_harness/test_charm.py**

/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s/tests/unit_harness/test_charm.py (lines 1-66)

<details>
<summary>66 lines</summary>

```
1. # Copyright 2026 Canonical Ltd.
2. # See LICENSE file for licensing details.
3. 
4. """Unit tests for Discourse charm."""
5. 
6. # pylint: disable=protected-access
7. # Protected access check is disabled in tests as we're injecting test data
8. 
9. import secrets
10. from unittest.mock import MagicMock, patch
11. 
12. import ops
13. import pytest
14. from ops.model import ActiveStatus, BlockedStatus, WaitingStatus
15. 
16. from charm import CONTAINER_NAME, DISCOURSE_PATH, SERVICE_NAME
17. from constants import DATABASE_NAME
18. from tests.unit_harness import helpers
19. 
20. 
21. @pytest.mark.parametrize(
22.     "with_postgres, with_redis, with_ingress, status",
23.     [
24.         (False, False, False, WaitingStatus("Waiting for database relation")),
25.         (False, True, False, WaitingStatus("Waiting for database relation")),
26.         (True, False, False, WaitingStatus("Waiting for redis relation")),
27.         (True, True, False, ActiveStatus()),
28.         (False, False, True, WaitingStatus("Waiting for database relation")),
29.         (False, True, True, WaitingStatus("Waiting for database relation")),
30.         (True, False, True, WaitingStatus("Waiting for redis relation")),
31.         (True, True, True, ActiveStatus()),
32.     ],
33.     ids=[
34.         "No relation",
35.         "Only redis",
36.         "Only postgres",
37.         "Postgres+redis",
38.         "Only ingress",
39.         "Redis+ingress",
40.         "Postgres+ingress",
41.         "All relations",
42.     ],
43. )
44. def test_relations(with_postgres, with_redis, with_ingress, status):
45.     """
46.     arrange: given a deployed discourse charm
47.     act: when pebble ready event is triggered
48.     assert: it will have the correct status depending on the relations
49.     """
50.     harness = helpers.start_harness(
51.         with_postgres=with_postgres, with_redis=with_redis, with_ingress=with_ingress
52.     )
53.     harness.container_pebble_ready("discourse")
54.     assert harness.model.unit.status == status
55. 
56. 
57. def test_ingress_relation_not_ready():
58.     """
59.     arrange: given a deployed discourse charm with the ingress established
60.     act: when pebble ready event is triggered
61.     assert: it will wait for the ingress relation.
62.     """
63.     harness = helpers.start_harness(with_postgres=False, with_redis=False, with_ingress=True)
64.     assert harness.model.unit.status == WaitingStatus("Waiting for database relation")
65. 
66.
```

</details>


---

<sub>⏱️ 7m 14s</sub>

### ✅ `view`

**/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s/tests/unit_harness/helpers.py**

/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s/tests/unit_harness/helpers.py

<details>
<summary>166 lines</summary>

```
1. # Copyright 2026 Canonical Ltd.
2. # See LICENSE file for licensing details.
3. 
4. """helpers for the unit tests."""
5. 
6. import contextlib
7. import typing
8. import unittest.mock
9. 
10. from ops.model import Container
11. from ops.testing import Harness
12. 
13. from charm import DiscourseCharm
14. 
15. DATABASE_NAME = "discourse"
16. 
17. 
18. def start_harness(  # pylint: disable=too-many-arguments
19.     *,
20.     saml_fields: tuple = (False, ""),
21.     with_postgres: bool = True,
22.     with_redis: bool = True,
23.     with_ingress: bool = False,
24.     with_config: typing.Optional[typing.Dict[str, typing.Any]] = None,
25.     run_initial_hooks=True,
26. ):
27.     """Start a harness discourse charm.
28. 
29.     This is also a workaround for the fact that Harness
30.     doesn't reinitialize the charm as expected.
31.     Ref: https://github.com/canonical/operator/issues/736
32. 
33.     Args:
34.         - with_postgres: should a postgres relation be added
35.         - with_redis: should a redis relation be added
36.         - with_ingress: should a ingress relation be added
37.         - with_config: apply some configuration to the charm
38. 
39.     Returns: a ready to use harness instance
40.     """
41.     harness = Harness(DiscourseCharm)
42.     if run_initial_hooks:
43.         harness.begin_with_initial_hooks()
44.     else:
45.         harness.begin()
46. 
47.     # We catch all exec calls to the container by default
48.     harness.handle_exec("discourse", [], result=0)
49. 
50.     if with_postgres:
51.         add_postgres_relation(harness)
52. 
53.     if with_redis:
54.         add_redis_relation(harness)
55. 
56.     if with_ingress:
57.         _add_ingress_relation(harness)
58. 
59.     if saml_fields[0]:
60.         _add_saml_relation(harness, saml_fields[1])
61. 
62.     if with_config is not None:
63.         harness.update_config(with_config)
64. 
65.     return harness
66. 
67. 
68. @contextlib.contextmanager
69. def _patch_setup_completed():
70.     """Patch filesystem calls in the _is_setup_completed and _set_setup_completed functions."""
71.     setup_completed = False
72. 
73.     def exists(*_args, **_kwargs):
74.         return setup_completed
75. 
76.     def push(*_args, **_kwargs):
77.         nonlocal setup_completed
78.         setup_completed = True
79. 
80.     with unittest.mock.patch.multiple(Container, exists=exists, push=push):
81.         yield
82. 
83. 
84. def add_postgres_relation(harness):
85.     """Add postgresql relation and relation data to the charm.
86. 
87.     Args:
88.         - A harness instance
89. 
90.     Returns: the same harness instance with an added relation
91.     """
92.     relation_data = {
93.         "database": DATABASE_NAME,
94.         "endpoints": "dbhost:5432,dbhost-2:5432",
95.         "password": "somepasswd",  # nosec
96.         "username": "someuser",
97.     }
98. 
99.     harness.db_relation_id = harness.add_relation("database", "postgresql")
100.     harness.add_relation_unit(harness.db_relation_id, "postgresql/0")
101.     harness.update_relation_data(
102.         harness.db_relation_id,
103.         "postgresql",
104.         relation_data,
105.     )
106. 
107. 
108. def add_redis_relation(harness, relation_data=None, app_data=None):
109.     """Add redis relation and relation data to the charm.
110. 
111.     Args:
112.         - A harness instance
113. 
114.     Returns: the same harness instance with an added relation
115.     """
116.     redis_relation_id = harness.add_relation(
117.         "redis",
118.         "redis",
119.         app_data={"leader-host": "redis-host"} if app_data is None else app_data,
120.     )
121.     harness.add_relation_unit(redis_relation_id, "redis/0")
122.     harness.update_relation_data(
123.         redis_relation_id,
124.         "redis/0",
125.         {"hostname": "redis-host", "port": "1010"} if relation_data is None else relation_data,
126.     )
127. 
128. 
129. def _add_ingress_relation(harness):
130.     """Add ingress relation and relation data to the charm.
131. 
132.     Args:
133.         - A harness instance
134. 
135.     Returns: the same harness instance with an added relation
136.     """
137.     nginx_route_relation_id = harness.add_relation("nginx-route", "ingress")
138.     harness.add_relation_unit(nginx_route_relation_id, "ingress/0")
139. 
140. 
141. def _add_saml_relation(harness, saml_target):
142.     """Add ingress relation and relation data to the charm.
143. 
144.     Args:
145.         - A harness instance
146. 
147.     Returns: the same harness instance with an added relation
148.     """
149.     harness.set_leader(True)
150.     saml_relation_id = harness.add_relation("saml", "saml-integrator")
151.     harness.add_relation_unit(saml_relation_id, "saml-integrator/0")
152.     harness.disable_hooks()
153.     binding = "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"
154.     harness.update_relation_data(
155.         relation_id=saml_relation_id,
156.         app_or_unit="saml-integrator",
157.         key_values={
158.             "entity_id": saml_target,
159.             "metadata_url": f"{saml_target}/saml/metadata",
160.             "x509certs": "test",
161.             "single_sign_on_service_redirect_url": f"{saml_target}/+saml",
162.             "single_sign_on_service_redirect_binding": binding,
163.         },
164.     )
165.     harness.enable_hooks()
166.
```

</details>


---

<sub>⏱️ 8m 3s</sub>

### 💬 Copilot

The Harness reuses the charm instance across events (unlike the new `ops.testing`), so `self._typed_config` set once in `__init__` becomes stale after `update_config`. I need to use a `@property` instead:

---

<sub>⏱️ 8m 3s</sub>

### ✅ `view`

**/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s/src/charm.py**

/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s/src/charm.py (lines 112-135)

<details>
<summary>24 lines</summary>

```
112.             self._database.database.on.database_created, self._on_database_created
113.         )
114.         self.framework.observe(
115.             self._database.database.on.endpoints_changed, self._on_database_endpoints_changed
116.         )
117.         self.framework.observe(
118.             self.on[DATABASE_RELATION_NAME].relation_broken,
119.             self._on_database_relation_broken,
120.         )
121. 
122.         self._require_nginx_route()
123.         self.saml = SamlRequires(self)
124.         self.framework.observe(self.saml.on.saml_data_available, self._on_saml_data_available)
125. 
126.         self.framework.observe(self.on.start, self._on_start)
127.         self.framework.observe(self.on.upgrade_charm, self._on_upgrade_charm)
128.         self.framework.observe(self.on.discourse_pebble_ready, self._on_discourse_pebble_ready)
129.         self.framework.observe(self.on.config_changed, self._on_config_changed)
130.         self.framework.observe(self.on.promote_user_action, self._on_promote_user_action)
131.         self.framework.observe(self.on.create_user_action, self._on_create_user_action)
132.         self.framework.observe(self.on.anonymize_user_action, self._on_anonymize_user_action)
133. 
134.         self.redis = RedisRequires(self)
135.         self.framework.observe(self.on.redis_relation_updated, self._redis_relation_changed)
```

</details>


---

<sub>⏱️ 8m 7s</sub>

### ✅ `view`

**/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s/src/charm.py**

/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s/src/charm.py (lines 97-115)

<details>
<summary>19 lines</summary>

```
97.     # pylint: disable=too-many-instance-attributes
98.     # All attributes are necessary for the charm functionality
99. 
100.     on = RedisRelationCharmEvents()
101. 
102.     def __init__(self, *args):
103.         """Initialize defaults and event handlers."""
104.         super().__init__(*args)
105. 
106.         self._typed_config = self.load_config(DiscourseConfig)
107. 
108.         self._database = DatabaseHandler(self, DATABASE_RELATION_NAME)
109.         self._oauth = OAuthObserver(self, self._setup_and_activate, self._get_external_hostname)
110. 
111.         self.framework.observe(
112.             self._database.database.on.database_created, self._on_database_created
113.         )
114.         self.framework.observe(
115.             self._database.database.on.endpoints_changed, self._on_database_endpoints_changed
```

</details>


---

<sub>⏱️ 8m 14s</sub>

### ✅ `edit`

**/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s/src/charm.py**

/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s/src/charm.py

```
File /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s/src/charm.py updated with changes.
```


---

<sub>⏱️ 8m 18s</sub>

### 💬 Copilot

Now I need to add a `@property` for `_typed_config` somewhere in the class. Let me add it right after the class-level `on` attribute:

---

<sub>⏱️ 8m 18s</sub>

### ✅ `view`

**/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s/src/charm.py**

/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s/src/charm.py (lines 148-175)

<details>
<summary>28 lines</summary>

```
148.         """Handle start event.
149. 
150.         Args:
151.             event: Event triggering the start event handler.
152.         """
153.         self._setup_and_activate()
154. 
155.     def _on_upgrade_charm(self, _: ops.UpgradeCharmEvent) -> None:
156.         """Handle upgrade charm event.
157. 
158.         Args:
159.             event: Event triggering the upgrade charm event handler.
160.         """
161.         self.on[self.restart_manager.name].acquire_lock.emit()
162. 
163.     def _on_discourse_pebble_ready(self, _: ops.PebbleReadyEvent) -> None:
164.         """Handle discourse pebble ready event.
165. 
166.         Args:
167.             event: Event triggering the discourse pebble ready event handler.
168.         """
169.         self._setup_and_activate()
170. 
171.     def _redis_relation_changed(self, _: HookEvent) -> None:
172.         """Handle redis relation changed event.
173. 
174.         Args:
175.             event: Event triggering the redis relation changed event handler.
```

</details>


---

<sub>⏱️ 8m 22s</sub>

### ✅ `view`

**/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s/src/charm.py**

/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s/src/charm.py (lines 138-150)

<details>
<summary>13 lines</summary>

```
138.         self._logging = LogProxyConsumer(
139.             self, relation_name="logging", log_files=LOG_PATHS, container_name=CONTAINER_NAME
140.         )
141.         self._grafana_dashboards = GrafanaDashboardProvider(self)
142. 
143.         self.restart_manager = RollingOpsManager(
144.             charm=self, relation="restart", callback=self._on_rolling_restart
145.         )
146. 
147.     def _on_start(self, _: ops.StartEvent) -> None:
148.         """Handle start event.
149. 
150.         Args:
```

</details>


---

<sub>⏱️ 8m 27s</sub>

### ✅ `edit`

**/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s/src/charm.py**

/tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s/src/charm.py

```
File /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s/src/charm.py updated with changes.
```


---

<sub>⏱️ 8m 35s</sub>

### ✅ `bash`

**Run unit tests again**

$ cd /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s && tox -e unit 2>&1 | tail -25

<details>
<summary>24 lines</summary>

```
tests/unit_harness/test_charm.py::test_on_config_changed_when_valid
tests/unit_harness/test_charm.py::test_on_config_changed_when_valid
tests/unit_harness/test_charm.py::test_on_config_changed_when_valid
tests/unit_harness/test_charm.py::test_on_config_changed_when_valid
tests/unit_harness/test_charm.py::test_on_config_changed_when_valid
tests/unit_harness/test_charm.py::test_on_config_changed_when_valid
tests/unit_harness/test_charm.py::test_on_config_changed_when_valid
  /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s/lib/charms/saml_integrator/v0/saml.py:211: PydanticDeprecatedSince20: `parse_obj_as` is deprecated. Use `pydantic.TypeAdapter.validate_python` instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.10/migration/
    parse_obj_as(AnyHttpUrl, relation_data.get("metadata_url"))

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
======================= 55 passed, 106 warnings in 2.22s =======================
unit: commands[1]> coverage report
Name                    Stmts   Miss Branch BrPart  Cover   Missing
-------------------------------------------------------------------
src/charm.py              396     42     96     15    88%   200, 208-209, 221, 281->285, 329, 398->406, 430->435, 447, 638-640, 645-646, 658-660, 665-666, 678-680, 703-705, 743->exit, 802-805, 815-816, 841-842, 854-855, 883-885, 892-893, 936-937, 953-954, 964->exit, 978
src/config.py              31      0      0      0   100%
src/constants.py           21      0      0      0   100%
src/database.py            29      1      8      1    95%   57
src/oauth_observer.py      54      8      8      2    84%   65, 80-81, 111, 114-123
-------------------------------------------------------------------
TOTAL                     531     51    112     18    89%
  unit: OK (2.67=setup[0.03]+cmd[2.56,0.08] seconds)
  congratulations :) (2.68 seconds)
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 8m 39s</sub>

### 💬 Copilot

All 55 tests pass. Now let's run the linter:

---

<sub>⏱️ 8m 40s</sub>

### ✅ `bash`

**Run linter**

$ cd /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s && tox -e lint 2>&1 | tail -30

<details>
<summary>28 lines</summary>

```
if saml_sync_groups:
             # Per https://github.com/discourse/discourse-saml setting this to `true`
@@ -417,9 +415,7 @@
             "DISCOURSE_S3_ENDPOINT": self._typed_config.s3_endpoint,
             "DISCOURSE_S3_REGION": self._typed_config.s3_region,
             "DISCOURSE_S3_SECRET_ACCESS_KEY": self._typed_config.s3_secret_access_key,
-            "DISCOURSE_S3_INSTALL_CORS_RULE": str(
-                self._typed_config.s3_install_cors_rule
-            ).lower(),
+            "DISCOURSE_S3_INSTALL_CORS_RULE": str(self._typed_config.s3_install_cors_rule).lower(),
             "DISCOURSE_USE_S3": "true",
         }
         if self._typed_config.s3_backup_bucket:
@@ -884,11 +880,7 @@
             event.fail(f"Failed to make user with email {email}: {ex.stdout}")  # type: ignore
             return
 
-        if (
-            not params.admin
-            and params.active
-            and not self._activate_user(email)
-        ):
+        if not params.admin and params.active and not self._activate_user(email):
             event.fail(f"Could not find user {email} to activate")
             return
 

lint: exit 1 (0.01 seconds) /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s> ruff format --check --diff src tests pid=23626
  lint: FAIL code 1 (0.21=setup[0.12]+cmd[0.08,0.01] seconds)
  evaluation failed :( (0.23 seconds)
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 8m 47s</sub>

### ✅ `bash`

**Auto-fix formatting**

$ cd /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s && tox -e fmt 2>&1 | tail -10

<details>
<summary>11 lines</summary>

```
fmt: venv> /home/ubuntu/.local/share/uv/tools/tox/bin/uv venv -p /home/ubuntu/.local/share/uv/tools/tox/bin/python --allow-existing --python-preference system /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s/.tox/fmt
fmt: uv-sync> uv sync --locked --python-preference system --no-default-groups --group fmt -p /home/ubuntu/.local/share/uv/tools/tox/bin/python
fmt: commands[0]> ruff check --fix --select I src tests
warning: Selection `CPY` has no effect because preview is not enabled.
Found 1 error (1 fixed, 0 remaining).
fmt: commands[1]> ruff format src tests
warning: Selection `CPY` has no effect because preview is not enabled.
1 file reformatted, 19 files left unchanged
  fmt: OK (0.10=setup[0.08]+cmd[0.01,0.01] seconds)
  congratulations :) (0.12 seconds)
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 8m 56s</sub>

### ✅ `bash`

**Run linter after formatting**

$ cd /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s && tox -e lint 2>&1 | tail -20

<details>
<summary>13 lines</summary>

```
lint: uv-sync> uv sync --locked --python-preference system --no-default-groups --group lint -p /home/ubuntu/.local/share/uv/tools/tox/bin/python
lint: commands[0]> codespell /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s
lint: commands[1]> ruff format --check --diff src tests
warning: Selection `CPY` has no effect because preview is not enabled.
20 files already formatted
lint: commands[2]> ruff check src tests
warning: Selection `CPY` has no effect because preview is not enabled.
All checks passed!
lint: commands[3]> mypy src tests
Success: no issues found in 20 source files
  lint: OK (2.93=setup[0.03]+cmd[0.08,0.01,0.01,2.80] seconds)
  congratulations :) (2.94 seconds)
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 9m 1s</sub>

### 💬 Copilot

All lint and tests pass. Let me commit the changes:

---

<sub>⏱️ 9m 2s</sub>

### ✅ `bash`

**Check staged changes**

$ cd /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s && git add -A && git diff --staged --stat

<details>
<summary>8 lines</summary>

```
.baseline_commit                |   1 +
 .github/copilot-instructions.md | 211 ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
 pyproject.toml                  |   2 +-
 src/charm.py                    | 154 +++++++++++++++++++++++++++++++++-------------------------
 src/config.py                   |  40 +++++++++++++++
 uv.lock                         |   2 +-
 6 files changed, 343 insertions(+), 67 deletions(-)
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 9m 11s</sub>

### ✅ `bash`

**Commit changes**

$ cd /tmp/ops-upgrade-experiment/discourse-k8s-operator__all__C1s && git commit -m "Upgrade ops usage: typed config, action params, version bump

- Add DiscourseConfig Pydantic model in src/config.py mirroring all
  config.yaml options with typed fields and defaults
- Use self.load_config(DiscourseConfig) via a property to replace all
  self.config[...] / self.config.get(...) accesses with typed field access
- Add PromoteUserParams, CreateUserParams, AnonymizeUserParams dataclasses
  and replace event.params[...] with event.load_params() in all three
  action handlers
- Bump ops pin from ops==2.23.2 to ops>=2.23.0

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"

<details>
<summary>6 lines</summary>

```
[detached HEAD b81385d] Upgrade ops usage: typed config, action params, version bump
 6 files changed, 343 insertions(+), 67 deletions(-)
 create mode 100644 .baseline_commit
 create mode 100644 .github/copilot-instructions.md
 create mode 100644 src/config.py
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 9m 20s</sub>

### ❌ `store_memory`

<details>
<summary>Arguments</summary>

```json
{
  "subject": "testing patterns",
  "fact": "This charm has both old Harness tests (tests/unit_harness/) and new ops.testing Scenario tests (tests/unit/). When storing config in __init__ via load_config, use a @property instead to avoid stale values in the Harness (which reuses charm instances across events).",
  "citations": "src/charm.py:147-150, tests/unit_harness/helpers.py:41-64",
  "reason": "The charm has both old Harness and new ops.testing tests. The Harness reuses the charm instance across events so instance variables set in __init__ become stale when config changes. A @property ensures fresh config on each access. This is critical for future code changes involving load_config.",
  "category": "general"
}
```

</details>

```
Unable to store memory. You can continue with your task without storing this information.
```


---

<sub>⏱️ 9m 28s</sub>

### ✅ `task_complete`

**Applied three ops upgrades to the discourse-k8s-operator charm:

1. **Config Classes (A)** — Created `src/config.py` with a Pydantic `DiscourseConfig` model mirroring all `config.yaml` options. Added a `@property _typed_config` to the charm class that calls `self.load_config(DiscourseConfig)` on each access (property rather than `__init__` assignment ensures correct behavior with both Harness and modern `ops.testing`). Replaced all `self.config[...]` / `self.config.get(...)` calls throughout `charm.py` with typed attribute access.

2. **Action Classes (B)** — Added `PromoteUserParams`, `CreateUserParams`, and `AnonymizeUserParams` dataclasses and replaced `event.params[...]` / `event.params.get(...)` with `event.load_params()` in all three action handlers.

3. **Ops version bump** — Changed `ops==2.23.2` → `ops>=2.23.0` in `pyproject.toml` and updated `uv.lock`.

All 55 unit tests pass and linting (ruff, mypy, codespell) is clean.**

<details>
<summary>Arguments</summary>

```json
{
  "summary": "Applied three ops upgrades to the discourse-k8s-operator charm:\n\n1. **Config Classes (A)** — Created `src/config.py` with a Pydantic `DiscourseConfig` model mirroring all `config.yaml` options. Added a `@property _typed_config` to the charm class that calls `self.load_config(DiscourseConfig)` on each access (property rather than `__init__` assignment ensures correct behavior with both Harness and modern `ops.testing`). Replaced all `self.config[...]` / `self.config.get(...)` calls throughout `charm.py` with typed attribute access.\n\n2. **Action Classes (B)** — Added `PromoteUserParams`, `CreateUserParams`, and `AnonymizeUserParams` dataclasses and replaced `event.params[...]` / `event.params.get(...)` with `event.load_params()` in all three action handlers.\n\n3. **Ops version bump** — Changed `ops==2.23.2` → `ops>=2.23.0` in `pyproject.toml` and updated `uv.lock`.\n\nAll 55 unit tests pass and linting (ruff, mypy, codespell) is clean."
}
```

</details>

<details>
<summary>5 lines</summary>

```
Applied three ops upgrades to the discourse-k8s-operator charm:

1. **Config Classes (A)** — Created `src/config.py` with a Pydantic `DiscourseConfig` model mirroring all `config.yaml` options. Added a `@property _typed_config` to the charm class that calls `self.load_config(DiscourseConfig)` on each access (property rather than `__init__` assignment ensures correct behavior with both Harness and modern `ops.testing`). Replaced all `self.config[...]` / `self.config.get(...)` calls throughout `charm.py` with typed attribute access.

2. **Action Classes (B)** — Added `PromoteUserParams`, `CreateUserParams`, and `AnonymizeUserParams` dataclasses and replaced `event.params[...]` / `event.params.get(...)` with `event.load_params()` in all three action handlers.

3. **Ops version bump** — Changed `ops==2.23.2` → `ops>=2.23.0` in `pyproject.toml` and updated `uv.lock`.

All 55 unit tests pass and linting (ruff, mypy, codespell) is clean.
```

</details>


---

<sub>⏱️ 9m 35s</sub>

### ℹ️ Info

Response was interrupted due to a server error. Retrying...

---

<sub>⏱️ 9m 39s</sub>

### ℹ️ Info

Response was interrupted due to a server error. Retrying...

---

<sub>⏱️ 9m 44s</sub>

### ℹ️ Info

Response was interrupted due to a server error. Retrying...

---

<sub>⏱️ 9m 49s</sub>

### ℹ️ Info

Response was interrupted due to a server error. Retrying...

---

<sub>⏱️ 9m 54s</sub>

### ℹ️ Info

Response was interrupted due to a server error. Retrying...

---

<sub>⏱️ 9m 58s</sub>

### ❌ Error

Execution failed: Error: Failed to get response from the AI model; retried 5 times (total retry wait time: 6.161058580785209 seconds) Last error: Unknown error

---

<sub>Generated by [GitHub Copilot CLI](https://github.com/features/copilot/cli)</sub>
