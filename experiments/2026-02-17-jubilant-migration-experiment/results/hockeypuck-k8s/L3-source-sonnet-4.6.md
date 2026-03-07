# 🤖 Copilot CLI Session

> **Session ID:** `f81b2698-8c86-426c-bdf5-eae362bb52a6`
> **Started:** 7 Mar 2026, 3:55:22 PM
> **Duration:** 8m 59s
> **Exported:** 7 Mar 2026, 4:04:22 PM

<sub>⏱️ 6s</sub>

### 👤 User

Migrate this charm's integration tests from pytest-operator (python-libjuju) to jubilant and pytest-jubilant. Update all test files, conftest.py, helpers, and dependencies.

Before starting, install jubilant and pytest-jubilant from PyPI (pip install jubilant pytest-jubilant) and read the source code to understand the API. The key modules are the Juju class, wait helpers (all_active, all_blocked, any_error), and the pytest-jubilant fixtures (pack, get_resources, juju fixture, temp_model_factory).

---

<sub>⏱️ 11s</sub>

### ✅ `view`

**/tmp/hockeypuck-k8s-L3-source-sonnet-4.6**

/tmp/hockeypuck-k8s-L3-source-sonnet-4.6

<details>
<summary>26 lines</summary>

```
.git
.github
.gitignore
.jujuignore
.licenserc.yaml
.trivyignore
.woke.yaml
CODEOWNERS
CONTRIBUTING.md
LICENSE
README.md
SECURITY.md
charmcraft.yaml
docs
hockeypuck_rock
icon.svg
lib
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

<sub>⏱️ 11s</sub>

### ✅ `bash`

**List all test files**

$ find /tmp/hockeypuck-k8s-L3-source-sonnet-4.6/tests -type f | sort

<details>
<summary>9 lines</summary>

```
/tmp/hockeypuck-k8s-L3-source-sonnet-4.6/tests/__init__.py
/tmp/hockeypuck-k8s-L3-source-sonnet-4.6/tests/conftest.py
/tmp/hockeypuck-k8s-L3-source-sonnet-4.6/tests/integration/__init__.py
/tmp/hockeypuck-k8s-L3-source-sonnet-4.6/tests/integration/conftest.py
/tmp/hockeypuck-k8s-L3-source-sonnet-4.6/tests/integration/pre_run_script.sh
/tmp/hockeypuck-k8s-L3-source-sonnet-4.6/tests/integration/test_charm.py
/tmp/hockeypuck-k8s-L3-source-sonnet-4.6/tests/unit/__init__.py
/tmp/hockeypuck-k8s-L3-source-sonnet-4.6/tests/unit/test_traefik_route_observer.py
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 17s</sub>

### ✅ `bash`

**Install jubilant and pytest-jubilant**

$ pip install jubilant pytest-jubilant 2>&1 | tail -20

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
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 16s</sub>

### ✅ `view`

**/tmp/hockeypuck-k8s-L3-source-sonnet-4.6/tests/integration/test_charm.py**

/tmp/hockeypuck-k8s-L3-source-sonnet-4.6/tests/integration/test_charm.py

<details>
<summary>243 lines</summary>

```
1. #!/usr/bin/env python3
2. 
3. # Copyright 2025 Canonical Ltd.
4. # See LICENSE file for licensing details.
5. 
6. """Integration tests."""
7. 
8. import json
9. import logging
10. import socket
11. import typing
12. from typing import Any
13. 
14. import pytest
15. import requests
16. from gnupg import GPG
17. from juju.application import Application
18. from juju.client._definitions import UnitStatus
19. 
20. from actions import HTTP_PORT, RECONCILIATION_PORT
21. 
22. logger = logging.getLogger(__name__)
23. 
24. 
25. @pytest.mark.abort_on_fail
26. @pytest.mark.usefixtures("hockeypuck_k8s_app")
27. async def test_hockeypuck_health(hockeypuck_url: str) -> None:
28.     """
29.     arrange: Build and deploy the Hockeypuck charm.
30.     act: Send a request to the main page.
31.     assert: Returns 200 and the page contains the title.
32.     """
33.     response = requests.get(
34.         f"{hockeypuck_url}/",
35.         timeout=5,
36.     )
37.     assert response.status_code == 200
38.     assert "<title>OpenPGP Keyserver</title>" in response.text
39. 
40. 
41. @pytest.mark.usefixtures("hockeypuck_k8s_app")
42. @pytest.mark.dependency(name="test_adding_records")
43. async def test_adding_records(gpg_key: Any, hockeypuck_url: str) -> None:
44.     """
45.     arrange: Create a GPG Key
46.     act: Send a request to add a PGP key and lookup the key using the API
47.     assert: API is added successfully and lookup of key returns the key.
48.     """
49.     gpg = GPG()
50.     fingerprint = gpg_key.fingerprint
51.     public_key = gpg.export_keys(fingerprint)
52.     response = requests.post(
53.         f"{hockeypuck_url}/pks/add",
54.         timeout=20,
55.         data={"keytext": public_key},
56.     )
57.     assert response.status_code == 200
58. 
59.     response = requests.get(
60.         f"{hockeypuck_url}/pks/lookup?op=get&search=0x{fingerprint}",
61.         timeout=20,
62.         headers={"Host": "hockeypuck.local"},
63.     )
64. 
65.     assert response.status_code == 200
66.     assert "BEGIN PGP PUBLIC KEY BLOCK" in response.text
67. 
68. 
69. @pytest.mark.dependency(depends=["test_adding_records"])
70. async def test_lookup_key(hockeypuck_k8s_app: Application, gpg_key: Any) -> None:
71.     """
72.     arrange: Deploy the Hockeypuck charm and create a GPG key.
73.     act: Execute the lookup-key action.
74.     assert: Action returns 0.
75.     """
76.     fingerprint = gpg_key.fingerprint
77.     action = await hockeypuck_k8s_app.units[0].run_action(
78.         "lookup-key", **{"keyword": f"0x{fingerprint}"}
79.     )
80.     await action.wait()
81.     assert action.results["return-code"] == 0
82.     assert "result" in action.results
83.     assert "BEGIN PGP PUBLIC KEY BLOCK" in action.results["result"]
84. 
85. 
86. async def test_lookup_key_not_found(hockeypuck_k8s_app: Application) -> None:
87.     """
88.     arrange: Deploy the Hockeypuck charm.
89.     act: Execute the lookup-key action with an invalid key.
90.     assert: Action raises a 404 error
91.     """
92.     fingerprint = "RANDOMKEY"
93.     action = await hockeypuck_k8s_app.units[0].run_action(
94.         "lookup-key", **{"keyword": f"0x{fingerprint}"}
95.     )
96.     await action.wait()
97.     assert "Not Found" in action.data["message"]
98. 
99. 
100. async def test_unit_limit(hockeypuck_k8s_app: Application) -> None:
101.     """
102.     arrange: Deploy the Hockeypuck charm.
103.     act: Add a unit to the application.
104.     assert: The application is blocked.
105.     """
106.     await hockeypuck_k8s_app.add_unit()
107.     await hockeypuck_k8s_app.model.wait_for_idle(status="blocked", apps=[hockeypuck_k8s_app.name])
108.     assert hockeypuck_k8s_app.status == "blocked"
109.     assert (
110.         hockeypuck_k8s_app.status_message == "Hockeypuck does not support multi-unit deployments"
111.     )
112.     await hockeypuck_k8s_app.scale(scale=1)
113.     await hockeypuck_k8s_app.model.wait_for_idle(status="active", apps=[hockeypuck_k8s_app.name])
114.     assert hockeypuck_k8s_app.status == "active"
115. 
116. 
117. @pytest.mark.usefixtures("external_peer_config")
118. @pytest.mark.dependency(depends=["test_adding_records"])
119. @pytest.mark.flaky(reruns=10, reruns_delay=10)
120. async def test_reconciliation(
121.     hockeypuck_secondary_app: Application,
122.     gpg_key: Any,
123. ) -> None:
124.     """
125.     arrange: Deploy the Hockeypuck charm in the secondary model and set up peering.
126.     act: Reconcile the application with the first hockeypuck server.
127.     assert: Key is present in the secondary model hockeypuck server.
128.     """
129.     status = await hockeypuck_secondary_app.model.get_status()
130.     hockeypuck_secondary_application = typing.cast(
131.         Application, status.applications[hockeypuck_secondary_app.name]
132.     )
133.     units = hockeypuck_secondary_application.units
134.     for unit in units.values():
135.         unit_status: UnitStatus = unit
136.         unit_address: str = (
137.             unit_status.address.decode()
138.             if isinstance(unit_status.address, bytes)
139.             else typing.cast(str, unit_status.address)
140.         )
141.         response = requests.get(
142.             f"http://{unit_address}:{HTTP_PORT}/pks/lookup"
143.             f"?op=get&search=0x{gpg_key.fingerprint}",
144.             timeout=20,
145.         )
146. 
147.         assert response.status_code == 200, f"Key not found in {unit_address}"
148.         assert "BEGIN PGP PUBLIC KEY BLOCK" in response.text, "Invalid response"
149. 
150. 
151. @pytest.mark.dependency(depends=["test_adding_records"])
152. async def test_block_keys_action(hockeypuck_secondary_app: Application, gpg_key: Any) -> None:
153.     """
154.     arrange: Deploy the Hockeypuck charm in the secondary model and set up peering.
155.     act: Execute the delete and blocklist action.
156.     assert: Lookup for the key returns 404.
157.     """
158.     fingerprint = gpg_key.fingerprint
159.     action = await hockeypuck_secondary_app.units[0].run_action(
160.         "block-keys", **{"fingerprints": fingerprint, "comment": "R1234"}
161.     )
162.     await action.wait()
163.     assert action.results["return-code"] == 0
164. 
165.     status = await hockeypuck_secondary_app.model.get_status()
166.     hockeypuck_secondary_application = typing.cast(
167.         Application, status.applications[hockeypuck_secondary_app.name]
168.     )
169.     for unit in hockeypuck_secondary_application.units.values():
170.         unit_status: UnitStatus = unit
171.         unit_address: str = (
172.             unit_status.address.decode()
173.             if isinstance(unit_status.address, bytes)
174.             else typing.cast(str, unit_status.address)
175.         )
176.         response = requests.get(
177.             f"http://{unit_address}:{HTTP_PORT}/pks/lookup"
178.             f"?op=get&search=0x{gpg_key.fingerprint}",
179.             timeout=20,
180.         )
181. 
182.         assert response.status_code == 404
183. 
184. 
185. @pytest.mark.dependency(depends=["test_adding_records"])
186. async def test_block_keys_action_multiple(hockeypuck_k8s_app: Application, gpg_key: Any) -> None:
187.     """
188.     arrange: Deploy the Hockeypuck charm.
189.     act: Execute the delete and blocklist action with multiple keys (one valid and present,
190.     one invalid, one valid but not present).
191.     assert: Action returns 0 and event result contains the status of each key.
192.     """
193.     fingerprint1 = str(gpg_key.fingerprint).lower()  # valid key that is present in the database
194.     fingerprint2 = "eaf2dd785260ec0cd047f463e449a664b36b34b1"  # valid key that is not present
195.     fingerprint3 = "shbfsdiuf98hu"  # invalid key
196.     action = await hockeypuck_k8s_app.units[0].run_action(
197.         "block-keys",
198.         **{"fingerprints": f"{fingerprint1},{fingerprint2},{fingerprint3}", "comment": "R1234"},
199.     )
200.     await action.wait()
201.     expected_result = {}
202.     expected_result[fingerprint1] = "Deleted and blocked successfully."
203.     expected_result[fingerprint2] = "Fingerprint unavailable in the database."
204.     expected_result[fingerprint3] = (
205.         "Invalid fingerprint format. "
206.         "Fingerprints must be 40 or 64 characters long and "
207.         "consist of hexadecimal characters only."
208.     )
209.     assert action.results[fingerprint1] == expected_result[fingerprint1]
210.     assert action.results[fingerprint2] == expected_result[fingerprint2]
211.     assert action.results[fingerprint3] == expected_result[fingerprint3]
212. 
213. 
214. async def test_rebuild_prefix_tree_action(hockeypuck_k8s_app: Application) -> None:
215.     """
216.     arrange: Deploy the Hockeypuck charm and integrate with Postgres and Traefik.
217.     act: Execute the rebuild prefix tree action.
218.     assert: Action returns 0.
219.     """
220.     action = await hockeypuck_k8s_app.units[0].run_action("rebuild-prefix-tree")
221.     await action.wait()
222.     assert action.results["return-code"] == 0
223. 
224. 
225. async def test_traefik_route_integration(traefik_app: Application) -> None:
226.     """
227.     arrange: Deploy the traefik-k8s charm and integrate with Hockeypuck.
228.     act: Test connectivity to the reconciliation port.
229.     assert: Connection request is successful.
230.     """
231.     action = await traefik_app.units[0].run_action("show-proxied-endpoints")
232.     await action.wait()
233.     assert action.results["return-code"] == 0
234.     result = json.loads(action.results["proxied-endpoints"])
235.     host = result["traefik-k8s"]["url"].removeprefix("http://")
236.     port = RECONCILIATION_PORT
237.     try:
238.         with socket.create_connection((host, port), timeout=5):
239.             connected = True
240.     except (socket.timeout, socket.error):
241.         connected = False
242.     assert connected, f"Failed to connect to {host}:{port}"
243.
```

</details>


---

<sub>⏱️ 16s</sub>

### ✅ `view`

**/tmp/hockeypuck-k8s-L3-source-sonnet-4.6/tests/integration/conftest.py**

/tmp/hockeypuck-k8s-L3-source-sonnet-4.6/tests/integration/conftest.py

<details>
<summary>204 lines</summary>

```
1. # Copyright 2025 Canonical Ltd.
2. # See LICENSE file for licensing details.
3. 
4. """Fixtures for hockeypuck-k8s tests."""
5. 
6. import json
7. import logging
8. import secrets
9. from pathlib import Path
10. from typing import Any
11. 
12. import gnupg
13. import pytest_asyncio
14. from juju.application import Application
15. from juju.model import Model
16. from pytest import Config
17. from pytest_operator.plugin import OpsTest
18. 
19. from actions import HTTP_PORT, METRICS_PORT, RECONCILIATION_PORT
20. from admin_gpg import PASSWORD_ALPHABET
21. 
22. logger = logging.getLogger(__name__)
23. 
24. 
25. @pytest_asyncio.fixture(scope="module", name="model")
26. async def model_fixture(ops_test: OpsTest) -> Model:
27.     """Return the current testing juju model."""
28.     assert ops_test.model
29.     return ops_test.model
30. 
31. 
32. @pytest_asyncio.fixture(scope="module", name="secondary_model_alias")
33. async def secondary_model_fixture(ops_test: OpsTest) -> str:
34.     """Create a secondary Juju model for external peer reconcilitation."""
35.     model_alias = "secondary-model"
36.     model_name = "hockeypuck-secondary"
37.     await ops_test.track_model(model_alias, model_name=model_name)
38.     return model_alias
39. 
40. 
41. @pytest_asyncio.fixture(scope="module", name="postgresql_app")
42. async def postgresql_app_fixture(
43.     model: Model,
44. ) -> Application:
45.     """Deploy postgresql-k8s charm."""
46.     app = await model.deploy(
47.         "postgresql-k8s",
48.         channel="14/stable",
49.         trust=True,
50.     )
51.     await model.wait_for_idle(status="active", apps=[app.name])
52.     return app
53. 
54. 
55. @pytest_asyncio.fixture(scope="module", name="traefik_app")
56. async def traefik_app_fixture(
57.     model: Model,
58. ) -> Application:
59.     """Deploy traefik-k8s charm."""
60.     traefik_app = await model.deploy(
61.         "traefik-k8s",
62.         channel="latest/stable",
63.         trust=True,
64.     )
65.     await model.wait_for_idle(status="active", apps=[traefik_app.name])
66.     return traefik_app
67. 
68. 
69. @pytest_asyncio.fixture(scope="module", name="hockeypuck_url")
70. async def hockeypuck_url_fixture(
71.     traefik_app: Application,
72. ) -> str:
73.     """Get the endpoint proxied by Traefik."""
74.     action = await traefik_app.units[0].run_action("show-proxied-endpoints")
75.     await action.wait()
76.     proxied_endpoints = json.loads(action.results.get("proxied-endpoints"))
77.     hockeypuck_url = proxied_endpoints["hockeypuck-k8s"]["url"]
78.     return hockeypuck_url
79. 
80. 
81. @pytest_asyncio.fixture(scope="module", name="hockeypuck_charm")
82. async def hockeypuck_charm_fixture(pytestconfig: Config, ops_test: OpsTest) -> str | Path:
83.     """Get value from parameter charm-file."""
84.     charm = pytestconfig.getoption("--charm-file")
85.     if not charm:
86.         charm = await ops_test.build_charm(".")
87.         assert charm, "Charm not built"
88.         return charm
89.     return charm
90. 
91. 
92. @pytest_asyncio.fixture(scope="module", name="hockeypuck_app_image")
93. async def hockeypuck_app_image_fixture(pytestconfig: Config) -> str:
94.     """Get value from parameter rock-file."""
95.     rock = pytestconfig.getoption("--hockeypuck-image")
96.     assert rock, "--hockeypuck-image must be set"
97.     return rock
98. 
99. 
100. @pytest_asyncio.fixture(scope="module", name="hockeypuck_k8s_app")
101. async def hockeypuck_k8s_app_fixture(
102.     model: Model,
103.     hockeypuck_charm: str | Path,
104.     hockeypuck_app_image: str,
105.     traefik_app: Application,
106.     postgresql_app: Application,
107. ) -> Application:
108.     """Deploy the hockeypuck-k8s application, relates with Postgresql and Traefik."""
109.     resources = {
110.         "app-image": hockeypuck_app_image,
111.     }
112.     app = await model.deploy(
113.         f"./{hockeypuck_charm}",
114.         resources=resources,
115.         config={
116.             "app-port": HTTP_PORT,
117.             "metrics-port": METRICS_PORT,
118.         },
119.     )
120.     await model.add_relation(app.name, postgresql_app.name)
121.     await model.add_relation(app.name, f"{traefik_app.name}:ingress")
122.     await model.add_relation(app.name, f"{traefik_app.name}:traefik-route")
123.     await model.wait_for_idle(status="active")
124.     return app
125. 
126. 
127. @pytest_asyncio.fixture(scope="module", name="gpg_key")
128. def gpg_key_fixture() -> Any:
129.     """Return a GPG key."""
130.     gpg = gnupg.GPG()
131.     password = "".join(secrets.choice(PASSWORD_ALPHABET) for _ in range(10))
132.     input_data = gpg.gen_key_input(
133.         key_type="RSA",
134.         key_length=2048,
135.         name_real="Test User",
136.         name_email="test@gmail.com",
137.         passphrase=password,
138.     )
139.     key = gpg.gen_key(input_data)
140.     if not key.fingerprint:
141.         raise RuntimeError("GPG key generation failed.")
142.     return key
143. 
144. 
145. @pytest_asyncio.fixture(scope="module", name="hockeypuck_secondary_app")
146. async def hockeypuck_secondary_app_fixture(
147.     secondary_model_alias: str,
148.     hockeypuck_charm: str | Path,
149.     hockeypuck_app_image: str,
150.     ops_test: OpsTest,
151. ) -> Application:
152.     """Deploy the hockeypuck-k8s application in the secondary model and relate with Postgresql"""
153.     resources = {
154.         "app-image": hockeypuck_app_image,
155.     }
156.     # Switch context to the new model
157.     with ops_test.model_context(secondary_model_alias) as secondary_model:
158.         app = await secondary_model.deploy(
159.             f"./{hockeypuck_charm}",
160.             resources=resources,
161.             config={
162.                 "app-port": HTTP_PORT,
163.                 "metrics-port": METRICS_PORT,
164.             },
165.         )
166.         postgresql_app = await secondary_model.deploy(
167.             "postgresql-k8s",
168.             channel="14/stable",
169.             trust=True,
170.         )
171.         await secondary_model.wait_for_idle(status="active", apps=[postgresql_app.name])
172.         await secondary_model.add_relation(app.name, postgresql_app.name)
173.         await secondary_model.wait_for_idle(status="active")
174.         return app
175. 
176. 
177. @pytest_asyncio.fixture(scope="module", name="external_peer_config")
178. async def external_peer_config_fixture(
179.     hockeypuck_k8s_app: Application,
180.     hockeypuck_secondary_app: Application,
181. ) -> None:
182.     """Set external peers on both hockeypuck servers for peer reconciliation."""
183.     # <unit-name>.<app-name>-endpoints.<model-name>.svc.cluster.local
184.     primary_unit_name = (hockeypuck_k8s_app.units[0].name).replace("/", "-")
185.     hockeypuck_primary_fqdn = (
186.         f"{primary_unit_name}."
187.         f"{hockeypuck_k8s_app.name}-endpoints."
188.         f"{hockeypuck_k8s_app.model.name}.svc.cluster.local"
189.     )
190.     primary_config = f"{hockeypuck_primary_fqdn},{HTTP_PORT},{RECONCILIATION_PORT}"
191.     await hockeypuck_secondary_app.set_config({"external-peers": primary_config})
192. 
193.     secondary_unit_name = (hockeypuck_secondary_app.units[0].name).replace("/", "-")
194.     hockeypuck_secondary_fqdn = (
195.         f"{secondary_unit_name}."
196.         f"{hockeypuck_secondary_app.name}-endpoints."
197.         f"{hockeypuck_secondary_app.model.name}.svc.cluster.local"
198.     )
199.     secondary_config = f"{hockeypuck_secondary_fqdn},{HTTP_PORT},{RECONCILIATION_PORT}"
200.     await hockeypuck_k8s_app.set_config({"external-peers": secondary_config})
201. 
202.     await hockeypuck_k8s_app.model.wait_for_idle(status="active")
203.     await hockeypuck_secondary_app.model.wait_for_idle(status="active")
204.
```

</details>


---

<sub>⏱️ 16s</sub>

### ✅ `view`

**/tmp/hockeypuck-k8s-L3-source-sonnet-4.6/tests/conftest.py**

/tmp/hockeypuck-k8s-L3-source-sonnet-4.6/tests/conftest.py

<details>
<summary>19 lines</summary>

```
1. # Copyright 2025 Canonical Ltd.
2. # See LICENSE file for licensing details.
3. 
4. """Additional pytest options for tests."""
5. 
6. from pytest import Parser
7. 
8. 
9. def pytest_addoption(parser: Parser) -> None:
10.     """Parse additional pytest options.
11. 
12.     Args:
13.         parser: Pytest parser.
14.     """
15.     parser.addoption(
16.         "--hockeypuck-image", action="store", help="Hockeypuck app image to be deployed"
17.     )
18.     parser.addoption("--charm-file", action="store", help="Charm file to be deployed")
19.
```

</details>


---

<sub>⏱️ 22s</sub>

### ✅ `view`

**/tmp/hockeypuck-k8s-L3-source-sonnet-4.6/pyproject.toml**

/tmp/hockeypuck-k8s-L3-source-sonnet-4.6/pyproject.toml

<details>
<summary>81 lines</summary>

```
1. [tool.bandit]
2. exclude_dirs = ["/venv/"]
3. [tool.bandit.assert_used]
4. skips = ["*/*test.py", "*/test_*.py", "*tests/*.py"]
5. 
6. # Testing tools configuration
7. [tool.coverage.run]
8. branch = true
9. 
10. # Formatting tools configuration
11. [tool.black]
12. line-length = 99
13. target-version = ["py38"]
14. 
15. [tool.coverage.report]
16. show_missing = true
17. 
18. # Linting tools configuration
19. [tool.flake8]
20. max-line-length = 99
21. max-doc-length = 99
22. max-complexity = 10
23. exclude = [".git", "__pycache__", ".tox", "build", "dist", "*.egg_info", "venv"]
24. select = ["E", "W", "F", "C", "N", "R", "D", "H"]
25. # Ignore W503, E501 because using black creates errors with this
26. # Ignore D107 Missing docstring in __init__
27. ignore = ["W503", "E501", "D107"]
28. # D100, D101, D102, D103: Ignore missing docstrings in tests
29. per-file-ignores = ["tests/*:D100,D101,D102,D103,D104,D205,D212,D415"]
30. docstring-convention = "google"
31. 
32. [tool.isort]
33. line_length = 99
34. profile = "black"
35. 
36. [tool.mypy]
37. check_untyped_defs = true
38. disallow_untyped_defs = true
39. explicit_package_bases = true
40. ignore_missing_imports = true
41. namespace_packages = true
42. 
43. [[tool.mypy.overrides]]
44. disallow_untyped_defs = false
45. module = "tests.*"
46. 
47. [tool.pylint]
48. disable = "wrong-import-order"
49. 
50. [tool.pytest.ini_options]
51. minversion = "6.0"
52. log_cli_level = "INFO"
53. addopts = "--strict-markers"
54. 
55. # Linting tools configuration
56. [tool.ruff]
57. line-length = 99
58. select = ["E", "W", "F", "C", "N", "D", "I001"]
59. extend-ignore = [
60.     "D203",
61.     "D204",
62.     "D213",
63.     "D215",
64.     "D400",
65.     "D404",
66.     "D406",
67.     "D407",
68.     "D408",
69.     "D409",
70.     "D413",
71. ]
72. ignore = ["E501", "D107"]
73. extend-exclude = ["__pycache__", "*.egg_info"]
74. per-file-ignores = {"tests/*" = ["D100","D101","D102","D103","D104"]}
75. 
76. [tool.ruff.mccabe]
77. max-complexity = 10
78. 
79. [tool.codespell]
80. skip = "build,lib,venv,icon.svg,.tox,.git,.mypy_cache,.ruff_cache,.coverage"
81.
```

</details>


---

<sub>⏱️ 22s</sub>

### ✅ `view`

**/tmp/hockeypuck-k8s-L3-source-sonnet-4.6/tox.ini**

/tmp/hockeypuck-k8s-L3-source-sonnet-4.6/tox.ini

<details>
<summary>117 lines</summary>

```
1. # Copyright 2025 Canonical Ltd.
2. # See LICENSE file for licensing details.
3. 
4. [tox]
5. skipsdist=True
6. skip_missing_interpreters = True
7. envlist = lint, unit, static, coverage-report
8. 
9. [vars]
10. src_path = {toxinidir}/src/
11. tst_path = {toxinidir}/tests/
12. rock_files_path = {toxinidir}/hockeypuck_rock/
13. all_path = {[vars]src_path} {[vars]tst_path} {[vars]rock_files_path}
14. 
15. [testenv]
16. setenv =
17.   PYTHONPATH = {toxinidir}:{toxinidir}/lib:{[vars]src_path}
18.   PYTHONBREAKPOINT=ipdb.set_trace
19.   PY_COLORS=1
20. passenv =
21.   PYTHONPATH
22.   CHARM_BUILD_DIR
23.   MODEL_SETTINGS
24. 
25. [testenv:fmt]
26. description = Apply coding style standards to code
27. deps =
28.     black
29.     isort
30. commands =
31.     isort {[vars]all_path}
32.     black {[vars]all_path}
33. 
34. [testenv:lint]
35. description = Check code against coding style standards
36. deps =
37.     black
38.     codespell
39.     flake8
40.     flake8-builtins
41.     flake8-copyright
42.     flake8-docstrings
43.     flake8-docstrings-complete
44.     flake8-test-docs
45.     gnupg
46.     isort
47.     mypy
48.     pep8-naming
49.     psycopg2-binary
50.     pydocstyle>=2.10
51.     pylint
52.     pyproject-flake8
53.     pytest
54.     pytest-asyncio
55.     pytest-operator
56.     requests
57.     types-PyYAML
58.     types-requests
59.     -r{toxinidir}/requirements.txt
60. commands =
61.     pydocstyle {[vars]src_path}
62.     # uncomment the following line if this charm owns a lib
63.     # codespell {[vars]lib_path}
64.     codespell {toxinidir} --skip {toxinidir}/.git --skip {toxinidir}/.tox \
65.       --skip {toxinidir}/build --skip {toxinidir}/lib --skip {toxinidir}/venv \
66.       --skip {toxinidir}/.mypy_cache --skip {toxinidir}/icon.svg
67.     # pflake8 wrapper supports config from pyproject.toml
68.     pflake8 {[vars]all_path} --ignore=W503
69.     isort --check-only --diff {[vars]all_path}
70.     black --check --diff {[vars]all_path}
71.     mypy {[vars]all_path}
72.     pylint {[vars]all_path}
73. 
74. [testenv:unit]
75. description = Run unit tests
76. deps =
77.     coverage[toml]
78.     pytest
79.     -r{toxinidir}/requirements.txt
80. commands =
81.     coverage run --source={[vars]src_path} \
82.         -m pytest --ignore={[vars]tst_path}integration -v --tb native -s {posargs}
83.     coverage report
84. 
85. [testenv:coverage-report]
86. description = Create test coverage report
87. deps =
88.     coverage[toml]
89.     pytest
90.     -r{toxinidir}/requirements.txt
91. commands =
92.     coverage report
93. 
94. [testenv:static]
95. description = Run static analysis tests
96. deps =
97.     bandit[toml]
98.     -r{toxinidir}/requirements.txt
99. commands =
100.     bandit -c {toxinidir}/pyproject.toml -r {[vars]src_path} {[vars]tst_path}
101. 
102. [testenv:integration]
103. description = Run integration tests
104. deps =
105.     -r{toxinidir}/requirements.txt
106.     allure-pytest>=2.8.18
107.     git+https://github.com/canonical/data-platform-workflows@v24.0.0\#subdirectory=python/pytest_plugins/allure_pytest_collection_report
108.     gnupg
109.     pytest
110.     pytest-asyncio
111.     pytest-dependency
112.     pytest-operator
113.     pytest-rerunfailures
114.     python-gnupg
115. commands =
116.     pytest -v --tb native --ignore={[vars]tst_path}unit --log-cli-level=INFO -s {posargs}
117.
```

</details>


---

<sub>⏱️ 22s</sub>

### ✅ `view`

**/tmp/hockeypuck-k8s-L3-source-sonnet-4.6/requirements.txt**

/tmp/hockeypuck-k8s-L3-source-sonnet-4.6/requirements.txt

<details>
<summary>6 lines</summary>

```
1. ops==3.6.0
2. paas-charm==1.10.0
3. python-gnupg==0.5.6
4. requests==2.32.5
5. setuptools==82.0.0
6.
```

</details>


---

<sub>⏱️ 27s</sub>

### ✅ `bash`

**Install jubilant and pytest-jubilant**

$ pip install jubilant pytest-jubilant --break-system-packages 2>&1 | tail -20

<details>
<summary>10 lines</summary>

```
Defaulting to user installation because normal site-packages is not writeable
Requirement already satisfied: jubilant in /home/ubuntu/.local/lib/python3.12/site-packages (1.7.0)
Requirement already satisfied: pytest-jubilant in /home/ubuntu/.local/lib/python3.12/site-packages (1.1)
Requirement already satisfied: PyYAML==6.* in /usr/lib/python3/dist-packages (from jubilant) (6.0.1)
Requirement already satisfied: pytest>=8.3.5 in /home/ubuntu/.local/lib/python3.12/site-packages (from pytest-jubilant) (9.0.2)
Requirement already satisfied: iniconfig>=1.0.1 in /home/ubuntu/.local/lib/python3.12/site-packages (from pytest>=8.3.5->pytest-jubilant) (2.3.0)
Requirement already satisfied: packaging>=22 in /usr/lib/python3/dist-packages (from pytest>=8.3.5->pytest-jubilant) (24.0)
Requirement already satisfied: pluggy<2,>=1.5 in /home/ubuntu/.local/lib/python3.12/site-packages (from pytest>=8.3.5->pytest-jubilant) (1.6.0)
Requirement already satisfied: pygments>=2.7.2 in /usr/lib/python3/dist-packages (from pytest>=8.3.5->pytest-jubilant) (2.17.2)
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 34s</sub>

### ✅ `bash`

**Read jubilant API docs**

$ python3 -c "import jubilant; help(jubilant)" 2>&1 | head -200

<details>
<summary>196 lines</summary>

```
Help on package jubilant:

NAME
    jubilant - Jubilant is a Pythonic wrapper around the Juju CLI.

PACKAGE CONTENTS
    _all_any
    _juju
    _pretty
    _task
    _test_helpers
    _version
    _yaml
    modeltypes
    secrettypes
    statustypes

CLASSES
    builtins.Exception(builtins.BaseException)
        jubilant._juju.WaitError
        jubilant._task.TaskError
    builtins.object
        jubilant._juju.Juju
        jubilant._task.Task
        jubilant._version.Version
        jubilant.modeltypes.ModelInfo
        jubilant.secrettypes.Secret
            jubilant.secrettypes.RevealedSecret
        jubilant.statustypes.Status
    builtins.str(builtins.object)
        jubilant.secrettypes.SecretURI
    subprocess.CalledProcessError(subprocess.SubprocessError)
        jubilant._juju.CLIError

    class CLIError(subprocess.CalledProcessError)
     |  CLIError(returncode, cmd, output=None, stderr=None)
     |
     |  Subclass of ``CalledProcessError`` that includes stdout and stderr in the ``__str__``.
     |
     |  Method resolution order:
     |      CLIError
     |      subprocess.CalledProcessError
     |      subprocess.SubprocessError
     |      builtins.Exception
     |      builtins.BaseException
     |      builtins.object
     |
     |  Methods defined here:
     |
     |  __str__(self) -> 'str'
     |      Return str(self).
     |
     |  ----------------------------------------------------------------------
     |  Methods inherited from subprocess.CalledProcessError:
     |
     |  __init__(self, returncode, cmd, output=None, stderr=None)
     |      Initialize self.  See help(type(self)) for accurate signature.
     |
     |  ----------------------------------------------------------------------
     |  Data descriptors inherited from subprocess.CalledProcessError:
     |
     |  stdout
     |      Alias for output attribute, to match stderr
     |
     |  ----------------------------------------------------------------------
     |  Data descriptors inherited from subprocess.SubprocessError:
     |
     |  __weakref__
     |      list of weak references to the object
     |
     |  ----------------------------------------------------------------------
     |  Static methods inherited from builtins.Exception:
     |
     |  __new__(*args, **kwargs) class method of builtins.Exception
     |      Create and return a new object.  See help(type) for accurate signature.
     |
     |  ----------------------------------------------------------------------
     |  Methods inherited from builtins.BaseException:
     |
     |  __delattr__(self, name, /)
     |      Implement delattr(self, name).
     |
     |  __getattribute__(self, name, /)
     |      Return getattr(self, name).
     |
     |  __reduce__(...)
     |      Helper for pickle.
     |
     |  __repr__(self, /)
     |      Return repr(self).
     |
     |  __setattr__(self, name, value, /)
     |      Implement setattr(self, name, value).
     |
     |  __setstate__(...)
     |
     |  add_note(...)
     |      Exception.add_note(note) --
     |      add a note to the exception
     |
     |  with_traceback(...)
     |      Exception.with_traceback(tb) --
     |      set self.__traceback__ to tb and return self.
     |
     |  ----------------------------------------------------------------------
     |  Data descriptors inherited from builtins.BaseException:
     |
     |  __cause__
     |      exception cause
     |
     |  __context__
     |      exception context
     |
     |  __dict__
     |
     |  __suppress_context__
     |
     |  __traceback__
     |
     |  args

    class Juju(builtins.object)
     |  Juju(*, model: 'str | None' = None, wait_timeout: 'float' = 180.0, cli_binary: 'str | pathlib.Path | None' = None)
     |
     |  Instantiate this class to run Juju commands.
     |
     |  Most methods directly call a single Juju CLI command. If a CLI command doesn't yet exist as a
     |  method, use :meth:`cli`.
     |
     |  Example::
     |
     |      juju = jubilant.Juju()
     |      juju.deploy('snappass-test')
     |
     |  Args:
     |      model: If specified, operate on this Juju model, otherwise use the current Juju model.
     |          If the model is in another controller, prefix the model name with ``<controller>:``.
     |      wait_timeout: The default timeout for :meth:`wait` (in seconds) if that method's *timeout*
     |          parameter is not specified.
     |      cli_binary: Path to the Juju CLI binary. If not specified, uses ``juju`` and assumes it is
     |          in the PATH.
     |
     |  Methods defined here:
     |
     |  __init__(self, *, model: 'str | None' = None, wait_timeout: 'float' = 180.0, cli_binary: 'str | pathlib.Path | None' = None)
     |      Initialize self.  See help(type(self)) for accurate signature.
     |
     |  __repr__(self) -> 'str'
     |      Return repr(self).
     |
     |  add_credential(self, cloud: 'str', credential: 'str | pathlib.Path | Mapping[str, Any]', *, client: 'bool' = False, controller: 'str | None' = None, region: 'str | None' = None) -> 'None'
     |      Add a credential for a cloud.
     |
     |      Args:
     |          cloud: Name of the cloud to add credentials for.
     |          credential: Path to a YAML file containing credential to add, or a mapping
     |              representing the parsed credential YAML (``{'credentials': ...}``).
     |          client: Set to True to save credentials on the client, meaning controllers
     |              created later will have access to them. You must specify ``client=True``
     |              or provide *controller* (or both).
     |          controller: If specified, save credentials to the named controller.
     |          region: Cloud region that the credential is valid for.
     |
     |  add_model(self, model: 'str', cloud: 'str | None' = None, *, controller: 'str | None' = None, config: 'Mapping[str, ConfigValue] | None' = None, credential: 'str | None' = None) -> 'None'
     |      Add a named model and set this instance's model to it.
     |
     |      To avoid interfering with CLI users, this won't switch the Juju CLI to the
     |      newly-created model. However, because :attr:`model` is set to the name of the new
     |      model, all subsequent operations on this instance will use the new model.
     |
     |      Args:
     |          model: Name of model to add.
     |          cloud: Name of cloud or region (or cloud/region) to use for the model.
     |          controller: Name of controller to operate in. If not specified, use the current
     |              controller.
     |          config: Model configuration as key-value pairs, for example,
     |              ``{'image-stream': 'daily'}``.
     |          credential: Name of cloud credential to use for the model.
     |
     |  add_secret(self, name: 'str', content: 'Mapping[str, str]', *, info: 'str | None' = None) -> 'SecretURI'
     |      Add a new named secret and return its secret URI.
     |
     |      Args:
     |          name: Name for the secret.
     |          content: Key-value pairs that represent the secret content, for example
     |              ``{'password': 'hunter2'}``.
     |          info: Description for the secret.
     |
     |  add_ssh_key(self, *keys: 'str') -> 'None'
     |      Add one or more SSH keys to the model.
     |
     |      The SSH keys are added to all current and future machines in the model.
     |
     |      Args:
     |          keys: SSH public key or keys to add. Each key should be the full
     |              SSH public key string (for example, ``ssh-rsa AAAAB3... user@host``).
     |
     |  add_unit(self, app: 'str', *, attach_storage: 'str | Iterable[str] | None' = None, num_units: 'int' = 1, to: 'str | Iterable[str] | None' = None)
     |      Add one or more units to a deployed application.
     |
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 34s</sub>

### ✅ `bash`

**Read pytest-jubilant API docs**

$ python3 -c "import pytest_jubilant; help(pytest_jubilant)" 2>&1 | head -200

<details>
<summary>16 lines</summary>

```
Help on package pytest_jubilant:

NAME
    pytest_jubilant - Welcome to pytest-jubilant!

PACKAGE CONTENTS
    main
    version

FUNCTIONS
    get_resources(root: Union[pathlib.Path, str] = './') -> Optional[Dict[str, str]]
        Obtain the charm resources from metadata.yaml's upstream-source fields.

    pack(root: Union[pathlib.Path, str] = './', platform: Optional[str] = None) -> pathlib.Path
        Pack a local charm and return it.

DATA
    __all__ = ['pack', 'get_resources']

FILE
    /home/ubuntu/.local/lib/python3.12/site-packages/pytest_jubilant/__init__.py
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 41s</sub>

### ✅ `bash`

**List Juju methods**

$ python3 -c "
from jubilant import Juju
import inspect
# Show key methods
methods = [m for m in dir(Juju) if not m.startswith('_')]
print('Juju methods:', methods)
"

```
Juju methods: ['add_credential', 'add_model', 'add_secret', 'add_ssh_key', 'add_unit', 'bootstrap', 'cli', 'config', 'consume', 'debug_log', 'deploy', 'destroy_model', 'exec', 'grant_secret', 'integrate', 'model_config', 'model_constraints', 'offer', 'refresh', 'remove_application', 'remove_relation', 'remove_secret', 'remove_ssh_key', 'remove_unit', 'run', 'scp', 'secrets', 'show_model', 'show_secret', 'ssh', 'status', 'trust', 'update_secret', 'version', 'wait']
<exited with exit code 0>
```


---

<sub>⏱️ 41s</sub>

### ✅ `bash`

**Show jubilant wait helpers**

$ python3 -c "
import jubilant
# Show wait helpers
print(dir(jubilant))
print('---')
import inspect
print(inspect.getsource(jubilant._all_any))
"

<details>
<summary>154 lines</summary>

```
['CLIError', 'ConfigValue', 'Juju', 'ModelInfo', 'RevealedSecret', 'Secret', 'SecretURI', 'Status', 'Task', 'TaskError', 'Version', 'WaitError', '__all__', '__builtins__', '__cached__', '__doc__', '__file__', '__loader__', '__name__', '__package__', '__path__', '__spec__', '__version__', '_all_any', '_juju', '_pretty', '_task', '_test_helpers', '_version', '_yaml', 'all_active', 'all_agents_idle', 'all_blocked', 'all_error', 'all_maintenance', 'all_waiting', 'any_active', 'any_blocked', 'any_error', 'any_maintenance', 'any_waiting', 'modeltypes', 'secrettypes', 'statustypes', 'temp_model']
---
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

<sub>⏱️ 49s</sub>

### ✅ `bash`

**Read key Juju method signatures**

$ python3 -c "
import jubilant
import inspect
# Show Juju.deploy, Juju.wait, Juju.run, Juju.integrate signatures
for method in ['deploy', 'wait', 'run', 'integrate', 'config', 'add_unit', 'remove_unit', 'status']:
    sig = inspect.signature(getattr(jubilant.Juju, method))
    print(f'Juju.{method}{sig}')
print()
# Show Juju.run source
print(inspect.getsource(jubilant.Juju.run))
"

<details>
<summary>79 lines</summary>

```
Juju.deploy(self, charm: 'str | pathlib.Path', app: 'str | None' = None, *, attach_storage: 'str | Iterable[str] | None' = None, base: 'str | None' = None, bind: 'Mapping[str, str] | str | None' = None, channel: 'str | None' = None, config: 'Mapping[str, ConfigValue] | None' = None, constraints: 'Mapping[str, str] | None' = None, force: 'bool' = False, num_units: 'int' = 1, overlays: 'Iterable[str | pathlib.Path]' = (), resources: 'Mapping[str, str] | None' = None, revision: 'int | None' = None, storage: 'Mapping[str, str] | None' = None, to: 'str | Iterable[str] | None' = None, trust: 'bool' = False) -> 'None'
Juju.wait(self, ready: 'Callable[[Status], bool]', *, error: 'Callable[[Status], bool] | None' = None, delay: 'float' = 1.0, timeout: 'float | None' = None, successes: 'int' = 3) -> 'Status'
Juju.run(self, unit: 'str', action: 'str', params: 'Mapping[str, Any] | None' = None, *, wait: 'float | None' = None) -> 'Task'
Juju.integrate(self, app1: 'str', app2: 'str', *, via: 'str | Iterable[str] | None' = None) -> 'None'
Juju.config(self, app: 'str', values: 'Mapping[str, ConfigValue] | None' = None, *, app_config: 'bool' = False, reset: 'str | Iterable[str]' = ()) -> 'Mapping[str, ConfigValue] | None'
Juju.add_unit(self, app: 'str', *, attach_storage: 'str | Iterable[str] | None' = None, num_units: 'int' = 1, to: 'str | Iterable[str] | None' = None)
Juju.remove_unit(self, *app_or_unit: 'str', destroy_storage: 'bool' = False, force: 'bool' = False, num_units: 'int' = 0) -> 'None'
Juju.status(self) -> 'Status'

    def run(
        self,
        unit: str,
        action: str,
        params: Mapping[str, Any] | None = None,
        *,
        wait: float | None = None,
    ) -> Task:
        """Run an action on the given unit and wait for the result.

        Note: this method does not support running an action on multiple units
        at once. If you need that, let us know, and we'll consider adding it
        with a new ``run_multiple`` method or similar.

        Example::

            juju = jubilant.Juju()
            result = juju.run('mysql/0', 'get-password')
            assert result.results['username'] == 'USER0'

        Args:
            unit: Name of unit to run the action on, for example ``mysql/0`` or
                ``mysql/leader``.
            action: Name of action to run.
            params: Named parameters to pass to the action.
            wait: Maximum time to wait for action to finish; :class:`TimeoutError` is raised if
                this is reached. Juju's default is to wait 60 seconds.

        Returns:
            The task created to run the action, including logs, failure message, and so on.

        Raises:
            ValueError: if the action or the unit doesn't exist.
            TaskError: if the action failed.
            TimeoutError: if *wait* was specified and the wait time was reached.
        """
        args = ['run', '--format', 'json', unit, action]
        if wait is not None:
            args.extend(['--wait', f'{wait}s'])

        with (
            tempfile.NamedTemporaryFile('w+', dir=self._temp_dir)
            if params is not None
            else contextlib.nullcontext()
        ) as params_file:
            # params_file is defined when params is not None
            if params_file is not None:
                _yaml.safe_dump(params, params_file)
                params_file.flush()
                args.extend(['--params', params_file.name])
            try:
                stdout, stderr = self._cli(*args)
            except CLIError as exc:
                if 'timed out' in exc.stderr:
                    msg = f'timed out waiting for action, stderr:\n{exc.stderr}'
                    raise TimeoutError(msg) from None
                # With Juju 4, trying to run an action that is not defined gives an error like:
                # ERROR action "not-defined-action" not defined for unit "unit/0". (not found)
                if '(not found)' in exc.stderr:
                    raise ValueError(
                        f'error running action {action!r}, stderr:\n{exc.stderr}'
                    ) from None
                # The "juju run" CLI command fails if the action has an uncaught exception.
                if 'task failed' not in exc.stderr:
                    raise
                stdout = exc.stdout
                stderr = exc.stderr

            # Command doesn't return any stdout if no units exist.
            results: dict[str, Any] = json.loads(stdout) if stdout.strip() else {}
            if not results:
                raise ValueError(f'error running action {action!r}, stderr:\n{stderr}')
            # Don't look up results[unit] directly, because if the caller specifies
            # app/leader it is returned as app/N, for example app/0.
            task_dict = next(iter(results.values()))
            task = Task._from_dict(task_dict)
            task.raise_on_failure()
            return task
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 49s</sub>

### ✅ `bash`

**Read deploy and wait source**

$ python3 -c "
import jubilant
import inspect
# Show deploy and wait source
print('=== DEPLOY ===')
print(inspect.getsource(jubilant.Juju.deploy))
print('=== WAIT ===')
print(inspect.getsource(jubilant.Juju.wait))
"

<details>
<summary>171 lines</summary>

```
=== DEPLOY ===
    def deploy(
        self,
        charm: str | pathlib.Path,
        app: str | None = None,
        *,
        attach_storage: str | Iterable[str] | None = None,
        base: str | None = None,
        bind: Mapping[str, str] | str | None = None,
        channel: str | None = None,
        config: Mapping[str, ConfigValue] | None = None,
        constraints: Mapping[str, str] | None = None,
        force: bool = False,
        num_units: int = 1,
        overlays: Iterable[str | pathlib.Path] = (),
        resources: Mapping[str, str] | None = None,
        revision: int | None = None,
        storage: Mapping[str, str] | None = None,
        to: str | Iterable[str] | None = None,
        trust: bool = False,
    ) -> None:
        """Deploy an application or bundle.

        Args:
            charm: Name of charm or bundle to deploy, or path to a local file (must start with
                ``/`` or ``.``).
            app: Custom application name within the model. Defaults to the charm name.
            attach_storage: Existing storage(s) to attach to the deployed unit, for example,
                ``foo/0`` or ``mydisk/1``. Not available for Kubernetes models.
            base: The base on which to deploy, for example, ``ubuntu@22.04``.
            bind: Either a mapping of endpoint-to-space bindings, for example
                ``{'database-peers': 'internal-space'}``, or a single space name, which is
                equivalent to binding all endpoints to that space.
            channel: Channel to use when deploying from Charmhub, for example, ``latest/edge``.
            config: Application configuration as key-value pairs, for example,
                ``{'name': 'My Wiki'}``.
            constraints: Hardware constraints for new machines, for example, ``{'mem': '8G'}``.
            force: If true, bypass checks such as supported bases.
            num_units: Number of units to deploy for principal charms.
            overlays: File paths of bundles to overlay on the primary bundle, applied in order.
            resources: Specify named resources to use for deployment, for example:
                ``{'bin': '/path/to/some/binary'}``.
            revision: Charmhub revision number to deploy.
            storage: Constraints for named storage(s), for example, ``{'data': 'tmpfs,1G'}``.
            to: Machine or container to deploy the unit in (bypasses constraints). For example,
                to deploy to a new LXD container on machine 25, use ``lxd:25``.
            trust: If true, allows charm to run hooks that require access to cloud credentials.
        """
        # Need this check because str is also an iterable of str.
        if isinstance(overlays, str):
            raise TypeError('overlays must be an iterable of str or pathlib.Path, not str')

        with self._deploy_tempdir(charm, resources) as (_charm, resources):
            assert _charm is not None
            args = ['deploy', _charm]

            if app is not None:
                args.append(app)

            if attach_storage:
                if isinstance(attach_storage, str):
                    args.extend(['--attach-storage', attach_storage])
                else:
                    args.extend(['--attach-storage', ','.join(attach_storage)])
            if base is not None:
                args.extend(['--base', base])
            if bind is not None:
                if not isinstance(bind, str):
                    bind = ' '.join(f'{k}={v}' for k, v in bind.items())
                args.extend(['--bind', bind])
            if channel is not None:
                args.extend(['--channel', channel])
            if config is not None:
                for k, v in config.items():
                    args.extend(['--config', _format_config(k, v)])
            if constraints is not None:
                for k, v in constraints.items():
                    args.extend(['--constraints', f'{k}={v}'])
            if force:
                args.append('--force')
            if num_units != 1:
                args.extend(['--num-units', str(num_units)])
            for overlay in overlays:
                args.extend(['--overlay', str(overlay)])
            if resources is not None:
                for k, v in resources.items():
                    args.extend(['--resource', f'{k}={v}'])
            if revision is not None:
                args.extend(['--revision', str(revision)])
            if storage is not None:
                for k, v in storage.items():
                    args.extend(['--storage', f'{k}={v}'])
            if to:
                if isinstance(to, str):
                    args.extend(['--to', to])
                else:
                    args.extend(['--to', ','.join(to)])
            if trust:
                args.append('--trust')

            self.cli(*args)

=== WAIT ===
    def wait(
        self,
        ready: Callable[[Status], bool],
        *,
        error: Callable[[Status], bool] | None = None,
        delay: float = 1.0,
        timeout: float | None = None,
        successes: int = 3,
    ) -> Status:
        """Wait until ``ready(status)`` returns true.

        This fetches the Juju status repeatedly (waiting *delay* seconds between each call),
        and returns the last status after the *ready* callable returns true for *successes*
        times in a row.

        Example::

            juju = jubilant.Juju()
            juju.deploy('snappass-test')
            juju.wait(jubilant.all_active)

            # Or something more complex: wait specifically for 'snappass-test' to be active,
            # and raise if any app or unit is seen in "error" status while waiting.
            juju.wait(
                lambda status: jubilant.all_active(status, 'snappass-test'),
                error=jubilant.any_error,
            )

        For more examples, see `Tutorial | Use a custom wait condition <https://documentation.ubuntu.com/jubilant/tutorial/getting-started/#use-a-custom-wait-condition>`_.

        This function logs the status object after the first status call, and after subsequent
        calls if the status object has changed. Logs are sent to the logger named
        ``jubilant.wait`` at INFO level, so to disable these logs, set the level to WARNING or
        above::

            logging.getLogger('jubilant.wait').setLevel('WARNING')

        Args:
            ready: Callable that takes a :class:`Status` object and returns true when the wait
                should be considered ready. It needs to return true *successes* times in a row
                before ``wait`` returns.
            error: Callable that takes a :class:`Status` object and returns true when ``wait``
                should raise an error (:class:`WaitError`).
            delay: Delay in seconds between status calls.
            timeout: Overall timeout in seconds; :class:`TimeoutError` is raised if this
                is reached. If not specified, uses the *wait_timeout* specified when the
                instance was created.
            successes: Number of times *ready* must return true for the wait to succeed.

        Raises:
            TimeoutError: If the *timeout* is reached. A string representation
                of the last status, if any, is added as an exception note.
            WaitError: If the *error* callable returns True. A string representation
                of the last status is added as an exception note.
        """
        if timeout is None:
            timeout = self.wait_timeout

        status = None
        success_count = 0
        start = time.monotonic()

        while time.monotonic() - start < timeout:
            prev_status = status

            stdout, _ = self._cli('status', '--format', 'json', log=False)
            result = json.loads(stdout)
            status = Status._from_dict(result)

            if status != prev_status:
                diff = _status_diff(prev_status, status)
                if diff:
                    logger_wait.info('wait: status changed:\n%s', diff)

            if error is not None and error(status):
                name = getattr(error, '__qualname__', repr(error))
                raise WaitError(f'error function {name} returned true\n{status}')

            if ready(status):
                success_count += 1
                if success_count >= successes:
                    return status
            else:
                success_count = 0

            time.sleep(delay)

        if status is None:
            raise TimeoutError(f'wait timed out after {timeout}s')
        raise TimeoutError(f'wait timed out after {timeout}s\n{status}')
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 1m 0s</sub>

### ✅ `bash`

**Read pytest-jubilant main source**

$ python3 -c "
import inspect
import pytest_jubilant.main as pj
print(inspect.getsource(pj))
"

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

<sub>⏱️ 1m 0s</sub>

### ✅ `bash`

**Read status types**

$ python3 -c "
import jubilant
import inspect
# Show status types
print(inspect.getsource(jubilant.statustypes))
" 2>&1 | head -100

<details>
<summary>84 lines</summary>

```
"""Dataclasses that contain parsed output from ``juju status --format=json``.

These dataclasses were originally `generated from <https://github.com/juju/juju/compare/main...benhoyt:juju:status-dataclasses>`_
the Go structs in the Juju codebase, to ensure they are correct. Class names
come from the Go struct name, whereas attribute names come from the JSON field
names. The one exception is that "Application" has been renamed to "App"
throughout, for brevity (and "application" to "app").
"""

from __future__ import annotations

import dataclasses
from typing import Any

from . import _pretty

__all__ = [
    'AppStatus',
    'AppStatusRelation',
    'CombinedStorage',
    'ControllerStatus',
    'EntityStatus',
    'FilesystemAttachment',
    'FilesystemAttachments',
    'FilesystemInfo',
    'FormattedBase',
    'LxdProfileContents',
    'MachineStatus',
    'ModelStatus',
    'NetworkInterface',
    'OfferStatus',
    'RemoteAppStatus',
    'RemoteEndpoint',
    'Status',
    'StatusInfo',
    'StorageAttachments',
    'StorageInfo',
    'UnitStatus',
    'UnitStorageAttachment',
    'VolumeAttachment',
    'VolumeAttachments',
    'VolumeInfo',
]


@dataclasses.dataclass(frozen=True)
class FormattedBase:
    name: str
    channel: str

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> FormattedBase:
        return cls(
            name=d['name'],
            channel=d['channel'],
        )


@dataclasses.dataclass(frozen=True)
class StatusInfo:
    """The main status class used for application, unit, and machine status."""

    current: str = ''
    message: str = ''
    reason: str = ''
    since: str = ''
    version: str = ''
    life: str = ''

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> StatusInfo:
        if 'status-error' in d:
            return cls(current='failed', message=d['status-error'])
        return cls(
            current=d.get('current') or '',
            message=d.get('message') or '',
            reason=d.get('reason') or '',
            since=d.get('since') or '',
            version=d.get('version') or '',
            life=d.get('life') or '',
        )


@dataclasses.dataclass(frozen=True)
class AppStatusRelation:
    related_app: str = ''
    interface: str = ''
    scope: str = ''

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> AppStatusRelation:
        return cls(
            related_app=d.get('related-application') or '',
            interface=d.get('interface') or '',
            scope=d.get('scope') or '',
        )


@dataclasses.dataclass(frozen=True)
class UnitStatus:
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 1m 9s</sub>

### ✅ `bash`

**Read Task class source**

$ python3 -c "
import jubilant
import inspect
print(inspect.getsource(jubilant._task.Task))
" 2>&1 | head -80

<details>
<summary>66 lines</summary>

```
@dataclasses.dataclass(frozen=True)
class Task:
    """A task holds the results of Juju running an action or exec command on a single unit."""

    id: str
    """Task ID of the action, for use with ``juju show-task``."""

    status: Literal['aborted', 'cancelled', 'completed', 'error', 'failed']
    """Status of the action (Juju operation). Typically "completed" or "failed"."""

    results: dict[str, Any] = dataclasses.field(default_factory=dict)  # type: ignore
    """Results of the action provided by the charm.

    This excludes the special "return-code", "stdout", and "stderr" keys
    inserted by Juju; those values are provided by separate attributes.
    """

    return_code: int = 0
    """Return code from executing the charm action hook."""

    stdout: str = ''
    """Stdout printed by the action hook."""

    stderr: str = ''
    """Stderr printed by the action hook."""

    message: str = ''
    """Failure message, if the charm provided a message when it failed the action."""

    log: list[str] = dataclasses.field(default_factory=list)  # type: ignore
    """List of messages logged by the action hook."""

    def __str__(self) -> str:
        details: list[str] = []
        if self.results:
            details.append(f'Results: {self.results}')
        if self.stdout:
            details.append(f'Stdout:\n{self.stdout}')
        if self.stderr:
            details.append(f'Stderr:\n{self.stderr}')
        if self.message:
            details.append(f'Message: {self.message}')
        if self.log:
            log_str = '\n'.join(self.log)
            details.append(f'Log:\n{log_str}')
        s = f'Task {self.id}: status {self.status!r}, return code {self.return_code}'
        if details:
            s += ', details:\n' + '\n'.join(details)
        return s

    def __repr__(self) -> str:
        return _pretty.dump(self)

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> Task:
        results: dict[str, Any] = d.get('results') or {}
        return_code = results.pop('return-code', 0)
        stdout = results.pop('stdout', '')
        stderr = results.pop('stderr', '')
        return cls(
            id=d['id'],
            status=d['status'],
            results=results,
            return_code=return_code,
            stdout=stdout,
            stderr=stderr,
            message=d.get('message') or '',
            log=d.get('log') or [],
        )

    @property
    def success(self) -> bool:
        """Whether the action was successful."""
        return self.status == 'completed' and self.return_code == 0

    def raise_on_failure(self):
        """If task was not successful, raise a :class:`TaskError`."""
        if not self.success:
            raise TaskError(self)
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 1m 9s</sub>

### ✅ `bash`

**Read Status class source**

$ python3 -c "
import jubilant
import inspect
# Show Status.apps structure
src = inspect.getsource(jubilant.statustypes.Status)
print(src[:3000])
"

<details>
<summary>62 lines</summary>

```
@dataclasses.dataclass(frozen=True)
class Status:
    """Parsed version of the status object returned by ``juju status --format=json``."""

    model: ModelStatus
    """Model information."""

    machines: dict[str, MachineStatus]
    """Mapping of machine ID string (for example, ``"0"``) to machine information."""

    apps: dict[str, AppStatus]
    """Mapping of application name to application information."""

    app_endpoints: dict[str, RemoteAppStatus] = dataclasses.field(default_factory=dict)  # type: ignore
    """Mapping of offer name to remote application information."""

    offers: dict[str, OfferStatus] = dataclasses.field(default_factory=dict)  # type: ignore
    """Mapping of offer name to offer information."""

    storage: CombinedStorage = dataclasses.field(default_factory=CombinedStorage)
    """Storage information."""

    controller: ControllerStatus = dataclasses.field(default_factory=ControllerStatus)
    """Controller information."""

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> Status:
        return cls(
            model=ModelStatus._from_dict(d['model']),
            machines={k: MachineStatus._from_dict(v) for k, v in d['machines'].items()},
            apps={k: AppStatus._from_dict(v) for k, v in d['applications'].items()},
            app_endpoints={
                k: RemoteAppStatus._from_dict(v)
                for k, v in d.get('application-endpoints', {}).items()
            },
            offers={k: OfferStatus._from_dict(v) for k, v in d.get('offers', {}).items()},
            storage=(
                CombinedStorage._from_dict(d['storage']) if 'storage' in d else CombinedStorage()
            ),
            controller=(
                ControllerStatus._from_dict(d['controller'])
                if 'controller' in d
                else ControllerStatus()
            ),
        )

    def __repr__(self) -> str:
        """Return a pretty-printed version of the status."""
        return _pretty.dump(self)

    def __str__(self) -> str:
        """Return a pretty-printed version of the status."""
        return repr(self)

    def __eq__(self, other: object) -> bool:
        """Report whether two status objects are equivalent.

        This excludes the :attr:`controller` attribute, because that only has a timestamp that
        constantly updates.
        """
        if not isinstance(other, Status):
            return False
        for field in dataclasses.fields(self):
            if field.name == 'controller':
                continue
            if getattr(self, field.name) != getattr(other, field.name):
                return False
        return True

    def get_units(self, app: str) -> dict[str, UnitStatus]:
        """Get all units of the given *app*, including units of subordinate apps.

        For subordinate apps, this finds and returns the subordinate units using the app's
        ``subordinate_to`` list. For principal (non-subordinate) apps, this is equivalent to
        ``st
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 1m 16s</sub>

### ✅ `bash`

**Read AppStatus and UnitStatus**

$ python3 -c "
import jubilant
import inspect
# Show AppStatus and UnitStatus
src = inspect.getsource(jubilant.statustypes.AppStatus)
print('=== AppStatus ===')
print(src[:1500])
src = inspect.getsource(jubilant.statustypes.UnitStatus)
print('=== UnitStatus ===')
print(src[:1500])
"

<details>
<summary>77 lines</summary>

```
=== AppStatus ===
@dataclasses.dataclass(frozen=True)
class AppStatus:
    """Status of a single application."""

    charm: str
    charm_origin: str
    charm_name: str
    charm_rev: int
    exposed: bool

    base: FormattedBase | None = None
    charm_channel: str = ''
    charm_version: str = ''
    charm_profile: str = ''
    can_upgrade_to: str = ''
    scale: int = 0
    provider_id: str = ''
    address: str = ''
    life: str = ''
    app_status: StatusInfo = dataclasses.field(default_factory=StatusInfo)
    relations: dict[str, list[AppStatusRelation]] = dataclasses.field(default_factory=dict)  # type: ignore
    subordinate_to: list[str] = dataclasses.field(default_factory=list)  # type: ignore
    units: dict[str, UnitStatus] = dataclasses.field(default_factory=dict)  # type: ignore
    version: str = ''
    endpoint_bindings: dict[str, str] = dataclasses.field(default_factory=dict)  # type: ignore

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> AppStatus:
        if 'status-error' in d:
            return cls(
                charm='<failed>',
                charm_origin='<failed>',
                charm_name='<failed>',
                charm_rev=-1,
                exposed=False,
                app_status=StatusInfo(current='failed', message=d['status-error']),
            )
        return cls(
            charm=d['charm'],
            charm_origin=d['charm-origin'],
            charm_name=d['charm-name'],
            charm_rev=d['charm-rev'],
            expo
=== UnitStatus ===
@dataclasses.dataclass(frozen=True)
class UnitStatus:
    """Status of a single unit."""

    workload_status: StatusInfo = dataclasses.field(default_factory=StatusInfo)
    juju_status: StatusInfo = dataclasses.field(default_factory=StatusInfo)
    leader: bool = False
    upgrading_from: str = ''
    machine: str = ''
    open_ports: list[str] = dataclasses.field(default_factory=list)  # type: ignore
    public_address: str = ''
    address: str = ''
    provider_id: str = ''
    subordinates: dict[str, UnitStatus] = dataclasses.field(default_factory=dict)  # type: ignore

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> UnitStatus:
        if 'status-error' in d:
            return cls(
                workload_status=StatusInfo(current='failed', message=d['status-error']),
                juju_status=StatusInfo(current='failed', message=d['status-error']),
            )
        return cls(
            workload_status=(
                StatusInfo._from_dict(d['workload-status'])
                if 'workload-status' in d
                else StatusInfo()
            ),
            juju_status=(
                StatusInfo._from_dict(d['juju-status']) if 'juju-status' in d else StatusInfo()
            ),
            leader=d.get('leader') or False,
            upgrading_from=d.get('upgrading-from') or '',
            machine=d.get('machine') or '',
            open_ports=d.get('open-ports') or [],
            public_address=d.get('public-address') or '',
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 1m 26s</sub>

### ✅ `bash`

**Read temp_model context manager**

$ python3 -c "
import jubilant
import inspect
print(inspect.getsource(jubilant.temp_model))
"

<details>
<summary>52 lines</summary>

```
@contextlib.contextmanager
def temp_model(
    keep: bool = False,
    controller: str | None = None,
    cloud: str | None = None,
    config: Mapping[str, ConfigValue] | None = None,
    credential: str | None = None,
) -> Generator[Juju]:
    """Context manager to create a temporary model for running tests in.

    This creates a new model with a random name in the format ``jubilant-abcd1234``, and destroys
    it and its storage when the context manager exits.

    If destroying the model takes longer than 10 minutes, log an error and return successfully.
    This is mainly to work around issues with Microk8s destroy-model hanging indefinitely.

    Provides a :class:`Juju` instance to operate on.

    If you want to configure its parameters, such as ``wait_timeout``, set the appropriate
    attribute inside the ``with`` statement. For example, to create a pytest fixture using
    ``temp_model``::

        @pytest.fixture(scope='module')
        def juju():
            with jubilant.temp_model() as juju:
                juju.wait_timeout = 10 * 60
                yield juju  # run the test

    Args:
        keep: If true, keep the created model around when the context manager exits.
        controller: Name of controller where the temporary model will be added.
        cloud: Name of cloud or region (or cloud/region) to use for the temporary model.
        config: Temporary model configuration as key-value pairs, for example,
            ``{'image-stream': 'daily'}``.
        credential: Name of cloud credential to use for the temporary model.
    """
    juju = Juju()
    model = 'jubilant-' + secrets.token_hex(4)  # 4 bytes (8 hex digits) should be plenty
    juju.add_model(model, cloud=cloud, controller=controller, config=config, credential=credential)
    try:
        yield juju
    finally:
        if not keep:
            assert juju.model is not None
            try:
                # We're not using juju.destroy_model() here, as Juju doesn't provide a way
                # to specify the timeout for the entire model destruction operation.
                args = ['destroy-model', juju.model, '--no-prompt', '--destroy-storage', '--force']
                juju._cli(*args, include_model=False, timeout=10 * 60)
                juju.model = None
            except subprocess.TimeoutExpired as exc:
                logger.error(
                    'timeout destroying model: %s\nStdout:\n%s\nStderr:\n%s',
                    exc,
                    exc.stdout,
                    exc.stderr,
                )
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 1m 26s</sub>

### ✅ `bash`

**Find actions.py to understand HTTP_PORT etc**

$ cat /tmp/hockeypuck-k8s-L3-source-sonnet-4.6/src/actions.py 2>/dev/null || find /tmp/hockeypuck-k8s-L3-source-sonnet-4.6/src -name "actions.py" | head -3

<details>
<summary>148 lines</summary>

```
# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

"""Hockeypuck charm actions."""

import logging
import re
import typing

import ops
import paas_app_charmer.go
import requests
from requests.exceptions import RequestException

from admin_gpg import AdminGPG

WORKLOAD_CONTAINER_NAME = "app"

logger = logging.getLogger(__name__)

HTTP_PORT: typing.Final[int] = 11371  # the port hockeypuck listens to for HTTP requests
RECONCILIATION_PORT: typing.Final[int] = 11370  # the port hockeypuck listens to for reconciliation
METRICS_PORT: typing.Final[int] = 9626  # the metrics port
FINGERPRINT_REGEX = re.compile(r"[0-9A-Fa-f]{40}|[0-9A-Fa-f]{64}")


class Observer(ops.Object):
    """Charm actions observer."""

    def __init__(self, charm: paas_app_charmer.go.Charm):
        """Initialize the observer and register actions handlers.

        Args:
            charm: The parent charm to attach the observer to.
        """
        super().__init__(charm, "actions-observer")
        self.charm = charm

        charm.framework.observe(charm.on.block_keys_action, self._block_keys_action)
        charm.framework.observe(
            charm.on.rebuild_prefix_tree_action, self._rebuild_prefix_tree_action
        )
        charm.framework.observe(charm.on.lookup_key_action, self._lookup_key_action)

    def _block_keys_action(self, event: ops.ActionEvent) -> None:
        """Blocklist and delete keys from the database.

        Args:
            event: the event triggering the original action.
        """
        try:
            if not self.charm.is_ready():
                raise RuntimeError("Service not yet ready.")

            input_fingerprints: str = event.params["fingerprints"]
            comment: str = event.params["comment"]
            fingerprints = input_fingerprints.split(",")

            result = {}
            fingerprints = [fingerprint.lower() for fingerprint in fingerprints]
            for fingerprint in fingerprints:
                if not FINGERPRINT_REGEX.fullmatch(fingerprint):
                    result[fingerprint] = (
                        "Invalid fingerprint format. "
                        "Fingerprints must be 40 or 64 characters long and "
                        "consist of hexadecimal characters only."
                    )
                    continue
                response = requests.get(
                    f"http://127.0.0.1:{HTTP_PORT}/pks/lookup?op=get&search=0x{fingerprint}",
                    timeout=20,
                )
                if response.status_code == 404:
                    result[fingerprint] = "Fingerprint unavailable in the database."
                    continue
                if not response.ok:
                    response.raise_for_status()
                if "-----BEGIN PGP PUBLIC KEY BLOCK-----" in response.text:
                    public_key = response.text
                    request = "/pks/delete\n" + public_key
                    admin_gpg = AdminGPG(self.model)
                    signature = admin_gpg.generate_signature(request=request)
                    response = requests.post(
                        f"http://127.0.0.1:{HTTP_PORT}/pks/delete",
                        timeout=20,
                        data={"keytext": request, "keysig": signature},
                    )
                    response.raise_for_status()
                    logging.info("Deleted %s from the database.", fingerprint)
                    event.log(f"Deleted {fingerprint} from the database.")
                else:
                    raise RuntimeError(
                        f"Public key not found in response for fingerprint: {fingerprint}"
                    )
            fingerprints_to_block = list(set(fingerprints) - set(result))

            command = [
                "/hockeypuck/bin/block_keys.py",
                "--fingerprints",
                ",".join(fingerprints_to_block),
                "--comment",
                comment,
            ]
            self._execute_action(event, command)
            for fingerprint in fingerprints_to_block:
                result[fingerprint] = "Deleted and blocked successfully."
            event.set_results(result)
        except (
            RuntimeError,
            RequestException,
        ) as e:
            logger.exception("Action failed: %s", e)
            event.fail(f"Failed: {e}")

    def _rebuild_prefix_tree_action(self, event: ops.ActionEvent) -> None:
        """Rebuild the prefix tree using the hockeypuck-pbuild binary.

        Args:
            event: the event triggering the original action.
        """
        command = [
            "/hockeypuck/bin/hockeypuck-pbuild",
            "-config",
            "/hockeypuck/etc/hockeypuck.conf",
        ]
        self._execute_action(event, command)

    def _lookup_key_action(self, event: ops.ActionEvent) -> None:
        """Lookup a key in the hockeypuck database using email id or fingerprint or keyword.

        Args:
            event: the event triggering the original action.
        """
        keyword = event.params["keyword"]
        if not self.charm.is_ready():
            event.fail("Service not yet ready.")
        try:
            response = requests.get(
                f"http://127.0.0.1:{HTTP_PORT}/pks/lookup?op=get&search={keyword}",
                timeout=20,
            )
            response.raise_for_status()
            event.set_results({"result": response.text})
        except RequestException as e:
            logger.error("Action failed: %s", e)
            event.fail(f"Failed: {str(e)}")

    def _execute_action(self, event: ops.ActionEvent, command: list[str]) -> None:
        """Stop the hockeypuck service, execute the action and start the service.

        Args:
            event: the event triggering the original action.
            command: the command to be executed inside the hockeypuck container.
        """
        if not self.charm.is_ready():
            event.fail("Service not yet ready.")
        hockeypuck_container = self.charm.unit.get_container(WORKLOAD_CONTAINER_NAME)
        service_name = next(iter(hockeypuck_container.get_services()))
        try:
            hockeypuck_container.pebble.stop_services(services=[service_name])
            process = hockeypuck_container.exec(
                command,
                service_context=service_name,
            )
            process.wait_output()
        except ops.pebble.ExecError as ex:
            logger.exception("Action %s failed: %s %s", ex.command, ex.stdout, ex.stderr)
            event.fail(f"Failed: {ex.stderr!r}")
        finally:
            hockeypuck_container.pebble.start_services(services=[service_name])
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 5m 25s</sub>

### 💬 Copilot

Now I have all the information needed. Let me create a plan and implement the migration.

---

<sub>⏱️ 5m 25s</sub>

### ✅ `sql`

**Create migration todos**

<details>
<summary>Arguments</summary>

```json
{
  "description": "Create migration todos",
  "query": "\nINSERT INTO todos (id, title, description, status) VALUES\n  ('conftest-root', 'Update tests/conftest.py', 'Add abort_on_fail marker registration; keep --charm-file and --hockeypuck-image options', 'pending'),\n  ('conftest-integration', 'Rewrite tests/integration/conftest.py', 'Remove async/await and pytest_asyncio, replace OpsTest/Model/Application with jubilant.Juju. Use temp_model_factory for secondary model. Use juju.deploy/wait/integrate/config.', 'pending'),\n  ('test-charm', 'Rewrite tests/integration/test_charm.py', 'Remove async/await, replace python-libjuju Application API with juju.run/status. Handle TaskError for expected failures. Fix status checks using jubilant status types.', 'pending'),\n  ('tox-ini', 'Update tox.ini deps', 'Replace pytest-asyncio, pytest-operator with jubilant, pytest-jubilant in integration and lint envs', 'pending'),\n  ('pyproject-toml', 'Update pyproject.toml', 'Add abort_on_fail and jubilant markers. Remove asyncio_mode if present.', 'pending');\n"
}
```

</details>

```
5 row(s) inserted. Last inserted row ID: 5.
```


---

<sub>⏱️ 5m 32s</sub>

### ✅ `sql`

**Mark first todos in_progress**

<details>
<summary>Arguments</summary>

```json
{
  "description": "Mark first todos in_progress",
  "query": "UPDATE todos SET status = 'in_progress' WHERE id IN ('conftest-root', 'conftest-integration', 'test-charm', 'tox-ini', 'pyproject-toml');"
}
```

</details>

```
5 row(s) updated.
```


---

<sub>⏱️ 5m 41s</sub>

### ✅ `edit`

**/tmp/hockeypuck-k8s-L3-source-sonnet-4.6/tests/conftest.py**

/tmp/hockeypuck-k8s-L3-source-sonnet-4.6/tests/conftest.py

```
File /tmp/hockeypuck-k8s-L3-source-sonnet-4.6/tests/conftest.py updated with changes.
```


---

<sub>⏱️ 6m 26s</sub>

### 💬 Copilot

Now rewrite the integration conftest:

---

<sub>⏱️ 6m 26s</sub>

### ✅ `edit`

**/tmp/hockeypuck-k8s-L3-source-sonnet-4.6/tests/integration/conftest.py**

/tmp/hockeypuck-k8s-L3-source-sonnet-4.6/tests/integration/conftest.py

```
File /tmp/hockeypuck-k8s-L3-source-sonnet-4.6/tests/integration/conftest.py updated with changes.
```


---

<sub>⏱️ 7m 21s</sub>

### 💬 Copilot

Now rewrite the test file:

---

<sub>⏱️ 7m 21s</sub>

### ✅ `edit`

**/tmp/hockeypuck-k8s-L3-source-sonnet-4.6/tests/integration/test_charm.py**

/tmp/hockeypuck-k8s-L3-source-sonnet-4.6/tests/integration/test_charm.py

```
File /tmp/hockeypuck-k8s-L3-source-sonnet-4.6/tests/integration/test_charm.py updated with changes.
```


---

<sub>⏱️ 7m 30s</sub>

### 💬 Copilot

Now update `tox.ini` to replace pytest-operator/pytest-asyncio with jubilant/pytest-jubilant:

---

<sub>⏱️ 7m 30s</sub>

### ✅ `edit`

**/tmp/hockeypuck-k8s-L3-source-sonnet-4.6/tox.ini**

/tmp/hockeypuck-k8s-L3-source-sonnet-4.6/tox.ini

```
File /tmp/hockeypuck-k8s-L3-source-sonnet-4.6/tox.ini updated with changes.
```


---

<sub>⏱️ 7m 37s</sub>

### ✅ `edit`

**/tmp/hockeypuck-k8s-L3-source-sonnet-4.6/tox.ini**

/tmp/hockeypuck-k8s-L3-source-sonnet-4.6/tox.ini

```
File /tmp/hockeypuck-k8s-L3-source-sonnet-4.6/tox.ini updated with changes.
```


---

<sub>⏱️ 7m 44s</sub>

### 💬 Copilot

Now verify the final state of all changed files:

---

<sub>⏱️ 7m 44s</sub>

### ✅ `bash`

**Validate Python syntax of all changed files**

$ cd /tmp/hockeypuck-k8s-L3-source-sonnet-4.6 && python3 -c "
import ast, sys
for f in ['tests/conftest.py', 'tests/integration/conftest.py', 'tests/integration/test_charm.py']:
    try:
        ast.parse(open(f).read())
        print(f'OK: {f}')
    except SyntaxError as e:
        print(f'SYNTAX ERROR in {f}: {e}')
        sys.exit(1)
"

```
OK: tests/conftest.py
OK: tests/integration/conftest.py
OK: tests/integration/test_charm.py
<exited with exit code 0>
```


---

<sub>⏱️ 7m 56s</sub>

### ✅ `bash`

**Validate migration completeness**

$ cd /tmp/hockeypuck-k8s-L3-source-sonnet-4.6 && python3 -c "
import ast

# Check no async def in integration tests
for f in ['tests/integration/conftest.py', 'tests/integration/test_charm.py']:
    tree = ast.parse(open(f).read())
    async_fns = [n.name for n in ast.walk(tree) if isinstance(n, ast.AsyncFunctionDef)]
    if async_fns:
        print(f'ASYNC FOUND in {f}: {async_fns}')
    else:
        print(f'No async in {f}: OK')

# Check no old imports
import re
for f in ['tests/integration/conftest.py', 'tests/integration/test_charm.py']:
    content = open(f).read()
    bad = ['pytest_asyncio', 'pytest_operator', 'juju.application', 'juju.model', 'juju.client', 'OpsTest']
    for b in bad:
        if b in content:
            print(f'OLD IMPORT {b!r} found in {f}')
        
# Check new imports present
for f in ['tests/integration/conftest.py', 'tests/integration/test_charm.py']:
    content = open(f).read()
    for imp in ['jubilant', 'pytest_jubilant']:
        if imp in content:
            print(f'New import {imp!r} found in {f}: OK')
        else:
            print(f'MISSING import {imp!r} in {f}')
"

<details>
<summary>8 lines</summary>

```
No async in tests/integration/conftest.py: OK
No async in tests/integration/test_charm.py: OK
OLD IMPORT 'juju.model' found in tests/integration/conftest.py
New import 'jubilant' found in tests/integration/conftest.py: OK
New import 'pytest_jubilant' found in tests/integration/conftest.py: OK
New import 'jubilant' found in tests/integration/test_charm.py: OK
MISSING import 'pytest_jubilant' in tests/integration/test_charm.py
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 8m 2s</sub>

### ✅ `bash`

**Find juju.model reference**

$ grep -n "juju.model\|juju\.model" /tmp/hockeypuck-k8s-L3-source-sonnet-4.6/tests/integration/conftest.py

```
150:        f"{juju.model}.svc.cluster.local"
<exited with exit code 0>
```


---

<sub>⏱️ 8m 9s</sub>

### 💬 Copilot

That's `juju.model` as an attribute access on the `Juju` instance — not an import. The test file doesn't need `pytest_jubilant` directly since it just uses the `juju` fixture. Both are fine. Let me do a final check on tox.ini:

---

<sub>⏱️ 8m 10s</sub>

### ✅ `bash`

**Verify tox.ini changes**

$ grep -n "asyncio\|operator\|jubilant" /tmp/hockeypuck-k8s-L3-source-sonnet-4.6/tox.ini

```
47:    jubilant
55:    pytest-jubilant
109:    jubilant
112:    pytest-jubilant
<exited with exit code 0>
```


---

<sub>⏱️ 8m 17s</sub>

### ✅ `bash`

**Show changed files summary**

$ cd /tmp/hockeypuck-k8s-L3-source-sonnet-4.6 && git --no-pager diff --stat

<details>
<summary>6 lines</summary>

```
tests/conftest.py               |  13 +++++
 tests/integration/conftest.py   | 242 ++++++++++++++++++++++++++++++++++----------------------------------------------
 tests/integration/test_charm.py | 145 ++++++++++++++++++++----------------------------
 tox.ini                         |   8 +--
 4 files changed, 180 insertions(+), 228 deletions(-)
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 8m 30s</sub>

### ✅ `bash`

**Commit migration changes**

$ cd /tmp/hockeypuck-k8s-L3-source-sonnet-4.6 && git add -A && git commit -m "Migrate integration tests from pytest-operator to jubilant

Replace python-libjuju/pytest-operator with jubilant/pytest-jubilant:
- Remove all async/await; tests are now synchronous
- Replace OpsTest/Model/Application with jubilant.Juju instances
- Use juju.deploy/wait/integrate/config/run instead of libjuju methods
- Use jubilant.all_active/all_blocked wait helpers
- Use temp_model_factory.get_juju() for secondary model
- Replace action.results['return-code'] with task.return_code
- Replace action.results['key'] with task.results['key']
- Use pytest.raises(jubilant.TaskError) for expected action failures
- Access unit addresses via status.apps[app].units[unit].address (plain str)
- Replace pytest-asyncio and pytest-operator deps with jubilant/pytest-jubilant
- Register abort_on_fail marker to satisfy --strict-markers

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

<sub>⏱️ 8m 40s</sub>

### ✅ `bash`

**Commit with git config**

$ cd /tmp/hockeypuck-k8s-L3-source-sonnet-4.6 && git config user.email "copilot@github.com" && git config user.name "Copilot" && git commit -m "Migrate integration tests from pytest-operator to jubilant

Replace python-libjuju/pytest-operator with jubilant/pytest-jubilant:
- Remove all async/await; tests are now synchronous
- Replace OpsTest/Model/Application with jubilant.Juju instances
- Use juju.deploy/wait/integrate/config/run instead of libjuju methods
- Use jubilant.all_active/all_blocked wait helpers
- Use temp_model_factory.get_juju() for secondary model
- Replace action.results['return-code'] with task.return_code
- Replace action.results['key'] with task.results['key']
- Use pytest.raises(jubilant.TaskError) for expected action failures
- Access unit addresses via status.apps[app].units[unit].address (plain str)
- Replace pytest-asyncio and pytest-operator deps with jubilant/pytest-jubilant
- Register abort_on_fail marker to satisfy --strict-markers

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"

```
[main 0721ee7] Migrate integration tests from pytest-operator to jubilant
 4 files changed, 180 insertions(+), 228 deletions(-)
<exited with exit code 0>
```


---

<sub>⏱️ 8m 45s</sub>

### ✅ `sql`

**Mark all todos done**

<details>
<summary>Arguments</summary>

```json
{
  "description": "Mark all todos done",
  "query": "UPDATE todos SET status = 'done';"
}
```

</details>

```
5 row(s) updated.
```


---

<sub>⏱️ 8m 59s</sub>

### 💬 Copilot

Migration complete. Here's a summary of all changes:

## Changes made

### `tests/conftest.py`
- Added `pytest_configure` to register the `abort_on_fail` marker (required by `--strict-markers`)

### `tests/integration/conftest.py` (full rewrite)
- Removed all `async def`/`await`, `pytest_asyncio`, `OpsTest`, `Model`, `Application` imports
- Added `jubilant`, `pytest_jubilant` imports
- `juju_secondary` fixture uses `temp_model_factory.get_juju("secondary")` instead of `ops_test.track_model()`
- `hockeypuck_charm` uses `pytest_jubilant.pack()` when no `--charm-file` is provided
- All deploy fixtures use `juju.deploy()` + `juju.wait(jubilant.all_active)` instead of `model.deploy()` + `model.wait_for_idle()`
- `hockeypuck_k8s_app` returns the app name string `"hockeypuck-k8s"` instead of an `Application` object
- `hockeypuck_url` runs the Traefik action via `juju.run("traefik-k8s/0", "show-proxied-endpoints")`
- `external_peer_config` reads unit names from `juju.status()` and sets config via `juju.config()`

### `tests/integration/test_charm.py` (full rewrite)
- Removed all `async def`/`await`, `typing`, `juju.*` imports
- Tests take `juju: jubilant.Juju` and `juju_secondary: jubilant.Juju` fixtures instead of `Application` objects
- `juju.run(unit, action, params)` replaces `app.units[0].run_action()`; result is a `Task`
- `task.return_code` replaces `action.results["return-code"]`; `task.results["key"]` replaces `action.results["key"]`
- `test_lookup_key_not_found` uses `pytest.raises(jubilant.TaskError)` to catch the failed action, checking `exc_info.value.task.message`
- `test_unit_limit` uses `juju.add_unit()`/`juju.remove_unit()` + `juju.wait(jubilant.all_blocked/all_active)`
- `test_reconciliation`/`test_block_keys_action` access `unit.address` directly (plain `str`, no bytes decode needed)

### `tox.ini`
- `[testenv:integration]`: replaced `pytest-asyncio`, `pytest-operator` with `jubilant`, `pytest-jubilant`
- `[testenv:lint]`: same replacement

---

<sub>Generated by [GitHub Copilot CLI](https://github.com/features/copilot/cli)</sub>
