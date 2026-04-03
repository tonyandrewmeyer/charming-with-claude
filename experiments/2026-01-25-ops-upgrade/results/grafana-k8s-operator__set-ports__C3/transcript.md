# 🤖 Copilot CLI Session

> [!NOTE]
> - **Session ID:** `c5e734bf-bd92-4571-900a-223b1ffa2f79`  
> - **Started:** 4/3/2026, 7:09:33 AM  
> - **Duration:** 2m 35s  
> - **Exported:** 4/3/2026, 7:12:09 AM  

---

<sub>⏱️ 5s</sub>

### 👤 User

ops 2.7.0 added a declarative Unit.set_ports() API that replaces the imperative open_port()/close_port() pattern. Instead of tracking which ports to open and close individually, charms declare the full set of desired ports and ops handles the diff. The charm at https://github.com/canonical/minio-operator already uses this feature -- look at how they did it and update this charm similarly.

---

<sub>⏱️ 17s</sub>

### 📦 task (Completed)

### ✅ `github-mcp-server-get_file_contents`

**/**

<details>
<summary>Arguments</summary>

```json
{
  "owner": "canonical",
  "repo": "minio-operator",
  "path": "/"
}
```

</details>

```
[{"type":"dir","size":0,"name":".github","path":".github","sha":"acd63bb089aac4e8cea4a7cc9a134c9d62debfd8","url":"https://api.github.com/repos/canonical/minio-operator/contents/.github?ref=42a875c5cefce5bc57e7acd7152d5db725faf400","git_url":"https://api.github.com/repos/canonical/minio-operator/git/trees/acd63bb089aac4e8cea4a7cc9a134c9d62debfd8","html_url":"https://github.com/canonical/minio-operator/tree/42a875c5cefce5bc57e7acd7152d5db725faf400/.github"},{"type":"file","size":113,"name":".gitignore","path":".gitignore","sha":"e342a9acb405a144a89b548b56753fe09bed327c","url":"https://api.github.com/repos/canonical/minio-operator/contents/.gitignore?ref=42a875c5cefce5bc57e7acd7152d5db725faf400","git_url":"https://api.github.com/repos/canonical/minio-operator/git/blobs/e342a9acb405a144a89b548b56753fe09bed327c","html_url":"https://github.com/canonical/minio-operator/blob/42a875c5cefce5bc57e7acd7152d5db725faf400/.gitignore","download_url":"https://raw.githubusercontent.com/canonical/minio-operator/42a875c5cefce5bc57e7acd7152d5db725faf400/.gitignore"},{"type":"file","size":28,"name":"CODEOWNERS","path":"CODEOWNERS","sha":"b0115c112195dc4657cbb731e82fed6db4de8dc9","url":"https://api.github.com/repos/canonical/minio-operator/contents/CODEOWNERS?ref=42a875c5cefce5bc57e7acd7152d5db725faf400","git_url":"https://api.github.com/repos/canonical/minio-operator/git/blobs/b0115c112195dc4657cbb731e82fed6db4de8dc9","html_url":"https://github.com/canonical/minio-operator/blob/42a875c5cefce5bc57e7acd7152d5db725faf400/CODEOWNERS","download_url":"https://raw.githubusercontent.com/canonical/minio-operator/42a875c5cefce5bc57e7acd7152d5db725faf400/CODEOWNERS"},{"type":"file","size":4286,"name":"CONTRIBUTING.md","path":"CONTRIBUTING.md","sha":"77b445f090b9a18203456bc3b8097030b054654c","url":"https://api.github.com/repos/canonical/minio-operator/contents/CONTRIBUTING.md?ref=42a875c5cefce5bc57e7acd7152d5db725faf400","git_url":"https://api.github.com/repos/canonical/minio-operator/git/blobs/77b445f090b9a18203456bc3b8097030b054654c","html_url":"https://github.com/canonical/minio-operator/blob/42a875c5cefce5bc57e7acd7152d5db725faf400/CONTRIBUTING.md","download_url":"https://raw.githubusercontent.com/canonical/minio-operator/42a875c5cefce5bc57e7acd7152d5db725faf400/CONTRIBUTING.md"},{"type":"file","size":11357,"name":"LICENSE","path":"LICENSE","sha":"261eeb9e9f8b2b4b0d119366dda99c6fd7d35c64","url":"https://api.github.com/repos/canonical/minio-operator/contents/LICENSE?ref=42a875c5cefce5bc57e7acd7152d5db725faf400","git_url":"https://api.github.com/repos/canonical/minio-operator/git/blobs/261eeb9e9f8b2b4b0d119366dda99c6fd7d35c64","html_url":"https://github.com/canonical/minio-operator/blob/42a875c5cefce5bc57e7acd7152d5db725faf400/LICENSE","download_url":"https://raw.githubusercontent.com/canonical/minio-operator/42a875c5cefce5bc57e7acd7152d5db725faf400/LICENSE"},{"type":"file","size":2791,"name":"README.md","path":"README.md","sha":"d563e83ff4747cabbf7444073e4011dcadd72069","url":"https://api.github.com/repos/canonical/minio-operator/contents/README.md?ref=42a875c5cefce5bc57e7acd7152d5db725faf400","git_url":"https://api.github.com/repos/canonical/minio-operator/git/blobs/d563e83ff4747cabbf7444073e4011dcadd72069","html_url":"https://github.com/canonical/minio-operator/blob/42a875c5cefce5bc57e7acd7152d5db725faf400/README.md","download_url":"https://raw.githubusercontent.com/canonical/minio-operator/42a875c5cefce5bc57e7acd7152d5db725faf400/README.md"},{"type":"file","size":4497,"name":"charmcraft.yaml","path":"charmcraft.yaml","sha":"b1c6bf36390e9eb8dc2d41083847300c65948566","url":"https://api.github.com/repos/canonical/minio-operator/contents/charmcraft.yaml?ref=42a875c5cefce5bc57e7acd7152d5db725faf400","git_url":"https://api.github.com/repos/canonical/minio-operator/git/blobs/b1c6bf36390e9eb8dc2d41083847300c65948566","html_url":"https://github.com/canonical/minio-operator/blob/42a875c5cefce5bc57e7acd7152d5db725faf400/charmcraft.yaml","download_url":"https://raw.githubusercontent.com/canonical/minio-operator/42a875c5cefce5bc57e7acd7152d5db725faf400/charmcraft.yaml"},{"type":"file","size":510,"name":"concierge.yaml","path":"concierge.yaml","sha":"43e723a2a57a815e347b4427abda9f52d5a0c2f2","url":"https://api.github.com/repos/canonical/minio-operator/contents/concierge.yaml?ref=42a875c5cefce5bc57e7acd7152d5db725faf400","git_url":"https://api.github.com/repos/canonical/minio-operator/git/blobs/43e723a2a57a815e347b4427abda9f52d5a0c2f2","html_url":"https://github.com/canonical/minio-operator/blob/42a875c5cefce5bc57e7acd7152d5db725faf400/concierge.yaml","download_url":"https://raw.githubusercontent.com/canonical/minio-operator/42a875c5cefce5bc57e7acd7152d5db725faf400/concierge.yaml"},{"type":"file","size":1303,"name":"config.yaml","path":"config.yaml","sha":"80e9f1820fcc0972d84fc3ff97590b8ecfc76a85","url":"https://api.github.com/repos/canonical/minio-operator/contents/config.yaml?ref=42a875c5cefce5bc57e7acd7152d5db725faf400","git_url":"https://api.github.com/repos/canonical/minio-operator/git/blobs/80e9f1820fcc0972d84fc3ff97590b8ecfc76a85","html_url":"https://github.com/canonical/minio-operator/blob/42a875c5cefce5bc57e7acd7152d5db725faf400/config.yaml","download_url":"https://raw.githubusercontent.com/canonical/minio-operator/42a875c5cefce5bc57e7acd7152d5db725faf400/config.yaml"},{"type":"file","size":3463,"name":"icon.svg","path":"icon.svg","sha":"db8dfe7616eadb25331c0754ff81f41b4725c5b1","url":"https://api.github.com/repos/canonical/minio-operator/contents/icon.svg?ref=42a875c5cefce5bc57e7acd7152d5db725faf400","git_url":"https://api.github.com/repos/canonical/minio-operator/git/blobs/db8dfe7616eadb25331c0754ff81f41b4725c5b1","html_url":"https://github.com/canonical/minio-operator/blob/42a875c5cefce5bc57e7acd7152d5db725faf400/icon.svg","download_url":"https://raw.githubusercontent.com/canonical/minio-operator/42a875c5cefce5bc57e7acd7152d5db725faf400/icon.svg"},{"type":"dir","size":0,"name":"lib","path":"lib","sha":"fd457db224518ed446a660cedc0e1c9c9dbad4e6","url":"https://api.github.com/repos/canonical/minio-operator/contents/lib?ref=42a875c5cefce5bc57e7acd7152d5db725faf400","git_url":"https://api.github.com/repos/canonical/minio-operator/git/trees/fd457db224518ed446a660cedc0e1c9c9dbad4e6","html_url":"https://github.com/canonical/minio-operator/tree/42a875c5cefce5bc57e7acd7152d5db725faf400/lib"},{"type":"file","size":2383,"name":"metadata.yaml","path":"metadata.yaml","sha":"c58e3c58164654a3ea9811dd65652a88037f04eb","url":"https://api.github.com/repos/canonical/minio-operator/contents/metadata.yaml?ref=42a875c5cefce5bc57e7acd7152d5db725faf400","git_url":"https://api.github.com/repos/canonical/minio-operator/git/blobs/c58e3c58164654a3ea9811dd65652a88037f04eb","html_url":"https://github.com/canonical/minio-operator/blob/42a875c5cefce5bc57e7acd7152d5db725faf400/metadata.yaml","download_url":"https://raw.githubusercontent.com/canonical/minio-operator/42a875c5cefce5bc57e7acd7152d5db725faf400/metadata.yaml"},{"type":"file","size":313706,"name":"poetry.lock","path":"poetry.lock","sha":"2f74c704c0eb77fe110ce245b1d58ed308cc1aee","url":"https://api.github.com/repos/canonical/minio-operator/contents/poetry.lock?ref=42a875c5cefce5bc57e7acd7152d5db725faf400","git_url":"https://api.github.com/repos/canonical/minio-operator/git/blobs/2f74c704c0eb77fe110ce245b1d58ed308cc1aee","html_url":"https://github.com/canonical/minio-operator/blob/42a875c5cefce5bc57e7acd7152d5db725faf400/poetry.lock","download_url":"https://raw.githubusercontent.com/canonical/minio-operator/42a875c5cefce5bc57e7acd7152d5db725faf400/poetry.lock"},{"type":"file","size":2283,"name":"pyproject.toml","path":"pyproject.toml","sha":"e4a9023f3a11627e345f4caef3bcb1224bb0e000","url":"https://api.github.com/repos/canonical/minio-operator/contents/pyproject.toml?ref=42a875c5cefce5bc57e7acd7152d5db725faf400","git_url":"https://api.github.com/repos/canonical/minio-operator/git/blobs/e4a9023f3a11627e345f4caef3bcb1224bb0e000","html_url":"https://github.com/canonical/minio-operator/blob/42a875c5cefce5bc57e7acd7152d5db725faf400/pyproject.toml","download_url":"https://raw.githubusercontent.com/canonical/minio-operator/42a875c5cefce5bc57e7acd7152d5db725faf400/pyproject.toml"},{"type":"file","size":149,"name":"renovate.json","path":"renovate.json","sha":"64e9df108a7e1ed1ad12022a3873728eadd1e697","url":"https://api.github.com/repos/canonical/minio-operator/contents/renovate.json?ref=42a875c5cefce5bc57e7acd7152d5db725faf400","git_url":"https://api.github.com/repos/canonical/minio-operator/git/blobs/64e9df108a7e1ed1ad12022a3873728eadd1e697","html_url":"https://github.com/canonical/minio-operator/blob/42a875c5cefce5bc57e7acd7152d5db725faf400/renovate.json","download_url":"https://raw.githubusercontent.com/canonical/minio-operator/42a875c5cefce5bc57e7acd7152d5db725faf400/renovate.json"},{"type":"dir","size":0,"name":"src","path":"src","sha":"74804e52960167cf89eadd3f29cbbbfcc4269633","url":"https://api.github.com/repos/canonical/minio-operator/contents/src?ref=42a875c5cefce5bc57e7acd7152d5db725faf400","git_url":"https://api.github.com/repos/canonical/minio-operator/git/trees/74804e52960167cf89eadd3f29cbbbfcc4269633","html_url":"https://github.com/canonical/minio-operator/tree/42a875c5cefce5bc57e7acd7152d5db725faf400/src"},{"type":"dir","size":0,"name":"terraform","path":"terraform","sha":"57eb2717c2458ed5ca0d6a5dd673d4b4bad80866","url":"https://api.github.com/repos/canonical/minio-operator/contents/terraform?ref=42a875c5cefce5bc57e7acd7152d5db725faf400","git_url":"https://api.github.com/repos/canonical/minio-operator/git/trees/57eb2717c2458ed5ca0d6a5dd673d4b4bad80866","html_url":"https://github.com/canonical/minio-operator/tree/42a875c5cefce5bc57e7acd7152d5db725faf400/terraform"},{"type":"dir","size":0,"name":"tests","path":"tests","sha":"b4fe6a41d9291df70c8ec9fd1fd09730a613eb42","url":"https://api.github.com/repos/canonical/minio-operator/contents/tests?ref=42a875c5cefce5bc57e7acd7152d5db725faf400","git_url":"https://api.github.com/repos/canonical/minio-operator/git/trees/b4fe6a41d9291df70c8ec9fd1fd09730a613eb42","html_url":"https://github.com/canonical/minio-operator/tree/42a875c5cefce5bc57e7acd7152d5db725faf400/tests"},{"type":"dir","size":0,"name":"tools","path":"tools","sha":"7eb578f867ce9b851624dd212ac6610d9d4bfe7a","url":"https://api.github.com/repos/canonical/minio-operator/contents/tools?ref=42a875c5cefce5bc57e7acd7152d5db725faf400","git_url":"https://api.github.com/repos/canonical/minio-operator/git/trees/7eb578f867ce9b851624dd212ac6610d9d4bfe7a","html_url":"https://github.com/canonical/minio-operator/tree/42a875c5cefce5bc57e7acd7152d5db725faf400/tools"},{"type":"file","size":2530,"name":"tox.ini","path":"tox.ini","sha":"a24a8cced06dc944dd6f1ade04b9c78386256e83","url":"https://api.github.com/repos/canonical/minio-operator/contents/tox.ini?ref=42a875c5cefce5bc57e7acd7152d5db725faf400","git_url":"https://api.github.com/repos/canonical/minio-operator/git/blobs/a24a8cced06dc944dd6f1ade04b9c78386256e83","html_url":"https://github.com/canonical/minio-operator/blob/42a875c5cefce5bc57e7acd7152d5db725faf400/tox.ini","download_url":"https://raw.githubusercontent.com/canonical/minio-operator/42a875c5cefce5bc57e7acd7152d5db725faf400/tox.ini"}]
```


### ✅ `github-mcp-server-search_code`

**set_ports repo:canonical/minio-operator**

<details>
<summary>Arguments</summary>

```json
{
  "query": "set_ports repo:canonical/minio-operator"
}
```

</details>

```
{"total_count":1,"incomplete_results":false,"items":[{"name":"charm.py","path":"src/charm.py","sha":"61055e43490c4ebd78913993c09483a3e2a0da94","html_url":"https://github.com/canonical/minio-operator/blob/42a875c5cefce5bc57e7acd7152d5db725faf400/src/charm.py","repository":{"id":327684699,"node_id":"MDEwOlJlcG9zaXRvcnkzMjc2ODQ2OTk=","owner":{"login":"canonical","id":53057619,"node_id":"MDEyOk9yZ2FuaXphdGlvbjUzMDU3NjE5","avatar_url":"https://avatars.githubusercontent.com/u/53057619?v=4","html_url":"https://github.com/canonical","gravatar_id":"","type":"Organization","site_admin":false,"url":"https://api.github.com/users/canonical","events_url":"https://api.github.com/users/canonical/events{/privacy}","following_url":"https://api.github.com/users/canonical/following{/other_user}","followers_url":"https://api.github.com/users/canonical/followers","gists_url":"https://api.github.com/users/canonical/gists{/gist_id}","organizations_url":"https://api.github.com/users/canonical/orgs","received_events_url":"https://api.github.com/users/canonical/received_events","repos_url":"https://api.github.com/users/canonical/repos","starred_url":"https://api.github.com/users/canonical/starred{/owner}{/repo}","subscriptions_url":"https://api.github.com/users/canonical/subscriptions"},"name":"minio-operator","full_name":"canonical/minio-operator","description":"MinIO Operator","html_url":"https://github.com/canonical/minio-operator","fork":false,"private":false,"url":"https://api.github.com/repos/canonical/minio-operator","archive_url":"https://api.github.com/repos/canonical/minio-operator/{archive_format}{/ref}","assignees_url":"https://api.github.com/repos/canonical/minio-operator/assignees{/user}","blobs_url":"https://api.github.com/repos/canonical/minio-operator/git/blobs{/sha}","branches_url":"https://api.github.com/repos/canonical/minio-operator/branches{/branch}","collaborators_url":"https://api.github.com/repos/canonical/minio-operator/collaborators{/collaborator}","comments_url":"https://api.github.com/repos/canonical/minio-operator/comments{/number}","commits_url":"https://api.github.com/repos/canonical/minio-operator/commits{/sha}","compare_url":"https://api.github.com/repos/canonical/minio-operator/compare/{base}...{head}","contents_url":"https://api.github.com/repos/canonical/minio-operator/contents/{+path}","contributors_url":"https://api.github.com/repos/canonical/minio-operator/contributors","deployments_url":"https://api.github.com/repos/canonical/minio-operator/deployments","downloads_url":"https://api.github.com/repos/canonical/minio-operator/downloads","events_url":"https://api.github.com/repos/canonical/minio-operator/events","forks_url":"https://api.github.com/repos/canonical/minio-operator/forks","git_commits_url":"https://api.github.com/repos/canonical/minio-operator/git/commits{/sha}","git_refs_url":"https://api.github.com/repos/canonical/minio-operator/git/refs{/sha}","git_tags_url":"https://api.github.com/repos/canonical/minio-operator/git/tags{/sha}","hooks_url":"https://api.github.com/repos/canonical/minio-operator/hooks","issue_comment_url":"https://api.github.com/repos/canonical/minio-operator/issues/comments{/number}","issue_events_url":"https://api.github.com/repos/canonical/minio-operator/issues/events{/number}","issues_url":"https://api.github.com/repos/canonical/minio-operator/issues{/number}","keys_url":"https://api.github.com/repos/canonical/minio-operator/keys{/key_id}","labels_url":"https://api.github.com/repos/canonical/minio-operator/labels{/name}","languages_url":"https://api.github.com/repos/canonical/minio-operator/languages","merges_url":"https://api.github.com/repos/canonical/minio-operator/merges","milestones_url":"https://api.github.com/repos/canonical/minio-operator/milestones{/number}","notifications_url":"https://api.github.com/repos/canonical/minio-operator/notifications{?since,all,participating}","pulls_url":"https://api.github.com/repos/canonical/minio-operator/pulls{/number}","releases_url":"https://api.github.com/repos/canonical/minio-operator/releases{/id}","stargazers_url":"https://api.github.com/repos/canonical/minio-operator/stargazers","statuses_url":"https://api.github.com/repos/canonical/minio-operator/statuses/{sha}","subscribers_url":"https://api.github.com/repos/canonical/minio-operator/subscribers","subscription_url":"https://api.github.com/repos/canonical/minio-operator/subscription","tags_url":"https://api.github.com/repos/canonical/minio-operator/tags","trees_url":"https://api.github.com/repos/canonical/minio-operator/git/trees{/sha}","teams_url":"https://api.github.com/repos/canonical/minio-operator/teams"}}]}
```


### ✅ `github-mcp-server-search_code`

**open_port repo:canonical/minio-operator**

<details>
<summary>Arguments</summary>

```json
{
  "query": "open_port repo:canonical/minio-operator"
}
```

</details>

```
{"total_count":0,"incomplete_results":false}
```


### ✅ `github-mcp-server-search_code`

**close_port repo:canonical/minio-operator**

<details>
<summary>Arguments</summary>

```json
{
  "query": "close_port repo:canonical/minio-operator"
}
```

</details>

```
{"total_count":0,"incomplete_results":false}
```


### 💬 Copilot

Good! I found that `set_ports()` is used in `src/charm.py`. Let me get that file and search for all related port APIs more thoroughly:

### ✅ `github-mcp-server-get_file_contents`

**/src**

<details>
<summary>Arguments</summary>

```json
{
  "owner": "canonical",
  "path": "/src",
  "repo": "minio-operator"
}
```

</details>

```
[{"type":"file","size":10168,"name":"charm.py","path":"src/charm.py","sha":"61055e43490c4ebd78913993c09483a3e2a0da94","url":"https://api.github.com/repos/canonical/minio-operator/contents/src/charm.py?ref=42a875c5cefce5bc57e7acd7152d5db725faf400","git_url":"https://api.github.com/repos/canonical/minio-operator/git/blobs/61055e43490c4ebd78913993c09483a3e2a0da94","html_url":"https://github.com/canonical/minio-operator/blob/42a875c5cefce5bc57e7acd7152d5db725faf400/src/charm.py","download_url":"https://raw.githubusercontent.com/canonical/minio-operator/42a875c5cefce5bc57e7acd7152d5db725faf400/src/charm.py"},{"type":"dir","size":0,"name":"components","path":"src/components","sha":"4380c98e460fc41e192e083c6890aad586dd81b3","url":"https://api.github.com/repos/canonical/minio-operator/contents/src/components?ref=42a875c5cefce5bc57e7acd7152d5db725faf400","git_url":"https://api.github.com/repos/canonical/minio-operator/git/trees/4380c98e460fc41e192e083c6890aad586dd81b3","html_url":"https://github.com/canonical/minio-operator/tree/42a875c5cefce5bc57e7acd7152d5db725faf400/src/components"},{"type":"dir","size":0,"name":"grafana_dashboards","path":"src/grafana_dashboards","sha":"6e37bc9a4a71250fbdbc758ba912ad71266ec9e8","url":"https://api.github.com/repos/canonical/minio-operator/contents/src/grafana_dashboards?ref=42a875c5cefce5bc57e7acd7152d5db725faf400","git_url":"https://api.github.com/repos/canonical/minio-operator/git/trees/6e37bc9a4a71250fbdbc758ba912ad71266ec9e8","html_url":"https://github.com/canonical/minio-operator/tree/42a875c5cefce5bc57e7acd7152d5db725faf400/src/grafana_dashboards"},{"type":"dir","size":0,"name":"prometheus_alert_rules","path":"src/prometheus_alert_rules","sha":"19693133b586c7ba8ec31af00d321ef0555ec915","url":"https://api.github.com/repos/canonical/minio-operator/contents/src/prometheus_alert_rules?ref=42a875c5cefce5bc57e7acd7152d5db725faf400","git_url":"https://api.github.com/repos/canonical/minio-operator/git/trees/19693133b586c7ba8ec31af00d321ef0555ec915","html_url":"https://github.com/canonical/minio-operator/tree/42a875c5cefce5bc57e7acd7152d5db725faf400/src/prometheus_alert_rules"}]
```


### ✅ `github-mcp-server-get_file_contents`

**/src/charm.py**

<details>
<summary>Arguments</summary>

```json
{
  "owner": "canonical",
  "path": "/src/charm.py",
  "repo": "minio-operator"
}
```

</details>

<details>
<summary>233 lines</summary>

```
successfully downloaded text file (SHA: 61055e43490c4ebd78913993c09483a3e2a0da94)#!/usr/bin/env python3
# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

import logging
from random import choices
from string import ascii_uppercase, digits
from typing import List, Optional

from charmed_kubeflow_chisme.components import (
    CharmReconciler,
    LazyContainerFileTemplate,
    LeadershipGateComponent,
    SdiRelationBroadcasterComponent,
)
from charmed_kubeflow_chisme.exceptions import ErrorWithStatus
from charms.grafana_k8s.v0.grafana_dashboard import GrafanaDashboardProvider
from charms.prometheus_k8s.v0.prometheus_scrape import MetricsEndpointProvider
from charms.velero_libs.v0.velero_backup_config import VeleroBackupProvider, VeleroBackupSpec
from lightkube.models.core_v1 import ServicePort
from ops import BlockedStatus, CharmBase, StoredState, main

from components.owasp_logging import OWASPLoggerComponent
from components.pebble_component import MinIOInputs, MinIOPebbleService
from components.service_component import KubernetesServicePatchComponent
from components.service_mesh_component import ServiceMeshComponent

logger = logging.getLogger(__name__)


class MinIOOperator(CharmBase):
    _stored = StoredState()

    def __init__(self, *args):
        super().__init__(*args)
        try:
            minio_args = self._get_minio_args()
            secret_key = self._get_secret_key()
        except ErrorWithStatus as e:
            self.unit.status = e.status
            return

        self.model.unit.set_ports(
            int(self.model.config["port"]),
            int(self.model.config["console-port"]),
        )

        self.charm_reconciler = CharmReconciler(self)

        self.leadership_gate = self.charm_reconciler.add(
            component=LeadershipGateComponent(
                charm=self,
                name="leadership-gate",
            ),
            depends_on=[],
        )

        self.service_mesh = self.charm_reconciler.add(
            component=ServiceMeshComponent(charm=self, name="service-mesh"),
            depends_on=[self.leadership_gate],
        )

        self.owasp_logger = self.charm_reconciler.add(
            component=OWASPLoggerComponent(charm=self, stored=self._stored),
            depends_on=[self.leadership_gate],
        )

        self.service_patcher = self.charm_reconciler.add(
            component=KubernetesServicePatchComponent(
                charm=self,
                name="kubernetes-service-patch",
                ports=[
                    ServicePort(int(self.model.config["port"]), name="minio"),
                    ServicePort(int(self.model.config["console-port"]), name="minio-console"),
                ],
            ),
            depends_on=[self.leadership_gate],
        )

        self.object_storage_relation = self.charm_reconciler.add(
            component=SdiRelationBroadcasterComponent(
                charm=self,
                name="relation:object_storage",
                relation_name="object-storage",
                data_to_send={
                    "port": self.model.config["port"],
                    "secure": False,
                    "access-key": self.model.config["access-key"],
                    "secret-key": secret_key,
                    "namespace": self.model.name,
                    "service": self.model.app.name,
                },
            ),
            depends_on=[self.leadership_gate, self.service_patcher],
        )

        self.minio_container = self.charm_reconciler.add(
            component=MinIOPebbleService(
                charm=self,
                name="container:minio",
                container_name="minio",
                service_name="minio",
                files_to_push=self._get_files_to_push(),
                inputs_getter=lambda: MinIOInputs(
                    MINIO_ARGS=minio_args,
                    MINIO_ROOT_USER=self.model.config["access-key"],
                    MINIO_ROOT_PASSWORD=secret_key,
                    MINIO_PORT=int(self.model.config["port"]),
                ),
            ),
            depends_on=[
                self.leadership_gate,
                self.service_patcher,
                self.object_storage_relation,
            ],
        )

        self.prometheus_provider = MetricsEndpointProvider(
            charm=self,
            jobs=[
                {
                    "job_name": "minio_metrics",
                    "scrape_interval": "30s",
                    "metrics_path": "/minio/v2/metrics/cluster",
                    "static_configs": [{"targets": [f"*:{self.model.config['port']}"]}],
                }
            ],
        )
        self.velero_backup_config = VeleroBackupProvider(
            charm=self,
            relation_name="velero-backup-config",
            spec=VeleroBackupSpec(
                include_namespaces=[self.model.name],
                include_resources=["persistentvolumeclaims", "persistentvolumes"],
                label_selector={
                    "app.kubernetes.io/name": self.app.name,
                },
            ),
        )
        self.dashboard_provider = GrafanaDashboardProvider(self)

        self.charm_reconciler.install_default_event_handlers()

    def _get_minio_args(self) -> List[str]:
        """
        Build command line arguments for MinIO based on configuration mode.

        Returns:
            List[str]: Command line arguments for MinIO

        Raises:
            ErrorWithStatus: If mode is invalid or required configurations are missing
        """
        model_mode = self.model.config.get("mode")

        if model_mode == "server":
            return self._with_console_address(
                ["server", "/data", "--certs-dir", "/minio/.minio/certs"]
            )
        elif model_mode == "gateway":
            return self._with_console_address(self._get_minio_args_gateway())

        error_msg = f"Invalid mode '{model_mode}'. Supported values: 'server', 'gateway'"
        logger.error(error_msg)
        raise ErrorWithStatus(error_msg, BlockedStatus)

    def _with_console_address(self, minio_args: List[str]) -> List[str]:
        """
        Append console address configuration to MinIO arguments.

        Args:
            minio_args (List[str]): Existing MinIO command line arguments

        Returns:
            List[str]: Updated command line arguments with console address
        """
        console_port = self.model.config["console-port"]
        return [*minio_args, "--console-address", f":{console_port}"]

    def _get_minio_args_gateway(self) -> List[str]:
        """
        Build command line arguments for MinIO in gateway mode.

        Returns:
            List[str]: Command line arguments for MinIO in gateway mode

        Raises:
            ErrorWithStatus: If required gateway configuration is missing
        """
        storage = self.model.config.get("gateway-storage-service")
        if not storage and storage not in ["s3", "azure"]:
            raise ErrorWithStatus(
                "MinIO gateway mode requires 'gateway-storage-service' configuration. "
                "Supported values: 's3', 'azure'",
                BlockedStatus,
            )

        logger.debug(f"MinIO gateway mode configured for: {storage}")
        endpoint = self.model.config.get("storage-service-endpoint")

        if endpoint:
            return ["gateway", storage, endpoint]
        return ["gateway", storage]

    def _get_secret_key(self) -> str:
        """
        Get the secret key for MinIO from the model configuration or stored state.
        Returns:
            str: The secret key to be used by MinIO
        Raises:
            ErrorWithStatus: If the secret key is too short
        """
        config_secret = self.model.config.get("secret-key")
        if config_secret:
            if len(config_secret) < 8:
                raise ErrorWithStatus(
                    "The 'secret-key' config value must be at least 8 characters long.",
                    BlockedStatus,
                )
            secret = config_secret
        else:
            try:
                secret = self._stored.secret_key
                logger.info("Using existing secret key from stored state.")
            except AttributeError:
                logger.debug("No secret key provided in config, generating a new one.")
                secret = "".join(choices(ascii_uppercase + digits, k=30))
                self._stored.set_default(secret_key=secret)

        return secret

    def _get_files_to_push(self) -> Optional[List[LazyContainerFileTemplate]]:
        """
        Get the list of files to push to the MinIO container.
        This includes SSL certificate files if configured for MinIO to use secure connections.

        Returns:
            List[ContainerFileTemplate]: List of files to be pushed
        """
        files: LazyContainerFileTemplate = []
        if self.model.config.get("ssl-key") and self.model.config.get("ssl-cert"):
            ssl_config = [
                LazyContainerFileTemplate(
                    source_template=self.model.config["ssl-key"],
                    destination_path="/minio/.minio/certs/private.key",
                    permissions=0o511,
                ),
                LazyContainerFileTemplate(
                    source_template=self.model.config["ssl-cert"],
                    destination_path="/minio/.minio/certs/public.crt",
                    permissions=0o511,
                ),
            ]
            if self.model.config.get("ssl-ca"):
                ssl_config.append(
                    LazyContainerFileTemplate(
                        source_template=self.model.config["ssl-ca"],
                        destination_path="/minio/.minio/certs/CAs/root.cert",
                        permissions=0o511,
                    )
                )
            logger.info("SSL configuration provided, pushing SSL files to MinIO container.")
            files.extend(ssl_config)
        logger.info("No SSL configuration provided, skipping file push.")
        return files if files else None


if __name__ == "__main__":  # pragma: nocover
    main(MinIOOperator)
```

</details>


### 💬 Copilot

Perfect! I found the usage of `set_ports()`. Now let me check the components directory to see if there are any other uses of port-related APIs:

### ✅ `github-mcp-server-get_file_contents`

**/src/components**

<details>
<summary>Arguments</summary>

```json
{
  "owner": "canonical",
  "path": "/src/components",
  "repo": "minio-operator"
}
```

</details>

```
[{"type":"file","size":1542,"name":"owasp_logging.py","path":"src/components/owasp_logging.py","sha":"0e5372c1807c91cdaaa4d8fbfe06a28e1a2a8bba","url":"https://api.github.com/repos/canonical/minio-operator/contents/src/components/owasp_logging.py?ref=42a875c5cefce5bc57e7acd7152d5db725faf400","git_url":"https://api.github.com/repos/canonical/minio-operator/git/blobs/0e5372c1807c91cdaaa4d8fbfe06a28e1a2a8bba","html_url":"https://github.com/canonical/minio-operator/blob/42a875c5cefce5bc57e7acd7152d5db725faf400/src/components/owasp_logging.py","download_url":"https://raw.githubusercontent.com/canonical/minio-operator/42a875c5cefce5bc57e7acd7152d5db725faf400/src/components/owasp_logging.py"},{"type":"file","size":2515,"name":"pebble_component.py","path":"src/components/pebble_component.py","sha":"672ccc75165d0a5a4b1e9ec4bb23bc0449997e44","url":"https://api.github.com/repos/canonical/minio-operator/contents/src/components/pebble_component.py?ref=42a875c5cefce5bc57e7acd7152d5db725faf400","git_url":"https://api.github.com/repos/canonical/minio-operator/git/blobs/672ccc75165d0a5a4b1e9ec4bb23bc0449997e44","html_url":"https://github.com/canonical/minio-operator/blob/42a875c5cefce5bc57e7acd7152d5db725faf400/src/components/pebble_component.py","download_url":"https://raw.githubusercontent.com/canonical/minio-operator/42a875c5cefce5bc57e7acd7152d5db725faf400/src/components/pebble_component.py"},{"type":"file","size":3665,"name":"service_component.py","path":"src/components/service_component.py","sha":"2d9e7fbba8b539863834fbbba728e4644d0bbe80","url":"https://api.github.com/repos/canonical/minio-operator/contents/src/components/service_component.py?ref=42a875c5cefce5bc57e7acd7152d5db725faf400","git_url":"https://api.github.com/repos/canonical/minio-operator/git/blobs/2d9e7fbba8b539863834fbbba728e4644d0bbe80","html_url":"https://github.com/canonical/minio-operator/blob/42a875c5cefce5bc57e7acd7152d5db725faf400/src/components/service_component.py","download_url":"https://raw.githubusercontent.com/canonical/minio-operator/42a875c5cefce5bc57e7acd7152d5db725faf400/src/components/service_component.py"},{"type":"file","size":3332,"name":"service_mesh_component.py","path":"src/components/service_mesh_component.py","sha":"1a959b6d422481a9f9ddcbf1d834e14771d66759","url":"https://api.github.com/repos/canonical/minio-operator/contents/src/components/service_mesh_component.py?ref=42a875c5cefce5bc57e7acd7152d5db725faf400","git_url":"https://api.github.com/repos/canonical/minio-operator/git/blobs/1a959b6d422481a9f9ddcbf1d834e14771d66759","html_url":"https://github.com/canonical/minio-operator/blob/42a875c5cefce5bc57e7acd7152d5db725faf400/src/components/service_mesh_component.py","download_url":"https://raw.githubusercontent.com/canonical/minio-operator/42a875c5cefce5bc57e7acd7152d5db725faf400/src/components/service_mesh_component.py"}]
```


### 💬 Copilot

Let me check the service_component.py as well, since it might have additional port-related code:

### ✅ `github-mcp-server-get_file_contents`

**/src/components/service_component.py**

<details>
<summary>Arguments</summary>

```json
{
  "owner": "canonical",
  "path": "/src/components/service_component.py",
  "repo": "minio-operator"
}
```

</details>

<details>
<summary>81 lines</summary>

```
successfully downloaded text file (SHA: 2d9e7fbba8b539863834fbbba728e4644d0bbe80)import logging
from typing import List

from charmed_kubeflow_chisme.components import Component
from lightkube import Client
from lightkube.models.core_v1 import ServicePort, ServiceSpec
from lightkube.models.meta_v1 import ObjectMeta
from lightkube.resources.core_v1 import Service
from lightkube.types import PatchType
from ops import ActiveStatus, BlockedStatus, CharmBase, StatusBase

logger = logging.getLogger(__name__)


class KubernetesServicePatchComponent(Component):
    """Kubernetes Service Patch Component."""

    def __init__(
        self,
        charm: CharmBase,
        name: str,
        ports: List[ServicePort],
    ):
        """Initialize the KubernetesServiceComponent."""
        super().__init__(charm=charm, name=name)
        self._charm = charm
        self._lightkube_client = Client()
        self._service_name = self._charm.app.name
        self._service_object = self._get_service_object(
            service_name=self._service_name,
            ports=ports,
            namespace=self._charm.model.name,
            app_name=self._charm.app.name,
        )

    def _configure_app_leader(self, event):
        """Execute everything this Component should do at the Application level for leaders."""
        logger.info("Checking if K8s Service needs to be updated.")
        if self._is_patched():
            logger.info("K8s Service %s is already patched, skipping", self._service_name)
            return

        logger.info("K8s Service %s is not patched, applying patch", self._service_name)
        self._lightkube_client.patch(
            Service, self._service_name, self._service_object, patch_type=PatchType.MERGE
        )

    def get_status(self) -> StatusBase:
        """Returns the status of this Component."""
        logger.info("Checking the status of the Kubernetes Service Patch Component.")
        if not self._is_patched():
            return BlockedStatus("K8s Service was not patched correctly. Check logs for details.")

        return ActiveStatus()

    def _is_patched(self) -> bool:
        """Check if the service is already patched."""
        fetched_service_object = self._lightkube_client.get(
            Service, name=self._service_name, namespace=self._charm.model.name
        )
        expected_ports = [(p.port, p.targetPort) for p in self._service_object.spec.ports]
        fetched_ports = [(p.port, p.targetPort) for p in fetched_service_object.spec.ports]
        return expected_ports == fetched_ports

    def _get_service_object(
        self, service_name: str, ports: List[ServicePort], namespace: str, app_name: str
    ) -> Service:
        """Creates a valid Service representation.

        Args:
            service_name (str): The name of the service.
            ports (List[ServicePort]): A list of ServicePort objects defining the service ports.
            namespace (str): The namespace in which the service will be created.
            app_name (str): The name of the application to which this service belongs.
        Returns:
            Service: A valid representation of a Kubernetes Service with the correct ports.
        """
        for port in ports:
            port.targetPort = port.targetPort or port.port

        return Service(
            apiVersion="v1",
            kind="Service",
            metadata=ObjectMeta(
                namespace=namespace,
                name=service_name,
                labels={"app.kubernetes.io/name": app_name},
            ),
            spec=ServiceSpec(
                selector={"app.kubernetes.io/name": app_name},
                ports=ports,
                type="ClusterIP",
            ),
        )
```

</details>


### 💬 Copilot

Now let me verify the configuration to see what ports are defined:

### ✅ `github-mcp-server-get_file_contents`

**/config.yaml**

<details>
<summary>Arguments</summary>

```json
{
  "owner": "canonical",
  "path": "/config.yaml",
  "repo": "minio-operator"
}
```

</details>

<details>
<summary>43 lines</summary>

```
successfully downloaded text file (SHA: 80e9f1820fcc0972d84fc3ff97590b8ecfc76a85)# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

options:
  port:
    type: int
    default: 9000
    description: HTTP port
  console-port:
    type: int
    default: 9001
    description: HTTP port for minio console
  access-key:
    type: string
    default: 'minio'
    description: Access key
  secret-key:
    type: string
    default: ''
    description: Secret key. Must be at least 8 characters long. If not provided, a random key will be used.
  mode:
    type: string
    default: 'server'
    description: "Mode of operations. Possible values: server, gateway"
  gateway-storage-service:
    type: string
    default: ''
    description: "Storage service used by gateway to store objects. This value is required for gateway mode. Possible values: s3, azure"
  storage-service-endpoint:
    type: string
    default: ''
    description: "Service endpoint of gateway storage service. This value is optional when using S3 or Azure public API endpoints"
  ssl-ca:
    type: string
    default: ''
    description: "Base64 encoded certificate authority for untrusted certificate chains"
  ssl-cert:
    type: string
    default: ''
    description: "Base64 encoded SSL certificate."
  ssl-key:
    type: string
    default: ''
    description: "Base64 encoded SSL key."
```

</details>


### 💬 Copilot

Perfect! Now I have all the information I need. Let me provide a comprehensive summary:

## Analysis: MinIO Operator's Use of `set_ports()` API

### 1. **All Uses of Port-Related APIs**

**Found 1 use of `set_ports()`** (no uses of `open_port()` or `close_port()`)

### 2. **Code Snippet with Location**

**File:** `src/charm.py` (Lines 40-42)

```python
self.model.unit.set_ports(
    int(self.model.config["port"]),
    int(self.model.config["console-port"]),
)
```

**Context (Full `__init__` method setup - Lines 30-45):**
```python
def __init__(self, *args):
    super().__init__(*args)
    try:
        minio_args = self._get_minio_args()
        secret_key = self._get_secret_key()
    except ErrorWithStatus as e:
        self.unit.status = e.status
        return

    self.model.unit.set_ports(
        int(self.model.config["port"]),
        int(self.model.config["console-port"]),
    )
```

### 3. **Pattern Explanation**

The MinIO operator uses `set_ports()` with the following pattern:

**Port Configuration:**
- **Port 1:** `port` (default: 9000) - MinIO API server port
- **Port 2:** `console-port` (default: 9001) - MinIO console UI port

**When Called:**
- Called **once during charm initialization** in the `__init__` method (line 40)
- Called **immediately** after validating configuration and secret key
- Called **before** setting up any charm components or event handlers

**How Ports Are Determined:**
- Ports come from **charm configuration** (`self.model.config`)
- Both are converted to integers: `int(self.model.config["port"])` and `int(self.model.config["console-port"])`
- Default values are defined in `config.yaml`:
  - `port`: 9000
  - `console-port`: 9001

**Related Port Usage:**
The charm also uses these same ports in other components:
1. **ServicePort objects** (lines 57-60 in charm.py) - passed to `KubernetesServicePatchComponent`:
   ```python
   ports=[
       ServicePort(int(self.model.config["port"]), name="minio"),
       ServicePort(int(self.model.config["console-port"]), name="minio-console"),
   ],
   ```

2. **Prometheus metrics configuration** (lines 94-97):
   ```python
   "static_configs": [{"targets": [f"*:{self.model.config['port']}"]}],
   ```

3. **MinIO container configuration** (line 113):
   ```python
   MINIO_PORT=int(self.model.config["port"]),
   ```

**Key Insight:** The operator uses `set_ports()` with a multi-port setup (2 ports) in a single call to declare all ports that the charm uses, allowing Kubernetes to properly expose these ports on the unit.


---

<sub>⏱️ 17s</sub>

### 📦 task (Completed)

### 💬 Copilot

I'll analyze the charm codebase to understand the port management pattern. Let me search for the port-related functions and examine the key files.

### ✅ `glob`

**/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C3**

"**/src/**/*.py" in /tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C3

<details>
<summary>10 matches</summary>

```
/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C3/tests/integration/grafana-tester/src/charm.py
/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C3/src/relation.py
/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C3/src/charm.py
/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C3/src/grafana.py
/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C3/src/models.py
/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C3/src/grafana_client.py
/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C3/src/custom_ini_config.py
/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C3/src/secret_storage.py
/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C3/src/grafana_config.py
/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C3/src/constants.py
```

</details>


### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C3.**

/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C3

<details>
<summary>20 lines</summary>

```
.git
.github
.gitignore
.jujuignore
CODEOWNERS
CONTRIBUTING.md
LICENSE
README.md
RELEASE.md
SECURITY.md
charmcraft.yaml
icon.svg
lib
probes
pyproject.toml
src
terraform
tests
tox.ini
uv.lock
```

</details>


### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C3/charmcraft.yaml.**

/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C3/charmcraft.yaml

<details>
<summary>267 lines</summary>

```
1. # Copyright 2021 Canonical Ltd.
2. # See LICENSE file for licensing details.
3. 
4. type: charm
5. name: grafana-k8s
6. summary: Data visualization and observability with Grafana
7. description: |
8.   Grafana provides dashboards for monitoring data and this
9.   charm is written to allow for HA on Kubernetes and can take
10.   multiple data sources (for example, Prometheus).
11. 
12. links:
13.   documentation: https://discourse.charmhub.io/t/grafana-operator-k8s-docs-index/5612
14.   website:
15.     - https://charmhub.io/grafana-k8s
16.   source:
17.     - https://github.com/canonical/grafana-k8s-operator
18.   issues:
19.     - https://github.com/canonical/grafana-k8s-operator/issues
20. 
21. assumes:
22.   - k8s-api
23.   - juju >= 3.6
24. 
25. containers:
26.   grafana:
27.     resource: grafana-image
28.     mounts:
29.       - storage: database
30.         location: /var/lib/grafana
31. 
32. storage:
33.   database:
34.     type: filesystem
35. 
36. requires:
37.   grafana-source:
38.     interface: grafana_datasource
39.     optional: true
40.   grafana-dashboard:
41.     interface: grafana_dashboard
42.     optional: true
43.   grafana-auth:
44.     interface: grafana_auth
45.     optional: true
46.   pgsql:
47.     interface: postgresql_client
48.     limit: 1
49.     optional: true
50.     description: |
51.       This endpoint allows using a PostgreSQL database backend for data storage.
52.       Using this endpoint overrides Grafana's usage of the embedded sqlite3 database
53.       for data storage and is required for more than one Grafana unit.
54.   catalogue:
55.     interface: catalogue
56.     optional: true
57.   ingress:
58.     interface: ingress
59.     limit: 1
60.     optional: true
61.   certificates:
62.     interface: tls-certificates
63.     limit: 1
64.     optional: true
65.     description: Certificate and key files for Grafana to use with TLS.
66.   receive-ca-cert:
67.     interface: certificate_transfer
68.     optional: true
69.     description: |
70.       Receive a CA cert for grafana to trust.
71.       This relation can be used with a local CA to obtain the CA cert that was used to sign proxied
72.       endpoints.
73.   oauth:
74.     interface: oauth
75.     limit: 1
76.     optional: true
77.     description: |
78.       Receive oauth server's info and a set of client credentials.
79.       This relation can be used to integrate grafana with an oAuth2/OIDC Provider.
80.   charm-tracing:
81.     description: |
82.       Enables sending charm traces to a distributed tracing backend such as Tempo.
83.     limit: 1
84.     optional: true
85.     interface: tracing
86.   workload-tracing:
87.     description: |
88.       Enables sending workload traces to a distributed tracing backend such as Tempo.
89.     limit: 1
90.     optional: true
91.     interface: tracing
92.   service-mesh:
93.     limit: 1
94.     interface: service_mesh
95.     description: |
96.       Subscribe this charm to a service mesh and create authorization policies.
97.   require-cmr-mesh:
98.     interface: cross_model_mesh
99.     description: |
100.       Allow a cross-model application access to this charm via the service mesh.
101.       This relation provides additional data required by the service mesh to enforce cross-model authorization policies.
102. 
103. provides:
104.   profiling-endpoint:
105.     interface: parca_scrape
106.     optional: true
107.     description: |
108.       Links to grafana's pprof endpoint. Can be used to integrate with parca to 
109.       profile the grafana server process.
110.   metrics-endpoint:
111.     interface: prometheus_scrape
112.     optional: true
113.     description: Links to grafana's own `/metrics` endpoint.
114.   grafana-metadata:
115.     interface: grafana_metadata
116.     optional: true
117.     description: |
118.       Provides metadata about the grafana instance, such as its URL and ID.
119.   provide-cmr-mesh:
120.     interface: cross_model_mesh
121.     description: |
122.       Access a cross-model application from this charm via the service mesh.
123.       This relation provides additional data required by the service mesh to enforce cross-model authorization policies.
124. 
125. peers:
126.   grafana:
127.     interface: grafana_peers
128.   replicas:
129.     # Peer relation used as storage for TLS data
130.     interface: grafana_replicas
131. 
132. resources:
133.   grafana-image:
134.     type: oci-image
135.     description: upstream docker image for Grafana
136.     upstream-source: docker.io/ubuntu/grafana@sha256:d2f26ddd1e0263cd84291375f9a2309dbc08abbd465e0554a5b678824a5f207a  # renovate: oci-image tag: 12.0-24.04
137. 
138. platforms:
139.   ubuntu@24.04:amd64:
140. 
141. parts:
142.   charm:
143.     source: .
144.     plugin: uv
145.     build-packages: [git]
146.     build-snaps: [astral-uv]
147.     override-build: |
148.       craftctl default
149.       git describe --always > $CRAFT_PART_INSTALL/version
150.   static-sqlite3:
151.     plugin: dump
152.     source: .
153.     build-packages:
154.       - curl
155.     override-pull: |
156.       curl -L https://github.com/CompuRoot/static-sqlite3/releases/latest/download/sqlite3 -o sqlite-static
157.       chmod +x sqlite-static
158.   cos-tool:
159.     plugin: dump
160.     source: .
161.     build-packages:
162.       - curl
163.     override-pull: |
164.       curl -L -O https://github.com/canonical/cos-tool/releases/latest/download/cos-tool-${CRAFT_ARCH_BUILD_FOR}
165.       chmod 775 cos-tool-*
166. 
167. actions:
168.   get-admin-password:
169.     description: |
170.       Get the dashboard url and initial admin password for the Grafana web interface. Initial
171.       admin password is generated at charm deployment time. If the password has been changed,
172.       a notice of that fact will be returned by this action instead.
173. 
174. config:
175.   options:
176.     allow_anonymous_access:
177.       type: boolean
178.       default: false
179.       description: |
180.         Whether Grafana should allow anonymous access to dashboards. Unless
181.         you have some other authentication mechanism in front of your deployment,
182.         you likely do not want to enable this.
183.     allow_embedding:
184.       type: boolean
185.       default: false
186.       description: |
187.         Whether Grafana should allow embedding dashboards using iframes. Unless
188.         you have a clear reason for doing so, you likely do not want to enable this.
189.     log_level:
190.       type: string
191.       description: |
192.         Logging level for Grafana. Options are “debug”, “info”,
193.         “warn”, “error”, and “critical”.
194.       default: info
195.     admin_user:
196.       description: The Grafana administrative user
197.       type: string
198.       default: admin
199.     web_external_url:
200.       description: |
201.         DEPRECATED. This config option is no longer used, in favor of "skipPrefix".
202. 
203.         The URL under which Grafana is externally reachable (for example,
204.         if Grafana is served via a reverse proxy).
205. 
206.         Used for generating relative and absolute links back to
207.         Grafana itself. If the URL has a path portion, it will be used to
208.         prefix all HTTP endpoints served by Grafana.
209. 
210.         If omitted, relevant URL components will be derived automatically.
211. 
212.         If provided, this should be a complete URI, including scheme, or a
213.         fully qualified subpath starting with `/`.
214. 
215.         If Grafana is being served directly from the root of a fully-qualified
216.         host or a bare A record, this may be omitted.
217.       type: string
218.       default: ""
219.     enable_auto_assign_org:
220.       description: |
221.         Set to true to automatically add new users to the main organization (id 1). When set to
222.         false, new users automatically cause a new organization to be created for that new user.
223.       type: boolean
224.       default: true
225.     datasource_query_timeout:
226.       description: |
227.         The default timeout for querying a Grafana datasource. Each datasource can
228.         also configure its own preferred timeout value through relation data. If the
229.         value configured through relation data is larger than datasource_query_timeout
230.         then that value is left unchanged. The value of this configuration option must
231.         be a positive integer representing the maximum number of seconds Grafana will
232.         wait for a datasource to respond to a query.
233.       type: int
234.       default: 300
235.     cpu:
236.       description: |
237.         K8s cpu resource limit, e.g. "1" or "500m". Default is unset (no limit). This value is used
238.         for the "limits" portion of the resource requirements (the "requests" portion is
239.         automatically deduced from it).
240.         See https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/
241.       type: string
242.     memory:
243.       description: |
244.         K8s memory resource limit, e.g. "1Gi". Default is unset (no limit). This value is used
245.         for the "limits" portion of the resource requirements (the "requests" portion is
246.         automatically deduced from it).
247.         See https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/
248.       type: string
249.     reporting_enabled:
250.       description: |
251.         When disabled, Grafana will be configured to not send anonymous usage statistics to stats.grafana.org, nor
252.         periodically check for updates.
253.         It is very helpful to the Grafana project, so please leave this enabled.
254.         
255.         When enabled, Grafana will use its default values for analytics.
256.         
257.         Ref: https://grafana.com/docs/grafana/latest/setup-grafana/configure-grafana/#analytics
258.       type: boolean
259.       default: true
260.     custom_config:
261.       type: string
262.       description: |
263.         Additional configuration options to be added to grafana.ini.
264.         These options will be appended to the grafana.ini file, allowing for custom configuration.
265.         Note that this config option accepts only a small subset of the grafana.ini file.
266.         Currently supported sections:
267.         - [smtp], ref: https://grafana.com/docs/grafana/latest/setup-grafana/configure-grafana/#smtp
```

</details>


### 💬 Copilot

Now let me search for port-related function calls and examine the main charm file:

### ✅ `grep`

**/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C3/src**

"open_port\(|close_port\(|set_ports\(|opened_ports\(" (/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C3/src)

```
/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C3/src/charm.py:        self._set_ports()
/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C3/src/charm.py:    def _set_ports(self):
/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C3/src/charm.py:        actual_ports = self.unit.opened_ports()
/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C3/src/charm.py:            self.unit.close_port(p.protocol, p.port)
/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C3/src/charm.py:            self.unit.open_port(p.protocol, p.port)
```


### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C3/src/charm.py.**

/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C3/src/charm.py

```
File too large to read at once (26.6 KB). Consider using the grep tool to search within the file, or view with view_range to read specific sections.
```


### ✅ `grep`

**/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C3/src/constants.py**

"port|PORT|Port" (/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C3/src/constants.py)

```
/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C3/src/constants.py:    "host",  # in the form '<url_or_ip>:<port>', e.g. 127.0.0.1:3306
/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C3/src/constants.py:PROFILING_PORT = 8080
/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C3/src/constants.py:WORKLOAD_PORT = 3000
```


### 💬 Copilot

Good! Now let me view the charm.py file in specific sections to see the complete port management pattern:

### ✅ `bash`

**Find all port-related function calls with line numbers**

$ grep -n "_set_ports\|open_port\|close_port\|opened_ports" /tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C3/src/charm.py

<details>
<summary>6 lines</summary>

```
428:        self._set_ports()
648:    def _set_ports(self):
651:        actual_ports = self.unit.opened_ports()
656:            self.unit.close_port(p.protocol, p.port)
660:            self.unit.open_port(p.protocol, p.port)
<exited with exit code 0>
```

</details>


### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C3/src/constants.py.**

/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C3/src/constants.py

<details>
<summary>29 lines</summary>

```
1. """Charm constants."""
2. 
3. REQUIRED_DATABASE_FIELDS = {
4.     "type",  # mysql, postgres or sqlite3 (sqlite3 doesn't work for HA)
5.     "host",  # in the form '<url_or_ip>:<port>', e.g. 127.0.0.1:3306
6.     "name",
7.     "user",
8.     "password",
9. }
10. PEER_RELATION = "grafana"
11. PGSQL_RELATION = "pgsql"
12. DATABASE_PATH = "/var/lib/grafana/grafana.db"
13. # https://grafana.com/docs/grafana/latest/setup-grafana/configure-security/configure-authentication/generic-oauth
14. OAUTH_SCOPES = "openid email offline_access"
15. OAUTH_GRANT_TYPES = ["authorization_code", "refresh_token"]
16. GRAFANA_WORKLOAD = "grafana"
17. VALID_AUTHENTICATION_MODES = {"proxy"}
18. CONFIG_PATH = "/etc/grafana/grafana-config.ini"
19. PROVISIONING_PATH = "/etc/grafana/provisioning"
20. DATASOURCES_PATH = "/etc/grafana/provisioning/datasources/datasources.yaml"
21. DASHBOARDS_DIR = f"{PROVISIONING_PATH}/dashboards"
22. GRAFANA_CRT_PATH = "/etc/grafana/grafana.crt"
23. GRAFANA_KEY_PATH = "/etc/grafana/grafana.key"
24. CA_CERT_PATH = "/usr/local/share/ca-certificates/cos-ca.crt"
25. TRUSTED_CA_CERT_PATH = "/usr/local/share/ca-certificates/trusted-ca-cert.crt"
26. PROFILING_PORT = 8080
27. WORKLOAD_PORT = 3000
28. METRICS_PATH = "/metrics"
29.
```

</details>


### 💬 Copilot

Now let me view the specific sections of charm.py where the port management functions are defined and called:

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C3/src/charm.py.**

/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C3/src/charm.py (lines 420-440)

<details>
<summary>21 lines</summary>

```
420.         """The admin password."""
421.         contents = self._secret_storage.contents
422.         if not contents:
423.             return None
424.         return contents.get('password')
425. 
426.     def _reconcile(self):
427.         """Unconditional control logic."""
428.         self._set_ports()
429.         self.unit.set_workload_version(self._grafana_service.grafana_version)
430.         if not self.resource_patch.is_ready():
431.             logger.debug("Resource patch not ready yet. Skipping cluster update step.")
432.             return
433.         if self.charm_tracing.is_ready() and (endpoint:= self.charm_tracing.get_endpoint("otlp_http")):
434.             ops_tracing.set_destination(
435.                 url=endpoint + "/v1/traces",
436.                 ca=self._tls_config.ca if self._tls_config else None
437.             )
438.         self.ingress.provide_ingress_requirements(scheme=self._scheme, port=WORKLOAD_PORT)
439.         if self._check_wrong_relations():
440.             return
```

</details>


### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C3/src/charm.py.**

/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C3/src/charm.py (lines 640-670)

<details>
<summary>30 lines</summary>

```
640.         env_vars = {}
641.         auth_var_prefix = "GF_AUTH_" + auth_mode.upper() + "_"
642.         mode_enabled_var = auth_var_prefix + "ENABLED"
643.         env_vars[mode_enabled_var] = "True"
644.         for var in conf[auth_mode].keys():
645.             env_vars[auth_var_prefix + str(var).upper()] = str(conf[auth_mode][var])
646.         return env_vars
647. 
648.     def _set_ports(self):
649.         """Open necessary (and close no longer needed) workload ports."""
650.         planned_ports = {Port(protocol="tcp", port=WORKLOAD_PORT)} if self.unit.is_leader() else set()
651.         actual_ports = self.unit.opened_ports()
652. 
653.         # Ports may change across an upgrade, so need to sync
654.         ports_to_close = actual_ports.difference(planned_ports)
655.         for p in ports_to_close:
656.             self.unit.close_port(p.protocol, p.port)
657. 
658.         new_ports_to_open = planned_ports.difference(actual_ports)
659.         for p in new_ports_to_open:
660.             self.unit.open_port(p.protocol, p.port)
661. 
662.     def _resource_reqs_from_config(self) -> ResourceRequirements:
663.         limits = {"cpu": self.model.config.get("cpu"), "memory": self.model.config.get("memory")}
664.         requests = {"cpu": "0.25", "memory": "200Mi"}
665.         return adjust_resource_requirements(limits, requests, adhere_to_requests=True)
666. 
667. if __name__ == "__main__":
668.     main(GrafanaCharm, use_juju_for_storage=True)
669.
```

</details>


### 💬 Copilot

Let me check the imports and see if Port is defined in the file:

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C3/src/charm.py.**

/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C3/src/charm.py (lines 1-60)

<details>
<summary>60 lines</summary>

```
1. #! /usr/bin/env python3
2. # -*- coding: utf-8 -*-
3. #
4. #  Copyright 2021 Canonical Ltd.
5. #
6. #  Licensed under the Apache License, Version 2.0 (the "License");
7. #  you may not use this file except in compliance with the License.
8. #  You may obtain a copy of the License at
9. #
10. #      http://www.apache.org/licenses/LICENSE-2.0
11. #
12. #  Unless required by applicable law or agreed to in writing, software
13. #  distributed under the License is distributed on an "AS IS" BASIS,
14. #  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
15. #  See the License for the specific language governing permissions and
16. #  limitations under the License.
17. 
18. """A Kubernetes charm for Grafana."""
19. 
20. import logging
21. import os
22. import socket
23. import subprocess
24. from pathlib import Path
25. from typing import Any, Dict, cast, Optional
26. from urllib.parse import urlparse
27. 
28. from cosl import JujuTopology
29. from cosl.reconciler import all_events, observe_events
30. from ops import ActiveStatus, BlockedStatus, CollectStatusEvent, RelationBrokenEvent, StatusBase, main
31. from ops.charm import (
32.     ActionEvent,
33.     CharmBase,
34.     RelationChangedEvent,
35. )
36. from ops.model import Port
37. from secret_storage import SecretStorage
38. 
39. from charms.catalogue_k8s.v1.catalogue import CatalogueConsumer, CatalogueItem
40. from charms.certificate_transfer_interface.v1.certificate_transfer import (
41.     CertificateTransferRequires,
42. )
43. from charms.data_platform_libs.v0.data_interfaces import DatabaseRequires
44. from charms.grafana_k8s.v0.grafana_auth import AuthRequirer, AuthRequirerCharmEvents
45. from charms.grafana_k8s.v0.grafana_dashboard import GrafanaDashboardConsumer
46. from charms.grafana_k8s.v0.grafana_metadata import GrafanaMetadataProvider
47. from charms.grafana_k8s.v0.grafana_source import (
48.     GrafanaSourceConsumer,
49. )
50. from charms.hydra.v0.oauth import (
51.     ClientConfig as OauthClientConfig,
52.     OAuthRequirer,
53.     OauthProviderConfig
54. )
55. from charms.istio_beacon_k8s.v0.service_mesh import UnitPolicy, ServiceMeshConsumer
56. from charms.observability_libs.v0.kubernetes_compute_resources_patch import (
57.     KubernetesComputeResourcesPatch,
58.     ResourceRequirements,
59.     adjust_resource_requirements,
60. )
```

</details>


### ✅ `bash`

**View imports section**

$ grep -n "from\|import" /tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C3/src/charm.py | head -40

<details>
<summary>41 lines</summary>

```
20:import logging
21:import os
22:import socket
23:import subprocess
24:from pathlib import Path
25:from typing import Any, Dict, cast, Optional
26:from urllib.parse import urlparse
28:from cosl import JujuTopology
29:from cosl.reconciler import all_events, observe_events
30:from ops import ActiveStatus, BlockedStatus, CollectStatusEvent, RelationBrokenEvent, StatusBase, main
31:from ops.charm import (
36:from ops.model import Port
37:from secret_storage import SecretStorage
39:from charms.catalogue_k8s.v1.catalogue import CatalogueConsumer, CatalogueItem
40:from charms.certificate_transfer_interface.v1.certificate_transfer import (
43:from charms.data_platform_libs.v0.data_interfaces import DatabaseRequires
44:from charms.grafana_k8s.v0.grafana_auth import AuthRequirer, AuthRequirerCharmEvents
45:from charms.grafana_k8s.v0.grafana_dashboard import GrafanaDashboardConsumer
46:from charms.grafana_k8s.v0.grafana_metadata import GrafanaMetadataProvider
47:from charms.grafana_k8s.v0.grafana_source import (
50:from charms.hydra.v0.oauth import (
55:from charms.istio_beacon_k8s.v0.service_mesh import UnitPolicy, ServiceMeshConsumer
56:from charms.observability_libs.v0.kubernetes_compute_resources_patch import (
61:from charms.parca_k8s.v0.parca_scrape import ProfilingEndpointProvider
62:from charms.prometheus_k8s.v0.prometheus_scrape import MetricsEndpointProvider
63:from charms.tempo_coordinator_k8s.v0.tracing import TracingEndpointRequirer
64:from charms.traefik_k8s.v2.ingress import IngressPerAppRequirer, IngressPerAppReadyEvent, IngressPerAppRevokedEvent
65:from grafana import Grafana
66:from grafana_client import GrafanaClient, GrafanaCommError
67:from grafana_config import GrafanaConfig
68:from secret_storage import generate_password
69:from relation import Relation
70:from models import DatasourceConfig, PebbleEnvironment, TLSConfig
71:from charms.tls_certificates_interface.v4.tls_certificates import (
76:from constants import (
87:import ops_tracing
106:        self._topology = JujuTopology.from_charm(self)
180:            self, GRAFANA_WORKLOAD, resource_reqs_func=self._resource_reqs_from_config
320:                "visualize metrics from mixed datasources in configurable "
511:            event: A :class:`RelationChangedEvent` from a `database` source
<exited with exit code 0>
```

</details>


### 💬 Copilot

Perfect! Now let me get the full constants.py file to see all port-related constants:

### ✅ `bash`

**Check charm.py line count**

$ wc -l /tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C3/src/charm.py

```
668 /tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C3/src/charm.py
<exited with exit code 0>
```


### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C3/src/charm.py.**

/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C3/src/charm.py (lines 76-90)

<details>
<summary>15 lines</summary>

```
76. from constants import (
77.     PEER_RELATION,
78.     WORKLOAD_PORT,
79.     OAUTH_SCOPES,
80.     CA_CERT_PATH,
81.     GRAFANA_WORKLOAD,
82.     PGSQL_RELATION,
83.     PROFILING_PORT,
84.     OAUTH_GRANT_TYPES,
85.     VALID_AUTHENTICATION_MODES,
86.     METRICS_PATH)
87. import ops_tracing
88. 
89. logger = logging.getLogger()
90.
```

</details>


### 💬 Copilot

Excellent! Now let me verify if there are any other port-related uses across the entire src directory:

### ✅ `bash`

**Search for port constant usage**

$ grep -r "WORKLOAD_PORT\|PROFILING_PORT" /tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C3/src --include="*.py"

<details>
<summary>17 lines</summary>

```
/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C3/src/constants.py:PROFILING_PORT = 8080
/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C3/src/constants.py:WORKLOAD_PORT = 3000
/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C3/src/grafana.py:    PROFILING_PORT,
/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C3/src/grafana.py:    WORKLOAD_PORT,
/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C3/src/grafana.py:                    "GF_DIAGNOSTICS_PROFILING_PORT": str(PROFILING_PORT),
/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C3/src/grafana.py:                            "GF_SERVER_HTTP_PORT": str(WORKLOAD_PORT),
/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C3/src/charm.py:    WORKLOAD_PORT,
/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C3/src/charm.py:    PROFILING_PORT,
/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C3/src/charm.py:        self.ingress = IngressPerAppRequirer(self, port=WORKLOAD_PORT, scheme=self._scheme, strip_prefix=False)
/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C3/src/charm.py:                    ports=[WORKLOAD_PORT],
/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C3/src/charm.py:                    ports=[PROFILING_PORT],
/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C3/src/charm.py:            urls=[f"{self.app.name}:{WORKLOAD_PORT}"],
/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C3/src/charm.py:        return f"{self._scheme}://{self._fqdn}:{WORKLOAD_PORT}"
/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C3/src/charm.py:        job = {"static_configs": [{"targets": [f"*:{PROFILING_PORT}"]}], "scheme": self._scheme}
/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C3/src/charm.py:        self.ingress.provide_ingress_requirements(scheme=self._scheme, port=WORKLOAD_PORT)
/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C3/src/charm.py:        planned_ports = {Port(protocol="tcp", port=WORKLOAD_PORT)} if self.unit.is_leader() else set()
<exited with exit code 0>
```

</details>


### ✅ `bash`

**Search all port-related function calls in src**

$ grep -r "open_port\|close_port\|set_ports\|opened_ports" /tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C3/src --include="*.py" -n

<details>
<summary>6 lines</summary>

```
/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C3/src/charm.py:428:        self._set_ports()
/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C3/src/charm.py:648:    def _set_ports(self):
/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C3/src/charm.py:651:        actual_ports = self.unit.opened_ports()
/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C3/src/charm.py:656:            self.unit.close_port(p.protocol, p.port)
/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C3/src/charm.py:660:            self.unit.open_port(p.protocol, p.port)
<exited with exit code 0>
```

</details>


### 💬 Copilot

Perfect! Let me also check the grafana.py to see how those port constants are used:

### ✅ `bash`

**Find port configuration in grafana.py**

$ grep -n "PROFILING_PORT\|WORKLOAD_PORT\|GF_SERVER_HTTP_PORT\|GF_DIAGNOSTICS_PROFILING_PORT" /tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C3/src/grafana.py -B 2 -A 2

<details>
<summary>21 lines</summary>

```
38-    GRAFANA_CRT_PATH,
39-    OAUTH_SCOPES,
40:    PROFILING_PORT,
41-    GRAFANA_WORKLOAD,
42-    CONFIG_PATH,
43:    WORKLOAD_PORT,
44-    PROVISIONING_PATH,
45-    DATASOURCES_PATH,
--
190-                    "GF_DIAGNOSTICS_PROFILING_ENABLED": "true",
191-                    "GF_DIAGNOSTICS_PROFILING_ADDR": "0.0.0.0",
192:                    "GF_DIAGNOSTICS_PROFILING_PORT": str(PROFILING_PORT),
193-                }
194-            )
--
212-                        "startup": "enabled",
213-                        "environment": {
214:                            "GF_SERVER_HTTP_PORT": str(WORKLOAD_PORT),
215-                            "GF_LOG_LEVEL": pebble_env.log_level,
216-                            "GF_PLUGINS_ENABLE_ALPHA": "true",
<exited with exit code 0>
```

</details>


### 💬 Copilot

Perfect! Now let me get a summary view of the main charm class definition to understand the context better:

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C3/src/charm.py.**

/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C3/src/charm.py (lines 91-115)

<details>
<summary>25 lines</summary>

```
91. 
92. class GrafanaCharm(CharmBase):
93.     """Charm to run Grafana on Kubernetes.
94. 
95.     This charm allows for high-availability
96.     (as long as a non-sqlite database relation is present).
97. 
98.     Developers of this charm should be aware of the Grafana provisioning docs:
99.     https://grafana.com/docs/grafana/latest/administration/provisioning/
100.     """
101. 
102.     def __init__(self, *args):
103.         super().__init__(*args)
104. 
105.         # -- initialize states --
106.         self._topology = JujuTopology.from_charm(self)
107.         self._fqdn = socket.getfqdn()
108.         self.peers = Relation(app=self.app, relation=self.model.get_relation(PEER_RELATION))
109.         self._secret_storage = SecretStorage(self, "admin-password",
110.                                              default=lambda: {"password": generate_password()})
111. 
112. 
113.         # -- certificates
114.         self._csr_attributes = CertificateRequestAttributes(
115.             # the `common_name` field is required but limited to 64 characters.
```

</details>


### 💬 Copilot

Excellent! Now I have all the information needed. Let me create a comprehensive summary:

## Grafana K8s Operator Charm - Port Management Analysis

### **Summary**

This is a **Kubernetes charm** (type: `charm`) for Grafana, as defined in `/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C3/charmcraft.yaml`.

---

### **1. Port-Related Function Usage in src/**

All port management happens in **`/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C3/src/charm.py`**:

| Function | Line | Context |
|----------|------|---------|
| `self._set_ports()` | 428 | Called in `_reconcile()` method |
| `self.unit.opened_ports()` | 651 | Gets current open ports |
| `self.unit.close_port()` | 656 | Closes ports to remove |
| `self.unit.open_port()` | 660 | Opens new planned ports |

**Complete `_set_ports()` method** (lines 648-660):
```python
def _set_ports(self):
    """Open necessary (and close no longer needed) workload ports."""
    planned_ports = {Port(protocol="tcp", port=WORKLOAD_PORT)} if self.unit.is_leader() else set()
    actual_ports = self.unit.opened_ports()

    # Ports may change across an upgrade, so need to sync
    ports_to_close = actual_ports.difference(planned_ports)
    for p in ports_to_close:
        self.unit.close_port(p.protocol, p.port)

    new_ports_to_open = planned_ports.difference(actual_ports)
    for p in new_ports_to_open:
        self.unit.open_port(p.protocol, p.port)
```

---

### **2. Main Charm Files**

**Primary charm file**: `/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C3/src/charm.py`

**Class**: `GrafanaCharm(CharmBase)` (line 92)
- Handles reconciliation through `_reconcile()` method (line 426)
- Manages port configuration for Kubernetes charm instances

**Key imports** (line 36):
```python
from ops.model import Port
```

---

### **3. Port-Related Configuration & Constants**

**File**: `/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C3/src/constants.py`

```python
PROFILING_PORT = 8080      # (line 26) - Grafana diagnostics profiling port
WORKLOAD_PORT = 3000       # (line 27) - Main Grafana HTTP server port
METRICS_PATH = "/metrics"  # (line 28) - Metrics endpoint
```

---

### **4. Port Usage Across Codebase**

#### **In charm.py:**
- Line 139: `IngressPerAppRequirer(self, port=WORKLOAD_PORT, ...)`
- Line 184-186: `MetricsEndpointProvider` with `ports=[WORKLOAD_PORT]`
- Line 187-189: `ProfilingEndpointProvider` with `ports=[PROFILING_PORT]`
- Line 210: Catalogue item with `urls=[f"{self.app.name}:{WORKLOAD_PORT}"]`
- Line 268: `f"{self._scheme}://{self._fqdn}:{WORKLOAD_PORT}"`
- Line 315: `job = {"static_configs": [{"targets": [f"*:{PROFILING_PORT}"]}], ...}`
- Line 438: `self.ingress.provide_ingress_requirements(scheme=self._scheme, port=WORKLOAD_PORT)`

#### **In grafana.py:**
- Line 192: `"GF_DIAGNOSTICS_PROFILING_PORT": str(PROFILING_PORT)` - Enables Grafana profiling
- Line 214: `"GF_SERVER_HTTP_PORT": str(WORKLOAD_PORT)` - Sets Grafana HTTP port

---

### **5. Port Management Pattern**

**Key Pattern**: Leadership-based port opening
```python
# Only the leader unit opens the port
planned_ports = {Port(protocol="tcp", port=WORKLOAD_PORT)} if self.unit.is_leader() else set()
```

**Behavior**:
1. Only leader units open ports (TCP on port 3000)
2. Non-leader units don't open any ports (empty set)
3. Syncs ports across upgrades (closes old, opens new)
4. Uses set difference to track changes

---

### **6. Charm Type Information**

From `charmcraft.yaml`:
- **Type**: Kubernetes charm (`type: charm`)
- **Name**: `grafana-k8s`
- **Requires Juju \>= 3.6**
- **Container**: `grafana` using OCI image
- **Storage**: `database` (filesystem at `/var/lib/grafana`)

The charm handles ingress, metrics scraping, and profiling endpoint exposure through various provider relations.


---

<sub>⏱️ 1m 32s</sub>

### 💬 Copilot

Now I have a clear picture. Let me look at the actual charm.py to make the targeted changes.

---

<sub>⏱️ 1m 32s</sub>

### ✅ `bash`

**Find all port-related code in charm.py**

$ grep -n "Port\|open_port\|close_port\|set_ports\|opened_ports" /tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C3/src/charm.py

<details>
<summary>9 lines</summary>

```
36:from ops.model import Port
428:        self._set_ports()
648:    def _set_ports(self):
650:        planned_ports = {Port(protocol="tcp", port=WORKLOAD_PORT)} if self.unit.is_leader() else set()
651:        actual_ports = self.unit.opened_ports()
653:        # Ports may change across an upgrade, so need to sync
656:            self.unit.close_port(p.protocol, p.port)
660:            self.unit.open_port(p.protocol, p.port)
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 1m 37s</sub>

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C3/src/charm.py.**

/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C3/src/charm.py (lines 34-40)

<details>
<summary>7 lines</summary>

```
34.     RelationChangedEvent,
35. )
36. from ops.model import Port
37. from secret_storage import SecretStorage
38. 
39. from charms.catalogue_k8s.v1.catalogue import CatalogueConsumer, CatalogueItem
40. from charms.certificate_transfer_interface.v1.certificate_transfer import (
```

</details>


---

<sub>⏱️ 1m 37s</sub>

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C3/src/charm.py.**

/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C3/src/charm.py (lines 645-665)

<details>
<summary>21 lines</summary>

```
645.             env_vars[auth_var_prefix + str(var).upper()] = str(conf[auth_mode][var])
646.         return env_vars
647. 
648.     def _set_ports(self):
649.         """Open necessary (and close no longer needed) workload ports."""
650.         planned_ports = {Port(protocol="tcp", port=WORKLOAD_PORT)} if self.unit.is_leader() else set()
651.         actual_ports = self.unit.opened_ports()
652. 
653.         # Ports may change across an upgrade, so need to sync
654.         ports_to_close = actual_ports.difference(planned_ports)
655.         for p in ports_to_close:
656.             self.unit.close_port(p.protocol, p.port)
657. 
658.         new_ports_to_open = planned_ports.difference(actual_ports)
659.         for p in new_ports_to_open:
660.             self.unit.open_port(p.protocol, p.port)
661. 
662.     def _resource_reqs_from_config(self) -> ResourceRequirements:
663.         limits = {"cpu": self.model.config.get("cpu"), "memory": self.model.config.get("memory")}
664.         requests = {"cpu": "0.25", "memory": "200Mi"}
665.         return adjust_resource_requirements(limits, requests, adhere_to_requests=True)
```

</details>


---

<sub>⏱️ 1m 43s</sub>

### 💬 Copilot

Now I'll make the changes: replace the manual diff logic with `set_ports()` and remove the unused `Port` import.

---

<sub>⏱️ 1m 43s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C3/src/charm.py.**

/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C3/src/charm.py

```
File /tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C3/src/charm.py updated with changes.
```


---

<sub>⏱️ 1m 43s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C3/src/charm.py.**

/tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C3/src/charm.py

```
File /tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C3/src/charm.py updated with changes.
```


---

<sub>⏱️ 1m 48s</sub>

### 💬 Copilot

Now let's verify the changes look correct and run the tests:

---

<sub>⏱️ 1m 48s</sub>

### ✅ `bash`

**Verify port-related changes**

$ grep -n "Port\|open_port\|close_port\|set_ports\|opened_ports" /tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C3/src/charm.py

```
427:        self._set_ports()
647:    def _set_ports(self):
649:        self.unit.set_ports(*([WORKLOAD_PORT] if self.unit.is_leader() else []))
<exited with exit code 0>
```


---

<sub>⏱️ 1m 52s</sub>

### ✅ `bash`

**Check tox config for test commands**

$ cd /tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C3 && cat tox.ini | head -40

<details>
<summary>36 lines</summary>

```
# Copyright 2021 Canonical Ltd.
# See LICENSE file for licensing details.
[tox]
skipsdist=True
skip_missing_interpreters = True
envlist = lint, static, unit

[vars]
src_path = {toxinidir}/src
tst_path = {toxinidir}/tests
lib_path = {toxinidir}/lib/charms/grafana_k8s
all_path = {[vars]src_path} {[vars]tst_path} {[vars]lib_path}
uv_flags = --frozen --isolated --extra=dev

[testenv]
allowlist_externals = uv
basepython = python3
setenv =
  PYTHONPATH = {toxinidir}:{toxinidir}/lib:{[vars]src_path}
  PYTHONBREAKPOINT=ipdb.set_trace
  PY_COLORS=1
passenv =
  PYTHONPATH
  CHARM_PATH

[testenv:lock]
description = Update uv.lock with the latest deps
commands =
  uv lock --upgrade --no-cache

[testenv:lint]
description = Lint the code
commands =
    uv run {[vars]uv_flags} ruff check {[vars]all_path}

[testenv:static]
description = Run static checks
allowlist_externals =
  {[testenv]allowlist_externals}
  /usr/bin/env
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 2m 18s</sub>

### ✅ `bash`

**Run linting and unit tests**

$ cd /tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C3 && tox -e lint,static,unit 2>&1 | tail -50

<details>
<summary>45 lines</summary>

```
self.harness = Harness(ProviderCharm, meta=CONSUMER_META)

tests/unit/test_source_provider.py::TestAlertManagerProvider::test_provider_sets_scrape_data
  /tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C3/tests/unit/test_source_provider.py:106: PendingDeprecationWarning: Harness is deprecated. For the recommended approach, see: https://documentation.ubuntu.com/ops/latest/howto/write-unit-tests-for-a-charm/
    self.harness = Harness(AlertManagerProviderCharm, meta=CONSUMER_META)

tests/unit/test_source_provider.py::TestMimirProvider::test_provider_sets_scrape_data
  /tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C3/tests/unit/test_source_provider.py:125: PendingDeprecationWarning: Harness is deprecated. For the recommended approach, see: https://documentation.ubuntu.com/ops/latest/howto/write-unit-tests-for-a-charm/
    self.harness = Harness(MimirProviderCharm, meta=CONSUMER_META)

tests/unit/test_source_provider.py::TestSourceProviderWithIngress::test_provider_unit_sets_scheme_if_not_provided
tests/unit/test_source_provider.py::TestSourceProviderWithIngress::test_provider_unit_sets_source_uri_if_provided
  /tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C3/tests/unit/test_source_provider.py:154: PendingDeprecationWarning: Harness is deprecated. For the recommended approach, see: https://documentation.ubuntu.com/ops/latest/howto/write-unit-tests-for-a-charm/
    self.harness = Harness(ProviderCharmWithIngress, meta=CONSUMER_META)

tests/unit/test_source_provider.py::TestFollowerSourceProvider::test_ingressed_shares_uri
tests/unit/test_source_provider.py::TestFollowerSourceProvider::test_not_ingressed_does_not_share_uri
  /tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C3/tests/unit/test_source_provider.py:188: PendingDeprecationWarning: Harness is deprecated. For the recommended approach, see: https://documentation.ubuntu.com/ops/latest/howto/write-unit-tests-for-a-charm/
    self.harness = Harness(ProviderCharmWithIngress, meta=CONSUMER_META)

tests/unit/test_source_provider.py::TestDashboardProviderNoRefreshEvent::test_provider_instantiates_correctly
  /tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C3/tests/unit/test_source_provider.py:239: PendingDeprecationWarning: Harness is deprecated. For the recommended approach, see: https://documentation.ubuntu.com/ops/latest/howto/write-unit-tests-for-a-charm/
    self.harness = Harness(ProviderCharmNoRefreshEvent, meta=CONSUMER_META)

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
================= 122 passed, 1 skipped, 112 warnings in 4.25s =================
unit: commands[3]> uv run --frozen --isolated --extra=dev coverage report
warning: The `requires-python` specifier (`~=3.8`) in `grafana-k8s` uses the tilde specifier (`~=`) without a patch version. This will be interpreted as `>=3.8, <4`. Did you mean `~=3.8.0` to constrain the version as `>=3.8.0, <3.9`? We recommend only using the tilde specifier with a patch version to avoid ambiguity.
Installed 119 packages in 48ms
Name                                             Stmts   Miss Branch BrPart  Cover   Missing
--------------------------------------------------------------------------------------------
lib/charms/grafana_k8s/v0/grafana_auth.py          149     19     40      8    86%   246-248, 252, 259-260, 331, 333, 351, 367, 473-474, 493, 570, 572, 574, 576, 589-590
lib/charms/grafana_k8s/v0/grafana_dashboard.py     701    254    288     39    59%   399-402, 414-423, 435-442, 470-487, 522, 528, 534, 539-543, 571->570, 618->641, 629->628, 646->642, 685, 689-693, 704, 710-728, 838, 842, 844-850, 872, 932->935, 960-963, 971-972, 1019-1021, 1023, 1077-1080, 1084, 1092-1094, 1171-1172, 1228->exit, 1230, 1243->exit, 1249-1251, 1255, 1266->exit, 1283->exit, 1308->1307, 1314->exit, 1325->exit, 1335-1346, 1373, 1451, 1467->1470, 1470->exit, 1475-1477, 1504-1507, 1527-1532, 1565-1566, 1587-1616, 1635, 1641-1645, 1709-1712, 1718-1719, 1776-1801, 1808-1809, 1813-1830, 1835-1842, 1846-1863, 1885-1920, 1924-1993, 2003-2029, 2032, 2053, 2057-2058, 2063-2082, 2086-2116, 2121, 2123-2124, 2141-2143, 2152-2154
lib/charms/grafana_k8s/v0/grafana_metadata.py       46      1      8      1    96%   162
lib/charms/grafana_k8s/v0/grafana_source.py        306     45    112     16    83%   183-187, 194-197, 209-218, 230-237, 262, 268, 274, 279-283, 393-394, 405->408, 440-445, 455, 617, 638-641, 683, 686, 724->727, 727->exit, 765, 770->exit, 797-803, 816-817
src/charm.py                                       287     51     66     17    77%   293, 330-331, 408, 430-431, 433, 439, 448, 457-461, 464-465, 501, 513, 528, 544-551, 563-604, 618, 619->exit, 621->exit, 637-638, 652-654, 657
src/constants.py                                    19      0      0      0   100%
src/custom_ini_config.py                            48      0      8      1    98%   79->78
src/grafana.py                                     213     48     70     16    75%   92-100, 147, 179, 188, 257->exit, 282, 300-304, 329-339, 342-343, 353-362, 365-367, 409->exit, 415->exit, 426, 432-438, 442, 467-471, 484-485, 507->exit, 509-510, 521-522
src/grafana_client.py                               35      9      2      0    76%   73-74, 89-99
src/grafana_config.py                              105     16     20      3    85%   62-64, 71-76, 114, 160-175
src/models.py                                       23      0      0      0   100%
src/relation.py                                     20      0      6      1    96%   24->exit
src/secret_storage.py                               37      4      4      0    90%   49-52
--------------------------------------------------------------------------------------------
TOTAL                                             1989    447    624    102    74%
  lint: OK (0.27=setup[0.04]+cmd[0.23] seconds)
  static: OK (4.38=setup[0.03]+cmd[4.35,0.00] seconds)
  unit: OK (15.81=setup[0.04]+cmd[1.07,5.53,8.82,0.36] seconds)
  congratulations :) (20.47 seconds)
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 2m 22s</sub>

### 💬 Copilot

All 122 tests pass. Let me commit the changes:

---

<sub>⏱️ 2m 22s</sub>

### ✅ `bash`

**Show the diff**

$ cd /tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C3 && git diff

<details>
<summary>29 lines</summary>

```diff
diff --git a/src/charm.py b/src/charm.py
index 71972f3..2bb168a 100755
--- a/src/charm.py
+++ b/src/charm.py
@@ -33,7 +33,6 @@ from ops.charm import (
     CharmBase,
     RelationChangedEvent,
 )
-from ops.model import Port
 from secret_storage import SecretStorage
 
 from charms.catalogue_k8s.v1.catalogue import CatalogueConsumer, CatalogueItem
@@ -647,17 +646,7 @@ class GrafanaCharm(CharmBase):
 
     def _set_ports(self):
         """Open necessary (and close no longer needed) workload ports."""
-        planned_ports = {Port(protocol="tcp", port=WORKLOAD_PORT)} if self.unit.is_leader() else set()
-        actual_ports = self.unit.opened_ports()
-
-        # Ports may change across an upgrade, so need to sync
-        ports_to_close = actual_ports.difference(planned_ports)
-        for p in ports_to_close:
-            self.unit.close_port(p.protocol, p.port)
-
-        new_ports_to_open = planned_ports.difference(actual_ports)
-        for p in new_ports_to_open:
-            self.unit.open_port(p.protocol, p.port)
+        self.unit.set_ports(*([WORKLOAD_PORT] if self.unit.is_leader() else []))
 
     def _resource_reqs_from_config(self) -> ResourceRequirements:
         limits = {"cpu": self.model.config.get("cpu"), "memory": self.model.config.get("memory")}
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 2m 29s</sub>

### ✅ `bash`

**Commit the changes**

$ cd /tmp/ops-upgrade-experiment/grafana-k8s-operator__set-ports__C3 && git add src/charm.py && git commit -m "refactor: replace open/close_port with declarative set_ports()

Use the ops 2.7.0 Unit.set_ports() API instead of manually diffing
opened_ports() against desired ports and calling open_port()/close_port()
individually. This simplifies _set_ports() to a single declarative call.

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"

```
[detached HEAD 34f3a86] refactor: replace open/close_port with declarative set_ports()
 1 file changed, 1 insertion(+), 12 deletions(-)
<exited with exit code 0>
```


---

<sub>⏱️ 2m 35s</sub>

### ✅ `task_complete`

**Replaced the manual `open_port()`/`close_port()` pattern ...**

<details>
<summary>Arguments</summary>

```json
{
  "summary": "Replaced the manual `open_port()`/`close_port()` pattern in `src/charm.py` with the declarative `Unit.set_ports()` API:\n\n- **Removed** the manual diff logic in `_set_ports()` that called `opened_ports()`, computed set differences, and looped to open/close ports individually\n- **Replaced** with a single `self.unit.set_ports(*([WORKLOAD_PORT] if self.unit.is_leader() else []))` — passing the port for leader units, or no args (clears all) for non-leaders\n- **Removed** the now-unused `from ops.model import Port` import\n\nAll 122 unit tests pass."
}
```

</details>

<details>
<summary>5 lines</summary>

```
Replaced the manual `open_port()`/`close_port()` pattern in `src/charm.py` with the declarative `Unit.set_ports()` API:

- **Removed** the manual diff logic in `_set_ports()` that called `opened_ports()`, computed set differences, and looped to open/close ports individually
- **Replaced** with a single `self.unit.set_ports(*([WORKLOAD_PORT] if self.unit.is_leader() else []))` — passing the port for leader units, or no args (clears all) for non-leaders
- **Removed** the now-unused `from ops.model import Port` import

All 122 unit tests pass.
```

</details>


---

<sub>⏱️ 2m 35s</sub>

### ✓ Task Complete

Replaced the manual `open_port()`/`close_port()` pattern in `src/charm.py` with the declarative `Unit.set_ports()` API:

- **Removed** the manual diff logic in `_set_ports()` that called `opened_ports()`, computed set differences, and looped to open/close ports individually
- **Replaced** with a single `self.unit.set_ports(*([WORKLOAD_PORT] if self.unit.is_leader() else []))` — passing the port for leader units, or no args (clears all) for non-leaders
- **Removed** the now-unused `from ops.model import Port` import

All 122 unit tests pass.

---

<sub>Generated by [GitHub Copilot CLI](https://github.com/features/copilot/cli)</sub>
