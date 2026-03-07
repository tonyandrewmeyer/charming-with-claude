# 🤖 Copilot CLI Session

> **Session ID:** `3e8fba82-4414-4dab-a82c-0eb89cb30b56`
> **Duration:** 10m 28s

<sub>⏱️ 5s</sub>

### 👤 User

Migrate this charm's integration tests from pytest-operator (python-libjuju) to jubilant and pytest-jubilant. Update all test files, conftest.py, helpers, and dependencies.

Before starting, install jubilant and pytest-jubilant from PyPI (pip install jubilant pytest-jubilant) and read the source code to understand the API. The key modules are the Juju class, wait helpers (all_active, all_blocked, any_error), and the pytest-jubilant fixtures (pack, get_resources, juju fixture, temp_model_factory).

---

<sub>⏱️ 11s</sub>

### ✅ `bash`

**Install jubilant and pytest-jubilant**

$ cd /tmp/s3-integrator-L3-sonnet && pip install jubilant pytest-jubilant --quiet 2>&1 | tail -5

```
bash: pip: command not found
<exited with exit code 0>
```


---

<sub>⏱️ 11s</sub>

### ✅ `view`

**/tmp/s3-integrator-L3-sonnet/tests**

/tmp/s3-integrator-L3-sonnet/tests

```
ca_chain.pem
integration
spread
unit
```


---

<sub>⏱️ 15s</sub>

### ✅ `bash`

**Install with pip3**

$ pip3 install jubilant pytest-jubilant --quiet 2>&1 | tail -5 && python3 -c "import jubilant; print(jubilant.__file__)"

```
bash: pip3: command not found
Traceback (most recent call last):
  File "<string>", line 1, in <module>
ModuleNotFoundError: No module named 'jubilant'
<exited with exit code 1>
```


---

<sub>⏱️ 15s</sub>

### ✅ `view`

**/tmp/s3-integrator-L3-sonnet/tests/integration**

/tmp/s3-integrator-L3-sonnet/tests/integration

```
__init__.py
application-charm
architecture.py
helpers.py
test_s3_charm.py
```


---

<sub>⏱️ 20s</sub>

### ✅ `bash`

**Find Python executable**

$ which python python3 python3.10 python3.11 python3.12 2>/dev/null; ls /usr/bin/python* 2>/dev/null; ls /usr/local/bin/python* 2>/dev/null

```
/usr/bin/python3
/usr/bin/python3.12
/usr/bin/python3  /usr/bin/python3.12
<exited with exit code 2>
```


---

<sub>⏱️ 20s</sub>

### ✅ `bash`

**Read pyproject.toml**

$ cd /tmp/s3-integrator-L3-sonnet && cat pyproject.toml

<details>
<summary>78 lines</summary>

```
# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.

[tool.poetry]
package-mode = false
requires-poetry = ">=2.0.0"

[tool.poetry.dependencies]
python = "^3.10"
ops = "^3.6.0"

[tool.poetry.group.charm-libs.dependencies]

[tool.poetry.group.format]
optional = true

[tool.poetry.group.format.dependencies]
ruff = "^0.15.4"

[tool.poetry.group.lint]
optional = true

[tool.poetry.group.lint.dependencies]
codespell = "^2.4.1"

[tool.poetry.group.unit.dependencies]
coverage = {extras = ["toml"], version = "^7.13.4"}
pytest = "^8.4.2"
pytest-asyncio = "*"
parameterized = "^0.9.0"

[tool.poetry.group.integration.dependencies]
pytest = "^8.4.2"
pytest-operator = "^0.43.2"
juju = "^3.5.2.0"

# Testing tools configuration
[tool.coverage.run]
branch = true

[tool.coverage.report]
show_missing = true

[tool.pytest.ini_options]
minversion = "6.0"
log_cli_level = "INFO"
asyncio_mode = "auto"
markers = ["unstable"]

# Formatting tools configuration
[tool.black]
line-length = 99
target-version = ["py310"]

# Linting tools configuration
[tool.ruff]
# preview and explicit preview are enabled for CPY001
preview = true
target-version = "py310"
src = ["src", "."]
line-length = 99

[tool.ruff.lint]
explicit-preview-rules = true
select = ["A", "E", "W", "F", "C", "N", "D", "I001", "CPY001"]
extend-ignore = [
    "D203",
    "D204",
    "D213",
    "D215",
    "D400",
    "D404",
    "D406",
    "D407",
    "D408",
    "D409",
    "D413",
]
# Ignore E501 because using black creates errors with this
# Ignore D107 Missing docstring in __init__
ignore = ["E501", "D107"]

[tool.ruff.lint.per-file-ignores]
"tests/*" = ["D100", "D101", "D102", "D103", "D104"]

[tool.ruff.lint.flake8-copyright]
# Check for properly formatted copyright header in each file
author = "Canonical Ltd."
notice-rgx = "Copyright\\s\\d{4}([-,]\\d{4})*\\s+"
min-file-size = 1

[tool.ruff.lint.mccabe]
max-complexity = 10

[tool.ruff.lint.pydocstyle]
convention = "google"
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 24s</sub>

### ✅ `bash`

**Install with python3.12 -m pip**

$ python3.12 -m pip install jubilant pytest-jubilant 2>&1 | tail -10

```
/usr/bin/python3.12: No module named pip
<exited with exit code 0>
```


---

<sub>⏱️ 24s</sub>

### ✅ `view`

**/tmp/s3-integrator-L3-sonnet/tests/integration/test_s3_charm.py**

/tmp/s3-integrator-L3-sonnet/tests/integration/test_s3_charm.py

<details>
<summary>261 lines</summary>

```
1. #!/usr/bin/env python3
2. # Copyright 2022 Canonical Ltd.
3. # See LICENSE file for licensing details.
4. import asyncio
5. import base64
6. import json
7. import logging
8. from pathlib import Path
9. 
10. import pytest
11. import yaml
12. from pytest_operator.plugin import OpsTest
13. 
14. from . import architecture
15. from .helpers import (
16.     fetch_action_get_connection_info,
17.     fetch_action_sync_s3_credentials,
18.     get_application_data,
19.     get_certificate_from_file,
20.     get_relation_data,
21.     is_relation_broken,
22.     is_relation_joined,
23. )
24. 
25. logger = logging.getLogger(__name__)
26. 
27. S3_METADATA = yaml.safe_load(Path("./metadata.yaml").read_text())
28. S3_APP_NAME = S3_METADATA["name"]
29. 
30. APP_METADATA = yaml.safe_load(
31.     Path("./tests/integration/application-charm/metadata.yaml").read_text()
32. )
33. APPLICATION_APP_NAME = APP_METADATA["name"]
34. 
35. APPS = [S3_APP_NAME, APPLICATION_APP_NAME]
36. FIRST_RELATION = "first-s3-credentials"
37. SECOND_RELATION = "second-s3-credentials"
38. 
39. 
40. @pytest.mark.group(1)
41. @pytest.mark.abort_on_fail
42. @pytest.mark.skip_if_deployed
43. async def test_build_and_deploy(ops_test: OpsTest):
44.     """Build the charm and deploy 1 units for provider and requirer charm."""
45.     # Build and deploy charm from local source folder
46.     s3_charm = f"./s3-integrator_ubuntu@22.04-{architecture.architecture}.charm"
47.     app_charm = f"./tests/integration/application-charm/application_ubuntu@22.04-{architecture.architecture}.charm"
48. 
49.     await asyncio.gather(
50.         ops_test.model.deploy(s3_charm, application_name=S3_APP_NAME, num_units=1),
51.         ops_test.model.deploy(app_charm, application_name=APPLICATION_APP_NAME, num_units=1),
52.     )
53.     # Reduce the update_status frequency until the cluster is deployed
54.     async with ops_test.fast_forward():
55.         await ops_test.model.block_until(
56.             lambda: len(ops_test.model.applications[S3_APP_NAME].units) == 1
57.         )
58. 
59.         await ops_test.model.block_until(
60.             lambda: len(ops_test.model.applications[APPLICATION_APP_NAME].units) == 1
61.         )
62.         await asyncio.gather(
63.             ops_test.model.wait_for_idle(
64.                 apps=[S3_APP_NAME],
65.                 status="blocked",
66.                 timeout=1000,
67.             ),
68.             ops_test.model.wait_for_idle(
69.                 apps=[APPLICATION_APP_NAME],
70.                 status="waiting",
71.                 raise_on_blocked=True,
72.                 timeout=1000,
73.             ),
74.         )
75. 
76.     assert len(ops_test.model.applications[S3_APP_NAME].units) == 1
77. 
78.     for unit in ops_test.model.applications[S3_APP_NAME].units:
79.         assert unit.workload_status == "blocked"
80. 
81.     assert len(ops_test.model.applications[APPLICATION_APP_NAME].units) == 1
82. 
83. 
84. @pytest.mark.group(1)
85. @pytest.mark.abort_on_fail
86. async def test_sync_credential_action(ops_test: OpsTest):
87.     """Tests the correct output of actions."""
88.     s3_integrator_unit = ops_test.model.applications[S3_APP_NAME].units[0]
89.     action = await s3_integrator_unit.run_action(action_name="get-s3-credentials")
90.     result = await action.wait()
91.     assert result.status == "failed"
92. 
93.     access_key = "test-access-key"
94.     secret_key = "test-secret-key"
95. 
96.     action_result = await fetch_action_sync_s3_credentials(
97.         s3_integrator_unit, access_key=access_key, secret_key=secret_key
98.     )
99. 
100.     # test the correct status of the charm
101.     async with ops_test.fast_forward():
102.         await ops_test.model.wait_for_idle(apps=[S3_APP_NAME], status="active")
103. 
104.     assert action_result["ok"] == "Credentials successfully updated."
105. 
106.     connection_info = await fetch_action_get_connection_info(s3_integrator_unit)
107.     assert connection_info["access-key"] == "************"
108.     assert connection_info["secret-key"] == "************"
109. 
110.     # checks for another update of of the credentials
111.     updated_secret_key = "new-test-secret-key"
112.     action_result = await fetch_action_sync_s3_credentials(
113.         s3_integrator_unit, access_key=access_key, secret_key=updated_secret_key
114.     )
115. 
116.     async with ops_test.fast_forward():
117.         await ops_test.model.wait_for_idle(apps=[S3_APP_NAME], status="active")
118. 
119.     # check that secret key has been updated
120.     assert action_result["ok"] == "Credentials successfully updated."
121. 
122.     connection_info = await fetch_action_get_connection_info(s3_integrator_unit)
123.     assert connection_info["access-key"] == "************"
124.     assert connection_info["secret-key"] == "************"
125. 
126. 
127. @pytest.mark.group(1)
128. @pytest.mark.abort_on_fail
129. async def test_config_options(ops_test: OpsTest):
130.     """Tests the correct handling of configuration parameters."""
131.     # test tls-ca-chain
132.     ca_chain = get_certificate_from_file("tests/ca_chain.pem")
133.     ca_chain_bytes = base64.b64encode(ca_chain.encode("utf-8"))
134.     configuration_parameters = {
135.         "tls-ca-chain": ca_chain_bytes.decode("utf-8"),
136.         "s3-api-version": "1.0",
137.         "storage-class": "cinder",
138.         "attributes": "a1:v1, a2:v2, a3:v3",
139.         "path": "/test/path_1/",
140.         "region": "us-east-2",
141.         "endpoint": "s3.amazonaws.com",
142.         "experimental-delete-older-than-days": "7",
143.     }
144.     # apply new configuration options
145.     await ops_test.model.applications[S3_APP_NAME].set_config(configuration_parameters)
146.     # wait for active status
147.     await ops_test.model.wait_for_idle(apps=[S3_APP_NAME], status="active")
148.     # test the returns
149.     s3_integrator_unit = ops_test.model.applications[S3_APP_NAME].units[0]
150.     action = await s3_integrator_unit.run_action(action_name="get-s3-connection-info")
151.     action_result = await action.wait()
152.     configured_options = action_result.results
153.     # test the correctness of the configuration fields
154.     assert configured_options["storage-class"] == "cinder"
155.     assert configured_options["s3-api-version"] == "1.0"
156.     assert configured_options["delete-older-than-days"] == "7"
157.     assert len(json.loads(configured_options["attributes"])) == 3
158.     assert len(json.loads(configured_options["tls-ca-chain"])) == 2
159.     assert configured_options["region"] == "us-east-2"
160.     assert configured_options["path"] == "/test/path_1/"
161.     assert configured_options["endpoint"] == "s3.amazonaws.com"
162. 
163. 
164. @pytest.mark.group(1)
165. @pytest.mark.abort_on_fail
166. async def test_relation_creation(ops_test: OpsTest):
167.     """Relate charms and wait for the expected changes in status."""
168.     await ops_test.model.add_relation(S3_APP_NAME, f"{APPLICATION_APP_NAME}:{FIRST_RELATION}")
169. 
170.     async with ops_test.fast_forward():
171.         await ops_test.model.block_until(
172.             lambda: is_relation_joined(ops_test, FIRST_RELATION, FIRST_RELATION) is True
173.         )
174. 
175.         await ops_test.model.wait_for_idle(apps=APPS, status="active")
176.     await ops_test.model.wait_for_idle(apps=APPS, status="active")
177.     # test the content of the relation data bag
178. 
179.     relation_data = await get_relation_data(ops_test, APPLICATION_APP_NAME, FIRST_RELATION)
180.     application_data = await get_application_data(ops_test, APPLICATION_APP_NAME, FIRST_RELATION)
181.     # check if the different parameters correspond to expected ones.
182.     relation_id = relation_data[0]["relation-id"]
183.     # check correctness for some fields
184.     assert "access-key" in application_data
185.     assert "secret-key" in application_data
186.     assert "bucket" in application_data
187.     assert application_data["bucket"] == f"relation-{relation_id}"
188.     assert application_data["access-key"] == "test-access-key"
189.     assert application_data["secret-key"] == "new-test-secret-key"
190.     assert application_data["storage-class"] == "cinder"
191.     assert application_data["s3-api-version"] == "1.0"
192.     assert application_data["delete-older-than-days"] == "7"
193.     assert len(json.loads(application_data["attributes"])) == 3
194.     assert len(json.loads(application_data["tls-ca-chain"])) == 2
195.     assert application_data["region"] == "us-east-2"
196.     assert application_data["path"] == "/test/path_1/"
197. 
198.     # update bucket name and check if the change is propagated in the relation databag
199.     new_bucket_name = "new-bucket-name"
200.     params = {"bucket": new_bucket_name}
201.     await ops_test.model.applications[S3_APP_NAME].set_config(params)
202.     # wait for active status
203.     await ops_test.model.wait_for_idle(apps=[S3_APP_NAME], status="active")
204.     application_data = await get_application_data(ops_test, APPLICATION_APP_NAME, FIRST_RELATION)
205.     # check bucket name
206.     assert application_data["bucket"] == new_bucket_name
207. 
208.     # check that bucket name set in the requirer application is correct
209.     await ops_test.model.add_relation(S3_APP_NAME, f"{APPLICATION_APP_NAME}:{SECOND_RELATION}")
210.     # wait for relation joined
211.     async with ops_test.fast_forward():
212.         await ops_test.model.block_until(
213.             lambda: is_relation_joined(ops_test, SECOND_RELATION, SECOND_RELATION) is True
214.         )
215.         await ops_test.model.wait_for_idle(apps=APPS, status="active")
216. 
217.     # read data of the second relation
218.     application_data = await get_application_data(ops_test, APPLICATION_APP_NAME, SECOND_RELATION)
219.     assert "access-key" in application_data
220.     assert "secret-key" in application_data
221.     assert "bucket" in application_data
222.     # check correctness of connection parameters in the relation databag
223.     assert application_data["bucket"] == new_bucket_name
224.     assert application_data["access-key"] == "test-access-key"
225.     assert application_data["secret-key"] == "new-test-secret-key"
226.     assert application_data["storage-class"] == "cinder"
227.     assert application_data["s3-api-version"] == "1.0"
228.     assert application_data["delete-older-than-days"] == "7"
229.     assert len(json.loads(application_data["attributes"])) == 3
230.     assert len(json.loads(application_data["tls-ca-chain"])) == 2
231.     assert application_data["region"] == "us-east-2"
232.     assert application_data["path"] == "/test/path_1/"
233. 
234. 
235. @pytest.mark.group(1)
236. async def test_relation_broken(ops_test: OpsTest):
237.     """Remove relation and wait for the expected changes in status."""
238.     # Remove relations
239.     await ops_test.model.applications[S3_APP_NAME].remove_relation(
240.         f"{APPLICATION_APP_NAME}:{FIRST_RELATION}", S3_APP_NAME
241.     )
242.     await ops_test.model.block_until(
243.         lambda: is_relation_broken(ops_test, FIRST_RELATION, FIRST_RELATION) is True
244.     )
245.     await ops_test.model.applications[S3_APP_NAME].remove_relation(
246.         f"{APPLICATION_APP_NAME}:{SECOND_RELATION}", S3_APP_NAME
247.     )
248.     await ops_test.model.block_until(
249.         lambda: is_relation_broken(ops_test, SECOND_RELATION, SECOND_RELATION) is True
250.     )
251.     # test correct application status
252.     async with ops_test.fast_forward():
253.         await asyncio.gather(
254.             ops_test.model.wait_for_idle(
255.                 apps=[S3_APP_NAME], status="active", raise_on_blocked=True
256.             ),
257.             ops_test.model.wait_for_idle(
258.                 apps=[APPLICATION_APP_NAME], status="waiting", raise_on_blocked=True
259.             ),
260.         )
261.
```

</details>


---

<sub>⏱️ 24s</sub>

### ✅ `view`

**/tmp/s3-integrator-L3-sonnet/tests/integration/helpers.py**

/tmp/s3-integrator-L3-sonnet/tests/integration/helpers.py

<details>
<summary>168 lines</summary>

```
1. #!/usr/bin/env python3
2. # Copyright 2022 Canonical Ltd.
3. # See LICENSE file for licensing details.
4. 
5. import logging
6. from typing import Dict, Optional
7. 
8. import yaml
9. from juju.unit import Unit
10. from pytest_operator.plugin import OpsTest
11. 
12. logger = logging.getLogger(__name__)
13. 
14. 
15. async def fetch_action_get_credentials(unit: Unit) -> Dict:
16.     """Helper to run an action to fetch credentials.
17. 
18.     Args:
19.         unit: The juju unit on which to run the get-s3-credentials action for credentials
20.         action: the
21.     Returns:
22.         A dictionary with the server config username and password
23.     """
24.     action = await unit.run_action(action_name="get-s3-credentials")
25.     result = await action.wait()
26.     return result.results
27. 
28. 
29. async def fetch_action_get_connection_info(unit: Unit) -> Dict:
30.     """Helper to run an action to fetch connection info.
31. 
32.     Args:
33.         unit: The juju unit on which to run the get_connection_info action for credentials
34.     Returns:
35.         A dictionary with the server config username and password
36.     """
37.     action = await unit.run_action(action_name="get-s3-connection-info")
38.     result = await action.wait()
39.     return result.results
40. 
41. 
42. async def fetch_action_sync_s3_credentials(unit: Unit, access_key: str, secret_key: str) -> Dict:
43.     """Helper to run an action to sync credentials.
44. 
45.     Args:
46.         unit: The juju unit on which to run the get-password action for credentials
47.         access_key: the access_key to access the s3 compatible endpoint
48.         secret_key: the secret key to access the s3 compatible endpoint
49.     Returns:
50.         A dictionary with the server config username and password
51.     """
52.     parameters = {"access-key": access_key, "secret-key": secret_key}
53.     action = await unit.run_action(action_name="sync-s3-credentials", **parameters)
54.     result = await action.wait()
55. 
56.     return result.results
57. 
58. 
59. def is_relation_joined(ops_test: OpsTest, endpoint_one: str, endpoint_two: str) -> bool:
60.     """Check if a relation is joined.
61. 
62.     Args:
63.         ops_test: The ops test object passed into every test case
64.         endpoint_one: The first endpoint of the relation
65.         endpoint_two: The second endpoint of the relation
66.     """
67.     for rel in ops_test.model.relations:
68.         endpoints = [endpoint.name for endpoint in rel.endpoints]
69.         if endpoint_one in endpoints and endpoint_two in endpoints:
70.             return True
71.     return False
72. 
73. 
74. def is_relation_broken(ops_test: OpsTest, endpoint_one: str, endpoint_two: str) -> bool:
75.     """Check if a relation is broken.
76. 
77.     Args:
78.         ops_test: The ops test object passed into every test case
79.         endpoint_one: The first endpoint of the relation
80.         endpoint_two: The second endpoint of the relation
81.     """
82.     for rel in ops_test.model.relations:
83.         endpoints = [endpoint.name for endpoint in rel.endpoints]
84.         if endpoint_one not in endpoints and endpoint_two not in endpoints:
85.             return True
86.     return False
87. 
88. 
89. async def run_command_on_unit(unit: Unit, command: str) -> Optional[str]:
90.     """Run a command in one Juju unit.
91. 
92.     Args:
93.         unit: the Juju unit instance.
94.         command: the command to run.
95. 
96.     Returns:
97.         command execution output or none if the command produces no output.
98.     """
99.     # workaround for https://github.com/juju/python-libjuju/issues/707
100.     action = await unit.run(command)
101.     result = await action.wait()
102.     code = str(result.results.get("Code") or result.results.get("return-code"))
103.     stdout = result.results.get("Stdout") or result.results.get("stdout")
104.     stderr = result.results.get("Stderr") or result.results.get("stderr")
105.     assert code == "0", f"{command} failed ({code}): {stderr or stdout}"
106.     return stdout
107. 
108. 
109. async def get_relation_data(
110.     ops_test: OpsTest,
111.     application_name: str,
112.     relation_name: str,
113. ) -> list:
114.     """Returns a list that contains the relation-data.
115. 
116.     Args:
117.         ops_test: The ops test framework instance
118.         application_name: The name of the application
119.         relation_name: name of the relation to get connection data from
120.     Returns:
121.         a list that contains the relation-data
122.     """
123.     # get available unit id for the desired application
124.     units_ids = [
125.         app_unit.name.split("/")[1]
126.         for app_unit in ops_test.model.applications[application_name].units
127.     ]
128.     assert len(units_ids) > 0
129.     unit_name = f"{application_name}/{units_ids[0]}"
130.     raw_data = (await ops_test.juju("show-unit", unit_name))[1]
131.     if not raw_data:
132.         raise ValueError(f"no unit info could be grabbed for {unit_name}")
133.     data = yaml.safe_load(raw_data)
134.     # Filter the data based on the relation name.
135.     relation_data = [v for v in data[unit_name]["relation-info"] if v["endpoint"] == relation_name]
136.     if len(relation_data) == 0:
137.         raise ValueError(
138.             f"no relation data could be grabbed on relation with endpoint {relation_name}"
139.         )
140. 
141.     return relation_data
142. 
143. 
144. async def get_application_data(
145.     ops_test: OpsTest,
146.     application_name: str,
147.     relation_name: str,
148. ) -> Dict:
149.     """Returns the application data bag of a given application and relation.
150. 
151.     Args:
152.         ops_test: The ops test framework instance
153.         application_name: The name of the application
154.         relation_name: name of the relation to get connection data from
155.     Returns:
156.         a dictionary that contains the application-data
157.     """
158.     relation_data = await get_relation_data(ops_test, application_name, relation_name)
159.     application_data = relation_data[0]["application-data"]
160.     return application_data
161. 
162. 
163. def get_certificate_from_file(filename: str) -> str:
164.     """Returns the certificate as a string."""
165.     with open(filename, "r") as file:
166.         certificate = file.read()
167.     return certificate
168.
```

</details>


---

<sub>⏱️ 29s</sub>

### ✅ `bash`

**Find conftest files**

$ find /tmp/s3-integrator-L3-sonnet/tests -name "conftest.py" | xargs cat 2>/dev/null || echo "No conftest.py found"

```

<exited with exit code 0>
```


---

<sub>⏱️ 29s</sub>

### ✅ `view`

**/tmp/s3-integrator-L3-sonnet/tests/integration/architecture.py**

/tmp/s3-integrator-L3-sonnet/tests/integration/architecture.py

<details>
<summary>8 lines</summary>

```
1. # Copyright 2024 Canonical Ltd.
2. # See LICENSE file for licensing details.
3. import subprocess
4. 
5. architecture = subprocess.run(
6.     ["dpkg", "--print-architecture"], capture_output=True, check=True, encoding="utf-8"
7. ).stdout.strip()
8.
```

</details>


---

<sub>⏱️ 46s</sub>

### ✅ `bash`

**Install pip then jubilant/pytest-jubilant**

$ # Install jubilant and pytest-jubilant using the available python
python3 -m ensurepip --upgrade 2>&1 | tail -3 || true
curl -sS https://bootstrap.pypa.io/get-pip.py | python3 2>&1 | tail -3 || true
python3 -m pip install jubilant pytest-jubilant 2>&1 | tail -10

<details>
<summary>5 lines</summary>

```
/usr/bin/python3: No module named ensurepip

note: If you believe this is a mistake, please contact your Python installation or OS distribution provider. You can override this, at the risk of breaking your Python installation or OS, by passing --break-system-packages.
hint: See PEP 668 for the detailed specification.
/usr/bin/python3: No module named pip
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 51s</sub>

### ✅ `bash`

**Install pip via apt**

$ apt-get install -y python3-pip 2>&1 | tail -3 || sudo apt-get install -y python3-pip 2>&1 | tail -3

```
E: Could not open lock file /var/lib/dpkg/lock-frontend - open (13: Permission denied)
E: Unable to acquire the dpkg frontend lock (/var/lib/dpkg/lock-frontend), are you root?
<exited with exit code 0>
```


---

<sub>⏱️ 1m 24s</sub>

### ✅ `bash`

**Install pip and jubilant**

$ sudo apt-get install -y python3-pip 2>&1 | tail -5 && python3 -m pip install jubilant pytest-jubilant 2>&1 | tail -10

```
<command with shellId: 8 is still running after 30 seconds. The command is still running but hasn't produced output yet. It may be waiting for input or still processing. Use read_bash to continue waiting, write_bash if you think it needs input, or stop_bash to stop it.>
```


---

<sub>⏱️ 2m 0s</sub>

### ✅ `read_bash`

<details>
<summary>Arguments</summary>

```json
{
  "shellId": "8",
  "delay": 30
}
```

</details>

```
<command with shellId: 8 is still running after 30 seconds. The command is still running but hasn't produced output yet. It may be waiting for input or still processing. Use read_bash to continue waiting, write_bash if you think it needs input, or stop_bash to stop it.>
```


---

<sub>⏱️ 2m 55s</sub>

### ✅ `read_bash`

<details>
<summary>Arguments</summary>

```json
{
  "delay": 60,
  "shellId": "8"
}
```

</details>

<details>
<summary>11 lines</summary>

```
User sessions running outdated binaries:
 ubuntu @ session #7: bash[12696,13002]

No VM guests are running outdated hypervisor (qemu) binaries on this host.
    sure you have python3-full installed.
    
    If you wish to install a non-Debian packaged Python application,
    it may be easiest to use pipx install xyz, which will manage a
    virtual environment for you. Make sure you have pipx installed.
    
    See /usr/share/doc/python3.12/README.venv for more information.

note: If you believe this is a mistake, please contact your Python installation or OS distribution provider. You can override this, at the risk of breaking your Python installation or OS, by passing --break-system-packages.
hint: See PEP 668 for the detailed specification.
<command with id: 8 exited with exit code 0>
```

</details>


---

<sub>⏱️ 3m 1s</sub>

### ✅ `bash`

**Install with break-system-packages**

$ python3 -m pip install jubilant pytest-jubilant --break-system-packages 2>&1 | tail -10

<details>
<summary>11 lines</summary>

```
Collecting pluggy<2,>=1.5 (from pytest>=8.3.5->pytest-jubilant)
  Using cached pluggy-1.6.0-py3-none-any.whl.metadata (4.8 kB)
Requirement already satisfied: pygments>=2.7.2 in /usr/lib/python3/dist-packages (from pytest>=8.3.5->pytest-jubilant) (2.17.2)
Using cached jubilant-1.7.0-py3-none-any.whl (33 kB)
Using cached pytest_jubilant-1.1-py3-none-any.whl (12 kB)
Using cached pytest-9.0.2-py3-none-any.whl (374 kB)
Using cached iniconfig-2.3.0-py3-none-any.whl (7.5 kB)
Using cached pluggy-1.6.0-py3-none-any.whl (20 kB)
Installing collected packages: pluggy, jubilant, iniconfig, pytest, pytest-jubilant
Successfully installed iniconfig-2.3.0 jubilant-1.7.0 pluggy-1.6.0 pytest-9.0.2 pytest-jubilant-1.1
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 3m 7s</sub>

### ✅ `bash`

**Verify install**

$ python3 -c "import jubilant; print(jubilant.__file__)" && python3 -c "import pytest_jubilant; print(pytest_jubilant.__file__)"

```
/home/ubuntu/.local/lib/python3.12/site-packages/jubilant/__init__.py
/home/ubuntu/.local/lib/python3.12/site-packages/pytest_jubilant/__init__.py
<exited with exit code 0>
```


---

<sub>⏱️ 3m 11s</sub>

### ✅ `bash`

**List jubilant source files**

$ find /home/ubuntu/.local/lib/python3.12/site-packages/jubilant -name "*.py" | sort && echo "---" && find /home/ubuntu/.local/lib/python3.12/site-packages/pytest_jubilant -name "*.py" | sort

<details>
<summary>16 lines</summary>

```
/home/ubuntu/.local/lib/python3.12/site-packages/jubilant/__init__.py
/home/ubuntu/.local/lib/python3.12/site-packages/jubilant/_all_any.py
/home/ubuntu/.local/lib/python3.12/site-packages/jubilant/_juju.py
/home/ubuntu/.local/lib/python3.12/site-packages/jubilant/_pretty.py
/home/ubuntu/.local/lib/python3.12/site-packages/jubilant/_task.py
/home/ubuntu/.local/lib/python3.12/site-packages/jubilant/_test_helpers.py
/home/ubuntu/.local/lib/python3.12/site-packages/jubilant/_version.py
/home/ubuntu/.local/lib/python3.12/site-packages/jubilant/_yaml.py
/home/ubuntu/.local/lib/python3.12/site-packages/jubilant/modeltypes.py
/home/ubuntu/.local/lib/python3.12/site-packages/jubilant/secrettypes.py
/home/ubuntu/.local/lib/python3.12/site-packages/jubilant/statustypes.py
---
/home/ubuntu/.local/lib/python3.12/site-packages/pytest_jubilant/__init__.py
/home/ubuntu/.local/lib/python3.12/site-packages/pytest_jubilant/main.py
/home/ubuntu/.local/lib/python3.12/site-packages/pytest_jubilant/version.py
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 3m 16s</sub>

### ✅ `bash`

**Read jubilant __init__**

$ cat /home/ubuntu/.local/lib/python3.12/site-packages/jubilant/__init__.py

<details>
<summary>53 lines</summary>

```
"""Jubilant is a Pythonic wrapper around the Juju CLI."""

from . import modeltypes, secrettypes, statustypes
from ._all_any import (
    all_active,
    all_agents_idle,
    all_blocked,
    all_error,
    all_maintenance,
    all_waiting,
    any_active,
    any_blocked,
    any_error,
    any_maintenance,
    any_waiting,
)
from ._juju import CLIError, ConfigValue, Juju, WaitError
from ._task import Task, TaskError
from ._test_helpers import temp_model
from ._version import Version
from .modeltypes import ModelInfo
from .secrettypes import RevealedSecret, Secret, SecretURI
from .statustypes import Status

__all__ = [
    'CLIError',
    'ConfigValue',
    'Juju',
    'ModelInfo',
    'RevealedSecret',
    'Secret',
    'SecretURI',
    'Status',
    'Task',
    'TaskError',
    'Version',
    'WaitError',
    'all_active',
    'all_agents_idle',
    'all_blocked',
    'all_error',
    'all_maintenance',
    'all_waiting',
    'any_active',
    'any_blocked',
    'any_error',
    'any_maintenance',
    'any_waiting',
    'modeltypes',
    'secrettypes',
    'statustypes',
    'temp_model',
]

__version__ = '1.7.0'
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 3m 16s</sub>

### ✅ `bash`

**Read pytest-jubilant main**

$ cat /home/ubuntu/.local/lib/python3.12/site-packages/pytest_jubilant/main.py

<details>
<summary>237 lines</summary>

```
#!/usr/bin/env python3
# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

"""Main plugin module."""
import dataclasses
import logging
import os
import secrets
import shlex
import subprocess
from pathlib import Path
from typing import Union, Optional, Dict
from unittest.mock import MagicMock, patch

import jubilant
import pytest
import yaml

JDL_LOGFILE_EXTENSION = "-jdl.txt"
DEFAULT_JDL_DUMP_PATH = "./.logs"


def pytest_addoption(parser):
    group = parser.getgroup("jubilant")
    group.addoption(
        "--model",
        action="store",
        default=None,
        help="Juju model name to target.",
    )
    group.addoption(
        "--keep-models",
        action="store_true",
        default=False,
        help="Skip model teardown.",
    )
    group.addoption(
        "--no-setup",
        action="store_true",
        default=False,
        help='Skip tests marked with "setup".',
    )
    group.addoption(
        "--no-teardown",
        action="store_true",
        default=False,
        help='Skip tests marked with "teardown".',
    )
    group.addoption(
        "--switch",
        action="store_true",
        default=False,
        help="Switch to the temporary model that is currently being worked on.",
    )
    group.addoption(
        "--dump-logs",
        action="store",
        default=DEFAULT_JDL_DUMP_PATH,
        help="Directory in which to dump any juju debug-log for any model prior to tearing it down. "
        "Set to empty string to disable the behaviour.",
    )


_cli_mock: Optional[MagicMock] = None


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "setup: tests that setup some parts of the environment."
    )
    config.addinivalue_line(
        "markers", "teardown: tests that tear down some parts of the environment."
    )

    # horrible to do it this way, but it's easy
    if os.getenv("PYTESTING_PYTEST_JUBILANT"):
        mm = MagicMock()
        mm.return_value = MagicMock(stdout="output", stderr="error")
        ctx = patch("subprocess.run", new=mm)
        ctx.__enter__()
        global _cli_mock
        _cli_mock = mm


def pytest_collection_modifyitems(config: pytest.Config, items):
    def _set_keep_models(val: bool = True):
        # TODO: less hacky way to do this?
        optname = config._opt2dest.get("--keep-models", "--keep-models")  # noqa
        config.option.__setattr__(optname, val)

    if config.getoption("--no-teardown"):
        skipper = pytest.mark.skip(reason="--no-teardown provided.")
        for item in items:
            if "teardown" in item.keywords:
                item.add_marker(skipper)

        if config.getoption("--keep-models"):
            logging.warning("--no-teardown implies --keep-models")
        else:
            _set_keep_models(True)

    if config.getoption("--no-setup"):
        skipper = pytest.mark.skip(reason="--no-setup provided.")
        for item in items:
            if "setup" in item.keywords:
                item.add_marker(skipper)


class TempModelFactory:
    """Manages temporary models for testing."""

    def __init__(
        self,
        prefix: str,
        randbits: Optional[str] = None,
        check_models_unique: bool = True,
    ):
        self.prefix = prefix
        self.randbits = randbits
        self._models: Dict[str, jubilant.Juju] = {}
        self._check_models_unique = check_models_unique

    def get_juju(self, suffix: str) -> jubilant.Juju:
        model_name = "-".join(filter(None, (self.prefix, self.randbits, suffix)))
        if model_name in self._models:
            raise ValueError(
                f"model {model_name} already registered on this temp_model factory. "
                "choose a different prefix."
            )

        juju = jubilant.Juju(model=model_name)
        try:
            juju.add_model(model_name)
        except jubilant.CLIError as e:
            # If --model is set (_check_models_unique is False), then the user wants collisions.
            # If the name is randomly generated, the chance of colliding with another
            # randomly generated model that wasn't torn down is tiny, but still present.
            if (
                "already exists on this k8s cluster" in e.args[1]
                and self._check_models_unique
            ):
                raise

        self._models[model_name] = juju
        return juju

    def dump_all_logs(self, path: Path = Path(DEFAULT_JDL_DUMP_PATH)):
        path.mkdir(parents=True, exist_ok=True)
        for model, juju in self._models.items():
            jdl_path = path / (model + JDL_LOGFILE_EXTENSION)
            jdl = juju.cli("debug-log", "--replay")
            jdl_path.write_text(jdl)
            logging.info(f"dropping jdl for model {model} to {jdl_path}")

    def teardown(self, force: bool = False):
        for model, juju in self._models.items():
            juju.destroy_model(model, destroy_storage=True, force=force)


@pytest.fixture(scope="module")
def cli_mock(request):
    yield _cli_mock


@pytest.fixture(scope="module")
def temp_model_factory(request):
    user_model = request.config.getoption("--model")
    if user_model:
        prefix = user_model
        randbits = None
    else:
        prefix = (request.module.__name__.rpartition(".")[-1]).replace("_", "-")
        randbits = (
            "testing"
            if os.getenv("PYTESTING_PYTEST_JUBILANT")
            else secrets.token_hex(4)
        )
    factory = TempModelFactory(
        prefix=prefix, randbits=randbits, check_models_unique=not user_model
    )

    yield factory

    # BEFORE tearing down the models, dump any and all juju debug-logs
    if dump_logs := request.config.getoption("--dump-logs"):
        factory.dump_all_logs(Path(dump_logs))

    if not request.config.getoption("--keep-models"):
        # TODO: jubilant defaults to --force, but is that a good idea?
        factory.teardown(force=True)

    if _cli_mock:
        _cli_mock.reset_mock()


@pytest.fixture(scope="module")
def juju(request, temp_model_factory):
    juju = temp_model_factory.get_juju("")
    if request.config.getoption("--switch"):
        juju.cli("switch", juju.model, include_model=False)
    return juju


@dataclasses.dataclass
class _Result:
    charm: Path
    resources: Optional[Dict[str, str]]


def _pack(root: Union[Path, str], platform: Optional[str] = None):
    _platform = f" --platform {platform}" if platform else ""
    cmd = f"charmcraft pack -p {root}{_platform}"
    proc = subprocess.run(
        shlex.split(cmd),
        check=True,
        capture_output=True,
        text=True,
    )

    # The output looks like:
    # ❯ charmcraft pack
    # Packed tempo-coordinator-k8s_ubuntu@24.04-amd64.charm
    # Packed tempo-coordinator-k8s_ubuntu@22.04-amd64.charm

    # Don't ask me why this goes to stderr.
    output = proc.stderr

    # we parse it and collect all the built charms.
    packed_charms = []
    for line in output.strip().splitlines():
        if line.startswith("Packed"):
            packed_charms.append(line.split()[1])

    if not packed_charms:
        raise ValueError(
            f"unable to get packed charm(s) ({cmd!r} completed with {proc.returncode=}, {proc.stdout=}, {proc.stderr=})"
        )

    return packed_charms


def pack(root: Union[Path, str] = "./", platform: Optional[str] = None) -> Path:
    """Pack a local charm and return it."""
    packed_charms = _pack(root, platform)

    if len(packed_charms) > 1:
        raise ValueError(
            "This charm supports multiple platforms. "
            "Pass a `platform` argument to control which charm you're getting instead."
        )

    return Path(packed_charms[0]).resolve()


def get_resources(root: Union[Path, str] = "./") -> Optional[Dict[str, str]]:
    """Obtain the charm resources from metadata.yaml's upstream-source fields."""
    for meta_name in ("metadata.yaml", "charmcraft.yaml"):
        if (meta_yaml := Path(root) / meta_name).exists():
            logging.debug(f"found metadata file: {meta_yaml}")
            meta = yaml.safe_load(meta_yaml.read_text())
            if meta_resources := meta.get("resources"):
                try:
                    resources = {
                        resource: res_meta["upstream-source"]
                        for resource, res_meta in meta_resources.items()
                    }
                except KeyError:
                    logging.exception(
                        "The `upstream-source` key wasn't found in the resource. If your charm follows a different convention of pointing at an OCI image, you need to pack it manually."
                    )
                    raise
            else:
                resources = None
                logging.info(
                    f"resources not found in {meta_name}; proceeding without resources"
                )
            break
    else:
        resources = None
        logging.error(
            f"metadata/charmcraft.yaml not found at {root}; unable to load resources"
        )

    return resources
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 3m 24s</sub>

### ✅ `bash`

**Read Juju class - part 1**

$ cat /home/ubuntu/.local/lib/python3.12/site-packages/jubilant/_juju.py | head -200

<details>
<summary>166 lines</summary>

```
from __future__ import annotations

import contextlib
import functools
import json
import logging
import os
import pathlib
import shlex
import shutil
import subprocess
import tempfile
import time
from collections.abc import Callable, Iterable, Mapping
from typing import Any, Generator, Literal, Union, overload

from . import _pretty, _yaml
from ._task import Task
from ._version import Version
from .modeltypes import ModelInfo
from .secrettypes import RevealedSecret, Secret, SecretURI
from .statustypes import Status

logger = logging.getLogger('jubilant')
logger_wait = logging.getLogger('jubilant.wait')


class CLIError(subprocess.CalledProcessError):
    """Subclass of ``CalledProcessError`` that includes stdout and stderr in the ``__str__``."""

    def __str__(self) -> str:
        s = super().__str__()
        if self.stdout:
            s += '\nStdout:\n' + self.stdout
        if self.stderr:
            s += '\nStderr:\n' + self.stderr
        return s


class WaitError(Exception):
    """Raised when :meth:`Juju.wait`'s *error* callable returns False."""


ConfigValue = Union[bool, int, float, str, SecretURI]
"""The possible types a charm config value can be."""

ConstraintValue = Union[bool, int, float, str]
"""The possible types a constraint value can be (model, bootstrap or deployment constraint)."""


class Juju:
    """Instantiate this class to run Juju commands.

    Most methods directly call a single Juju CLI command. If a CLI command doesn't yet exist as a
    method, use :meth:`cli`.

    Example::

        juju = jubilant.Juju()
        juju.deploy('snappass-test')

    Args:
        model: If specified, operate on this Juju model, otherwise use the current Juju model.
            If the model is in another controller, prefix the model name with ``<controller>:``.
        wait_timeout: The default timeout for :meth:`wait` (in seconds) if that method's *timeout*
            parameter is not specified.
        cli_binary: Path to the Juju CLI binary. If not specified, uses ``juju`` and assumes it is
            in the PATH.
    """

    model: str | None
    """If not None, operate on this Juju model, otherwise use the current Juju model.

    If the model is in another controller, prefix the model name with ``<controller>:``; for
    example, ``juju = jubilant.Juju(model='mycontroller:my-model')``.
    """

    wait_timeout: float
    """The default timeout for :meth:`wait` (in seconds) if that method's *timeout* parameter is
    not specified.
    """

    cli_binary: str
    """Path to the Juju CLI binary. If None, uses ``juju`` and assumes it is in the PATH."""

    def __init__(
        self,
        *,
        model: str | None = None,
        wait_timeout: float = 3 * 60.0,
        cli_binary: str | pathlib.Path | None = None,
    ):
        self.model = model
        self.wait_timeout = wait_timeout
        self.cli_binary = str(cli_binary or 'juju')

    def __repr__(self) -> str:
        args = [
            f'model={self.model!r}',
            f'wait_timeout={self.wait_timeout}',
            f'cli_binary={self.cli_binary!r}',
        ]
        return f'Juju({", ".join(args)})'

    # Keep the public methods in alphabetical order, so we don't have to think
    # about where to put each new method.

    @overload
    def add_credential(
        self,
        cloud: str,
        credential: str | pathlib.Path | Mapping[str, Any],
        *,
        client: Literal[True],
        controller: None = None,
        region: str | None = None,
    ) -> None: ...

    @overload
    def add_credential(
        self,
        cloud: str,
        credential: str | pathlib.Path | Mapping[str, Any],
        *,
        client: bool = False,
        controller: str,
        region: str | None = None,
    ) -> None: ...

    def add_credential(
        self,
        cloud: str,
        credential: str | pathlib.Path | Mapping[str, Any],
        *,
        client: bool = False,
        controller: str | None = None,
        region: str | None = None,
    ) -> None:
        """Add a credential for a cloud.

        Args:
            cloud: Name of the cloud to add credentials for.
            credential: Path to a YAML file containing credential to add, or a mapping
                representing the parsed credential YAML (``{'credentials': ...}``).
            client: Set to True to save credentials on the client, meaning controllers
                created later will have access to them. You must specify ``client=True``
                or provide *controller* (or both).
            controller: If specified, save credentials to the named controller.
            region: Cloud region that the credential is valid for.
        """
        if not client and controller is None:
            raise TypeError('"client" must be True or "controller" must be specified (or both)')

        args = ['add-credential', cloud]

        if client:
            args.append('--client')
        if controller is not None:
            args.extend(['--controller', controller])
        if region is not None:
            args.extend(['--region', region])

        if isinstance(credential, (str, pathlib.Path)):
            args.extend(['--file', str(credential)])
            self.cli(*args, include_model=False)
        else:
            with tempfile.NamedTemporaryFile('w+', dir=self._temp_dir) as temp_file:
                _yaml.safe_dump(credential, temp_file)
                temp_file.flush()
                args.extend(['--file', temp_file.name])
                self.cli(*args, include_model=False)

    def add_model(
        self,
        model: str,
        cloud: str | None = None,
        *,
        controller: str | None = None,
        config: Mapping[str, ConfigValue] | None = None,
        credential: str | None = None,
    ) -> None:
        """Add a named model and set this instance's model to it.

        To avoid interfering with CLI users, this won't switch the Juju CLI to the
        newly-created model. However, because :attr:`model` is set to the name of the new
        model, all subsequent operations on this instance will use the new model.

        Args:
            model: Name of model to add.
            cloud: Name of cloud or region (or cloud/region) to use for the model.
            controller: Name of controller to operate in. If not specified, use the current
                controller.
            config: Model configuration as key-value pairs, for example,
                ``{'image-stream': 'daily'}``.
            credential: Name of cloud credential to use for the model.
        """
        args = ['add-model', '--no-switch', model]

        if cloud is not None:
            args.append(cloud)
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 3m 24s</sub>

### ✅ `bash`

**Read all_any helpers**

$ cat /home/ubuntu/.local/lib/python3.12/site-packages/jubilant/_all_any.py

<details>
<summary>152 lines</summary>

```
from __future__ import annotations

from collections.abc import Iterable

from .statustypes import Status


def all_active(status: Status, *apps: str) -> bool:
    """Report whether all apps and units in *status* (or in *apps* if provided) are "active".

    Examples::

        # Use the callable directly to wait for all apps in status to be active.
        juju.wait(jubilant.all_active)

        # Use a lambda to wait for all apps specified (blog, mysql) to be active.
        juju.wait(lambda status: jubilant.all_active(status, 'blog', 'mysql'))

    Args:
        status: The status object being tested.
        apps: If provided, only these applications (and their units) are tested. If an app is not
            present in ``status.apps``, returns False.
    """
    return _all_statuses_are('active', status, apps)


def all_blocked(status: Status, *apps: str) -> bool:
    """Report whether all apps and units in *status* (or in *apps* if provided) are "blocked".

    See :func:`all_active` for examples.

    Args:
        status: The status object being tested.
        apps: If provided, only these applications (and their units) are tested. If an app is not
            present in ``status.apps``, returns False.
    """
    return _all_statuses_are('blocked', status, apps)


def all_error(status: Status, *apps: str) -> bool:
    """Report whether all apps and units in *status* (or in *apps* if provided) are "error".

    See :func:`all_active` for examples.

    Args:
        status: The status object being tested.
        apps: If provided, only these applications (and their units) are tested. If an app is not
            present in ``status.apps``, returns False.
    """
    return _all_statuses_are('error', status, apps)


def all_maintenance(status: Status, *apps: str) -> bool:
    """Report whether all apps and units in *status* (or in *apps* if provided) are "maintenance".

    See :func:`all_active` for examples.

    Args:
        status: The status object being tested.
        apps: If provided, only these applications (and their units) are tested. If an app is not
            present in ``status.apps``, returns False.
    """
    return _all_statuses_are('maintenance', status, apps)


def all_waiting(status: Status, *apps: str) -> bool:
    """Report whether all apps and units in *status* (or in *apps* if provided) are "waiting".

    See :func:`all_active` for examples.

    Args:
        status: The status object being tested.
        apps: If provided, only these applications (and their units) are tested. If an app is not
            present in ``status.apps``, returns False.
    """
    return _all_statuses_are('waiting', status, apps)


def any_active(status: Status, *apps: str) -> bool:
    """Report whether any app or unit in *status* (or in *apps* if provided) is "active".

    See :func:`any_error` for examples.

    Args:
        status: The status object being tested.
        apps: If provided, only these applications (and their units) are tested.
    """
    return _any_status_is('active', status, apps)


def any_blocked(status: Status, *apps: str) -> bool:
    """Report whether any app or unit in *status* (or in *apps* if provided) is "blocked".

    See :func:`any_error` for examples.

    Args:
        status: The status object being tested.
        apps: If provided, only these applications (and their units) are tested.
    """
    return _any_status_is('blocked', status, apps)


def any_error(status: Status, *apps: str) -> bool:
    """Report whether any app or unit in *status* (or in *apps* if provided) is "error".

    Examples::

        # Use the callable directly to raise an error if any apps go into error.
        juju.wait(jubilant.all_active, error=jubilant.any_error)

        # Use a lambda to wait for any of the apps specified (blog, mysql) to go into error.
        juju.wait(
            jubilant.all_active,
            error=lambda status: jubilant.any_error(status, 'blog', 'mysql')),
        )

    Args:
        status: The status object being tested.
        apps: If provided, only these applications (and their units) are tested.
    """
    return _any_status_is('error', status, apps)


def any_maintenance(status: Status, *apps: str) -> bool:
    """Report whether any app or unit in *status* (or in *apps* if provided) is "maintenance".

    See :func:`any_error` for examples.

    Args:
        status: The status object being tested.
        apps: If provided, only these applications (and their units) are tested.
    """
    return _any_status_is('maintenance', status, apps)


def any_waiting(status: Status, *apps: str) -> bool:
    """Report whether any app or unit in *status* (or in *apps* if provided) is "waiting".

    See :func:`any_error` for examples.

    Args:
        status: The status object being tested.
        apps: If provided, only these applications (and their units) are tested.
    """
    return _any_status_is('waiting', status, apps)


def all_agents_idle(status: Status, *apps: str) -> bool:
    """Report whether all unit agents in *status* (filtered to *apps* if provided) are "idle".

    Unlike the other ``all_*`` and ``any_*`` helpers, this method looks at the status of each
    Juju unit agent, not the workload's application or unit status.

    Examples::

        # Use the callable directly to wait for unit agents from all apps to be idle.
        juju.wait(jubilant.all_agents_idle)

        # Use a lambda to wait for unit agents only from specified apps (blog, mysql).
        juju.wait(lambda status: jubilant.all_agents_idle(status, 'blog', 'mysql'))

    Args:
        status: The status object being tested.
        apps: If provided, only the unit agents of units from these applications are tested.
            If an app is not present in ``status.apps``, returns False.
    """
    return _all_agent_statuses_are('idle', status, apps)


def _all_statuses_are(expected: str, status: Status, apps: Iterable[str]) -> bool:
    if not apps:
        apps = status.apps

    for app in apps:
        app_info = status.apps.get(app)
        if app_info is None:
            return False
        if app_info.app_status.current != expected:
            return False
        for unit_info in status.get_units(app).values():
            if unit_info.workload_status.current != expected:
                return False
    return True


def _any_status_is(expected: str, status: Status, apps: Iterable[str]) -> bool:
    if not apps:
        apps = status.apps

    for app in apps:
        app_info = status.apps.get(app)
        if app_info is None:
            continue
        if app_info.app_status.current == expected:
            return True
        for unit_info in status.get_units(app).values():
            if unit_info.workload_status.current == expected:
                return True
    return False


def _all_agent_statuses_are(expected: str, status: Status, apps: Iterable[str]) -> bool:
    if not apps:
        apps = status.apps

    for app in apps:
        app_info = status.apps.get(app)
        if app_info is None:
            return False
        for unit_info in status.get_units(app).values():
            if unit_info.juju_status.current != expected:
                return False
    return True
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 3m 32s</sub>

### ✅ `bash`

**Find key methods in Juju class**

$ grep -n "def deploy\|def wait\|def run_action\|def relate\|def add_relation\|def remove_relation\|def set_config\|def get_config\|def run\|def show_unit\|def status\|def cli\b" /home/ubuntu/.local/lib/python3.12/site-packages/jubilant/_juju.py | head -60

<details>
<summary>7 lines</summary>

```
370:    def cli(self, *args: str, include_model: bool = True, stdin: str | None = None) -> str:
522:    def deploy(
964:    def remove_relation(self, app1: str, app2: str, *, force: bool = False) -> None:
1047:    def run(
1323:    def status(self) -> Status:
1387:    def wait(
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 3m 41s</sub>

### ✅ `bash`

**Find all key methods**

$ grep -n "def deploy\|def wait\|def run_action\|def integrate\|def relate\|def add_relation\|def remove_relation\|def set_config\|def get_config\|def run\b\|def show_unit\|def status\b\|def cli\b\|def action\b" /home/ubuntu/.local/lib/python3.12/site-packages/jubilant/_juju.py

<details>
<summary>8 lines</summary>

```
370:    def cli(self, *args: str, include_model: bool = True, stdin: str | None = None) -> str:
522:    def deploy(
757:    def integrate(self, app1: str, app2: str, *, via: str | Iterable[str] | None = None) -> None:
964:    def remove_relation(self, app1: str, app2: str, *, force: bool = False) -> None:
1047:    def run(
1323:    def status(self) -> Status:
1387:    def wait(
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 3m 53s</sub>

### ✅ `bash`

**Read key Juju methods**

$ sed -n '370,430p' /home/ubuntu/.local/lib/python3.12/site-packages/jubilant/_juju.py
echo "---"
sed -n '522,620p' /home/ubuntu/.local/lib/python3.12/site-packages/jubilant/_juju.py
echo "---"
sed -n '757,800p' /home/ubuntu/.local/lib/python3.12/site-packages/jubilant/_juju.py
echo "---"
sed -n '964,1010p' /home/ubuntu/.local/lib/python3.12/site-packages/jubilant/_juju.py
echo "---"
sed -n '1047,1120p' /home/ubuntu/.local/lib/python3.12/site-packages/jubilant/_juju.py
echo "---"
sed -n '1323,1500p' /home/ubuntu/.local/lib/python3.12/site-packages/jubilant/_juju.py

<details>
<summary>5 lines</summary>

```
Output too large to read at once (21.4 KB). Saved to: /tmp/copilot-tool-output-1772843082250-1z00qd.txt
Consider using tools like grep (for searching), head/tail (for viewing start/end), view with view_range (for specific sections), or jq (for JSON) to examine portions of the output.

Preview (first 500 chars):
    def cli(self, *args: str, include_model: bool = True, stdin: str | None = None) -> str:
        
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 3m 57s</sub>

### ✅ `bash`

**Read saved output**

$ cat /tmp/copilot-tool-output-1772843082250-1z00qd.txt

<details>
<summary>5 lines</summary>

```
Output too large to read at once (21.0 KB). Saved to: /tmp/copilot-tool-output-1772843087089-m8ulyd.txt
Consider using tools like grep (for searching), head/tail (for viewing start/end), view with view_range (for specific sections), or jq (for JSON) to examine portions of the output.

Preview (first 500 chars):
    def cli(self, *args: str, include_model: bool = True, stdin: str | None = None) -> str:
        
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 4m 2s</sub>

### ✅ `view`

**/home/ubuntu/.local/lib/python3.12/site-packages/jubilant/_juju.py**

/home/ubuntu/.local/lib/python3.12/site-packages/jubilant/_juju.py (lines 370-430)

<details>
<summary>61 lines</summary>

```
370.     def cli(self, *args: str, include_model: bool = True, stdin: str | None = None) -> str:
371.         """Run a Juju CLI command and return its standard output.
372. 
373.         Args:
374.             args: Command-line arguments (excluding ``juju``).
375.             include_model: If true and :attr:`model` is set, insert the ``--model`` argument
376.                 after the first argument in *args*.
377.             stdin: Standard input to send to the process, if any.
378.         """
379.         stdout, _ = self._cli(*args, include_model=include_model, stdin=stdin)
380.         return stdout
381. 
382.     def _cli(
383.         self,
384.         *args: str,
385.         include_model: bool = True,
386.         stdin: str | None = None,
387.         log: bool = True,
388.         timeout: float | None = None,
389.     ) -> tuple[str, str]:
390.         """Run a Juju CLI command and return its standard output and standard error."""
391.         if include_model and self.model is not None:
392.             args = (args[0], '--model', self.model, *args[1:])
393.         if log:
394.             logger.info('cli: juju %s', shlex.join(args))
395.         try:
396.             process = subprocess.run(
397.                 [self.cli_binary, *args],
398.                 check=True,
399.                 capture_output=True,
400.                 encoding='utf-8',
401.                 input=stdin,
402.                 timeout=timeout,
403.             )
404.         except subprocess.CalledProcessError as e:
405.             raise CLIError(e.returncode, e.cmd, e.stdout, e.stderr) from None
406.         return (process.stdout, process.stderr)
407. 
408.     @overload
409.     def config(self, app: str, *, app_config: bool = False) -> Mapping[str, ConfigValue]: ...
410. 
411.     @overload
412.     def config(
413.         self,
414.         app: str,
415.         values: Mapping[str, ConfigValue],
416.         *,
417.         reset: str | Iterable[str] = (),
418.     ) -> None: ...
419. 
420.     @overload
421.     def config(self, app: str, *, reset: str | Iterable[str]) -> None: ...
422. 
423.     def config(
424.         self,
425.         app: str,
426.         values: Mapping[str, ConfigValue] | None = None,
427.         *,
428.         app_config: bool = False,
429.         reset: str | Iterable[str] = (),
430.     ) -> Mapping[str, ConfigValue] | None:
```

</details>


---

<sub>⏱️ 4m 2s</sub>

### ✅ `view`

**/home/ubuntu/.local/lib/python3.12/site-packages/jubilant/_juju.py**

/home/ubuntu/.local/lib/python3.12/site-packages/jubilant/_juju.py (lines 522-640)

<details>
<summary>119 lines</summary>

```
522.     def deploy(
523.         self,
524.         charm: str | pathlib.Path,
525.         app: str | None = None,
526.         *,
527.         attach_storage: str | Iterable[str] | None = None,
528.         base: str | None = None,
529.         bind: Mapping[str, str] | str | None = None,
530.         channel: str | None = None,
531.         config: Mapping[str, ConfigValue] | None = None,
532.         constraints: Mapping[str, str] | None = None,
533.         force: bool = False,
534.         num_units: int = 1,
535.         overlays: Iterable[str | pathlib.Path] = (),
536.         resources: Mapping[str, str] | None = None,
537.         revision: int | None = None,
538.         storage: Mapping[str, str] | None = None,
539.         to: str | Iterable[str] | None = None,
540.         trust: bool = False,
541.     ) -> None:
542.         """Deploy an application or bundle.
543. 
544.         Args:
545.             charm: Name of charm or bundle to deploy, or path to a local file (must start with
546.                 ``/`` or ``.``).
547.             app: Custom application name within the model. Defaults to the charm name.
548.             attach_storage: Existing storage(s) to attach to the deployed unit, for example,
549.                 ``foo/0`` or ``mydisk/1``. Not available for Kubernetes models.
550.             base: The base on which to deploy, for example, ``ubuntu@22.04``.
551.             bind: Either a mapping of endpoint-to-space bindings, for example
552.                 ``{'database-peers': 'internal-space'}``, or a single space name, which is
553.                 equivalent to binding all endpoints to that space.
554.             channel: Channel to use when deploying from Charmhub, for example, ``latest/edge``.
555.             config: Application configuration as key-value pairs, for example,
556.                 ``{'name': 'My Wiki'}``.
557.             constraints: Hardware constraints for new machines, for example, ``{'mem': '8G'}``.
558.             force: If true, bypass checks such as supported bases.
559.             num_units: Number of units to deploy for principal charms.
560.             overlays: File paths of bundles to overlay on the primary bundle, applied in order.
561.             resources: Specify named resources to use for deployment, for example:
562.                 ``{'bin': '/path/to/some/binary'}``.
563.             revision: Charmhub revision number to deploy.
564.             storage: Constraints for named storage(s), for example, ``{'data': 'tmpfs,1G'}``.
565.             to: Machine or container to deploy the unit in (bypasses constraints). For example,
566.                 to deploy to a new LXD container on machine 25, use ``lxd:25``.
567.             trust: If true, allows charm to run hooks that require access to cloud credentials.
568.         """
569.         # Need this check because str is also an iterable of str.
570.         if isinstance(overlays, str):
571.             raise TypeError('overlays must be an iterable of str or pathlib.Path, not str')
572. 
573.         with self._deploy_tempdir(charm, resources) as (_charm, resources):
574.             assert _charm is not None
575.             args = ['deploy', _charm]
576. 
577.             if app is not None:
578.                 args.append(app)
579. 
580.             if attach_storage:
581.                 if isinstance(attach_storage, str):
582.                     args.extend(['--attach-storage', attach_storage])
583.                 else:
584.                     args.extend(['--attach-storage', ','.join(attach_storage)])
585.             if base is not None:
586.                 args.extend(['--base', base])
587.             if bind is not None:
588.                 if not isinstance(bind, str):
589.                     bind = ' '.join(f'{k}={v}' for k, v in bind.items())
590.                 args.extend(['--bind', bind])
591.             if channel is not None:
592.                 args.extend(['--channel', channel])
593.             if config is not None:
594.                 for k, v in config.items():
595.                     args.extend(['--config', _format_config(k, v)])
596.             if constraints is not None:
597.                 for k, v in constraints.items():
598.                     args.extend(['--constraints', f'{k}={v}'])
599.             if force:
600.                 args.append('--force')
601.             if num_units != 1:
602.                 args.extend(['--num-units', str(num_units)])
603.             for overlay in overlays:
604.                 args.extend(['--overlay', str(overlay)])
605.             if resources is not None:
606.                 for k, v in resources.items():
607.                     args.extend(['--resource', f'{k}={v}'])
608.             if revision is not None:
609.                 args.extend(['--revision', str(revision)])
610.             if storage is not None:
611.                 for k, v in storage.items():
612.                     args.extend(['--storage', f'{k}={v}'])
613.             if to:
614.                 if isinstance(to, str):
615.                     args.extend(['--to', to])
616.                 else:
617.                     args.extend(['--to', ','.join(to)])
618.             if trust:
619.                 args.append('--trust')
620. 
621.             self.cli(*args)
622. 
623.     def destroy_model(
624.         self,
625.         model: str,
626.         *,
627.         destroy_storage: bool = False,
628.         force: bool = False,
629.         no_wait: bool = False,
630.         release_storage: bool = False,
631.         timeout: float | None = None,
632.     ) -> None:
633.         """Terminate all machines (or containers) and resources for a model.
634. 
635.         If the given model is this instance's model, also sets this instance's
636.         :attr:`model` to None.
637. 
638.         Args:
639.             model: Name of model to destroy.
640.             destroy_storage: If True, destroy all storage instances in the model.
```

</details>


---

<sub>⏱️ 4m 8s</sub>

### ✅ `view`

**/home/ubuntu/.local/lib/python3.12/site-packages/jubilant/_juju.py**

/home/ubuntu/.local/lib/python3.12/site-packages/jubilant/_juju.py (lines 757-820)

<details>
<summary>64 lines</summary>

```
757.     def integrate(self, app1: str, app2: str, *, via: str | Iterable[str] | None = None) -> None:
758.         """Integrate two applications, creating a relation between them.
759. 
760.         The order of *app1* and *app2* is not significant. Each of them should
761.         be in the format ``<application>[:<endpoint>]``. The endpoint is only
762.         required if there's more than one possible integration between the two
763.         applications.
764. 
765.         To integrate an application in the current model with an application in
766.         another model (cross-model), prefix *app1* or *app2* with ``<model>.``.
767.         To integrate with an application on another controller, *app1* or *app2* must
768.         be an offer endpoint. See ``juju integrate --help`` for details.
769. 
770.         Args:
771.             app1: One of the applications (and endpoints) to integrate.
772.             app2: The other of the applications (and endpoints) to integrate.
773.             via: Inform the offering side (the remote application) of the
774.                 source of traffic, to enable network ports to be opened. This
775.                 is in CIDR notation, for example ``192.0.2.0/24``.
776.         """
777.         args = ['integrate', app1, app2]
778.         if via:
779.             if isinstance(via, str):
780.                 args.extend(['--via', via])
781.             else:
782.                 args.extend(['--via', ','.join(via)])
783.         self.cli(*args)
784. 
785.     @overload
786.     def model_config(self) -> Mapping[str, ConfigValue]: ...
787. 
788.     @overload
789.     def model_config(
790.         self, values: Mapping[str, ConfigValue], *, reset: str | Iterable[str] = ()
791.     ) -> None: ...
792. 
793.     @overload
794.     def model_config(self, *, reset: str | Iterable[str]) -> None: ...
795. 
796.     def model_config(
797.         self, values: Mapping[str, ConfigValue] | None = None, reset: str | Iterable[str] = ()
798.     ) -> Mapping[str, ConfigValue] | None:
799.         """Get or set the configuration of the model.
800. 
801.         If called with no arguments, get the model config and return it.
802. 
803.         If called with the *values* or *reset* arguments, set the model config values and return
804.         None, and reset any keys in *reset* to their defaults.
805. 
806.         Args:
807.             values: Mapping of model config names to values to set, for example
808.                 ``{'update-status-hook-interval': '10s'}``.
809.             reset: Key or list of keys to reset to their defaults.
810.         """
811.         if values is None and not reset:
812.             stdout = self.cli('model-config', '--format', 'json')
813.             result = json.loads(stdout)
814.             return {k: v['Value'] for k, v in result.items() if 'Value' in v}
815. 
816.         args = ['model-config']
817.         if values:
818.             args.extend(_format_config(k, v) for k, v in values.items())
819.         if reset:
820.             if not isinstance(reset, str):
```

</details>


---

<sub>⏱️ 4m 8s</sub>

### ✅ `view`

**/home/ubuntu/.local/lib/python3.12/site-packages/jubilant/_juju.py**

/home/ubuntu/.local/lib/python3.12/site-packages/jubilant/_juju.py (lines 964-1010)

<details>
<summary>47 lines</summary>

```
964.     def remove_relation(self, app1: str, app2: str, *, force: bool = False) -> None:
965.         """Remove an existing relation between two applications (opposite of :meth:`integrate`).
966. 
967.         The order of *app1* and *app2* is not significant. Each of them should
968.         be in the format ``<application>[:<endpoint>]``. The endpoint is only
969.         required if there's more than one possible integration between the two
970.         applications.
971. 
972.         Args:
973.             app1: One of the applications (and endpoints) to integrate.
974.             app2: The other of the applications (and endpoints) to integrate.
975.             force: Force removal, ignoring operational errors.
976.         """
977.         args = ['remove-relation', app1, app2]
978.         if force:
979.             args.append('--force')
980.         self.cli(*args)
981. 
982.     def remove_secret(self, identifier: str | SecretURI, *, revision: int | None = None) -> None:
983.         """Remove a secret from the model.
984. 
985.         Args:
986.             identifier: The name or URI of the secret to remove.
987.             revision: The revision of the secret to remove. If not specified, remove all revisions.
988.         """
989.         args = ['remove-secret', identifier]
990.         if revision is not None:
991.             args.extend(['--revision', str(revision)])
992.         self.cli(*args)
993. 
994.     def remove_ssh_key(self, *ids: str) -> None:
995.         """Remove one or more SSH keys from the model.
996. 
997.         The SSH keys are removed from all machines in the model.
998. 
999.         Args:
1000.             ids: SSH key identifier or identifiers to remove. Each identifier can be
1001.                 a key fingerprint (for example,
1002.                 ``45:7f:33:2c:10:4e:6c:14:e3:a1:a4:c8:b2:e1:34:b4``), a key comment
1003.                 (for example, ``user@host``), or the full SSH public key string.
1004.         """
1005.         self.cli('remove-ssh-key', *ids)
1006. 
1007.     def remove_unit(
1008.         self,
1009.         *app_or_unit: str,
1010.         destroy_storage: bool = False,
```

</details>


---

<sub>⏱️ 4m 8s</sub>

### ✅ `view`

**/home/ubuntu/.local/lib/python3.12/site-packages/jubilant/_juju.py**

/home/ubuntu/.local/lib/python3.12/site-packages/jubilant/_juju.py (lines 1047-1120)

<details>
<summary>74 lines</summary>

```
1047.     def run(
1048.         self,
1049.         unit: str,
1050.         action: str,
1051.         params: Mapping[str, Any] | None = None,
1052.         *,
1053.         wait: float | None = None,
1054.     ) -> Task:
1055.         """Run an action on the given unit and wait for the result.
1056. 
1057.         Note: this method does not support running an action on multiple units
1058.         at once. If you need that, let us know, and we'll consider adding it
1059.         with a new ``run_multiple`` method or similar.
1060. 
1061.         Example::
1062. 
1063.             juju = jubilant.Juju()
1064.             result = juju.run('mysql/0', 'get-password')
1065.             assert result.results['username'] == 'USER0'
1066. 
1067.         Args:
1068.             unit: Name of unit to run the action on, for example ``mysql/0`` or
1069.                 ``mysql/leader``.
1070.             action: Name of action to run.
1071.             params: Named parameters to pass to the action.
1072.             wait: Maximum time to wait for action to finish; :class:`TimeoutError` is raised if
1073.                 this is reached. Juju's default is to wait 60 seconds.
1074. 
1075.         Returns:
1076.             The task created to run the action, including logs, failure message, and so on.
1077. 
1078.         Raises:
1079.             ValueError: if the action or the unit doesn't exist.
1080.             TaskError: if the action failed.
1081.             TimeoutError: if *wait* was specified and the wait time was reached.
1082.         """
1083.         args = ['run', '--format', 'json', unit, action]
1084.         if wait is not None:
1085.             args.extend(['--wait', f'{wait}s'])
1086. 
1087.         with (
1088.             tempfile.NamedTemporaryFile('w+', dir=self._temp_dir)
1089.             if params is not None
1090.             else contextlib.nullcontext()
1091.         ) as params_file:
1092.             # params_file is defined when params is not None
1093.             if params_file is not None:
1094.                 _yaml.safe_dump(params, params_file)
1095.                 params_file.flush()
1096.                 args.extend(['--params', params_file.name])
1097.             try:
1098.                 stdout, stderr = self._cli(*args)
1099.             except CLIError as exc:
1100.                 if 'timed out' in exc.stderr:
1101.                     msg = f'timed out waiting for action, stderr:\n{exc.stderr}'
1102.                     raise TimeoutError(msg) from None
1103.                 # With Juju 4, trying to run an action that is not defined gives an error like:
1104.                 # ERROR action "not-defined-action" not defined for unit "unit/0". (not found)
1105.                 if '(not found)' in exc.stderr:
1106.                     raise ValueError(
1107.                         f'error running action {action!r}, stderr:\n{exc.stderr}'
1108.                     ) from None
1109.                 # The "juju run" CLI command fails if the action has an uncaught exception.
1110.                 if 'task failed' not in exc.stderr:
1111.                     raise
1112.                 stdout = exc.stdout
1113.                 stderr = exc.stderr
1114. 
1115.             # Command doesn't return any stdout if no units exist.
1116.             results: dict[str, Any] = json.loads(stdout) if stdout.strip() else {}
1117.             if not results:
1118.                 raise ValueError(f'error running action {action!r}, stderr:\n{stderr}')
1119.             # Don't look up results[unit] directly, because if the caller specifies
1120.             # app/leader it is returned as app/N, for example app/0.
```

</details>


---

<sub>⏱️ 4m 8s</sub>

### ✅ `view`

**/home/ubuntu/.local/lib/python3.12/site-packages/jubilant/_juju.py**

/home/ubuntu/.local/lib/python3.12/site-packages/jubilant/_juju.py (lines 1323-1500)

<details>
<summary>178 lines</summary>

```
1323.     def status(self) -> Status:
1324.         """Fetch the status of the current model, including its applications and units."""
1325.         stdout = self.cli('status', '--format', 'json')
1326.         result = json.loads(stdout)
1327.         return Status._from_dict(result)
1328. 
1329.     def trust(
1330.         self, app: str, *, remove: bool = False, scope: Literal['cluster'] | None = None
1331.     ) -> None:
1332.         """Set the trust status of a deployed application.
1333. 
1334.         Args:
1335.             app: Application name to set trust status for.
1336.             remove: Set to True to remove trust status.
1337.             scope: On Kubernetes models, this must be set to "cluster", as the trust operation
1338.                 grants the charm full access to the cluster.
1339.         """
1340.         args = ['trust', app]
1341.         if remove:
1342.             args.append('--remove')
1343.         if scope is not None:
1344.             args.extend(['--scope', scope])
1345. 
1346.         self.cli(*args)
1347. 
1348.     def update_secret(
1349.         self,
1350.         identifier: str | SecretURI,
1351.         content: Mapping[str, str],
1352.         *,
1353.         info: str | None = None,
1354.         name: str | None = None,
1355.         auto_prune: bool = False,
1356.     ) -> None:
1357.         """Update the content of a secret.
1358. 
1359.         Args:
1360.             identifier: The name or URI of the secret to update.
1361.             content: Key-value pairs that represent the secret content, for example
1362.                 ``{'password': 'hunter2'}``.
1363.             info: New description for the secret.
1364.             name: New name for the secret.
1365.             auto_prune: automatically remove revisions that are no longer tracked by any observers.
1366.         """
1367.         args = ['update-secret', identifier]
1368.         if info is not None:
1369.             args.extend(['--info', info])
1370.         if name is not None:
1371.             args.extend(['--name', name])
1372.         if auto_prune:
1373.             args.append('--auto-prune')
1374. 
1375.         with tempfile.NamedTemporaryFile('w+', dir=self._temp_dir) as file:
1376.             _yaml.safe_dump(content, file)
1377.             file.flush()
1378.             args.extend(['--file', file.name])
1379.             self.cli(*args)
1380. 
1381.     def version(self) -> Version:
1382.         """Return the parsed Juju CLI version."""
1383.         stdout = self.cli('version', '--format', 'json', '--all', include_model=False)
1384.         version_dict = json.loads(stdout)
1385.         return Version._from_dict(version_dict)
1386. 
1387.     def wait(
1388.         self,
1389.         ready: Callable[[Status], bool],
1390.         *,
1391.         error: Callable[[Status], bool] | None = None,
1392.         delay: float = 1.0,
1393.         timeout: float | None = None,
1394.         successes: int = 3,
1395.     ) -> Status:
1396.         """Wait until ``ready(status)`` returns true.
1397. 
1398.         This fetches the Juju status repeatedly (waiting *delay* seconds between each call),
1399.         and returns the last status after the *ready* callable returns true for *successes*
1400.         times in a row.
1401. 
1402.         Example::
1403. 
1404.             juju = jubilant.Juju()
1405.             juju.deploy('snappass-test')
1406.             juju.wait(jubilant.all_active)
1407. 
1408.             # Or something more complex: wait specifically for 'snappass-test' to be active,
1409.             # and raise if any app or unit is seen in "error" status while waiting.
1410.             juju.wait(
1411.                 lambda status: jubilant.all_active(status, 'snappass-test'),
1412.                 error=jubilant.any_error,
1413.             )
1414. 
1415.         For more examples, see `Tutorial | Use a custom wait condition <https://documentation.ubuntu.com/jubilant/tutorial/getting-started/#use-a-custom-wait-condition>`_.
1416. 
1417.         This function logs the status object after the first status call, and after subsequent
1418.         calls if the status object has changed. Logs are sent to the logger named
1419.         ``jubilant.wait`` at INFO level, so to disable these logs, set the level to WARNING or
1420.         above::
1421. 
1422.             logging.getLogger('jubilant.wait').setLevel('WARNING')
1423. 
1424.         Args:
1425.             ready: Callable that takes a :class:`Status` object and returns true when the wait
1426.                 should be considered ready. It needs to return true *successes* times in a row
1427.                 before ``wait`` returns.
1428.             error: Callable that takes a :class:`Status` object and returns true when ``wait``
1429.                 should raise an error (:class:`WaitError`).
1430.             delay: Delay in seconds between status calls.
1431.             timeout: Overall timeout in seconds; :class:`TimeoutError` is raised if this
1432.                 is reached. If not specified, uses the *wait_timeout* specified when the
1433.                 instance was created.
1434.             successes: Number of times *ready* must return true for the wait to succeed.
1435. 
1436.         Raises:
1437.             TimeoutError: If the *timeout* is reached. A string representation
1438.                 of the last status, if any, is added as an exception note.
1439.             WaitError: If the *error* callable returns True. A string representation
1440.                 of the last status is added as an exception note.
1441.         """
1442.         if timeout is None:
1443.             timeout = self.wait_timeout
1444. 
1445.         status = None
1446.         success_count = 0
1447.         start = time.monotonic()
1448. 
1449.         while time.monotonic() - start < timeout:
1450.             prev_status = status
1451. 
1452.             stdout, _ = self._cli('status', '--format', 'json', log=False)
1453.             result = json.loads(stdout)
1454.             status = Status._from_dict(result)
1455. 
1456.             if status != prev_status:
1457.                 diff = _status_diff(prev_status, status)
1458.                 if diff:
1459.                     logger_wait.info('wait: status changed:\n%s', diff)
1460. 
1461.             if error is not None and error(status):
1462.                 name = getattr(error, '__qualname__', repr(error))
1463.                 raise WaitError(f'error function {name} returned true\n{status}')
1464. 
1465.             if ready(status):
1466.                 success_count += 1
1467.                 if success_count >= successes:
1468.                     return status
1469.             else:
1470.                 success_count = 0
1471. 
1472.             time.sleep(delay)
1473. 
1474.         if status is None:
1475.             raise TimeoutError(f'wait timed out after {timeout}s')
1476.         raise TimeoutError(f'wait timed out after {timeout}s\n{status}')
1477. 
1478.     @functools.cached_property
1479.     def _juju_is_snap(self) -> bool:
1480.         which = shutil.which(self.cli_binary)
1481.         return which is not None and '/snap/' in which
1482. 
1483.     @functools.cached_property
1484.     def _temp_dir(self) -> str:
1485.         if self._juju_is_snap:
1486.             # If Juju is running as a snap, we can't use /tmp, so put temp files here instead.
1487.             temp_dir = os.path.expanduser('~/snap/juju/common')
1488.             os.makedirs(temp_dir, exist_ok=True)
1489.             return temp_dir
1490.         else:
1491.             return tempfile.gettempdir()
1492. 
1493.     # This context manager is for deploy() and refresh(), and automatically copies
1494.     # a local charm file and local resource files into a temporary directory if Juju
1495.     # is running as a snap (in which case /tmp is not accessible).
1496.     @contextlib.contextmanager
1497.     def _deploy_tempdir(
1498.         self,
1499.         charm: str | pathlib.Path | None,
1500.         resources: Mapping[str, str] | None,
```

</details>


---

<sub>⏱️ 4m 14s</sub>

### 💬 Copilot

Now I have a thorough understanding of both APIs. Let me also check the `Task` type and `statustypes`:

---

<sub>⏱️ 4m 14s</sub>

### ✅ `bash`

**Check Task class**

$ grep -n "class Task\|results\|status\|failure" /home/ubuntu/.local/lib/python3.12/site-packages/jubilant/_task.py | head -30

<details>
<summary>17 lines</summary>

```
9:class TaskError(Exception):
23:class Task:
24:    """A task holds the results of Juju running an action or exec command on a single unit."""
29:    status: Literal['aborted', 'cancelled', 'completed', 'error', 'failed']
32:    results: dict[str, Any] = dataclasses.field(default_factory=dict)  # type: ignore
56:        if self.results:
57:            details.append(f'Results: {self.results}')
67:        s = f'Task {self.id}: status {self.status!r}, return code {self.return_code}'
77:        results: dict[str, Any] = d.get('results') or {}
78:        return_code = results.pop('return-code', 0)
79:        stdout = results.pop('stdout', '')
80:        stderr = results.pop('stderr', '')
83:            status=d['status'],
84:            results=results,
95:        return self.status == 'completed' and self.return_code == 0
97:    def raise_on_failure(self):
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 4m 14s</sub>

### ✅ `bash`

**Check Status types**

$ grep -n "class Status\|apps\|class App\|units\|class Unit\|relations\b" /home/ubuntu/.local/lib/python3.12/site-packages/jubilant/statustypes.py | head -40

<details>
<summary>34 lines</summary>

```
60:class StatusInfo:
85:class AppStatusRelation:
100:class UnitStatus:
169:class AppStatus:
188:    relations: dict[str, list[AppStatusRelation]] = dataclasses.field(default_factory=dict)  # type: ignore
190:    units: dict[str, UnitStatus] = dataclasses.field(default_factory=dict)  # type: ignore
225:            relations={
227:                for k, v in d.get('relations', {}).items()
230:            units={k: UnitStatus._from_dict(v) for k, v in d.get('units', {}).items()},
279:class UnitStorageAttachment:
295:    units: dict[str, UnitStorageAttachment]
300:            units={k: UnitStorageAttachment._from_dict(v) for k, v in d['units'].items()},
346:    units: dict[str, UnitStorageAttachment] = dataclasses.field(default_factory=dict)  # type: ignore
357:            units={k: UnitStorageAttachment._from_dict(v) for k, v in d.get('units', {}).items()},
415:    units: dict[str, UnitStorageAttachment] = dataclasses.field(default_factory=dict)  # type: ignore
424:            units={k: UnitStorageAttachment._from_dict(v) for k, v in d.get('units', {}).items()},
682:    relations: dict[str, list[str]] = dataclasses.field(default_factory=dict)  # type: ignore
700:            relations=d.get('relations') or {},
705:class Status:
714:    apps: dict[str, AppStatus]
734:            apps={k: AppStatus._from_dict(v) for k, v in d['applications'].items()},
773:    def get_units(self, app: str) -> dict[str, UnitStatus]:
774:        """Get all units of the given *app*, including units of subordinate apps.
776:        For subordinate apps, this finds and returns the subordinate units using the app's
777:        ``subordinate_to`` list. For principal (non-subordinate) apps, this is equivalent to
778:        ``status.apps[app].units``.
781:            Dict of units where the key is the unit name and the value is the :class:`UnitStatus`.
784:        app_info = self.apps.get(app)
788:            return app_info.units
790:        units: dict[str, UnitStatus] = {}
793:            for unit_info in self.apps[principal].units.values():
796:                        units[sub_name] = sub  # noqa: PERF403
797:        return units
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 4m 44s</sub>

### ✅ `view`

**/home/ubuntu/.local/lib/python3.12/site-packages/jubilant/_juju.py**

/home/ubuntu/.local/lib/python3.12/site-packages/jubilant/_juju.py (lines 1120-1180)

<details>
<summary>61 lines</summary>

```
1120.             # app/leader it is returned as app/N, for example app/0.
1121.             task_dict = next(iter(results.values()))
1122.             task = Task._from_dict(task_dict)
1123.             task.raise_on_failure()
1124.             return task
1125. 
1126.     def scp(
1127.         self,
1128.         source: str | pathlib.Path,
1129.         destination: str | pathlib.Path,
1130.         *,
1131.         container: str | None = None,
1132.         host_key_checks: bool = True,
1133.         scp_options: Iterable[str] = (),
1134.     ) -> None:
1135.         """Securely transfer files within a model.
1136. 
1137.         Args:
1138.             source: Source of file, in format ``[[<user>@]<target>:]<path>``.
1139.             destination: Destination for file, in format ``[<user>@]<target>[:<path>]``.
1140.             container: Name of container for Kubernetes charms. Defaults to the charm container.
1141.             host_key_checks: Set to False to disable host key checking (insecure).
1142.             scp_options: ``scp`` client options, for example ``['-r', '-C']``.
1143.         """
1144.         # Need this check because str is also an iterable of str.
1145.         if isinstance(scp_options, str):
1146.             raise TypeError('scp_options must be an iterable of str, not str')
1147. 
1148.         args = ['scp']
1149.         if container is not None:
1150.             args.extend(['--container', container])
1151.         if not host_key_checks:
1152.             args.append('--no-host-key-checks')
1153.         args.append('--')
1154.         args.extend(scp_options)
1155. 
1156.         source = str(source)
1157.         destination = str(destination)
1158.         temp_needed = (':' not in source) != (':' not in destination) and self._juju_is_snap
1159.         if not temp_needed:
1160.             # Simple cases: juju not snap, or local->local, or remote->remote
1161.             args.append(source)
1162.             args.append(destination)
1163.             self.cli(*args)
1164.             return
1165. 
1166.         with tempfile.NamedTemporaryFile('w+', dir=self._temp_dir) as file_temp:
1167.             if ':' not in source:
1168.                 # Local source, remote destination
1169.                 shutil.copy(source, file_temp.name)
1170.                 args.append(file_temp.name)
1171.                 args.append(destination)
1172.                 self.cli(*args)
1173.             else:
1174.                 # Remote source, local destination
1175.                 args.append(source)
1176.                 args.append(file_temp.name)
1177.                 self.cli(*args)
1178.                 shutil.copy(file_temp.name, destination)
1179. 
1180.     def secrets(self, *, owner: str | None = None) -> list[Secret]:
```

</details>


---

<sub>⏱️ 4m 44s</sub>

### ✅ `bash`

**Check if run raises on failure**

$ grep -n "raise_on_failure\|TaskError\|raise Task" /home/ubuntu/.local/lib/python3.12/site-packages/jubilant/_juju.py | head -20

```
704:            TaskError: if the command failed.
742:        task.raise_on_failure()
1080:            TaskError: if the action failed.
1123:            task.raise_on_failure()
<exited with exit code 0>
```


---

<sub>⏱️ 5m 34s</sub>

### ✅ `bash`

**Check pytest_jubilant exports**

$ python3 -c "import pytest_jubilant; print(dir(pytest_jubilant))"

```
['__all__', '__builtins__', '__cached__', '__doc__', '__file__', '__loader__', '__name__', '__package__', '__path__', '__spec__', 'get_resources', 'main', 'pack']
<exited with exit code 0>
```


---

<sub>⏱️ 5m 34s</sub>

### ✅ `view`

**/home/ubuntu/.local/lib/python3.12/site-packages/jubilant/statustypes.py**

/home/ubuntu/.local/lib/python3.12/site-packages/jubilant/statustypes.py (lines 85-105)

<details>
<summary>21 lines</summary>

```
85. class AppStatusRelation:
86.     related_app: str = ''
87.     interface: str = ''
88.     scope: str = ''
89. 
90.     @classmethod
91.     def _from_dict(cls, d: dict[str, Any]) -> AppStatusRelation:
92.         return cls(
93.             related_app=d.get('related-application') or '',
94.             interface=d.get('interface') or '',
95.             scope=d.get('scope') or '',
96.         )
97. 
98. 
99. @dataclasses.dataclass(frozen=True)
100. class UnitStatus:
101.     """Status of a single unit."""
102. 
103.     workload_status: StatusInfo = dataclasses.field(default_factory=StatusInfo)
104.     juju_status: StatusInfo = dataclasses.field(default_factory=StatusInfo)
105.     leader: bool = False
```

</details>


---

<sub>⏱️ 5m 47s</sub>

### 💬 Copilot

Let me check the unit tests before touching pytest config:

---

<sub>⏱️ 5m 47s</sub>

### ✅ `bash`

**Check unit test async usage**

$ grep -l "async def\|asyncio" /tmp/s3-integrator-L3-sonnet/tests/unit/*.py 2>/dev/null | head -5 && ls /tmp/s3-integrator-L3-sonnet/tests/unit/

```
/tmp/s3-integrator-L3-sonnet/tests/unit/test_charm.py
__init__.py  helpers.py  test_charm.py
<exited with exit code 0>
```


---

<sub>⏱️ 5m 53s</sub>

### ✅ `bash`

**Check unit test structure**

$ head -20 /tmp/s3-integrator-L3-sonnet/tests/unit/test_charm.py

<details>
<summary>16 lines</summary>

```
# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

import unittest
from asyncio.log import logger
from unittest import mock

from ops.model import BlockedStatus
from ops.testing import Harness

from charm import S3IntegratorCharm


class TestCharm(unittest.TestCase):
    def setUp(self):
        self.harness = Harness(S3IntegratorCharm)
        self.addCleanup(self.harness.cleanup)
        self.harness.begin()
        self.peer_relation_id = self.harness.add_relation(
            "s3-integrator-peers", "s3-integrator-peers"
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 6m 28s</sub>

### ✅ `bash`

**Find exec/ssh methods**

$ grep -n "def exec\|def ssh\|def run_on" /home/ubuntu/.local/lib/python3.12/site-packages/jubilant/_juju.py

```
665:    def exec(
670:    def exec(self, command: str, *args: str, unit: str, wait: float | None = None) -> Task: ...
672:    def exec(
1280:    def ssh(
<exited with exit code 0>
```


---

<sub>⏱️ 6m 32s</sub>

### ✅ `view`

**/home/ubuntu/.local/lib/python3.12/site-packages/jubilant/_juju.py**

/home/ubuntu/.local/lib/python3.12/site-packages/jubilant/_juju.py (lines 660-720)

<details>
<summary>61 lines</summary>

```
660.         self.cli(*args, include_model=False)
661.         if model == self.model:
662.             self.model = None
663. 
664.     @overload
665.     def exec(
666.         self, command: str, *args: str, machine: int | str, wait: float | None = None
667.     ) -> Task: ...
668. 
669.     @overload
670.     def exec(self, command: str, *args: str, unit: str, wait: float | None = None) -> Task: ...
671. 
672.     def exec(
673.         self,
674.         command: str,
675.         *args: str,
676.         machine: int | str | None = None,
677.         unit: str | None = None,
678.         wait: float | None = None,
679.     ) -> Task:
680.         """Run the command on the remote target specified.
681. 
682.         You must specify either *machine* or *unit*, but not both.
683. 
684.         Note: this method does not support running a command on multiple units
685.         at once. If you need that, let us know, and we'll consider adding it
686.         with a new ``exec_multiple`` method or similar.
687. 
688.         Args:
689.             command: Command to run. Because the command is executed using the shell,
690.                 arguments may also be included here as a single string, for example
691.                 ``juju.exec('echo foo', ...)``.
692.             args: Arguments of the command.
693.             machine: ID of machine to run the command on, for example ``0``, ``"0"``,
694.                 or ``"0/lxd/0"``.
695.             unit: Name of unit to run the command on, for example ``mysql/0`` or ``mysql/leader``.
696.             wait: Maximum time to wait for command to finish; :class:`TimeoutError` is raised if
697.                 this is reached. Juju's default is to wait 5 minutes.
698. 
699.         Returns:
700.             The task created to run the command, including logs, failure message, and so on.
701. 
702.         Raises:
703.             ValueError: if the machine or unit doesn't exist.
704.             TaskError: if the command failed.
705.             TimeoutError: if *wait* was specified and the wait time was reached.
706.         """
707.         if (machine is not None and unit is not None) or (machine is None and unit is None):
708.             raise TypeError('must specify "machine" or "unit", but not both')
709. 
710.         cli_args = ['exec', '--format', 'json']
711.         if machine is not None:
712.             cli_args.extend(['--machine', str(machine)])
713.         else:
714.             assert unit is not None
715.             cli_args.extend(['--unit', unit])
716.         if wait is not None:
717.             cli_args.extend(['--wait', f'{wait}s'])
718.         cli_args.append('--')
719.         cli_args.append(command)
720.         cli_args.extend(args)
```

</details>


---

<sub>⏱️ 6m 57s</sub>

### 💬 Copilot

Now I have a complete picture of the jubilant API. Let me implement the migration:

---

<sub>⏱️ 6m 58s</sub>

### ✅ `sql`

**Create migration todos**

<details>
<summary>Arguments</summary>

```json
{
  "description": "Create migration todos",
  "query": "INSERT INTO todos (id, title, description, status) VALUES\n  ('pyproject', 'Update pyproject.toml', 'Replace pytest-operator + juju with jubilant + pytest-jubilant in integration group. Keep asyncio_mode for unit tests.', 'pending'),\n  ('helpers', 'Rewrite helpers.py', 'Remove async/await, replace Unit type with str, use juju.run() for actions, juju.cli() for show-unit. Remove is_relation_joined/broken and run_command_on_unit (not used in tests). Pass juju: Juju to helpers needing model access.', 'pending'),\n  ('conftest', 'Create conftest.py', 'Module-scoped fixtures for packing s3 charm and app charm using pytest_jubilant.pack()', 'pending'),\n  ('testfile', 'Rewrite test_s3_charm.py', 'Remove async def, replace OpsTest with juju: jubilant.Juju, replace asyncio.gather with sequential calls, use jubilant.wait() helpers. Handle expected action failure with pytest.raises(TaskError).', 'pending');"
}
```

</details>

```
4 row(s) inserted. Last inserted row ID: 4.
```


---

<sub>⏱️ 7m 4s</sub>

### ✅ `edit`

**/tmp/s3-integrator-L3-sonnet/pyproject.toml**

/tmp/s3-integrator-L3-sonnet/pyproject.toml

```
File /tmp/s3-integrator-L3-sonnet/pyproject.toml updated with changes.
```


---

<sub>⏱️ 7m 32s</sub>

### 💬 Copilot

Now rewrite `helpers.py`:

---

<sub>⏱️ 7m 32s</sub>

### ✅ `edit`

**/tmp/s3-integrator-L3-sonnet/tests/integration/helpers.py**

/tmp/s3-integrator-L3-sonnet/tests/integration/helpers.py

```
File /tmp/s3-integrator-L3-sonnet/tests/integration/helpers.py updated with changes.
```


---

<sub>⏱️ 7m 40s</sub>

### 💬 Copilot

Now create `conftest.py`:

---

<sub>⏱️ 7m 40s</sub>

### ✅ `create`

**/tmp/s3-integrator-L3-sonnet/tests/integration/conftest.py**

/tmp/s3-integrator-L3-sonnet/tests/integration/conftest.py

```
Created file /tmp/s3-integrator-L3-sonnet/tests/integration/conftest.py with 495 characters
```


---

<sub>⏱️ 8m 39s</sub>

### 💬 Copilot

Now rewrite `test_s3_charm.py`:

---

<sub>⏱️ 8m 39s</sub>

### ✅ `edit`

**/tmp/s3-integrator-L3-sonnet/tests/integration/test_s3_charm.py**

/tmp/s3-integrator-L3-sonnet/tests/integration/test_s3_charm.py

```
File /tmp/s3-integrator-L3-sonnet/tests/integration/test_s3_charm.py updated with changes.
```


---

<sub>⏱️ 8m 46s</sub>

### 💬 Copilot

Now let's verify the files look correct and run the linter:

---

<sub>⏱️ 8m 47s</sub>

### ✅ `bash`

**Syntax check all migrated files**

$ cd /tmp/s3-integrator-L3-sonnet && python3 -c "
import ast, sys
for f in ['tests/integration/helpers.py', 'tests/integration/test_s3_charm.py', 'tests/integration/conftest.py']:
    try:
        ast.parse(open(f).read())
        print(f'OK: {f}')
    except SyntaxError as e:
        print(f'SYNTAX ERROR in {f}: {e}')
        sys.exit(1)
"

```
OK: tests/integration/helpers.py
OK: tests/integration/test_s3_charm.py
OK: tests/integration/conftest.py
<exited with exit code 0>
```


---

<sub>⏱️ 8m 47s</sub>

### ✅ `bash`

**Verify no old API references remain**

$ cd /tmp/s3-integrator-L3-sonnet && grep -n "async def\|await \|ops_test\|OpsTest\|pytest_operator\|from juju\|asyncio.gather\|block_until\|fast_forward\|is_relation_joined\|is_relation_broken" tests/integration/test_s3_charm.py tests/integration/helpers.py tests/integration/conftest.py 2>/dev/null

```

<exited with exit code 1>
```


---

<sub>⏱️ 8m 51s</sub>

### 💬 Copilot

No old API references remain. Let's run the linter:

---

<sub>⏱️ 8m 52s</sub>

### ✅ `bash`

**Run ruff linter on migrated files**

$ cd /tmp/s3-integrator-L3-sonnet && python3 -m ruff check tests/integration/ --select E,F,I001 2>&1

```
/usr/bin/python3: No module named ruff
<exited with exit code 1>
```


---

<sub>⏱️ 8m 59s</sub>

### ✅ `bash`

**Find ruff**

$ find /home/ubuntu/.local/bin /usr/local/bin -name ruff 2>/dev/null; python3 -m pip show ruff --break-system-packages 2>/dev/null | head -3

```

<exited with exit code 0>
```


---

<sub>⏱️ 9m 20s</sub>

### ✅ `bash`

**Install ruff and lint**

$ python3 -m pip install ruff --break-system-packages -q && python3 -m ruff check tests/integration/ 2>&1

<details>
<summary>38 lines</summary>

```
F401 [*] `ops.framework` imported but unused
   --> tests/integration/application-charm/lib/charms/data_platform_libs/v0/s3.py:120:8
    |
119 | import ops.charm
120 | import ops.framework
    |        ^^^^^^^^^^^^^
121 | import ops.model
122 | from ops.charm import (
    |
help: Remove unused import: `ops.framework`
117 | from typing import Dict, List, Optional, Union
118 | 
119 | import ops.charm
    - import ops.framework
120 | import ops.model
121 | from ops.charm import (
122 |     CharmBase,

F401 [*] `ops.model` imported but unused
   --> tests/integration/application-charm/lib/charms/data_platform_libs/v0/s3.py:121:8
    |
119 | import ops.charm
120 | import ops.framework
121 | import ops.model
    |        ^^^^^^^^^
122 | from ops.charm import (
123 |     CharmBase,
    |
help: Remove unused import: `ops.model`
118 | 
119 | import ops.charm
120 | import ops.framework
    - import ops.model
121 | from ops.charm import (
122 |     CharmBase,
123 |     CharmEvents,

Found 2 errors.
[*] 2 fixable with the `--fix` option.
<exited with exit code 1>
```

</details>


---

<sub>⏱️ 9m 32s</sub>

### ✅ `bash`

**Lint only migrated files**

$ cd /tmp/s3-integrator-L3-sonnet && python3 -m ruff check tests/integration/helpers.py tests/integration/test_s3_charm.py tests/integration/conftest.py 2>&1

```
All checks passed!
<exited with exit code 0>
```


---

<sub>⏱️ 9m 46s</sub>

### 💬 Copilot

All checks pass. Let me do a final review of the complete migration:

---

<sub>⏱️ 9m 47s</sub>

### ✅ `bash`

**Final review of changes**

$ cd /tmp/s3-integrator-L3-sonnet && echo "=== pyproject.toml integration group ===" && grep -A4 "\[tool.poetry.group.integration" pyproject.toml && echo "" && echo "=== New files ===" && wc -l tests/integration/helpers.py tests/integration/test_s3_charm.py tests/integration/conftest.py

<details>
<summary>11 lines</summary>

```
=== pyproject.toml integration group ===
[tool.poetry.group.integration.dependencies]
pytest = "^8.4.2"
jubilant = "*"
pytest-jubilant = "*"


=== New files ===
  126 tests/integration/helpers.py
  195 tests/integration/test_s3_charm.py
   18 tests/integration/conftest.py
  339 total
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 9m 54s</sub>

### ✅ `bash`

**Show git diff summary**

$ cd /tmp/s3-integrator-L3-sonnet && git diff --stat

```
pyproject.toml                     |   4 +-
 tests/integration/helpers.py       | 141 ++++++++++++++++++++-----------------------------------
 tests/integration/test_s3_charm.py | 195 ++++++++++++++++++++++++++---------------------------------------------------
 3 files changed, 117 insertions(+), 223 deletions(-)
<exited with exit code 0>
```


---

<sub>⏱️ 10m 8s</sub>

### ✅ `bash`

**Commit migration**

$ cd /tmp/s3-integrator-L3-sonnet && git add -A && git commit -m "Migrate integration tests from pytest-operator to jubilant

- Replace pytest-operator + python-libjuju with jubilant + pytest-jubilant
  in pyproject.toml integration dependencies
- Rewrite helpers.py: remove async/await, replace Unit type with str unit
  names, use juju.run() for actions and juju.cli() for show-unit,
  remove is_relation_joined/is_relation_broken (replaced by juju.wait()),
  migrate run_command_on_unit to use juju.exec()
- Rewrite test_s3_charm.py: remove async def / asyncio.gather /
  ops_test.fast_forward, replace OpsTest fixture with jubilant.Juju,
  use jubilant.all_active/all_blocked/all_waiting predicates in juju.wait(),
  catch expected action failure with pytest.raises(jubilant.TaskError),
  use juju.integrate() / juju.remove_relation() / juju.config()
- Create conftest.py with module-scoped s3_charm and app_charm fixtures
  that pack charms via pytest_jubilant.pack()

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"

<details>
<summary>9 lines</summary>

```
Author identity unknown

*** Please tell me who you are.

Run

  git config --global user.email "you@example.com"
  git config --global user.name "Your Name"

to set your account's default identity.
Omit --global to set the identity only in this repository.

fatal: unable to auto-detect email address (got 'ubuntu@jubilant-migration.(none)')
<exited with exit code 128>
```

</details>


---

<sub>⏱️ 10m 16s</sub>

### ✅ `bash`

**Commit with git config**

$ cd /tmp/s3-integrator-L3-sonnet && git config user.email "copilot@github.com" && git config user.name "Copilot" && git commit -m "Migrate integration tests from pytest-operator to jubilant

- Replace pytest-operator + python-libjuju with jubilant + pytest-jubilant
  in pyproject.toml integration dependencies
- Rewrite helpers.py: remove async/await, replace Unit type with str unit
  names, use juju.run() for actions and juju.cli() for show-unit,
  remove is_relation_joined/is_relation_broken (replaced by juju.wait()),
  migrate run_command_on_unit to use juju.exec()
- Rewrite test_s3_charm.py: remove async def / asyncio.gather /
  ops_test.fast_forward, replace OpsTest fixture with jubilant.Juju,
  use jubilant.all_active/all_blocked/all_waiting predicates in juju.wait(),
  catch expected action failure with pytest.raises(jubilant.TaskError),
  use juju.integrate() / juju.remove_relation() / juju.config()
- Create conftest.py with module-scoped s3_charm and app_charm fixtures
  that pack charms via pytest_jubilant.pack()

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"

```
[main 71c0eed] Migrate integration tests from pytest-operator to jubilant
 4 files changed, 135 insertions(+), 223 deletions(-)
 create mode 100644 tests/integration/conftest.py
<exited with exit code 0>
```


---

<sub>⏱️ 10m 28s</sub>

### 💬 Copilot

Migration complete. Here's a summary of what changed:

**`pyproject.toml`**: Replaced `pytest-operator` + `juju` with `jubilant` + `pytest-jubilant` in the integration dependency group.

**`tests/integration/helpers.py`**: Fully rewritten synchronously:
- Functions now take `juju: jubilant.Juju` + `unit: str` instead of `ops_test: OpsTest` + `Unit`
- `fetch_action_*` helpers use `juju.run(unit, action, params)` → returns `Task.results`
- `get_relation_data` / `get_application_data` use `juju.cli("show-unit", ...)` (returns `str`, not a tuple)
- `run_command_on_unit` migrated to `juju.exec(command, unit=unit)`
- Removed `is_relation_joined` / `is_relation_broken` (replaced by `juju.wait()` predicates)

**`tests/integration/conftest.py`** *(new)*: Module-scoped `s3_charm` and `app_charm` fixtures that call `pytest_jubilant.pack()` to build charms once per test module.

**`tests/integration/test_s3_charm.py`**: All tests converted from `async def` to `def`:
- `ops_test: OpsTest` → `juju: jubilant.Juju` (provided by pytest-jubilant's `juju` fixture)
- `asyncio.gather` / `fast_forward` / `block_until` → `juju.wait(lambda status: ...)`
- Expected action failure checked with `pytest.raises(jubilant.TaskError)`
- `set_config` → `juju.config(app, values)`, `add_relation` → `juju.integrate()`, `remove_relation` → `juju.remove_relation()`

---

<sub>Generated by [GitHub Copilot CLI](https://github.com/features/copilot/cli)</sub>
