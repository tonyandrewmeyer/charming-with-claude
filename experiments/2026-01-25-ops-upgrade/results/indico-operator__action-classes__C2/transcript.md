# 🤖 Copilot CLI Session

> **Session ID:** `813ded4a-f795-4676-a630-9ec57a266af4`
> **Duration:** 5m 38s
> **Exported:** 2/18/2026, 20:20:51 PM

<sub>⏱️ 4s</sub>

### 👤 User

ops 2.23.0 added support for defining action parameters as Python dataclasses or Pydantic models, loaded via ActionEvent.load_params(), replacing raw dictionary access to event.params. Learn how to use that feature and update this charm to make use of it.

---

<sub>⏱️ 11s</sub>

### ✅ `view`

**/tmp/ops-upgrade-experiment/indico-operator__action-classes__C2**

/tmp/ops-upgrade-experiment/indico-operator__action-classes__C2

<details>
<summary>38 lines</summary>

```
.baseline_commit
.copilot-collections.yaml
.dockerignore
.git
.github
.gitignore
.jujuignore
.licenserc.yaml
.trivyignore
.vale
.vale.ini
.woke.yaml
CODEOWNERS
LICENSE
Makefile
Makefile.docs
README.md
SECURITY.md
ZAP.md
actions.yaml
charmcraft.yaml
config.yaml
docs
icon.svg
indico_rock
lib
load_tests
metadata.yaml
nginx_rock
pyproject.toml
renovate.json
requirements.txt
src
terraform
tests
tox.ini
trivy.yaml
zap_rules.tsv
```

</details>


---

<sub>⏱️ 12s</sub>

### ✅ `bash`

**View actions.yaml**

$ cat /tmp/ops-upgrade-experiment/indico-operator__action-classes__C2/actions.yaml

<details>
<summary>22 lines</summary>

```
# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

refresh-external-resources:
  description: Pull changes from the customization repository, reload uWSGI and upgrade the external plugins
add-admin:
  description: Add an admin to Indico
  params:
    email:
      type: string
      description: User email.
    password:
      type: string
      description: User password.
  required: [email, password]
anonymize-user:
  description: Anonymize stored personal data to facilitate GDPR compliance
  params:
    email:
      type: string
      description: User email (or a list of emails separated by comma). Maximum of 50 emails.
  required: [email]
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 12s</sub>

### ✅ `bash`

**Find main charm files**

$ cat /tmp/ops-upgrade-experiment/indico-operator__action-classes__C2/src/charm.py 2>/dev/null || find /tmp/ops-upgrade-experiment/indico-operator__action-classes__C2/src -name "*.py" | head -20

<details>
<summary>8 lines</summary>

```
Output too large to read at once (39.2 KB). Saved to: /tmp/copilot-tool-output-1773199524435-ux9xkt.txt
Consider using tools like grep (for searching), head/tail (for viewing start/end), view with view_range (for specific sections), or jq (for JSON) to examine portions of the output.

Preview (first 500 chars):
#!/usr/bin/env python3

# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

"
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 18s</sub>

### ✅ `bash`

**Find action parameter usage in charm.py**

$ grep -n "event.params\|ActionEvent\|action_params\|\.params\[" /tmp/ops-upgrade-experiment/indico-operator__action-classes__C2/src/charm.py | head -40

<details>
<summary>15 lines</summary>

```
25:from ops.charm import ActionEvent, CharmBase, HookEvent, PebbleReadyEvent, RelationDepartedEvent
836:    def _refresh_external_resources_action(self, event: ActionEvent) -> None:
898:    def _add_admin_action(self, event: ActionEvent) -> None:
911:            event.params["email"],
912:            event.params["password"],
924:                event.set_results({"user": f"{event.params['email']}", "output": output})
930:                    f"Failed to create admin {event.params['email']}: {ex.stdout!r}"
933:    def _execute_anonymize_cmd(self, event: ActionEvent) -> Iterator[str]:
937:            event (ActionEvent): Event triggered by the anonymize-user action
944:        for email in event.params["email"].split(EMAIL_LIST_SEPARATOR):
972:                fail_msg = f"Failed to anonymize user {event.params['email']}: {ex.stdout!r}"
976:    def _anonymize_user_action(self, event: ActionEvent) -> None:
985:        if len(event.params["email"].split(EMAIL_LIST_SEPARATOR)) > EMAIL_LIST_MAX:
996:                "user": f"{event.params['email']}",
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 18s</sub>

### ✅ `bash`

**Find action handler methods**

$ grep -n "def.*action\|_on_.*action\|ActionEvent" /tmp/ops-upgrade-experiment/indico-operator__action-classes__C2/src/charm.py

<details>
<summary>7 lines</summary>

```
25:from ops.charm import ActionEvent, CharmBase, HookEvent, PebbleReadyEvent, RelationDepartedEvent
836:    def _refresh_external_resources_action(self, event: ActionEvent) -> None:
898:    def _add_admin_action(self, event: ActionEvent) -> None:
933:    def _execute_anonymize_cmd(self, event: ActionEvent) -> Iterator[str]:
937:            event (ActionEvent): Event triggered by the anonymize-user action
976:    def _anonymize_user_action(self, event: ActionEvent) -> None:
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 27s</sub>

### ✅ `web_search`

**ops 2.23.0 ActionEvent load_params dataclass pydantic action parameters Python charm**

<details>
<summary>Arguments</summary>

```json
{
  "query": "ops 2.23.0 ActionEvent load_params dataclass pydantic action parameters Python charm"
}
```

</details>

````
{"type":"text","text":{"value":"In ops 2.23.0 (the Operator Framework for Juju charms), handling action parameters in a strongly-typed way is greatly improved with the ActionEvent.load_params method. This method can be used to load and validate action parameters directly into a Python dataclass or a Pydantic BaseModel subclass, bringing modern type safety and clarity to charm development.\n\nHere's how it works and some best practices:\n\n### Using ActionEvent.load_params\n\n- `ActionEvent.load_params(cls)` reads the raw action parameters and loads them into an instance of the provided class (`cls`), matching Juju action parameter keys to Python attribute names (converting dashes to underscores).\n- You can use either a dataclass or a Pydantic BaseModel for your parameter class.\n- Extra parameters in the action call that are not present in your dataclass or Pydantic model are ignored.\n- If the data is invalid (not matching the type annotations), an exception is raised (configurable to `raise` or `fail`).\n\n#### Example with Pydantic\n\n```python\nfrom ops import CharmBase, ActionEvent\nfrom pydantic import BaseModel\n\nclass BackupParams(BaseModel):\n    filename: str\n    compress: bool = False\n\ndef _on_backup(self, event: ActionEvent):\n    params = event.load_params(BackupParams)\n    # params.filename and params.compress validated and ready to use\n```\n\n#### Example with Dataclass\n\n```python\nfrom dataclasses import dataclass\nfrom ops import CharmBase, ActionEvent\n\n@dataclass\nclass RestoreParams:\n    filename: str\n\ndef _on_restore(self, event: ActionEvent):\n    params = event.load_params(RestoreParams)\n    # params.filename validated and ready to use\n```\n\n### Advantages and Considerations\n\n- **Pydantic models** offer rich validation, error messaging, and support for default values and extra fields (if configured).\n- **Dataclasses** offer lightweight typing but require all fields to be known in advance. They do not natively support ignoring extra arguments unless you add workarounds【3:6†source】.\n- Parameters passed by users in `juju run-action` like `--filename=test.txt --compress=true` are automatically matched and type-checked.\n- In both cases, only the fields present in your parameter class are populated; others are ignored.\n\n### Error Handling\n\n- If the action's parameters do not validate, load_params will raise a `ValueError` (by default) or can record the failure via `fail` error policy.\n\n### References and Further Reading\n\n- The official ops framework documentation explains `ActionEvent` and `load_params` with examples for both Pydantic and dataclass use cases【3:0†source】.\n- The Charmhub Data Platform Libraries also provide patterns and helper libraries for parameter validation and model usage in charms, often leveraging Pydantic for richer validation features【3:5†source】.\n\n### Conclusion\n\nUsing `ActionEvent.load_params` in ops 2.23.0 greatly simplifies the validation and consumption of action parameters in Python charms. Prefer Pydantic if you want advanced validation (e.g., regex, constraints, post-init hooks), or use standard dataclasses for simpler, lightweight use cases.\n\nFor official guidance and practical usage examples, see:\n- Ops 2.x Documentation on ActionEvent and load_params【3:0†source】\n- Charmhub Data Models library for charm parameter validation patterns【3:5†source】\n\nLet me know if you need a concrete code sample or have questions about error handling or integrating this in your own charm!","annotations":[{"text":"【3:6†source】","start_index":1968,"end_index":1980,"url_citation":{"title":"Pydantic & Dataclasses – How to Allow Extra Kwargs - JCharisTech","url":"https://blog.jcharistech.com/2024/02/11/pydantic-dataclasses-how-to-allow-extra-kwargs/"}},{"text":"【3:0†source】","start_index":2564,"end_index":2576,"url_citation":{"title":"ops - Ops 2.x documentation","url":"https://documentation.ubuntu.com/ops/2.x/reference/ops/"}},{"text":"【3:5†source】","start_index":2768,"end_index":2780,"url_citation":{"title":"charmhub.io","url":"https://charmhub.io/data-platform-libs/libraries/data_models/download"}},{"text":"【3:0†source】","start_index":3203,"end_index":3215,"url_citation":{"title":"ops - Ops 2.x documentation","url":"https://documentation.ubuntu.com/ops/2.x/reference/ops/"}},{"text":"【3:5†source】","start_index":3286,"end_index":3298,"url_citation":{"title":"charmhub.io","url":"https://charmhub.io/data-platform-libs/libraries/data_models/download"}}]},"bing_searches":[{"text":"ops 2.23.0 ActionEvent load_params dataclass pydantic action parameters Python charm","url":"https://www.bing.com/search?q=ops+2.23.0+ActionEvent+load_params+dataclass+pydantic+action+parameters+Python+charm"}],"annotations":null}
````


---

<sub>⏱️ 33s</sub>

### ✅ `bash`

**Check ops version**

$ python3 -c "import ops; print(ops.__version__)" 2>/dev/null || pip show ops 2>/dev/null | grep Version

```
2.23.2
<exited with exit code 0>
```


---

<sub>⏱️ 33s</sub>

### ✅ `bash`

**Check ops version in requirements**

$ grep -n "^ops\|ops==" /tmp/ops-upgrade-experiment/indico-operator__action-classes__C2/requirements.txt

```
2:ops>=2.0.0,<3.0.0
<exited with exit code 0>
```


---

<sub>⏱️ 32s</sub>

### ✅ `view`

**/tmp/ops-upgrade-experiment/indico-operator__action-classes__C2/src/charm.py**

/tmp/ops-upgrade-experiment/indico-operator__action-classes__C2/src/charm.py (lines 890-1000)

<details>
<summary>111 lines</summary>

```
890.         Returns:
891.             If secrets are supported or not.
892.         """
893.         juju_version = JujuVersion.from_environ()
894.         # Because we're only using secrets in a peer relation we don't need to
895.         # check if the other end of a relation also supports secrets...
896.         return juju_version.has_secrets
897. 
898.     def _add_admin_action(self, event: ActionEvent) -> None:
899.         """Add a new user to Indico.
900. 
901.         Args:
902.             event: Event triggered by the add_admin action
903.         """
904.         container = self.unit.get_container("indico")
905.         indico_env_config = self._get_indico_env_config_str(container)
906. 
907.         cmd = [
908.             "/usr/bin/indico",
909.             "autocreate",
910.             "admin",
911.             event.params["email"],
912.             event.params["password"],
913.         ]
914. 
915.         if container.can_connect():
916.             process = container.exec(
917.                 cmd,
918.                 user="indico",
919.                 working_dir="/srv/indico",
920.                 environment=indico_env_config,
921.             )
922.             try:
923.                 output = process.wait_output()
924.                 event.set_results({"user": f"{event.params['email']}", "output": output})
925.             except ExecError as ex:
926.                 logger.exception("Action add-admin failed: %s", ex.stdout)
927. 
928.                 event.fail(
929.                     # Parameter validation errors are printed to stdout
930.                     f"Failed to create admin {event.params['email']}: {ex.stdout!r}"
931.                 )
932. 
933.     def _execute_anonymize_cmd(self, event: ActionEvent) -> Iterator[str]:
934.         """Execute anonymize command for each email.
935. 
936.         Args:
937.             event (ActionEvent): Event triggered by the anonymize-user action
938. 
939.         Yields:
940.             Iterator[str]: Output of each command execution
941.         """
942.         container = self.unit.get_container("indico")
943.         indico_env_config = self._get_indico_env_config_str(container)
944.         for email in event.params["email"].split(EMAIL_LIST_SEPARATOR):
945.             cmd = [
946.                 "/usr/bin/indico",
947.                 "anonymize",
948.                 "user",
949.                 email,
950.             ]
951. 
952.             if not container.can_connect():
953.                 logger.error(
954.                     "Action anonymize-user failed: cannot connect to the Indico workload container"
955.                 )
956.                 self.unit.status = WaitingStatus(
957.                     "Waiting to be able to connect to workload container"
958.                 )
959.                 return
960. 
961.             process = container.exec(
962.                 cmd,
963.                 user="indico",
964.                 working_dir="/srv/indico",
965.                 environment=indico_env_config,
966.             )
967.             try:
968.                 out = process.wait_output()
969.                 yield out[0].replace("\n", "")
970.             except ExecError as ex:
971.                 logger.exception("Action anonymize-user failed: %s", ex.stdout)
972.                 fail_msg = f"Failed to anonymize user {event.params['email']}: {ex.stdout!r}"
973.                 event.fail("Failed to anonymize one or more users, please verify the results.")
974.                 yield fail_msg
975. 
976.     def _anonymize_user_action(self, event: ActionEvent) -> None:
977.         """Anonymize user in Indico.
978. 
979.         If find an error, the action will fail. All the results will be set until the error
980.         has happened.
981. 
982.         Args:
983.             event: Event triggered by the anonymize-user action
984.         """
985.         if len(event.params["email"].split(EMAIL_LIST_SEPARATOR)) > EMAIL_LIST_MAX:
986.             max_reached_msg = (
987.                 "Failed to anonymize user: "
988.                 f"List of more than {EMAIL_LIST_MAX} emails are not allowed"
989.             )
990.             logger.error("Action anonymize-user failed: %s", max_reached_msg)
991.             event.fail(max_reached_msg)
992.             return
993.         output_list = list(self._execute_anonymize_cmd(event))
994.         event.set_results(
995.             {
996.                 "user": f"{event.params['email']}",
997.                 "output": EMAIL_LIST_SEPARATOR.join(output_list),
998.             }
999.         )
1000.
```

</details>


---

<sub>⏱️ 38s</sub>

### ✅ `view`

**/tmp/ops-upgrade-experiment/indico-operator__action-classes__C2/src/charm.py**

/tmp/ops-upgrade-experiment/indico-operator__action-classes__C2/src/charm.py (lines 1-50)

<details>
<summary>50 lines</summary>

```
1. #!/usr/bin/env python3
2. 
3. # Copyright 2025 Canonical Ltd.
4. # See LICENSE file for licensing details.
5. 
6. """Charm for Indico on kubernetes."""
7. 
8. # pylint: disable=too-many-lines
9. 
10. import logging
11. import os
12. import secrets
13. import typing
14. from re import findall
15. from typing import Any, Dict, Iterator, List, Optional, Tuple
16. from urllib.parse import urlparse
17. 
18. import charms.loki_k8s.v0.loki_push_api
19. import ops
20. from charms.grafana_k8s.v0.grafana_dashboard import GrafanaDashboardProvider
21. from charms.loki_k8s.v0.loki_push_api import LogProxyConsumer
22. from charms.nginx_ingress_integrator.v0.nginx_route import require_nginx_route
23. from charms.prometheus_k8s.v0.prometheus_scrape import MetricsEndpointProvider
24. from charms.redis_k8s.v0.redis import RedisRelationCharmEvents, RedisRequires
25. from ops.charm import ActionEvent, CharmBase, HookEvent, PebbleReadyEvent, RelationDepartedEvent
26. from ops.jujuversion import JujuVersion
27. from ops.main import main
28. from ops.model import ActiveStatus, BlockedStatus, Container, MaintenanceStatus, WaitingStatus
29. from ops.pebble import ExecError
30. 
31. from database_observer import DatabaseObserver
32. from s3_observer import S3Observer
33. from saml_observer import SamlObserver
34. from smtp_observer import SmtpObserver
35. from state import CharmConfigInvalidError, ProxyConfig, State
36. 
37. logger = logging.getLogger(__name__)
38. 
39. CELERY_PROMEXP_PORT = "9808"
40. DATABASE_NAME = "indico"
41. EMAIL_LIST_MAX = 50
42. EMAIL_LIST_SEPARATOR = ","
43. INDICO_CUSTOMIZATION_DIR = "/srv/indico/custom"
44. NGINX_PROMEXP_PORT = "9113"
45. PORT = 8080
46. STATSD_PROMEXP_PORT = "9102"
47. SAML_GROUPS_PLUGIN_NAME = "saml_groups"
48. 
49. UWSGI_TOUCH_RELOAD = "/srv/indico/indico.wsgi"
50.
```

</details>


---

<sub>⏱️ 39s</sub>

### ✅ `bash`

**Find class definitions and constants**

$ grep -n "EMAIL_LIST_SEPARATOR\|EMAIL_LIST_MAX\|^class " /tmp/ops-upgrade-experiment/indico-operator__action-classes__C2/src/charm.py | head -20

<details>
<summary>9 lines</summary>

```
41:EMAIL_LIST_MAX = 50
42:EMAIL_LIST_SEPARATOR = ","
52:class InvalidRedisNameError(Exception):
56:class IndicoOperatorCharm(CharmBase):  # pylint: disable=too-many-instance-attributes
944:        for email in event.params["email"].split(EMAIL_LIST_SEPARATOR):
985:        if len(event.params["email"].split(EMAIL_LIST_SEPARATOR)) > EMAIL_LIST_MAX:
988:                f"List of more than {EMAIL_LIST_MAX} emails are not allowed"
997:                "output": EMAIL_LIST_SEPARATOR.join(output_list),
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 56s</sub>

### 💬 Copilot

Now I have a clear picture. I'll add dataclasses for both action parameter sets and update the handlers to use `event.load_params()`.

---

<sub>⏱️ 56s</sub>

### ✅ `view`

**/tmp/ops-upgrade-experiment/indico-operator__action-classes__C2/src/charm.py**

/tmp/ops-upgrade-experiment/indico-operator__action-classes__C2/src/charm.py (lines 10-16)

<details>
<summary>7 lines</summary>

```
10. import logging
11. import os
12. import secrets
13. import typing
14. from re import findall
15. from typing import Any, Dict, Iterator, List, Optional, Tuple
16. from urllib.parse import urlparse
```

</details>


---

<sub>⏱️ 1m 0s</sub>

### ✅ `edit`

**/tmp/ops-upgrade-experiment/indico-operator__action-classes__C2/src/charm.py**

/tmp/ops-upgrade-experiment/indico-operator__action-classes__C2/src/charm.py

```
File /tmp/ops-upgrade-experiment/indico-operator__action-classes__C2/src/charm.py updated with changes.
```


---

<sub>⏱️ 1m 5s</sub>

### 💬 Copilot

Now add the dataclasses after the constants block:

---

<sub>⏱️ 1m 5s</sub>

### ✅ `view`

**/tmp/ops-upgrade-experiment/indico-operator__action-classes__C2/src/charm.py**

/tmp/ops-upgrade-experiment/indico-operator__action-classes__C2/src/charm.py (lines 48-58)

<details>
<summary>11 lines</summary>

```
48. SAML_GROUPS_PLUGIN_NAME = "saml_groups"
49. 
50. UWSGI_TOUCH_RELOAD = "/srv/indico/indico.wsgi"
51. 
52. 
53. class InvalidRedisNameError(Exception):
54.     """Represents invalid redis name error."""
55. 
56. 
57. class IndicoOperatorCharm(CharmBase):  # pylint: disable=too-many-instance-attributes
58.     """Charm for Indico on kubernetes.
```

</details>


---

<sub>⏱️ 1m 9s</sub>

### ✅ `edit`

**/tmp/ops-upgrade-experiment/indico-operator__action-classes__C2/src/charm.py**

/tmp/ops-upgrade-experiment/indico-operator__action-classes__C2/src/charm.py

```
File /tmp/ops-upgrade-experiment/indico-operator__action-classes__C2/src/charm.py updated with changes.
```


---

<sub>⏱️ 1m 20s</sub>

### 💬 Copilot

Now update `_add_admin_action` to use `event.load_params()`:

---

<sub>⏱️ 1m 20s</sub>

### ✅ `edit`

**/tmp/ops-upgrade-experiment/indico-operator__action-classes__C2/src/charm.py**

/tmp/ops-upgrade-experiment/indico-operator__action-classes__C2/src/charm.py

```
File /tmp/ops-upgrade-experiment/indico-operator__action-classes__C2/src/charm.py updated with changes.
```


---

<sub>⏱️ 1m 31s</sub>

### 💬 Copilot

Now update `_execute_anonymize_cmd` and `_anonymize_user_action`:

---

<sub>⏱️ 1m 31s</sub>

### ✅ `edit`

**/tmp/ops-upgrade-experiment/indico-operator__action-classes__C2/src/charm.py**

/tmp/ops-upgrade-experiment/indico-operator__action-classes__C2/src/charm.py

```
File /tmp/ops-upgrade-experiment/indico-operator__action-classes__C2/src/charm.py updated with changes.
```


---

<sub>⏱️ 1m 34s</sub>

### ✅ `view`

**/tmp/ops-upgrade-experiment/indico-operator__action-classes__C2/src/charm.py**

/tmp/ops-upgrade-experiment/indico-operator__action-classes__C2/src/charm.py (lines 990-1020)

<details>
<summary>31 lines</summary>

```
990.                 fail_msg = f"Failed to anonymize user {params.email}: {ex.stdout!r}"
991.                 event.fail("Failed to anonymize one or more users, please verify the results.")
992.                 yield fail_msg
993. 
994.     def _anonymize_user_action(self, event: ActionEvent) -> None:
995.         """Anonymize user in Indico.
996. 
997.         If find an error, the action will fail. All the results will be set until the error
998.         has happened.
999. 
1000.         Args:
1001.             event: Event triggered by the anonymize-user action
1002.         """
1003.         if len(event.params["email"].split(EMAIL_LIST_SEPARATOR)) > EMAIL_LIST_MAX:
1004.             max_reached_msg = (
1005.                 "Failed to anonymize user: "
1006.                 f"List of more than {EMAIL_LIST_MAX} emails are not allowed"
1007.             )
1008.             logger.error("Action anonymize-user failed: %s", max_reached_msg)
1009.             event.fail(max_reached_msg)
1010.             return
1011.         output_list = list(self._execute_anonymize_cmd(event))
1012.         event.set_results(
1013.             {
1014.                 "user": f"{event.params['email']}",
1015.                 "output": EMAIL_LIST_SEPARATOR.join(output_list),
1016.             }
1017.         )
1018. 
1019. 
1020. if __name__ == "__main__":  # pragma: no cover
```

</details>


---

<sub>⏱️ 1m 42s</sub>

### ✅ `edit`

**/tmp/ops-upgrade-experiment/indico-operator__action-classes__C2/src/charm.py**

/tmp/ops-upgrade-experiment/indico-operator__action-classes__C2/src/charm.py

```
File /tmp/ops-upgrade-experiment/indico-operator__action-classes__C2/src/charm.py updated with changes.
```


---

<sub>⏱️ 1m 46s</sub>

### 💬 Copilot

Now let's verify the changes look correct and run the tests:

---

<sub>⏱️ 1m 47s</sub>

### ✅ `bash`

**Verify no remaining event.params references**

$ grep -n "event.params\|load_params\|AddAdminParams\|AnonymizeUserParams" /tmp/ops-upgrade-experiment/indico-operator__action-classes__C2/src/charm.py

<details>
<summary>7 lines</summary>

```
54:class AddAdminParams:
62:class AnonymizeUserParams:
920:        params = event.load_params(AddAdminParams)
950:    def _execute_anonymize_cmd(self, event: ActionEvent, params: AnonymizeUserParams) -> Iterator[str]:
955:            params (AnonymizeUserParams): Parsed parameters for the anonymize-user action
1003:        params = event.load_params(AnonymizeUserParams)
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 1m 51s</sub>

### 💬 Copilot

All `event.params` references are replaced. Let's run the tests to verify nothing is broken:

---

<sub>⏱️ 1m 52s</sub>

### ✅ `bash`

**Run unit tests**

$ cd /tmp/ops-upgrade-experiment/indico-operator__action-classes__C2 && pip install -q tox && tox -e unit -- -x -q 2>&1 | tail -30

<details>
<summary>16 lines</summary>

```
error: externally-managed-environment

× This environment is externally managed
╰─> To install Python packages system-wide, try apt install
    python3-xyz, where xyz is the package you are trying to
    install.
    
    If you wish to install a non-Debian-packaged Python package,
    create a virtual environment using python3 -m venv path/to/venv.
    Then use path/to/venv/bin/python and path/to/venv/bin/pip. Make
    sure you have python3-full installed.
    
    If you wish to install a non-Debian packaged Python application,
    it may be easiest to use pipx install xyz, which will manage a
    virtual environment for you. Make sure you have pipx installed.
    
    See /usr/share/doc/python3.12/README.venv for more information.

note: If you believe this is a mistake, please contact your Python installation or OS distribution provider. You can override this, at the risk of breaking your Python installation or OS, by passing --break-system-packages.
hint: See PEP 668 for the detailed specification.
<exited with exit code 1>
```

</details>


---

<sub>⏱️ 1m 57s</sub>

### ✅ `bash`

**Check if tox is already installed**

$ which tox && tox --version

```
/home/ubuntu/.local/bin/tox
4.39.0 from /home/ubuntu/.local/share/uv/tools/tox/lib/python3.12/site-packages/tox/__init__.py
registered plugins:
    tox-uv-1.29.0 at /home/ubuntu/.local/share/uv/tools/tox/lib/python3.12/site-packages/tox_uv/plugin.py with uv==0.10.4
<exited with exit code 0>
```


---

<sub>⏱️ 2m 3s</sub>

### ✅ `bash`

**Run unit tests with tox**

$ cd /tmp/ops-upgrade-experiment/indico-operator__action-classes__C2 && tox -e unit -- -x -q 2>&1 | tail -40

<details>
<summary>38 lines</summary>

```
DEBUG    ops.model:model.py:2412 Pebble API is not ready; ConnectionError: Cannot connect to Pebble; did you forget to call begin_with_initial_hooks() or set_can_connect()?
DEBUG    ops.framework:framework.py:998 Emitting custom event <RedisRelationUpdatedEvent via IndicoOperatorCharm/on/redis_relation_updated[22]>.
DEBUG    ops.model:model.py:2412 Pebble API is not ready; ConnectionError: Cannot connect to Pebble; did you forget to call begin_with_initial_hooks() or set_can_connect()?
DEBUG    ops.framework:framework.py:998 Emitting custom event <RedisRelationUpdatedEvent via IndicoOperatorCharm/on/redis_relation_updated[24]>.
DEBUG    ops.model:model.py:2412 Pebble API is not ready; ConnectionError: Cannot connect to Pebble; did you forget to call begin_with_initial_hooks() or set_can_connect()?
DEBUG    ops.framework:framework.py:998 Emitting custom event <RedisRelationUpdatedEvent via IndicoOperatorCharm/on/redis_relation_updated[24]>.
DEBUG    ops.model:model.py:2412 Pebble API is not ready; ConnectionError: Cannot connect to Pebble; did you forget to call begin_with_initial_hooks() or set_can_connect()?
DEBUG    ops.framework:framework.py:998 Emitting custom event <RedisRelationUpdatedEvent via IndicoOperatorCharm/on/redis_relation_updated[26]>.
DEBUG    ops.model:model.py:2412 Pebble API is not ready; ConnectionError: Cannot connect to Pebble; did you forget to call begin_with_initial_hooks() or set_can_connect()?
DEBUG    ops.framework:framework.py:998 Emitting custom event <RedisRelationUpdatedEvent via IndicoOperatorCharm/on/redis_relation_updated[26]>.
DEBUG    ops.model:model.py:2412 Pebble API is not ready; ConnectionError: Cannot connect to Pebble; did you forget to call begin_with_initial_hooks() or set_can_connect()?
DEBUG    charms.grafana_k8s.v0.grafana_dashboard:grafana_dashboard.py:967 Processed dashboard '/tmp/ops-upgrade-experiment/indico-operator__action-classes__C2/src/grafana_dashboards/indico_service_health.json': replaced original uid '' with '0d416b01dd6ecd69b9eac00713fb7ca5811bd1e1'
DEBUG    charms.grafana_k8s.v0.grafana_dashboard:grafana_dashboard.py:967 Processed dashboard '/tmp/ops-upgrade-experiment/indico-operator__action-classes__C2/src/grafana_dashboards/celery.json': replaced original uid 'celery-32s3' with '091b7166a798d2c3c1c80c7c58cee48685df6674'
DEBUG    charms.grafana_k8s.v0.grafana_dashboard:grafana_dashboard.py:967 Processed dashboard '/tmp/ops-upgrade-experiment/indico-operator__action-classes__C2/src/grafana_dashboards/indico.json': replaced original uid '' with 'c79b131d619b838329208d62bf7fee48f012dddd'
DEBUG    ops.model:model.py:2412 Pebble API is not ready; ConnectionError: Cannot connect to Pebble; did you forget to call begin_with_initial_hooks() or set_can_connect()?
=============================== warnings summary ===============================
tests/unit_harness/test_actions.py::TestActions::test_add_admin
  /tmp/ops-upgrade-experiment/indico-operator__action-classes__C2/tests/unit_harness/test_base.py:21: PendingDeprecationWarning: Harness is deprecated. For the recommended approach, see: https://ops.readthedocs.io/en/latest/howto/write-unit-tests-for-a-charm.html
    self.harness = Harness(IndicoOperatorCharm)

tests/unit_harness/test_actions.py::TestActions::test_add_admin
  /tmp/ops-upgrade-experiment/indico-operator__action-classes__C2/lib/charms/data_platform_libs/v0/data_interfaces.py:1160: DeprecationWarning: JujuVersion.from_environ() is deprecated, use self.model.juju_version instead
    self._jujuversion = JujuVersion.from_environ()

tests/unit_harness/test_actions.py::TestActions::test_add_admin
tests/unit_harness/test_actions.py::TestActions::test_add_admin
tests/unit_harness/test_actions.py::TestActions::test_add_admin
tests/unit_harness/test_actions.py::TestActions::test_add_admin
tests/unit_harness/test_actions.py::TestActions::test_add_admin
  /tmp/ops-upgrade-experiment/indico-operator__action-classes__C2/src/charm.py:909: DeprecationWarning: JujuVersion.from_environ() is deprecated, use self.model.juju_version instead
    juju_version = JujuVersion.from_environ()

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ============================
FAILED tests/unit_harness/test_actions.py::TestActions::test_add_admin - AttributeError: Mock object has no attribute 'load_params'
!!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
=================== 1 failed, 1 passed, 7 warnings in 0.55s ====================
unit: exit 1 (1.07 seconds) /tmp/ops-upgrade-experiment/indico-operator__action-classes__C2> coverage run --source=/tmp/ops-upgrade-experiment/indico-operator__action-classes__C2/src/ -m pytest --ignore=/tmp/ops-upgrade-experiment/indico-operator__action-classes__C2/tests/integration -v --tb native -s -x -q pid=25324
  unit: FAIL code 1 (1.84=setup[0.77]+cmd[1.07] seconds)
  evaluation failed :( (1.85 seconds)
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 2m 8s</sub>

### 💬 Copilot

The tests need to be updated to mock `load_params`. Let me look at the test file:

---

<sub>⏱️ 2m 9s</sub>

### ✅ `bash`

**View action tests**

$ cat /tmp/ops-upgrade-experiment/indico-operator__action-classes__C2/tests/unit_harness/test_actions.py

<details>
<summary>331 lines</summary>

```
# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

"""Indico charm unit tests."""

# pylint:disable=duplicate-code,protected-access

import typing
from secrets import token_hex
from unittest.mock import DEFAULT, MagicMock, patch

from ops.charm import ActionEvent
from ops.model import Container
from ops.pebble import ExecError

from charm import EMAIL_LIST_MAX, EMAIL_LIST_SEPARATOR, IndicoOperatorCharm
from tests.unit_harness.test_base import TestBase


class TestActions(TestBase):
    """Indico charm unit tests."""

    @patch.object(Container, "exec")
    @patch("charm.secrets")
    def test_refresh_external_resources_when_customization_and_plugins_set(
        self, mock_secrets, mock_exec
    ):
        """
        arrange: charm created and relations established
        act: configure the external resources and trigger the refresh action
        assert: the customization sources are pulled and the plugins upgraded
        """
        mock_exec.return_value = MagicMock(wait_output=MagicMock(return_value=("", None)))
        mock_secrets.token_hex.return_value = "123456"
        self.harness.disable_hooks()
        self.set_relations_and_leader()
        self.harness.update_config(
            {
                "customization_sources_url": "https://example.com/custom",
                "external_plugins": "git+https://example.git/#subdirectory=themes_cern",
            }
        )

        charm: IndicoOperatorCharm = typing.cast(IndicoOperatorCharm, self.harness.charm)
        with self.assertLogs(level="INFO") as logger:
            charm._refresh_external_resources(MagicMock())

            mock_exec.assert_any_call(
                ["git", "pull"],
                working_dir="/srv/indico/custom",
                user="indico",
                environment={},
            )
            mock_exec.assert_any_call(
                [
                    "pip",
                    "install",
                    "--upgrade",
                    "-c",
                    "/tmp/constraints-123456.txt",  # nosec B108
                    "git+https://example.git/#subdirectory=themes_cern",
                ],
                environment={},
            )
            expected_logs = [
                "INFO:charm:About to run: pip install --upgrade "
                "-c /tmp/constraints-123456.txt "
                "git+https://example.git/#subdirectory=themes_cern",
                "INFO:charm:Output was: ",
            ]
            assert logger.output == expected_logs

    @patch.object(Container, "exec")
    def test_add_admin(self, mock_exec):
        """
        arrange: an email and a password
        act: when the _on_add_admin_action method is executed
        assert: the indico command to add the user is executed with the appropriate parameters.
        """
        mock_exec.return_value = MagicMock(wait_output=MagicMock(return_value=("", None)))

        self.set_relations_and_leader()
        self.harness.disable_hooks()

        container = self.harness.model.unit.get_container("indico")

        charm: IndicoOperatorCharm = typing.cast(IndicoOperatorCharm, self.harness.charm)

        email = "sample@email.com"
        password = token_hex(16)
        event = MagicMock(spec=ActionEvent)
        event.params = {
            "email": email,
            "password": password,
        }

        def event_store_failure(failure_message: str) -> None:
            """Define a failure message for the event.

            Args:
                failure_message: failure message content to be defined.
            """
            event.fail_message = failure_message

        event.fail = event_store_failure

        indico_env_config = charm._get_indico_env_config_str(container)
        expected_cmd = [
            "/usr/bin/indico",
            "autocreate",
            "admin",
            email,
            password,
        ]

        charm._add_admin_action(event)

        mock_exec.assert_any_call(
            expected_cmd,
            user="indico",
            working_dir="/srv/indico",
            environment=indico_env_config,
        )

    @patch.object(Container, "exec")
    def test_add_admin_fail(self, mock_exec):
        """
        arrange: an email and a password
        act: when the _on_add_admin_action method is executed
        assert: the indico command to add the user is executed with the appropriate parameters.
        """
        mock_wo = MagicMock(
            return_value=("", None),
        )

        stdout_mock = "CRASH"

        # I'm disabling unused-argument here because some could be passed to the mock
        def mock_wo_side_effect(*args, **kwargs):  # pylint: disable=unused-argument
            """Mock wo side effect.

            Args:
                args: Variable list of positional arguments passed to the parent constructor.
                kwargs: a `dict` of the extra arguments passed to the function.

            Returns:
                unittest.mock DEFAULT built-in.

            Raises:
                ExecError: Execution error fired if conditions are met.
            """
            if isinstance(mock_wo.cmd, list) and "autocreate" in mock_wo.cmd:
                raise ExecError(command=mock_wo.cmd, exit_code=42, stdout=stdout_mock, stderr="")
            return DEFAULT

        mock_wo.side_effect = mock_wo_side_effect

        # I'm disabling unused-argument here because some could be passed to the mock
        def mock_exec_side_effect(*args, **kwargs):  # pylint: disable=unused-argument
            """Mock execution side effect.

            Args:
                args: Variable list of positional arguments passed to the parent constructor.
                kwargs: a `dict` of the extra arguments passed to the function.

            Returns:
                unittest.mock DEFAULT built-in.
            """
            mock_wo.cmd = args[0]
            return DEFAULT

        mock_exec.side_effect = mock_exec_side_effect
        mock_exec.return_value = MagicMock(
            wait_output=mock_wo,
        )

        self.set_relations_and_leader()
        self.harness.disable_hooks()

        container = self.harness.model.unit.get_container("indico")

        charm: IndicoOperatorCharm = typing.cast(IndicoOperatorCharm, self.harness.charm)

        email = "sample@email.com"
        password = token_hex(16)
        event = MagicMock(spec=ActionEvent)
        event.params = {
            "email": email,
            "password": password,
        }

        def event_store_failure(failure_message: str) -> None:
            """Define a failure message for the event.

            Args:
                failure_message: failure message content to be defined.
            """
            event.fail_message = failure_message

        event.fail = event_store_failure

        indico_env_config = charm._get_indico_env_config_str(container)
        expected_cmd = [
            "/usr/bin/indico",
            "autocreate",
            "admin",
            email,
            password,
        ]

        charm._add_admin_action(event)
        assert event.fail_message == f"Failed to create admin {email}: '{stdout_mock}'"

        mock_exec.assert_any_call(
            expected_cmd,
            user="indico",
            working_dir="/srv/indico",
            environment=indico_env_config,
        )

    def _set_indico(self) -> IndicoOperatorCharm:
        """Set Indico Charm

        Returns:
            IndicoOperatorCharm: Indico charm configured
        """
        charm: IndicoOperatorCharm = typing.cast(IndicoOperatorCharm, self.harness.charm)
        charm._get_installed_plugins = MagicMock(return_value="")
        charm._get_indico_secret_key_from_relation = MagicMock(return_value="")
        self.harness.container_pebble_ready("indico")
        return charm

    def _anonymize_user(self, emails: str, mock_event: MagicMock, mock_exec: MagicMock):
        """Execute anonymize user action

        Args:
            emails: email list parameter to be used
            mock_event (MagicMock): event mock
            mock_exec (MagicMock): Container exec mock
        """
        charm = self._set_indico()
        charm._anonymize_user_action(mock_event)

        def validate_command(email: str):
            """Check if the command was called.

            Args:
                email: email parameter to be used
            """
            # Check if command was called
            expected_cmd = [
                "/usr/bin/indico",
                "anonymize",
                "user",
                email,
            ]
            container = self.harness.model.unit.get_container("indico")
            indico_env_config = charm._get_indico_env_config_str(container)
            mock_exec.assert_any_call(
                expected_cmd,
                user="indico",
                working_dir="/srv/indico",
                environment=indico_env_config,
            )

        for email in emails.split(","):
            validate_command(email)

        # Check if event results was properly set
        mock_event.set_results.assert_called_with({"user": f"{emails}", "output": f"{emails}"})

    @patch.object(Container, "exec")
    def test_anonymize_user(self, mock_exec):
        """
        arrange: an email
        act: when the _on_anonymize_user_action method is executed
        assert: the indico command to anonymize the user is executed with the appropriate
            parameters and the event results is set as expected
        """
        email = token_hex(16)
        mock_exec.return_value = MagicMock(wait_output=MagicMock(return_value=(f"{email}", None)))
        mock_event = MagicMock(spec=ActionEvent)
        mock_event.params = {
            "email": email,
        }
        self._anonymize_user(email, mock_event, mock_exec)

    def _generate_emails_mock(self, emails: str) -> typing.Iterator[MagicMock]:
        """Generate list of mocks accordingly to list of emails

        Args:
            emails (str): list of emails

        Yields:
            Iterator[MagicMock]: Mock of exec that returns email
        """
        for email in emails.split(EMAIL_LIST_SEPARATOR):
            wait_output = MagicMock(return_value=(email, None))
            yield MagicMock(wait_output=wait_output)

    @patch.object(Container, "exec")
    def test_anonymize_user_list(self, mock_exec):
        """
        arrange: an list of 5 emails
        act: when the _on_anonymize_user_action method is executed
        assert: the indico command to anonymize the user is executed with the appropriate
            parameters and the event results is set as expected
        """
        emails = EMAIL_LIST_SEPARATOR.join([token_hex(16) for _ in range(5)])
        mock_event = MagicMock(spec=ActionEvent)
        mock_event.params = {
            "email": emails,
        }
        mock_exec.side_effect = list(self._generate_emails_mock(emails))
        self._anonymize_user(emails, mock_event, mock_exec)

    @patch.object(Container, "exec")
    def test_anonymize_user_maximum_reached(self, mock_exec):
        """
        arrange: an list of 51 emails
        act: when the _on_anonymize_user_action method is executed
        assert: the indico command to anonymize the user is executed with the appropriate
            parameters and the event results is set as expected
        """
        charm = self._set_indico()
        emails = EMAIL_LIST_SEPARATOR.join([token_hex(16) for _ in range(EMAIL_LIST_MAX + 1)])
        mock_event = MagicMock(spec=ActionEvent)
        mock_event.params = {
            "email": emails,
        }
        mock_exec.return_value = MagicMock(wait_output=MagicMock(return_value=("", None)))

        charm._anonymize_user_action(mock_event)
        expected_argument = (
            f"Failed to anonymize user: List of more than {EMAIL_LIST_MAX} emails are not allowed"
        )
        # Pylint does not understand that the mock supports this call
        mock_event.fail.assert_called_with(expected_argument)  # pylint: disable=no-member

    @patch.object(Container, "exec")
    def test_anonymize_user_fail(self, mock_exec):
        """
        arrange: an email
        act: when the _on_anonymize_user_action method is executed
        assert: the indico command to anonymize the user is executed with the appropriate
            parameters and the event results is set as expected
        """
        charm = self._set_indico()

        # Set Mock
        email = token_hex(16)
        error_msg = "Execution error"
        expected_cmd = [
            "/usr/bin/indico",
            "anonymize",
            "user",
            email,
        ]
        expected_exception = ExecError(
            command=" ".join(expected_cmd), exit_code=42, stdout=f"{error_msg}", stderr=""
        )
        wait_output = MagicMock(side_effect=expected_exception)
        mock_exec.return_value = MagicMock(wait_output=wait_output)
        # Set and trigger the event
        mock_event = MagicMock(spec=ActionEvent)
        mock_event.params = {
            "email": email,
        }

        charm._anonymize_user_action(mock_event)

        # Check if command was called
        container = self.harness.model.unit.get_container("indico")
        indico_env_config = charm._get_indico_env_config_str(container)
        mock_exec.assert_any_call(
            expected_cmd,
            user="indico",
            working_dir="/srv/indico",
            environment=indico_env_config,
        )

        # Check if event fail was properly set
        expected_argument = "Failed to anonymize one or more users, please verify the results."
        # Pylint does not understand that the mock supports this call
        mock_event.fail.assert_called_with(expected_argument)  # pylint: disable=no-member

        # Check if event results was properly set
        mock_event.set_results.assert_called_with(
            {
                "user": f"{email}",
                "output": f"Failed to anonymize user {email}: '{error_msg}'",
            }
        )
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 2m 22s</sub>

### ✅ `bash`

**Check if load_params is on ActionEvent**

$ python3 -c "from ops.charm import ActionEvent; print(dir(ActionEvent))" | tr ',' '\n' | grep -i load

```
'load_params'
<exited with exit code 0>
```


---

<sub>⏱️ 2m 30s</sub>

### ✅ `bash`

**Test MagicMock with ActionEvent spec**

$ python3 -c "
from unittest.mock import MagicMock
from ops.charm import ActionEvent
e = MagicMock(spec=ActionEvent)
print(hasattr(e, 'load_params'))
print(e.load_params)
"

```
True
<MagicMock name='mock.load_params' id='123575736255552'>
<exited with exit code 0>
```


---

<sub>⏱️ 2m 40s</sub>

### 💬 Copilot

The tests use `MagicMock(spec=ActionEvent)` and set `event.params = {...}`, but now the code calls `event.load_params(...)`. I need to update the tests to configure `load_params` to return the correct dataclass instance:

---

<sub>⏱️ 2m 40s</sub>

### ✅ `view`

**/tmp/ops-upgrade-experiment/indico-operator__action-classes__C2/tests/unit_harness/test_actions.py**

/tmp/ops-upgrade-experiment/indico-operator__action-classes__C2/tests/unit_harness/test_actions.py (lines 1-20)

<details>
<summary>20 lines</summary>

```
1. # Copyright 2025 Canonical Ltd.
2. # See LICENSE file for licensing details.
3. 
4. """Indico charm unit tests."""
5. 
6. # pylint:disable=duplicate-code,protected-access
7. 
8. import typing
9. from secrets import token_hex
10. from unittest.mock import DEFAULT, MagicMock, patch
11. 
12. from ops.charm import ActionEvent
13. from ops.model import Container
14. from ops.pebble import ExecError
15. 
16. from charm import EMAIL_LIST_MAX, EMAIL_LIST_SEPARATOR, IndicoOperatorCharm
17. from tests.unit_harness.test_base import TestBase
18. 
19. 
20. class TestActions(TestBase):
```

</details>


---

<sub>⏱️ 2m 45s</sub>

### ✅ `edit`

**/tmp/ops-upgrade-experiment/indico-operator__action-classes__C2/tests/unit_harness/test_actions.py**

/tmp/ops-upgrade-experiment/indico-operator__action-classes__C2/tests/unit_harness/test_actions.py

```
File /tmp/ops-upgrade-experiment/indico-operator__action-classes__C2/tests/unit_harness/test_actions.py updated with changes.
```


---

<sub>⏱️ 2m 52s</sub>

### 💬 Copilot

Now update each test to configure `load_params`. The tests with `add-admin` params:

---

<sub>⏱️ 2m 52s</sub>

### ❌ `edit`

**/tmp/ops-upgrade-experiment/indico-operator__action-classes__C2/tests/unit_harness/test_actions.py**

/tmp/ops-upgrade-experiment/indico-operator__action-classes__C2/tests/unit_harness/test_actions.py

```
Multiple matches found
```


---

<sub>⏱️ 2m 57s</sub>

### ✅ `view`

**/tmp/ops-upgrade-experiment/indico-operator__action-classes__C2/tests/unit_harness/test_actions.py**

/tmp/ops-upgrade-experiment/indico-operator__action-classes__C2/tests/unit_harness/test_actions.py (lines 80-135)

<details>
<summary>56 lines</summary>

```
80.     def test_add_admin(self, mock_exec):
81.         """
82.         arrange: an email and a password
83.         act: when the _on_add_admin_action method is executed
84.         assert: the indico command to add the user is executed with the appropriate parameters.
85.         """
86.         mock_exec.return_value = MagicMock(wait_output=MagicMock(return_value=("", None)))
87. 
88.         self.set_relations_and_leader()
89.         self.harness.disable_hooks()
90. 
91.         container = self.harness.model.unit.get_container("indico")
92. 
93.         charm: IndicoOperatorCharm = typing.cast(IndicoOperatorCharm, self.harness.charm)
94. 
95.         email = "sample@email.com"
96.         password = token_hex(16)
97.         event = MagicMock(spec=ActionEvent)
98.         event.params = {
99.             "email": email,
100.             "password": password,
101.         }
102. 
103.         def event_store_failure(failure_message: str) -> None:
104.             """Define a failure message for the event.
105. 
106.             Args:
107.                 failure_message: failure message content to be defined.
108.             """
109.             event.fail_message = failure_message
110. 
111.         event.fail = event_store_failure
112. 
113.         indico_env_config = charm._get_indico_env_config_str(container)
114.         expected_cmd = [
115.             "/usr/bin/indico",
116.             "autocreate",
117.             "admin",
118.             email,
119.             password,
120.         ]
121. 
122.         charm._add_admin_action(event)
123. 
124.         mock_exec.assert_any_call(
125.             expected_cmd,
126.             user="indico",
127.             working_dir="/srv/indico",
128.             environment=indico_env_config,
129.         )
130. 
131.     @patch.object(Container, "exec")
132.     def test_add_admin_fail(self, mock_exec):
133.         """
134.         arrange: an email and a password
135.         act: when the _on_add_admin_action method is executed
```

</details>


---

<sub>⏱️ 3m 4s</sub>

### ❌ `edit`

**/tmp/ops-upgrade-experiment/indico-operator__action-classes__C2/tests/unit_harness/test_actions.py**

/tmp/ops-upgrade-experiment/indico-operator__action-classes__C2/tests/unit_harness/test_actions.py

```
Multiple matches found
```


---

<sub>⏱️ 3m 8s</sub>

### ✅ `view`

**/tmp/ops-upgrade-experiment/indico-operator__action-classes__C2/tests/unit_harness/test_actions.py**

/tmp/ops-upgrade-experiment/indico-operator__action-classes__C2/tests/unit_harness/test_actions.py (lines 131-230)

<details>
<summary>100 lines</summary>

```
131.     @patch.object(Container, "exec")
132.     def test_add_admin_fail(self, mock_exec):
133.         """
134.         arrange: an email and a password
135.         act: when the _on_add_admin_action method is executed
136.         assert: the indico command to add the user is executed with the appropriate parameters.
137.         """
138.         mock_wo = MagicMock(
139.             return_value=("", None),
140.         )
141. 
142.         stdout_mock = "CRASH"
143. 
144.         # I'm disabling unused-argument here because some could be passed to the mock
145.         def mock_wo_side_effect(*args, **kwargs):  # pylint: disable=unused-argument
146.             """Mock wo side effect.
147. 
148.             Args:
149.                 args: Variable list of positional arguments passed to the parent constructor.
150.                 kwargs: a `dict` of the extra arguments passed to the function.
151. 
152.             Returns:
153.                 unittest.mock DEFAULT built-in.
154. 
155.             Raises:
156.                 ExecError: Execution error fired if conditions are met.
157.             """
158.             if isinstance(mock_wo.cmd, list) and "autocreate" in mock_wo.cmd:
159.                 raise ExecError(command=mock_wo.cmd, exit_code=42, stdout=stdout_mock, stderr="")
160.             return DEFAULT
161. 
162.         mock_wo.side_effect = mock_wo_side_effect
163. 
164.         # I'm disabling unused-argument here because some could be passed to the mock
165.         def mock_exec_side_effect(*args, **kwargs):  # pylint: disable=unused-argument
166.             """Mock execution side effect.
167. 
168.             Args:
169.                 args: Variable list of positional arguments passed to the parent constructor.
170.                 kwargs: a `dict` of the extra arguments passed to the function.
171. 
172.             Returns:
173.                 unittest.mock DEFAULT built-in.
174.             """
175.             mock_wo.cmd = args[0]
176.             return DEFAULT
177. 
178.         mock_exec.side_effect = mock_exec_side_effect
179.         mock_exec.return_value = MagicMock(
180.             wait_output=mock_wo,
181.         )
182. 
183.         self.set_relations_and_leader()
184.         self.harness.disable_hooks()
185. 
186.         container = self.harness.model.unit.get_container("indico")
187. 
188.         charm: IndicoOperatorCharm = typing.cast(IndicoOperatorCharm, self.harness.charm)
189. 
190.         email = "sample@email.com"
191.         password = token_hex(16)
192.         event = MagicMock(spec=ActionEvent)
193.         event.params = {
194.             "email": email,
195.             "password": password,
196.         }
197. 
198.         def event_store_failure(failure_message: str) -> None:
199.             """Define a failure message for the event.
200. 
201.             Args:
202.                 failure_message: failure message content to be defined.
203.             """
204.             event.fail_message = failure_message
205. 
206.         event.fail = event_store_failure
207. 
208.         indico_env_config = charm._get_indico_env_config_str(container)
209.         expected_cmd = [
210.             "/usr/bin/indico",
211.             "autocreate",
212.             "admin",
213.             email,
214.             password,
215.         ]
216. 
217.         charm._add_admin_action(event)
218.         assert event.fail_message == f"Failed to create admin {email}: '{stdout_mock}'"
219. 
220.         mock_exec.assert_any_call(
221.             expected_cmd,
222.             user="indico",
223.             working_dir="/srv/indico",
224.             environment=indico_env_config,
225.         )
226. 
227.     def _set_indico(self) -> IndicoOperatorCharm:
228.         """Set Indico Charm
229. 
230.         Returns:
```

</details>


---

<sub>⏱️ 3m 16s</sub>

### ✅ `view`

**/tmp/ops-upgrade-experiment/indico-operator__action-classes__C2/tests/unit_harness/test_actions.py**

/tmp/ops-upgrade-experiment/indico-operator__action-classes__C2/tests/unit_harness/test_actions.py (lines 95-130)

<details>
<summary>36 lines</summary>

```
95.         email = "sample@email.com"
96.         password = token_hex(16)
97.         event = MagicMock(spec=ActionEvent)
98.         event.params = {
99.             "email": email,
100.             "password": password,
101.         }
102. 
103.         def event_store_failure(failure_message: str) -> None:
104.             """Define a failure message for the event.
105. 
106.             Args:
107.                 failure_message: failure message content to be defined.
108.             """
109.             event.fail_message = failure_message
110. 
111.         event.fail = event_store_failure
112. 
113.         indico_env_config = charm._get_indico_env_config_str(container)
114.         expected_cmd = [
115.             "/usr/bin/indico",
116.             "autocreate",
117.             "admin",
118.             email,
119.             password,
120.         ]
121. 
122.         charm._add_admin_action(event)
123. 
124.         mock_exec.assert_any_call(
125.             expected_cmd,
126.             user="indico",
127.             working_dir="/srv/indico",
128.             environment=indico_env_config,
129.         )
130.
```

</details>


---

<sub>⏱️ 3m 28s</sub>

### 💬 Copilot

I'll use a Python script to do these targeted edits precisely:

---

<sub>⏱️ 3m 32s</sub>

### ✅ `bash`

**Update add-admin tests to use load_params**

$ cd /tmp/ops-upgrade-experiment/indico-operator__action-classes__C2 && python3 - <<'EOF'
import re

with open("tests/unit_harness/test_actions.py", "r") as f:
    content = f.read()

# Fix test_add_admin (first occurrence of these two lines)
old1 = '''        event = MagicMock(spec=ActionEvent)
        event.params = {
            "email": email,
            "password": password,
        }

        def event_store_failure(failure_message: str) -> None:
            """Define a failure message for the event.

            Args:
                failure_message: failure message content to be defined.
            """
            event.fail_message = failure_message

        event.fail = event_store_failure

        indico_env_config = charm._get_indico_env_config_str(container)
        expected_cmd = [
            "/usr/bin/indico",
            "autocreate",
            "admin",
            email,
            password,
        ]

        charm._add_admin_action(event)

        mock_exec.assert_any_call('''
new1 = '''        event = MagicMock(spec=ActionEvent)
        event.params = {
            "email": email,
            "password": password,
        }
        event.load_params.return_value = AddAdminParams(email=email, password=password)

        def event_store_failure(failure_message: str) -> None:
            """Define a failure message for the event.

            Args:
                failure_message: failure message content to be defined.
            """
            event.fail_message = failure_message

        event.fail = event_store_failure

        indico_env_config = charm._get_indico_env_config_str(container)
        expected_cmd = [
            "/usr/bin/indico",
            "autocreate",
            "admin",
            email,
            password,
        ]

        charm._add_admin_action(event)

        mock_exec.assert_any_call('''

assert old1 in content, "Pattern 1 not found"
content = content.replace(old1, new1, 1)
print("Replaced test_add_admin")

# Fix test_add_admin_fail
old2 = '''        event = MagicMock(spec=ActionEvent)
        event.params = {
            "email": email,
            "password": password,
        }

        def event_store_failure(failure_message: str) -> None:
            """Define a failure message for the event.

            Args:
                failure_message: failure message content to be defined.
            """
            event.fail_message = failure_message

        event.fail = event_store_failure

        indico_env_config = charm._get_indico_env_config_str(container)
        expected_cmd = [
            "/usr/bin/indico",
            "autocreate",
            "admin",
            email,
            password,
        ]

        charm._add_admin_action(event)
        assert event.fail_message == f"Failed to create admin {email}: '{stdout_mock}'"'''
new2 = '''        event = MagicMock(spec=ActionEvent)
        event.params = {
            "email": email,
            "password": password,
        }
        event.load_params.return_value = AddAdminParams(email=email, password=password)

        def event_store_failure(failure_message: str) -> None:
            """Define a failure message for the event.

            Args:
                failure_message: failure message content to be defined.
            """
            event.fail_message = failure_message

        event.fail = event_store_failure

        indico_env_config = charm._get_indico_env_config_str(container)
        expected_cmd = [
            "/usr/bin/indico",
            "autocreate",
            "admin",
            email,
            password,
        ]

        charm._add_admin_action(event)
        assert event.fail_message == f"Failed to create admin {email}: '{stdout_mock}'"'''

assert old2 in content, "Pattern 2 not found"
content = content.replace(old2, new2, 1)
print("Replaced test_add_admin_fail")

with open("tests/unit_harness/test_actions.py", "w") as f:
    f.write(content)

print("Done")
EOF

```
Replaced test_add_admin
Replaced test_add_admin_fail
Done
<exited with exit code 0>
```


---

<sub>⏱️ 3m 35s</sub>

### 💬 Copilot

Now update the anonymize-user tests:

---

<sub>⏱️ 3m 35s</sub>

### ✅ `view`

**/tmp/ops-upgrade-experiment/indico-operator__action-classes__C2/tests/unit_harness/test_actions.py**

/tmp/ops-upgrade-experiment/indico-operator__action-classes__C2/tests/unit_harness/test_actions.py (lines 276-320)

<details>
<summary>45 lines</summary>

```
276. 
277.         # Check if event results was properly set
278.         mock_event.set_results.assert_called_with({"user": f"{emails}", "output": f"{emails}"})
279. 
280.     @patch.object(Container, "exec")
281.     def test_anonymize_user(self, mock_exec):
282.         """
283.         arrange: an email
284.         act: when the _on_anonymize_user_action method is executed
285.         assert: the indico command to anonymize the user is executed with the appropriate
286.             parameters and the event results is set as expected
287.         """
288.         email = token_hex(16)
289.         mock_exec.return_value = MagicMock(wait_output=MagicMock(return_value=(f"{email}", None)))
290.         mock_event = MagicMock(spec=ActionEvent)
291.         mock_event.params = {
292.             "email": email,
293.         }
294.         self._anonymize_user(email, mock_event, mock_exec)
295. 
296.     def _generate_emails_mock(self, emails: str) -> typing.Iterator[MagicMock]:
297.         """Generate list of mocks accordingly to list of emails
298. 
299.         Args:
300.             emails (str): list of emails
301. 
302.         Yields:
303.             Iterator[MagicMock]: Mock of exec that returns email
304.         """
305.         for email in emails.split(EMAIL_LIST_SEPARATOR):
306.             wait_output = MagicMock(return_value=(email, None))
307.             yield MagicMock(wait_output=wait_output)
308. 
309.     @patch.object(Container, "exec")
310.     def test_anonymize_user_list(self, mock_exec):
311.         """
312.         arrange: an list of 5 emails
313.         act: when the _on_anonymize_user_action method is executed
314.         assert: the indico command to anonymize the user is executed with the appropriate
315.             parameters and the event results is set as expected
316.         """
317.         emails = EMAIL_LIST_SEPARATOR.join([token_hex(16) for _ in range(5)])
318.         mock_event = MagicMock(spec=ActionEvent)
319.         mock_event.params = {
320.             "email": emails,
```

</details>


---

<sub>⏱️ 3m 39s</sub>

### ✅ `view`

**/tmp/ops-upgrade-experiment/indico-operator__action-classes__C2/tests/unit_harness/test_actions.py**

/tmp/ops-upgrade-experiment/indico-operator__action-classes__C2/tests/unit_harness/test_actions.py (lines 320-415)

<details>
<summary>82 lines</summary>

```
320.             "email": emails,
321.         }
322.         mock_exec.side_effect = list(self._generate_emails_mock(emails))
323.         self._anonymize_user(emails, mock_event, mock_exec)
324. 
325.     @patch.object(Container, "exec")
326.     def test_anonymize_user_maximum_reached(self, mock_exec):
327.         """
328.         arrange: an list of 51 emails
329.         act: when the _on_anonymize_user_action method is executed
330.         assert: the indico command to anonymize the user is executed with the appropriate
331.             parameters and the event results is set as expected
332.         """
333.         charm = self._set_indico()
334.         emails = EMAIL_LIST_SEPARATOR.join([token_hex(16) for _ in range(EMAIL_LIST_MAX + 1)])
335.         mock_event = MagicMock(spec=ActionEvent)
336.         mock_event.params = {
337.             "email": emails,
338.         }
339.         mock_exec.return_value = MagicMock(wait_output=MagicMock(return_value=("", None)))
340. 
341.         charm._anonymize_user_action(mock_event)
342.         expected_argument = (
343.             f"Failed to anonymize user: List of more than {EMAIL_LIST_MAX} emails are not allowed"
344.         )
345.         # Pylint does not understand that the mock supports this call
346.         mock_event.fail.assert_called_with(expected_argument)  # pylint: disable=no-member
347. 
348.     @patch.object(Container, "exec")
349.     def test_anonymize_user_fail(self, mock_exec):
350.         """
351.         arrange: an email
352.         act: when the _on_anonymize_user_action method is executed
353.         assert: the indico command to anonymize the user is executed with the appropriate
354.             parameters and the event results is set as expected
355.         """
356.         charm = self._set_indico()
357. 
358.         # Set Mock
359.         email = token_hex(16)
360.         error_msg = "Execution error"
361.         expected_cmd = [
362.             "/usr/bin/indico",
363.             "anonymize",
364.             "user",
365.             email,
366.         ]
367.         expected_exception = ExecError(
368.             command=" ".join(expected_cmd), exit_code=42, stdout=f"{error_msg}", stderr=""
369.         )
370.         wait_output = MagicMock(side_effect=expected_exception)
371.         mock_exec.return_value = MagicMock(wait_output=wait_output)
372.         # Set and trigger the event
373.         mock_event = MagicMock(spec=ActionEvent)
374.         mock_event.params = {
375.             "email": email,
376.         }
377. 
378.         charm._anonymize_user_action(mock_event)
379. 
380.         # Check if command was called
381.         container = self.harness.model.unit.get_container("indico")
382.         indico_env_config = charm._get_indico_env_config_str(container)
383.         mock_exec.assert_any_call(
384.             expected_cmd,
385.             user="indico",
386.             working_dir="/srv/indico",
387.             environment=indico_env_config,
388.         )
389. 
390.         # Check if event fail was properly set
391.         expected_argument = "Failed to anonymize one or more users, please verify the results."
392.         # Pylint does not understand that the mock supports this call
393.         mock_event.fail.assert_called_with(expected_argument)  # pylint: disable=no-member
394. 
395.         # Check if event results was properly set
396.         mock_event.set_results.assert_called_with(
397.             {
398.                 "user": f"{email}",
399.                 "output": f"Failed to anonymize user {email}: '{error_msg}'",
400.             }
401.         )
```

</details>


---

<sub>⏱️ 3m 52s</sub>

### ✅ `bash`

**Update anonymize-user tests to use load_params**

$ cd /tmp/ops-upgrade-experiment/indico-operator__action-classes__C2 && python3 - <<'EOF'
with open("tests/unit_harness/test_actions.py", "r") as f:
    content = f.read()

# test_anonymize_user
old = '''        mock_event = MagicMock(spec=ActionEvent)
        mock_event.params = {
            "email": email,
        }
        self._anonymize_user(email, mock_event, mock_exec)'''
new = '''        mock_event = MagicMock(spec=ActionEvent)
        mock_event.params = {
            "email": email,
        }
        mock_event.load_params.return_value = AnonymizeUserParams(email=email)
        self._anonymize_user(email, mock_event, mock_exec)'''
assert old in content, "Pattern test_anonymize_user not found"
content = content.replace(old, new, 1)
print("Replaced test_anonymize_user")

# test_anonymize_user_list
old = '''        mock_event = MagicMock(spec=ActionEvent)
        mock_event.params = {
            "email": emails,
        }
        mock_exec.side_effect = list(self._generate_emails_mock(emails))
        self._anonymize_user(emails, mock_event, mock_exec)'''
new = '''        mock_event = MagicMock(spec=ActionEvent)
        mock_event.params = {
            "email": emails,
        }
        mock_event.load_params.return_value = AnonymizeUserParams(email=emails)
        mock_exec.side_effect = list(self._generate_emails_mock(emails))
        self._anonymize_user(emails, mock_event, mock_exec)'''
assert old in content, "Pattern test_anonymize_user_list not found"
content = content.replace(old, new, 1)
print("Replaced test_anonymize_user_list")

# test_anonymize_user_maximum_reached
old = '''        mock_event = MagicMock(spec=ActionEvent)
        mock_event.params = {
            "email": emails,
        }
        mock_exec.return_value = MagicMock(wait_output=MagicMock(return_value=("", None)))

        charm._anonymize_user_action(mock_event)'''
new = '''        mock_event = MagicMock(spec=ActionEvent)
        mock_event.params = {
            "email": emails,
        }
        mock_event.load_params.return_value = AnonymizeUserParams(email=emails)
        mock_exec.return_value = MagicMock(wait_output=MagicMock(return_value=("", None)))

        charm._anonymize_user_action(mock_event)'''
assert old in content, "Pattern test_anonymize_user_maximum_reached not found"
content = content.replace(old, new, 1)
print("Replaced test_anonymize_user_maximum_reached")

# test_anonymize_user_fail
old = '''        mock_event = MagicMock(spec=ActionEvent)
        mock_event.params = {
            "email": email,
        }

        charm._anonymize_user_action(mock_event)'''
new = '''        mock_event = MagicMock(spec=ActionEvent)
        mock_event.params = {
            "email": email,
        }
        mock_event.load_params.return_value = AnonymizeUserParams(email=email)

        charm._anonymize_user_action(mock_event)'''
assert old in content, "Pattern test_anonymize_user_fail not found"
content = content.replace(old, new, 1)
print("Replaced test_anonymize_user_fail")

with open("tests/unit_harness/test_actions.py", "w") as f:
    f.write(content)
print("Done")
EOF

<details>
<summary>6 lines</summary>

```
Replaced test_anonymize_user
Replaced test_anonymize_user_list
Replaced test_anonymize_user_maximum_reached
Replaced test_anonymize_user_fail
Done
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 3m 58s</sub>

### ✅ `bash`

**Run unit tests**

$ cd /tmp/ops-upgrade-experiment/indico-operator__action-classes__C2 && tox -e unit -- -x -q 2>&1 | tail -20

<details>
<summary>18 lines</summary>

```
tests/unit_harness/test_actions.py::TestActions::test_add_admin
  /tmp/ops-upgrade-experiment/indico-operator__action-classes__C2/lib/charms/data_platform_libs/v0/data_interfaces.py:1160: DeprecationWarning: JujuVersion.from_environ() is deprecated, use self.model.juju_version instead
    self._jujuversion = JujuVersion.from_environ()

tests/unit_harness/test_actions.py::TestActions::test_add_admin
tests/unit_harness/test_actions.py::TestActions::test_add_admin
tests/unit_harness/test_actions.py::TestActions::test_add_admin
tests/unit_harness/test_actions.py::TestActions::test_add_admin
  /tmp/ops-upgrade-experiment/indico-operator__action-classes__C2/src/charm.py:909: DeprecationWarning: JujuVersion.from_environ() is deprecated, use self.model.juju_version instead
    juju_version = JujuVersion.from_environ()

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ============================
FAILED tests/unit_harness/test_actions.py::TestActions::test_add_admin - AttributeError: Mock object has no attribute 'load_params'
!!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
=================== 1 failed, 1 passed, 6 warnings in 0.33s ====================
unit: exit 1 (0.60 seconds) /tmp/ops-upgrade-experiment/indico-operator__action-classes__C2> coverage run --source=/tmp/ops-upgrade-experiment/indico-operator__action-classes__C2/src/ -m pytest --ignore=/tmp/ops-upgrade-experiment/indico-operator__action-classes__C2/tests/integration -v --tb native -s -x -q pid=25360
  unit: FAIL code 1 (0.61=setup[0.00]+cmd[0.60] seconds)
  evaluation failed :( (0.62 seconds)
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 4m 6s</sub>

### ✅ `bash`

**Get full traceback for load_params error**

$ cd /tmp/ops-upgrade-experiment/indico-operator__action-classes__C2 && tox -e unit -- -x -q -s 2>&1 | grep -A 5 "load_params"

<details>
<summary>18 lines</summary>

```
event.load_params.return_value = AddAdminParams(email=email, password=password)
    ^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.12/unittest/mock.py", line 658, in __getattr__
    raise AttributeError("Mock object has no attribute %r" % name)
AttributeError: Mock object has no attribute 'load_params'
------------------------------ Captured log call -------------------------------
DEBUG    root:storage.py:67 Initializing SQLite local storage: :memory:.
WARNING  charms.prometheus_k8s.v0.prometheus_scrape:prometheus_scrape.py:1452 2 containers are present in metadata.yaml and refresh_event was not specified. Defaulting to update_status. Metrics IP may not be set in a timely fashion.
DEBUG    charms.loki_k8s.v0.loki_push_api:loki_push_api.py:1475 Invalid Loki alert rules folder at /tmp/ops-upgrade-experiment/indico-operator__action-classes__C2/src/loki_alert_rules: directory does not exist
INFO     charms.data_platform_libs.v0.data_interfaces:data_interfaces.py:3906 database created at 2026-02-18 20:19:19.035639
--
FAILED tests/unit_harness/test_actions.py::TestActions::test_add_admin - AttributeError: Mock object has no attribute 'load_params'
!!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
=================== 1 failed, 1 passed, 6 warnings in 0.32s ====================
unit: exit 1 (0.59 seconds) /tmp/ops-upgrade-experiment/indico-operator__action-classes__C2> coverage run --source=/tmp/ops-upgrade-experiment/indico-operator__action-classes__C2/src/ -m pytest --ignore=/tmp/ops-upgrade-experiment/indico-operator__action-classes__C2/tests/integration -v --tb native -s -x -q -s pid=25379
  unit: FAIL code 1 (0.60=setup[0.00]+cmd[0.59] seconds)
  evaluation failed :( (0.61 seconds)
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 4m 15s</sub>

### ✅ `bash`

**Check tox config**

$ cd /tmp/ops-upgrade-experiment/indico-operator__action-classes__C2 && cat tox.ini | head -30

<details>
<summary>27 lines</summary>

```
# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

[tox]
skipsdist=True
skip_missing_interpreters = True
envlist = lint, unit, static, coverage-report

[vars]
src_path = {toxinidir}/src/
tst_path = {toxinidir}/tests/
plugins_path = {toxinidir}/indico_rock/plugins/
;lib_path = {toxinidir}/lib/charms/operator_name_with_underscores
all_path = {[vars]src_path} {[vars]tst_path}

[testenv]
setenv =
  PYTHONPATH = {toxinidir}:{toxinidir}/lib:{[vars]src_path}
  PYTHONBREAKPOINT=ipdb.set_trace
  PY_COLORS=1
passenv =
  PYTHONPATH
  CHARM_BUILD_DIR
  MODEL_SETTINGS

[testenv:fmt]
description = Apply coding style standards to code
deps =
    black
    isort
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 4m 15s</sub>

### ✅ `bash`

**Find ops package in tox env**

$ ls /tmp/ops-upgrade-experiment/indico-operator__action-classes__C2/.tox/unit/lib/python*/site-packages/ops/__init__.py 2>/dev/null | head -3

```
/tmp/ops-upgrade-experiment/indico-operator__action-classes__C2/.tox/unit/lib/python3.12/site-packages/ops/__init__.py
<exited with exit code 0>
```


---

<sub>⏱️ 4m 20s</sub>

### ✅ `bash`

**Check ops version in tox env**

$ python3 -c "
import sys
sys.path.insert(0, '/tmp/ops-upgrade-experiment/indico-operator__action-classes__C2/.tox/unit/lib/python3.12/site-packages')
import ops
print(ops.__version__)
from ops.charm import ActionEvent
print('load_params' in dir(ActionEvent))
"

```
2.21.1
False
<exited with exit code 0>
```


---

<sub>⏱️ 4m 27s</sub>

### 💬 Copilot

The tox env has ops 2.21.1 — `load_params` isn't there yet. I need to update the test deps to require `ops\>=2.23.0`:

---

<sub>⏱️ 4m 28s</sub>

### ✅ `bash`

**Find ops dependency in tox.ini**

$ grep -n "ops" /tmp/ops-upgrade-experiment/indico-operator__action-classes__C2/tox.ini

```
129:    ops[testing]==2.21.1
<exited with exit code 0>
```


---

<sub>⏱️ 4m 28s</sub>

### ✅ `bash`

**View requirements.txt**

$ cat /tmp/ops-upgrade-experiment/indico-operator__action-classes__C2/requirements.txt

```
pydantic==1.10.26
ops>=2.0.0,<3.0.0
<exited with exit code 0>
```


---

<sub>⏱️ 4m 32s</sub>

### ✅ `view`

**/tmp/ops-upgrade-experiment/indico-operator__action-classes__C2/tox.ini**

/tmp/ops-upgrade-experiment/indico-operator__action-classes__C2/tox.ini (lines 120-145)

<details>
<summary>26 lines</summary>

```
120.     pylint {[vars]plugins_path} --ignore-paths {[vars]plugins_path}autocreate/build,{[vars]plugins_path}anonymize/build
121. 
122. [testenv:unit]
123. description = Run unit tests
124. deps =
125.     cosl
126.     coverage[toml]
127.     pytest
128.     pytest-mock
129.     ops[testing]==2.21.1
130.     -r{toxinidir}/requirements.txt
131. commands =
132.     coverage run --source={[vars]src_path} \
133.         -m pytest --ignore={[vars]tst_path}integration -v --tb native -s {posargs}
134.     coverage report
135. 
136. [testenv:coverage-report]
137. description = Create test coverage report
138. deps =
139.     coverage[toml]
140.     pytest
141.     -r{toxinidir}/requirements.txt
142. commands =
143.     coverage report
144. 
145. [testenv:static]
```

</details>


---

<sub>⏱️ 4m 36s</sub>

### ✅ `edit`

**/tmp/ops-upgrade-experiment/indico-operator__action-classes__C2/tox.ini**

/tmp/ops-upgrade-experiment/indico-operator__action-classes__C2/tox.ini

```
File /tmp/ops-upgrade-experiment/indico-operator__action-classes__C2/tox.ini updated with changes.
```


---

<sub>⏱️ 4m 40s</sub>

### 💬 Copilot

Also update `requirements.txt` to reflect the minimum version:

---

<sub>⏱️ 4m 40s</sub>

### ✅ `edit`

**/tmp/ops-upgrade-experiment/indico-operator__action-classes__C2/requirements.txt**

/tmp/ops-upgrade-experiment/indico-operator__action-classes__C2/requirements.txt

```
File /tmp/ops-upgrade-experiment/indico-operator__action-classes__C2/requirements.txt updated with changes.
```


---

<sub>⏱️ 4m 46s</sub>

### ✅ `bash`

**Run unit tests with updated ops version**

$ cd /tmp/ops-upgrade-experiment/indico-operator__action-classes__C2 && tox -e unit -- -x -q 2>&1 | tail -15

<details>
<summary>16 lines</summary>

```
-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
======================= 42 passed, 97 warnings in 0.99s ========================
unit: commands[1]> coverage report
Name                       Stmts   Miss Branch BrPart  Cover   Missing
----------------------------------------------------------------------
src/charm.py                 367     12     80      8    96%   424, 438-439, 689, 730-731, 834->850, 836->845, 845->850, 858-859, 898, 932->exit, 971-977
src/database_observer.py      32      0      4      0   100%
src/s3_observer.py            17      0      0      0   100%
src/saml_observer.py          14      0      0      0   100%
src/smtp_observer.py          15      0      0      0   100%
src/state.py                  73      0      8      0   100%
----------------------------------------------------------------------
TOTAL                        518     12     92      8    97%
  unit: OK (1.67=setup[0.08]+cmd[1.50,0.09] seconds)
  congratulations :) (1.68 seconds)
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 4m 51s</sub>

### 💬 Copilot

All 42 tests pass. Let me do a final review of the changes:

---

<sub>⏱️ 4m 51s</sub>

### ✅ `bash`

**Show changed files summary**

$ cd /tmp/ops-upgrade-experiment/indico-operator__action-classes__C2 && git --no-pager diff --stat

<details>
<summary>6 lines</summary>

```
requirements.txt                   |  2 +-
 src/charm.py                       | 39 +++++++++++++++++++++++++++++----------
 tests/unit_harness/test_actions.py | 14 +++++++++++++-
 tox.ini                            |  2 +-
 4 files changed, 44 insertions(+), 13 deletions(-)
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 4m 55s</sub>

### ✅ `bash`

**Show charm.py diff**

$ cd /tmp/ops-upgrade-experiment/indico-operator__action-classes__C2 && git --no-pager diff src/charm.py

<details>
<summary>109 lines</summary>

```diff
diff --git a/src/charm.py b/src/charm.py
index 1040d7d..8f72e2f 100755
--- a/src/charm.py
+++ b/src/charm.py
@@ -11,6 +11,7 @@ import logging
 import os
 import secrets
 import typing
+from dataclasses import dataclass
 from re import findall
 from typing import Any, Dict, Iterator, List, Optional, Tuple
 from urllib.parse import urlparse
@@ -49,6 +50,21 @@ SAML_GROUPS_PLUGIN_NAME = "saml_groups"
 UWSGI_TOUCH_RELOAD = "/srv/indico/indico.wsgi"
 
 
+@dataclass
+class AddAdminParams:
+    """Parameters for the add-admin action."""
+
+    email: str
+    password: str
+
+
+@dataclass
+class AnonymizeUserParams:
+    """Parameters for the anonymize-user action."""
+
+    email: str
+
+
 class InvalidRedisNameError(Exception):
     """Represents invalid redis name error."""
 
@@ -901,6 +917,7 @@ class IndicoOperatorCharm(CharmBase):  # pylint: disable=too-many-instance-attri
         Args:
             event: Event triggered by the add_admin action
         """
+        params = event.load_params(AddAdminParams)
         container = self.unit.get_container("indico")
         indico_env_config = self._get_indico_env_config_str(container)
 
@@ -908,8 +925,8 @@ class IndicoOperatorCharm(CharmBase):  # pylint: disable=too-many-instance-attri
             "/usr/bin/indico",
             "autocreate",
             "admin",
-            event.params["email"],
-            event.params["password"],
+            params.email,
+            params.password,
         ]
 
         if container.can_connect():
@@ -921,27 +938,28 @@ class IndicoOperatorCharm(CharmBase):  # pylint: disable=too-many-instance-attri
             )
             try:
                 output = process.wait_output()
-                event.set_results({"user": f"{event.params['email']}", "output": output})
+                event.set_results({"user": f"{params.email}", "output": output})
             except ExecError as ex:
                 logger.exception("Action add-admin failed: %s", ex.stdout)
 
                 event.fail(
                     # Parameter validation errors are printed to stdout
-                    f"Failed to create admin {event.params['email']}: {ex.stdout!r}"
+                    f"Failed to create admin {params.email}: {ex.stdout!r}"
                 )
 
-    def _execute_anonymize_cmd(self, event: ActionEvent) -> Iterator[str]:
+    def _execute_anonymize_cmd(self, event: ActionEvent, params: AnonymizeUserParams) -> Iterator[str]:
         """Execute anonymize command for each email.
 
         Args:
             event (ActionEvent): Event triggered by the anonymize-user action
+            params (AnonymizeUserParams): Parsed parameters for the anonymize-user action
 
         Yields:
             Iterator[str]: Output of each command execution
         """
         container = self.unit.get_container("indico")
         indico_env_config = self._get_indico_env_config_str(container)
-        for email in event.params["email"].split(EMAIL_LIST_SEPARATOR):
+        for email in params.email.split(EMAIL_LIST_SEPARATOR):
             cmd = [
                 "/usr/bin/indico",
                 "anonymize",
@@ -969,7 +987,7 @@ class IndicoOperatorCharm(CharmBase):  # pylint: disable=too-many-instance-attri
                 yield out[0].replace("\n", "")
             except ExecError as ex:
                 logger.exception("Action anonymize-user failed: %s", ex.stdout)
-                fail_msg = f"Failed to anonymize user {event.params['email']}: {ex.stdout!r}"
+                fail_msg = f"Failed to anonymize user {params.email}: {ex.stdout!r}"
                 event.fail("Failed to anonymize one or more users, please verify the results.")
                 yield fail_msg
 
@@ -982,7 +1000,8 @@ class IndicoOperatorCharm(CharmBase):  # pylint: disable=too-many-instance-attri
         Args:
             event: Event triggered by the anonymize-user action
         """
-        if len(event.params["email"].split(EMAIL_LIST_SEPARATOR)) > EMAIL_LIST_MAX:
+        params = event.load_params(AnonymizeUserParams)
+        if len(params.email.split(EMAIL_LIST_SEPARATOR)) > EMAIL_LIST_MAX:
             max_reached_msg = (
                 "Failed to anonymize user: "
                 f"List of more than {EMAIL_LIST_MAX} emails are not allowed"
@@ -990,10 +1009,10 @@ class IndicoOperatorCharm(CharmBase):  # pylint: disable=too-many-instance-attri
             logger.error("Action anonymize-user failed: %s", max_reached_msg)
             event.fail(max_reached_msg)
             return
-        output_list = list(self._execute_anonymize_cmd(event))
+        output_list = list(self._execute_anonymize_cmd(event, params))
         event.set_results(
             {
-                "user": f"{event.params['email']}",
+                "user": f"{params.email}",
                 "output": EMAIL_LIST_SEPARATOR.join(output_list),
             }
         )
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 5m 2s</sub>

### 💬 Copilot

Now commit the changes:

---

<sub>⏱️ 5m 3s</sub>

### ✅ `bash`

**Commit changes**

$ cd /tmp/ops-upgrade-experiment/indico-operator__action-classes__C2 && git add -A && git commit -m "Use ActionEvent.load_params() with dataclasses for action params

Replace raw event.params dict access with typed dataclasses and
ActionEvent.load_params(), as introduced in ops 2.23.0.

- Add AddAdminParams and AnonymizeUserParams dataclasses
- Update _add_admin_action, _anonymize_user_action, and
  _execute_anonymize_cmd to use load_params()
- Bump minimum ops version to >=2.23.0 in requirements.txt and tox.ini
- Update tests to configure load_params mock return values

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"

```
[detached HEAD 4e16120] Use ActionEvent.load_params() with dataclasses for action params
 5 files changed, 45 insertions(+), 13 deletions(-)
 create mode 100644 .baseline_commit
<exited with exit code 0>
```


---

<sub>⏱️ 5m 12s</sub>

### ✅ `task_complete`

**Updated the charm to use `ActionEvent.load_params()` with Python dataclasses, replacing raw `event.params` dict access:

1. **`src/charm.py`**: Added `from dataclasses import dataclass` import; added two dataclasses (`AddAdminParams` with `email`/`password`, `AnonymizeUserParams` with `email`); updated `_add_admin_action` and `_anonymize_user_action` to call `event.load_params(...)`, and updated `_execute_anonymize_cmd` to accept the parsed `AnonymizeUserParams` instance instead of re-accessing `event.params`.

2. **`requirements.txt`** and **`tox.ini`**: Bumped minimum ops version from `>=2.0.0` / `==2.21.1` to `>=2.23.0` (where `load_params` was introduced).

3. **`tests/unit_harness/test_actions.py`**: Imported the new dataclasses and configured `event.load_params.return_value` in each action test so mocks return properly typed param objects.

All 42 unit tests pass.**

<details>
<summary>Arguments</summary>

```json
{
  "summary": "Updated the charm to use `ActionEvent.load_params()` with Python dataclasses, replacing raw `event.params` dict access:\n\n1. **`src/charm.py`**: Added `from dataclasses import dataclass` import; added two dataclasses (`AddAdminParams` with `email`/`password`, `AnonymizeUserParams` with `email`); updated `_add_admin_action` and `_anonymize_user_action` to call `event.load_params(...)`, and updated `_execute_anonymize_cmd` to accept the parsed `AnonymizeUserParams` instance instead of re-accessing `event.params`.\n\n2. **`requirements.txt`** and **`tox.ini`**: Bumped minimum ops version from `>=2.0.0` / `==2.21.1` to `>=2.23.0` (where `load_params` was introduced).\n\n3. **`tests/unit_harness/test_actions.py`**: Imported the new dataclasses and configured `event.load_params.return_value` in each action test so mocks return properly typed param objects.\n\nAll 42 unit tests pass."
}
```

</details>

<details>
<summary>5 lines</summary>

```
Updated the charm to use `ActionEvent.load_params()` with Python dataclasses, replacing raw `event.params` dict access:

1. **`src/charm.py`**: Added `from dataclasses import dataclass` import; added two dataclasses (`AddAdminParams` with `email`/`password`, `AnonymizeUserParams` with `email`); updated `_add_admin_action` and `_anonymize_user_action` to call `event.load_params(...)`, and updated `_execute_anonymize_cmd` to accept the parsed `AnonymizeUserParams` instance instead of re-accessing `event.params`.

2. **`requirements.txt`** and **`tox.ini`**: Bumped minimum ops version from `>=2.0.0` / `==2.21.1` to `>=2.23.0` (where `load_params` was introduced).

3. **`tests/unit_harness/test_actions.py`**: Imported the new dataclasses and configured `event.load_params.return_value` in each action test so mocks return properly typed param objects.

All 42 unit tests pass.
```

</details>


---

<sub>⏱️ 5m 17s</sub>

### ℹ️ Info

Response was interrupted due to a server error. Retrying...

---

<sub>⏱️ 5m 21s</sub>

### ℹ️ Info

Response was interrupted due to a server error. Retrying...

---

<sub>⏱️ 5m 25s</sub>

### ℹ️ Info

Response was interrupted due to a server error. Retrying...

---

<sub>⏱️ 5m 29s</sub>

### ℹ️ Info

Response was interrupted due to a server error. Retrying...

---

<sub>⏱️ 5m 34s</sub>

### ℹ️ Info

Response was interrupted due to a server error. Retrying...

---

<sub>⏱️ 5m 38s</sub>

### ❌ Error

Execution failed: Error: Failed to get response from the AI model; retried 5 times (total retry wait time: 5.8423304783833245 seconds) Last error: Unknown error

---

<sub>Generated by [GitHub Copilot CLI](https://github.com/features/copilot/cli)</sub>
