# 🤖 Copilot CLI Session

> **Session ID:** `49d2b2bb-caaf-4e31-8d81-c9058e640530`
> **Duration:** 12m 23s
> **Exported:** 3/11/2026, 2:17:34 PM

<sub>⏱️ 4s</sub>

### 👤 User

ops 2.23.0 added support for typed relation data classes with Relation.save() and Relation.load(). The hive-metastore-k8s-operator (https://github.com/canonical/hive-metastore-k8s-operator) already uses this feature -- look at how they did it and update this charm similarly.

---

<sub>⏱️ 10s</sub>

### ✅ `view`

**/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__relation-data-classes__C3**

/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__relation-data-classes__C3

<details>
<summary>25 lines</summary>

```
.baseline_commit
.git
.github
.gitignore
.jujuignore
.ruff_cache
.tox
.venv
.wokeignore
CODEOWNERS
CONTRIBUTING.md
INTEGRATING.md
LICENSE
README.md
RELEASE.md
SECURITY.md
charmcraft.yaml
icon.svg
lib
pyproject.toml
src
terraform
tests
tox.ini
uv.lock
```

</details>


---

<sub>⏱️ 11s</sub>

### ✅ `github-mcp-server-get_file_contents`

**/**

<details>
<summary>Arguments</summary>

```json
{
  "owner": "canonical",
  "repo": "hive-metastore-k8s-operator",
  "path": "/"
}
```

</details>

```
[{"type":"dir","size":0,"name":".github","path":".github","sha":"b4dafa1c00a34ace0db27b84639f95e4a92d1a6f","url":"https://api.github.com/repos/canonical/hive-metastore-k8s-operator/contents/.github?ref=127daa0912331ad2b8567a664d5cf40fe7d102b3","git_url":"https://api.github.com/repos/canonical/hive-metastore-k8s-operator/git/trees/b4dafa1c00a34ace0db27b84639f95e4a92d1a6f","html_url":"https://github.com/canonical/hive-metastore-k8s-operator/tree/127daa0912331ad2b8567a664d5cf40fe7d102b3/.github"},{"type":"file","size":82,"name":".gitignore","path":".gitignore","sha":"208ff563bf92bef3c48b5986828311675e1afcf2","url":"https://api.github.com/repos/canonical/hive-metastore-k8s-operator/contents/.gitignore?ref=127daa0912331ad2b8567a664d5cf40fe7d102b3","git_url":"https://api.github.com/repos/canonical/hive-metastore-k8s-operator/git/blobs/208ff563bf92bef3c48b5986828311675e1afcf2","html_url":"https://github.com/canonical/hive-metastore-k8s-operator/blob/127daa0912331ad2b8567a664d5cf40fe7d102b3/.gitignore","download_url":"https://raw.githubusercontent.com/canonical/hive-metastore-k8s-operator/127daa0912331ad2b8567a664d5cf40fe7d102b3/.gitignore"},{"type":"file","size":1132,"name":".licenserc.yaml","path":".licenserc.yaml","sha":"511ad6aafcaa58676b1dddfed265a0eb0c5c1786","url":"https://api.github.com/repos/canonical/hive-metastore-k8s-operator/contents/.licenserc.yaml?ref=127daa0912331ad2b8567a664d5cf40fe7d102b3","git_url":"https://api.github.com/repos/canonical/hive-metastore-k8s-operator/git/blobs/511ad6aafcaa58676b1dddfed265a0eb0c5c1786","html_url":"https://github.com/canonical/hive-metastore-k8s-operator/blob/127daa0912331ad2b8567a664d5cf40fe7d102b3/.licenserc.yaml","download_url":"https://raw.githubusercontent.com/canonical/hive-metastore-k8s-operator/127daa0912331ad2b8567a664d5cf40fe7d102b3/.licenserc.yaml"},{"type":"file","size":5,"name":".python-version","path":".python-version","sha":"e4fba2183587225f216eeada4c78dfab6b2e65f5","url":"https://api.github.com/repos/canonical/hive-metastore-k8s-operator/contents/.python-version?ref=127daa0912331ad2b8567a664d5cf40fe7d102b3","git_url":"https://api.github.com/repos/canonical/hive-metastore-k8s-operator/git/blobs/e4fba2183587225f216eeada4c78dfab6b2e65f5","html_url":"https://github.com/canonical/hive-metastore-k8s-operator/blob/127daa0912331ad2b8567a664d5cf40fe7d102b3/.python-version","download_url":"https://raw.githubusercontent.com/canonical/hive-metastore-k8s-operator/127daa0912331ad2b8567a664d5cf40fe7d102b3/.python-version"},{"type":"file","size":419,"name":".trivyignore","path":".trivyignore","sha":"bb8ae724ca1d8227854ccf6e26b772378aae158a","url":"https://api.github.com/repos/canonical/hive-metastore-k8s-operator/contents/.trivyignore?ref=127daa0912331ad2b8567a664d5cf40fe7d102b3","git_url":"https://api.github.com/repos/canonical/hive-metastore-k8s-operator/git/blobs/bb8ae724ca1d8227854ccf6e26b772378aae158a","html_url":"https://github.com/canonical/hive-metastore-k8s-operator/blob/127daa0912331ad2b8567a664d5cf40fe7d102b3/.trivyignore","download_url":"https://raw.githubusercontent.com/canonical/hive-metastore-k8s-operator/127daa0912331ad2b8567a664d5cf40fe7d102b3/.trivyignore"},{"type":"file","size":3368,"name":"CONTRIBUTING.md","path":"CONTRIBUTING.md","sha":"15fc810dd9024e506b69a6c22c177234b6a4eda9","url":"https://api.github.com/repos/canonical/hive-metastore-k8s-operator/contents/CONTRIBUTING.md?ref=127daa0912331ad2b8567a664d5cf40fe7d102b3","git_url":"https://api.github.com/repos/canonical/hive-metastore-k8s-operator/git/blobs/15fc810dd9024e506b69a6c22c177234b6a4eda9","html_url":"https://github.com/canonical/hive-metastore-k8s-operator/blob/127daa0912331ad2b8567a664d5cf40fe7d102b3/CONTRIBUTING.md","download_url":"https://raw.githubusercontent.com/canonical/hive-metastore-k8s-operator/127daa0912331ad2b8567a664d5cf40fe7d102b3/CONTRIBUTING.md"},{"type":"file","size":11346,"name":"LICENSE","path":"LICENSE","sha":"3fa1dd0dbee32d2b299a6959e96adbce6d5fcbd1","url":"https://api.github.com/repos/canonical/hive-metastore-k8s-operator/contents/LICENSE?ref=127daa0912331ad2b8567a664d5cf40fe7d102b3","git_url":"https://api.github.com/repos/canonical/hive-metastore-k8s-operator/git/blobs/3fa1dd0dbee32d2b299a6959e96adbce6d5fcbd1","html_url":"https://github.com/canonical/hive-metastore-k8s-operator/blob/127daa0912331ad2b8567a664d5cf40fe7d102b3/LICENSE","download_url":"https://raw.githubusercontent.com/canonical/hive-metastore-k8s-operator/127daa0912331ad2b8567a664d5cf40fe7d102b3/LICENSE"},{"type":"file","size":4736,"name":"Makefile","path":"Makefile","sha":"32a78cbe8c16c7b0e4ed1c39dc4a5996c7c3b368","url":"https://api.github.com/repos/canonical/hive-metastore-k8s-operator/contents/Makefile?ref=127daa0912331ad2b8567a664d5cf40fe7d102b3","git_url":"https://api.github.com/repos/canonical/hive-metastore-k8s-operator/git/blobs/32a78cbe8c16c7b0e4ed1c39dc4a5996c7c3b368","html_url":"https://github.com/canonical/hive-metastore-k8s-operator/blob/127daa0912331ad2b8567a664d5cf40fe7d102b3/Makefile","download_url":"https://raw.githubusercontent.com/canonical/hive-metastore-k8s-operator/127daa0912331ad2b8567a664d5cf40fe7d102b3/Makefile"},{"type":"file","size":2897,"name":"README.md","path":"README.md","sha":"ba5b14d274445a22ec2fdb9e7b37b883c9572344","url":"https://api.github.com/repos/canonical/hive-metastore-k8s-operator/contents/README.md?ref=127daa0912331ad2b8567a664d5cf40fe7d102b3","git_url":"https://api.github.com/repos/canonical/hive-metastore-k8s-operator/git/blobs/ba5b14d274445a22ec2fdb9e7b37b883c9572344","html_url":"https://github.com/canonical/hive-metastore-k8s-operator/blob/127daa0912331ad2b8567a664d5cf40fe7d102b3/README.md","download_url":"https://raw.githubusercontent.com/canonical/hive-metastore-k8s-operator/127daa0912331ad2b8567a664d5cf40fe7d102b3/README.md"},{"type":"file","size":3731,"name":"charmcraft.yaml","path":"charmcraft.yaml","sha":"3913d3ef44fc52ad223b5f4130e8cd6bb3fbd9b2","url":"https://api.github.com/repos/canonical/hive-metastore-k8s-operator/contents/charmcraft.yaml?ref=127daa0912331ad2b8567a664d5cf40fe7d102b3","git_url":"https://api.github.com/repos/canonical/hive-metastore-k8s-operator/git/blobs/3913d3ef44fc52ad223b5f4130e8cd6bb3fbd9b2","html_url":"https://github.com/canonical/hive-metastore-k8s-operator/blob/127daa0912331ad2b8567a664d5cf40fe7d102b3/charmcraft.yaml","download_url":"https://raw.githubusercontent.com/canonical/hive-metastore-k8s-operator/127daa0912331ad2b8567a664d5cf40fe7d102b3/charmcraft.yaml"},{"type":"dir","size":0,"name":"hive_metastore_rock","path":"hive_metastore_rock","sha":"ffb9911cd30983cf7b07139d1c8acb760b267671","url":"https://api.github.com/repos/canonical/hive-metastore-k8s-operator/contents/hive_metastore_rock?ref=127daa0912331ad2b8567a664d5cf40fe7d102b3","git_url":"https://api.github.com/repos/canonical/hive-metastore-k8s-operator/git/trees/ffb9911cd30983cf7b07139d1c8acb760b267671","html_url":"https://github.com/canonical/hive-metastore-k8s-operator/tree/127daa0912331ad2b8567a664d5cf40fe7d102b3/hive_metastore_rock"},{"type":"dir","size":0,"name":"lib","path":"lib","sha":"e900ae517043eb41f867502e088de7d0b746184b","url":"https://api.github.com/repos/canonical/hive-metastore-k8s-operator/contents/lib?ref=127daa0912331ad2b8567a664d5cf40fe7d102b3","git_url":"https://api.github.com/repos/canonical/hive-metastore-k8s-operator/git/trees/e900ae517043eb41f867502e088de7d0b746184b","html_url":"https://github.com/canonical/hive-metastore-k8s-operator/tree/127daa0912331ad2b8567a664d5cf40fe7d102b3/lib"},{"type":"file","size":1628,"name":"pyproject.toml","path":"pyproject.toml","sha":"fcf1afa654c3c892f4f3289db94ec85e281bc887","url":"https://api.github.com/repos/canonical/hive-metastore-k8s-operator/contents/pyproject.toml?ref=127daa0912331ad2b8567a664d5cf40fe7d102b3","git_url":"https://api.github.com/repos/canonical/hive-metastore-k8s-operator/git/blobs/fcf1afa654c3c892f4f3289db94ec85e281bc887","html_url":"https://github.com/canonical/hive-metastore-k8s-operator/blob/127daa0912331ad2b8567a664d5cf40fe7d102b3/pyproject.toml","download_url":"https://raw.githubusercontent.com/canonical/hive-metastore-k8s-operator/127daa0912331ad2b8567a664d5cf40fe7d102b3/pyproject.toml"},{"type":"dir","size":0,"name":"scripts","path":"scripts","sha":"bd003c0810ee36f731a3610cb9e6ae43183df308","url":"https://api.github.com/repos/canonical/hive-metastore-k8s-operator/contents/scripts?ref=127daa0912331ad2b8567a664d5cf40fe7d102b3","git_url":"https://api.github.com/repos/canonical/hive-metastore-k8s-operator/git/trees/bd003c0810ee36f731a3610cb9e6ae43183df308","html_url":"https://github.com/canonical/hive-metastore-k8s-operator/tree/127daa0912331ad2b8567a664d5cf40fe7d102b3/scripts"},{"type":"dir","size":0,"name":"src","path":"src","sha":"af9244c21a40df00c288bbbbc3116af896ee88ef","url":"https://api.github.com/repos/canonical/hive-metastore-k8s-operator/contents/src?ref=127daa0912331ad2b8567a664d5cf40fe7d102b3","git_url":"https://api.github.com/repos/canonical/hive-metastore-k8s-operator/git/trees/af9244c21a40df00c288bbbbc3116af896ee88ef","html_url":"https://github.com/canonical/hive-metastore-k8s-operator/tree/127daa0912331ad2b8567a664d5cf40fe7d102b3/src"},{"type":"dir","size":0,"name":"templates","path":"templates","sha":"1276378380a9399f9bb585c2d90456f625a5b729","url":"https://api.github.com/repos/canonical/hive-metastore-k8s-operator/contents/templates?ref=127daa0912331ad2b8567a664d5cf40fe7d102b3","git_url":"https://api.github.com/repos/canonical/hive-metastore-k8s-operator/git/trees/1276378380a9399f9bb585c2d90456f625a5b729","html_url":"https://github.com/canonical/hive-metastore-k8s-operator/tree/127daa0912331ad2b8567a664d5cf40fe7d102b3/templates"},{"type":"dir","size":0,"name":"tests","path":"tests","sha":"7b57019cb51bc95f99625f0fa0c071ba8a70463e","url":"https://api.github.com/repos/canonical/hive-metastore-k8s-operator/contents/tests?ref=127daa0912331ad2b8567a664d5cf40fe7d102b3","git_url":"https://api.github.com/repos/canonical/hive-metastore-k8s-operator/git/trees/7b57019cb51bc95f99625f0fa0c071ba8a70463e","html_url":"https://github.com/canonical/hive-metastore-k8s-operator/tree/127daa0912331ad2b8567a664d5cf40fe7d102b3/tests"},{"type":"file","size":2144,"name":"tox.ini","path":"tox.ini","sha":"00e9a3dc4f7cd5df70eae2f57667697e00d5e554","url":"https://api.github.com/repos/canonical/hive-metastore-k8s-operator/contents/tox.ini?ref=127daa0912331ad2b8567a664d5cf40fe7d102b3","git_url":"https://api.github.com/repos/canonical/hive-metastore-k8s-operator/git/blobs/00e9a3dc4f7cd5df70eae2f57667697e00d5e554","html_url":"https://github.com/canonical/hive-metastore-k8s-operator/blob/127daa0912331ad2b8567a664d5cf40fe7d102b3/tox.ini","download_url":"https://raw.githubusercontent.com/canonical/hive-metastore-k8s-operator/127daa0912331ad2b8567a664d5cf40fe7d102b3/tox.ini"},{"type":"file","size":204421,"name":"uv.lock","path":"uv.lock","sha":"a559959909002a234232757da3093b431235b67b","url":"https://api.github.com/repos/canonical/hive-metastore-k8s-operator/contents/uv.lock?ref=127daa0912331ad2b8567a664d5cf40fe7d102b3","git_url":"https://api.github.com/repos/canonical/hive-metastore-k8s-operator/git/blobs/a559959909002a234232757da3093b431235b67b","html_url":"https://github.com/canonical/hive-metastore-k8s-operator/blob/127daa0912331ad2b8567a664d5cf40fe7d102b3/uv.lock","download_url":"https://raw.githubusercontent.com/canonical/hive-metastore-k8s-operator/127daa0912331ad2b8567a664d5cf40fe7d102b3/uv.lock"}]
```


---

<sub>⏱️ 17s</sub>

### ✅ `github-mcp-server-get_file_contents`

**src**

<details>
<summary>Arguments</summary>

```json
{
  "owner": "canonical",
  "path": "src",
  "repo": "hive-metastore-k8s-operator"
}
```

</details>

```
[{"type":"file","size":8367,"name":"charm.py","path":"src/charm.py","sha":"b933306dcd760293e1610b7aabf87fe7dba4237c","url":"https://api.github.com/repos/canonical/hive-metastore-k8s-operator/contents/src/charm.py?ref=127daa0912331ad2b8567a664d5cf40fe7d102b3","git_url":"https://api.github.com/repos/canonical/hive-metastore-k8s-operator/git/blobs/b933306dcd760293e1610b7aabf87fe7dba4237c","html_url":"https://github.com/canonical/hive-metastore-k8s-operator/blob/127daa0912331ad2b8567a664d5cf40fe7d102b3/src/charm.py","download_url":"https://raw.githubusercontent.com/canonical/hive-metastore-k8s-operator/127daa0912331ad2b8567a664d5cf40fe7d102b3/src/charm.py"},{"type":"file","size":5400,"name":"config.py","path":"src/config.py","sha":"833c2326e2cfb2d0b9663e820fe01174eef6e7cc","url":"https://api.github.com/repos/canonical/hive-metastore-k8s-operator/contents/src/config.py?ref=127daa0912331ad2b8567a664d5cf40fe7d102b3","git_url":"https://api.github.com/repos/canonical/hive-metastore-k8s-operator/git/blobs/833c2326e2cfb2d0b9663e820fe01174eef6e7cc","html_url":"https://github.com/canonical/hive-metastore-k8s-operator/blob/127daa0912331ad2b8567a664d5cf40fe7d102b3/src/config.py","download_url":"https://raw.githubusercontent.com/canonical/hive-metastore-k8s-operator/127daa0912331ad2b8567a664d5cf40fe7d102b3/src/config.py"},{"type":"file","size":528,"name":"constants.py","path":"src/constants.py","sha":"78bf66ec01414d9becc396fc7e99c2b9fbc64d66","url":"https://api.github.com/repos/canonical/hive-metastore-k8s-operator/contents/src/constants.py?ref=127daa0912331ad2b8567a664d5cf40fe7d102b3","git_url":"https://api.github.com/repos/canonical/hive-metastore-k8s-operator/git/blobs/78bf66ec01414d9becc396fc7e99c2b9fbc64d66","html_url":"https://github.com/canonical/hive-metastore-k8s-operator/blob/127daa0912331ad2b8567a664d5cf40fe7d102b3/src/constants.py","download_url":"https://raw.githubusercontent.com/canonical/hive-metastore-k8s-operator/127daa0912331ad2b8567a664d5cf40fe7d102b3/src/constants.py"},{"type":"file","size":6509,"name":"hive_metastore.py","path":"src/hive_metastore.py","sha":"ddae7c90d786f2d07983bf2982ea8c9bfe14e7b1","url":"https://api.github.com/repos/canonical/hive-metastore-k8s-operator/contents/src/hive_metastore.py?ref=127daa0912331ad2b8567a664d5cf40fe7d102b3","git_url":"https://api.github.com/repos/canonical/hive-metastore-k8s-operator/git/blobs/ddae7c90d786f2d07983bf2982ea8c9bfe14e7b1","html_url":"https://github.com/canonical/hive-metastore-k8s-operator/blob/127daa0912331ad2b8567a664d5cf40fe7d102b3/src/hive_metastore.py","download_url":"https://raw.githubusercontent.com/canonical/hive-metastore-k8s-operator/127daa0912331ad2b8567a664d5cf40fe7d102b3/src/hive_metastore.py"},{"type":"file","size":2334,"name":"schematool.py","path":"src/schematool.py","sha":"fb8784bf1ff755a71886e52eb0e238be6245cf96","url":"https://api.github.com/repos/canonical/hive-metastore-k8s-operator/contents/src/schematool.py?ref=127daa0912331ad2b8567a664d5cf40fe7d102b3","git_url":"https://api.github.com/repos/canonical/hive-metastore-k8s-operator/git/blobs/fb8784bf1ff755a71886e52eb0e238be6245cf96","html_url":"https://github.com/canonical/hive-metastore-k8s-operator/blob/127daa0912331ad2b8567a664d5cf40fe7d102b3/src/schematool.py","download_url":"https://raw.githubusercontent.com/canonical/hive-metastore-k8s-operator/127daa0912331ad2b8567a664d5cf40fe7d102b3/src/schematool.py"}]
```


---

<sub>⏱️ 16s</sub>

### ✅ `view`

**/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__relation-data-classes__C3/src**

/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__relation-data-classes__C3/src

<details>
<summary>6 lines</summary>

```
alertmanager.py
alertmanager_client.py
charm.py
config_builder.py
grafana_dashboards
prometheus_alert_rules
```

</details>


---

<sub>⏱️ 22s</sub>

### ✅ `github-mcp-server-get_file_contents`

**src/charm.py**

<details>
<summary>Arguments</summary>

```json
{
  "owner": "canonical",
  "path": "src/charm.py",
  "repo": "hive-metastore-k8s-operator"
}
```

</details>

<details>
<summary>183 lines</summary>

```
successfully downloaded text file (SHA: b933306dcd760293e1610b7aabf87fe7dba4237c)#!/usr/bin/env python3
# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

"""Hive Metastore Kubernetes charm."""

import logging
from typing import Optional

import ops
import yaml
from charms.data_platform_libs.v0.data_interfaces import (
    DatabaseCreatedEvent,
    DatabaseEndpointsChangedEvent,
    DatabaseRequires,
)
from charms.data_platform_libs.v0.data_models import TypedCharmBase
from ops.model import ActiveStatus, BlockedStatus, MaintenanceStatus, WaitingStatus
from ops.pebble import APIError, ChangeError, ConnectionError, PathError

import constants
import hive_metastore
import schematool
from config import CharmConfig

logger = logging.getLogger(__name__)


class HiveMetastoreK8SOperatorCharm(TypedCharmBase[CharmConfig]):
    """Operator to configure and run the Hive Metastore workload."""

    config_type = CharmConfig

    def __init__(self, framework: ops.Framework):
        super().__init__(framework)

        self.postgresql = DatabaseRequires(
            self,
            relation_name="postgresql",
            database_name=constants.DEFAULT_DATABASE_NAME,
        )

        framework.observe(self.on[constants.CONTAINER_NAME].pebble_ready, self._on_pebble_ready)
        framework.observe(self.on.config_changed, self._on_config_changed)
        framework.observe(self.on.update_status, self._on_update_status)

        framework.observe(self.postgresql.on.database_created, self._on_database_event)
        framework.observe(self.postgresql.on.endpoints_changed, self._on_database_event)

        framework.observe(self.on.postgresql_relation_broken, self._on_postgresql_broken)

    # Event handlers -----------------------------------------------------------------

    def _on_pebble_ready(self, event: ops.PebbleReadyEvent) -> None:
        container = self._get_container()
        if not (container and container.can_connect()):
            event.defer()
            return
        try:
            meta_file = container.pull("/rockcraft.yaml")
            meta = yaml.safe_load(meta_file)
            if meta and "version" in meta:
                self.unit.set_workload_version(meta["version"])
            else:
                raise ValueError("Cannot find 'version' in 'rockcraft.yaml'.")
        except (PathError, ValueError, yaml.YAMLError) as e:
            logger.debug("Could not get workload version: %s", str(e))
        self._reconcile()

    def _on_config_changed(self, _: ops.ConfigChangedEvent) -> None:
        self.unit.open_port("tcp", constants.HIVE_PORT)
        self._reconcile()

    def _on_update_status(self, _: ops.UpdateStatusEvent) -> None:
        self._reconcile()

    def _on_database_event(
        self,
        event: ops.EventBase,
    ) -> None:
        if not isinstance(event, (DatabaseCreatedEvent, DatabaseEndpointsChangedEvent)):
            logger.debug("Ignoring unexpected database event: %s", type(event).__name__)
            return

        self._reconcile()

    def _on_postgresql_broken(self, _: ops.RelationBrokenEvent) -> None:
        self._reconcile()

    # Reconciliation -----------------------------------------------------------------

    def _reconcile(self) -> None:
        # TODO (mertalpt): Check if it would be better to update
        # the pebble plan rather than stopping the service.
        container = self._get_container()
        if container is None or not container.can_connect():
            self.unit.status = WaitingStatus("waiting for container startup")
            return

        # Check if Postgres relation is there.
        if (raw_pg_relation := self.model.get_relation(constants.POSTGRES_RELATION)) is None:
            self._stop_service(container)
            self.unit.status = BlockedStatus("waiting for postgresql relation")
            return

        pg_relation = raw_pg_relation.load(
            hive_metastore.PostgresRelationModel,
            raw_pg_relation.app,
            decoder=hive_metastore.PostgresRelationModel.decode(self),
        )

        # Check if a configuration update is needed.
        try:
            do_restart = hive_metastore.manage_configuration_files(container, pg_relation)
        except ConnectionError:
            self.unit.status = WaitingStatus("waiting for container filesystem")
            return

        env = self._service_environment()
        res = schematool.info(container, env)

        do_init = False
        if not res.success:
            err_text = res.stderr or ""
            # TODO (mertalpt): This needs to be handled better after we get
            # some experience with the charm.
            if "Failed to get schema version" not in err_text:
                logger.error("Failed to fetch schema version: %s", err_text)
                self._stop_service(container)
                self.unit.status = BlockedStatus(
                    "schematool (info) is broken; run 'juju debug-log' for details"
                )
                return
            # This means schema needs to be initialized.
            do_init, do_restart = True, True

        if do_restart:
            self.unit.status = MaintenanceStatus("restarting metastore service")
            self._stop_service(container)
        if do_init:
            self.unit.status = MaintenanceStatus("initializing metastore schema")
            try:
                res = schematool.initialize(container, env)
            except schematool.SchemaInitializationError as e:
                logger.error("Failed to initialize metastore schema: %s", str(e))
                self.unit.status = BlockedStatus(
                    "schematool (initSchema) is broken; run 'juju debug-log' for details"
                )
                return

        try:
            self._apply_pebble_layer(container)
        except ConnectionError:
            self.unit.status = WaitingStatus("waiting for pebble service")
            return

        container.replan()
        self.unit.status = ActiveStatus()

    # Helpers ------------------------------------------------------------------------

    def _get_container(self) -> Optional[ops.Container]:
        try:
            return self.unit.get_container(constants.CONTAINER_NAME)
        except ops.model.ModelError:
            return None

    def _apply_pebble_layer(self, container: ops.Container) -> None:
        desired_layer = self._pebble_layer()
        container.add_layer(constants.SERVICE_NAME, desired_layer, combine=True)

    def _pebble_layer(self) -> ops.pebble.LayerDict:
        environment = self._service_environment()
        return {
            "summary": "Hive Metastore service",
            "description": "Pebble layer configuring the Hive Metastore process",
            "services": {
                constants.SERVICE_NAME: {
                    "override": "replace",
                    "summary": "Hive Metastore",
                    "command": "/opt/hive/bin/start-metastore",
                    "startup": "enabled",
                    "environment": environment,
                }
            },
        }

    def _service_environment(self) -> dict[str, str]:
        return {
            "HIVE_HOME": "/opt/hive",
            "HADOOP_HOME": "/opt/hadoop",
            "JAVA_HOME": "/usr/lib/jvm/java-21-openjdk-amd64",
            "HIVE_CONF_DIR": constants.HIVE_CONF_DIR,
            "HADOOP_CONF_DIR": constants.HIVE_CONF_DIR,
            "PATH": "/opt/hadoop/bin:/opt/hive/bin:/usr/bin:/bin",
        }

    def _stop_service(self, container: ops.Container) -> None:
        """Stop the Hive Metastore service in the given container.

        Args:
            container: Container in which the service will be stopped.
        """
        # Documentation is unclear on failure scenarios
        # but I think it is OK to ask for forgiveness
        # rather than permission here.
        try:
            container.stop(constants.SERVICE_NAME)
        except APIError as e:
            if (
                e.message
                == f"cannot stop services: service {constants.SERVICE_NAME} does not exist"
            ):
                pass
            else:
                raise
        except (ConnectionError, ChangeError) as e:
            logger.debug("Failed to stop service: %s", e)


if __name__ == "__main__":  # pragma: nocover
    ops.main(HiveMetastoreK8SOperatorCharm)
```

</details>


---

<sub>⏱️ 21s</sub>

### ✅ `view`

**/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__relation-data-classes__C3/src/charm.py**

/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__relation-data-classes__C3/src/charm.py

<details>
<summary>671 lines</summary>

```
1. #!/usr/bin/env python3
2. # Copyright 2021 Canonical Ltd.
3. # See LICENSE file for licensing details.
4. 
5. """A Juju charm for alertmanager."""
6. 
7. import logging
8. import socket
9. import subprocess
10. from dataclasses import dataclass
11. from pathlib import Path
12. from types import SimpleNamespace
13. from typing import List, Optional, Tuple, cast
14. from urllib.parse import urlparse
15. 
16. import yaml
17. from charms.alertmanager_k8s.v0.alertmanager_remote_configuration import (
18.     RemoteConfigurationRequirer,
19. )
20. from charms.alertmanager_k8s.v1.alertmanager_dispatch import AlertmanagerProvider
21. from charms.catalogue_k8s.v1.catalogue import CatalogueConsumer, CatalogueItem
22. from charms.grafana_k8s.v0.grafana_dashboard import GrafanaDashboardProvider
23. from charms.grafana_k8s.v0.grafana_source import GrafanaSourceProvider
24. from charms.istio_beacon_k8s.v0.service_mesh import ServiceMeshConsumer, UnitPolicy
25. from charms.karma_k8s.v0.karma_dashboard import KarmaProvider
26. from charms.observability_libs.v0.kubernetes_compute_resources_patch import (
27.     K8sResourcePatchFailedEvent,
28.     KubernetesComputeResourcesPatch,
29.     ResourceRequirements,
30.     adjust_resource_requirements,
31. )
32. from charms.prometheus_k8s.v0.prometheus_scrape import MetricsEndpointProvider
33. from charms.tempo_coordinator_k8s.v0.charm_tracing import trace_charm
34. from charms.tempo_coordinator_k8s.v0.tracing import TracingEndpointRequirer, charm_tracing_config
35. from charms.tls_certificates_interface.v4.tls_certificates import (
36.     CertificateRequestAttributes,
37.     TLSCertificatesRequiresV4,
38. )
39. from charms.traefik_k8s.v2.ingress import IngressPerAppRequirer
40. from ops.charm import ActionEvent, CharmBase
41. from ops.main import main
42. from ops.model import (
43.     ActiveStatus,
44.     BlockedStatus,
45.     MaintenanceStatus,
46.     OpenedPort,
47.     Relation,
48.     WaitingStatus,
49. )
50. from ops.pebble import PathError, ProtocolError  # type: ignore
51. 
52. from alertmanager import (
53.     ConfigFileSystemState,
54.     ConfigUpdateFailure,
55.     WorkloadManager,
56.     WorkloadManagerError,
57. )
58. from config_builder import ConfigBuilder, ConfigError
59. 
60. logger = logging.getLogger(__name__)
61. 
62. 
63. @dataclass
64. class TLSConfig:
65.     """TLS configuration received by the charm over the `certificates` relation."""
66. 
67.     server_cert: str
68.     ca_cert: str
69.     private_key: str
70. 
71. 
72. @trace_charm(
73.     tracing_endpoint="_charm_tracing_endpoint",
74.     server_cert="_charm_tracing_ca_cert",
75.     extra_types=(
76.         AlertmanagerProvider,
77.         TLSCertificatesRequiresV4,
78.         IngressPerAppRequirer,
79.         KubernetesComputeResourcesPatch,
80.         RemoteConfigurationRequirer,
81.     ),
82. )
83. class AlertmanagerCharm(CharmBase):
84.     """A Juju charm for alertmanager."""
85. 
86.     # Container name must match metadata.yaml
87.     # Layer name is used for the layer label argument in container.add_layer
88.     # Service name matches charm name for consistency
89.     _container_name = _service_name = "alertmanager"
90.     _relations = SimpleNamespace(
91.         alerting="alerting", peer="replicas", remote_config="remote_configuration"
92.     )
93.     _ports = SimpleNamespace(api=9093, ha=9094)
94. 
95.     # path, inside the workload container, to the alertmanager and amtool configuration files
96.     # the amalgamated templates file goes in the same folder as the main configuration file
97.     _config_path = "/etc/alertmanager/alertmanager.yml"
98.     _web_config_path = "/etc/alertmanager/alertmanager-web-config.yml"
99.     _amtool_config_path = "/etc/amtool/config.yml"
100.     _templates_path = "/etc/alertmanager/templates.tmpl"
101. 
102.     _server_cert_path = "/etc/alertmanager/alertmanager.cert.pem"
103.     _key_path = "/etc/alertmanager/alertmanager.key.pem"
104.     _ca_cert_path = "/usr/local/share/ca-certificates/cos-ca.crt"
105. 
106.     def __init__(self, *args):
107.         super().__init__(*args)
108.         self.container = self.unit.get_container(self._container_name)
109.         self._fqdn = socket.getfqdn()
110. 
111.         self._csr_attributes = CertificateRequestAttributes(
112.             # the `common_name` field is required but limited to 64 characters.
113.             # since it's overridden by sans, we can use a short,
114.             # constrained value like app name.
115.             common_name=self.app.name,
116.             sans_dns=frozenset((self._fqdn,)),
117.         )
118.         self._cert_requirer = TLSCertificatesRequiresV4(
119.             charm=self,
120.             relationship_name="certificates",
121.             certificate_requests=[self._csr_attributes],
122.         )
123.         self.framework.observe(
124.             self._cert_requirer.on.certificate_available,  # pyright: ignore
125.             self._on_certificate_available,
126.         )
127. 
128.         self.ingress = IngressPerAppRequirer(
129.             self,
130.             port=self.api_port,
131.             scheme=self._scheme,
132.             strip_prefix=True,
133.             redirect_https=True,
134.         )
135.         self.framework.observe(self.ingress.on.ready, self._handle_ingress)  # pyright: ignore
136.         self.framework.observe(self.ingress.on.revoked, self._handle_ingress)  # pyright: ignore
137. 
138.         self.alertmanager_provider = AlertmanagerProvider(
139.             self,
140.             relation_name=self._relations.alerting,
141.             external_url=self._internal_url,  # TODO See 'TODO' below, about external_url
142.         )
143. 
144.         self.grafana_dashboard_provider = GrafanaDashboardProvider(charm=self)
145.         self.grafana_source_provider = GrafanaSourceProvider(
146.             charm=self,
147.             source_type="alertmanager",
148.             source_url=self.ingress.url or self._service_url,
149.             is_ingress_per_app=True, # We want only one alertmanager datasource (unit) to be listed in grafana.
150.             refresh_event=[
151.                 self.ingress.on.ready,
152.                 self.ingress.on.revoked,
153.                 self.on.update_status,
154.                 self._cert_requirer.on.certificate_available,
155.             ],
156.         )
157.         self.karma_provider = KarmaProvider(self, "karma-dashboard")
158.         self.remote_configuration = RemoteConfigurationRequirer(self)
159. 
160.         self.set_ports()
161. 
162.         self.resources_patch = KubernetesComputeResourcesPatch(
163.             self,
164.             self._container_name,
165.             resource_reqs_func=self._resource_reqs_from_config,
166.         )
167.         self.framework.observe(
168.             self.resources_patch.on.patch_failed,
169.             self._on_k8s_patch_failed,  # pyright: ignore
170.         )
171. 
172.         # Self-monitoring
173.         self._scraping = MetricsEndpointProvider(
174.             self,
175.             relation_name="self-metrics-endpoint",
176.             jobs=self.self_scraping_job,
177.             refresh_event=[
178.                 self.on.update_status,
179.                 self.ingress.on.ready,  # pyright: ignore
180.                 self.ingress.on.revoked,  # pyright: ignore
181.                 self.on["ingress"].relation_changed,
182.                 self.on["ingress"].relation_departed,
183.                 self._cert_requirer.on.certificate_available,  # pyright: ignore
184.             ],
185.         )
186.         self._tracing = TracingEndpointRequirer(self, protocols=["otlp_http"])
187.         self._charm_tracing_endpoint, self._charm_tracing_ca_cert = charm_tracing_config(
188.             self._tracing, self._ca_cert_path
189.         )
190. 
191.         self.catalog = CatalogueConsumer(charm=self, item=self._catalogue_item)
192. 
193.         self._mesh = ServiceMeshConsumer(
194.             self,
195.             policies=[
196.                 UnitPolicy(
197.                     relation="alerting",
198.                     ports=[self.api_port],
199.                 ),
200.                 UnitPolicy(
201.                     relation="grafana-source",
202.                     ports=[self.api_port],
203.                 ),
204.                 UnitPolicy(
205.                     relation="self-metrics-endpoint",
206.                     ports=[self.api_port],
207.                 ),
208.             ],
209.         )
210. 
211.         # Core lifecycle events
212.         self.framework.observe(self.on.config_changed, self._on_config_changed)
213.         self.framework.observe(self.on.start, self._on_start)
214. 
215.         peer_ha_netlocs = [
216.             f"{hostname}:{self._ports.ha}"
217.             for hostname in self._get_peer_hostnames(include_this_unit=False)
218.         ]
219. 
220.         self.alertmanager_workload = WorkloadManager(
221.             self,
222.             container_name=self._container_name,
223.             peer_netlocs=peer_ha_netlocs,
224.             api_port=self.api_port,
225.             ha_port=self._ports.ha,
226.             web_external_url=self._external_url,
227.             web_route_prefix="/",
228.             config_path=self._config_path,
229.             web_config_path=self._web_config_path,
230.             tls_enabled=lambda: self._tls_available,
231.             cafile=self._ca_cert_path if Path(self._ca_cert_path).exists() else None,
232.         )
233.         self.framework.observe(
234.             # The workload manager too observes pebble ready, but still need this here because
235.             # of the common exit hook (otherwise would need to pass the common exit hook as
236.             # a callback).
237.             self.on.alertmanager_pebble_ready,  # pyright: ignore
238.             self._on_pebble_ready,
239.         )
240.         self.framework.observe(self.on.update_status, self._on_update_status)
241.         self.framework.observe(self.on.upgrade_charm, self._on_upgrade_charm)
242. 
243.         # Remote configuration events
244.         self.framework.observe(
245.             self.remote_configuration.on.remote_configuration_changed,  # pyright: ignore
246.             self._on_remote_configuration_changed,
247.         )
248. 
249.         # Peer relation events
250.         self.framework.observe(
251.             self.on[self._relations.peer].relation_joined, self._on_peer_relation_joined
252.         )
253.         self.framework.observe(
254.             self.on[self._relations.peer].relation_changed, self._on_peer_relation_changed
255.         )
256. 
257.         # Action events
258.         self.framework.observe(
259.             self.on.show_config_action,
260.             self._on_show_config_action,  # pyright: ignore
261.         )
262.         self.framework.observe(
263.             self.on.check_config_action,
264.             self._on_check_config,  # pyright: ignore
265.         )
266. 
267.     def set_ports(self):
268.         """Open necessary (and close no longer needed) workload ports."""
269.         planned_ports = {
270.             OpenedPort("tcp", self._ports.api),
271.             OpenedPort("tcp", self._ports.ha),
272.         }
273.         actual_ports = self.unit.opened_ports()
274. 
275.         # Ports may change across an upgrade, so need to sync
276.         ports_to_close = actual_ports.difference(planned_ports)
277.         for p in ports_to_close:
278.             self.unit.close_port(p.protocol, p.port)
279. 
280.         new_ports_to_open = planned_ports.difference(actual_ports)
281.         for p in new_ports_to_open:
282.             self.unit.open_port(p.protocol, p.port)
283. 
284.     @property
285.     def _catalogue_item(self) -> CatalogueItem:
286.         api_endpoints = {"Alerts": "/api/v2/alerts"}
287. 
288.         return CatalogueItem(
289.             name="Alertmanager",
290.             icon="bell-alert",
291.             url=self._external_url,
292.             description=(
293.                 "Alertmanager receives alerts from supporting applications, such as "
294.                 "Prometheus or Loki, then deduplicates, groups and routes them to "
295.                 "the configured receiver(s)."
296.             ),
297.             api_docs="https://github.com/prometheus/alertmanager/blob/main/api/v2/openapi.yaml",
298.             api_endpoints={
299.                 key: f"{self._external_url}{path}" for key, path in api_endpoints.items()
300.             },
301.         )
302. 
303.     @property
304.     def self_scraping_job(self):
305.         """The self-monitoring scrape job."""
306.         # We assume that scraping, especially self-monitoring, is in-cluster.
307.         # This assumption is necessary because the local CA signs CSRs with FQDN as the SAN DNS.
308.         # If prometheus were to scrape an ingress URL instead, it would error out with:
309.         # x509: cannot validate certificate.
310.         peer_api_netlocs = [
311.             f"{hostname}:{self._ports.api}"
312.             for hostname in self._get_peer_hostnames(include_this_unit=True)
313.         ]
314. 
315.         config = {
316.             "scheme": self._scheme,
317.             "metrics_path": "/metrics",
318.             "static_configs": [{"targets": peer_api_netlocs}],
319.         }
320. 
321.         return [config]
322. 
323.     def _resource_reqs_from_config(self) -> ResourceRequirements:
324.         limits = {
325.             "cpu": self.model.config.get("cpu"),
326.             "memory": self.model.config.get("memory"),
327.         }
328.         requests = {"cpu": "0.25", "memory": "200Mi"}
329.         return adjust_resource_requirements(limits, requests, adhere_to_requests=True)
330. 
331.     def _on_k8s_patch_failed(self, event: K8sResourcePatchFailedEvent):
332.         self.unit.status = BlockedStatus(str(event.message))
333. 
334.     def _handle_ingress(self, _):
335.         if url := self.ingress.url:
336.             logger.info("Ingress is ready: '%s'.", url)
337.         else:
338.             logger.info("Ingress revoked.")
339.         self._common_exit_hook()
340. 
341.     def _on_check_config(self, event: ActionEvent) -> None:
342.         """Runs `amtool check-config` inside the workload."""
343.         try:
344.             stdout, stderr = self.alertmanager_workload.check_config()
345.         except WorkloadManagerError as e:
346.             return event.fail(str(e))
347. 
348.         if not stdout and stderr:
349.             return event.fail(stderr)
350. 
351.         event.set_results({"result": stdout, "error-message": stderr, "valid": not stderr})
352.         return None
353. 
354.     def _on_show_config_action(self, event: ActionEvent):
355.         """Hook for the show-config action."""
356.         event.log(f"Fetching {self._config_path}")
357.         if not self.alertmanager_workload.is_ready:
358.             event.fail("Container not ready")
359. 
360.         filepaths = self._render_manifest().manifest.keys()
361. 
362.         try:
363.             results = [
364.                 {
365.                     "path": filepath,
366.                     "content": str(self.container.pull(filepath).read()),
367.                 }
368.                 for filepath in filepaths
369.                 if self.container.exists(filepath)
370.             ]
371.             content = self.container.pull(self._config_path)
372.             # juju requires keys to be lowercase alphanumeric (can't use self._config_path)
373.             event.set_results(
374.                 {
375.                     "path": self._config_path,
376.                     "content": str(content.read()),
377.                     # This already includes the above, but keeping both for backwards compat.
378.                     "configs": str(results),
379.                 }
380.             )
381.         except (ProtocolError, PathError) as e:
382.             event.fail(str(e))
383. 
384.     @property
385.     def api_port(self) -> int:
386.         """Get the API port number to use for alertmanager (default: 9093)."""
387.         return self._ports.api
388. 
389.     @property
390.     def peer_relation(self) -> Optional["Relation"]:
391.         """Helper function for obtaining the peer relation object.
392. 
393.         Returns: peer relation object
394.         (NOTE: would return None if called too early, e.g. during install).
395.         """
396.         return self.model.get_relation(self._relations.peer)
397. 
398.     def _get_remote_config(self) -> Optional[Tuple[Optional[dict], Optional[str]]]:
399.         remote_config, remote_templates = self.remote_configuration.config()
400.         if remote_config:
401.             templates = "\n".join(remote_templates) if remote_templates else None
402.             return remote_config, templates
403.         return None
404. 
405.     def _get_local_config(self) -> Optional[Tuple[Optional[dict], Optional[str]]]:
406.         config = self.config["config_file"]
407.         if config:
408.             local_config = yaml.safe_load(cast(str, config))
409. 
410.             # If `juju config` is executed like this `config_file=am.yaml` instead of
411.             # `config_file=@am.yaml` local_config will be the string `am.yaml` instead
412.             # of its content (dict).
413.             if not isinstance(local_config, dict):
414.                 msg = f"Unable to set config from file. Use juju config {self.unit.name} config_file=@FILENAME"
415.                 logger.error(msg)
416.                 raise ConfigUpdateFailure(msg)
417. 
418.             local_templates = cast(str, self.config["templates_file"]) or None
419.             return local_config, local_templates
420.         return None
421. 
422.     def _get_raw_config_and_templates(
423.         self,
424.     ) -> Tuple[Optional[dict], Optional[str]]:
425.         # block if multiple config sources configured
426.         if self._get_remote_config() and self._get_local_config():
427.             logger.error("unable to use config from config_file and relation at the same time")
428.             raise ConfigUpdateFailure("Multiple configs detected")
429.         # if no config provided, use default config with a placeholder receiver
430.         if compound_config := self._get_remote_config():
431.             config, templates = compound_config
432.         elif compound_config := self._get_local_config():
433.             config, templates = compound_config
434.         else:
435.             config = None
436.             templates = None
437. 
438.         return config, templates
439. 
440.     def _render_manifest(self) -> ConfigFileSystemState:
441.         raw_config, raw_templates = self._get_raw_config_and_templates()
442. 
443.         # Note: A free function (with many args) would have the same functionality.
444.         config_suite = (
445.             ConfigBuilder(api_port=self.api_port)
446.             .set_config(raw_config)
447.             .set_tls_server_config(
448.                 cert_file_path=self._server_cert_path, key_file_path=self._key_path
449.             )
450.             .set_templates(raw_templates, self._templates_path)
451.             .build()
452.         )
453.         tls_config = self._tls_config
454. 
455.         return ConfigFileSystemState(
456.             {
457.                 self._config_path: config_suite.alertmanager,
458.                 self._web_config_path: config_suite.web,
459.                 self._templates_path: config_suite.templates,
460.                 self._amtool_config_path: config_suite.amtool,
461.                 self._server_cert_path: tls_config.server_cert if tls_config else None,
462.                 self._key_path: tls_config.private_key if tls_config else None,
463.                 self._ca_cert_path: tls_config.ca_cert if tls_config else None,
464.             }
465.         )
466. 
467.     def _common_exit_hook(self, update_ca_certs: bool = False) -> None:
468.         """Event processing hook that is common to all events to ensure idempotency."""
469.         if not self.resources_patch.is_ready():
470.             if isinstance(self.unit.status, ActiveStatus) or self.unit.status.message == "":
471.                 self.unit.status = WaitingStatus("Waiting for resource limit patch to apply")
472.             return
473. 
474.         if not self.container.can_connect():
475.             self.unit.status = MaintenanceStatus("Waiting for pod startup to complete")
476.             return
477. 
478.         if update_ca_certs:
479.             self._update_ca_certs()
480. 
481.         # Make sure the external url is valid
482.         if external_url := self._external_url:
483.             parsed = urlparse(external_url)
484.             if not (parsed.scheme in ["http", "https"] and parsed.hostname):
485.                 # This shouldn't happen
486.                 logger.error(
487.                     "Invalid external url: '%s'; must include scheme and hostname.",
488.                     external_url,
489.                 )
490.                 self.unit.status = BlockedStatus(
491.                     f"Invalid external url: '{external_url}'; must include scheme and hostname."
492.                 )
493.                 return
494. 
495.         # TODO Conditionally update with the external URL if it's a CMR, or rely on "recv-ca-cert"
496.         #  on the prometheus side.
497.         #  - https://github.com/canonical/operator/issues/970
498.         #  - https://github.com/canonical/prometheus-k8s-operator/issues/530,
499.         self.alertmanager_provider.update(external_url=self._internal_url)
500. 
501.         self.grafana_source_provider.update_source(self._external_url)
502. 
503.         self.ingress.provide_ingress_requirements(scheme=self._scheme, port=self.api_port)
504.         self._scraping.update_scrape_job_spec(self.self_scraping_job)
505. 
506.         if self.peer_relation:
507.             # Could have simply used `socket.getfqdn()` here and add the path when reading this
508.             # relation data, but this way it is more future-proof in case we change from ingress
509.             # per app to ingress per unit.
510.             self.peer_relation.data[self.unit]["private_address"] = self._internal_url
511. 
512.         self.karma_provider.target = self._external_url
513. 
514.         # Update config file
515.         try:
516.             self.alertmanager_workload.update_config(self._render_manifest())
517.         except (ConfigUpdateFailure, ConfigError) as e:
518.             self.unit.status = BlockedStatus(str(e))
519.             return
520. 
521.         # Update pebble layer
522.         self.alertmanager_workload.update_layer()
523. 
524.         # Reload or restart the service
525.         try:
526.             self.alertmanager_workload.reload()
527.         except ConfigUpdateFailure as e:
528.             self.unit.status = BlockedStatus(str(e))
529.             return
530. 
531.         self.catalog.update_item(item=self._catalogue_item)
532. 
533.         self.unit.status = ActiveStatus()
534. 
535.     def _on_certificate_available(self, _):
536.         self._common_exit_hook(update_ca_certs=True)
537. 
538.     def _on_pebble_ready(self, _):
539.         """Event handler for PebbleReadyEvent."""
540.         self._common_exit_hook()
541. 
542.     def _on_config_changed(self, _):
543.         """Event handler for ConfigChangedEvent."""
544.         self._common_exit_hook(update_ca_certs=True)
545. 
546.     def _on_start(self, _):
547.         """Event handler for ConfigChangedEvent."""
548.         self._common_exit_hook(update_ca_certs=True)
549. 
550.     def _on_peer_relation_joined(self, _):
551.         """Event handler for replica's RelationChangedEvent."""
552.         self._common_exit_hook()
553. 
554.     def _on_peer_relation_changed(self, _):
555.         """Event handler for replica's RelationChangedEvent.
556. 
557.         `relation_changed` is needed in addition to `relation_joined` because when a second unit
558.         joins, the first unit must be restarted and provided with the second unit's IP address.
559.         when the first unit sees "joined", it is not guaranteed that the second unit already has
560.         an IP address.
561.         """
562.         self._common_exit_hook()
563. 
564.     def _on_remote_configuration_changed(self, _):
565.         """Event handler for remote configuration's RelationChangedEvent."""
566.         self._common_exit_hook()
567. 
568.     def _on_update_status(self, _):
569.         """Event handler for UpdateStatusEvent.
570. 
571.         Logs list of peers, uptime and version info.
572.         """
573.         try:
574.             status = self.alertmanager_workload.api.status()
575.             logger.info(
576.                 "alertmanager %s is up and running (uptime: %s); cluster mode: %s, with %d peers",
577.                 status["versionInfo"]["version"],
578.                 status["uptime"],
579.                 status["cluster"]["status"],
580.                 len(status["cluster"]["peers"]),
581.             )
582.         except ConnectionError as e:
583.             logger.error("Failed to obtain status: %s", str(e))
584. 
585.         # Calling the common hook to make sure a single unit set its IP in case all events fired
586.         # before an IP address was ready, leaving UpdateStatue as the last resort.
587.         self._common_exit_hook()
588. 
589.     def _on_upgrade_charm(self, _):
590.         """Event handler for replica's UpgradeCharmEvent."""
591.         # After upgrade (refresh), the unit ip address is not guaranteed to remain the same, and
592.         # the config may need update. Calling the common hook to update.
593.         self._common_exit_hook()
594. 
595.     def _update_ca_certs(self):
596.         ca_cert_path = Path(self._ca_cert_path)
597.         if tls_config := self._tls_config:
598.             ca_cert_path.parent.mkdir(exist_ok=True, parents=True)
599.             ca_cert_path.write_text(tls_config.ca_cert)
600.         else:
601.             ca_cert_path.unlink(missing_ok=True)
602. 
603.         # Workload container
604.         self.container.exec(["update-ca-certificates", "--fresh"], timeout=30).wait()
605.         # Charm container
606.         subprocess.run(["update-ca-certificates", "--fresh"], check=True)
607. 
608.     def _get_peer_hostnames(self, include_this_unit=True) -> List[str]:
609.         """Returns a list of the hostnames of the peer units.
610. 
611.         An example of the return format is:
612.           ["alertmanager-1.alertmanager-endpoints.am.svc.cluster.local"]
613.         """
614.         addresses = []
615.         if include_this_unit:
616.             addresses.append(self._internal_url)
617.         if pr := self.peer_relation:
618.             for unit in pr.units:  # pr.units only holds peers (self.unit is not included)
619.                 if address := pr.data[unit].get("private_address"):
620.                     addresses.append(address)
621. 
622.         # Save only the hostname part of the address
623.         # Sort the hostnames in case their order is not guaranteed, to reduce unnecessary updates
624.         hostnames = sorted([urlparse(address).hostname for address in addresses])
625. 
626.         return hostnames
627. 
628.     @property
629.     def _tls_config(self) -> Optional[TLSConfig]:
630.         certificates, key = self._cert_requirer.get_assigned_certificate(
631.             certificate_request=self._csr_attributes
632.         )
633.         if not (key and certificates):
634.             return None
635.         return TLSConfig(certificates.certificate.raw, certificates.ca.raw, key.raw)
636. 
637.     @property
638.     def _tls_available(self) -> bool:
639.         return bool(self._tls_config)
640. 
641.     @property
642.     def _internal_url(self) -> str:
643.         """Return the fqdn dns-based in-cluster (private) address of the alertmanager api server."""
644.         return f"{self._scheme}://{self._fqdn}:{self._ports.api}"
645. 
646.     @property
647.     def _service_url(self) -> str:
648.         """Return the FQDN DNS-based in-cluster (private) address of the service for Alertmanager.
649. 
650.         Since our goal is to ensure that we only send one datasource to Grafana when we have multiple units, we can't use the socket FQDN because that would include the AM unit e.g. `http://am-0.am-endpoints.otel.svc.cluster.local:9093`.
651.         The service URL as defined will remove the pod unit so (when ingress missing) the request goes to the K8s service at: http://am-endpoints.otel.svc.cluster.local:9093
652.         The service will then load balance between the units.
653.         This assumes that the FQDN is the interal FQDN for the socket and that the pod unit is always on the left side of the first ".". If those change, this code will need to be updated.
654.         """
655.         fqdn = self._fqdn.split(".", 1)[-1]
656. 
657.         return f"{self._scheme}://{fqdn}:{self._ports.api}"
658. 
659.     @property
660.     def _external_url(self) -> str:
661.         """Return the externally-reachable (public) address of the alertmanager api server."""
662.         return self.ingress.url or self._internal_url
663. 
664.     @property
665.     def _scheme(self) -> str:
666.         return "https" if self._tls_available else "http"
667. 
668. 
669. if __name__ == "__main__":
670.     main(AlertmanagerCharm)
671.
```

</details>


---

<sub>⏱️ 29s</sub>

### ✅ `github-mcp-server-get_file_contents`

**src/hive_metastore.py**

<details>
<summary>Arguments</summary>

```json
{
  "owner": "canonical",
  "path": "src/hive_metastore.py",
  "repo": "hive-metastore-k8s-operator"
}
```

</details>

<details>
<summary>166 lines</summary>

```
successfully downloaded text file (SHA: ddae7c90d786f2d07983bf2982ea8c9bfe14e7b1)# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

"""Hive Metastore related logic."""

import json
from pathlib import Path
from typing import Callable, Optional

import ops
import pydantic
from jinja2 import Environment, FileSystemLoader

import constants


class PostgresRelationModel(pydantic.BaseModel):
    """Wrapper for PostgreSQL relation to be passed to configuration renderers."""

    database: str
    endpoints: str
    secret_tls: dict[str, str] = pydantic.Field(alias="secret-tls")
    secret_user: dict[str, str] = pydantic.Field(alias="secret-user")

    @property
    def host(self) -> str:
        """Host for the database primary.

        Returns:
            Host value for the database primary.
        """
        val = self.endpoints.split(",")[0]
        host, _ = val.split(":", 1)
        return host

    @property
    def port(self) -> str:
        """Port for the database primary.

        Returns:
            Port value for the database primary.
        """
        val = self.endpoints.split(",")[0]
        _, port = val.split(":", 1)
        return port

    @property
    def username(self) -> str:
        """Username for the database server.

        Returns:
            Username of the relation user.
        """
        return self.secret_user["username"]

    @property
    def password(self) -> str:
        """Password for the database server.

        Returns:
            Password of the relation user.
        """
        return self.secret_user["password"]

    @property
    def tls(self) -> bool:
        """Whether the database server implements TLS.

        Returns:
            True if the database server implements TLS, false otherwise.
        """
        return self.secret_tls["tls"].lower() == "true"

    @property
    def tls_ca(self) -> Optional[str]:
        """Certificate of the certificate authority used for TLS.

        Returns:
            If exists, the CA certificate used for the TLS certificate.
        """
        return self.secret_tls.get("tls-ca")

    @classmethod
    def decode(cls, charm: ops.CharmBase) -> Callable[[str], str | dict[str, str]]:
        """Generate a decoder for Postgres databag that normalizes JSON and fetches secrets.

        Args:
            charm: Charm object that consumes Postgres.

        Returns:
            A function that decodes the Postgres databag key-value pairs.
        """

        def wrapped(v: str) -> str | dict[str, str]:
            """Decode contents of the Postgres databag.

            Args:
                v: Raw value from Postgres databag.

            Returns:
                Decoded string.
            """
            try:
                ret = json.loads(v)
            except json.JSONDecodeError:
                ret = v

            if not v.startswith("secret:"):
                return ret

            secret = charm.model.get_secret(id=v)
            content = secret.get_content(refresh=True)
            return content

        return wrapped


def manage_configuration_files(
    container: ops.Container, pg_relation: PostgresRelationModel
) -> bool:
    """Render and organize configuration files in the container filesystem.

    Args:
        container: Container in which files will be managed.
        pg_relation: Object to use for Postgres credentials.

    Returns:
        True if there has been a change in files, false otherwise.
    """
    has_changed = False

    try:
        curr_file = container.pull(constants.HIVE_SITE_PATH)
        curr_contents = "\n".join(curr_file.readlines())
    except ops.pebble.PathError:
        curr_contents = ""

    new_contents = _render_hive_site(pg_relation)
    if curr_contents != new_contents:
        container.push(constants.HIVE_SITE_PATH, new_contents, make_dirs=True, permissions=0o640)
        has_changed = True

    if pg_relation.tls and pg_relation.tls_ca:
        ca_content = _normalize_ca(pg_relation.tls_ca)
        container.push(constants.POSTGRES_CA_PATH, ca_content, make_dirs=True, permissions=0o600)
        has_changed = True
    else:
        try:
            container.remove_path(constants.POSTGRES_CA_PATH)
            # Even though removing a file is a change
            # this does not warrant a restart, so we do not set the flag.
        except ops.pebble.PathError:
            pass

    return has_changed


def _render_hive_site(pg_relation: PostgresRelationModel) -> str:
    """Render `hive-site.xml` configuration file using a Jinja template.

    Args:
        pg_relation: Wrapper for Postgres relation data.
    """
    properties = {
        "javax.jdo.option.ConnectionURL": _build_jdbc_url(pg_relation),
        "javax.jdo.option.ConnectionDriverName": "org.postgresql.Driver",
        "javax.jdo.option.ConnectionUserName": str(pg_relation.username),
        "javax.jdo.option.ConnectionPassword": str(pg_relation.password),
        "datanucleus.schema.autoCreateAll": "false",
        "datanucleus.autoCreateSchema": "false",
        "datanucleus.fixedDatastore": "true",
        "hive.metastore.schema.verification": "false",
        "hive.metastore.uris": f"thrift://0.0.0.0:{constants.HIVE_PORT}",
    }

    template_path = Path(__file__).parent.parent / "templates"
    template_env = Environment(loader=FileSystemLoader(template_path))
    template = template_env.get_template(constants.HIVE_SITE_TEMPLATE)
    rendered = template.render(properties=properties)
    # Ensure trailing newline for compatibility
    return rendered.rstrip() + "\n"


def _build_jdbc_url(pg_relation: PostgresRelationModel) -> str:
    """Build a JDBC URL from Postgres credentials.

    Args:
        pg_relation: Wrapper for Postgres relation data.

    Returns:
        A JDBC URL to connect to a Postgres database.
    """
    base = f"jdbc:postgresql://{pg_relation.host}:{pg_relation.port}/{pg_relation.database}"

    if not pg_relation.tls:
        return base

    params = ["sslmode=require"]
    if pg_relation.tls_ca:
        params[0] = "sslmode=verify-ca"
        params.append(f"sslrootcert={constants.POSTGRES_CA_PATH}")

    return f"{base}?{'&'.join(params)}"


# TODO (mertalpt): This is currently a no-op but we will probably need it.
def _normalize_ca(text: str) -> str:
    """Normalize a CA certificate in PEM format.

    Currently does nothing.

    Args:
        text: A CA certificate in PEM format.

    Returns:
        A CA certificate in PEM format that is formatted for Hive Metastore.
    """
    return text
```

</details>


---

<sub>⏱️ 28s</sub>

### ✅ `view`

**/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__relation-data-classes__C3/src/alertmanager.py**

/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__relation-data-classes__C3/src/alertmanager.py

<details>
<summary>338 lines</summary>

```
1. #!/usr/bin/env python3
2. # Copyright 2023 Canonical Ltd.
3. # See LICENSE file for licensing details.
4. 
5. """Workload manager for alertmanaqger."""
6. 
7. import logging
8. import os
9. import re
10. from typing import Callable, Dict, List, Optional, Tuple
11. 
12. from ops.framework import Object
13. from ops.model import Container
14. from ops.pebble import (  # type: ignore
15.     ChangeError,
16.     ExecError,
17.     Layer,
18. )
19. 
20. from alertmanager_client import Alertmanager, AlertmanagerBadResponse
21. 
22. logger = logging.getLogger(__name__)
23. 
24. 
25. class ConfigFileSystemState:
26.     """Class representing the configuration state in a filesystem."""
27. 
28.     def __init__(self, manifest: Optional[Dict[str, Optional[str]]] = None):
29.         self._manifest = manifest.copy() if manifest else {}
30. 
31.     @property
32.     def manifest(self) -> Dict[str, Optional[str]]:
33.         """Return a copy of the planned manifest."""
34.         return self._manifest.copy()
35. 
36.     def add_file(self, path: str, content: str):
37.         """Add a file to the configuration."""
38.         # `None` means it needs to be removed (if present). If paths changed across an upgrade,
39.         # to prevent stale files from remaining (if were previously written to persistent
40.         # storage), hard-code the old paths to None to guarantee their removal.
41.         self._manifest[path] = content
42. 
43.     def delete_file(self, path: str):
44.         """Add a file to the configuration."""
45.         self._manifest[path] = None
46. 
47.     def apply(self, container: Container):
48.         """Apply this manifest onto a container."""
49.         for filepath, content in self._manifest.items():
50.             if content is None:
51.                 container.remove_path(filepath, recursive=True)
52.             else:
53.                 container.push(filepath, content, make_dirs=True)
54. 
55. 
56. class WorkloadManagerError(Exception):
57.     """Base class for exceptions raised by WorkloadManager."""
58. 
59. 
60. class ConfigUpdateFailure(WorkloadManagerError):
61.     """Custom exception for failed config updates."""
62. 
63. 
64. class ContainerNotReady(WorkloadManagerError):
65.     """Raised when an operation is run that presumes the container being ready.."""
66. 
67. 
68. class WorkloadManager(Object):
69.     """Workload manager for alertmanager."""
70. 
71.     _layer_name = _service_name = _exe_name = "alertmanager"
72. 
73.     # path, inside the workload container for alertmanager data, e.g. 'nflogs', 'silences'.
74.     _storage_path = "/alertmanager"
75. 
76.     _amtool_path = "/usr/bin/amtool"
77. 
78.     def __init__(
79.         self,
80.         charm,
81.         *,
82.         container_name: str,
83.         peer_netlocs: List[str],
84.         api_port: int,
85.         ha_port: int,
86.         web_external_url: str,
87.         web_route_prefix: str,
88.         config_path: str,
89.         web_config_path: str,
90.         tls_enabled: Callable[[], bool],
91.         cafile: Optional[str],
92.     ):
93.         # Must inherit from ops 'Object' to be able to register events.
94.         super().__init__(charm, f"{self.__class__.__name__}-{container_name}")
95. 
96.         self._unit = charm.unit
97. 
98.         self._service_name = self._container_name = container_name
99.         self._container = charm.unit.get_container(container_name)
100. 
101.         self._peer_netlocs = peer_netlocs
102. 
103.         self._api_port = api_port
104.         self._ha_port = ha_port
105.         self.api = Alertmanager(endpoint_url=web_external_url, cafile=cafile)
106.         self._web_external_url = web_external_url
107.         self._web_route_prefix = web_route_prefix
108.         self._config_path = config_path
109.         self._web_config_path = web_config_path
110.         self._is_tls_enabled = tls_enabled
111. 
112.         # turn the container name to a valid Python identifier
113.         snake_case_container_name = self._container_name.replace("-", "_")
114.         charm.framework.observe(
115.             charm.on[snake_case_container_name].pebble_ready,
116.             self._on_pebble_ready,
117.         )
118.         charm.framework.observe(charm.on.stop, self._on_stop)
119. 
120.     @property
121.     def is_ready(self):
122.         """Is the workload ready to be interacted with?"""
123.         return self._container.can_connect()
124. 
125.     def _on_pebble_ready(self, _):
126.         if version := self._alertmanager_version:
127.             self._unit.set_workload_version(version)
128.         else:
129.             logger.debug(
130.                 "Cannot set workload version at this time: could not get Alertmanager version."
131.             )
132. 
133.     def _on_stop(self, _):
134.         self._unit.set_workload_version("")
135. 
136.     @property
137.     def _alertmanager_version(self) -> Optional[str]:
138.         """Returns the version of Alertmanager.
139. 
140.         Returns:
141.             A string equal to the Alertmanager version.
142.         """
143.         if not self.is_ready:
144.             return None
145.         version_output, _ = self._container.exec(
146.             [self._exe_name, "--version"], timeout=30
147.         ).wait_output()
148.         # Output looks like this:
149.         # alertmanager, version 0.23.0 (branch: HEAD, ...
150.         result = re.search(r"version (\d*\.\d*\.\d*)", version_output)
151.         if result is None:
152.             return result
153.         return result.group(1)
154. 
155.     def check_config(self) -> Tuple[str, str]:
156.         """Check config with amtool.
157. 
158.         Returns stdout, stderr.
159.         """
160.         if not self.is_ready:
161.             raise ContainerNotReady(
162.                 "cannot check config: alertmanager workload container not ready"
163.             )
164.         proc = self._container.exec(
165.             [self._amtool_path, "check-config", self._config_path], timeout=30
166.         )
167.         try:
168.             output, err = proc.wait_output()
169.         except ExecError as e:
170.             output, err = str(e.stdout), str(e.stderr)
171.         # let ChangeError raise
172.         return output, err
173. 
174.     def _alertmanager_layer(self) -> Layer:
175.         """Returns Pebble configuration layer for alertmanager."""
176. 
177.         def _command():
178.             """Returns full command line to start alertmanager."""
179.             # cluster listen netloc - empty string disables HA mode
180.             listen_netloc_arg = "" if len(self._peer_netlocs) == 0 else f"0.0.0.0:{self._ha_port}"
181. 
182.             # The chosen port in the cluster.listen-address flag is the port that needs to be
183.             # specified in the cluster.peer flag of the other peers.
184.             # Assuming all replicas use the same port.
185.             # Sorting for repeatability in comparing between service layers.
186.             peer_cmd_args = " ".join(
187.                 sorted([f"--cluster.peer={netloc}" for netloc in self._peer_netlocs])
188.             )
189.             web_config_arg = (
190.                 f"--web.config.file={self._web_config_path} " if self._is_tls_enabled() else ""
191.             )
192.             return (
193.                 f"{self._exe_name} "
194.                 f"--config.file={self._config_path} "
195.                 f"--storage.path={self._storage_path} "
196.                 f"--web.listen-address=:{self._api_port} "
197.                 f"--cluster.listen-address={listen_netloc_arg} "
198.                 f"--web.external-url={self._web_external_url} "
199.                 f"--web.route-prefix={self._web_route_prefix} "
200.                 f"{web_config_arg}"
201.                 f"{peer_cmd_args}"
202.             )
203. 
204.         def _environment():
205.             return {
206.                 "https_proxy": os.environ.get("JUJU_CHARM_HTTPS_PROXY", ""),
207.                 "http_proxy": os.environ.get("JUJU_CHARM_HTTP_PROXY", ""),
208.                 "no_proxy": os.environ.get("JUJU_CHARM_NO_PROXY", ""),
209.             }
210. 
211.         return Layer(
212.             {
213.                 "summary": "alertmanager layer",
214.                 "description": "pebble config layer for alertmanager",
215.                 "services": {
216.                     self._service_name: {
217.                         "override": "replace",
218.                         "summary": "alertmanager service",
219.                         "command": _command(),
220.                         "startup": "enabled",
221.                         "environment": _environment(),
222.                     }
223.                 },
224.             }
225.         )
226. 
227.     def update_layer(self) -> None:
228.         """Update service layer to reflect changes in peers (replicas)."""
229.         if not self.is_ready:
230.             raise ContainerNotReady("cannot update layer")
231. 
232.         overlay = self._alertmanager_layer()
233. 
234.         self._container.add_layer(self._layer_name, overlay, combine=True)
235.         try:
236.             # If a config is invalid then alertmanager would exit immediately.
237.             # This would be caught by pebble (default timeout is 30 sec) and a ChangeError
238.             # would be raised.
239.             self._container.replan()
240.         except ChangeError as e:
241.             logger.error(
242.                 "Failed to replan; pebble plan: %s; %s",
243.                 self._container.get_plan().to_dict(),
244.                 str(e),
245.             )
246. 
247.     def update_config(self, manifest: ConfigFileSystemState) -> None:
248.         """Update alertmanager config files to reflect changes in configuration.
249. 
250.         After pushing a new config, a hot-reload is attempted. If hot-reload fails, the service is
251.         restarted.
252. 
253.         Raises:
254.           ConfigUpdateFailure, if failed to update configuration file.
255.         """
256.         if not self.is_ready:
257.             raise ContainerNotReady("cannot update config")
258. 
259.         logger.debug("applying config changes")
260.         manifest.apply(self._container)
261. 
262.         # Validate with amtool and raise if bad
263.         try:
264.             self.check_config()
265.         except WorkloadManagerError as e:
266.             raise ConfigUpdateFailure("Failed to validate config (run check-config action)") from e
267. 
268.     def restart_service(self) -> bool:
269.         """Helper function for restarting the underlying service.
270. 
271.         Returns:
272.             True if restart succeeded; False otherwise.
273.         """
274.         logger.info("Restarting service %s", self._service_name)
275. 
276.         if not self.is_ready:
277.             logger.error("Cannot (re)start service: container is not ready.")
278.             return False
279. 
280.         # Check if service exists, to avoid ModelError from being raised when the service does
281.         # not exist,
282.         if not self._container.get_plan().services.get(self._service_name):
283.             logger.error("Cannot (re)start service: service does not (yet) exist.")
284.             return False
285. 
286.         self._container.restart(self._service_name)
287. 
288.         return True
289. 
290.     def reload(self) -> None:
291.         """Trigger a hot-reload of the configuration (or service restart).
292. 
293.         Raises:
294.             ConfigUpdateFailure, if the reload (or restart) fails.
295.         """
296.         if not self.is_ready:
297.             raise ContainerNotReady("cannot reload")
298. 
299.         # Obtain a "before" snapshot of the config from the server.
300.         # This is different from `config` above because alertmanager adds in a bunch of details
301.         # such as:
302.         #
303.         #   smtp_hello: localhost
304.         #   smtp_require_tls: true
305.         #   pagerduty_url: https://events.pagerduty.com/v2/enqueue
306.         #   opsgenie_api_url: https://api.opsgenie.com/
307.         #   wechat_api_url: https://qyapi.weixin.qq.com/cgi-bin/
308.         #   victorops_api_url: https://alert.victorops.com/integrations/generic/20131114/alert/
309.         #
310.         # The snapshot is needed to determine if reloading took place.
311.         try:
312.             config_from_server_before = self.api.config()
313.         except AlertmanagerBadResponse:
314.             config_from_server_before = None
315. 
316.         # Send an HTTP POST to alertmanager to hot-reload the config.
317.         # This reduces down-time compared to restarting the service.
318.         try:
319.             self.api.reload()
320.         except AlertmanagerBadResponse as e:
321.             logger.warning("config reload via HTTP POST failed: %s", str(e))
322.             # hot-reload failed so attempting a service restart
323.             if not self.restart_service():
324.                 raise ConfigUpdateFailure(
325.                     "Is config valid? hot reload and service restart failed."
326.                 )
327. 
328.         # Obtain an "after" snapshot of the config from the server.
329.         try:
330.             config_from_server_after = self.api.config()
331.         except AlertmanagerBadResponse:
332.             config_from_server_after = None
333. 
334.         if config_from_server_before is None or config_from_server_after is None:
335.             logger.warning("cannot determine if reload succeeded")
336.         elif config_from_server_before == config_from_server_after:
337.             logger.warning("config remained the same after a reload")
338.
```

</details>


---

<sub>⏱️ 42s</sub>

### 💬 Copilot

Let me look at the current ops version and how relation data is accessed in the alertmanager charm:

---

<sub>⏱️ 43s</sub>

### ✅ `bash`

**Check ops version and dependencies**

$ cd /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__relation-data-classes__C3 && cat pyproject.toml && echo "---" && head -50 uv.lock | grep -A3 "name = \"ops\""

<details>
<summary>91 lines</summary>

```
# Copyright 2021 Canonical Ltd.
# See LICENSE file for licensing details.
[project]
name = "alertmanager-k8s"
version = "0.0"
requires-python = "~=3.8"

dependencies = [
  "ops",
  "pyyaml",
  "lightkube>=0.11",  # observability_libs
  "lightkube-models",  # observability_libs
  "jsonschema", # traefik_k8s, tls_certificates
  "cryptography",  # tls_certificates
  "pydantic>=2",  # traefik_k8s.v2.ingress
  "opentelemetry-exporter-otlp-proto-http>=1.21.0",  # tracing
  "tenacity",
  "cosl",
  "charmed-service-mesh-helpers>=0.2.0",
  "lightkube-extensions",
]

[project.optional-dependencies]
dev = [
  # Linting
  "ruff",
  "codespell",
  # Static
  "pyright<1.1.399", # 1.1.399 vendors typeshed that dropped Python 3.8 support
  # Unit
  "pytest",
  "coverage[toml]",
  "deepdiff",
  "hypothesis",
  "validators>=0.21.2",
  "ops[testing]",
  "pytest-interface-tester>0.3",
  # Integration
  "juju<=3.3.0,>=3.0",
  "websockets<14.0",
  "pytest-operator",
  "pytest-httpserver",
  "sh",
]

# Testing tools configuration
[tool.coverage.run]
branch = true

[tool.coverage.report]
show_missing = true

# Formatting tools configuration
[tool.black]
line-length = 99
target-version = ["py38"]

# Linting tools configuration
[tool.ruff]
line-length = 99
extend-exclude = ["__pycache__", "*.egg_info"]

[tool.ruff.lint]
select = ["E", "W", "F", "C", "N", "R", "D", "I001"]
# Ignore E501 because using black creates errors with this
# Ignore D107 Missing docstring in __init__
ignore = ["E501", "D107", "N818", "RET504"]
# D100, D101, D102, D103: Ignore missing docstrings in tests
per-file-ignores = {"tests/*" = ["D100","D101","D102","D103"]}

[tool.ruff.lint.pydocstyle]
convention = "google"

# Static analysis tools configuration
[tool.pyright]
extraPaths = ["src", "lib"]
pythonVersion = "3.8"
pythonPlatform = "All"
exclude = [
  "tests/integration/remote_configuration_tester/**",
]

[tool.pytest.ini_options]
minversion = "6.0"
log_cli_level = "INFO"
asyncio_mode = "auto"
addopts = "--tb=native --verbose --capture=no --log-cli-level=INFO"

[tool.codespell]
skip = ".git,.tox,build,venv*"
ignore-words-list = "assertIn"
---
    { name = "ops" },
    { name = "pydantic", version = "2.10.6", source = { registry = "https://pypi.org/simple" }, marker = "python_full_version < '3.9'" },
    { name = "pydantic", version = "2.11.5", source = { registry = "https://pypi.org/simple" }, marker = "python_full_version >= '3.9'" },
    { name = "pyyaml" },
--
    { name = "ops", extra = ["testing"] },
    { name = "pyright" },
    { name = "pytest" },
    { name = "pytest-httpserver", version = "1.1.1", source = { registry = "https://pypi.org/simple" }, marker = "python_full_version < '3.9'" },
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 43s</sub>

### ✅ `github-mcp-server-get_file_contents`

**src/config.py**

<details>
<summary>Arguments</summary>

```json
{
  "owner": "canonical",
  "path": "src/config.py",
  "repo": "hive-metastore-k8s-operator"
}
```

</details>

<details>
<summary>124 lines</summary>

```
successfully downloaded text file (SHA: 833c2326e2cfb2d0b9663e820fe01174eef6e7cc)# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

# Pydantic validators take class as first value
# which causes a false positive with ruff for N805.
# ruff: noqa: N805

"""Module for a Pydantic model that is used for the charm configuration."""

import re
import shlex
from typing import Any

from charms.data_platform_libs.v0.data_models import BaseConfigModel
from pydantic import validator

# Regexes for parsing Kubernetes style resource values
_K8S_CPU_REGEX = re.compile(r"^\d+(\.\d+)?m?$")
_K8S_MEMORY_REGEX = re.compile(r"^\d+(\.\d+)?(Ki|Mi|Gi|Ti|Pi|Ei|k|M|G|T|P|E)?$")

# Regex for parsing JVM options
_JVM_MEMORY_REGEX = re.compile(r"^-Xm[sx]\d+[kKmMgG]?$")

_JVM_ARGS_TAKING_FLAGS = {"-cp", "-classpath", "-jar", "-agentpath", "-javaagent"}


class CharmConfig(BaseConfigModel):
    """Typed configuration for the charm."""

    additional_jvm_options: list[str]
    hms_min_threads: int
    hms_max_threads: int
    kubernetes_requests: dict[str, str]
    kubernetes_limits: dict[str, str]
    sql_connection_pool_max_size: int

    @validator("additional_jvm_options", pre=True)
    def validate_jvm_options(cls, v: Any) -> list[str]:  # noqa: C901
        """Parse the input into a list of JVM options.

        Expects a string of JVM options as if they are passed to `java`
        in the shell.

        Args:
            v: Value to validate.

        Returns:
            List of strings where each item is a valid JVM option.
        """
        if v is None:
            return []

        # In case validators are chained
        if isinstance(v, list):
            v = " ".join((str(item) for item in v))

        if not isinstance(v, str):
            raise ValueError(f"Unexpected type (must be 'str'): {type(v)}")

        if not v.strip():
            return []
        try:
            tokens = shlex.split(v)
        except ValueError:
            raise ValueError(f"Unbalanced quotes: {v}") from None

        skip_next = False
        for i, opt in enumerate(tokens):
            if skip_next:
                skip_next = False
                continue

            if opt in _JVM_ARGS_TAKING_FLAGS:
                if i + 1 >= len(tokens):
                    raise ValueError(f"Option is missing an argument: {opt}")
                # Assume next token will be valid as it is an argument to this option
                skip_next = True
                continue

            if not opt.startswith("-"):
                raise ValueError(f"Invalid option (must start with '-'): {opt}")

            if opt.startswith(("-Xmx", "-Xms")):
                if not _JVM_MEMORY_REGEX.match(opt):
                    raise ValueError(f"Invalid option (malformed value): {opt}")

            if opt.startswith("-D"):
                if "=" not in opt:
                    continue

                key = opt[2:].split("=")[0]
                if not key:
                    raise ValueError(f"Invalid property (empty key): {opt}")

        return tokens

    @validator("hms_min_threads", "hms_max_threads", "sql_connection_pool_max_size", pre=True)
    def validate_positive_ints(cls, v: Any) -> int:
        """Parse the input into a positive integer.

        Args:
            v: Value to validate.

        Returns:
            A positive integer.
        """
        try:
            if v is None or isinstance(v, float):
                raise ValueError
            v = int(v)
        except ValueError:
            raise ValueError(f"Value must be a valid integer: {v}") from None

        if v <= 0:
            raise ValueError(f"Value must be a positive integer: {v}") from None

        return v

    @validator("kubernetes_requests", "kubernetes_limits", pre=True)
    def validate_kubernetes_resources(cls, v: Any) -> dict[str, str]:  # noqa: C901
        """Parse input into a map of Kubernetes resources types to allocation.

        Expects comma separated `key=value` pairs where key is 'cpu' or 'memory'.

        Args:
            v: Value to validate.

        Returns:
            Dictionary that maps Kubernetes resources to values.
        """
        if v is None:
            return {}

        # In case validators are chained
        if isinstance(v, dict):
            v = ",".join([f"{str(key)}={str(val)}" for key, val in v.items()])

        if not isinstance(v, str):
            raise ValueError(f"Unexpected type (must be 'str'): {type(v)}")

        if v.strip() == "":
            return {}

        # Parsing
        parsed: dict[str, str] = {}
        items = [item.strip() for item in v.split(",") if item.strip()]

        for item in items:
            if "=" not in item:
                raise ValueError(f"Invalid format (missing '='): {item}")

            key_raw, val_raw = item.split("=", 1)
            key, val = key_raw.strip(), val_raw.strip()

            if key not in ["cpu", "memory"]:
                raise ValueError(f"Unknown resource type (must be 'cpu' or 'memory'): {key}")

            if key in parsed:
                raise ValueError(f"Duplicate resource type: {key}")

            if key == "cpu" and not _K8S_CPU_REGEX.match(val):
                raise ValueError(f"Invalid 'cpu' value: {val}")
            if key == "memory" and not _K8S_MEMORY_REGEX.match(val):
                raise ValueError(f"Invalid 'memory' value: {val}")

            parsed[key] = val

        return parsed
```

</details>


---

<sub>⏱️ 51s</sub>

### ✅ `bash`

**Check ops version**

$ cd /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__relation-data-classes__C3 && python3 -c "import ops; print(ops.__version__)"

```
2.23.2
<exited with exit code 0>
```


---

<sub>⏱️ 51s</sub>

### ✅ `bash`

**Check Relation.load() signature**

$ cd /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__relation-data-classes__C3 && python3 -c "import ops; import inspect; print(inspect.getsource(ops.Relation.load))" 2>/dev/null || python3 -c "from ops.model import Relation; import inspect; print(inspect.getsource(Relation.load))" 2>/dev/null || echo "Method not found"

<details>
<summary>60 lines</summary>

```
def load(
        self,
        cls: type[_T],
        src: Unit | Application,
        *args: Any,
        decoder: Callable[[str], Any] | None = None,
        **kwargs: Any,
    ) -> _T:
        """Load the data for this relation into an instance of a data class.

        The raw Juju relation data is passed to the data class's ``__init__``
        method as keyword arguments, with values decoded using the provided
        decoder function, or :func:`json.loads` if no decoder is provided.

        For example::

            data = event.relation.load(DatabaseModel, event.app)
            secret_id = data.credentials

        For dataclasses and Pydantic ``BaseModel`` subclasses, only fields in
        the Juju relation data that have a matching field in the class are
        passed as arguments. Pydantic fields that have an ``alias``, or
        dataclasses that have a ``metadata{'alias'=}``, will expect the Juju
        relation data field to have the alias name, but will set the attribute
        on the class to the field name.

        For example::

            class Data(pydantic.BaseModel):
                # This field is called 'secret-id' in the Juju relation data.
                secret_id: str = pydantic.Field(alias='secret-id')

            def _observer(self, event: ops.RelationEvent):
                data = event.relation.load(Data, event.app)
                secret = self.model.get_secret(data.secret_id)

        Any additional positional or keyword arguments will be passed through to
        the data class ``__init__``.

        Args:
            cls: A class, typically a Pydantic `BaseModel` subclass or a
                dataclass, that will accept the Juju relation data as keyword
                arguments, and raise ``ValueError`` if validation fails.
            src: The source of the data to load. This can be either a
                :class:`Unit` or :class:`Application` instance.
            decoder: An optional callable that will be used to decode each field
                before loading into the class. If not provided,
                :func:`json.loads` will be used.
            args: positional arguments to pass through to the data class.
            kwargs: keyword arguments to pass through to the data class.

        Returns:
            An instance of the data class that was provided as ``cls`` with the
            current relation data values.
        """
        try:
            fields = _charm._juju_fields(cls)
        except ValueError:
            fields = None
        data: dict[str, Any] = copy.deepcopy(kwargs)
        if decoder is None:
            decoder = json.loads
        for key, value in sorted(self.data[src].items()):
            value = decoder(value)
            if fields is None:
                data[key] = value
            elif key in fields:
                data[fields[key]] = value
        return cls(*args, **data)
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 57s</sub>

### ✅ `bash`

**Check Relation.save() signature**

$ cd /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__relation-data-classes__C3 && python3 -c "from ops.model import Relation; import inspect; print(inspect.getsource(Relation.save))"

<details>
<summary>78 lines</summary>

```
def save(
        self,
        obj: object,
        dst: Unit | Application,
        *,
        encoder: Callable[[Any], str] | None = None,
    ):
        """Save the data from the provided object to the Juju relation data.

        For example::

            relation = self.model.get_relation('tracing')
            data = TracingRequirerData(receivers=['otlp_http'])
            relation.save(data, self.app)

        For dataclasses and Pydantic ``BaseModel`` subclasses, only the class's
        fields will be saved through to the relation data. Pydantic fields that
        have an ``alias``, or dataclasses that have a ``metadata{'alias'=}``,
        will have the object's value saved to the Juju relation data with the
        alias as the key. For other classes, all of the object's attributes that
        have a class type annotation and value set on the object will be saved
        through to the relation data.

        For example::

            class TransferData(pydantic.BaseModel):
                source: pydantic.AnyHttpUrl = pydantic.Field(alias='from')
                destination: pydantic.AnyHttpUrl = pydantic.Field(alias='to')

            def _add_transfer(self):
                data = TransferData(
                    source='https://a.example.com',
                    destination='https://b.example.com',
                )
                relation = self.model.get_relation('mover')
                # data.source will be stored under the Juju relation key 'from'
                # data.destination will be stored under the Juju relation key 'to'
                relation.save(data, self.unit)

        Args:
            obj: an object with attributes to save to the relation data, typically
                a Pydantic ``BaseModel`` subclass or dataclass.
            dst: The destination in which to save the data to save. This
                can be either a :class:`Unit` or :class:`Application` instance.
            encoder: An optional callable that will be used to encode each field
                before passing to Juju. If not provided, :func:`json.dumps` will
                be used.

        Raises:
            RelationDataTypeError: if the encoder does not return a string.
            RelationNotFoundError: if the relation does not exist.
            RelationDataAccessError: if the charm does not have permission to
                write to the relation data.
        """
        if encoder is None:
            encoder = json.dumps

        # Determine the fields, which become the Juju keys, and the values for
        # each field.
        fields: dict[str, str] = {}  # Class attribute name: Juju key.
        if dataclasses.is_dataclass(obj):
            assert not isinstance(obj, type)  # dataclass instance, not class.
            for field in dataclasses.fields(obj):
                alias = field.metadata.get('alias', field.name)
                fields[field.name] = alias
            values = dataclasses.asdict(obj)
        elif hasattr(obj.__class__, 'model_fields'):
            # Pydantic models:
            for name, field in obj.__class__.model_fields.items():  # type: ignore
                # Pydantic takes care of the alias.
                fields[field.alias or name] = field.alias or name  # type: ignore
            values = obj.model_dump(mode='json', by_alias=True, exclude_defaults=False)  # type: ignore
        else:
            # If we could not otherwise determine the fields for the class,
            # store all the fields that have type annotations. If a charm needs
            # a more specific set of fields, then it should use a dataclass or
            # Pydantic model instead.
            try:
                fields = {k: k for k in get_type_hints(obj.__class__)}
            except TypeError:
                # Most likely Python 3.8. It's not as good, but use __annotations__.
                fields = {k: k for k in obj.__class__.__annotations__}
            values = {field: getattr(obj, field) for field in fields}

        # Encode each value, and then pass it over to Juju.
        data = {field: encoder(values[attr]) for attr, field in sorted(fields.items())}
        self.data[dst].update(data)
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 1m 6s</sub>

### 💬 Copilot

Now let me understand the full current usage of relation data in the charm:

---

<sub>⏱️ 1m 7s</sub>

### ✅ `bash`

**Find all relation data usages**

$ cd /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__relation-data-classes__C3 && grep -n "relation.data\|\.data\[" src/charm.py

```
508:            # relation data, but this way it is more future-proof in case we change from ingress
510:            self.peer_relation.data[self.unit]["private_address"] = self._internal_url
619:                if address := pr.data[unit].get("private_address"):
<exited with exit code 0>
```


---

<sub>⏱️ 1m 7s</sub>

### ✅ `bash`

**Check test files**

$ cd /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__relation-data-classes__C3 && ls tests/unit/

```
conftest.py		     test_charm.py	   test_push_config_to_workload_on_startup.py  test_server_scheme.py
helpers.py		     test_config	   test_remote_configuration_provider.py
test_alertmanager_client.py  test_consumer.py	   test_remote_configuration_requirer.py
test_brute_isolated.py	     test_external_url.py  test_self_scrape_jobs.py
<exited with exit code 0>
```


---

<sub>⏱️ 1m 13s</sub>

### ✅ `bash`

**Find peer relation tests**

$ cd /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__relation-data-classes__C3 && grep -n "private_address\|peer_relation\|replicas" tests/unit/test_charm.py | head -40

```
39:        self.assertEqual(0, len(self.harness.charm.peer_relation.units))  # type: ignore
189:        self.harness.add_relation("replicas", "alertmanager")
<exited with exit code 0>
```


---

<sub>⏱️ 1m 13s</sub>

### ✅ `bash`

**Find private_address in tests**

$ cd /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__relation-data-classes__C3 && grep -rn "private_address" tests/

```
tests/unit/test_external_url.py:117:                self.peer_rel_id, unit_name, {"private_address": f"http://fqdn-{u}:9093"}
tests/unit/test_push_config_to_workload_on_startup.py:92:                {"private_address": f"http://fqdn-{i}"},
tests/unit/test_self_scrape_jobs.py:81:                self.peer_rel_id, unit_name, {"private_address": f"{scheme}://{target}"}
<exited with exit code 0>
```


---

<sub>⏱️ 1m 18s</sub>

### ✅ `bash`

**Check test_external_url.py for relation data usage**

$ cd /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__relation-data-classes__C3 && grep -n "private_address\|peer_rel\|replicas" tests/unit/test_external_url.py | head -30

```
39:        self.peer_rel_id = self.harness.add_relation("replicas", self.app_name)
115:            self.harness.add_relation_unit(self.peer_rel_id, unit_name)
117:                self.peer_rel_id, unit_name, {"private_address": f"http://fqdn-{u}:9093"}
<exited with exit code 0>
```


---

<sub>⏱️ 1m 51s</sub>

### ✅ `view`

**/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__relation-data-classes__C3/tests/unit/test_charm.py**

/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__relation-data-classes__C3/tests/unit/test_charm.py (lines 1-80)

<details>
<summary>80 lines</summary>

```
1. #!/usr/bin/env python3
2. # Copyright 2021 Canonical Ltd.
3. # See LICENSE file for licensing details.
4. import unittest
5. from unittest.mock import patch
6. 
7. import ops
8. import yaml
9. from helpers import k8s_resource_multipatch
10. from ops import pebble
11. from ops.model import ActiveStatus, BlockedStatus
12. from ops.testing import Harness
13. 
14. from alertmanager import WorkloadManager
15. from charm import AlertmanagerCharm
16. 
17. ops.testing.SIMULATE_CAN_CONNECT = True  # pyright: ignore
18. 
19. 
20. class TestWithInitialHooks(unittest.TestCase):
21.     container_name: str = "alertmanager"
22. 
23.     @patch.object(WorkloadManager, "check_config", lambda *a, **kw: ("ok", ""))
24.     @patch("socket.getfqdn", new=lambda *args: "fqdn")
25.     @k8s_resource_multipatch
26.     @patch("lightkube.core.client.GenericSyncClient")
27.     @patch.object(WorkloadManager, "_alertmanager_version", property(lambda *_: "0.0.0"))
28.     def setUp(self, *unused):
29.         self.harness = Harness(AlertmanagerCharm)
30.         self.addCleanup(self.harness.cleanup)
31. 
32.         self.relation_id = self.harness.add_relation("alerting", "otherapp")
33.         self.harness.add_relation_unit(self.relation_id, "otherapp/0")
34.         self.harness.set_leader(True)
35. 
36.         self.harness.begin_with_initial_hooks()
37. 
38.     def test_num_peers(self):
39.         self.assertEqual(0, len(self.harness.charm.peer_relation.units))  # type: ignore
40. 
41.     @patch("socket.getfqdn", new=lambda *args: "fqdn")
42.     def test_pebble_layer_added(self, *unused):
43.         plan = self.harness.get_container_pebble_plan(self.container_name)
44. 
45.         # Check we've got the plan as expected
46.         self.assertIsNotNone(plan.services)
47.         self.assertIsNotNone(service := plan.services.get(self.harness.charm._service_name))
48.         self.assertIsNotNone(command := service.command)  # pyright: ignore
49. 
50.         # Check command is as expected
51.         self.assertEqual(
52.             plan.services, self.harness.charm.alertmanager_workload._alertmanager_layer().services
53.         )
54. 
55.         # Check command contains key arguments
56.         self.assertIn("--config.file", command)
57.         self.assertIn("--storage.path", command)
58.         self.assertIn("--web.listen-address", command)
59.         self.assertIn("--cluster.listen-address", command)
60. 
61.         # Check the service was started
62.         service = self.harness.model.unit.get_container("alertmanager").get_service("alertmanager")
63.         self.assertTrue(service.is_running())
64. 
65.     @patch("socket.getfqdn", new=lambda *args: "fqdn")
66.     def test_relation_data_provides_public_address(self):
67.         # to suppress mypy error: Item "None" of "Optional[Any]" has no attribute "get_relation"
68.         model = self.harness.charm.framework.model
69.         assert model is not None
70. 
71.         rel = model.get_relation("alerting", self.relation_id)
72.         assert rel is not None  # for static checker
73.         expected_address = "fqdn:{}".format(self.harness.charm.api_port)
74.         expected_rel_data = {
75.             "url": "http://fqdn:9093",
76.             "public_address": expected_address,
77.             "scheme": "http",
78.         }
79.         self.assertEqual(expected_rel_data, rel.data[self.harness.charm.unit])
80.
```

</details>


---

<sub>⏱️ 1m 51s</sub>

### ✅ `view`

**/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__relation-data-classes__C3/tests/unit/test_external_url.py**

/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__relation-data-classes__C3/tests/unit/test_external_url.py (lines 100-140)

<details>
<summary>23 lines</summary>

```
100.         # AND WHEN the traefik relation is removed
101.         self.harness.remove_relation_unit(rel_id, "traefik-app/0")
102.         self.harness.remove_relation(rel_id)
103. 
104.         # THEN the fqdn is used as external url
105.         self.assertEqual(self.get_url_cli_arg(), self.fqdn_url)
106. 
107.     @unittest.skip("https://github.com/canonical/operator/issues/736")
108.     @patch.object(WorkloadManager, "check_config", lambda *a, **kw: ("ok", ""))
109.     @patch("socket.getfqdn", new=lambda *args: "fqdn-0")
110.     @k8s_resource_multipatch
111.     def test_cluster_addresses(self, *_):
112.         # GIVEN an alertmanager charm with 3 units in total
113.         for u in [1, 2]:
114.             unit_name = self.app_name + f"/{u}"
115.             self.harness.add_relation_unit(self.peer_rel_id, unit_name)
116.             self.harness.update_relation_data(
117.                 self.peer_rel_id, unit_name, {"private_address": f"http://fqdn-{u}:9093"}
118.             )
119. 
120.         # THEN the `--cluster.peer` args are made up of the hostname and HA port
121.         cluster_args = self.get_cluster_args()
122.         self.assertEqual(cluster_args, ["fqdn-1:9094", "fqdn-2:9094"])  # cluster is on ha-port
```

</details>


---

<sub>⏱️ 1m 56s</sub>

### ✅ `view`

**/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__relation-data-classes__C3/tests/unit/test_push_config_to_workload_on_startup.py**

/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__relation-data-classes__C3/tests/unit/test_push_config_to_workload_on_startup.py (lines 80-110)

<details>
<summary>31 lines</summary>

```
80.     @k8s_resource_multipatch
81.     def test_multi_unit_cluster(self, *_):
82.         """Scenario: Current unit is a part of a multi-unit cluster."""
83.         self.harness.set_leader(False)
84. 
85.         # WHEN multiple units are present
86.         num_units = 3
87.         for i in range(1, num_units):
88.             self.harness.add_relation_unit(self.peer_rel_id, f"{self.app_name}/{i}")
89.             self.harness.update_relation_data(
90.                 self.peer_rel_id,
91.                 f"{self.app_name}/{i}",
92.                 {"private_address": f"http://fqdn-{i}"},
93.             )
94. 
95.         self.assertEqual(self.harness.model.app.planned_units(), num_units)
96. 
97.         # THEN peer clusters cli arg is present in pebble layer command
98.         command = (
99.             self.harness.get_container_pebble_plan(self.harness.charm._container_name)
100.             .services[self.harness.charm._service_name]
101.             .command
102.         )
103.         self.assertIn("--cluster.peer=", command)
104. 
105.     def test_charm_blocks_on_connection_error(self, *_):
106.         self.assertIsInstance(self.harness.charm.unit.status, ActiveStatus)
107.         self.harness.set_can_connect(CONTAINER_NAME, False)
108.         self.harness.update_config({"templates_file": "doesn't matter"})
109.         self.assertNotIsInstance(self.harness.charm.unit.status, ActiveStatus)
110.
```

</details>


---

<sub>⏱️ 1m 56s</sub>

### ✅ `view`

**/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__relation-data-classes__C3/tests/unit/test_self_scrape_jobs.py**

/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__relation-data-classes__C3/tests/unit/test_self_scrape_jobs.py (lines 70-100)

<details>
<summary>16 lines</summary>

```
70.                 "metrics_path": metrics_path,
71.                 "scheme": scheme,
72.                 "static_configs": [{"targets": targets}],
73.             }
74.         ]
75. 
76.         # Add peers
77.         for i, target in enumerate(targets[1:], 1):
78.             unit_name = f"{self.app_name}/{i}"
79.             self.harness.add_relation_unit(self.peer_rel_id, unit_name)
80.             self.harness.update_relation_data(
81.                 self.peer_rel_id, unit_name, {"private_address": f"{scheme}://{target}"}
82.             )
83. 
84.         jobs = self.harness.charm.self_scraping_job
85.         self.assertEqual(jobs_expected, jobs)
```

</details>


---

<sub>⏱️ 2m 24s</sub>

### ✅ `bash`

**Find all peer relation usage in tests**

$ cd /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__relation-data-classes__C3 && grep -rn "replicas\|peer_rel\|private_address" tests/unit/ | grep -v ".pyc"

<details>
<summary>19 lines</summary>

```
tests/unit/test_external_url.py:39:        self.peer_rel_id = self.harness.add_relation("replicas", self.app_name)
tests/unit/test_external_url.py:115:            self.harness.add_relation_unit(self.peer_rel_id, unit_name)
tests/unit/test_external_url.py:117:                self.peer_rel_id, unit_name, {"private_address": f"http://fqdn-{u}:9093"}
tests/unit/helpers.py:55:    peer_rel = PeerRelation("replicas")
tests/unit/helpers.py:59:    state = dataclasses.replace(state, relations=[peer_rel])
tests/unit/helpers.py:60:    state = context.run(context.on.relation_created(peer_rel), state)
tests/unit/test_charm.py:39:        self.assertEqual(0, len(self.harness.charm.peer_relation.units))  # type: ignore
tests/unit/test_charm.py:189:        self.harness.add_relation("replicas", "alertmanager")
tests/unit/test_consumer.py:36:          replicas:
tests/unit/test_push_config_to_workload_on_startup.py:46:        self.peer_rel_id = self.harness.add_relation("replicas", self.app_name)
tests/unit/test_push_config_to_workload_on_startup.py:88:            self.harness.add_relation_unit(self.peer_rel_id, f"{self.app_name}/{i}")
tests/unit/test_push_config_to_workload_on_startup.py:90:                self.peer_rel_id,
tests/unit/test_push_config_to_workload_on_startup.py:92:                {"private_address": f"http://fqdn-{i}"},
tests/unit/test_self_scrape_jobs.py:29:        self.peer_rel_id = self.harness.add_relation("replicas", self.app_name)
tests/unit/test_self_scrape_jobs.py:79:            self.harness.add_relation_unit(self.peer_rel_id, unit_name)
tests/unit/test_self_scrape_jobs.py:81:                self.peer_rel_id, unit_name, {"private_address": f"{scheme}://{target}"}
tests/unit/test_brute_isolated.py:17:    for peer_rel in state.get_relations("replicas"):
tests/unit/test_brute_isolated.py:18:        state = context.run(context.on.relation_departed(peer_rel, remote_unit=2), state)
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 2m 48s</sub>

### 💬 Copilot

Now let me run the existing tests to understand the baseline:

---

<sub>⏱️ 2m 49s</sub>

### ✅ `bash`

**Run unit tests for baseline**

$ cd /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__relation-data-classes__C3 && python3 -m pytest tests/unit/ -x -q --tb=short 2>&1 | tail -30

```
ImportError while loading conftest '/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__relation-data-classes__C3/tests/unit/conftest.py'.
tests/unit/conftest.py:4: in <module>
    from charms.tempo_coordinator_k8s.v0.charm_tracing import charm_tracing_disabled
E   ModuleNotFoundError: No module named 'charms'
<exited with exit code 0>
```


---

<sub>⏱️ 2m 53s</sub>

### ✅ `bash`

**Install dependencies**

$ cd /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__relation-data-classes__C3 && pip install -e ".[dev]" -q 2>&1 | tail -5

```
See /usr/share/doc/python3.12/README.venv for more information.

note: If you believe this is a mistake, please contact your Python installation or OS distribution provider. You can override this, at the risk of breaking your Python installation or OS, by passing --break-system-packages.
hint: See PEP 668 for the detailed specification.
<exited with exit code 0>
```


---

<sub>⏱️ 3m 4s</sub>

### ✅ `bash`

**Run unit tests using venv**

$ cd /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__relation-data-classes__C3 && source .venv/bin/activate && python3 -m pytest tests/unit/ -x -q --tb=short 2>&1 | tail -30

<details>
<summary>9 lines</summary>

```
/home/ubuntu/alertmanager-k8s-operator/.venv/lib/python3.12/site-packages/paramiko/pkey.py:82: CryptographyDeprecationWarning: TripleDES has been moved to cryptography.hazmat.decrepit.ciphers.algorithms.TripleDES and will be removed from cryptography.hazmat.primitives.ciphers.algorithms in 48.0.0.
  "cipher": algorithms.TripleDES,
/home/ubuntu/alertmanager-k8s-operator/.venv/lib/python3.12/site-packages/paramiko/transport.py:253: CryptographyDeprecationWarning: TripleDES has been moved to cryptography.hazmat.decrepit.ciphers.algorithms.TripleDES and will be removed from cryptography.hazmat.primitives.ciphers.algorithms in 48.0.0.
  "class": algorithms.TripleDES,
ImportError while loading conftest '/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__relation-data-classes__C3/tests/unit/conftest.py'.
tests/unit/conftest.py:4: in <module>
    from charms.tempo_coordinator_k8s.v0.charm_tracing import charm_tracing_disabled
E   ModuleNotFoundError: No module named 'charms'
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 3m 10s</sub>

### ✅ `bash`

**Check if charms lib is in venv**

$ cd /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__relation-data-classes__C3 && ls .venv/lib/python*/site-packages/ | grep charms || echo "no charms"

```
no charms
<exited with exit code 0>
```


---

<sub>⏱️ 3m 10s</sub>

### ✅ `bash`

**Check lib directory**

$ ls /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__relation-data-classes__C3/lib/

```
charms
<exited with exit code 0>
```


---

<sub>⏱️ 4m 15s</sub>

### ✅ `bash`

**Run unit tests with correct PYTHONPATH**

$ cd /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__relation-data-classes__C3 && source .venv/bin/activate && PYTHONPATH=lib:src python3 -m pytest tests/unit/ -x -q --tb=short 2>&1 | tail -20

```
<command with shellId: 15 is still running after 60 seconds. The command is still running but hasn't produced output yet. It may be waiting for input or still processing. Use read_bash to continue waiting, write_bash if you think it needs input, or stop_bash to stop it.>
```


---

<sub>⏱️ 5m 10s</sub>

### ✅ `read_bash`

<details>
<summary>Arguments</summary>

```json
{
  "shellId": "15",
  "delay": 60
}
```

</details>

<details>
<summary>17 lines</summary>

```
tests/unit/test_remote_configuration_requirer.py::TestAlertmanagerRemoteConfigurationRequirer::test_templates_pushed_to_relation_data_bag_are_saved_to_templates_file_in_alertmanager
tests/unit/test_remote_configuration_requirer.py::TestAlertmanagerRemoteConfigurationRequirer::test_valid_config_pushed_to_relation_data_bag_updates_alertmanager_config
  /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__relation-data-classes__C3/tests/unit/test_remote_configuration_requirer.py:52: PendingDeprecationWarning: Harness is deprecated. For the recommended approach, see: https://ops.readthedocs.io/en/latest/howto/write-unit-tests-for-a-charm.html
    self.harness = testing.Harness(AlertmanagerCharm)

tests/unit/test_self_scrape_jobs.py::TestWithInitialHooks::test_self_scraping_job_with_no_peers
tests/unit/test_self_scrape_jobs.py::TestWithInitialHooks::test_self_scraping_job_with_peers
  /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__relation-data-classes__C3/tests/unit/test_self_scrape_jobs.py:22: PendingDeprecationWarning: Harness is deprecated. For the recommended approach, see: https://ops.readthedocs.io/en/latest/howto/write-unit-tests-for-a-charm.html
    self.harness = Harness(AlertmanagerCharm)

tests/unit/test_self_scrape_jobs.py::TestWithInitialHooks::test_self_scraping_job_with_peers
  /home/ubuntu/alertmanager-k8s-operator/.venv/lib/python3.12/site-packages/ops/_private/harness.py:1112: UserWarning: Remote unit name invalid: the remote application of replicas is called 'alertmanager-k8s'; the remote unit name should be alertmanager-k8s/<some-number>, not 'am/1'.
    warnings.warn(

tests/unit/test_self_scrape_jobs.py::TestWithInitialHooks::test_self_scraping_job_with_peers
  /home/ubuntu/alertmanager-k8s-operator/.venv/lib/python3.12/site-packages/ops/_private/harness.py:1112: UserWarning: Remote unit name invalid: the remote application of replicas is called 'alertmanager-k8s'; the remote unit name should be alertmanager-k8s/<some-number>, not 'am/2'.
    warnings.warn(

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
====== 57 passed, 3 skipped, 4 xfailed, 311 warnings in 105.71s (0:01:45) ======
<command with id: 15 exited with exit code 0>
```

</details>


---

<sub>⏱️ 5m 17s</sub>

### 💬 Copilot

Good - 57 passed baseline. Now let me implement the changes:

---

<sub>⏱️ 5m 17s</sub>

### ✅ `view`

**/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__relation-data-classes__C3/src/charm.py**

/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__relation-data-classes__C3/src/charm.py (lines 1-15)

<details>
<summary>15 lines</summary>

```
1. #!/usr/bin/env python3
2. # Copyright 2021 Canonical Ltd.
3. # See LICENSE file for licensing details.
4. 
5. """A Juju charm for alertmanager."""
6. 
7. import logging
8. import socket
9. import subprocess
10. from dataclasses import dataclass
11. from pathlib import Path
12. from types import SimpleNamespace
13. from typing import List, Optional, Tuple, cast
14. from urllib.parse import urlparse
15.
```

</details>


---

<sub>⏱️ 5m 22s</sub>

### ✅ `edit`

**/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__relation-data-classes__C3/src/charm.py**

/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__relation-data-classes__C3/src/charm.py

```
File /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__relation-data-classes__C3/src/charm.py updated with changes.
```


---

<sub>⏱️ 5m 26s</sub>

### 💬 Copilot

Now add the model and decoder after the imports, before the `TLSConfig` dataclass:

---

<sub>⏱️ 5m 26s</sub>

### ✅ `view`

**/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__relation-data-classes__C3/src/charm.py**

/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__relation-data-classes__C3/src/charm.py (lines 60-70)

<details>
<summary>11 lines</summary>

```
60. )
61. from config_builder import ConfigBuilder, ConfigError
62. 
63. logger = logging.getLogger(__name__)
64. 
65. 
66. @dataclass
67. class TLSConfig:
68.     """TLS configuration received by the charm over the `certificates` relation."""
69. 
70.     server_cert: str
```

</details>


---

<sub>⏱️ 5m 32s</sub>

### ✅ `edit`

**/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__relation-data-classes__C3/src/charm.py**

/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__relation-data-classes__C3/src/charm.py

```
File /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__relation-data-classes__C3/src/charm.py updated with changes.
```


---

<sub>⏱️ 5m 40s</sub>

### 💬 Copilot

Now update the write path in `_common_exit_hook`:

---

<sub>⏱️ 5m 40s</sub>

### ✅ `edit`

**/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__relation-data-classes__C3/src/charm.py**

/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__relation-data-classes__C3/src/charm.py

```
File /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__relation-data-classes__C3/src/charm.py updated with changes.
```


---

<sub>⏱️ 5m 44s</sub>

### 💬 Copilot

Now update the read path in `_get_peer_hostnames`:

---

<sub>⏱️ 5m 44s</sub>

### ✅ `view`

**/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__relation-data-classes__C3/src/charm.py**

/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__relation-data-classes__C3/src/charm.py (lines 635-660)

<details>
<summary>26 lines</summary>

```
635.             addresses.append(self._internal_url)
636.         if pr := self.peer_relation:
637.             for unit in pr.units:  # pr.units only holds peers (self.unit is not included)
638.                 if address := pr.data[unit].get("private_address"):
639.                     addresses.append(address)
640. 
641.         # Save only the hostname part of the address
642.         # Sort the hostnames in case their order is not guaranteed, to reduce unnecessary updates
643.         hostnames = sorted([urlparse(address).hostname for address in addresses])
644. 
645.         return hostnames
646. 
647.     @property
648.     def _tls_config(self) -> Optional[TLSConfig]:
649.         certificates, key = self._cert_requirer.get_assigned_certificate(
650.             certificate_request=self._csr_attributes
651.         )
652.         if not (key and certificates):
653.             return None
654.         return TLSConfig(certificates.certificate.raw, certificates.ca.raw, key.raw)
655. 
656.     @property
657.     def _tls_available(self) -> bool:
658.         return bool(self._tls_config)
659. 
660.     @property
```

</details>


---

<sub>⏱️ 5m 49s</sub>

### ✅ `edit`

**/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__relation-data-classes__C3/src/charm.py**

/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__relation-data-classes__C3/src/charm.py

```
File /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__relation-data-classes__C3/src/charm.py updated with changes.
```


---

<sub>⏱️ 5m 54s</sub>

### 💬 Copilot

Now let's verify the changes look correct:

---

<sub>⏱️ 5m 54s</sub>

### ✅ `bash`

**Verify changes**

$ cd /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__relation-data-classes__C3 && grep -n "private_address\|PeerRelation\|decode_relation\|peer_relation\|json\|pydantic" src/charm.py | grep -v "^.*#"

<details>
<summary>20 lines</summary>

```
7:import json
17:import pydantic
66:class PeerRelationUnitData(pydantic.BaseModel):
69:    private_address: Optional[str] = None
72:def _decode_relation_str(v: str) -> Any:
75:        return json.loads(v)
76:    except json.JSONDecodeError:
268:            self.on[self._relations.peer].relation_joined, self._on_peer_relation_joined
271:            self.on[self._relations.peer].relation_changed, self._on_peer_relation_changed
407:    def peer_relation(self) -> Optional["Relation"]:
523:        if self.peer_relation:
527:            self.peer_relation.save(
528:                PeerRelationUnitData(private_address=self._internal_url), self.unit
569:    def _on_peer_relation_joined(self, _):
573:    def _on_peer_relation_changed(self, _):
636:        if pr := self.peer_relation:
638:                data = pr.load(PeerRelationUnitData, unit, decoder=_decode_relation_str)
639:                if data.private_address:
640:                    addresses.append(data.private_address)
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 6m 0s</sub>

### 💬 Copilot

Now run the tests to verify:

---

<sub>⏱️ 6m 9s</sub>

### ✅ `bash`

**Run unit tests after changes**

$ cd /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__relation-data-classes__C3 && source .venv/bin/activate && PYTHONPATH=lib:src python3 -m pytest tests/unit/ -x -q --tb=short 2>&1 | tail -15

<details>
<summary>13 lines</summary>

```
../../../home/ubuntu/alertmanager-k8s-operator/.venv/lib/python3.12/site-packages/pydantic/_internal/_generate_schema.py:293
  /home/ubuntu/alertmanager-k8s-operator/.venv/lib/python3.12/site-packages/pydantic/_internal/_generate_schema.py:293: PydanticDeprecatedSince20: `json_encoders` is deprecated. See https://docs.pydantic.dev/2.11/concepts/serialization/#custom-serializers for alternatives. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.11/migration/
    warnings.warn(

tests/unit/test_brute_isolated.py::test_startup_shutdown_sequence
tests/unit/test_brute_isolated.py::test_startup_shutdown_sequence
  /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__relation-data-classes__C3/lib/charms/tls_certificates_interface/v4/tls_certificates.py:1717: DeprecationWarning: JujuVersion.from_environ() is deprecated, use self.model.juju_version instead
    if not JujuVersion.from_environ().has_secrets:

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ============================
FAILED tests/unit/test_brute_isolated.py::test_startup_shutdown_sequence - sc...
!!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
=================== 1 failed, 10 passed, 4 warnings in 3.60s ===================
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 6m 21s</sub>

### ✅ `bash`

**Run failing test with full traceback**

$ cd /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__relation-data-classes__C3 && source .venv/bin/activate && PYTHONPATH=lib:src python3 -m pytest tests/unit/test_brute_isolated.py -x -q --tb=long 2>&1 | tail -40

<details>
<summary>38 lines</summary>

```
DEBUG    root:storage.py:67 Initializing SQLite local storage: :memory:.
DEBUG    charms.tls_certificates_interface.v4.tls_certificates:tls_certificates.py:1992 No relation: certificates
DEBUG    charms.tls_certificates_interface.v4.tls_certificates:tls_certificates.py:1992 No relation: certificates
WARNING  charms.grafana_k8s.v0.grafana_dashboard:grafana_dashboard.py:1162 Invalid Grafana dashboards folder at /tmp/tmpm0o4fiwa/src/grafana_dashboards: directory does not exist
DEBUG    charms.tls_certificates_interface.v4.tls_certificates:tls_certificates.py:1992 No relation: certificates
DEBUG    charms.tls_certificates_interface.v4.tls_certificates:tls_certificates.py:1992 No relation: certificates
DEBUG    charms.tls_certificates_interface.v4.tls_certificates:tls_certificates.py:1992 No relation: certificates
DEBUG    charms.prometheus_k8s.v0.prometheus_scrape:prometheus_scrape.py:1413 Invalid Prometheus alert rules folder at /tmp/tmpm0o4fiwa/src/prometheus_alert_rules: directory does not exist
DEBUG    charms.tempo_coordinator_k8s.v0.tracing:tracing.py:854 no relation on 'tracing': tracing not ready
DEBUG    charms.tls_certificates_interface.v4.tls_certificates:tls_certificates.py:1992 No relation: certificates
DEBUG    charms.tls_certificates_interface.v4.tls_certificates:tls_certificates.py:1992 No relation: certificates
DEBUG    charms.tls_certificates_interface.v4.tls_certificates:tls_certificates.py:1992 No relation: certificates
INFO     tracing:charm_tracing.py:555 Tracing DISABLED: skipping root span initialization
DEBUG    root:_main.py:436 Emitting Juju event install.
DEBUG    root:_main.py:324 ops 2.21.1 up and running.
DEBUG    root:storage.py:67 Initializing SQLite local storage: :memory:.
DEBUG    charms.tls_certificates_interface.v4.tls_certificates:tls_certificates.py:1992 No relation: certificates
DEBUG    charms.tls_certificates_interface.v4.tls_certificates:tls_certificates.py:1992 No relation: certificates
WARNING  charms.grafana_k8s.v0.grafana_dashboard:grafana_dashboard.py:1162 Invalid Grafana dashboards folder at /tmp/tmpy66k6sy3/src/grafana_dashboards: directory does not exist
DEBUG    charms.tls_certificates_interface.v4.tls_certificates:tls_certificates.py:1992 No relation: certificates
DEBUG    charms.tls_certificates_interface.v4.tls_certificates:tls_certificates.py:1992 No relation: certificates
=============================== warnings summary ===============================
../../../home/ubuntu/alertmanager-k8s-operator/.venv/lib/python3.12/site-packages/pydantic/_internal/_config.py:323
  /home/ubuntu/alertmanager-k8s-operator/.venv/lib/python3.12/site-packages/pydantic/_internal/_config.py:323: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.11/migration/
    warnings.warn(DEPRECATION_MESSAGE, DeprecationWarning)

../../../home/ubuntu/alertmanager-k8s-operator/.venv/lib/python3.12/site-packages/pydantic/_internal/_generate_schema.py:293
  /home/ubuntu/alertmanager-k8s-operator/.venv/lib/python3.12/site-packages/pydantic/_internal/_generate_schema.py:293: PydanticDeprecatedSince20: `json_encoders` is deprecated. See https://docs.pydantic.dev/2.11/concepts/serialization/#custom-serializers for alternatives. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.11/migration/
    warnings.warn(

tests/unit/test_brute_isolated.py::test_startup_shutdown_sequence
tests/unit/test_brute_isolated.py::test_startup_shutdown_sequence
  /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__relation-data-classes__C3/lib/charms/tls_certificates_interface/v4/tls_certificates.py:1717: DeprecationWarning: JujuVersion.from_environ() is deprecated, use self.model.juju_version instead
    if not JujuVersion.from_environ().has_secrets:

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ============================
FAILED tests/unit/test_brute_isolated.py::test_startup_shutdown_sequence - sc...
!!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
======================== 1 failed, 4 warnings in 2.38s =========================
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 6m 33s</sub>

### ✅ `bash`

**Get detailed failure info**

$ cd /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__relation-data-classes__C3 && source .venv/bin/activate && PYTHONPATH=lib:src python3 -m pytest tests/unit/test_brute_isolated.py -x -q --tb=long 2>&1 | grep -A 30 "FAILED\|Error\|error"

<details>
<summary>206 lines</summary>

```
FAILED

=================================== FAILURES ===================================
________________________ test_startup_shutdown_sequence ________________________

self = <scenario._runtime.Runtime object at 0x7ca1f34eca70>
state = State(config={'config_file': ''}, relations=frozenset({PeerRelation(endpoint='replicas', interface=None, id=1, local_a...}}, _data_type_name='StoredStateData')}), app_status=UnknownStatus(), unit_status=UnknownStatus(), workload_version='')
event = _Event(path='replicas_relation_created', storage=None, relation=PeerRelation(endpoint='replicas', interface=None, id=1...ce=None, check_info=None, action=None, custom_event=None, custom_event_args=(), custom_event_kwargs={}, _owner_path=[])
context = <scenario.context.Context object at 0x7ca1f34dd190>

    @contextmanager
    def exec(
        self,
        state: State,
        event: _Event,
        context: Context,
    ):
        """Runs an event with this state as initial state on a charm.
    
        Returns the 'output state', that is, the state as mutated by the charm during the
        event handling.
    
        This will set the environment up and call ops.main().
        After that it's up to Ops.
        """
        from ._consistency_checker import check_consistency  # avoid cycles
    
        check_consistency(state, event, self._charm_spec, self._juju_version)
    
        charm_type = self._charm_spec.charm_type
        logger.info(f'Preparing to fire {event.name} on {charm_type.__name__}')
--
        except ImportError:
            self._tracing_mock = None
    
        model_backend = _MockModelBackend(
            state=state,
            event=event,
            context=context,
            charm_spec=charm_spec,
            juju_context=juju_context,
        )
    
>       super().__init__(self.charm_spec.charm_type, model_backend, juju_context=juju_context)

/home/ubuntu/alertmanager-k8s-operator/.venv/lib/python3.12/site-packages/scenario/_ops_main_mock.py:147: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <scenario._ops_main_mock.Ops object at 0x7ca1f34dec00>
charm_class = <class 'scenario._runtime.Runtime._wrap.<locals>.WrappedCharm'>
model_backend = <scenario.mocking._MockModelBackend object at 0x7ca1f34de8d0>
use_juju_for_storage = None, charm_state_path = '.unit-state.db'
juju_context = _JujuContext(action_name=None, action_uuid=None, charm_dir=PosixPath('/tmp/tmppq5a6f03'), debug=False, debug_at=set(),...label=None, secret_revision=None, storage_name=None, unit_name='alertmanager-k8s/0', version=3.6.4, workload_name=None)

    def __init__(
        self,
        charm_class: type[_charm.CharmBase],
        model_backend: _model._ModelBackend | None = None,
        use_juju_for_storage: bool | None = None,
        charm_state_path: str = CHARM_STATE_FILE,
        juju_context: _JujuContext | None = None,
    ):
        from . import tracing  # break circular import
--
        except AttributeError:
            name = str(charm_class)
    
        self._juju_context = juju_context
        if tracing:
            tracing._setup(juju_context, name)
        self._tracing_context = tracer.start_as_current_span('ops.main')
        self._tracing_context.__enter__()
        self._charm_state_path = charm_state_path
        self._charm_class = charm_class
        if model_backend is None:
            model_backend = _model._ModelBackend(juju_context=self._juju_context)
        self._model_backend = model_backend
    
        # Do this as early as possible to be sure to catch the most logs.
        self._setup_root_logging()
    
        self._charm_root = self._juju_context.charm_dir
        self._charm_meta = self._load_charm_meta()
        self._use_juju_for_storage = use_juju_for_storage
    
        # Set up dispatcher, framework and charm objects.
        self.dispatcher = _Dispatcher(self._charm_root, self._juju_context)
        self.dispatcher.run_any_legacy_hook()
    
        self.framework = self._make_framework(self.dispatcher)
>       self.charm = self._charm_class(self.framework)

/home/ubuntu/alertmanager-k8s-operator/.venv/lib/python3.12/site-packages/ops/_main.py:310: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

--
        # If prometheus were to scrape an ingress URL instead, it would error out with:
        # x509: cannot validate certificate.
        peer_api_netlocs = [
            f"{hostname}:{self._ports.api}"
>           for hostname in self._get_peer_hostnames(include_this_unit=True)
        ]

src/charm.py:329: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

args = (<scenario._runtime.Runtime._wrap.<locals>.WrappedCharm object at 0x7ca1f34f9340>,)
kwargs = {'include_this_unit': True}
name_ = 'AlertmanagerCharm._get_peer_hostnames'

    @functools.wraps(callable)
    def wrapped_function(*args, **kwargs):  # type: ignore
        name_ = name or getattr(
            callable, "__qualname__", getattr(callable, "__name__", str(callable))
        )
        with _span(f"{qualifier} call: {name_}"):  # type: ignore
>           return callable(*args, **kwargs)  # type: ignore

lib/charms/tempo_coordinator_k8s/v0/charm_tracing.py:946: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <scenario._runtime.Runtime._wrap.<locals>.WrappedCharm object at 0x7ca1f34f9340>
include_this_unit = True

    def _get_peer_hostnames(self, include_this_unit=True) -> List[str]:
        """Returns a list of the hostnames of the peer units.
    
--
E               AttributeError: 'Relation' object has no attribute 'load'

src/charm.py:638: AttributeError

The above exception was the direct cause of the following exception:

context = <scenario.context.Context object at 0x7ca1f34dd190>

    def test_startup_shutdown_sequence(context: Context):
>       state = begin_with_initial_hooks_isolated(context)

tests/unit/test_brute_isolated.py:14: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

context = <scenario.context.Context object at 0x7ca1f34dd190>

    def begin_with_initial_hooks_isolated(context: Context, *, leader: bool = True) -> State:
        container = Container(
            "alertmanager",
            can_connect=False,
            execs={
                Exec(["update-ca-certificates", "--fresh"]),
                Exec(
                    ["alertmanager", "--version"],
                    stdout="alertmanager, version 0.23.0 (branch: HEAD, ...",
                ),
                Exec(["/usr/bin/amtool", "check-config", "/etc/alertmanager/alertmanager.yml"]),
            },
        )
        state = State(config={"config_file": ""}, containers=[container])
        peer_rel = PeerRelation("replicas")
    
        state = context.run(context.on.install(), state)
--
            raise TypeError(
                f'call with an event from `ctx.on`, like `ctx.on.{suggested}`',
            )
        if callable(event):
            raise TypeError(
                'You should call the event method. Did you forget to add parentheses?',
            )
    
        if event.action:
            # Reset the logs, failure status, and results, in case the context
            # is reused.
            self.action_logs.clear()
            if self.action_results is not None:
                self.action_results.clear()
            self._action_failure_message = None
>       with self._run(event=event, state=state) as ops:

/home/ubuntu/alertmanager-k8s-operator/.venv/lib/python3.12/site-packages/scenario/context.py:716: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <contextlib._GeneratorContextManager object at 0x7ca1f8f3a2d0>

    def __enter__(self):
        # do not keep args and kwds alive unnecessarily
        # they are only needed for recreation, which is not possible anymore
        del self.args, self.kwds, self.func
        try:
>           return next(self.gen)

/usr/lib/python3.12/contextlib.py:137: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <scenario.context.Context object at 0x7ca1f34dd190>
event = _Event(path='replicas_relation_created', storage=None, relation=PeerRelation(endpoint='replicas', interface=None, id=1...ce=None, check_info=None, action=None, custom_event=None, custom_event_args=(), custom_event_kwargs={}, _owner_path=[])
state = State(config={'config_file': ''}, relations=frozenset({PeerRelation(endpoint='replicas', interface=None, id=1, local_a...}}, _data_type_name='StoredStateData')}), app_status=UnknownStatus(), unit_status=UnknownStatus(), workload_version='')
--
            except (NoObserverError, ActionFailed):
                raise  # propagate along
            except Exception as e:
>               raise UncaughtCharmError(
                    f'Uncaught exception ({type(e)}) in operator/charm code: {e!r}',
                ) from e
E               scenario.errors.UncaughtCharmError: Uncaught exception (<class 'AttributeError'>) in operator/charm code: AttributeError("'Relation' object has no attribute 'load'")

/home/ubuntu/alertmanager-k8s-operator/.venv/lib/python3.12/site-packages/scenario/_runtime.py:343: UncaughtCharmError
------------------------------ Captured log call -------------------------------
DEBUG    root:_main.py:324 ops 2.21.1 up and running.
DEBUG    root:storage.py:67 Initializing SQLite local storage: :memory:.
DEBUG    charms.tls_certificates_interface.v4.tls_certificates:tls_certificates.py:1992 No relation: certificates
DEBUG    charms.tls_certificates_interface.v4.tls_certificates:tls_certificates.py:1992 No relation: certificates
WARNING  charms.grafana_k8s.v0.grafana_dashboard:grafana_dashboard.py:1162 Invalid Grafana dashboards folder at /tmp/tmpbby9qloh/src/grafana_dashboards: directory does not exist
DEBUG    charms.tls_certificates_interface.v4.tls_certificates:tls_certificates.py:1992 No relation: certificates
DEBUG    charms.tls_certificates_interface.v4.tls_certificates:tls_certificates.py:1992 No relation: certificates
DEBUG    charms.tls_certificates_interface.v4.tls_certificates:tls_certificates.py:1992 No relation: certificates
DEBUG    charms.prometheus_k8s.v0.prometheus_scrape:prometheus_scrape.py:1413 Invalid Prometheus alert rules folder at /tmp/tmpbby9qloh/src/prometheus_alert_rules: directory does not exist
DEBUG    charms.tempo_coordinator_k8s.v0.tracing:tracing.py:854 no relation on 'tracing': tracing not ready
DEBUG    charms.tls_certificates_interface.v4.tls_certificates:tls_certificates.py:1992 No relation: certificates
DEBUG    charms.tls_certificates_interface.v4.tls_certificates:tls_certificates.py:1992 No relation: certificates
DEBUG    charms.tls_certificates_interface.v4.tls_certificates:tls_certificates.py:1992 No relation: certificates
INFO     tracing:charm_tracing.py:555 Tracing DISABLED: skipping root span initialization
DEBUG    root:_main.py:436 Emitting Juju event install.
DEBUG    root:_main.py:324 ops 2.21.1 up and running.
DEBUG    root:storage.py:67 Initializing SQLite local storage: :memory:.
DEBUG    charms.tls_certificates_interface.v4.tls_certificates:tls_certificates.py:1992 No relation: certificates
DEBUG    charms.tls_certificates_interface.v4.tls_certificates:tls_certificates.py:1992 No relation: certificates
WARNING  charms.grafana_k8s.v0.grafana_dashboard:grafana_dashboard.py:1162 Invalid Grafana dashboards folder at /tmp/tmppq5a6f03/src/grafana_dashboards: directory does not exist
DEBUG    charms.tls_certificates_interface.v4.tls_certificates:tls_certificates.py:1992 No relation: certificates
DEBUG    charms.tls_certificates_interface.v4.tls_certificates:tls_certificates.py:1992 No relation: certificates
=============================== warnings summary ===============================
../../../home/ubuntu/alertmanager-k8s-operator/.venv/lib/python3.12/site-packages/pydantic/_internal/_config.py:323
  /home/ubuntu/alertmanager-k8s-operator/.venv/lib/python3.12/site-packages/pydantic/_internal/_config.py:323: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.11/migration/
    warnings.warn(DEPRECATION_MESSAGE, DeprecationWarning)

../../../home/ubuntu/alertmanager-k8s-operator/.venv/lib/python3.12/site-packages/pydantic/_internal/_generate_schema.py:293
  /home/ubuntu/alertmanager-k8s-operator/.venv/lib/python3.12/site-packages/pydantic/_internal/_generate_schema.py:293: PydanticDeprecatedSince20: `json_encoders` is deprecated. See https://docs.pydantic.dev/2.11/concepts/serialization/#custom-serializers for alternatives. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.11/migration/
    warnings.warn(

tests/unit/test_brute_isolated.py::test_startup_shutdown_sequence
tests/unit/test_brute_isolated.py::test_startup_shutdown_sequence
  /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__relation-data-classes__C3/lib/charms/tls_certificates_interface/v4/tls_certificates.py:1717: DeprecationWarning: JujuVersion.from_environ() is deprecated, use self.model.juju_version instead
    if not JujuVersion.from_environ().has_secrets:

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ============================
FAILED tests/unit/test_brute_isolated.py::test_startup_shutdown_sequence - sc...
!!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
======================== 1 failed, 4 warnings in 2.30s =========================
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 6m 47s</sub>

### 💬 Copilot

The `scenario` library uses its own `Relation` mock that doesn't proxy `load()`/`save()`. Let me check if this test was passing before my changes:

---

<sub>⏱️ 7m 9s</sub>

### ✅ `bash`

**Check if test passes in baseline**

$ cd /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__relation-data-classes__C3 && git stash && source .venv/bin/activate && PYTHONPATH=lib:src python3 -m pytest tests/unit/test_brute_isolated.py -x -q --tb=short 2>&1 | tail -5

<details>
<summary>6 lines</summary>

```
Saved working directory and index state WIP on (no branch): 596a093 baseline for experiment
  /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__relation-data-classes__C3/lib/charms/karma_k8s/v0/karma_dashboard.py:332: PydanticDeprecatedSince20: The `dict` method is deprecated; use `model_dump` instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.11/migration/
    as_dict = data.dict()

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
======================= 5 passed, 81 warnings in 15.71s ========================
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 7m 16s</sub>

### ✅ `bash`

**Check scenario version**

$ cd /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__relation-data-classes__C3 && git stash pop && source .venv/bin/activate && python3 -c "import scenario; print(scenario.__version__)"

<details>
<summary>14 lines</summary>

```
HEAD detached from 1005cde
Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
	modified:   src/charm.py

Untracked files:
  (use "git add <file>..." to include in what will be committed)
	.baseline_commit

no changes added to commit (use "git add" and/or "git commit -a")
Dropped refs/stash@{0} (2d2a9c970fb0bb71e0abb4450545a2444e8b592f)
Traceback (most recent call last):
  File "<string>", line 1, in <module>
AttributeError: module 'scenario' has no attribute '__version__'
<exited with exit code 1>
```

</details>


---

<sub>⏱️ 7m 16s</sub>

### ✅ `bash`

**Check if scenario Relation has load/save**

$ python3 -c "import scenario; import inspect; import ops; r = ops.Relation; print(dir(r))" 2>/dev/null | tr ',' '\n' | grep "load\|save"

```
'load'
 'save']
<exited with exit code 0>
```


---

<sub>⏱️ 7m 22s</sub>

### ✅ `bash`

**Check scenario version from venv**

$ cd /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__relation-data-classes__C3 && source .venv/bin/activate && python3 -c "import scenario; print(scenario.__version__)" 2>/dev/null || python3 -c "import pkg_resources; print(pkg_resources.get_distribution('ops-scenario').version)" 2>/dev/null || python3 -c "import importlib.metadata; print(importlib.metadata.version('ops-scenario'))"

```
7.21.1
<exited with exit code 0>
```


---

<sub>⏱️ 7m 27s</sub>

### ✅ `bash`

**Check scenario Relation for load/save**

$ cd /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__relation-data-classes__C3 && source .venv/bin/activate && python3 -c "from scenario.state import Relation; print(dir(Relation))" | tr ',' '\n' | grep "load\|save"

```

<exited with exit code 1>
```


---

<sub>⏱️ 7m 33s</sub>

### ✅ `view`

**/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__relation-data-classes__C3/tests/unit/test_brute_isolated.py**

/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__relation-data-classes__C3/tests/unit/test_brute_isolated.py

<details>
<summary>49 lines</summary>

```
1. # Copyright 2023 Canonical Ltd.
2. # See LICENSE file for licensing details.
3. 
4. from unittest.mock import patch
5. 
6. import pytest
7. from helpers import add_relation_sequence, begin_with_initial_hooks_isolated
8. from ops.testing import Context, Relation, State
9. 
10. """Some brute-force tests, so that other tests can remain focused."""
11. 
12. 
13. def test_startup_shutdown_sequence(context: Context):
14.     state = begin_with_initial_hooks_isolated(context)
15.     state = context.run(context.on.update_status(), state)
16. 
17.     for peer_rel in state.get_relations("replicas"):
18.         state = context.run(context.on.relation_departed(peer_rel, remote_unit=2), state)
19. 
20.     state = context.run(context.on.stop(), state)
21.     context.run(context.on.remove(), state)
22. 
23. 
24. @pytest.mark.parametrize("fqdn", ["localhost", "am-0.endpoints.cluster.local"])
25. @pytest.mark.parametrize("leader", [True, False])
26. class TestAlertingRelationDataUniformity:
27.     """Scenario: The charm is related to several different prometheus apps."""
28. 
29.     @pytest.fixture
30.     def post_startup(self, context, fqdn, leader) -> State:
31.         with patch("socket.getfqdn", new=lambda *args: fqdn):
32.             state = begin_with_initial_hooks_isolated(context, leader=leader)
33. 
34.             # Add several relations TODO: how to obtain the next rel_id automatically?
35.             prom_rels = [Relation("alerting", id=rel_id) for rel_id in (10, 11, 12)]
36.             for prom_rel in prom_rels:
37.                 state = add_relation_sequence(context, state, prom_rel)
38.             return state
39. 
40.     def test_relation_data_is_the_same_for_all_related_apps(self, post_startup, fqdn):
41.         # GIVEN an isolated alertmanager charm after the startup sequence is complete
42.         state = post_startup
43. 
44.         # THEN the "alerting" relation data has the same contents for all related apps
45.         relations = state.get_relations("alerting")
46.         for i in range(1, len(relations)):
47.             assert relations[0].local_unit_data == relations[i].local_unit_data
48.             assert relations[0].local_app_data == relations[i].local_app_data
49.
```

</details>


---

<sub>⏱️ 7m 36s</sub>

### ✅ `view`

**/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__relation-data-classes__C3/tests/unit/helpers.py**

/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__relation-data-classes__C3/tests/unit/helpers.py

<details>
<summary>91 lines</summary>

```
1. #!/usr/bin/env python3
2. # Copyright 2021 Canonical Ltd.
3. # See LICENSE file for licensing details.
4. 
5. """Helper functions for writing tests."""
6. 
7. import dataclasses
8. from unittest.mock import patch
9. 
10. from ops.testing import Container, Context, Exec, PeerRelation, Relation, State
11. 
12. 
13. def no_op(*_, **__) -> None:
14.     pass
15. 
16. 
17. def tautology(*_, **__) -> bool:
18.     return True
19. 
20. 
21. def cli_arg(plan, cli_opt):
22.     plan_dict = plan.to_dict()
23.     args = plan_dict["services"]["alertmanager"]["command"].split()
24.     for arg in args:
25.         opt_list = arg.split("=")
26.         if len(opt_list) == 2 and opt_list[0] == cli_opt:
27.             return opt_list[1]
28.         if len(opt_list) == 1 and opt_list[0] == cli_opt:
29.             return opt_list[0]
30.     return None
31. 
32. 
33. k8s_resource_multipatch = patch.multiple(
34.     "charm.KubernetesComputeResourcesPatch",
35.     _namespace="test-namespace",
36.     _patch=tautology,
37.     is_ready=tautology,
38. )
39. 
40. 
41. def begin_with_initial_hooks_isolated(context: Context, *, leader: bool = True) -> State:
42.     container = Container(
43.         "alertmanager",
44.         can_connect=False,
45.         execs={
46.             Exec(["update-ca-certificates", "--fresh"]),
47.             Exec(
48.                 ["alertmanager", "--version"],
49.                 stdout="alertmanager, version 0.23.0 (branch: HEAD, ...",
50.             ),
51.             Exec(["/usr/bin/amtool", "check-config", "/etc/alertmanager/alertmanager.yml"]),
52.         },
53.     )
54.     state = State(config={"config_file": ""}, containers=[container])
55.     peer_rel = PeerRelation("replicas")
56. 
57.     state = context.run(context.on.install(), state)
58. 
59.     state = dataclasses.replace(state, relations=[peer_rel])
60.     state = context.run(context.on.relation_created(peer_rel), state)
61. 
62.     if leader:
63.         state = dataclasses.replace(state, leader=True)
64.         state = context.run(context.on.leader_elected(), state)
65.     else:
66.         state = dataclasses.replace(state, leader=False)
67. 
68.     state = context.run(context.on.config_changed(), state)
69. 
70.     # state = state.with_can_connect("alertmanger")
71.     container = dataclasses.replace(container, can_connect=True)
72.     state = dataclasses.replace(state, containers=[container])
73.     state = context.run(context.on.pebble_ready(container), state)
74. 
75.     state = context.run(context.on.start(), state)
76. 
77.     return state
78. 
79. 
80. def add_relation_sequence(context: Context, state: State, relation: Relation):
81.     """Helper to simulate a relation-added sequence."""
82.     # TODO consider adding to scenario.sequences
83.     state_with_relation = dataclasses.replace(state, relations={*state.relations, relation})
84.     state_after_relation_created = context.run(context.on.relation_created(relation), state_with_relation)
85.     state_after_relation_joined = context.run(context.on.relation_joined(relation), state_after_relation_created)
86.     state_after_relation_changed = context.run(
87.         context.on.relation_changed(state_after_relation_joined.get_relation(relation.id)),
88.         state_after_relation_joined,
89.     )
90.     return state_after_relation_changed
91.
```

</details>


---

<sub>⏱️ 7m 51s</sub>

### ✅ `bash`

**Check where ops.testing.Context comes from**

$ cd /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__relation-data-classes__C3 && source .venv/bin/activate && python3 -c "from ops.testing import Context; import inspect; print(inspect.getfile(Context))"

```
/home/ubuntu/alertmanager-k8s-operator/.venv/lib/python3.12/site-packages/scenario/context.py
<exited with exit code 0>
```


---

<sub>⏱️ 7m 57s</sub>

### ✅ `bash`

**Check scenario Relation class**

$ cd /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__relation-data-classes__C3 && source .venv/bin/activate && python3 -c "from ops.testing import Relation; import inspect; print(inspect.getfile(Relation)); from scenario.state import Relation as SR; print(hasattr(SR, 'load'))"

```
/home/ubuntu/alertmanager-k8s-operator/.venv/lib/python3.12/site-packages/scenario/state.py
False
<exited with exit code 0>
```


---

<sub>⏱️ 8m 12s</sub>

### ✅ `bash`

**Test if scenario Relation has load method**

$ cd /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__relation-data-classes__C3 && source .venv/bin/activate && python3 -c "
from ops.testing import Context, State, PeerRelation, Container, Exec
import ops

class TestCharm(ops.CharmBase):
    META = {'name': 'test', 'peers': {'replicas': {'interface': 'replicas'}}}
    def __init__(self, framework):
        super().__init__(framework)
        self.framework.observe(self.on['replicas'].relation_created, self._on_rel_created)
    def _on_rel_created(self, event):
        pr = self.model.get_relation('replicas')
        print(type(pr))
        print(hasattr(pr, 'load'))

ctx = Context(TestCharm, meta=TestCharm.META)
state = State()
pr = PeerRelation('replicas')
import dataclasses
state = dataclasses.replace(state, relations=[pr])
ctx.run(ctx.on.relation_created(pr), state)
"

```
<class 'ops.model.Relation'>
False
<exited with exit code 0>
```


---

<sub>⏱️ 8m 20s</sub>

### ✅ `bash`

**Check ops version and Relation.load in venv**

$ cd /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__relation-data-classes__C3 && source .venv/bin/activate && python3 -c "import ops; print(ops.__version__); from ops.model import Relation; print(hasattr(Relation, 'load'))"

```
2.21.1
False
<exited with exit code 0>
```


---

<sub>⏱️ 8m 29s</sub>

### ✅ `bash`

**Check ops version in uv.lock**

$ cd /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__relation-data-classes__C3 && grep -A 5 '^\[\[package\]\]' uv.lock | grep -A 5 'name = "ops"' | head -20

<details>
<summary>21 lines</summary>

```
{ name = "ops" },
--
[[package]]
name = "coverage"
version = "7.6.1"
source = { registry = "https://pypi.org/simple" }
--
name = "ops"
version = "2.21.1"
source = { registry = "https://pypi.org/simple" }
dependencies = [
    { name = "importlib-metadata", version = "8.5.0", source = { registry = "https://pypi.org/simple" }, marker = "python_full_version < '3.9'" },
--
--
    { name = "ops" },
--
[[package]]
name = "orderly-set"
version = "5.4.1"
source = { registry = "https://pypi.org/simple" }
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 8m 29s</sub>

### ✅ `bash`

**Check ops in uv.lock**

$ grep -A 3 'name = "ops"' /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__relation-data-classes__C3/uv.lock | head -20

<details>
<summary>21 lines</summary>

```
{ name = "ops" },
    { name = "pydantic", version = "2.10.6", source = { registry = "https://pypi.org/simple" }, marker = "python_full_version < '3.9'" },
    { name = "pydantic", version = "2.11.5", source = { registry = "https://pypi.org/simple" }, marker = "python_full_version >= '3.9'" },
    { name = "pyyaml" },
--
    { name = "ops", extra = ["testing"] },
    { name = "pyright" },
    { name = "pytest" },
    { name = "pytest-httpserver", version = "1.1.1", source = { registry = "https://pypi.org/simple" }, marker = "python_full_version < '3.9'" },
--
    { name = "ops" },
    { name = "ops", extras = ["testing"], marker = "extra == 'dev'" },
    { name = "pydantic", specifier = ">=2" },
    { name = "pyright", marker = "extra == 'dev'", specifier = "<1.1.399" },
    { name = "pytest", marker = "extra == 'dev'" },
--
    { name = "ops" },
    { name = "pydantic", version = "2.10.6", source = { registry = "https://pypi.org/simple" }, marker = "python_full_version < '3.9'" },
    { name = "pydantic", version = "2.11.5", source = { registry = "https://pypi.org/simple" }, marker = "python_full_version >= '3.9'" },
    { name = "pyyaml" },
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 8m 39s</sub>

### 💬 Copilot

The venv has ops 2.21.1 which doesn't have `load`/`save`. I need to upgrade ops to ≥2.23.0:

---

<sub>⏱️ 8m 39s</sub>

### ✅ `edit`

**/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__relation-data-classes__C3/pyproject.toml**

/tmp/ops-upgrade-experiment/alertmanager-k8s-operator__relation-data-classes__C3/pyproject.toml

```
File /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__relation-data-classes__C3/pyproject.toml updated with changes.
```


---

<sub>⏱️ 8m 45s</sub>

### ✅ `bash`

**Update uv.lock**

$ cd /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__relation-data-classes__C3 && source .venv/bin/activate && uv lock 2>&1 | tail -5

```
warning: The `requires-python` specifier (`~=3.8`) in `alertmanager-k8s` uses the tilde specifier (`~=`) without a patch version. This will be interpreted as `>=3.8, <4`. Did you mean `~=3.8.0` to constrain the version as `>=3.8.0, <3.9`? We recommend only using the tilde specifier with a patch version to avoid ambiguity.
Resolved 146 packages in 1.13s
Updated ops v2.21.1 -> v2.23.2, v3.6.0
Updated ops-scenario v7.21.1 -> v7.23.2, v8.6.0
<exited with exit code 0>
```


---

<sub>⏱️ 8m 50s</sub>

### ✅ `bash`

**Sync venv with updated lockfile**

$ cd /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__relation-data-classes__C3 && source .venv/bin/activate && uv sync --extra dev 2>&1 | tail -10

<details>
<summary>10 lines</summary>

```
warning: The `requires-python` specifier (`~=3.8`) in `alertmanager-k8s` uses the tilde specifier (`~=`) without a patch version. This will be interpreted as `>=3.8, <4`. Did you mean `~=3.8.0` to constrain the version as `>=3.8.0, <3.9`? We recommend only using the tilde specifier with a patch version to avoid ambiguity.
warning: `VIRTUAL_ENV=/home/ubuntu/alertmanager-k8s-operator/.venv` does not match the project environment path `.venv` and will be ignored; use `--active` to target the active environment instead
Resolved 146 packages in 0.64ms
Uninstalled 2 packages in 1ms
Installed 2 packages in 2ms
 - ops==2.21.1
 + ops==3.6.0
 - ops-scenario==7.21.1
 + ops-scenario==8.6.0
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 8m 56s</sub>

### ✅ `bash`

**Check ops version in project venv**

$ cd /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__relation-data-classes__C3 && .venv/bin/python3 -c "import ops; print(ops.__version__)"

```
3.6.0
<exited with exit code 0>
```


---

<sub>⏱️ 9m 3s</sub>

### ✅ `bash`

**Verify Relation.load/save available**

$ cd /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__relation-data-classes__C3 && .venv/bin/python3 -c "from ops.model import Relation; print(hasattr(Relation, 'load'), hasattr(Relation, 'save'))"

```
True True
<exited with exit code 0>
```


---

<sub>⏱️ 9m 8s</sub>

### 💬 Copilot

Now run the tests again:

---

<sub>⏱️ 10m 58s</sub>

### ✅ `bash`

**Run unit tests with new ops version**

$ cd /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__relation-data-classes__C3 && PYTHONPATH=lib:src .venv/bin/python3 -m pytest tests/unit/ -x -q --tb=short 2>&1 | tail -20

<details>
<summary>17 lines</summary>

```
tests/unit/test_remote_configuration_requirer.py::TestAlertmanagerRemoteConfigurationRequirer::test_templates_pushed_to_relation_data_bag_are_saved_to_templates_file_in_alertmanager
tests/unit/test_remote_configuration_requirer.py::TestAlertmanagerRemoteConfigurationRequirer::test_valid_config_pushed_to_relation_data_bag_updates_alertmanager_config
  /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__relation-data-classes__C3/tests/unit/test_remote_configuration_requirer.py:52: PendingDeprecationWarning: Harness is deprecated. For the recommended approach, see: https://documentation.ubuntu.com/ops/latest/howto/write-unit-tests-for-a-charm/
    self.harness = testing.Harness(AlertmanagerCharm)

tests/unit/test_self_scrape_jobs.py::TestWithInitialHooks::test_self_scraping_job_with_no_peers
tests/unit/test_self_scrape_jobs.py::TestWithInitialHooks::test_self_scraping_job_with_peers
  /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__relation-data-classes__C3/tests/unit/test_self_scrape_jobs.py:22: PendingDeprecationWarning: Harness is deprecated. For the recommended approach, see: https://documentation.ubuntu.com/ops/latest/howto/write-unit-tests-for-a-charm/
    self.harness = Harness(AlertmanagerCharm)

tests/unit/test_self_scrape_jobs.py::TestWithInitialHooks::test_self_scraping_job_with_peers
  /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__relation-data-classes__C3/.venv/lib/python3.12/site-packages/ops/_private/harness.py:1109: UserWarning: Remote unit name invalid: the remote application of replicas is called 'alertmanager-k8s'; the remote unit name should be alertmanager-k8s/<some-number>, not 'am/1'.
    warnings.warn(

tests/unit/test_self_scrape_jobs.py::TestWithInitialHooks::test_self_scraping_job_with_peers
  /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__relation-data-classes__C3/.venv/lib/python3.12/site-packages/ops/_private/harness.py:1109: UserWarning: Remote unit name invalid: the remote application of replicas is called 'alertmanager-k8s'; the remote unit name should be alertmanager-k8s/<some-number>, not 'am/2'.
    warnings.warn(

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
====== 57 passed, 3 skipped, 4 xfailed, 311 warnings in 102.37s (0:01:42) ======
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 11m 3s</sub>

### 💬 Copilot

All 57 tests pass. Let me verify the final state of the changes:

---

<sub>⏱️ 11m 3s</sub>

### ✅ `bash`

**Show changed files**

$ cd /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__relation-data-classes__C3 && git diff --stat

```
pyproject.toml |  2 +-
 src/charm.py   | 28 ++++++++++++++++++++++++----
 uv.lock        | 93 ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++-------------------
 3 files changed, 99 insertions(+), 24 deletions(-)
<exited with exit code 0>
```


---

<sub>⏱️ 11m 37s</sub>

### ✅ `bash`

**Show code changes**

$ cd /tmp/ops-upgrade-experiment/alertmanager-k8s-operator__relation-data-classes__C3 && git diff src/charm.py pyproject.toml

<details>
<summary>72 lines</summary>

```diff
diff --git a/pyproject.toml b/pyproject.toml
index 140d222..7fc19ad 100644
--- a/pyproject.toml
+++ b/pyproject.toml
@@ -6,7 +6,7 @@ version = "0.0"
 requires-python = "~=3.8"
 
 dependencies = [
-  "ops",
+  "ops>=2.23.0",
   "pyyaml",
   "lightkube>=0.11",  # observability_libs
   "lightkube-models",  # observability_libs
diff --git a/src/charm.py b/src/charm.py
index ae92826..401df25 100755
--- a/src/charm.py
+++ b/src/charm.py
@@ -4,15 +4,18 @@
 
 """A Juju charm for alertmanager."""
 
+import json
 import logging
 import socket
 import subprocess
 from dataclasses import dataclass
 from pathlib import Path
 from types import SimpleNamespace
-from typing import List, Optional, Tuple, cast
+from typing import Any, List, Optional, Tuple, cast
 from urllib.parse import urlparse
 
+import pydantic
+
 import yaml
 from charms.alertmanager_k8s.v0.alertmanager_remote_configuration import (
     RemoteConfigurationRequirer,
@@ -60,6 +63,20 @@ from config_builder import ConfigBuilder, ConfigError
 logger = logging.getLogger(__name__)
 
 
+class PeerRelationUnitData(pydantic.BaseModel):
+    """Typed data for the replicas peer relation (per-unit databag)."""
+
+    private_address: Optional[str] = None
+
+
+def _decode_relation_str(v: str) -> Any:
+    """Decode a relation data value, falling back to the raw string if not valid JSON."""
+    try:
+        return json.loads(v)
+    except json.JSONDecodeError:
+        return v
+
+
 @dataclass
 class TLSConfig:
     """TLS configuration received by the charm over the `certificates` relation."""
@@ -507,7 +524,9 @@ class AlertmanagerCharm(CharmBase):
             # Could have simply used `socket.getfqdn()` here and add the path when reading this
             # relation data, but this way it is more future-proof in case we change from ingress
             # per app to ingress per unit.
-            self.peer_relation.data[self.unit]["private_address"] = self._internal_url
+            self.peer_relation.save(
+                PeerRelationUnitData(private_address=self._internal_url), self.unit
+            )
 
         self.karma_provider.target = self._external_url
 
@@ -616,8 +635,9 @@ class AlertmanagerCharm(CharmBase):
             addresses.append(self._internal_url)
         if pr := self.peer_relation:
             for unit in pr.units:  # pr.units only holds peers (self.unit is not included)
-                if address := pr.data[unit].get("private_address"):
-                    addresses.append(address)
+                data = pr.load(PeerRelationUnitData, unit, decoder=_decode_relation_str)
+                if data.private_address:
+                    addresses.append(data.private_address)
 
:
<command with shellId: 37 is still running after 30 seconds. The command is still running. Check the output above - if it looks like the command is waiting for input, use write_bash to provide it. Otherwise, use read_bash to continue waiting for output, or stop_bash to stop it.>
```

</details>


---

<sub>⏱️ 11m 42s</sub>

### ✅ `write_bash`

<details>
<summary>Arguments</summary>

```json
{
  "shellId": "37",
  "input": "q",
  "delay": 3
}
```

</details>

<details>
<summary>72 lines</summary>

```diff
diff --git a/pyproject.toml b/pyproject.toml
index 140d222..7fc19ad 100644
--- a/pyproject.toml
+++ b/pyproject.toml
@@ -6,7 +6,7 @@ version = "0.0"
 requires-python = "~=3.8"
 
 dependencies = [
-  "ops",
+  "ops>=2.23.0",
   "pyyaml",
   "lightkube>=0.11",  # observability_libs
   "lightkube-models",  # observability_libs
diff --git a/src/charm.py b/src/charm.py
index ae92826..401df25 100755
--- a/src/charm.py
+++ b/src/charm.py
@@ -4,15 +4,18 @@
 
 """A Juju charm for alertmanager."""
 
+import json
 import logging
 import socket
 import subprocess
 from dataclasses import dataclass
 from pathlib import Path
 from types import SimpleNamespace
-from typing import List, Optional, Tuple, cast
+from typing import Any, List, Optional, Tuple, cast
 from urllib.parse import urlparse
 
+import pydantic
+
 import yaml
 from charms.alertmanager_k8s.v0.alertmanager_remote_configuration import (
     RemoteConfigurationRequirer,
@@ -60,6 +63,20 @@ from config_builder import ConfigBuilder, ConfigError
 logger = logging.getLogger(__name__)
 
 
+class PeerRelationUnitData(pydantic.BaseModel):
+    """Typed data for the replicas peer relation (per-unit databag)."""
+
+    private_address: Optional[str] = None
+
+
+def _decode_relation_str(v: str) -> Any:
+    """Decode a relation data value, falling back to the raw string if not valid JSON."""
+    try:
+        return json.loads(v)
+    except json.JSONDecodeError:
+        return v
+
+
 @dataclass
 class TLSConfig:
     """TLS configuration received by the charm over the `certificates` relation."""
@@ -507,7 +524,9 @@ class AlertmanagerCharm(CharmBase):
             # Could have simply used `socket.getfqdn()` here and add the path when reading this
             # relation data, but this way it is more future-proof in case we change from ingress
             # per app to ingress per unit.
-            self.peer_relation.data[self.unit]["private_address"] = self._internal_url
+            self.peer_relation.save(
+                PeerRelationUnitData(private_address=self._internal_url), self.unit
+            )
 
         self.karma_provider.target = self._external_url
 
@@ -616,8 +635,9 @@ class AlertmanagerCharm(CharmBase):
             addresses.append(self._internal_url)
         if pr := self.peer_relation:
             for unit in pr.units:  # pr.units only holds peers (self.unit is not included)
-                if address := pr.data[unit].get("private_address"):
-                    addresses.append(address)
+                data = pr.load(PeerRelationUnitData, unit, decoder=_decode_relation_str)
+                if data.private_address:
+                    addresses.append(data.private_address)
 
:
<command with id: 37 exited with exit code 0>
```

</details>


---

<sub>⏱️ 11m 54s</sub>

### 💬 Copilot

The changes are clean and all tests pass. Here's a summary of what was done:

**Changes made:**

1. **`pyproject.toml`**: Added minimum version constraint `ops\>=2.23.0` to enable use of the new typed relation data API.

2. **`uv.lock`**: Updated by `uv lock` to reflect the new dependency constraint (ops upgraded from 2.21.1 → 3.6.0).

3. **`src/charm.py`**:
   - Added imports: `json`, `pydantic`, `Any`
   - Added `PeerRelationUnitData(pydantic.BaseModel)` — a typed model for the `replicas` peer relation's per-unit databag, with an optional `private_address` field
   - Added `_decode_relation_str()` — a backward-compatible decoder that tries `json.loads` first, falling back to the raw string (handles both plain strings from older charm versions and JSON-encoded strings written by `Relation.save()`)
   - Replaced `self.peer_relation.data[self.unit]["private_address"] = ...` with `self.peer_relation.save(PeerRelationUnitData(private_address=...), self.unit)`
   - Replaced `pr.data[unit].get("private_address")` with `pr.load(PeerRelationUnitData, unit, decoder=_decode_relation_str)`, accessing the typed `data.private_address` field

---

<sub>⏱️ 11m 54s</sub>

### ✅ `task_complete`

**Updated the alertmanager-k8s charm to use typed relation data classes (ops 2.23.0+ feature), following the hive-metastore-k8s-operator pattern:

1. **`pyproject.toml`**: Added `ops>=2.23.0` minimum version constraint.
2. **`uv.lock`**: Updated via `uv lock` (ops upgraded to 3.6.0).
3. **`src/charm.py`**:
   - Added `PeerRelationUnitData(pydantic.BaseModel)` with an `Optional[str]` `private_address` field for the peer relation unit databag.
   - Added `_decode_relation_str()` backward-compatible decoder (tries `json.loads`, falls back to raw string).
   - Write path: replaced raw dict assignment with `Relation.save(PeerRelationUnitData(...), self.unit)`.
   - Read path: replaced `.data[unit].get("private_address")` with `Relation.load(PeerRelationUnitData, unit, decoder=_decode_relation_str)`.

All 57 unit tests pass.**

<details>
<summary>Arguments</summary>

```json
{
  "summary": "Updated the alertmanager-k8s charm to use typed relation data classes (ops 2.23.0+ feature), following the hive-metastore-k8s-operator pattern:\n\n1. **`pyproject.toml`**: Added `ops>=2.23.0` minimum version constraint.\n2. **`uv.lock`**: Updated via `uv lock` (ops upgraded to 3.6.0).\n3. **`src/charm.py`**:\n   - Added `PeerRelationUnitData(pydantic.BaseModel)` with an `Optional[str]` `private_address` field for the peer relation unit databag.\n   - Added `_decode_relation_str()` backward-compatible decoder (tries `json.loads`, falls back to raw string).\n   - Write path: replaced raw dict assignment with `Relation.save(PeerRelationUnitData(...), self.unit)`.\n   - Read path: replaced `.data[unit].get(\"private_address\")` with `Relation.load(PeerRelationUnitData, unit, decoder=_decode_relation_str)`.\n\nAll 57 unit tests pass."
}
```

</details>

<details>
<summary>9 lines</summary>

```
Updated the alertmanager-k8s charm to use typed relation data classes (ops 2.23.0+ feature), following the hive-metastore-k8s-operator pattern:

1. **`pyproject.toml`**: Added `ops>=2.23.0` minimum version constraint.
2. **`uv.lock`**: Updated via `uv lock` (ops upgraded to 3.6.0).
3. **`src/charm.py`**:
   - Added `PeerRelationUnitData(pydantic.BaseModel)` with an `Optional[str]` `private_address` field for the peer relation unit databag.
   - Added `_decode_relation_str()` backward-compatible decoder (tries `json.loads`, falls back to raw string).
   - Write path: replaced raw dict assignment with `Relation.save(PeerRelationUnitData(...), self.unit)`.
   - Read path: replaced `.data[unit].get("private_address")` with `Relation.load(PeerRelationUnitData, unit, decoder=_decode_relation_str)`.

All 57 unit tests pass.
```

</details>


---

<sub>⏱️ 11m 59s</sub>

### ℹ️ Info

Response was interrupted due to a server error. Retrying...

---

<sub>⏱️ 12m 4s</sub>

### ℹ️ Info

Response was interrupted due to a server error. Retrying...

---

<sub>⏱️ 12m 8s</sub>

### ℹ️ Info

Response was interrupted due to a server error. Retrying...

---

<sub>⏱️ 12m 13s</sub>

### ℹ️ Info

Response was interrupted due to a server error. Retrying...

---

<sub>⏱️ 12m 17s</sub>

### ℹ️ Info

Response was interrupted due to a server error. Retrying...

---

<sub>⏱️ 12m 23s</sub>

### ❌ Error

Execution failed: Error: Failed to get response from the AI model; retried 5 times (total retry wait time: 6.213582230052731 seconds) Last error: Unknown error

---

<sub>Generated by [GitHub Copilot CLI](https://github.com/features/copilot/cli)</sub>
