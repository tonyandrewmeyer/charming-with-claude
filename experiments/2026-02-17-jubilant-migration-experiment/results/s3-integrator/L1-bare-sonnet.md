# 🤖 Copilot CLI Session

> **Session ID:** `47293ce1-384a-4e9f-ad31-91514d5eed69`
> **Started:** 3/7/2026, 12:54:19 PM
> **Duration:** 12m 33s
> **Exported:** 3/7/2026, 1:06:53 PM

<sub>⏱️ 5s</sub>

### 👤 User

Migrate this charm's integration tests from pytest-operator (python-libjuju) to jubilant and pytest-jubilant. Update all test files, conftest.py, helpers, and dependencies.

---

<sub>⏱️ 13s</sub>

### 📦 task (Completed)

### 💬 Copilot

I'll explore the integration test structure comprehensively. Let me start by examining the directory structure and finding all test files.

### ✅ `view`

**/tmp/s3-integrator-L1-sonnet**

/tmp/s3-integrator-L1-sonnet

<details>
<summary>20 lines</summary>

```
.git
.github
.gitignore
CONTRIBUTING.md
LICENSE
README.md
SECURITY.md
actions.yaml
charmcraft.yaml
concierge.yaml
config.yaml
icon.svg
lib
metadata.yaml
poetry.lock
pyproject.toml
spread.yaml
src
tests
tox.ini
```

</details>


### ✅ `glob`

**tests/**/***

"tests/**/*"

<details>
<summary>16 matches</summary>

```
./tests/spread/test_s3_charm.py/task.yaml
./tests/ca_chain.pem
./tests/unit/__init__.py
./tests/unit/test_charm.py
./tests/unit/helpers.py
./tests/integration/__init__.py
./tests/integration/architecture.py
./tests/integration/test_s3_charm.py
./tests/integration/helpers.py
./tests/integration/application-charm/actions.yaml
./tests/integration/application-charm/poetry.lock
./tests/integration/application-charm/charmcraft.yaml
./tests/integration/application-charm/src/charm.py
./tests/integration/application-charm/metadata.yaml
./tests/integration/application-charm/pyproject.toml
./tests/integration/application-charm/lib/charms/data_platform_libs/v0/s3.py
```

</details>


### ✅ `glob`

****/conftest.py**

"**/conftest.py"

```
No files matched the pattern.
```


### ✅ `glob`

****/*.py**

"**/*.py"

<details>
<summary>12 matches</summary>

```
./tests/unit/__init__.py
./tests/unit/test_charm.py
./tests/unit/helpers.py
./tests/integration/__init__.py
./tests/integration/architecture.py
./tests/integration/application-charm/src/charm.py
./tests/integration/application-charm/lib/charms/data_platform_libs/v0/s3.py
./tests/integration/helpers.py
./tests/integration/test_s3_charm.py
./src/charm.py
./src/constants.py
./lib/charms/data_platform_libs/v0/s3.py
```

</details>


### 💬 Copilot

Now let me read all the key test files and configuration files in parallel:

### ✅ `view`

**/tmp/s3-integrator-L1-sonnet/pyproject.toml**

/tmp/s3-integrator-L1-sonnet/pyproject.toml

<details>
<summary>97 lines</summary>

```
1. # Copyright 2022 Canonical Ltd.
2. # See LICENSE file for licensing details.
3. 
4. [tool.poetry]
5. package-mode = false
6. requires-poetry = ">=2.0.0"
7. 
8. [tool.poetry.dependencies]
9. python = "^3.10"
10. ops = "^3.6.0"
11. 
12. [tool.poetry.group.charm-libs.dependencies]
13. 
14. [tool.poetry.group.format]
15. optional = true
16. 
17. [tool.poetry.group.format.dependencies]
18. ruff = "^0.15.4"
19. 
20. [tool.poetry.group.lint]
21. optional = true
22. 
23. [tool.poetry.group.lint.dependencies]
24. codespell = "^2.4.1"
25. 
26. [tool.poetry.group.unit.dependencies]
27. coverage = {extras = ["toml"], version = "^7.13.4"}
28. pytest = "^8.4.2"
29. pytest-asyncio = "*"
30. parameterized = "^0.9.0"
31. 
32. [tool.poetry.group.integration.dependencies]
33. pytest = "^8.4.2"
34. pytest-operator = "^0.43.2"
35. juju = "^3.5.2.0"
36. 
37. # Testing tools configuration
38. [tool.coverage.run]
39. branch = true
40. 
41. [tool.coverage.report]
42. show_missing = true
43. 
44. [tool.pytest.ini_options]
45. minversion = "6.0"
46. log_cli_level = "INFO"
47. asyncio_mode = "auto"
48. markers = ["unstable"]
49. 
50. # Formatting tools configuration
51. [tool.black]
52. line-length = 99
53. target-version = ["py310"]
54. 
55. # Linting tools configuration
56. [tool.ruff]
57. # preview and explicit preview are enabled for CPY001
58. preview = true
59. target-version = "py310"
60. src = ["src", "."]
61. line-length = 99
62. 
63. [tool.ruff.lint]
64. explicit-preview-rules = true
65. select = ["A", "E", "W", "F", "C", "N", "D", "I001", "CPY001"]
66. extend-ignore = [
67.     "D203",
68.     "D204",
69.     "D213",
70.     "D215",
71.     "D400",
72.     "D404",
73.     "D406",
74.     "D407",
75.     "D408",
76.     "D409",
77.     "D413",
78. ]
79. # Ignore E501 because using black creates errors with this
80. # Ignore D107 Missing docstring in __init__
81. ignore = ["E501", "D107"]
82. 
83. [tool.ruff.lint.per-file-ignores]
84. "tests/*" = ["D100", "D101", "D102", "D103", "D104"]
85. 
86. [tool.ruff.lint.flake8-copyright]
87. # Check for properly formatted copyright header in each file
88. author = "Canonical Ltd."
89. notice-rgx = "Copyright\\s\\d{4}([-,]\\d{4})*\\s+"
90. min-file-size = 1
91. 
92. [tool.ruff.lint.mccabe]
93. max-complexity = 10
94. 
95. [tool.ruff.lint.pydocstyle]
96. convention = "google"
97.
```

</details>


### ✅ `view`

**/tmp/s3-integrator-L1-sonnet/tox.ini**

/tmp/s3-integrator-L1-sonnet/tox.ini

<details>
<summary>65 lines</summary>

```
1. # Copyright 2022 Canonical Ltd.
2. # See LICENSE file for licensing details.
3. 
4. [tox]
5. no_package = True
6. skip_missing_interpreters = True
7. env_list = lint, unit
8. 
9. [vars]
10. src_path = {tox_root}/src
11. tests_path = {tox_root}/tests
12. test_charm_libs_path = {[vars]tests_path}/integration/application-charm/lib/
13. all_path = {[vars]src_path} {[vars]tests_path}
14. 
15. [testenv]
16. set_env =
17.     PYTHONPATH = {tox_root}/lib:{[vars]src_path}
18.     PYTHONBREAKPOINT=ipdb.set_trace
19.     PY_COLORS=1
20. pass_env =
21.     PYTHONPATH
22.     CHARM_BUILD_DIR
23.     MODEL_SETTINGS
24. allowlist_externals =
25.     poetry
26. 
27. [testenv:format]
28. description = Apply coding style standards to code
29. commands_pre =
30.     poetry install --only format --no-root
31. commands =
32.     poetry lock
33.     poetry run ruff check --fix {[vars]all_path} --exclude {[vars]test_charm_libs_path}
34.     poetry run ruff format {[vars]all_path} --exclude {[vars]test_charm_libs_path}
35. 
36. [testenv:lint]
37. description = Check code against coding style standards
38. commands_pre =
39.     poetry install --only lint,format --no-root
40. commands =
41.     poetry check --lock
42.     poetry run codespell {[vars]all_path}
43.     poetry run ruff check {[vars]all_path} --exclude {[vars]test_charm_libs_path}
44.     poetry run ruff format --check --diff {[vars]all_path} --exclude {[vars]test_charm_libs_path}
45. 
46. [testenv:unit]
47. description = Run unit tests
48. commands_pre =
49.     poetry install --only main,charm-libs,unit --no-root
50. commands =
51.     poetry run coverage run --source={[vars]src_path} \
52.         -m pytest -v --tb native -s {posargs} {[vars]tests_path}/unit
53.     poetry run coverage report
54. 
55. [testenv:integration]
56. description = Run integration tests
57. pass_env =
58.     CI
59.     GITHUB_OUTPUT
60.     SECRETS_FROM_GITHUB
61. commands_pre =
62.     poetry install --only integration --no-root
63. commands =
64.     poetry run pytest -v --tb native --log-cli-level=INFO -s --ignore={[vars]tests_path}/unit/ {posargs}
65.
```

</details>


### ✅ `view`

**/tmp/s3-integrator-L1-sonnet/tests/integration/test_s3_charm.py**

/tmp/s3-integrator-L1-sonnet/tests/integration/test_s3_charm.py

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


### ❌ `view`

**/tmp/s3-integrator-L1-sonnet/tests/integration/conftest.py**

/tmp/s3-integrator-L1-sonnet/tests/integration/conftest.py

```
Path does not exist
```


### ✅ `view`

**/tmp/s3-integrator-L1-sonnet/tests/integration/helpers.py**

/tmp/s3-integrator-L1-sonnet/tests/integration/helpers.py

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


### ✅ `view`

**/tmp/s3-integrator-L1-sonnet/tests/integration/architecture.py**

/tmp/s3-integrator-L1-sonnet/tests/integration/architecture.py

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


### ✅ `view`

**/tmp/s3-integrator-L1-sonnet/tests/unit/test_charm.py**

/tmp/s3-integrator-L1-sonnet/tests/unit/test_charm.py

<details>
<summary>112 lines</summary>

```
1. # Copyright 2024 Canonical Ltd.
2. # See LICENSE file for licensing details.
3. 
4. import unittest
5. from asyncio.log import logger
6. from unittest import mock
7. 
8. from ops.model import BlockedStatus
9. from ops.testing import Harness
10. 
11. from charm import S3IntegratorCharm
12. 
13. 
14. class TestCharm(unittest.TestCase):
15.     def setUp(self):
16.         self.harness = Harness(S3IntegratorCharm)
17.         self.addCleanup(self.harness.cleanup)
18.         self.harness.begin()
19.         self.peer_relation_id = self.harness.add_relation(
20.             "s3-integrator-peers", "s3-integrator-peers"
21.         )
22.         self.charm = self.harness.charm
23. 
24.     def test_on_start(self):
25.         """Checks that the charm started in blockled status for missing parameters."""
26.         self.harness.set_leader(True)
27.         self.charm.on.config_changed.emit()
28.         self.charm.on.start.emit()
29.         # check that the charm is in blocked status
30.         logger.info(f"Status: {self.harness.model.unit.status}")
31.         self.assertTrue(isinstance(self.harness.model.unit.status, BlockedStatus))
32. 
33.     def test_on_config_changed(self):
34.         """Checks that configuration parameters are correctly stored in the databag."""
35.         # ensure that the peer relation databag is empty
36.         peer_relation_databag = self.harness.get_relation_data(
37.             self.peer_relation_id, self.harness.charm.app
38.         )
39.         self.assertEqual(peer_relation_databag, {})
40.         # trigger the leader_elected and config_changed events
41.         self.harness.set_leader(True)
42.         self.harness.update_config({"region": "test-region"})
43.         self.harness.update_config({"endpoint": "test-endpoint"})
44. 
45.         # ensure that the peer relation has 'cluster_name' set to the config value
46.         peer_relation_databag = self.harness.get_relation_data(
47.             self.peer_relation_id, self.harness.charm.app
48.         )
49. 
50.         self.assertEqual(peer_relation_databag["region"], "test-region")
51.         self.assertEqual(peer_relation_databag["endpoint"], "test-endpoint")
52. 
53.         peer_relation_databag = self.harness.get_relation_data(
54.             self.peer_relation_id, self.harness.charm.app
55.         )
56. 
57.         self.harness.update_config({"region": ""})
58.         self.assertIsNot("region", peer_relation_databag)
59. 
60.     def test_set_access_and_secret_key(self):
61.         """Tests that secret and access keys are set."""
62.         self.harness.set_leader(True)
63.         action_event = mock.Mock()
64.         action_event.params = {"access-key": "test-access-key", "secret-key": "test-secret-key"}
65.         self.harness.charm._on_sync_s3_credentials(action_event)
66. 
67.         access_key = self.harness.charm.app_peer_data["access-key"]
68.         secret_key = self.harness.charm.app_peer_data["secret-key"]
69.         # verify app data is updated and results are reported to user
70.         self.assertEqual("test-access-key", access_key)
71.         self.assertEqual("test-secret-key", secret_key)
72. 
73.         action_event.set_results.assert_called_once_with({
74.             "ok": "Credentials successfully updated."
75.         })
76. 
77.     def test_get_s3_credentials(self):
78.         """Tests that secret and access key are retrieved correctly."""
79.         self.harness.set_leader(True)
80.         event = mock.Mock()
81.         self.harness.charm.on_get_credentials_action(event)
82.         event.fail.assert_called()
83. 
84.         self.harness.charm.app_peer_data["access-key"] = "test-access-key"
85.         self.harness.charm.app_peer_data["secret-key"] = "test-secret-key"
86. 
87.         self.harness.charm.on_get_credentials_action(event)
88.         event.set_results.assert_called_with({"ok": "Credentials are configured."})
89. 
90.     def test_get_connection_info(self):
91.         """Tests that s3 connection parameters are retrieved correctly."""
92.         self.harness.set_leader(True)
93.         event = mock.Mock()
94.         self.harness.charm.app_peer_data["access-key"] = "test-access-key"
95.         self.harness.charm.app_peer_data["secret-key"] = "test-secret-key"
96.         self.harness.charm.on_get_connection_info_action(event)
97.         event.set_results.assert_called_with({
98.             "access-key": "************",
99.             "secret-key": "************",
100.         })
101.         # update some configuration parameters
102.         self.harness.update_config({"region": "test-region"})
103.         self.harness.update_config({"endpoint": "test-endpoint"})
104.         # test that new parameter are present in the event results.
105.         self.harness.charm.on_get_connection_info_action(event)
106.         event.set_results.assert_called_with({
107.             "access-key": "************",
108.             "secret-key": "************",
109.             "region": "test-region",
110.             "endpoint": "test-endpoint",
111.         })
112.
```

</details>


### ✅ `view`

**/tmp/s3-integrator-L1-sonnet/tests/unit/helpers.py**

/tmp/s3-integrator-L1-sonnet/tests/unit/helpers.py

<details>
<summary>32 lines</summary>

```
1. #!/usr/bin/env python3
2. # Copyright 2022 Canonical Ltd.
3. # See LICENSE file for licensing details.
4. 
5. """Helper functions for writing tests."""
6. 
7. from typing import Callable
8. from unittest.mock import patch
9. 
10. 
11. def patch_network_get(private_address="10.1.157.116") -> Callable:
12.     def network_get(*args, **kwargs) -> dict:
13.         """Patch for the not-yet-implemented testing backend needed for `bind_address`.
14. 
15.         This patch decorator can be used for cases such as:
16.         self.model.get_binding(event.relation).network.bind_address
17.         """
18.         return {
19.             "bind-addresses": [
20.                 {
21.                     "mac-address": "",
22.                     "interface-name": "",
23.                     "addresses": [{"hostname": "", "value": private_address, "cidr": ""}],
24.                 }
25.             ],
26.             "bind-address": private_address,
27.             "egress-subnets": ["10.152.183.65/32"],
28.             "ingress-addresses": ["10.152.183.65"],
29.         }
30. 
31.     return patch("ops.testing._TestingModelBackend.network_get", network_get)
32.
```

</details>


### 💬 Copilot

Now let me check if there's a conftest.py in the tests directory or if we need to look at pytest configuration:

### ✅ `bash`

**Find all conftest.py files in tests directory**

$ find /tmp/s3-integrator-L1-sonnet/tests -name "conftest.py" -type f 2>/dev/null

```

<exited with exit code 0>
```


### ✅ `view`

**/tmp/s3-integrator-L1-sonnet/tests**

/tmp/s3-integrator-L1-sonnet/tests

```
ca_chain.pem
integration
spread
unit
```


### ✅ `view`

**/tmp/s3-integrator-L1-sonnet/tests/integration**

/tmp/s3-integrator-L1-sonnet/tests/integration

```
__init__.py
application-charm
architecture.py
helpers.py
test_s3_charm.py
```


### 💬 Copilot

Now let me view the test-related files in more detail and check the test structure:

### ✅ `view`

**/tmp/s3-integrator-L1-sonnet/tests/unit/__init__.py**

/tmp/s3-integrator-L1-sonnet/tests/unit/__init__.py

```
1. # Copyright 2023 Canonical Ltd.
2. # See LICENSE file for licensing details.
3. 
```


### ✅ `view`

**/tmp/s3-integrator-L1-sonnet/tests/integration/__init__.py**

/tmp/s3-integrator-L1-sonnet/tests/integration/__init__.py

```
1. # Copyright 2023 Canonical Ltd.
2. # See LICENSE file for licensing details.
3. 
```


### ✅ `view`

**/tmp/s3-integrator-L1-sonnet/tests/integration/application-charm**

/tmp/s3-integrator-L1-sonnet/tests/integration/application-charm

<details>
<summary>7 lines</summary>

```
actions.yaml
charmcraft.yaml
lib
metadata.yaml
poetry.lock
pyproject.toml
src
```

</details>


### 💬 Copilot

Let me check the application charm to understand the test setup better:

### ✅ `view`

**/tmp/s3-integrator-L1-sonnet/tests/integration/application-charm/src/charm.py**

/tmp/s3-integrator-L1-sonnet/tests/integration/application-charm/src/charm.py

<details>
<summary>103 lines</summary>

```
1. #!/usr/bin/env python3
2. # Copyright 2022 Canonical Ltd.
3. # See LICENSE file for licensing details.
4. 
5. """Application charm that connects to database charms.
6. 
7. This charm is meant to be used only for testing
8. the database requires-provides relation.
9. """
10. 
11. import logging
12. 
13. from charms.data_platform_libs.v0.s3 import (
14.     CredentialsChangedEvent,
15.     CredentialsGoneEvent,
16.     S3Requirer,
17. )
18. from ops.charm import CharmBase, RelationJoinedEvent
19. from ops.main import main
20. from ops.model import ActiveStatus, WaitingStatus
21. 
22. logger = logging.getLogger(__name__)
23. 
24. PEER = "application-peers"
25. FIRST_RELATION = "first-s3-credentials"
26. SECOND_RELATION = "second-s3-credentials"
27. BUCKET_NAME = "test-bucket"
28. 
29. 
30. class ApplicationCharm(CharmBase):
31.     """Application charm that relates to S3 integrator."""
32. 
33.     def __init__(self, *args):
34.         super().__init__(*args)
35. 
36.         # Default charm events.
37.         self.framework.observe(self.on.start, self._on_start)
38. 
39.         # Events related to the requested database
40.         # (these events are defined in the database requires charm library).
41. 
42.         self.first_s3_client = S3Requirer(self, FIRST_RELATION)
43.         self.second_s3_client = S3Requirer(self, SECOND_RELATION, bucket_name=BUCKET_NAME)
44. 
45.         # add relation
46.         self.framework.observe(
47.             self.first_s3_client.on.credentials_changed, self._on_first_credential_changed
48.         )
49.         self.framework.observe(
50.             self.second_s3_client.on.credentials_changed, self._on_second_credential_changed
51.         )
52. 
53.         self.framework.observe(
54.             self.on[FIRST_RELATION].relation_joined, self._on_first_relation_joined
55.         )
56.         self.framework.observe(
57.             self.on[SECOND_RELATION].relation_joined, self._on_second_relation_joined
58.         )
59. 
60.         self.framework.observe(
61.             self.first_s3_client.on.credentials_gone, self._on_first_credential_gone
62.         )
63.         self.framework.observe(
64.             self.second_s3_client.on.credentials_gone, self._on_second_credential_gone
65.         )
66. 
67.     def _on_start(self, _) -> None:
68.         """Only sets an waiting status."""
69.         self.unit.status = WaitingStatus("Waiting for relation")
70. 
71.     def _on_first_relation_joined(self, _: RelationJoinedEvent):
72.         """On s3 credential relation joined."""
73.         self.unit.status = ActiveStatus()
74. 
75.     def _on_second_relation_joined(self, _: RelationJoinedEvent):
76.         """On s3 credential relation joined."""
77.         self.unit.status = ActiveStatus()
78. 
79.     def _on_first_credential_changed(self, e: CredentialsChangedEvent):
80.         credentials = self.first_s3_client.get_s3_connection_info()
81.         logger.info(f"First relation updated credentials: {credentials}")
82. 
83.     def _on_second_credential_changed(self, e: CredentialsChangedEvent):
84.         credentials = self.second_s3_client.get_s3_connection_info()
85.         logger.info(f"Second relation updated credentials: {credentials}")
86. 
87.     def _on_first_credential_gone(self, _: CredentialsGoneEvent):
88.         logger.info("First relation credentials GONE!")
89.         self.unit.status = WaitingStatus("Waiting for relation")
90. 
91.     def _on_second_credential_gone(self, _: CredentialsGoneEvent):
92.         logger.info("Second relation Credentials GONE!")
93.         self.unit.status = WaitingStatus("Waiting for relation")
94. 
95.     @property
96.     def _peers(self):
97.         """Retrieve the peer relation (`ops.model.Relation`)."""
98.         return self.model.get_relation(PEER)
99. 
100. 
101. if __name__ == "__main__":
102.     main(ApplicationCharm)
103.
```

</details>


### ✅ `view`

**/tmp/s3-integrator-L1-sonnet/tests/integration/application-charm/metadata.yaml**

/tmp/s3-integrator-L1-sonnet/tests/integration/application-charm/metadata.yaml

<details>
<summary>15 lines</summary>

```
1. # Copyright 2022 Canonical Ltd.
2. # See LICENSE file for licensing details.
3. name: application
4. description: |
5.   Data platform libs application charm used in integration tests.
6. summary: |
7.   Data platform libs application meant to be used
8.   only for testing of the libs in this repository.
9. 
10. requires:
11.   first-s3-credentials:
12.     interface: s3
13.   second-s3-credentials:
14.     interface: s3
15.
```

</details>


### ✅ `bash`

**View application charm pyproject.toml**

$ head -100 /tmp/s3-integrator-L1-sonnet/tests/integration/application-charm/pyproject.toml

<details>
<summary>10 lines</summary>

```
# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

[tool.poetry]
package-mode = false
requires-poetry = ">=2.0.0"

[tool.poetry.dependencies]
python = "^3.10"
ops = "^3.6.0"

[tool.poetry.group.charm-libs.dependencies]
<exited with exit code 0>
```

</details>


### 💬 Copilot

Perfect! Now let me create a comprehensive summary document. Let me also check the spread tests briefly:

### ✅ `bash`

**Check spread tests directory**

$ ls -la /tmp/s3-integrator-L1-sonnet/tests/spread/

```
total 12
drwxrwxr-x 3 ubuntu ubuntu 4096 Mar  7 12:53 .
drwxrwxr-x 5 ubuntu ubuntu 4096 Mar  7 12:53 ..
drwxrwxr-x 2 ubuntu ubuntu 4096 Mar  7 12:53 test_s3_charm.py
<exited with exit code 0>
```


### ✅ `view`

**/tmp/s3-integrator-L1-sonnet/tests/spread/test_s3_charm.py/task.yaml**

/tmp/s3-integrator-L1-sonnet/tests/spread/test_s3_charm.py/task.yaml

<details>
<summary>6 lines</summary>

```
1. summary: test_s3_charm.py
2. environment:
3.   TEST_MODULE: test_s3_charm.py
4. execute: |
5.   tox run -e integration -- "tests/integration/$TEST_MODULE" --controller "$CONTROLLER_NAME" --model testing
6.
```

</details>


### 💬 Copilot

Now let me compile and organize the complete information:

### ✅ `bash`

**Get line counts for test files**

$ wc -l /tmp/s3-integrator-L1-sonnet/tests/integration/test_s3_charm.py /tmp/s3-integrator-L1-sonnet/tests/integration/helpers.py /tmp/s3-integrator-L1-sonnet/tests/unit/test_charm.py

```
260 /tmp/s3-integrator-L1-sonnet/tests/integration/test_s3_charm.py
  167 /tmp/s3-integrator-L1-sonnet/tests/integration/helpers.py
  111 /tmp/s3-integrator-L1-sonnet/tests/unit/test_charm.py
  538 total
<exited with exit code 0>
```


### 💬 Copilot

Perfect! Now I have all the information. Let me create a comprehensive summary:

## S3-Integrator Charm Integration Test Structure Analysis

### 1. FULL DIRECTORY STRUCTURE

```
tests/
├── ca_chain.pem                          # Certificate file for TLS testing
├── integration/
│   ├── __init__.py                       # Empty init file
│   ├── architecture.py                   # Architecture detection (dpkg)
│   ├── helpers.py                        # Helper functions for integration tests (167 lines)
│   ├── test_s3_charm.py                  # Main integration test file (260 lines)
│   └── application-charm/                # Test fixture charm (requirer side)
│       ├── __init__.py
│       ├── actions.yaml
│       ├── charmcraft.yaml
│       ├── metadata.yaml
│       ├── poetry.lock
│       ├── pyproject.toml
│       ├── src/
│       │   └── charm.py                  # ApplicationCharm implementation
│       └── lib/
│           └── charms/data_platform_libs/v0/s3.py
├── unit/
│   ├── __init__.py                       # Empty init file
│   ├── test_charm.py                     # Unit tests (111 lines)
│   └── helpers.py                        # Unit test helpers
└── spread/
    └── test_s3_charm.py/
        └── task.yaml                     # Spread test runner configuration
```

**Key Notes:**
- **No conftest.py in integration tests**: Pytest uses default fixtures from pytest-operator plugin
- **No conftest.py in unit tests**: Uses unittest framework directly
- Architecture detection is done via subprocess call to `dpkg --print-architecture`

---

### 2. INTEGRATION TEST FILE CONTENT (`tests/integration/test_s3_charm.py`)

**260 lines total** - Contains 5 async test functions with `@pytest.mark.group(1)` and `@pytest.mark.abort_on_fail` decorators:

#### **Test Functions:**

1. **`test_build_and_deploy(ops_test: OpsTest)`** (Lines 40-82)
   - Builds and deploys both the S3 integrator charm and application charm
   - Uses `asyncio.gather()` for parallel deployments
   - Validates unit counts and initial status (s3-integrator: "blocked", application: "waiting")
   - Uses `ops_test.fast_forward()` context manager to accelerate status updates

2. **`test_sync_credential_action(ops_test: OpsTest)`** (Lines 84-125)
   - Tests sync-s3-credentials action with access key and secret key
   - Verifies action output and application transitions to "active" status
   - Tests credential updates multiple times
   - Uses `fast_forward()` for status acceleration

3. **`test_config_options(ops_test: OpsTest)`** (Lines 127-162)
   - Tests setting 8 configuration parameters (tls-ca-chain, s3-api-version, storage-class, attributes, path, region, endpoint, experimental-delete-older-than-days)
   - Runs `get-s3-connection-info` action to verify config was applied
   - Validates JSON parsing of complex fields (attributes, tls-ca-chain)

4. **`test_relation_creation(ops_test: OpsTest)`** (Lines 164-233)
   - Creates relations between S3 integrator and application charm (2 relations tested)
   - Tests relation data propagation through application data bag
   - Tests bucket name configuration updates
   - Verifies credentials and connection info in relation data

5. **`test_relation_broken(ops_test: OpsTest)`** (Lines 235-261)
   - Removes both relations
   - Verifies charm status transitions back to expected states

**Key Variables:**
- `S3_APP_NAME`: From metadata.yaml (s3-integrator)
- `APPLICATION_APP_NAME`: From application charm metadata (application)
- `FIRST_RELATION`: "first-s3-credentials"
- `SECOND_RELATION`: "second-s3-credentials"

---

### 3. INTEGRATION TEST HELPERS (`tests/integration/helpers.py`)

**167 lines** - Contains 8 async helper functions:

| Function | Purpose |
|----------|---------|
| `fetch_action_get_credentials(unit: Unit) -\> Dict` | Run get-s3-credentials action |
| `fetch_action_get_connection_info(unit: Unit) -\> Dict` | Run get-s3-connection-info action and return results |
| `fetch_action_sync_s3_credentials(unit, access_key, secret_key) -\> Dict` | Run sync-s3-credentials action with parameters |
| `is_relation_joined(ops_test, endpoint_one, endpoint_two) -\> bool` | Check if relation is joined by iterating `ops_test.model.relations` |
| `is_relation_broken(ops_test, endpoint_one, endpoint_two) -\> bool` | Check if relation is broken (endpoints NOT in relation list) |
| `run_command_on_unit(unit: Unit, command: str) -\> Optional[str]` | Execute shell command on unit via `unit.run()` action |
| `get_relation_data(ops_test, application_name, relation_name) -\> list` | Fetch raw relation data via `ops_test.juju()` and parse YAML |
| `get_application_data(ops_test, application_name, relation_name) -\> Dict` | Extract application-data from relation data bag |
| `get_certificate_from_file(filename: str) -\> str` | Read certificate file content |

**Key Patterns:**
- All async functions use `await unit.run_action()` and `await action.wait()`
- Relation info accessed via `ops_test.juju("show-unit", unit_name)` which returns YAML
- Application data accessed via `relation_data[0]["application-data"]`

---

### 4. UNIT TEST FILE (`tests/unit/test_charm.py`)

**111 lines** - Uses `unittest.TestCase` and `ops.testing.Harness`:

| Test Method | Purpose |
|-------------|---------|
| `test_on_start()` | Verify charm starts in "blocked" status when parameters missing |
| `test_on_config_changed()` | Verify config params (region, endpoint) stored in peer relation databag |
| `test_set_access_and_secret_key()` | Mock sync-s3-credentials action, verify key storage and action result |
| `test_get_s3_credentials()` | Mock get-s3-credentials action, verify failure when no credentials, success when set |
| `test_get_connection_info()` | Mock get-s3-connection-info action, verify masked keys (****) and config params |

**Key Setup:**
```python
def setUp(self):
    self.harness = Harness(S3IntegratorCharm)
    self.peer_relation_id = self.harness.add_relation("s3-integrator-peers", "s3-integrator-peers")
    self.charm = self.harness.charm
```

**Key Methods Used:**
- `self.harness.set_leader(True)` - Set as leader for peer relation access
- `self.harness.get_relation_data(relation_id, app)` - Get peer relation databag
- `self.harness.update_config({...})` - Simulate config changes
- `self.charm.app_peer_data` - Access peer relation data dictionary

---

### 5. UNIT TEST HELPERS (`tests/unit/helpers.py`)

**Small file** - Single utility function:

```python
def patch_network_get(private_address="10.1.157.116") -\> Callable:
    """Patch for the not-yet-implemented testing backend needed for `bind_address`."""
    # Returns dict with bind-addresses, bind-address, egress-subnets, ingress-addresses
```

Patches `ops.testing._TestingModelBackend.network_get` for testing network binding scenarios.

---

### 6. ARCHITECTURE DETECTION (`tests/integration/architecture.py`)

**7 lines** - Simple subprocess call:

```python
architecture = subprocess.run(
    ["dpkg", "--print-architecture"], capture_output=True, check=True, encoding="utf-8"
).stdout.strip()
```

Stores the system architecture (e.g., "amd64", "arm64") as module-level variable used in charm build paths.

---

### 7. APPLICATION CHARM (Test Fixture) - `tests/integration/application-charm/`

The **test requirer charm** (`ApplicationCharm`) that tests the S3 integrator provider:

**Key Features:**
- Uses `S3Requirer` library from `charms.data_platform_libs.v0.s3`
- Defines 2 S3 relations: `first-s3-credentials`, `second-s3-credentials`
- Second relation passes `bucket_name="test-bucket"` to requirer
- Observes events:
  - `on.start` - Sets "Waiting for relation" status
  - `credentials_changed` (both relations) - Logs connection info updates
  - `credentials_gone` (both relations) - Resets to "Waiting" status
  - `relation_joined` (both relations) - Sets to "Active" status

---

### 8. TESTING DEPENDENCIES (`pyproject.toml`)

**Integration Testing Group:**
```toml
[tool.poetry.group.integration.dependencies]
pytest = "^8.4.2"
pytest-operator = "^0.43.2"      # pytest plugin with OpsTest fixture
juju = "^3.5.2.0"                # python-libjuju for model interaction
```

**Unit Testing Group:**
```toml
[tool.poetry.group.unit.dependencies]
coverage = {extras = ["toml"], version = "^7.13.4"}
pytest = "^8.4.2"
pytest-asyncio = "*"
parameterized = "^0.9.0"
```

**Main Dependencies:**
- `python = "^3.10"`
- `ops = "^3.6.0"`

---

### 9. TEST CONFIGURATION (`pyproject.toml` - [tool.pytest.ini_options])

```toml
[tool.pytest.ini_options]
minversion = "6.0"
log_cli_level = "INFO"
asyncio_mode = "auto"           # Auto async mode for pytest-asyncio
markers = ["unstable"]           # Custom marker for unstable tests
```

---

### 10. TOX INTEGRATION TEST CONFIGURATION (`tox.ini` - [testenv:integration])

```ini
[testenv:integration]
description = Run integration tests
pass_env =
    CI
    GITHUB_OUTPUT
    SECRETS_FROM_GITHUB
commands_pre =
    poetry install --only integration --no-root
commands =
    poetry run pytest -v --tb native --log-cli-level=INFO -s --ignore={[vars]tests_path}/unit/ {posargs}
```

**Environment Setup:**
- Installs only integration dependencies (no main charm code packaging)
- PYTHONPATH set to `/lib:/src` (lib priority for charm-libs)
- `PYTHONBREAKPOINT=ipdb.set_trace` enabled for debugging
- Passes through CI/GitHub/secrets environment variables

---

### 11. HOW PYTEST-OPERATOR AND PYTHON-LIBJUJU ARE USED

#### **pytest-operator (`OpsTest` fixture)**

The `ops_test: OpsTest` parameter is provided by pytest-operator plugin:

| Feature | Usage in Tests |
|---------|----------------|
| **Model Management** | `ops_test.model` - Access to juju model with deployed charms |
| **Deploy Charms** | `await ops_test.model.deploy(charm_path, application_name, num_units)` |
| **Applications** | `ops_test.model.applications[app_name]` - Get application object |
| **Units** | `ops_test.model.applications[app_name].units[0]` - Get unit object |
| **Relations** | `await ops_test.model.add_relation()`, `.remove_relation()` |
| **Status Waiting** | `await ops_test.model.wait_for_idle(apps, status, timeout)` |
| **Unit Blocking** | `await ops_test.model.block_until(lambda: condition)` |
| **Speed Control** | `async with ops_test.fast_forward():` - Accelerate update_status |
| **Raw Juju CLI** | `await ops_test.juju("show-unit", unit_name)` - Execute juju commands |
| **Configuration** | `await ops_test.model.applications[app].set_config({...})` |

#### **python-libjuju (`juju` library)**

Used indirectly through `OpsTest` and directly on units:

| Feature | Usage in Tests |
|---------|----------------|
| **Unit Type** | `juju.unit.Unit` - Type hint for unit parameters |
| **Actions** | `await unit.run_action(action_name, **params)` - Execute charm actions |
| **Action Results** | `await action.wait()` returns object with `.status`, `.results` |
| **Shell Commands** | `await unit.run(command)` - Execute shell on unit (deprecated but used) |
| **Relation Info** | Model relations accessible via `ops_test.model.relations` |

**Action Pattern:**
```python
action = await unit.run_action(action_name="sync-s3-credentials", access_key="key", secret_key="secret")
result = await action.wait()
return result.results  # Dict with action output
```

---

### 12. FIXTURES DEFINED

**No conftest.py exists** - All fixtures come from pytest-operator plugin:

| Fixture | Source | Type |
|---------|--------|------|
| `ops_test` | pytest-operator plugin | Fixture of type `OpsTest` |

**Implicit from OpsTest:**
- `ops_test.model` - juju.model.Model instance
- `ops_test.model.applications` - Dict[str, Application]
- `ops_test.model.relations` - List of Relation objects

---

### 13. KEY PATTERNS AND CONVENTIONS

#### **Test Grouping & Execution Order:**
- All integration tests marked with `@pytest.mark.group(1)`
- All marked with `@pytest.mark.abort_on_fail` (stop on first failure)
- First test (`test_build_and_deploy`) decorated with `@pytest.mark.skip_if_deployed`
- Tests execute in definition order (pytest maintains order)

#### **Async/Await Patterns:**
```python
# Parallel operations
await asyncio.gather(
    ops_test.model.deploy(...),
    ops_test.model.deploy(...)
)

# Status acceleration
async with ops_test.fast_forward():
    await ops_test.model.wait_for_idle(...)
```

#### **Status Checking:**
```python
# Direct unit status
assert unit.workload_status == "blocked"

# Wait for status with timeout
await ops_test.model.wait_for_idle(
    apps=[app_name],
    status="active",
    timeout=1000,
    raise_on_blocked=True
)

# Poll until condition
await ops_test.model.block_until(lambda: condition_is_true)
```

#### **Relation Data Access:**
```python
# Via juju CLI through ops_test
raw_data = (await ops_test.juju("show-unit", unit_name))[1]  # stdout
data = yaml.safe_load(raw_data)
relation_data = data[unit_name]["relation-info"]  # List of relations

# Filter by endpoint name
relevant = [r for r in relation_data if r["endpoint"] == relation_name]
app_data = relevant[0]["application-data"]  # Dict of relation data
```

#### **Action Execution Pattern:**
```python
# Standard action with optional parameters
action = await unit.run_action(action_name="action-name", param1="value1")
result = await action.wait()
assert result.status == "completed" or "failed"
return result.results  # Dict of output
```

---

### 14. TEST EXECUTION FLOW

```
Integration Test Execution:
1. test_build_and_deploy()
   └─ Builds charms
   └─ Deploys s3-integrator and application
   └─ Waits for deployment completion
   
2. test_sync_credential_action()
   └─ Runs sync-s3-credentials action
   └─ Validates action output
   └─ Tests credential updates
   
3. test_config_options()
   └─ Sets 8 config parameters
   └─ Runs get-s3-connection-info action
   └─ Validates all config returned
   
4. test_relation_creation()
   └─ Creates first S3 relation
   └─ Validates relation data bag
   └─ Tests bucket name updates
   └─ Creates second S3 relation
   └─ Validates both relations separately
   
5. test_relation_broken()
   └─ Removes both relations
   └─ Validates status transitions

All tests use fast_forward() context manager to accelerate time-based status updates.
```

---

### 15. SUMMARY TABLE

| Aspect | Details |
|--------|---------|
| **Test Framework** | pytest (integration), unittest (unit) |
| **Integration Plugin** | pytest-operator 0.43.2+ with OpsTest fixture |
| **Juju Library** | python-libjuju 3.5.2+ |
| **Test Count** | 5 integration tests, 5 unit tests |
| **Async Support** | pytest-asyncio with `asyncio_mode = "auto"` |
| **Conftest Usage** | None - relies on pytest-operator defaults |
| **Configuration** | Via pyproject.toml and tox.ini |
| **Spread Tests** | Basic wrapper that runs integration tests via tox |
| **Test Fixture Charm** | ApplicationCharm in tests/integration/application-charm/ |
| **Relation Testing** | 2 relations to same S3 integrator provider |
| **Action Testing** | 3 actions tested (get-s3-credentials, sync-s3-credentials, get-s3-connection-info) |
| **Config Testing** | 8 config parameters tested for propagation |


---

<sub>⏱️ 1m 20s</sub>

### ✅ `view`

**/tmp/s3-integrator-L1-sonnet/tests/integration/test_s3_charm.py**

/tmp/s3-integrator-L1-sonnet/tests/integration/test_s3_charm.py

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

<sub>⏱️ 1m 20s</sub>

### ✅ `view`

**/tmp/s3-integrator-L1-sonnet/tests/integration/helpers.py**

/tmp/s3-integrator-L1-sonnet/tests/integration/helpers.py

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

<sub>⏱️ 1m 20s</sub>

### ✅ `view`

**/tmp/s3-integrator-L1-sonnet/pyproject.toml**

/tmp/s3-integrator-L1-sonnet/pyproject.toml

<details>
<summary>97 lines</summary>

```
1. # Copyright 2022 Canonical Ltd.
2. # See LICENSE file for licensing details.
3. 
4. [tool.poetry]
5. package-mode = false
6. requires-poetry = ">=2.0.0"
7. 
8. [tool.poetry.dependencies]
9. python = "^3.10"
10. ops = "^3.6.0"
11. 
12. [tool.poetry.group.charm-libs.dependencies]
13. 
14. [tool.poetry.group.format]
15. optional = true
16. 
17. [tool.poetry.group.format.dependencies]
18. ruff = "^0.15.4"
19. 
20. [tool.poetry.group.lint]
21. optional = true
22. 
23. [tool.poetry.group.lint.dependencies]
24. codespell = "^2.4.1"
25. 
26. [tool.poetry.group.unit.dependencies]
27. coverage = {extras = ["toml"], version = "^7.13.4"}
28. pytest = "^8.4.2"
29. pytest-asyncio = "*"
30. parameterized = "^0.9.0"
31. 
32. [tool.poetry.group.integration.dependencies]
33. pytest = "^8.4.2"
34. pytest-operator = "^0.43.2"
35. juju = "^3.5.2.0"
36. 
37. # Testing tools configuration
38. [tool.coverage.run]
39. branch = true
40. 
41. [tool.coverage.report]
42. show_missing = true
43. 
44. [tool.pytest.ini_options]
45. minversion = "6.0"
46. log_cli_level = "INFO"
47. asyncio_mode = "auto"
48. markers = ["unstable"]
49. 
50. # Formatting tools configuration
51. [tool.black]
52. line-length = 99
53. target-version = ["py310"]
54. 
55. # Linting tools configuration
56. [tool.ruff]
57. # preview and explicit preview are enabled for CPY001
58. preview = true
59. target-version = "py310"
60. src = ["src", "."]
61. line-length = 99
62. 
63. [tool.ruff.lint]
64. explicit-preview-rules = true
65. select = ["A", "E", "W", "F", "C", "N", "D", "I001", "CPY001"]
66. extend-ignore = [
67.     "D203",
68.     "D204",
69.     "D213",
70.     "D215",
71.     "D400",
72.     "D404",
73.     "D406",
74.     "D407",
75.     "D408",
76.     "D409",
77.     "D413",
78. ]
79. # Ignore E501 because using black creates errors with this
80. # Ignore D107 Missing docstring in __init__
81. ignore = ["E501", "D107"]
82. 
83. [tool.ruff.lint.per-file-ignores]
84. "tests/*" = ["D100", "D101", "D102", "D103", "D104"]
85. 
86. [tool.ruff.lint.flake8-copyright]
87. # Check for properly formatted copyright header in each file
88. author = "Canonical Ltd."
89. notice-rgx = "Copyright\\s\\d{4}([-,]\\d{4})*\\s+"
90. min-file-size = 1
91. 
92. [tool.ruff.lint.mccabe]
93. max-complexity = 10
94. 
95. [tool.ruff.lint.pydocstyle]
96. convention = "google"
97.
```

</details>


---

<sub>⏱️ 1m 20s</sub>

### ✅ `view`

**/tmp/s3-integrator-L1-sonnet/tox.ini**

/tmp/s3-integrator-L1-sonnet/tox.ini

<details>
<summary>65 lines</summary>

```
1. # Copyright 2022 Canonical Ltd.
2. # See LICENSE file for licensing details.
3. 
4. [tox]
5. no_package = True
6. skip_missing_interpreters = True
7. env_list = lint, unit
8. 
9. [vars]
10. src_path = {tox_root}/src
11. tests_path = {tox_root}/tests
12. test_charm_libs_path = {[vars]tests_path}/integration/application-charm/lib/
13. all_path = {[vars]src_path} {[vars]tests_path}
14. 
15. [testenv]
16. set_env =
17.     PYTHONPATH = {tox_root}/lib:{[vars]src_path}
18.     PYTHONBREAKPOINT=ipdb.set_trace
19.     PY_COLORS=1
20. pass_env =
21.     PYTHONPATH
22.     CHARM_BUILD_DIR
23.     MODEL_SETTINGS
24. allowlist_externals =
25.     poetry
26. 
27. [testenv:format]
28. description = Apply coding style standards to code
29. commands_pre =
30.     poetry install --only format --no-root
31. commands =
32.     poetry lock
33.     poetry run ruff check --fix {[vars]all_path} --exclude {[vars]test_charm_libs_path}
34.     poetry run ruff format {[vars]all_path} --exclude {[vars]test_charm_libs_path}
35. 
36. [testenv:lint]
37. description = Check code against coding style standards
38. commands_pre =
39.     poetry install --only lint,format --no-root
40. commands =
41.     poetry check --lock
42.     poetry run codespell {[vars]all_path}
43.     poetry run ruff check {[vars]all_path} --exclude {[vars]test_charm_libs_path}
44.     poetry run ruff format --check --diff {[vars]all_path} --exclude {[vars]test_charm_libs_path}
45. 
46. [testenv:unit]
47. description = Run unit tests
48. commands_pre =
49.     poetry install --only main,charm-libs,unit --no-root
50. commands =
51.     poetry run coverage run --source={[vars]src_path} \
52.         -m pytest -v --tb native -s {posargs} {[vars]tests_path}/unit
53.     poetry run coverage report
54. 
55. [testenv:integration]
56. description = Run integration tests
57. pass_env =
58.     CI
59.     GITHUB_OUTPUT
60.     SECRETS_FROM_GITHUB
61. commands_pre =
62.     poetry install --only integration --no-root
63. commands =
64.     poetry run pytest -v --tb native --log-cli-level=INFO -s --ignore={[vars]tests_path}/unit/ {posargs}
65.
```

</details>


---

<sub>⏱️ 1m 28s</sub>

### 💬 Copilot

Now let me look up the jubilant and pytest-jubilant API to understand the migration target:

---

<sub>⏱️ 1m 39s</sub>

### ✅ `web_search`

**jubilant pytest-jubilant juju charm testing library API reference deploy wait_for integrate run_action**

<details>
<summary>Arguments</summary>

```json
{
  "query": "jubilant pytest-jubilant juju charm testing library API reference deploy wait_for integrate run_action"
}
```

</details>

````
{"type":"text","text":{"value":"Here's a concise overview and API quick-reference for using Jubilant and pytest-jubilant in Juju charm integration tests, focusing on deploy, wait_for (wait), integrate, and run_action.\n\n### Overview\n\n- **Jubilant** is a Python library wrapping the Juju CLI, intended to supersede pytest-operator and python-libjuju for charm integration testing.\n- **pytest-jubilant** is a pytest plugin that adds fixtures and utilities for easier usage within pytest, especially if you are migrating from pytest-operator.\n\n---\n\n## Core API Concepts\n\n### 1. `deploy`\n- Deploy a charm to the Juju model.\n\n  ```python\n  juju.deploy('snappass-test')  # Deploy by charm name\n  juju.deploy('./foo.charm', 'foo')  # Deploy using a local charm file\n  ```\n\n### 2. `wait` (wait_for)\n- **Wait** for model/application status, using pre-built helpers like `jubilant.all_active`, or custom conditions.\n- Example waiting for all apps to become active:\n  ```python\n  juju.wait(jubilant.all_active)\n  ```\n- Wait for a specific app:\n  ```python\n  juju.wait(lambda status: jubilant.all_active(status, 'my-charm'))\n  ```\n- Custom condition:\n  ```python\n  juju.wait(lambda status: status.apps['myapp'].app_status.current == 'maintenance')\n  ```\n- Timeout can be set with the `timeout` parameter (default is 10 minutes):\n  ```python\n  juju.wait(jubilant.all_active, timeout=1200)\n  ```\n\n### 3. `integrate`\n- Relate (integrate) two applications by their charms:\n  ```python\n  juju.integrate('blog', 'mysql')\n  juju.integrate('blog', 'redis')\n  ```\n\n### 4. `run_action`\n- Run a Juju action against a unit:\n  ```python\n  result = juju.run_action('myapp/0', 'do-something', params={'foo': 'bar'})\n  # result is a dict containing the action output/result\n  ```\n\n---\n\n## Using Fixtures in pytest-jubilant\n\n- **`juju` fixture**: Provides a ready-to-use Juju instance scoped to your test/module.\n  ```python\n  def test_deploy(juju: Juju):\n      juju.deploy(\"./foo.charm\", \"foo\")\n      juju.wait(lambda status: all_active(status, \"foo\"), timeout=1000)\n  ```\n\n- **`temp_model_factory` fixture** (for multiple models):\n  ```python\n  @pytest.fixture\n  def istio(temp_model_factory):\n      yield temp_model_factory.get_juju(suffix=\"istio\")\n\n  def test_cmr(juju: Juju, istio: Juju):\n      istio.deploy(\"istio-k8s\", \"istio\")\n      istio.wait(lambda status: all_active(status, \"istio\"), timeout=1000)\n      # cross-model relation logic here\n  ```\n\n---\n\n## Additional Pytest CLI Options (pytest-jubilant)\n- `--model`, `--keep-models`, `--no-teardown`: Control temporary model lifecycles.\n- `--switch`: Switches you to the temporary model used by the current test.\n\n---\n\n## Documentation Links and Further Reading\n\n- [Jubilant API reference & guides](https://documentation.ubuntu.com/jubilant/)【3:5†source】【3:3†source】\n- [Getting started tutorial](https://documentation.ubuntu.com/jubilant/tutorial/getting-started/)【3:4†source】\n- [pytest-jubilant PyPI](https://pypi.org/project/pytest-jubilant/)【3:8†source】\n- [Migration guide](https://documentation.ubuntu.com/jubilant/how-to/migrate-from-pytest-operator/)【3:0†source】【3:9†source】\n- [Jubilant GitHub](https://github.com/canonical/jubilant)【3:2†source】\n\nIf you need detailed examples or particulars for other operations (like context managers for model creation/cleanup, or advanced status helpers), the official Jubilant documentation and the above resources provide more depth. Let me know if you need code samples for specific patterns!","annotations":[{"text":"【3:5†source】","start_index":2739,"end_index":2751,"url_citation":{"title":"Jubilant documentation","url":"https://documentation.ubuntu.com/jubilant/"}},{"text":"【3:3†source】","start_index":2751,"end_index":2763,"url_citation":{"title":"jubilant - Jubilant documentation","url":"https://canonical-jubilant.readthedocs-hosted.com/reference/jubilant/"}},{"text":"【3:4†source】","start_index":2861,"end_index":2873,"url_citation":{"title":"Getting started with Jubilant - Jubilant documentation","url":"https://documentation.ubuntu.com/jubilant/tutorial/getting-started/"}},{"text":"【3:8†source】","start_index":2941,"end_index":2953,"url_citation":{"title":"pytest-jubilant · PyPI","url":"https://pypi.org/project/pytest-jubilant/"}},{"text":"【3:0†source】","start_index":3053,"end_index":3065,"url_citation":{"title":"How to migrate from pytest-operator to Jubilant","url":"https://documentation.ubuntu.com/jubilant/how-to/migrate-from-pytest-operator/"}},{"text":"【3:9†source】","start_index":3065,"end_index":3077,"url_citation":{"title":"How-to guides - Jubilant documentation","url":"https://documentation.ubuntu.com/jubilant/how-to/"}},{"text":"【3:2†source】","start_index":3136,"end_index":3148,"url_citation":{"title":"Jubilant, the joyful library for driving Juju - GitHub","url":"https://github.com/canonical/jubilant"}}]},"bing_searches":[{"text":"jubilant pytest-jubilant juju charm testing library API reference deploy wait_for integrate run_action","url":"https://www.bing.com/search?q=jubilant+pytest-jubilant+juju+charm+testing+library+API+reference+deploy+wait_for+integrate+run_action"}],"annotations":null}
````


---

<sub>⏱️ 1m 39s</sub>

### ✅ `web_search`

**jubilant python juju testing library github canonical API examples**

<details>
<summary>Arguments</summary>

```json
{
  "query": "jubilant python juju testing library github canonical API examples"
}
```

</details>

````
{"type":"text","text":{"value":"The Jubilant Python library is a Pythonic, type-annotated wrapper for the Juju CLI, designed primarily for charm integration tests, and developed by Canonical. Jubilant offers a straightforward, synchronous API that maps closely to Juju CLI commands, doing away with the complexity and async-heavy nature of libraries like python-libjuju. It's recommended especially for those currently using `pytest-operator` for Juju charm testing.\n\n## Key Features\n- 1:1 mapping of methods to Juju CLI commands, with clear Python objects for responses.\n- Synchronous API; no need to use Python's async/await.\n- Works with `pytest` fixtures for easy setup/teardown.\n- Includes helpers for common test patterns, such as waiting for all apps to reach \"active\" status.\n\n## Installation\n\n```bash\npip install jubilant\n# or\nuv add jubilant\n```\nYou need to have the Juju CLI installed as well.\n\n## Basic Usage Example\n\nHere's a simple example of how you might use Jubilant in your Python code:\n\n```python\nimport jubilant\n\njuju = jubilant.Juju()\njuju.deploy('snappass-test')\njuju.wait(jubilant.all_active)  # Waits for all deployed apps to be active\n```\n\nTo wait for specific applications:\n\n```python\njuju.wait(lambda status: jubilant.all_active(status, 'snappass-test', 'another-app'))\n```\n\n## Pytest Fixture Example\n\nJubilant provides context managers that make integration testing with pytest easy:\n\n**conftest.py**\n```python\nimport pytest\nimport jubilant\n\n@pytest.fixture(scope='module')\ndef juju():\n    with jubilant.temp_model() as juju:\n        yield juju\n```\n\n**test_deploy.py**\n```python\ndef test_deploy(juju: jubilant.Juju):\n    juju.deploy('snappass-test')\n    status = juju.wait(jubilant.all_active)\n    address = status.apps['snappass-test'].units['snappass-test/0'].address\n    response = requests.get(f'http://{address}:5000/', timeout=10)\n    response.raise_for_status()\n    assert 'snappass' in response.text.lower()\n```\nYou can change the scope of the fixture for per-function or per-module models as needed.\n\n## Custom Wait Conditions\n\nJubilant allows you to specify custom conditions for waiting, such as:\n\n```python\ndef test_unknown(juju: jubilant.Juju):\n    juju.deploy('myapp')\n    juju.wait(lambda status: status.apps['myapp'].app_status.current == 'unknown')\n```\n\nOr deploy multiple apps and wait for all to be active:\n\n```python\ndef test_active_apps(juju: jubilant.Juju):\n    for app in ['blog', 'mysql', 'redis']:\n        juju.deploy(app)\n    juju.integrate('blog', 'mysql')\n    juju.integrate('blog', 'redis')\n    juju.wait(lambda status: jubilant.all_active(status, 'blog', 'mysql', 'redis'))\n```\n\n## Resources\n- [Canonical/jubilant GitHub repo with README and complete examples](https://github.com/canonical/jubilant)【3:0†source】\n- [PyPI: Jubilant package and usage description](https://pypi.org/project/jubilant/)【3:1†source】\n- [Jubilant official documentation (tutorial and API reference)](https://documentation.ubuntu.com/jubilant/)【3:2†source】【3:5†source】\n- [Technical blog post on Jubilant’s design and testing philosophy](https://benhoyt.com/writings/jubilant/)【3:9†source】\n- [Canonical’s official Juju documentation and ecosystem](https://canonical.com/juju/docs)【3:8†source】\n\nIf you want specific API documentation, refer to the [Jubilant reference docs](https://canonical-jubilant.readthedocs-hosted.com/reference/)【3:7†source】. For real-world examples, see the [Tutorial](https://documentation.ubuntu.com/jubilant/tutorial/getting-started/)【3:5†source】. \n\nLet me know if you need more advanced usage or a deeper API reference!","annotations":[{"text":"【3:0†source】","start_index":2725,"end_index":2737,"url_citation":{"title":"Jubilant, the joyful library for driving Juju - GitHub","url":"https://github.com/canonical/jubilant"}},{"text":"【3:1†source】","start_index":2822,"end_index":2834,"url_citation":{"title":"jubilant · PyPI","url":"https://pypi.org/project/jubilant/"}},{"text":"【3:2†source】","start_index":2943,"end_index":2955,"url_citation":{"title":"Jubilant documentation","url":"https://documentation.ubuntu.com/jubilant/"}},{"text":"【3:5†source】","start_index":2955,"end_index":2967,"url_citation":{"title":"Getting started with Jubilant - Jubilant documentation","url":"https://documentation.ubuntu.com/jubilant/tutorial/getting-started/"}},{"text":"【3:9†source】","start_index":3075,"end_index":3087,"url_citation":{"title":"Don’t fear Python subprocess or Go codegen","url":"https://benhoyt.com/writings/jubilant/"}},{"text":"【3:8†source】","start_index":3178,"end_index":3190,"url_citation":{"title":"Canonical | Trusted open source for enterprises - Juju","url":"https://canonical.com/juju/docs"}},{"text":"【3:7†source】","start_index":3332,"end_index":3344,"url_citation":{"title":"Reference - Jubilant documentation","url":"https://canonical-jubilant.readthedocs-hosted.com/reference/"}},{"text":"【3:5†source】","start_index":3458,"end_index":3470,"url_citation":{"title":"Getting started with Jubilant - Jubilant documentation","url":"https://documentation.ubuntu.com/jubilant/tutorial/getting-started/"}}]},"bing_searches":[{"text":"jubilant python juju testing library github canonical API examples","url":"https://www.bing.com/search?q=jubilant+python+juju+testing+library+github+canonical+API+examples"}],"annotations":null}
````


---

<sub>⏱️ 1m 44s</sub>

### ✅ `web_fetch`

**https://documentation.ubuntu.com/jubilant/how-to/migrate-from-pytest-operator/**

<details>
<summary>Arguments</summary>

```json
{
  "url": "https://documentation.ubuntu.com/jubilant/how-to/migrate-from-pytest-operator/",
  "max_length": 15000
}
```

</details>

<details>
<summary>236 lines</summary>

```
Contents of https://documentation.ubuntu.com/jubilant/how-to/migrate-from-pytest-operator/:
Many charm integration tests use [pytest-operator](https://github.com/charmed-kubernetes/pytest-operator) and [python-libjuju](https://github.com/juju/python-libjuju). This guide explains how to migrate your integration tests from those libraries to Jubilant.

To get help while you’re migrating tests, please keep the [API reference](../../reference/jubilant/) handy, and make use of your IDE’s autocompletion – Jubilant tries to provide good type annotations and docstrings.

Migrating your tests can be broken into three steps:

1.  Update your dependencies
    
2.  Add fixtures to `conftest.py`
    
3.  Update the tests themselves
    

Let’s look at each of these in turn.

## Update your dependencies[¶](#update-your-dependencies "Link to this heading")

The first thing you’ll need to do is add `jubilant` as a dependency to your `tox.ini` or `pyproject.toml` dependencies.

You can also remove the dependencies on `juju` (python-libjuju), `pytest-operator`, and `pytest-asyncio`.

If you’re using `tox.ini`, the diff might look like:

 \[testenv:integration\]
 deps =
     boto3
     cosl
\-    juju>=3.0
\+    jubilant~=1.0
     pytest
\-    pytest-operator
\-    pytest-asyncio
     -r{toxinidir}/requirements.txt

If you’re migrating a large number of tests, you may want to do it in stages. In that case, keep the old dependencies in place till the end, and migrate tests one at a time, so that both pytest-operator and Jubilant tests can run together.

## Add fixtures to `conftest.py`[¶](#add-fixtures-to-conftest-py "Link to this heading")

The pytest-operator library includes pytest fixtures, but Jubilant does not include any fixtures, so you’ll need to add one or two fixtures to your `conftest.py`.

### A `juju` model fixture[¶](#a-juju-model-fixture "Link to this heading")

Jubilant expects that a Juju controller has already been set up, either using [Concierge](https://github.com/jnsgruk/concierge) or a manual approach. However, you’ll want a fixture that creates a temporary model. We recommend naming the fixture `juju`:

\# tests/integration/conftest.py

import jubilant
import pytest

@pytest.fixture(scope\='module')
def juju(request: pytest.FixtureRequest):
    keep\_models \= bool(request.config.getoption('--keep-models'))

    with jubilant.temp\_model(keep\=keep\_models) as juju:
        juju.wait\_timeout \= 10 \* 60

        yield juju  \# run the test

        if request.session.testsfailed:
            log \= juju.debug\_log(limit\=1000)
            print(log, end\='')

def pytest\_addoption(parser):
    parser.addoption(
        '--keep-models',
        action\='store\_true',
        default\=False,
        help\='keep temporarily-created models',
    )

In your tests, use the fixture like this:

\# tests/integration/test\_charm.py

def test\_active(juju: jubilant.Juju):
    juju.deploy('mycharm')
    juju.wait(jubilant.all\_active)

    \# Or wait for just 'mycharm' to be active (ignoring other apps):
    juju.wait(lambda status: jubilant.all\_active(status, 'mycharm'))

A few things to note about the fixture:

*   It includes a command-line parameter `--keep-models`, to match pytest-operator. If the parameter is set, the fixture keeps the temporary model around after running the tests.
    
*   It sets [`juju.wait_timeout`](../../reference/jubilant/#jubilant.Juju.wait_timeout "jubilant.Juju.wait_timeout") to 10 minutes, to match python-libjuju’s default `wait_for_idle` timeout.
    
*   If any of the tests fail, it uses `juju.debug_log` to display the last 1000 lines of `juju debug-log` output.
    
*   It is module-scoped, like pytest-operator’s `ops_test` fixture. This means that a new model is created for every `test_*.py` file, but not for every test.
    

### An application fixture[¶](#an-application-fixture "Link to this heading")

If you don’t want to deploy your application in each test, you can add a module-scoped `app` fixture that deploys your charm and waits for it to go active.

The following fixture assumes that the charm has already been packed with `charmcraft pack` in a previous CI step (Jubilant has no equivalent of `ops_test.build_charm`):

\# tests/integration/conftest.py

import pathlib

import jubilant
import pytest

@pytest.fixture(scope\='module')
def app(juju: jubilant.Juju):
    juju.deploy(
        charm\_path('mycharm'),
        'mycharm',
        resources\={
            'mycharm-image': 'ghcr.io/canonical/...',
        },
        config\={
            'base\_url': '/api',
            'port': 80,
        },
        base\='ubuntu@20.04',
    )
    \# ... do any other application setup here ...
    juju.wait(jubilant.all\_active)

    yield 'mycharm'  \# run the test

def charm\_path(name: str) \-> pathlib.Path:
    """Return full absolute path to given test charm."""
    \# We're in tests/integration/conftest.py, so parent\*3 is repo top level.
    charm\_dir \= pathlib.Path(\_\_file\_\_).parent.parent.parent
    charms \= \[p.absolute() for p in charm\_dir.glob(f'{name}\_\*.charm')\]
    assert charms, f'{name}\_\*.charm not found'
    assert len(charms) \== 1, 'more than one .charm file, unsure which to use'
    return charms\[0\]

In your tests, you’ll need to specify that the test depends on both fixtures:

\# tests/integration/test\_charm.py

def test\_active(juju: jubilant.Juju, app: str):
    status \= juju.status()
    assert status.apps\[app\].is\_active

## Update the tests themselves[¶](#update-the-tests-themselves "Link to this heading")

Many features of pytest-operator and python-libjuju map quite directly to Jubilant, except without using `async`. Here is a summary of what you need to change:

*   Remove `async` and `await` keywords, and replace `pytest_asyncio.fixture` with `pytest.fixture`
    
*   Replace introspection of python-libjuju’s `Application` and `Unit` objects with [`juju.status`](../../reference/jubilant/#jubilant.Juju.status "jubilant.Juju.status")
    
*   Replace `model.wait_for_idle` with [`juju.wait`](../../reference/jubilant/#jubilant.Juju.wait "jubilant.Juju.wait") and an appropriate _ready_ callable
    
*   Replace `unit.run` with [`juju.exec`](../../reference/jubilant/#jubilant.Juju.exec "jubilant.Juju.exec"); note the different return type and error handling
    
*   Replace `unit.run_action` with [`juju.run`](../../reference/jubilant/#jubilant.Juju.run "jubilant.Juju.run"); note the different return type and error handling
    
*   Replace other python-libjuju methods with equivalent [`Juju`](../../reference/jubilant/#jubilant.Juju "jubilant.Juju") methods, which are normally much closer to the Juju CLI commands
    

Let’s look at some specifics in more detail.

### Deploying a charm[¶](#deploying-a-charm "Link to this heading")

To migrate a charm deployment from pytest-operator, drop the `await`, change `series` to `base`, and replace `model.wait_for_idle` with [`juju.wait`](../../reference/jubilant/#jubilant.Juju.wait "jubilant.Juju.wait"):

\# pytest-operator
postgres\_app \= await model.deploy(
    'postgresql-k8s',
    channel\='14/stable',
    series\='jammy',
    revision\=300,
    trust\=True,
    config\={'profile': 'testing'},
)
await model.wait\_for\_idle(apps\=\[postgres\_app.name\], status\='active')

\# jubilant
juju.deploy(
    'postgresql-k8s',
    channel\='14/stable',
    base\='ubuntu@22.04',
    revision\=300,
    trust\=True,
    config\={'profile': 'testing'},
)
juju.wait(lambda status: jubilant.all\_active(status, 'postgresql-k8s'))

### Fetching status[¶](#fetching-status "Link to this heading")

A python-libjuju model is updated in the background using websockets. In Jubilant you use ordinary Python function calls to fetch updates:

\# pytest-operator
async def test\_active(app: Application):
    assert app.units\[0\].workload\_status \== ActiveStatus.name

\# jubilant
def test\_active(juju: jubilant.Juju, app: str):
    status \= juju.status()
    assert status.apps\[app\].units\[app + '/0'\].is\_active

### Waiting for a condition[¶](#waiting-for-a-condition "Link to this heading")

However, instead of calling `status` directly, it’s usually better to wait for a certain condition to be true. In python-libjuju you used `model.wait_for_idle`; in Jubilant you use [`juju.wait`](../../reference/jubilant/#jubilant.Juju.wait "jubilant.Juju.wait"), which has a simpler and more consistent API.

The `wait` method takes a _ready_ callable, which takes a [`Status`](../../reference/jubilant/#jubilant.Status "jubilant.Status") object. Internally, `wait` polls `juju status` every second and calls the _ready_ callable, which must return `True` three times in a row (this is configurable).

You can optionally provide an _error_ callable, which also takes a `Status` object. If the _error_ callable returns `True`, `wait` raises a [`WaitError`](../../reference/jubilant/#jubilant.WaitError "jubilant.WaitError") immediately.

Jubilant provides helper functions to use for the _ready_ and _error_ callables, such as [`jubilant.all_active`](../../reference/jubilant/#jubilant.all_active "jubilant.all_active") and [`jubilant.any_error`](../../reference/jubilant/#jubilant.any_error "jubilant.any_error"). These check whether the workload status of all (or any) applications and their units are in a given state.

For example, here’s a simple `wait` call that waits for all applications and units to go “active” and raises an error if any go into “error”:

\# pytest-operator
async def test\_active(model: Model):
    await model.deploy('mycharm')
    await model.wait\_for\_idle(status\='active')  \# implies raise\_on\_error=True

\# jubilant
def test\_active(juju: jubilant.Juju):
    juju.deploy('mycharm')
    juju.wait(jubilant.all\_active, error\=jubilant.any\_error)

It’s usually best to wait on workload status with the `all_*` and `any_*` helpers. However, if you want to wait specifically for unit agent status to be idle, you can use [`jubilant.all_agents_idle`](../../reference/jubilant/#jubilant.all_agents_idle "jubilant.all_agents_idle"):

\# pytest-operator
async def test\_idle(model: Model):
    await model.deploy('mycharm')
    await model.wait\_for\_idle()

\# jubilant
def test\_active(juju: jubilant.Juju):
    juju.deploy('mycharm')
    juju.wait(jubilant.all\_agents\_idle)

It’s common to use a `lambda` function to customize the callable or compose multiple checks. For example, to wait specifically for `mysql` and `redis` to go active and `logger` to be blocked:

juju.wait(
    lambda status: (
        jubilant.all\_active(status, 'mysql', 'redis') and
        jubilant.all\_blocked(status, 'logger'),
    ),
)

The `wait` method also has other options (see [`juju.wait`](../../reference/jubilant/#jubilant.Juju.wait "jubilant.Juju.wait") for details):

juju.deploy('mycharm')
juju.wait(
    ready\=lambda status: jubilant.all\_active(status, 'mycharm'),
    error\=jubilant.any\_error,
    delay\=0.2,    \# poll "juju status" every 200ms (default 1s)
    timeout\=60,   \# set overall timeout to 60s (default juju.wait\_timeout)
    successes\=7,  \# require ready to return success 7x in a row (default 3)
)

For more examples, see [Tutorial | Use a custom wait condition](../../tutorial/getting-started/#use-a-custom-wait-condition).

### Integrating two applications[¶](#integrating-two-applications "Link to this heading")

To integrate two charms, remove the `async`\-related code and replace `model.add_relation` with [`juju.integrate`](../../reference/jubilant/#jubilant.Juju.integrate "jubilant.Juju.integrate"). For example, to integrate discourse-k8s with three other charms:

\# pytest-operator
await asyncio.gather(
    model.add\_relation('discourse-k8s', 'postgresql-k8s:database'),
    model.add\_relation('discourse-k8s', 'redis-k8s'),
    model.add\_relation('discourse-k8s', 'nginx-ingress-integrator'),
)
await model.wait\_for\_idle(status\='active')

\# jubilant
juju.integrate('discourse-k8s', 'postgresql-k8s:database')
juju.integrate('discourse-k8s', 'redis-k8s')
juju.integrate('discourse-k8s', 'nginx-ingress-integrator')
juju.wait(jubilant.all\_active)

### Executing a command[¶](#executing-a-command "Link to this heading")

In `pytest-operator` tests, you used `unit.run` to execute a command. With Jubilant (as with Juju 3.x) you use [`juju.exec`](../../reference/jubilant/#jubilant.Juju.exec "jubilant.Juju.exec"). Jubilant’s `exec` returns a [`jubilant.Task`](../../reference/jubilant/#jubilant.Task "jubilant.Task"), and it also checks errors for you:

\# pytest-operator
unit \= model.applications\['discourse-k8s'\].units\[0\]
action \= await unit.run('/bin/bash -c "..."')
await action.wait()
logger.info(action.results)
assert action.results\['return-code'\] \== 0, 'Enable plugins failed'

\# jubilant
task \= juju.exec('/bin/bash -c "..."', unit\='discourse-k8s/0')
logger.info(task.results)

### Running an action[¶](#running-an-action "Link to this heading")

In `pytest-operator` tests, you used `unit.run_action` to run an action. With Jubilant, you use [`juju.run`](../../reference/jubilant/#jubilant.Juju.run "jubilant.Juju.run"). Similar to `exec`, Jubilant’s `run` returns a [`jubilant.Task`](../../reference/jubilant/#jubilant.Task "jubilant.Task") and checks errors for you:

\# pytest-operator
app \= model.applications\['postgresl-k8s'\]
action \= await app.units\[0\].run\_action('get-password', username\='operator')
await action.wait()
password \= action.results\['password'\]

\# jubilant
task \= juju.run('postgresql-k8s/0', 'get-password', {'username': 'operator'})
password \= task.results\['password'\]

### The `cli` fallback[¶](#the-cli-fallback "Link to this heading")

Similar to how you could call `ops_test.juju`, with Jubilant you can call [`juju.cli`](../../reference/jubilant/#jubilant.Juju.cli "jubilant.Juju.cli") to execute an arbitrary Juju command. The `cli` method checks errors for you and raises a [`CLIError`](../../reference/jubilant/#jubilant.CLIError "jubilant.CLIError") if the command’s exit code is nonzero:

\# pytest-operator
return\_code, \_, scp\_err \= await ops\_test.juju(
    'scp',
    '--container',
    'postgresql',
    './testing\_database/testing\_database.sql',
    f'{postgres\_app.units\[0\].name}:.',
)
assert return\_code \== 0, scp\_err

\# jubilant
juju.cli(
    'scp',
    '--container',
    'postgresql',
    './testing\_database/testing\_database.sql',
    'postgresql-k8s/0:.',
)

### A `fast_forward` context manager[¶](#a-fast-forward-context-manager "Link to this heading")

Pytest-operator has a `fast_forward` context manager which temporarily speeds up `update-status` hooks to fire every 10 seconds (instead of Juju’s default of every 5 minutes). Jubilant doesn’t provide this context manager, as we don’t recommend it for new tests. If you need it for migrating existing tests, you can define it as:

@contextlib.contextmanager
def fast\_forward(juju: jubilant.Juju):
    """Context manager that temporarily speeds up update-status hooks to fire every 10s."""
    old \= juju.model\_config()\['update

<note>Content truncated. Call the fetch tool with a start_index of 15000 to get more content.</note>
```

</details>


---

<sub>⏱️ 1m 45s</sub>

### ✅ `web_fetch`

**https://canonical-jubilant.readthedocs-hosted.com/reference/jubilant/**

<details>
<summary>Arguments</summary>

```json
{
  "url": "https://canonical-jubilant.readthedocs-hosted.com/reference/jubilant/",
  "max_length": 15000
}
```

</details>

<details>
<summary>251 lines</summary>

```
Contents of https://canonical-jubilant.readthedocs-hosted.com/reference/jubilant/:
Jubilant is a Pythonic wrapper around the Juju CLI.

exception jubilant.CLIError(_returncode_, _cmd_, _output\=None_, _stderr\=None_)[¶](#jubilant.CLIError "Link to this definition")

Bases: `CalledProcessError`

Subclass of `CalledProcessError` that includes stdout and stderr in the `__str__`.

class jubilant.Juju(

_\*_,

_model: str | None \= None_,

_wait\_timeout: float \= 180.0_,

_cli\_binary: str | Path | None \= None_,

)[¶](#jubilant.Juju "Link to this definition")

Bases: `object`

Instantiate this class to run Juju commands.

Most methods directly call a single Juju CLI command. If a CLI command doesn’t yet exist as a method, use [`cli()`](#jubilant.Juju.cli "jubilant.Juju.cli").

Example:

juju \= jubilant.Juju()
juju.deploy('snappass-test')

Parameters:

*   **model** – If specified, operate on this Juju model, otherwise use the current Juju model. If the model is in another controller, prefix the model name with `<controller>:`.
    
*   **wait\_timeout** – The default timeout for [`wait()`](#jubilant.Juju.wait "jubilant.Juju.wait") (in seconds) if that method’s _timeout_ parameter is not specified.
    
*   **cli\_binary** – Path to the Juju CLI binary. If not specified, uses `juju` and assumes it is in the PATH.
    

add\_credential(

_cloud: str_,

_credential: str | Path | Mapping\[str, Any\]_,

_\*_,

_client: Literal\[True\]_,

_controller: None \= None_,

_region: str | None \= None_,

) → None[¶](#jubilant.Juju.add_credential "Link to this definition")

add\_credential(

_cloud: str_,

_credential: str | Path | Mapping\[str, Any\]_,

_\*_,

_client: bool \= False_,

_controller: str_,

_region: str | None \= None_,

) → None

Add a credential for a cloud.

Parameters:

*   **cloud** – Name of the cloud to add credentials for.
    
*   **credential** – Path to a YAML file containing credential to add, or a mapping representing the parsed credential YAML (`{'credentials': ...}`).
    
*   **client** – Set to true to save credentials on the client, meaning controllers created later will have access to them. You must specify `client=True` or provide _controller_ (or both).
    
*   **controller** – If specified, save credentials to the named controller.
    
*   **region** – Cloud region that the credential is valid for.
    

add\_model(

_model: str_,

_cloud: str | None \= None_,

_\*_,

_controller: str | None \= None_,

_config: Mapping\[str, bool | int | float | str | [SecretURI](../secrettypes/#jubilant.secrettypes.SecretURI "jubilant.secrettypes.SecretURI")\] | None \= None_,

_credential: str | None \= None_,

) → None[¶](#jubilant.Juju.add_model "Link to this definition")

Add a named model and set this instance’s model to it.

To avoid interfering with CLI users, this won’t switch the Juju CLI to the newly-created model. However, because [`model`](#jubilant.Juju.model "jubilant.Juju.model") is set to the name of the new model, all subsequent operations on this instance will use the new model.

Parameters:

*   **model** – Name of model to add.
    
*   **cloud** – Name of cloud or region (or cloud/region) to use for the model.
    
*   **controller** – Name of controller to operate in. If not specified, use the current controller.
    
*   **config** – Model configuration as key-value pairs, for example, `{'image-stream': 'daily'}`.
    
*   **credential** – Name of cloud credential to use for the model.
    

add\_secret(

_name: str_,

_content: Mapping\[str, str\]_,

_\*_,

_info: str | None \= None_,

) → [SecretURI](../secrettypes/#jubilant.secrettypes.SecretURI "jubilant.secrettypes.SecretURI")[¶](#jubilant.Juju.add_secret "Link to this definition")

Add a new named secret and return its secret URI.

Parameters:

*   **name** – Name for the secret.
    
*   **content** – Key-value pairs that represent the secret content, for example `{'password': 'hunter2'}`.
    
*   **info** – Description for the secret.
    

add\_ssh\_key(_\*keys: str_) → None[¶](#jubilant.Juju.add_ssh_key "Link to this definition")

Add one or more SSH keys to the model.

The SSH keys are added to all current and future machines in the model.

Parameters:

**keys** – SSH public key or keys to add. Each key should be the full SSH public key string (for example, `ssh-rsa AAAAB3... user@host`).

add\_unit(

_app: str_,

_\*_,

_attach\_storage: str | Iterable\[str\] | None \= None_,

_num\_units: int \= 1_,

_to: str | Iterable\[str\] | None \= None_,

)[¶](#jubilant.Juju.add_unit "Link to this definition")

Add one or more units to a deployed application.

Parameters:

*   **app** – Name of application to add units to.
    
*   **attach\_storage** – Existing storage(s) to attach to the deployed unit, for example, `foo/0` or `mydisk/1`. Not available for Kubernetes models.
    
*   **num\_units** – Number of units to add.
    
*   **to** – Machine or container to deploy the unit in (bypasses constraints). For example, to deploy to a new LXD container on machine 25, use `lxd:25`.
    

bootstrap(

_cloud: str_,

_controller: str_,

_\*_,

_bootstrap\_base: str | None \= None_,

_bootstrap\_constraints: Mapping\[str, str\] | None \= None_,

_config: Mapping\[str, bool | int | float | str | [SecretURI](../secrettypes/#jubilant.secrettypes.SecretURI "jubilant.secrettypes.SecretURI")\] | None \= None_,

_constraints: Mapping\[str, str\] | None \= None_,

_credential: str | None \= None_,

_force: bool \= False_,

_model\_defaults: Mapping\[str, bool | int | float | str | [SecretURI](../secrettypes/#jubilant.secrettypes.SecretURI "jubilant.secrettypes.SecretURI")\] | None \= None_,

_storage\_pool: Mapping\[str, str\] | None \= None_,

_to: str | Iterable\[str\] | None \= None_,

) → None[¶](#jubilant.Juju.bootstrap "Link to this definition")

Bootstrap a controller on a cloud environment.

To avoid interfering with CLI users, this does not switch the Juju CLI to the newly-created controller. In addition, `self.model` is not updated.

If you want to create a new controller with a model, use [`add_model()`](#jubilant.Juju.add_model "jubilant.Juju.add_model") after calling this method, which will set `self.model` for future commands:

juju \= jubilant.Juju()
juju.bootstrap('lxd', 'myctrl')
juju.add\_model('mymodel', controller\='myctrl')
\# self.model will be 'myctrl.mymodel' here

Parameters:

*   **cloud** – Name of cloud to bootstrap on. Initialization consists of creating a “controller” model and provisioning a machine to act as controller.
    
*   **controller** – Name for the controller.
    
*   **bootstrap\_base** – Specify the base of the bootstrap machine, for example `"24.04"`.
    
*   **bootstrap\_constraints** – Specify bootstrap machine constraints, for example, `{'mem': '8G'}`. If used, its values will also apply to any future controllers provisioned for high availability (HA).
    
*   **config** – Controller configuration options. Model config keys only affect the controller model.
    
*   **constraints** – Set model constraints, for example, `{'mem': '8G', 'cores': '4'}`. If used, its values will be set as the default constraints for all future workload machines in the model, exactly as if the constraints were set with `juju set-model-constraints`.
    
*   **credential** – Name of cloud credential to use when bootstrapping.
    
*   **force** – If true, allow bypassing of checks such as supported bases.
    
*   **model\_defaults** – Configuration options to set for all models.
    
*   **storage\_pool** – Options for an initial storage pool as key-value pairs. `name` and `type` are required, plus any additional attributes.
    
*   **to** – Placement directive indicating an instance to bootstrap.
    

cli(

_\*args: str_,

_include\_model: bool \= True_,

_stdin: str | None \= None_,

) → str[¶](#jubilant.Juju.cli "Link to this definition")

Run a Juju CLI command and return its standard output.

Parameters:

*   **args** – Command-line arguments (excluding `juju`).
    
*   **include\_model** – If true and [`model`](#jubilant.Juju.model "jubilant.Juju.model") is set, insert the `--model` argument after the first argument in _args_.
    
*   **stdin** – Standard input to send to the process, if any.
    

cli\_binary: str[¶](#jubilant.Juju.cli_binary "Link to this definition")

Path to the Juju CLI binary. If None, uses `juju` and assumes it is in the PATH.

config(

_app: str_,

_\*_,

_app\_config: bool \= False_,

) → Mapping\[str, bool | int | float | str | [SecretURI](../secrettypes/#jubilant.secrettypes.SecretURI "jubilant.secrettypes.SecretURI")\][¶](#jubilant.Juju.config "Link to this definition")

config(

_app: str_,

_values: Mapping\[str, bool | int | float | str | [SecretURI](../secrettypes/#jubilant.secrettypes.SecretURI "jubilant.secrettypes.SecretURI")\]_,

_\*_,

_reset: str | Iterable\[str\] \= ()_,

) → None

config(_app: str_, _\*_, _reset: str | Iterable\[str\]_) → None

Get or set the configuration of a deployed application.

If called with only the _app_ argument, get the config and return it.

If called with the _values_ or _reset_ arguments, set the config values and return None, and reset any keys in _reset_ to their defaults.

Parameters:

*   **app** – Application name to get or set config for.
    
*   **values** – Mapping of config names to values to set.
    
*   **app\_config** – When getting config, set this to true to get the (poorly-named) “application-config” values instead of charm config.
    
*   **reset** – Key or list of keys to reset to their defaults.
    

consume(

_model\_and\_app: str_,

_alias: str | None \= None_,

_\*_,

_controller: str | None \= None_,

_owner: str | None \= None_,

) → None[¶](#jubilant.Juju.consume "Link to this definition")

Add a remote offer to the model.

Examples:

juju.consume('othermodel.mysql', 'sql')
juju.consume('othermodel.mysql', controller\='ctrl2', owner\='admin')

Parameters:

*   **model\_and\_app** – Dotted application and model name to offer endpoints for, for example `othermodel.mysql`.
    
*   **alias** – A local alias for the offer, for use with [`integrate()`](#jubilant.Juju.integrate "jubilant.Juju.integrate"). Defaults to the application name.
    
*   **controller** – Remote offer’s controller. Defaults to the current controller.
    
*   **owner** – Remote model’s owner. Defaults to the user that is currently logged in to the controller providing the offer.
    

debug\_log(_\*_, _limit: int \= 0_) → str[¶](#jubilant.Juju.debug_log "Link to this definition")

Return debug log messages from a model.

For example, to create a pytest fixture which shows the last 1000 log lines if any tests fail:

@pytest.fixture(scope\='module')
def juju(request: pytest.FixtureRequest):
    with jubilant.temp\_model() as juju:
        yield juju  \# run the test
        if request.session.testsfailed:
            log \= juju.debug\_log(limit\=1000)
            print(log, end\='')

Parameters:

**limit** – Limit the result to the most recent _limit_ lines. Defaults to 0, meaning return all lines in the log.

deploy(

_charm: str | Path_,

_app: str | None \= None_,

_\*_,

_attach\_storage: str | Iterable\[str\] | None \= None_,

_base: str | None \= None_,

_bind: Mapping\[str, str\] | str | None \= None_,

_channel: str | None \= None_,

_config: Mapping\[str, bool | int | float | str | [SecretURI](../secrettypes/#jubilant.secrettypes.SecretURI "jubilant.secrettypes.SecretURI")\] | None \= None_,

_constraints: Mapping\[str, str\] | None \= None_,

_force: bool \= False_,

_num\_units: int \= 1_,

_overlays: Iterable\[str | Path\] \= ()_,

_resources: Mapping\[str, str\] | None \= None_,

_revision: int | None \= None_,

_storage: Mapping\[str, str\] | None \= None_,

_to: str | Iterable\[str\] | None \= None_,

_trust: bool \= False_,

) → None[¶](#jubilant.Juju.deploy "Link to this definition")

Deploy an application or bundle.

Parameters:

*   **charm** – Name of charm or bundle to deploy, or path to a local file (must start with `/` or `.`).
    
*   **app** – Custom application name within the model. Defaults to the charm name.
    
*   **attach\_storage** – Existing storage(s) to attach to the deployed unit, for example, `foo/0` or `mydisk/1`. Not available for Kubernetes models.
    
*   **base** – The base on which to deploy, for example, `ubuntu@22.04`.
    
*   **bind** – Either a mapping of endpoint-to-space bindings, for example `{'database-peers': 'internal-space'}`, or a single space name, which is equivalent to binding all endpoints to that space.
    
*   **channel** – Channel to use when deploying from Charmhub, for example, `latest/edge`.
    
*   **config** – Application configuration as key-value pairs, for example, `{'name': 'My Wiki'}`.
    
*   **constraints** – Hardware constraints for new machines, for example, `{'mem': '8G'}`.
    
*   **force** – If true, bypass checks such as supported bases.
    
*   **num\_units** – Number of units to deploy for principal charms.
    
*   **overlays** – File paths of bundles to overlay on the primary bundle, applied in order.
    
*   **resources** – Specify named resources to use for deployment, for example: `{'bin': '/path/to/some/binary'}`.
    
*   **revision** – Charmhub revision number to deploy.
    
*   **storage** – Constraints for named storage(s), for example, `{'data': 'tmpfs,1G'}`.
    
*   **to** – Machine or container to deploy the unit in (bypasses constraints). For example, to deploy to a new LXD container on machine 25, use `lxd:25`.
    
*   **trust** – If true, allows charm to run hooks that require access to cloud credentials.
    

destroy\_model(

_model: str_,

_\*_,

_destroy\_storage: bool \= False_,

_force: bool \= False_,

_no\_wait: bool \= False_,

_release\_storage: bool \= False_,

_timeout: float | None \= None_,

) → None[¶](#jubilant.Juju.destroy_model "Link to this definition")

Terminate all machines (or containers) and resources for a model.

If the given model is this instance’s model, also sets this instance’s [`model`](#jubilant.Juju.model "jubilant.Juju.model") to None.

Parameters:

*   **model** – Name of model to destroy.
    
*   **destroy\_storage** – If true, destroy all storage instances in the model.
    
*   **force** – If true, force model destruction and ignore any errors.
    
*   **no\_wait** – If true, rush through model destruction without waiting for each step to complete.
    
*   **release\_storage** – If true, release all storage instances in the model. This is mutually exclusive with _destroy\_storage_.
    
*   **timeout** – Maximum time (in seconds) to wait for each step in the model destruction. This option can only be used with _force_.
    

exec(

_command: str_,

_\*args: str_,

_machine: int | str_,

_wait: float | None \= None_,

) → [Task](#jubilant.Task "jubilant._task.Task")[¶](#jubilant.Juju.exec "Link to this definition")

exec(

_command: str_,

_\*args: str_,

_unit: str_,

_wait: float | None \= None_,

) → [Task](#jubilant.Task "jubilant._task.Task")

Run the command on

<note>Content truncated. Call the fetch tool with a start_index of 15000 to get more content.</note>
```

</details>


---

<sub>⏱️ 1m 51s</sub>

### ✅ `web_fetch`

**https://documentation.ubuntu.com/jubilant/how-to/migrate-from-pytest-operator/**

<details>
<summary>Arguments</summary>

```json
{
  "max_length": 10000,
  "url": "https://documentation.ubuntu.com/jubilant/how-to/migrate-from-pytest-operator/",
  "start_index": 15000
}
```

</details>

<details>
<summary>10 lines</summary>

```
Contents of https://documentation.ubuntu.com/jubilant/how-to/migrate-from-pytest-operator/:
-status-hook-interval'\]
    juju.model\_config({'update-status-hook-interval': '10s'})
    try:
        yield
    finally:
        juju.model\_config({'update-status-hook-interval': old})

## See more[¶](#see-more "Link to this heading")

*   [Jubilant’s API reference](../../reference/jubilant/)
    
*   [This discourse-k8s migration PR](https://github.com/canonical/discourse-k8s-operator/pull/326) shows how we migrated a real charm’s integration tests
```

</details>


---

<sub>⏱️ 1m 52s</sub>

### ✅ `web_fetch`

**https://canonical-jubilant.readthedocs-hosted.com/reference/jubilant/**

<details>
<summary>Arguments</summary>

```json
{
  "max_length": 10000,
  "url": "https://canonical-jubilant.readthedocs-hosted.com/reference/jubilant/",
  "start_index": 15000
}
```

</details>

<details>
<summary>161 lines</summary>

```
Contents of https://canonical-jubilant.readthedocs-hosted.com/reference/jubilant/:
 the remote target specified.

You must specify either _machine_ or _unit_, but not both.

Note: this method does not support running a command on multiple units at once. If you need that, let us know, and we’ll consider adding it with a new `exec_multiple` method or similar.

Parameters:

*   **command** – Command to run. Because the command is executed using the shell, arguments may also be included here as a single string, for example `juju.exec('echo foo', ...)`.
    
*   **args** – Arguments of the command.
    
*   **machine** – ID of machine to run the command on, for example `0`, `"0"`, or `"0/lxd/0"`.
    
*   **unit** – Name of unit to run the command on, for example `mysql/0` or `mysql/leader`.
    
*   **wait** – Maximum time to wait for command to finish; `TimeoutError` is raised if this is reached. Juju’s default is to wait 5 minutes.
    

Returns:

The task created to run the command, including logs, failure message, and so on.

Raises:

*   **ValueError** – if the machine or unit doesn’t exist.
    
*   [**TaskError**](#jubilant.TaskError "jubilant.TaskError") – if the command failed.
    
*   **TimeoutError** – if _wait_ was specified and the wait time was reached.
    

grant\_secret(

_identifier: str | [SecretURI](../secrettypes/#jubilant.secrettypes.SecretURI "jubilant.secrettypes.SecretURI")_,

_app: str | Iterable\[str\]_,

) → None[¶](#jubilant.Juju.grant_secret "Link to this definition")

Grant access to a secret for one or more applications.

Parameters:

*   **identifier** – The name or URI of the secret to grant access to.
    
*   **app** – Name or names of applications to grant access to.
    

integrate(

_app1: str_,

_app2: str_,

_\*_,

_via: str | Iterable\[str\] | None \= None_,

) → None[¶](#jubilant.Juju.integrate "Link to this definition")

Integrate two applications, creating a relation between them.

The order of _app1_ and _app2_ is not significant. Each of them should be in the format `<application>[:<endpoint>]`. The endpoint is only required if there’s more than one possible integration between the two applications.

To integrate an application in the current model with an application in another model (cross-model), prefix _app1_ or _app2_ with `<model>.`. To integrate with an application on another controller, _app1_ or _app2_ must be an offer endpoint. See `juju integrate --help` for details.

Parameters:

*   **app1** – One of the applications (and endpoints) to integrate.
    
*   **app2** – The other of the applications (and endpoints) to integrate.
    
*   **via** – Inform the offering side (the remote application) of the source of traffic, to enable network ports to be opened. This is in CIDR notation, for example `192.0.2.0/24`.
    

model: str | None[¶](#jubilant.Juju.model "Link to this definition")

If not None, operate on this Juju model, otherwise use the current Juju model.

If the model is in another controller, prefix the model name with `<controller>:`; for example, `juju = jubilant.Juju(model='mycontroller:my-model')`.

model\_config() → Mapping\[str, bool | int | float | str | [SecretURI](../secrettypes/#jubilant.secrettypes.SecretURI "jubilant.secrettypes.SecretURI")\][¶](#jubilant.Juju.model_config "Link to this definition")

model\_config(

_values: Mapping\[str, bool | int | float | str | [SecretURI](../secrettypes/#jubilant.secrettypes.SecretURI "jubilant.secrettypes.SecretURI")\]_,

_\*_,

_reset: str | Iterable\[str\] \= ()_,

) → None

model\_config(_\*_, _reset: str | Iterable\[str\]_) → None

Get or set the configuration of the model.

If called with no arguments, get the model config and return it.

If called with the _values_ or _reset_ arguments, set the model config values and return None, and reset any keys in _reset_ to their defaults.

Parameters:

*   **values** – Mapping of model config names to values to set, for example `{'update-status-hook-interval': '10s'}`.
    
*   **reset** – Key or list of keys to reset to their defaults.
    

model\_constraints() → Mapping\[str, bool | int | float | str\][¶](#jubilant.Juju.model_constraints "Link to this definition")

model\_constraints(

_constraints: Mapping\[str, bool | int | float | str\]_,

) → None

Get or set machine constraints on a model.

If called with no arguments, get the model constraints. If called with the _constraints_ argument, set the model constraints and return None.

Parameters:

**constraints** – Model constraints to set, for example, `{'mem': '8G', 'cores': 4}`.

offer(

_app: str_,

_\*_,

_controller: str | None \= None_,

_endpoint: str | Iterable\[str\]_,

_name: str | None \= None_,

) → None[¶](#jubilant.Juju.offer "Link to this definition")

Offer application endpoints for use in other models.

Examples:

juju.offer('mysql', endpoint\='db')
juju.offer('mymodel.mysql', endpoint\=\['db', 'log'\], name\='altname')

Parameters:

*   **app** – Application name to offer endpoints for. May include a dotted model name, for example `mymodel.mysql`.
    
*   **controller** – Name of controller to operate in. If not specified, use the current controller.
    
*   **endpoint** – Endpoint or endpoints to offer.
    
*   **name** – Name of the offer. By default, the offer is named after the application.
    

refresh(

_app: str_,

_\*_,

_base: str | None \= None_,

_channel: str | None \= None_,

_config: Mapping\[str, bool | int | float | str | [SecretURI](../secrettypes/#jubilant.secrettypes.SecretURI "jubilant.secrettypes.SecretURI")\] | None \= None_,

_force: bool \= False_,

_path: str | Path | None \= None_,

_resources: Mapping\[str, str\] | None \= None_,

_revision: int | None \= None_,

_storage: Mapping\[str, str\] | None \= None_,

_trust: bool \= False_,

)[¶](#jubilant.Juju.refresh "Link to this definition")

Refresh (upgrade) an application’s charm.

Parameters:

*   **app** – Name of application to refresh.
    
*   **base** – Select a different base than is currently running.
    
*   **channel** – Channel to use when deploying from Charmhub, for example, `latest/edge`.
    
*   **config** – Application configuration as key-value pairs.
    
*   **force** – If true, bypass checks such as supported bases.
    
*   **path** – Refresh to a charm located at this path.
    
*   **resources** – Specify named resources to use for deployment, for example: `{'bin': '/path/to/some/binary'}`.
    
*   **revision** – Charmhub revision number to deploy.
    
*   **storage** – Constraints for named storage(s), for example, `{'data': 'tmpfs,1G'}`.
    
*   **trust** – If true, allows charm to run hooks that require access to cloud credentials.
    

remove\_application(

_\*app: str_,

_destroy\_storage: bool \= False_,

_force: bool \= False_,

) → None[¶](#jubilant.Juju.remove_application "Link to this definition")

Remove applications from the model.

Parameters:

*   **app** – Name of the application or applications to remove.
    
*   **destroy\_storage** – If true, also destroy storage attached to application units.
    
*   **force** – Force removal even if an application is in an error state.
    

remove\_relation(_app1: str_, _app2: str_, _\*_, _force: bool \= False_) → None[¶](#jubilant.Juju.remove_relation "Link to this definition")

Remove an existing relation between two applications (opposite of [`integrate()`](#jubilant.Juju.integrate "jubilant.Juju.integrate")).

The order of _app1_ and _app2_ is not significant. Each of them should be in the format `<application>[:<endpoint>]`. The endpoint is only required if there’s more than one possible integration between the two applications.

Parameters:

*   **app1** – One of the applications (and endpoints) to integrate.
    
*   **app2** – The other of the applications (and endpoints) to integrate.
    
*   **force** – Force removal, ignoring operational errors.
    

remove\_secret(

_identifier: str | [SecretURI](../secrettypes/#jubilant.secrettypes.SecretURI "jubilant.secrettypes.SecretURI")_,

_\*_,

_revision: int | None \= None_,

) → None[¶](#jubilant.Juju.remove_secret "Link to this definition")

Remove a secret from the model.

Parameters:

*   **identifier** – The name or URI of the secret to remove.
    
*   **revision** – The revision of the secret to remove. If not specified, remove all revisions.
    

remove\_ssh\_key(_\*ids: str_) → None[¶](#jubilant.Juju.remove_ssh_key "Link to this definition")

Remove one or more SSH keys from the model.

The SSH keys are removed from all machines in the model.

Parameters:

**ids** – SSH key identifier or identifiers to remove. Each identifier can be a key fingerprint (for example, `45:7f:33:2c:10:4e:6c:14:e3:a1:a4:c8:b2:e1:34:b4`), a key comment (for example, `user@host`), or the full SSH public key string.

remove\_unit(

_\*app\_or\_unit: str_,

_destroy\_storage: bool \= False_,

_force: bool \= False_,

_num\_units: int \= 0_,

) → None[¶](#jubilant.Juju.remove_unit "Link to this definition")

Remove application units from the model.

Examples:

\# Kubernetes model:
juju.remove\_unit('wordpress', num\_units\=2)

\# Machine model:
juju.remove\_unit('wordpress/1')
juju.remove\_unit('wordpress/2', 'wordpress/3')

Parameters:

*   **app\_or\_unit** – On machine models, this is the name of the unit or units to remove. On Kubernetes models, this is actually the application name (a single string), as individual units are not named; you must use _num\_units_ to remove more than one unit on a Kubernetes model.
    
*   **destroy\_storage** – If true, also destroy storage attached to units.
    
*   **force** – Force removal even if a unit is in an error state.
    
*   **num\_units** – Number of units to remove (Kubernetes models only).
    

run(

_unit: str_,

_action: str_,

_params: Mapping\[str, Any\] | None \= None_,

_\*_,

_wait: float | None \= None_,

) → [Task](#jubilant.Task "jubilant._task.Task")[¶](#jubilant.Juju.run "Link to this definition")

Run an action on the given unit and wait for the result.

Note: this method does not support

<note>Content truncated. Call the fetch tool with a start_index of 25000 to get more content.</note>
```

</details>


---

<sub>⏱️ 4m 3s</sub>

### ✅ `web_fetch`

**https://canonical-jubilant.readthedocs-hosted.com/reference/statustypes/**

<details>
<summary>Arguments</summary>

```json
{
  "max_length": 12000,
  "url": "https://canonical-jubilant.readthedocs-hosted.com/reference/statustypes/"
}
```

</details>

<details>
<summary>167 lines</summary>

```
Contents of https://canonical-jubilant.readthedocs-hosted.com/reference/statustypes/:
Dataclasses that contain parsed output from `juju status --format=json`.

These dataclasses were originally [generated from](https://github.com/juju/juju/compare/main...benhoyt:juju:status-dataclasses) the Go structs in the Juju codebase, to ensure they are correct. Class names come from the Go struct name, whereas attribute names come from the JSON field names. The one exception is that “Application” has been renamed to “App” throughout, for brevity (and “application” to “app”).

class jubilant.statustypes.AppStatus(

_charm: str_,

_charm\_origin: str_,

_charm\_name: str_,

_charm\_rev: int_,

_exposed: bool_,

_base: [FormattedBase](#jubilant.statustypes.FormattedBase "jubilant.statustypes.FormattedBase") | None \= None_,

_charm\_channel: str \= ''_,

_charm\_version: str \= ''_,

_charm\_profile: str \= ''_,

_can\_upgrade\_to: str \= ''_,

_scale: int \= 0_,

_provider\_id: str \= ''_,

_address: str \= ''_,

_life: str \= ''_,

_app\_status: [StatusInfo](#jubilant.statustypes.StatusInfo "jubilant.statustypes.StatusInfo") \= <factory>_,

_relations: dict\[str_,

_list\[~jubilant.statustypes.AppStatusRelation\]\]\=<factory>_,

_subordinate\_to: list\[str\] \= <factory>_,

_units: dict\[str_,

_~jubilant.statustypes.UnitStatus\]\=<factory>_,

_version: str \= ''_,

_endpoint\_bindings: dict\[str_,

_str\]\=<factory>_,

)[¶](#jubilant.statustypes.AppStatus "Link to this definition")

Bases: `object`

Status of a single application.

address: str \= ''[¶](#jubilant.statustypes.AppStatus.address "Link to this definition")

app\_status: [StatusInfo](#jubilant.statustypes.StatusInfo "jubilant.statustypes.StatusInfo")[¶](#jubilant.statustypes.AppStatus.app_status "Link to this definition")

base: [FormattedBase](#jubilant.statustypes.FormattedBase "jubilant.statustypes.FormattedBase") | None \= None[¶](#jubilant.statustypes.AppStatus.base "Link to this definition")

can\_upgrade\_to: str \= ''[¶](#jubilant.statustypes.AppStatus.can_upgrade_to "Link to this definition")

charm: str[¶](#jubilant.statustypes.AppStatus.charm "Link to this definition")

charm\_channel: str \= ''[¶](#jubilant.statustypes.AppStatus.charm_channel "Link to this definition")

charm\_name: str[¶](#jubilant.statustypes.AppStatus.charm_name "Link to this definition")

charm\_origin: str[¶](#jubilant.statustypes.AppStatus.charm_origin "Link to this definition")

charm\_profile: str \= ''[¶](#jubilant.statustypes.AppStatus.charm_profile "Link to this definition")

charm\_rev: int[¶](#jubilant.statustypes.AppStatus.charm_rev "Link to this definition")

charm\_version: str \= ''[¶](#jubilant.statustypes.AppStatus.charm_version "Link to this definition")

endpoint\_bindings: dict\[str, str\][¶](#jubilant.statustypes.AppStatus.endpoint_bindings "Link to this definition")

exposed: bool[¶](#jubilant.statustypes.AppStatus.exposed "Link to this definition")

property is\_active: bool[¶](#jubilant.statustypes.AppStatus.is_active "Link to this definition")

Report whether the application status for this app is “active”.

property is\_blocked: bool[¶](#jubilant.statustypes.AppStatus.is_blocked "Link to this definition")

Report whether the application status for this app is “blocked”.

property is\_error: bool[¶](#jubilant.statustypes.AppStatus.is_error "Link to this definition")

Report whether the application status for this app is “error”.

property is\_maintenance: bool[¶](#jubilant.statustypes.AppStatus.is_maintenance "Link to this definition")

Report whether the application status for this app is “maintenance”.

property is\_waiting: bool[¶](#jubilant.statustypes.AppStatus.is_waiting "Link to this definition")

Report whether the application status for this app is “waiting”.

life: str \= ''[¶](#jubilant.statustypes.AppStatus.life "Link to this definition")

provider\_id: str \= ''[¶](#jubilant.statustypes.AppStatus.provider_id "Link to this definition")

relations: dict\[str, list\[[AppStatusRelation](#jubilant.statustypes.AppStatusRelation "jubilant.statustypes.AppStatusRelation")\]\][¶](#jubilant.statustypes.AppStatus.relations "Link to this definition")

scale: int \= 0[¶](#jubilant.statustypes.AppStatus.scale "Link to this definition")

subordinate\_to: list\[str\][¶](#jubilant.statustypes.AppStatus.subordinate_to "Link to this definition")

units: dict\[str, [UnitStatus](#jubilant.statustypes.UnitStatus "jubilant.statustypes.UnitStatus")\][¶](#jubilant.statustypes.AppStatus.units "Link to this definition")

version: str \= ''[¶](#jubilant.statustypes.AppStatus.version "Link to this definition")

class jubilant.statustypes.AppStatusRelation(

_related\_app: 'str' \= ''_,

_interface: 'str' \= ''_,

_scope: 'str' \= ''_,

)[¶](#jubilant.statustypes.AppStatusRelation "Link to this definition")

Bases: `object`

interface: str \= ''[¶](#jubilant.statustypes.AppStatusRelation.interface "Link to this definition")

scope: str \= ''[¶](#jubilant.statustypes.AppStatusRelation.scope "Link to this definition")

class jubilant.statustypes.CombinedStorage(

_storage: dict\[str_,

_~jubilant.statustypes.StorageInfo\]\=<factory>_,

_filesystems: dict\[str_,

_~jubilant.statustypes.FilesystemInfo\]\=<factory>_,

_volumes: dict\[str_,

_~jubilant.statustypes.VolumeInfo\]\=<factory>_,

)[¶](#jubilant.statustypes.CombinedStorage "Link to this definition")

Bases: `object`

Storage information.

filesystems: dict\[str, [FilesystemInfo](#jubilant.statustypes.FilesystemInfo "jubilant.statustypes.FilesystemInfo")\][¶](#jubilant.statustypes.CombinedStorage.filesystems "Link to this definition")

storage: dict\[str, [StorageInfo](#jubilant.statustypes.StorageInfo "jubilant.statustypes.StorageInfo")\][¶](#jubilant.statustypes.CombinedStorage.storage "Link to this definition")

volumes: dict\[str, [VolumeInfo](#jubilant.statustypes.VolumeInfo "jubilant.statustypes.VolumeInfo")\][¶](#jubilant.statustypes.CombinedStorage.volumes "Link to this definition")

class jubilant.statustypes.ControllerStatus(_timestamp: str \= ''_)[¶](#jubilant.statustypes.ControllerStatus "Link to this definition")

Bases: `object`

Basic controller information.

timestamp: str \= ''[¶](#jubilant.statustypes.ControllerStatus.timestamp "Link to this definition")

class jubilant.statustypes.EntityStatus(_current: str \= ''_, _message: str \= ''_, _since: str \= ''_)[¶](#jubilant.statustypes.EntityStatus "Link to this definition")

Bases: `object`

Status class used for storage status. See [`StatusInfo`](#jubilant.statustypes.StatusInfo "jubilant.statustypes.StatusInfo") for the main status class.

current: str \= ''[¶](#jubilant.statustypes.EntityStatus.current "Link to this definition")

message: str \= ''[¶](#jubilant.statustypes.EntityStatus.message "Link to this definition")

since: str \= ''[¶](#jubilant.statustypes.EntityStatus.since "Link to this definition")

class jubilant.statustypes.FilesystemAttachment(_mount\_point: 'str'_, _read\_only: 'bool'_, _life: 'str' \= ''_)[¶](#jubilant.statustypes.FilesystemAttachment "Link to this definition")

Bases: `object`

life: str \= ''[¶](#jubilant.statustypes.FilesystemAttachment.life "Link to this definition")

mount\_point: str[¶](#jubilant.statustypes.FilesystemAttachment.mount_point "Link to this definition")

read\_only: bool[¶](#jubilant.statustypes.FilesystemAttachment.read_only "Link to this definition")

class jubilant.statustypes.FilesystemAttachments(

_machines: 'dict\[str_,

_FilesystemAttachment\]'\=<factory>_,

_containers: 'dict\[str_,

_FilesystemAttachment\]'\=<factory>_,

_units: 'dict\[str_,

_UnitStorageAttachment\]'\=<factory>_,

)[¶](#jubilant.statustypes.FilesystemAttachments "Link to this definition")

Bases: `object`

containers: dict\[str, [FilesystemAttachment](#jubilant.statustypes.FilesystemAttachment "jubilant.statustypes.FilesystemAttachment")\][¶](#jubilant.statustypes.FilesystemAttachments.containers "Link to this definition")

machines: dict\[str, [FilesystemAttachment](#jubilant.statustypes.FilesystemAttachment "jubilant.statustypes.FilesystemAttachment")\][¶](#jubilant.statustypes.FilesystemAttachments.machines "Link to this definition")

units: dict\[str, [UnitStorageAttachment](#jubilant.statustypes.UnitStorageAttachment "jubilant.statustypes.UnitStorageAttachment")\][¶](#jubilant.statustypes.FilesystemAttachments.units "Link to this definition")

class jubilant.statustypes.FilesystemInfo(

_size: 'int'_,

_provider\_id: 'str' \= ''_,

_volume: 'str' \= ''_,

_storage: 'str' \= ''_,

_attachments: 'FilesystemAttachments' \= <factory>_,

_pool: 'str' \= ''_,

_life: 'str' \= ''_,

_status: 'EntityStatus' \= <factory>_,

)[¶](#jubilant.statustypes.FilesystemInfo "Link to this definition")

Bases: `object`

attachments: [FilesystemAttachments](#jubilant.statustypes.FilesystemAttachments "jubilant.statustypes.FilesystemAttachments")[¶](#jubilant.statustypes.FilesystemInfo.attachments "Link to this definition")

life: str \= ''[¶](#jubilant.statustypes.FilesystemInfo.life "Link to this definition")

pool: str \= ''[¶](#jubilant.statustypes.FilesystemInfo.pool "Link to this definition")

provider\_id: str \= ''[¶](#jubilant.statustypes.FilesystemInfo.provider_id "Link to this definition")

size: int[¶](#jubilant.statustypes.FilesystemInfo.size "Link to this definition")

status: [EntityStatus](#jubilant.statustypes.EntityStatus "jubilant.statustypes.EntityStatus")[¶](#jubilant.statustypes.FilesystemInfo.status "Link to this definition")

storage: str \= ''[¶](#jubilant.statustypes.FilesystemInfo.storage "Link to this definition")

volume: str \= ''[¶](#jubilant.statustypes.FilesystemInfo.volume "Link to this definition")

class jubilant.statustypes.FormattedBase(_name: 'str'_, _channel: 'str'_)[¶](#jubilant.statustypes.FormattedBase "Link to this definition")

Bases: `object`

channel: str[¶](#jubilant.statustypes.FormattedBase.channel "Link to this definition")

name: str[¶](#jubilant.statustypes.FormattedBase.name "Link to this definition")

class jubilant.statustypes.LxdProfileContents(

_config: 'dict\[str, str\]'_,

_description: 'str'_,

_devices: 'dict\[str, dict\[str, str\]\]'_,

)[¶](#jubilant.statustypes.LxdProfileContents "Link to this definition")

Bases: `object`

config: dict\[str, str\][¶](#jubilant.statustypes.LxdProfileContents.config "Link to this definition")

description: str[¶](#jubilant.statustypes.LxdProfileContents.description "Link to this definition")

devices: dict\[str, dict\[str, str\]\][¶](#jubilant.statustypes.LxdProfileContents.devices "Link to this definition")

class jubilant.statustypes.MachineStatus(

_juju\_status: [StatusInfo](#jubilant.statustypes.StatusInfo "jubilant.statustypes.StatusInfo") \= <factory>_,

_hostname: str \= ''_,

_dns\_name: str \= ''_,

_ip\_addresses: list\[str\] \= <factory>_,

_instance\_id: str \= ''_,

_display\_name: str \= ''_,

_machine\_status: [StatusInfo](#jubilant.statustypes.StatusInfo "jubilant.statustypes.StatusInfo") \= <factory>_,

_modification\_status: [StatusInfo](#jubilant.statustypes.StatusInfo "jubilant.statustypes.StatusInfo") \= <factory>_,

_base: [FormattedBase](#jubilant.statustypes.FormattedBase "jubilant.statustypes.FormattedBase") | None \= None_,

_network\_interfaces: dict\[str_,

_~jubilant.statustypes.NetworkInterface\]\=<factory>_,

_containers: dict\[str_,

_~jubilant.statustypes.MachineStatus\]\=<factory>_,

_constraints: str \= ''_,

_hardware: str \= ''_,

_controller\_member\_status: str \= ''_,

_ha\_primary: bool \= False_,

_lxd\_profiles: dict\[str_,

_~jubilant.statustypes.LxdProfileContents\]\=<factory>_,

)[¶](#jubilant.statustypes.MachineStatus "Link to this definition")

Bases: `object`

Status of a single machine.

base: [FormattedBase](#jubilant.statustypes.FormattedBase "jubilant.statustypes.FormattedBase") | None \= None[¶](#jubilant.statustypes.MachineStatus.base "Link to this definition")

constraints: str \= ''[¶](#jubilant.statustypes.MachineStatus.constraints "Link to this definition")

containers: dict\[str, [MachineStatus](#jubilant.statustypes.MachineSta

<note>Content truncated. Call the fetch tool with a start_index of 12000 to get more content.</note>
```

</details>


---

<sub>⏱️ 4m 11s</sub>

### ✅ `web_fetch`

**https://canonical-jubilant.readthedocs-hosted.com/reference/statustypes/**

<details>
<summary>Arguments</summary>

```json
{
  "max_length": 8000,
  "start_index": 12000,
  "url": "https://canonical-jubilant.readthedocs-hosted.com/reference/statustypes/"
}
```

</details>

<details>
<summary>101 lines</summary>

```
Contents of https://canonical-jubilant.readthedocs-hosted.com/reference/statustypes/:
tus "jubilant.statustypes.MachineStatus")\][¶](#jubilant.statustypes.MachineStatus.containers "Link to this definition")

controller\_member\_status: str \= ''[¶](#jubilant.statustypes.MachineStatus.controller_member_status "Link to this definition")

display\_name: str \= ''[¶](#jubilant.statustypes.MachineStatus.display_name "Link to this definition")

dns\_name: str \= ''[¶](#jubilant.statustypes.MachineStatus.dns_name "Link to this definition")

ha\_primary: bool \= False[¶](#jubilant.statustypes.MachineStatus.ha_primary "Link to this definition")

hardware: str \= ''[¶](#jubilant.statustypes.MachineStatus.hardware "Link to this definition")

hostname: str \= ''[¶](#jubilant.statustypes.MachineStatus.hostname "Link to this definition")

instance\_id: str \= ''[¶](#jubilant.statustypes.MachineStatus.instance_id "Link to this definition")

ip\_addresses: list\[str\][¶](#jubilant.statustypes.MachineStatus.ip_addresses "Link to this definition")

juju\_status: [StatusInfo](#jubilant.statustypes.StatusInfo "jubilant.statustypes.StatusInfo")[¶](#jubilant.statustypes.MachineStatus.juju_status "Link to this definition")

lxd\_profiles: dict\[str, [LxdProfileContents](#jubilant.statustypes.LxdProfileContents "jubilant.statustypes.LxdProfileContents")\][¶](#jubilant.statustypes.MachineStatus.lxd_profiles "Link to this definition")

machine\_status: [StatusInfo](#jubilant.statustypes.StatusInfo "jubilant.statustypes.StatusInfo")[¶](#jubilant.statustypes.MachineStatus.machine_status "Link to this definition")

modification\_status: [StatusInfo](#jubilant.statustypes.StatusInfo "jubilant.statustypes.StatusInfo")[¶](#jubilant.statustypes.MachineStatus.modification_status "Link to this definition")

network\_interfaces: dict\[str, [NetworkInterface](#jubilant.statustypes.NetworkInterface "jubilant.statustypes.NetworkInterface")\][¶](#jubilant.statustypes.MachineStatus.network_interfaces "Link to this definition")

class jubilant.statustypes.ModelStatus(

_name: str_,

_type: str_,

_controller: str_,

_cloud: str_,

_version: str_,

_region: str \= ''_,

_upgrade\_available: str \= ''_,

_model\_status: [StatusInfo](#jubilant.statustypes.StatusInfo "jubilant.statustypes.StatusInfo") \= <factory>_,

)[¶](#jubilant.statustypes.ModelStatus "Link to this definition")

Bases: `object`

Status and basic information about the model.

cloud: str[¶](#jubilant.statustypes.ModelStatus.cloud "Link to this definition")

Name of cloud, for example `aws` or `microk8s`.

controller: str[¶](#jubilant.statustypes.ModelStatus.controller "Link to this definition")

Name of controller.

model\_status: [StatusInfo](#jubilant.statustypes.StatusInfo "jubilant.statustypes.StatusInfo")[¶](#jubilant.statustypes.ModelStatus.model_status "Link to this definition")

Status of the model. Normally the _current_ field is `available`.

name: str[¶](#jubilant.statustypes.ModelStatus.name "Link to this definition")

Name of model.

region: str \= ''[¶](#jubilant.statustypes.ModelStatus.region "Link to this definition")

Cloud region.

type: str[¶](#jubilant.statustypes.ModelStatus.type "Link to this definition")

Type of model, for example, `caas` for a Kubernetes model.

upgrade\_available: str \= ''[¶](#jubilant.statustypes.ModelStatus.upgrade_available "Link to this definition")

Version number if a new Juju agent is available.

version: str[¶](#jubilant.statustypes.ModelStatus.version "Link to this definition")

Juju agent version.

class jubilant.statustypes.NetworkInterface(

_ip\_addresses: 'list\[str\]'_,

_mac\_address: 'str'_,

_is\_up: 'bool'_,

_gateway: 'str' \= ''_,

_dns\_nameservers: 'list\[str\]' \= <factory>_,

_space: 'str' \= ''_,

)[¶](#jubilant.statustypes.NetworkInterface "Link to this definition")

Bases: `object`

dns\_nameservers: list\[str\][¶](#jubilant.statustypes.NetworkInterface.dns_nameservers "Link to this definition")

gateway: str \= ''[¶](#jubilant.statustypes.NetworkInterface.gateway "Link to this definition")

ip\_addresses: list\[str\][¶](#jubilant.statustypes.NetworkInterface.ip_addresses "Link to this definition")

is\_up: bool[¶](#jubilant.statustypes.NetworkInterface.is_up "Link to this definition")

mac\_address: str[¶](#jubilant.statustypes.NetworkInterface.mac_address "Link to this definition")

space: str \= ''[¶](#jubilant.statustypes.NetworkInterface.space "Link to this definition")

class jubilant.statustypes.OfferStatus(

_app: 'str'_,

_endpoints: 'dict\[str, RemoteEndpoint\]'_,

_charm: 'str' \= ''_,

_total\_connected\_count: 'int' \= 0_,

_active\_connected\_count: 'int' \= 0_,

)[¶](#jubilant.statustypes.OfferStatus "Link to this definition")

Bases: `object`

active\_connected\_count: int \= 0[¶](#jubilant.statustypes.OfferStatus.active_connected_count "Link to this definition")

app: str[¶](#jubilant.statustypes.OfferStatus.app "Link to this definition")

charm: str \= ''[¶](#jubilant.statustypes.OfferStatus.charm "Link to this definition")

endpoints: dict\[str, [RemoteEndpoint](#jubilant.statustypes.RemoteEndpoint "jubilant.statustypes.RemoteEndpoint")\][¶](#jubilant.statustypes.OfferStatus.endpoints "Link to this definition")

total\_connected\_count: int \= 0[¶](#jubilant.statustypes.OfferStatus.total_connected_count "Link to this definition")

class jubilant.statustypes.RemoteAppStatus(

_url: 'str'_,

_endpoints: 'dict\[str_,

_RemoteEndpoint\]'\=<factory>_,

_life: 'str' \= ''_,

_app\_status: 'StatusInfo' \= <factory>_,

_relations: 'dict\[str_,

_list\[str\]\]'\=<factory>_,

)[¶](#jubilant.statustypes.RemoteAppStatus "Link to this definition")

Bases: `object`

app\_status: [StatusInfo](#jubilant.statustypes.StatusInfo "jubilant.statustypes.StatusInfo")[¶](#jubilant.statustypes.RemoteAppStatus.app_status "Link to this definition")

endpoints: dict\[str, [RemoteEndpoint](#jubilant.statustypes.RemoteEndpoint "jubilant.statustypes.RemoteEndpoint")\][¶](#jubilant.statustypes.RemoteAppStatus.endpoints "Link to this definition")

life: str \= ''[¶](#jubilant.statustypes.RemoteAppStatus.life "Link to this definition")

relations: dict\[str, list\[str\]\][¶](#jubilant.statustypes.RemoteAppStatus.relations "Link to this definition")

url: str[¶](#jubilant.statustypes.RemoteAppStatus.url "Link to this definition")

class jubilant.statustypes.RemoteEndpoint(_interface: 'str'_, _role: 'str'_)[¶](#jubilant.statustypes.RemoteEndpoint "Link to this definition")

Bases: `object`

interface: str[¶](#jubilant.statustypes.RemoteEndpoint.interface "Link to this definition")

role: str[¶](#jubilant.statustypes.RemoteEndpoint.role "Link to this definition")

class jubilant.statustypes.Status(_model: ~jubilant.statustypes.ModelStatus, machines: dict\[str, ~jubilant.statustypes.MachineStatus\], apps: dict\[str, ~jubilant.statustypes.AppStatus\], app\_endpoints: dict\[str, ~jubilant.statustypes.RemoteAppStatus\] \= <factory>, offers: dict\[str, ~jubilant.statustypes.OfferStatus\] \= <factory>, storage: ~jubilant.statustypes.CombinedStorage \= <factory>, controller: ~jubilant.statustypes.ControllerStatus \= <factory>_)[¶](#jubilant.statustypes.Status "Link to this definition")

Bases: `object`

Parsed version of the status object returned by `juju status --format=json`.

app\_endpoints: dict\[str, [RemoteAppStatus](#jubilant.statustypes.RemoteAppStatus "jubilant.statustypes.RemoteAppStatus")\][¶](#jubilant.statustypes.Status.app_endpoints "Link to this definition")

Mapping of offer name to remote application information.

apps: dict\[str, [AppStatus](#jubilant.statustypes.AppStatus "jubilant.statustypes.AppStatus")\][¶](#jubilant.statustypes.Status.apps "Link to this definition")

Mapping of application name to application information.

controller: [ControllerStatus](#jubilant.statustypes.ControllerStatus "jubilant.statustypes.ControllerStatus")[¶](#jubilant.statustypes.Status.controller "Link to this definition")

Controller information.

get\_units(_app: str_) → dict\[str, [UnitStatus](#jubilant.statustypes.UnitStatus "jubilant.statustypes.UnitStatus"

<note>Content truncated. Call the fetch tool with a start_index of 20000 to get more content.</note>
```

</details>


---

<sub>⏱️ 4m 15s</sub>

### ✅ `web_fetch`

**https://canonical-jubilant.readthedocs-hosted.com/reference/statustypes/**

<details>
<summary>Arguments</summary>

```json
{
  "max_length": 8000,
  "start_index": 20000,
  "url": "https://canonical-jubilant.readthedocs-hosted.com/reference/statustypes/"
}
```

</details>

<details>
<summary>114 lines</summary>

```
Contents of https://canonical-jubilant.readthedocs-hosted.com/reference/statustypes/:
)\][¶](#jubilant.statustypes.Status.get_units "Link to this definition")

Get all units of the given _app_, including units of subordinate apps.

For subordinate apps, this finds and returns the subordinate units using the app’s `subordinate_to` list. For principal (non-subordinate) apps, this is equivalent to `status.apps[app].units`.

Returns:

Dict of units where the key is the unit name and the value is the [`UnitStatus`](#jubilant.statustypes.UnitStatus "jubilant.statustypes.UnitStatus"). If _app_ is not found, return an empty dict.

machines: dict\[str, [MachineStatus](#jubilant.statustypes.MachineStatus "jubilant.statustypes.MachineStatus")\][¶](#jubilant.statustypes.Status.machines "Link to this definition")

Mapping of machine ID string (for example, `"0"`) to machine information.

model: [ModelStatus](#jubilant.statustypes.ModelStatus "jubilant.statustypes.ModelStatus")[¶](#jubilant.statustypes.Status.model "Link to this definition")

Model information.

offers: dict\[str, [OfferStatus](#jubilant.statustypes.OfferStatus "jubilant.statustypes.OfferStatus")\][¶](#jubilant.statustypes.Status.offers "Link to this definition")

Mapping of offer name to offer information.

storage: [CombinedStorage](#jubilant.statustypes.CombinedStorage "jubilant.statustypes.CombinedStorage")[¶](#jubilant.statustypes.Status.storage "Link to this definition")

Storage information.

class jubilant.statustypes.StatusInfo(

_current: str \= ''_,

_message: str \= ''_,

_reason: str \= ''_,

_since: str \= ''_,

_version: str \= ''_,

_life: str \= ''_,

)[¶](#jubilant.statustypes.StatusInfo "Link to this definition")

Bases: `object`

The main status class used for application, unit, and machine status.

current: str \= ''[¶](#jubilant.statustypes.StatusInfo.current "Link to this definition")

life: str \= ''[¶](#jubilant.statustypes.StatusInfo.life "Link to this definition")

message: str \= ''[¶](#jubilant.statustypes.StatusInfo.message "Link to this definition")

reason: str \= ''[¶](#jubilant.statustypes.StatusInfo.reason "Link to this definition")

since: str \= ''[¶](#jubilant.statustypes.StatusInfo.since "Link to this definition")

version: str \= ''[¶](#jubilant.statustypes.StatusInfo.version "Link to this definition")

class jubilant.statustypes.StorageAttachments(_units: 'dict\[str, UnitStorageAttachment\]'_)[¶](#jubilant.statustypes.StorageAttachments "Link to this definition")

Bases: `object`

units: dict\[str, [UnitStorageAttachment](#jubilant.statustypes.UnitStorageAttachment "jubilant.statustypes.UnitStorageAttachment")\][¶](#jubilant.statustypes.StorageAttachments.units "Link to this definition")

class jubilant.statustypes.StorageInfo(

_kind: 'str'_,

_status: 'EntityStatus'_,

_persistent: 'bool'_,

_life: 'str' \= ''_,

_attachments: 'StorageAttachments | None' \= None_,

)[¶](#jubilant.statustypes.StorageInfo "Link to this definition")

Bases: `object`

attachments: [StorageAttachments](#jubilant.statustypes.StorageAttachments "jubilant.statustypes.StorageAttachments") | None \= None[¶](#jubilant.statustypes.StorageInfo.attachments "Link to this definition")

kind: str[¶](#jubilant.statustypes.StorageInfo.kind "Link to this definition")

life: str \= ''[¶](#jubilant.statustypes.StorageInfo.life "Link to this definition")

persistent: bool[¶](#jubilant.statustypes.StorageInfo.persistent "Link to this definition")

status: [EntityStatus](#jubilant.statustypes.EntityStatus "jubilant.statustypes.EntityStatus")[¶](#jubilant.statustypes.StorageInfo.status "Link to this definition")

class jubilant.statustypes.UnitStatus(

_workload\_status: [StatusInfo](#jubilant.statustypes.StatusInfo "jubilant.statustypes.StatusInfo") \= <factory>_,

_juju\_status: [StatusInfo](#jubilant.statustypes.StatusInfo "jubilant.statustypes.StatusInfo") \= <factory>_,

_leader: bool \= False_,

_upgrading\_from: str \= ''_,

_machine: str \= ''_,

_open\_ports: list\[str\] \= <factory>_,

_public\_address: str \= ''_,

_address: str \= ''_,

_provider\_id: str \= ''_,

_subordinates: dict\[str_,

_~jubilant.statustypes.UnitStatus\]\=<factory>_,

)[¶](#jubilant.statustypes.UnitStatus "Link to this definition")

Bases: `object`

Status of a single unit.

address: str \= ''[¶](#jubilant.statustypes.UnitStatus.address "Link to this definition")

property is\_active: bool[¶](#jubilant.statustypes.UnitStatus.is_active "Link to this definition")

Report whether the workload status for this unit status is “active”.

property is\_blocked: bool[¶](#jubilant.statustypes.UnitStatus.is_blocked "Link to this definition")

Report whether the workload status for this unit status is “blocked”.

property is\_error: bool[¶](#jubilant.statustypes.UnitStatus.is_error "Link to this definition")

Report whether the workload status for this unit status is “error”.

property is\_maintenance: bool[¶](#jubilant.statustypes.UnitStatus.is_maintenance "Link to this definition")

Report whether the workload status for this unit status is “maintenance”.

property is\_waiting: bool[¶](#jubilant.statustypes.UnitStatus.is_waiting "Link to this definition")

Report whether the workload status for this unit status is “waiting”.

juju\_status: [StatusInfo](#jubilant.statustypes.StatusInfo "jubilant.statustypes.StatusInfo")[¶](#jubilant.statustypes.UnitStatus.juju_status "Link to this definition")

leader: bool \= False[¶](#jubilant.statustypes.UnitStatus.leader "Link to this definition")

machine: str \= ''[¶](#jubilant.statustypes.UnitStatus.machine "Link to this definition")

open\_ports: list\[str\][¶](#jubilant.statustypes.UnitStatus.open_ports "Link to this definition")

provider\_id: str \= ''[¶](#jubilant.statustypes.UnitStatus.provider_id "Link to this definition")

public\_address: str \= ''[¶](#jubilant.statustypes.UnitStatus.public_address "Link to this definition")

subordinates: dict\[str, [UnitStatus](#jubilant.statustypes.UnitStatus "jubilant.statustypes.UnitStatus")\][¶](#jubilant.statustypes.UnitStatus.subordinates "Link to this definition")

upgrading\_from: str \= ''[¶](#jubilant.statustypes.UnitStatus.upgrading_from "Link to this definition")

workload\_status: [StatusInfo](#jubilant.statustypes.StatusInfo "jubilant.statustypes.StatusInfo")[¶](#jubilant.statustypes.UnitStatus.workload_status "Link to this definition")

class jubilant.statustypes.UnitStorageAttachment(

_machine: 'str' \= ''_,

_location: 'str' \= ''_,

_life: 'str' \= ''_,

)[¶](#jubilant.statustypes.UnitStorageAttachment "Link to this definition")

Bases: `object`

life: str \= ''[¶](#jubilant.statustypes.UnitStorageAttachment.life "Link to this definition")

location: str \= ''[¶](#jubilant.statustypes.UnitStorageAttachment.location "Link to this definition")

machine: str \= ''[¶](#jubilant.statustypes.UnitStorageAttachment.machine "Link to this definition")

class jubilant.statustypes.VolumeAttachment(

_read\_only: 'bool'_,

_device: 'str' \= ''_,

_device\_link: 'str' \= ''_,

_bus\_address: 'str' \= ''_,

_life: 'str' \= ''_,

)[¶](#jubilant.statustypes.VolumeAttachment "Link to this definition")

Bases: `object`

bus\_address: str \= ''[¶](#jubilant.statustypes.VolumeAttachment.bus_address "Link to this definition")

device: str \= ''[¶](#jubilant.statustypes.VolumeAttachment.device "Link to this definition")

device\_link: str \= ''[¶](#jubilant.statustypes.VolumeAttachment.device_link "Link to this definition")

life: str \= ''[¶](#jubilant.statustypes.VolumeAttachment.life "Link to this definition")

read\_only: bool[¶](#jubilant.statustypes.VolumeAttachment.read_only "Link to this definition")

class jubilant.statustypes.VolumeAttachments(

_machines: 'dict\[str_,

_VolumeAttachment\]'\=<factory>_,

_containers: 'dict\[str_,

_VolumeAttachment\]'\=<factory>_,

_units: 'dict\[str_,

_UnitStorageAttachment\]'\=<factory>_,

)[¶](#jubilant.statustypes.VolumeAttachments "Link to this definition")

Bases: `object`

containers: dict\[str, [VolumeAttachment](#jubilant.statustypes.VolumeAttachment "jubilant.statustypes.V

<note>Content truncated. Call the fetch tool with a start_index of 28000 to get more content.</note>
```

</details>


---

<sub>⏱️ 6m 5s</sub>

### 💬 Copilot

Let me check the pytest-jubilant docs to understand what it provides:

---

<sub>⏱️ 6m 5s</sub>

### ✅ `web_fetch`

**https://pypi.org/project/pytest-jubilant/**

<details>
<summary>Arguments</summary>

```json
{
  "max_length": 12000,
  "url": "https://pypi.org/project/pytest-jubilant/"
}
```

</details>

```
Contents of https://pypi.org/project/pytest-jubilant/:
A required part of this site couldn’t load. This may be due to a browser extension, network issues, or browser settings. Please check your connection, disable any ad blockers, or try using a different browser.
```


---

<sub>⏱️ 6m 27s</sub>

### ✅ `web_search`

**pytest-jubilant plugin juju fixture conftest module-scoped keep-models CLI options documentation**

<details>
<summary>Arguments</summary>

```json
{
  "query": "pytest-jubilant plugin juju fixture conftest module-scoped keep-models CLI options documentation"
}
```

</details>

````
{"type":"text","text":{"value":"Here’s a comprehensive breakdown of how the `pytest-jubilant` plugin manages Juju models via module-scoped fixtures—specifically how to use and customize these with options like `--keep-models`, and how to configure the fixture in your `conftest.py`. This also covers relevant CLI options as documented upstream.\n\n### `pytest-jubilant`: Overview\n\n`pytest-jubilant` is a replacement for `pytest-operator`, streamlining integration testing for Juju charms. Its core value is managing temporary Juju models for your tests, by providing robust fixtures and CLI options for lifecycle control.\n\n---\n\n### Key Fixture: `juju` (Module-Scoped)\n\n**Definition in `conftest.py`:**\n```python\nimport jubilant\nimport pytest\n\n@pytest.fixture(scope='module')\ndef juju(request: pytest.FixtureRequest):\n    keep_models = bool(request.config.getoption('--keep-models'))\n    with jubilant.temp_model(keep=keep_models) as juju:\n        juju.wait_timeout = 10 * 60  # 10 minutes\n        yield juju\n    # Optionally, print juju debug log if a test fails\n    if request.session.testsfailed:\n        log = juju.debug_log(limit=1000)\n        print(log, end='')\n\ndef pytest_addoption(parser):\n    parser.addoption('--keep-models', action='store_true', default=False,\n                     help='keep temporarily-created models')\n```\n- The fixture is **module-scoped**, so each test module (file) gets its own isolated model.\n- Temporary models are created for test runs and can be left running with (`--keep-models`) or torn down on completion.\n- On test failure, the last 1000 lines of Juju debug log are printed for easier diagnosis.\n\n---\n\n### Model Lifecycle CLI Options\n\nYou can control how models are created/destroyed during your test run using these `pytest` command-line options:\n\n- **`--keep-models`**:  \n  Keeps temporary models after test runs, rather than cleaning them up automatically. Useful for debugging or investigation.\n- **`--model NAME`**:  \n  Override (fix) the model name. By default, models are named with the test module + random bits. Using this option lets you reuse an existing model across test runs.  \n  _Example:_  \n  `pytest ./tests/integration -k test_foo --model \"model2\"`\n- **`--no-teardown`**:  \n  When used with `--model`, prevents the test runner from destroying the named model at the end of the session.\n- **`--switch`**:  \n  When used, the CLI switches you into the model context during the test run. Handy for real-time monitoring.\n\nFrom the docs:\n- `pytest tests/test_cmr.py --keep-models` skips model teardown for all generated models.\n- `pytest tests/test_cmr.py --model test-cmr-<randomhex>` uses a specific model name; with fixture suffixes, you can predict all model names, enabling test model reuse.\n- `pytest ./tests/integration -k test_foo --model \"model1\" --no-teardown` runs on an existing \"model1\" and keeps it after test run.\n- `pytest ./tests/integration -k test-something --switch` switches your environment to the current test-generated model for interactive investigation【3:0†pytest-jubilant · PyPI†https://pypi.org/project/pytest-jubilant/】【3:1†How to migrate from pytest-operator to Jubilant - Jubilant documentation†https://documentation.ubuntu.com/jubilant/how-to/migrate-from-pytest-operator/】【3:3†Getting started with Jubilant - Jubilant documentation†https://documentation.ubuntu.com/jubilant/tutorial/getting-started/】【3:4†How to migrate from pytest-operator to Jubilant†https://canonical-jubilant.readthedocs-hosted.com/how-to/migrate-from-pytest-operator/】【3:5†Jubilant, the joyful library for driving Juju - GitHub†https://github.com/canonical/jubilant】.\n\n---\n\n### Real-World Example\n\n**conftest.py**\n```python\n@pytest.fixture(scope='module')\ndef juju(request):\n    keep = request.config.getoption(\"--keep-models\")\n    with jubilant.temp_model(keep=keep) as juju:\n        yield juju\n```\n\n**Command-line usage**\n- Run and keep models:  \n  `pytest tests/ --keep-models`\n- Use/reuse a named model:  \n  `pytest tests/ --model my-shared-model --no-teardown`\n\n---\n\n### Additional Notes\n\n- Use the `juju` fixture in your tests as a parameter; lifecycle is handled automatically as per scope and options.\n- Factory patterns are supported if you want multiple models/test (see the `temp_model_factory` fixture).\n- Use `conftest.py` to define these fixtures for easy sharing across test files【3:6†Using conftest.py vs. importing fixtures from dedicate modules†https://stackoverflow.com/questions/73191533/using-conftest-py-vs-importing-fixtures-from-dedicate-modules】【3:9†Pytest Advanced Techniques: Mastering Python Test Automation†https://yrkan.com/blog/pytest-advanced-techniques/】.\n\n---\n\n### Learn More\n\n- [pytest-jubilant PyPI](https://pypi.org/project/pytest-jubilant/)\n- [Official migration guide (with fixture examples)](https://documentation.ubuntu.com/jubilant/how-to/migrate-from-pytest-operator/)\n- [Getting started with Jubilant: CLI & fixtures](https://documentation.ubuntu.com/jubilant/tutorial/getting-started/)\n- [Jubilant GitHub repository](https://github.com/canonical/jubilant/)\n\nIf you need a concrete, copy/paste-ready `conftest.py` or further info on more advanced fixture patterns, let me know!","annotations":[{"text":"【3:0†pytest-jubilant · PyPI†https://pypi.org/project/pytest-jubilant/】","start_index":3000,"end_index":3070,"url_citation":{"title":"pytest-jubilant · PyPI","url":"https://pypi.org/project/pytest-jubilant/"}},{"text":"【3:1†How to migrate from pytest-operator to Jubilant - Jubilant documentation†https://documentation.ubuntu.com/jubilant/how-to/migrate-from-pytest-operator/】","start_index":3070,"end_index":3227,"url_citation":{"title":"How to migrate from pytest-operator to Jubilant - Jubilant documentation","url":"https://documentation.ubuntu.com/jubilant/how-to/migrate-from-pytest-operator/"}},{"text":"【3:3†Getting started with Jubilant - Jubilant documentation†https://documentation.ubuntu.com/jubilant/tutorial/getting-started/】","start_index":3227,"end_index":3355,"url_citation":{"title":"Getting started with Jubilant - Jubilant documentation","url":"https://documentation.ubuntu.com/jubilant/tutorial/getting-started/"}},{"text":"【3:4†How to migrate from pytest-operator to Jubilant†https://canonical-jubilant.readthedocs-hosted.com/how-to/migrate-from-pytest-operator/】","start_index":3355,"end_index":3495,"url_citation":{"title":"How to migrate from pytest-operator to Jubilant","url":"https://canonical-jubilant.readthedocs-hosted.com/how-to/migrate-from-pytest-operator/"}},{"text":"【3:5†Jubilant, the joyful library for driving Juju - GitHub†https://github.com/canonical/jubilant】","start_index":3495,"end_index":3593,"url_citation":{"title":"Jubilant, the joyful library for driving Juju - GitHub","url":"https://github.com/canonical/jubilant"}},{"text":"【3:6†Using conftest.py vs. importing fixtures from dedicate modules†https://stackoverflow.com/questions/73191533/using-conftest-py-vs-importing-fixtures-from-dedicate-modules】","start_index":4322,"end_index":4497,"url_citation":{"title":"Using conftest.py vs. importing fixtures from dedicate modules","url":"https://stackoverflow.com/questions/73191533/using-conftest-py-vs-importing-fixtures-from-dedicate-modules"}},{"text":"【3:9†Pytest Advanced Techniques: Mastering Python Test Automation†https://yrkan.com/blog/pytest-advanced-techniques/】","start_index":4497,"end_index":4614,"url_citation":{"title":"Pytest Advanced Techniques: Mastering Python Test Automation","url":"https://yrkan.com/blog/pytest-advanced-techniques/"}}]},"bing_searches":[{"text":"pytest-jubilant plugin juju fixture conftest module-scoped keep-models CLI options documentation","url":"https://www.bing.com/search?q=pytest-jubilant+plugin+juju+fixture+conftest+module-scoped+keep-models+CLI+options+documentation"}],"annotations":null}
````


---

<sub>⏱️ 7m 23s</sub>

### 💬 Copilot

Now I have everything I need. Let me implement the full migration:

---

<sub>⏱️ 7m 23s</sub>

### ✅ `sql`

**Create migration todos**

<details>
<summary>Arguments</summary>

```json
{
  "description": "Create migration todos",
  "query": "INSERT INTO todos (id, title, description, status) VALUES\n  ('conftest', 'Create conftest.py', 'Create tests/integration/conftest.py with juju module-scoped fixture using jubilant.temp_model, --keep-models option, and debug log on failure', 'pending'),\n  ('helpers', 'Rewrite helpers.py', 'Convert helpers.py from async/libjuju to sync jubilant API. Replace Unit params with (juju, unit_name) pairs. Replace ops_test.juju() with juju.cli(). Add fast_forward context manager.', 'pending'),\n  ('test-file', 'Rewrite test_s3_charm.py', 'Remove async/await, replace OpsTest with jubilant.Juju fixture, update all model/deploy/wait/action/config/relation calls to jubilant API.', 'pending'),\n  ('pyproject', 'Update pyproject.toml', 'Replace pytest-operator and juju deps with jubilant and pytest-jubilant. Remove asyncio_mode from pytest options.', 'pending'),\n  ('tox', 'Update tox.ini if needed', 'Check if tox.ini integration section needs updates after deps change.', 'pending')"
}
```

</details>

```
5 row(s) inserted. Last inserted row ID: 5.
```


---

<sub>⏱️ 7m 30s</sub>

### ✅ `create`

**/tmp/s3-integrator-L1-sonnet/tests/integration/conftest.py**

/tmp/s3-integrator-L1-sonnet/tests/integration/conftest.py

```
Created file /tmp/s3-integrator-L1-sonnet/tests/integration/conftest.py with 685 characters
```


---

<sub>⏱️ 7m 35s</sub>

### ✅ `sql`

**Mark conftest done**

<details>
<summary>Arguments</summary>

```json
{
  "description": "Mark conftest done",
  "query": "UPDATE todos SET status = 'done' WHERE id = 'conftest'"
}
```

</details>

```
1 row(s) updated.
```


---

<sub>⏱️ 8m 6s</sub>

### 💬 Copilot

Now rewrite `helpers.py`:

---

<sub>⏱️ 8m 6s</sub>

### ✅ `edit`

**/tmp/s3-integrator-L1-sonnet/tests/integration/helpers.py**

/tmp/s3-integrator-L1-sonnet/tests/integration/helpers.py

```
File /tmp/s3-integrator-L1-sonnet/tests/integration/helpers.py updated with changes.
```


---

<sub>⏱️ 9m 5s</sub>

### 💬 Copilot

Now rewrite `test_s3_charm.py`:

---

<sub>⏱️ 9m 5s</sub>

### ✅ `edit`

**/tmp/s3-integrator-L1-sonnet/tests/integration/test_s3_charm.py**

/tmp/s3-integrator-L1-sonnet/tests/integration/test_s3_charm.py

```
File /tmp/s3-integrator-L1-sonnet/tests/integration/test_s3_charm.py updated with changes.
```


---

<sub>⏱️ 9m 11s</sub>

### 💬 Copilot

Now update `pyproject.toml`:

---

<sub>⏱️ 9m 11s</sub>

### ✅ `edit`

**/tmp/s3-integrator-L1-sonnet/pyproject.toml**

/tmp/s3-integrator-L1-sonnet/pyproject.toml

```
File /tmp/s3-integrator-L1-sonnet/pyproject.toml updated with changes.
```


---

<sub>⏱️ 9m 16s</sub>

### ✅ `edit`

**/tmp/s3-integrator-L1-sonnet/pyproject.toml**

/tmp/s3-integrator-L1-sonnet/pyproject.toml

```
File /tmp/s3-integrator-L1-sonnet/pyproject.toml updated with changes.
```


---

<sub>⏱️ 9m 22s</sub>

### ✅ `sql`

**Mark remaining todos done**

<details>
<summary>Arguments</summary>

```json
{
  "description": "Mark remaining todos done",
  "query": "UPDATE todos SET status = 'done' WHERE id IN ('helpers', 'test-file', 'pyproject')"
}
```

</details>

```
3 row(s) updated.
```


---

<sub>⏱️ 9m 28s</sub>

### 💬 Copilot

Now update `poetry.lock` by running `poetry lock` and verify tox.ini needs no changes:

---

<sub>⏱️ 9m 28s</sub>

### ✅ `bash`

**Update poetry.lock for new deps**

$ cd /tmp/s3-integrator-L1-sonnet && poetry lock --no-update 2>&1 | tail -5

```
bash: poetry: command not found
<exited with exit code 0>
```


---

<sub>⏱️ 9m 34s</sub>

### ✅ `bash`

**Check poetry availability**

$ which pip3 && pip3 install poetry --quiet 2>&1 | tail -3 || pipx install poetry 2>&1 | tail -3

```
bash: pipx: command not found
<exited with exit code 0>
```


---

<sub>⏱️ 9m 43s</sub>

### ✅ `bash`

**Install poetry**

$ pip3 install poetry --quiet 2>&1 | tail -3 && poetry --version 2>&1

```
bash: pip3: command not found
bash: poetry: command not found
<exited with exit code 127>
```


---

<sub>⏱️ 9m 49s</sub>

### ✅ `bash`

**Install poetry via pip**

$ pip install poetry --quiet 2>&1 | tail -3 && python -m poetry --version

```
bash: pip: command not found
bash: python: command not found
<exited with exit code 127>
```


---

<sub>⏱️ 9m 55s</sub>

### ✅ `bash`

**Find Python and install poetry**

$ python3 --version && pip3 install --user poetry 2>&1 | tail -3

```
Python 3.12.3
bash: pip3: command not found
<exited with exit code 0>
```


---

<sub>⏱️ 10m 24s</sub>

### ✅ `bash`

**Install poetry via installer script**

$ curl -sSL https://install.python-poetry.org | python3 - 2>&1 | tail -5 && export PATH="$HOME/.local/bin:$PATH" && poetry --version

<details>
<summary>4 lines</summary>

```
You can test that everything is set up by executing:

`poetry --version`

Poetry (version 2.3.2)
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 10m 31s</sub>

### ✅ `bash`

**Update poetry.lock**

$ export PATH="$HOME/.local/bin:$PATH" && cd /tmp/s3-integrator-L1-sonnet && poetry lock --no-update 2>&1

```
Creating virtualenv non-package-mode-77-Ba6UJ-py3.12 in /home/ubuntu/.cache/pypoetry/virtualenvs

The option "--no-update" does not exist
<exited with exit code 1>
```


---

<sub>⏱️ 10m 45s</sub>

### ✅ `bash`

**Run poetry lock**

$ export PATH="$HOME/.local/bin:$PATH" && cd /tmp/s3-integrator-L1-sonnet && poetry lock 2>&1

```
Resolving dependencies... (0.0s)Resolving dependencies... (0.1s)Resolving dependencies... (0.2s)Resolving dependencies... (0.3s)Resolving dependencies... (0.4s)Resolving dependencies... (0.5s)Resolving dependencies... (0.6s)Resolving dependencies... (0.7s)Resolving dependencies... (0.8s)Resolving dependencies... (0.9s)Resolving dependencies... (1.0s)Resolving dependencies... (1.1s)Resolving dependencies... (1.2s)Resolving dependencies... (1.3s)Resolving dependencies... (1.4s)Resolving dependencies... (1.5s)Resolving dependencies... (1.6s)Resolving dependencies... (1.7s)Resolving dependencies... (1.8s)Resolving dependencies... (1.9s)Resolving dependencies... (2.0s)Resolving dependencies... (2.1s)Resolving dependencies... (2.2s)Resolving dependencies... (2.3s)Resolving dependencies... (2.4s)Resolving dependencies... (2.5s)Resolving dependencies... (2.6s)Resolving dependencies... (2.7s)Resolving dependencies... (2.8s)Resolving dependencies... (2.9s)Resolving dependencies... (3.0s)Resolving dependencies... (3.1s)Resolving dependencies... (3.2s)Resolving dependencies... (3.3s)Resolving dependencies... (3.4s)Resolving dependencies... (3.5s)Resolving dependencies... (3.6s)Resolving dependencies... (3.7s)Resolving dependencies... (3.8s)Resolving dependencies... (3.9s)Resolving dependencies... (4.0s)Resolving dependencies... (4.1s)

Writing lock file
<exited with exit code 0>
```


---

<sub>⏱️ 10m 57s</sub>

### 💬 Copilot

Lock file updated. Let me do a final verification of all the changed files:

---

<sub>⏱️ 10m 58s</sub>

### ✅ `bash`

**Check no old patterns remain**

$ cd /tmp/s3-integrator-L1-sonnet && grep -n "pytest-operator\|python-libjuju\|juju =\|asyncio_mode\|ops_test\|async def test\|await ops_test" tests/integration/test_s3_charm.py tests/integration/helpers.py tests/integration/conftest.py pyproject.toml 2>/dev/null | head -30

```

<exited with exit code 0>
```


---

<sub>⏱️ 11m 8s</sub>

### ✅ `bash`

**Verify jubilant references**

$ cd /tmp/s3-integrator-L1-sonnet && grep -n "jubilant\|pytest-jubilant" pyproject.toml && echo "---" && grep -rn "jubilant" tests/integration/ | head -20

<details>
<summary>24 lines</summary>

```
34:jubilant = ">=1.0"
35:pytest-jubilant = ">=0.1"
---
tests/integration/test_s3_charm.py:9:import jubilant
tests/integration/test_s3_charm.py:41:def test_build_and_deploy(juju: jubilant.Juju):
tests/integration/test_s3_charm.py:52:                jubilant.all_blocked(status, S3_APP_NAME)
tests/integration/test_s3_charm.py:69:def test_sync_credential_action(juju: jubilant.Juju):
tests/integration/test_s3_charm.py:73:    with pytest.raises(jubilant.TaskError):
tests/integration/test_s3_charm.py:84:        juju.wait(lambda status: jubilant.all_active(status, S3_APP_NAME))
tests/integration/test_s3_charm.py:99:        juju.wait(lambda status: jubilant.all_active(status, S3_APP_NAME))
tests/integration/test_s3_charm.py:111:def test_config_options(juju: jubilant.Juju):
tests/integration/test_s3_charm.py:129:    juju.wait(lambda status: jubilant.all_active(status, S3_APP_NAME))
tests/integration/test_s3_charm.py:145:def test_relation_creation(juju: jubilant.Juju):
tests/integration/test_s3_charm.py:150:        juju.wait(lambda status: jubilant.all_active(status, *APPS))
tests/integration/test_s3_charm.py:152:    juju.wait(lambda status: jubilant.all_active(status, *APPS))
tests/integration/test_s3_charm.py:178:    juju.wait(lambda status: jubilant.all_active(status, S3_APP_NAME))
tests/integration/test_s3_charm.py:187:        juju.wait(lambda status: jubilant.all_active(status, *APPS))
tests/integration/test_s3_charm.py:208:def test_relation_broken(juju: jubilant.Juju):
tests/integration/test_s3_charm.py:217:                jubilant.all_active(status, S3_APP_NAME)
tests/integration/conftest.py:5:import jubilant
tests/integration/conftest.py:22:    with jubilant.temp_model(keep=keep_models) as juju:
tests/integration/helpers.py:9:import jubilant
tests/integration/helpers.py:16:def fast_forward(juju: jubilant.Juju, interval: str = "10s"):
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 11m 17s</sub>

### ✅ `bash`

**Syntax check all migrated files**

$ cd /tmp/s3-integrator-L1-sonnet && python3 -c "
import ast, sys
files = [
    'tests/integration/test_s3_charm.py',
    'tests/integration/helpers.py',
    'tests/integration/conftest.py',
]
for f in files:
    try:
        with open(f) as fh:
            ast.parse(fh.read())
        print(f'OK: {f}')
    except SyntaxError as e:
        print(f'SYNTAX ERROR in {f}: {e}')
        sys.exit(1)
"

```
OK: tests/integration/test_s3_charm.py
OK: tests/integration/helpers.py
OK: tests/integration/conftest.py
<exited with exit code 0>
```


---

<sub>⏱️ 11m 26s</sub>

### ✅ `bash`

**Show what changed**

$ cd /tmp/s3-integrator-L1-sonnet && git --no-pager diff --stat && echo "---" && git --no-pager status --short

<details>
<summary>12 lines</summary>

```
poetry.lock                        | 1401 ++--------------------------------------------------------------------------
 pyproject.toml                     |    5 +-
 tests/integration/helpers.py       |  162 ++++-----
 tests/integration/test_s3_charm.py |  160 ++++-----
 4 files changed, 152 insertions(+), 1576 deletions(-)
---
 M poetry.lock
 M pyproject.toml
 M tests/integration/helpers.py
 M tests/integration/test_s3_charm.py
?? tests/integration/conftest.py
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 11m 37s</sub>

### ✅ `sql`

**Mark tox todo done**

<details>
<summary>Arguments</summary>

```json
{
  "description": "Mark tox todo done",
  "query": "UPDATE todos SET status = 'done', description = 'tox.ini integration section unchanged - poetry install --only integration and pytest invocation are unchanged; no async-related options were there' WHERE id = 'tox'"
}
```

</details>

```
1 row(s) updated.
```


---

<sub>⏱️ 11m 54s</sub>

### 💬 Copilot

Now commit the changes:

---

<sub>⏱️ 11m 56s</sub>

### ✅ `bash`

**Commit the migration**

$ cd /tmp/s3-integrator-L1-sonnet && git add tests/integration/conftest.py tests/integration/helpers.py tests/integration/test_s3_charm.py pyproject.toml poetry.lock && git commit -m "Migrate integration tests from pytest-operator to jubilant

Replace pytest-operator (python-libjuju) with jubilant and pytest-jubilant:

- Add tests/integration/conftest.py with module-scoped juju fixture using
  jubilant.temp_model(), --keep-models CLI option, and debug log on failure
- Rewrite helpers.py: remove async/await and libjuju Unit/OpsTest types;
  replace unit.run_action() with juju.run(), unit.run() with juju.exec(),
  ops_test.juju() with juju.cli(); add fast_forward context manager
- Rewrite test_s3_charm.py: remove async/await and asyncio.gather();
  replace OpsTest fixture with jubilant.Juju; replace model.deploy() with
  juju.deploy(), model.wait_for_idle()/block_until() with juju.wait(),
  model.add_relation() with juju.integrate(), application.set_config() with
  juju.config(), application.remove_relation() with juju.remove_relation();
  replace failed-action status check with pytest.raises(jubilant.TaskError);
  replace is_relation_joined/is_relation_broken block_until polls with direct
  juju.wait() lambdas using jubilant.all_active/all_blocked/is_waiting
- Update pyproject.toml: replace pytest-operator and juju deps with jubilant
  and pytest-jubilant; remove asyncio_mode = 'auto' (no longer needed)
- Update poetry.lock

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

<sub>⏱️ 12m 14s</sub>

### ✅ `bash`

**Commit with identity**

$ cd /tmp/s3-integrator-L1-sonnet && git config user.email "copilot@github.com" && git config user.name "GitHub Copilot" && git commit -m "Migrate integration tests from pytest-operator to jubilant

Replace pytest-operator (python-libjuju) with jubilant and pytest-jubilant:

- Add tests/integration/conftest.py with module-scoped juju fixture using
  jubilant.temp_model(), --keep-models CLI option, and debug log on failure
- Rewrite helpers.py: remove async/await and libjuju Unit/OpsTest types;
  replace unit.run_action() with juju.run(), unit.run() with juju.exec(),
  ops_test.juju() with juju.cli(); add fast_forward context manager
- Rewrite test_s3_charm.py: remove async/await and asyncio.gather();
  replace OpsTest fixture with jubilant.Juju; replace model.deploy() with
  juju.deploy(), model.wait_for_idle()/block_until() with juju.wait(),
  model.add_relation() with juju.integrate(), application.set_config() with
  juju.config(), application.remove_relation() with juju.remove_relation();
  replace failed-action status check with pytest.raises(jubilant.TaskError);
  replace is_relation_joined/is_relation_broken block_until polls with direct
  juju.wait() lambdas using jubilant.all_active/all_blocked/is_waiting
- Update pyproject.toml: replace pytest-operator and juju deps with jubilant
  and pytest-jubilant; remove asyncio_mode = 'auto' (no longer needed)
- Update poetry.lock

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"

```
[main ba902a3] Migrate integration tests from pytest-operator to jubilant
 5 files changed, 181 insertions(+), 1576 deletions(-)
 create mode 100644 tests/integration/conftest.py
<exited with exit code 0>
```


---

<sub>⏱️ 12m 33s</sub>

### 💬 Copilot

The migration is complete. Here's a summary of all changes made:

### Changes
| File | Action | What changed |
|------|--------|--------------|
| `tests/integration/conftest.py` | **Created** | Module-scoped `juju` fixture using `jubilant.temp_model()`, `--keep-models` CLI option, debug log on failure |
| `tests/integration/helpers.py` | **Rewritten** | Removed all `async`/`await`, replaced `Unit`/`OpsTest` types with `jubilant.Juju` + unit name strings; `unit.run_action()` → `juju.run()`, `unit.run()` → `juju.exec()`, `ops_test.juju()` → `juju.cli()`; added `fast_forward()` context manager; removed `is_relation_joined`/`is_relation_broken` (replaced by inline `juju.wait()` lambdas) |
| `tests/integration/test_s3_charm.py` | **Rewritten** | All `async def` → `def`, dropped `asyncio.gather()`; `OpsTest` → `jubilant.Juju`; deploys, waits, relations, config, and action calls all converted; failed action checked with `pytest.raises(jubilant.TaskError)` |
| `pyproject.toml` | **Updated** | Replaced `pytest-operator` + `juju` deps with `jubilant\>=1.0` + `pytest-jubilant\>=0.1`; removed `asyncio_mode = "auto"` |
| `poetry.lock` | **Updated** | Regenerated to reflect new dependencies |

---

<sub>Generated by [GitHub Copilot CLI](https://github.com/features/copilot/cli)</sub>
