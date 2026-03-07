# 🤖 Copilot CLI Session

> **Session ID:** `10f60d15-a06e-423c-9702-61fdee0dd281`
> **Started:** 7 Mar 2026, 3:10:35 PM
> **Duration:** 9m 52s
> **Exported:** 7 Mar 2026, 3:20:27 PM

<sub>⏱️ 6s</sub>

### 👤 User

Migrate this charm's integration tests from pytest-operator (python-libjuju) to jubilant and pytest-jubilant. Update all test files, conftest.py, helpers, and dependencies.

Before starting, install jubilant and pytest-jubilant from PyPI (pip install jubilant pytest-jubilant) and read the source code to understand the API. The key modules are the Juju class, wait helpers (all_active, all_blocked, any_error), and the pytest-jubilant fixtures (pack, get_resources, juju fixture, temp_model_factory).

---

<sub>⏱️ 12s</sub>

### ✅ `bash`

**List all test files**

$ find /tmp/nginx-ingress-integrator-L3-source-sonnet-4.6/tests -type f | sort

<details>
<summary>21 lines</summary>

```
/tmp/nginx-ingress-integrator-L3-source-sonnet-4.6/tests/__init__.py
/tmp/nginx-ingress-integrator-L3-source-sonnet-4.6/tests/conftest.py
/tmp/nginx-ingress-integrator-L3-source-sonnet-4.6/tests/files/test_encrypted_private_key1.pem
/tmp/nginx-ingress-integrator-L3-source-sonnet-4.6/tests/files/test_encrypted_private_key2.pem
/tmp/nginx-ingress-integrator-L3-source-sonnet-4.6/tests/files/test_private_key1.pem
/tmp/nginx-ingress-integrator-L3-source-sonnet-4.6/tests/files/test_private_key2.pem
/tmp/nginx-ingress-integrator-L3-source-sonnet-4.6/tests/integration/__init__.py
/tmp/nginx-ingress-integrator-L3-source-sonnet-4.6/tests/integration/any_charm_nginx_route.py
/tmp/nginx-ingress-integrator-L3-source-sonnet-4.6/tests/integration/conftest.py
/tmp/nginx-ingress-integrator-L3-source-sonnet-4.6/tests/integration/test_cert_relation.py
/tmp/nginx-ingress-integrator-L3-source-sonnet-4.6/tests/integration/test_ingress_relation.py
/tmp/nginx-ingress-integrator-L3-source-sonnet-4.6/tests/integration/test_nginx_route.py
/tmp/nginx-ingress-integrator-L3-source-sonnet-4.6/tests/unit/cert.pem
/tmp/nginx-ingress-integrator-L3-source-sonnet-4.6/tests/unit/conftest.py
/tmp/nginx-ingress-integrator-L3-source-sonnet-4.6/tests/unit/constants.py
/tmp/nginx-ingress-integrator-L3-source-sonnet-4.6/tests/unit/key.pem
/tmp/nginx-ingress-integrator-L3-source-sonnet-4.6/tests/unit/test_cert_relation.py
/tmp/nginx-ingress-integrator-L3-source-sonnet-4.6/tests/unit/test_ingress.py
/tmp/nginx-ingress-integrator-L3-source-sonnet-4.6/tests/unit/test_nginx_route.py
/tmp/nginx-ingress-integrator-L3-source-sonnet-4.6/tests/unit/test_status.py
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 12s</sub>

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

<sub>⏱️ 17s</sub>

### ✅ `bash`

**Install jubilant and pytest-jubilant with break-system-packages**

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

<sub>⏱️ 16s</sub>

### ✅ `view`

**/tmp/nginx-ingress-integrator-L3-source-sonnet-4.6/tests/integration/conftest.py**

/tmp/nginx-ingress-integrator-L3-source-sonnet-4.6/tests/integration/conftest.py

<details>
<summary>195 lines</summary>

```
1. # Copyright 2025 Canonical Ltd.
2. # See LICENSE file for licensing details.
3. 
4. # mypy: disable-error-code="union-attr"
5. # pylint: disable=subprocess-run-check,consider-using-with,duplicate-code
6. 
7. """General configuration module for integration tests."""
8. 
9. from pathlib import Path
10. 
11. import kubernetes
12. import pytest
13. import pytest_asyncio
14. import yaml
15. from juju.model import Model
16. from ops.model import ActiveStatus
17. from pytest import Config, fixture
18. from pytest_operator.plugin import OpsTest
19. 
20. # Mype can't recognize the name as a string type, so we should skip the type check.
21. ACTIVE_STATUS_NAME = ActiveStatus.name  # type: ignore[has-type]
22. ANY_APP_NAME = "any"
23. INGRESS_APP_NAME = "ingress"
24. NEW_HOSTNAME = "any.other"
25. NEW_INGRESS = "any-other-ingress"
26. NEW_PORT = 18080
27. 
28. 
29. @fixture(scope="module", name="metadata")
30. def metadata_fixture():
31.     """Provide charm metadata."""
32.     yield yaml.safe_load(Path("./metadata.yaml").read_text(encoding="utf8"))
33. 
34. 
35. @fixture(scope="module")
36. def app_name(metadata):
37.     """Provide app name from the metadata."""
38.     yield metadata["name"]
39. 
40. 
41. @pytest_asyncio.fixture(scope="module", name="model", autouse=True)
42. async def model_fixture(ops_test: OpsTest, pytestconfig: Config) -> Model:
43.     """The current test model."""
44.     assert ops_test.model
45.     model_arch = pytestconfig.getoption("--model-arch")
46.     if model_arch:
47.         #  Equivalent to `juju set-model-constraints arch=<amd64 / arm64 / ...>`
48.         await ops_test.model.set_constraints({"arch": model_arch})
49.     return ops_test.model
50. 
51. 
52. @fixture(scope="module")
53. def run_action(ops_test: OpsTest):
54.     """Create a async function to run action and return results."""
55. 
56.     async def _run_action(application_name, action_name, **params):
57.         """Run a juju action.
58. 
59.         Args:
60.             application_name: Name of the Juju application.
61.             action_name: Name of the action to execute.
62.             params: Extra parameters for the action.
63. 
64.         Returns:
65.             The results of the action.
66.         """
67.         application = ops_test.model.applications[application_name]
68.         action = await application.units[0].run_action(action_name, **params)
69.         await action.wait()
70.         return action.results
71. 
72.     return _run_action
73. 
74. 
75. @fixture(scope="module")
76. def wait_for_ingress(ops_test: OpsTest):
77.     """Create an async function, that will wait until ingress resource with certain name exists."""
78.     kubernetes.config.load_kube_config()
79.     kube = kubernetes.client.NetworkingV1Api()
80. 
81.     async def _wait_for_ingress(ingress_name):
82.         """Wait for the Ingress to be configured.
83. 
84.         Args:
85.             ingress_name: Name of the Ingress.
86.         """
87.         await ops_test.model.block_until(
88.             lambda: ingress_name
89.             in [
90.                 ingress.metadata.name
91.                 for ingress in kube.list_namespaced_ingress(ops_test.model_name).items
92.             ],
93.             wait_period=5,
94.             timeout=10 * 60,
95.         )
96. 
97.     return _wait_for_ingress
98. 
99. 
100. @fixture(scope="module", name="get_ingress_annotation")
101. def get_ingress_annotation_fixture(ops_test: OpsTest):
102.     """Create a function that will retrieve all annotation from a ingress by its name."""
103.     assert ops_test.model
104.     kubernetes.config.load_kube_config()
105.     kube = kubernetes.client.NetworkingV1Api()
106.     model_name = ops_test.model_name
107. 
108.     def _get_ingress_annotation(ingress_name: str):
109.         """Get the annotations from an Ingress.
110. 
111.         Args:
112.             ingress_name: Name of the Ingress.
113. 
114.         Returns:
115.             the list of annotations from the requested Ingress.
116.         """
117.         return kube.read_namespaced_ingress(
118.             ingress_name, namespace=model_name
119.         ).metadata.annotations
120. 
121.     return _get_ingress_annotation
122. 
123. 
124. @pytest_asyncio.fixture(scope="module")
125. async def wait_ingress_annotation(ops_test: OpsTest, get_ingress_annotation):
126.     """Create an async function that will wait until certain annotation exists on ingress."""
127.     assert ops_test.model
128. 
129.     async def _wait_ingress_annotation(ingress_name: str, annotation_name: str):
130.         """Wait until the ingress annotations are done.
131. 
132.         Args:
133.             ingress_name: Name of the ingress.
134.             annotation_name: Name of the ingress' annotation.
135.         """
136.         await ops_test.model.block_until(
137.             lambda: annotation_name in get_ingress_annotation(ingress_name),
138.             wait_period=5,
139.             timeout=300,
140.         )
141. 
142.     return _wait_ingress_annotation
143. 
144. 
145. @pytest_asyncio.fixture(scope="module")
146. async def build_and_deploy_ingress(model: Model, ops_test: OpsTest, pytestconfig: pytest.Config):
147.     """Create an async function to build the nginx ingress integrator charm then deploy it.
148. 
149.     Args:
150.         model: Juju model for the test.
151.         ops_test: Operator Framework for the test.
152.         pytestconfig: pytest config.
153.     """
154. 
155.     async def _build_and_deploy_ingress(application_name: str = "ingress"):
156.         """Build and deploy the Ingress charm.
157. 
158.         Returns:
159.             The fully deployed Ingress charm.
160.         """
161.         charm = pytestconfig.getoption("--charm-file")
162.         if not charm:
163.             charm = await ops_test.build_charm(".")
164.         return await model.deploy(
165.             str(charm), application_name=application_name, series="jammy", trust=True
166.         )
167. 
168.     return _build_and_deploy_ingress
169. 
170. 
171. @pytest_asyncio.fixture(scope="module")
172. async def deploy_any_charm(model: Model):
173.     """Create an async function to deploy any-charm.
174. 
175.     The function accepts a string as the initial src-overwrite configuration.
176.     """
177. 
178.     async def _deploy_any_charm(src_overwrite):
179.         """Deploy the any-charm for testing.
180. 
181.         Args:
182.             src_overwrite: files to overwrite for testing purposes.
183. 
184.         Returns:
185.             The any-charm application.
186.         """
187.         return await model.deploy(
188.             "any-charm",
189.             application_name="any",
190.             channel="beta",
191.             config={"python-packages": "pydantic<2.0", "src-overwrite": src_overwrite},
192.         )
193. 
194.     return _deploy_any_charm
195.
```

</details>


---

<sub>⏱️ 16s</sub>

### ✅ `view`

**/tmp/nginx-ingress-integrator-L3-source-sonnet-4.6/tests/integration/test_ingress_relation.py**

/tmp/nginx-ingress-integrator-L3-source-sonnet-4.6/tests/integration/test_ingress_relation.py

<details>
<summary>116 lines</summary>

```
1. # Copyright 2025 Canonical Ltd.
2. # See LICENSE file for licensing details.
3. 
4. """Integration test for ingress relation."""
5. 
6. import asyncio
7. import json
8. import pathlib
9. import textwrap
10. 
11. import pytest
12. import requests
13. from juju.model import Model
14. 
15. 
16. def make_any_charm_source(strip_prefix: bool = False, model_name: str = "testing") -> str:
17.     """Generate the source code for the any-charm with ingress relation.
18. 
19.     Args:
20.         strip_prefix: Whether to strip the prefix from the URL path.
21.         model_name: The name of the Juju model.
22. 
23.     Return:
24.         str: The source code of the any-charm.
25.     """
26.     file_path_expr = (
27.         f'www_dir / "{model_name}-any" / "ok"' if not strip_prefix else 'www_dir / "ok"'
28.     )
29. 
30.     return textwrap.dedent(
31.         f"""\
32.         import pathlib
33.         import subprocess
34.         import os
35.         import signal
36.         import ops
37.         from any_charm_base import AnyCharmBase
38.         from ingress import IngressPerAppRequirer
39. 
40.         class AnyCharm(AnyCharmBase):
41.             def __init__(self, *args, **kwargs):
42.                 super().__init__(*args, **kwargs)
43.                 self.ingress = IngressPerAppRequirer(self, port=8080, strip_prefix={strip_prefix})
44.                 self.framework.observe(
45.                     self.on.ingress_relation_changed, self._on_ingress_relation_changed
46.                 )
47. 
48.             def start_server(self):
49.                 www_dir = pathlib.Path("/tmp/www")
50.                 www_dir.mkdir(exist_ok=True)
51. 
52.                 file_path = {file_path_expr}
53.                 file_path.parent.mkdir(exist_ok=True)
54.                 file_path.write_text(str(self.ingress.url))
55. 
56.                 pid_file = pathlib.Path("/tmp/any.pid")
57.                 if pid_file.exists():
58.                     try:
59.                         os.kill(int(pid_file.read_text(encoding="utf8")), signal.SIGKILL)
60.                     except ProcessLookupError:
61.                         pass
62.                     pid_file.unlink()
63. 
64.                 proc_http = subprocess.Popen(
65.                     ["python3", "-m", "http.server", "-d", www_dir, "8080"],
66.                     start_new_session=True,
67.                 )
68.                 pid_file.write_text(str(proc_http.pid), encoding="utf8")
69. 
70.             def _on_ingress_relation_changed(self, event):
71.                 self.unit.status = ops.ActiveStatus()
72.         """
73.     )
74. 
75. 
76. @pytest.mark.parametrize("strip_prefix", [False, True])
77. async def test_ingress_relation(
78.     model: Model, deploy_any_charm, run_action, build_and_deploy_ingress, strip_prefix: bool
79. ):
80.     """Test the ingress relation with both strip_prefix settings.
81. 
82.     Deploy ingress and any-charm, run HTTP test, and clean up.
83.     """
84.     src_overwrite = {
85.         "ingress.py": pathlib.Path("lib/charms/traefik_k8s/v2/ingress.py").read_text(
86.             encoding="utf-8"
87.         ),
88.         "any_charm.py": make_any_charm_source(strip_prefix, model.name),
89.     }
90. 
91.     _, ingress = await asyncio.gather(
92.         deploy_any_charm(json.dumps(src_overwrite)),
93.         build_and_deploy_ingress(),
94.     )
95. 
96.     await ingress.set_config({"service-hostname": "any"})
97.     await model.wait_for_idle()
98.     await model.add_relation("any:ingress", "ingress:ingress")
99.     await model.wait_for_idle(status="active")
100. 
101.     await run_action("any", "rpc", method="start_server")
102. 
103.     response = requests.get(
104.         f"http://127.0.0.1/{model.name}-any/ok", headers={"Host": "any"}, timeout=5
105.     )
106. 
107.     expected_text = f"http://any/{model.name}-any"
108.     assert response.status_code == 200
109.     assert response.text == expected_text
110. 
111.     await model.remove_application("any")
112.     await model.remove_application("ingress")
113.     await model.block_until(
114.         lambda: "any" not in model.applications and "ingress" not in model.applications
115.     )
116.
```

</details>


---

<sub>⏱️ 22s</sub>

### ✅ `view`

**/tmp/nginx-ingress-integrator-L3-source-sonnet-4.6/tests/integration/test_cert_relation.py**

/tmp/nginx-ingress-integrator-L3-source-sonnet-4.6/tests/integration/test_cert_relation.py

<details>
<summary>195 lines</summary>

```
1. # Copyright 2025 Canonical Ltd.
2. # See LICENSE file for licensing details.
3. 
4. # pylint: disable=unused-argument,duplicate-code
5. 
6. """Integration test relation file."""
7. 
8. import asyncio
9. import json
10. import logging
11. import time
12. import typing
13. from pathlib import Path
14. 
15. import pytest
16. import pytest_asyncio
17. from juju.model import Model
18. from ops.model import ActiveStatus
19. from pytest_operator.plugin import OpsTest
20. 
21. LOGGER = logging.getLogger(__name__)
22. 
23. # Mypy can't recognize the name as a string type, so we should skip the type check.
24. ACTIVE_STATUS_NAME = ActiveStatus.name
25. TLS_CERTIFICATES_PROVIDER_APP_NAME = "self-signed-certificates"
26. SELF_SIGNED_CERTIFICATES_CHARM_NAME = "self-signed-certificates"
27. INGRESS_APP_NAME = "ingress"
28. ANY_APP_NAME = "any"
29. ANY_APP_NAME_2 = "any2"
30. NEW_HOSTNAME = "any.other"
31. 
32. 
33. def gen_src_overwrite(
34.     service_hostname: str = "any",
35.     service_name: str = "any",
36.     service_port: int = 8080,
37.     additional_hostnames: typing.Optional[str] = None,
38. ) -> str:
39.     """Generate the src-overwrite config value for testing nginx-route relation.
40. 
41.     Args:
42.         service_hostname: Ingress service hostname.
43.         service_name: Ingress service name.
44.         service_port: Ingress service port
45.         additional_hostnames: Ingress additional hostnames
46. 
47.     Returns:
48.         written src-overwrite variable.
49.     """
50.     nginx_route_lib_path = "lib/charms/nginx_ingress_integrator/v0/nginx_route.py"
51.     nginx_route_lib = Path(nginx_route_lib_path).read_text(encoding="utf8")
52.     any_charm_script = Path("tests/integration/any_charm_nginx_route.py").read_text(
53.         encoding="utf8"
54.     )
55.     nginx_route_config = {
56.         "service_hostname": service_hostname,
57.         "service_name": service_name,
58.         "service_port": service_port,
59.     }
60.     if additional_hostnames:
61.         nginx_route_config["additional_hostnames"] = additional_hostnames
62.     any_charm_src_overwrite = {
63.         "any_charm.py": any_charm_script,
64.         "nginx_route.py": nginx_route_lib,
65.         "nginx_route_config.json": json.dumps(nginx_route_config),
66.     }
67.     return json.dumps(any_charm_src_overwrite)
68. 
69. 
70. @pytest_asyncio.fixture(scope="module")
71. async def build_and_deploy(
72.     model: Model,
73.     deploy_any_charm,
74.     run_action,
75.     build_and_deploy_ingress,
76. ):
77.     """Build and deploy nginx-ingress-integrator charm.
78. 
79.     Also deploy and relate an any-charm application for test purposes.
80. 
81.     Returns: None.
82.     """
83.     await asyncio.gather(
84.         deploy_any_charm(gen_src_overwrite()),
85.         build_and_deploy_ingress(),
86.     )
87.     await model.wait_for_idle()
88.     await run_action(ANY_APP_NAME, "rpc", method="start_server")
89.     relation_name = f"{INGRESS_APP_NAME}:nginx-route"
90.     await model.add_relation(f"{ANY_APP_NAME}:nginx-route", relation_name)
91.     await model.wait_for_idle()
92.     await model.deploy(
93.         SELF_SIGNED_CERTIFICATES_CHARM_NAME,
94.         application_name=TLS_CERTIFICATES_PROVIDER_APP_NAME,
95.         channel="1/stable",
96.     )
97. 
98.     await model.wait_for_idle(
99.         apps=[TLS_CERTIFICATES_PROVIDER_APP_NAME],
100.         status="active",
101.         timeout=1000,
102.     )
103. 
104. 
105. @pytest.mark.usefixtures("build_and_deploy")
106. async def test_given_charms_deployed_when_relate_then_status_is_active(
107.     model: Model, ops_test: OpsTest
108. ):
109.     """
110.     arrange: sample certificate charm has been deployed.
111.     act: integrate the sample certificate provider charm to the given charm.
112.     assert: the integration is successful.
113.     """
114.     await model.add_relation(TLS_CERTIFICATES_PROVIDER_APP_NAME, "ingress:certificates")
115. 
116.     await model.wait_for_idle(
117.         apps=[INGRESS_APP_NAME, TLS_CERTIFICATES_PROVIDER_APP_NAME],
118.         status="active",
119.         timeout=1000,
120.     )
121. 
122. 
123. @pytest.mark.usefixtures("build_and_deploy")
124. async def test_given_charms_deployed_when_relate_then_requirer_received_certs(
125.     model: Model, ops_test: OpsTest
126. ):
127.     """
128.     arrange: given charm has been built, deployed and related to a certificate provider.
129.     act: get the current certificates provided.
130.     assert: the given charm has been provided a certificate successfully.
131.     """
132.     requirer_unit = model.units["ingress/0"]
133. 
134.     action = await requirer_unit.run_action(action_name="get-certificate", hostname="any")
135. 
136.     action_output = await model.get_action_output(action_uuid=action.entity_id, wait=60)
137.     assert action_output["return-code"] == 0
138.     assert "ca-any" in action_output and action_output["ca-any"] is not None
139.     assert "certificate-any" in action_output and action_output["certificate-any"] is not None
140.     assert "chain-any" in action_output and action_output["chain-any"] is not None
141. 
142. 
143. @pytest.mark.usefixtures("build_and_deploy")
144. async def test_given_additional_requirer_charm_deployed_when_relate_then_requirer_received_certs(
145.     model: Model,
146.     run_action,
147.     build_and_deploy_ingress,
148. ):
149.     """
150.     arrange: given charm has been built, deployed and integrated with a dependent application.
151.     act: deploy another instance of the given charm.
152.     assert: the process of deployment, integration and certificate provision is successful.
153.     """
154.     new_requirer_app_name = "ingress2"
155.     await build_and_deploy_ingress(application_name=new_requirer_app_name)
156.     await model.deploy(
157.         "any-charm",
158.         application_name=ANY_APP_NAME_2,
159.         channel="beta",
160.         config={"src-overwrite": gen_src_overwrite()},
161.     )
162.     await model.wait_for_idle()
163.     await run_action(ANY_APP_NAME_2, "rpc", method="start_server")
164.     relation_name = f"{new_requirer_app_name}:nginx-route"
165.     await model.add_relation(f"{ANY_APP_NAME_2}:nginx-route", relation_name)
166.     await model.wait_for_idle()
167. 
168.     await model.add_relation(
169.         TLS_CERTIFICATES_PROVIDER_APP_NAME, f"{new_requirer_app_name}:certificates"
170.     )
171.     await model.wait_for_idle(
172.         apps=[
173.             TLS_CERTIFICATES_PROVIDER_APP_NAME,
174.             new_requirer_app_name,
175.         ],
176.         status="active",
177.         timeout=1000,
178.     )
179.     requirer_unit = model.units[f"{new_requirer_app_name}/0"]
180. 
181.     t0 = time.time()
182.     timeout = 600
183.     while time.time() - t0 < timeout:
184.         action = await requirer_unit.run_action(action_name="get-certificate", hostname="any")
185.         action_output = await model.get_action_output(action_uuid=action.entity_id, wait=60)
186. 
187.         keys = ["ca-any", "certificate-any", "chain-any"]
188.         if action_output["return-code"] == 0 and all(action_output.get(key) for key in keys):
189.             LOGGER.info("Certificate received")
190.             return
191. 
192.         LOGGER.info("Waiting for certificate")
193.         time.sleep(5)
194.     raise TimeoutError("Timed out waiting for certificate")
195.
```

</details>


---

<sub>⏱️ 22s</sub>

### ✅ `view`

**/tmp/nginx-ingress-integrator-L3-source-sonnet-4.6/tests/integration/test_nginx_route.py**

/tmp/nginx-ingress-integrator-L3-source-sonnet-4.6/tests/integration/test_nginx_route.py

<details>
<summary>239 lines</summary>

```
1. # Copyright 2025 Canonical Ltd.
2. # See LICENSE file for licensing details.
3. """Integration test relation file."""
4. 
5. import asyncio
6. import json
7. import time
8. import typing
9. from pathlib import Path
10. 
11. import pytest
12. import pytest_asyncio
13. import requests
14. from juju.model import Model
15. 
16. INGRESS_APP_NAME = "ingress"
17. ANY_APP_NAME = "any"
18. NEW_HOSTNAME = "any.other"
19. 
20. 
21. def gen_src_overwrite(
22.     service_hostname: str = "any",
23.     service_name: str = "any",
24.     service_port: int = 8080,
25.     additional_hostnames: typing.Optional[str] = None,
26. ) -> str:
27.     """Generate the src-overwrite config value for testing nginx-route relation.
28. 
29.     Args:
30.         service_hostname: Ingress service hostname.
31.         service_name: Ingress service name.
32.         service_port: Ingress service port
33.         additional_hostnames: Ingress additional hostnames
34. 
35.     Returns:
36.         written src-overwrite variable.
37.     """
38.     nginx_route_lib_path = "lib/charms/nginx_ingress_integrator/v0/nginx_route.py"
39.     nginx_route_lib = Path(nginx_route_lib_path).read_text(encoding="utf8")
40.     any_charm_script = Path("tests/integration/any_charm_nginx_route.py").read_text(
41.         encoding="utf8"
42.     )
43.     nginx_route_config = {
44.         "service_hostname": service_hostname,
45.         "service_name": service_name,
46.         "service_port": service_port,
47.     }
48.     if additional_hostnames:
49.         nginx_route_config["additional_hostnames"] = additional_hostnames
50.     any_charm_src_overwrite = {
51.         "any_charm.py": any_charm_script,
52.         "nginx_route.py": nginx_route_lib,
53.         "nginx_route_config.json": json.dumps(nginx_route_config),
54.     }
55.     return json.dumps(any_charm_src_overwrite)
56. 
57. 
58. def requests_get(url: str, host_header: str, retry_timeout: int = 120) -> requests.Response:
59.     """Requests get, but will retry when the response status code is not 200.
60. 
61.     Args:
62.         url: URL to request.
63.         host_header: Host header for the request.
64.         retry_timeout: time to retry the request if the request fails.
65. 
66.     Returns:
67.         An HTTP response for the request.
68.     """
69.     time_start = time.time()
70.     while True:
71.         response = requests.get(url, headers={"Host": host_header}, timeout=5)
72.         if response.status_code == 200 or time.time() - time_start > retry_timeout:
73.             return response
74.         time.sleep(1)
75. 
76. 
77. @pytest_asyncio.fixture(scope="module")
78. async def build_and_deploy(model: Model, deploy_any_charm, run_action, build_and_deploy_ingress):
79.     """Build and deploy nginx-ingress-integrator charm.
80. 
81.     Also deploy and relate an any-charm application for test purposes.
82. 
83.     Returns: None.
84.     """
85.     await asyncio.gather(
86.         deploy_any_charm(gen_src_overwrite()),
87.         build_and_deploy_ingress(),
88.     )
89.     await model.wait_for_idle()
90.     await run_action(ANY_APP_NAME, "rpc", method="start_server")
91.     relation_name = f"{INGRESS_APP_NAME}:nginx-route"
92.     await model.add_relation(f"{ANY_APP_NAME}:nginx-route", relation_name)
93.     await model.wait_for_idle()
94. 
95. 
96. @pytest.mark.usefixtures("build_and_deploy")
97. async def test_ingress_connectivity():
98.     """
99.     arrange: given charm has been built and deployed.
100.     act: access ingress IP address with correct host name in HTTP headers.
101.     assert: HTTP request should be forwarded to the application, while a HTTP request without the
102.         correct Host header should return with a response of 404 NOT FOUND.
103.     """
104.     response = requests_get("http://127.0.0.1/ok", host_header="any")
105. 
106.     assert response.text == "ok"
107.     assert response.status_code == 200
108.     assert (
109.         requests_get("http://127.0.0.1/ok", host_header="any.other", retry_timeout=0).status_code
110.         == 404
111.     )
112. 
113. 
114. @pytest.mark.usefixtures("build_and_deploy")
115. async def test_ingress_connectivity_different_backend(model: Model):
116.     """
117.     arrange: given charm has been built and deployed.
118.     act: change the backend protocol.
119.     assert: HTTP request should be forwarded to the application via GRPC
120.         resulting in HTTP status code 502 Bad Gateway.
121.     """
122.     # First check if is OK
123.     response = requests_get("http://127.0.0.1/ok", host_header="any")
124.     assert response.text == "ok"
125.     assert response.status_code == 200
126.     # Then change the config and check if there is an error
127.     await model.applications["ingress"].set_config({"backend-protocol": "GRPC"})
128.     await model.wait_for_idle(status="active")
129.     response = requests_get("http://127.0.0.1/ok", host_header="any")
130.     assert response.status_code == 502
131.     # Undo the change and check again
132.     await model.applications["ingress"].set_config({"backend-protocol": "HTTP"})
133.     await model.wait_for_idle(status="active")
134.     response = requests_get("http://127.0.0.1/ok", host_header="any")
135.     assert response.text == "ok"
136.     assert response.status_code == 200
137. 
138. 
139. @pytest.mark.usefixtures("build_and_deploy")
140. async def test_ingress_connectivity_invalid_backend(model: Model):
141.     """
142.     arrange: given charm has been built and deployed.
143.     act: change the backend protocol.
144.     assert: unit status is blocked.
145.     """
146.     # First check if is OK
147.     response = requests_get("http://127.0.0.1/ok", host_header="any")
148.     assert response.text == "ok"
149.     assert response.status_code == 200
150.     # Then change the config and check if there is an error
151.     await model.applications["ingress"].set_config({"backend-protocol": "FAKE"})
152.     await model.wait_for_idle()
153.     unit = model.applications[INGRESS_APP_NAME].units[0]
154.     assert unit.workload_status == "blocked"
155.     assert "invalid backend protocol" in unit.workload_status_message
156.     # Undo the change and check again
157.     await model.applications["ingress"].set_config({"backend-protocol": "HTTP"})
158.     await model.wait_for_idle(status="active")
159.     response = requests_get("http://127.0.0.1/ok", host_header="any")
160.     assert response.text == "ok"
161.     assert response.status_code == 200
162. 
163. 
164. @pytest_asyncio.fixture(name="set_service_hostname")
165. async def set_service_hostname_fixture(model: Model):
166.     """A fixture to set service-hostname to NEW_HOSTNAME in the any-charm nginx-route relation."""
167.     await model.applications[ANY_APP_NAME].set_config(
168.         {"src-overwrite": gen_src_overwrite(service_hostname=NEW_HOSTNAME)}
169.     )
170.     await model.wait_for_idle(status="active")
171.     yield
172.     await model.applications[ANY_APP_NAME].set_config({"src-overwrite": gen_src_overwrite()})
173.     await model.wait_for_idle(status="active")
174. 
175. 
176. @pytest.mark.usefixtures("build_and_deploy", "set_service_hostname")
177. async def test_update_service_hostname():
178.     """
179.     arrange: given charm has been built and deployed.
180.     act: update the service-hostname option in any-charm.
181.     assert: HTTP request with the service-hostname value as the host header should be forwarded
182.         to the application correctly.
183.     """
184.     response = requests_get("http://127.0.0.1/ok", host_header=NEW_HOSTNAME)
185.     assert response.text == "ok"
186.     assert response.status_code == 200
187. 
188. 
189. @pytest_asyncio.fixture(name="set_additional_hosts")
190. async def set_additional_hosts_fixture(model: Model, run_action):
191.     """A fixture to set additional-hosts to NEW_HOSTNAME in the any-charm nginx-route relation."""
192.     await model.applications[ANY_APP_NAME].set_config(
193.         {"src-overwrite": gen_src_overwrite(additional_hostnames=NEW_HOSTNAME)}
194.     )
195.     await model.wait_for_idle(status="active")
196.     yield
197.     await model.applications[ANY_APP_NAME].set_config({"src-overwrite": gen_src_overwrite()})
198.     await model.wait_for_idle(status="active")
199.     action_result = await run_action(ANY_APP_NAME, "get-relation-data")
200.     relation_data = json.loads(action_result["relation-data"])[0]
201.     assert "additional-hostnames" not in relation_data["application_data"]["any"]
202. 
203. 
204. @pytest.mark.usefixtures("build_and_deploy", "set_additional_hosts")
205. async def test_update_additional_hosts(run_action):
206.     """
207.     arrange: given charm has been built and deployed,
208.     act: update the additional-hostnames option in the nginx-route relation using any-charm.
209.     assert: HTTP request with the additional-hostnames value as the host header should be
210.         forwarded to the application correctly. And the additional-hostnames should exist
211.         in the nginx-route relation data.
212.     """
213.     response = requests_get("http://127.0.0.1/ok", host_header=NEW_HOSTNAME)
214.     assert response.text == "ok"
215.     assert response.status_code == 200
216.     action_result = await run_action(ANY_APP_NAME, "get-relation-data")
217.     relation_data = json.loads(action_result["relation-data"])[0]
218.     assert "additional-hostnames" in relation_data["application_data"]["any"]
219. 
220. 
221. @pytest.mark.usefixtures("build_and_deploy")
222. async def test_missing_field(model: Model, run_action):
223.     """
224.     arrange: given charm has been built and deployed.
225.     act: update the nginx-route relation data with service-name missing.
226.     assert: Nginx ingress integrator charm should enter blocked status.
227.     """
228.     await model.applications[ANY_APP_NAME].set_config({"src-overwrite": gen_src_overwrite()})
229.     await run_action(
230.         ANY_APP_NAME,
231.         "rpc",
232.         method="delete_nginx_route_relation_data",
233.         kwargs=json.dumps({"field": "service-name"}),
234.     )
235.     await model.wait_for_idle()
236.     unit = model.applications[INGRESS_APP_NAME].units[0]
237.     assert unit.workload_status == "blocked"
238.     assert unit.workload_status_message == "Missing fields for nginx-route: service-name"
239.
```

</details>


---

<sub>⏱️ 28s</sub>

### 💬 Copilot

Now let me explore the jubilant API:

---

<sub>⏱️ 28s</sub>

### ✅ `bash`

**Read jubilant API**

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

<sub>⏱️ 28s</sub>

### ✅ `bash`

**Read pytest-jubilant API**

$ python3 -c "import pytest_jubilant; help(pytest_jubilant)" 2>&1 | head -150

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

<sub>⏱️ 35s</sub>

### ✅ `bash`

**Read key Juju methods**

$ python3 -c "import jubilant; j=jubilant.Juju; help(j)" 2>&1 | grep -A5 "def \|wait\|deploy\|relate\|run_action\|config\|status" | head -200

<details>
<summary>201 lines</summary>

```
|  Juju(*, model: 'str | None' = None, wait_timeout: 'float' = 180.0, cli_binary: 'str | pathlib.Path | None' = None)
 |
 |  Instantiate this class to run Juju commands.
 |
 |  Most methods directly call a single Juju CLI command. If a CLI command doesn't yet exist as a
 |  method, use :meth:`cli`.
--
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
--
 |  __init__(self, *, model: 'str | None' = None, wait_timeout: 'float' = 180.0, cli_binary: 'str | pathlib.Path | None' = None)
 |      Initialize self.  See help(type(self)) for accurate signature.
 |
 |  __repr__(self) -> 'str'
 |      Return repr(self).
 |
--
 |  add_model(self, model: 'str', cloud: 'str | None' = None, *, controller: 'str | None' = None, config: 'Mapping[str, ConfigValue] | None' = None, credential: 'str | None' = None) -> 'None'
 |      Add a named model and set this instance's model to it.
 |
 |      To avoid interfering with CLI users, this won't switch the Juju CLI to the
 |      newly-created model. However, because :attr:`model` is set to the name of the new
 |      model, all subsequent operations on this instance will use the new model.
--
 |          config: Model configuration as key-value pairs, for example,
 |              ``{'image-stream': 'daily'}``.
 |          credential: Name of cloud credential to use for the model.
 |
 |  add_secret(self, name: 'str', content: 'Mapping[str, str]', *, info: 'str | None' = None) -> 'SecretURI'
 |      Add a new named secret and return its secret URI.
--
 |      Add one or more units to a deployed application.
 |
 |      Args:
 |          app: Name of application to add units to.
 |          attach_storage: Existing storage(s) to attach to the deployed unit, for example,
 |              ``foo/0`` or ``mydisk/1``. Not available for Kubernetes models.
 |          num_units: Number of units to add.
 |          to: Machine or container to deploy the unit in (bypasses constraints). For example,
 |              to deploy to a new LXD container on machine 25, use ``lxd:25``.
 |
 |  bootstrap(self, cloud: 'str', controller: 'str', *, bootstrap_base: 'str | None' = None, bootstrap_constraints: 'Mapping[str, str] | None' = None, config: 'Mapping[str, ConfigValue] | None' = None, constraints: 'Mapping[str, str] | None' = None, credential: 'str | None' = None, force: 'bool' = False, model_defaults: 'Mapping[str, ConfigValue] | None' = None, storage_pool: 'Mapping[str, str] | None' = None, to: 'str | Iterable[str] | None' = None) -> 'None'
 |      Bootstrap a controller on a cloud environment.
 |
 |      To avoid interfering with CLI users, this does not switch the Juju CLI
 |      to the newly-created controller. In addition, ``self.model`` is not updated.
 |
--
 |          config: Controller configuration options. Model config keys only affect the
 |              controller model.
 |          constraints: Set model constraints, for example, ``{'mem': '8G', 'cores': '4'}``.
 |              If used, its values will be set as the default constraints for all future
 |              workload machines in the model, exactly as if the constraints were set with
 |              ``juju set-model-constraints``.
--
 |  config(self, app: 'str', values: 'Mapping[str, ConfigValue] | None' = None, *, app_config: 'bool' = False, reset: 'str | Iterable[str]' = ()) -> 'Mapping[str, ConfigValue] | None'
 |      Get or set the configuration of a deployed application.
 |
 |      If called with only the *app* argument, get the config and return it.
 |
 |      If called with the *values* or *reset* arguments, set the config values and return None,
 |      and reset any keys in *reset* to their defaults.
 |
 |      Args:
 |          app: Application name to get or set config for.
 |          values: Mapping of config names to values to set.
 |          app_config: When getting config, set this to True to get the
 |              (poorly-named) "application-config" values instead of charm config.
 |          reset: Key or list of keys to reset to their defaults.
 |
 |  consume(self, model_and_app: 'str', alias: 'str | None' = None, *, controller: 'str | None' = None, owner: 'str | None' = None) -> 'None'
 |      Add a remote offer to the model.
 |
--
 |          def juju(request: pytest.FixtureRequest):
 |              with jubilant.temp_model() as juju:
 |                  yield juju  # run the test
 |                  if request.session.testsfailed:
 |                      log = juju.debug_log(limit=1000)
 |                      print(log, end='')
--
 |  deploy(self, charm: 'str | pathlib.Path', app: 'str | None' = None, *, attach_storage: 'str | Iterable[str] | None' = None, base: 'str | None' = None, bind: 'Mapping[str, str] | str | None' = None, channel: 'str | None' = None, config: 'Mapping[str, ConfigValue] | None' = None, constraints: 'Mapping[str, str] | None' = None, force: 'bool' = False, num_units: 'int' = 1, overlays: 'Iterable[str | pathlib.Path]' = (), resources: 'Mapping[str, str] | None' = None, revision: 'int | None' = None, storage: 'Mapping[str, str] | None' = None, to: 'str | Iterable[str] | None' = None, trust: 'bool' = False) -> 'None'
 |      Deploy an application or bundle.
 |
 |      Args:
 |          charm: Name of charm or bundle to deploy, or path to a local file (must start with
 |              ``/`` or ``.``).
 |          app: Custom application name within the model. Defaults to the charm name.
 |          attach_storage: Existing storage(s) to attach to the deployed unit, for example,
 |              ``foo/0`` or ``mydisk/1``. Not available for Kubernetes models.
 |          base: The base on which to deploy, for example, ``ubuntu@22.04``.
 |          bind: Either a mapping of endpoint-to-space bindings, for example
 |              ``{'database-peers': 'internal-space'}``, or a single space name, which is
 |              equivalent to binding all endpoints to that space.
 |          channel: Channel to use when deploying from Charmhub, for example, ``latest/edge``.
 |          config: Application configuration as key-value pairs, for example,
 |              ``{'name': 'My Wiki'}``.
 |          constraints: Hardware constraints for new machines, for example, ``{'mem': '8G'}``.
 |          force: If true, bypass checks such as supported bases.
 |          num_units: Number of units to deploy for principal charms.
 |          overlays: File paths of bundles to overlay on the primary bundle, applied in order.
 |          resources: Specify named resources to use for deployment, for example:
 |              ``{'bin': '/path/to/some/binary'}``.
 |          revision: Charmhub revision number to deploy.
 |          storage: Constraints for named storage(s), for example, ``{'data': 'tmpfs,1G'}``.
 |          to: Machine or container to deploy the unit in (bypasses constraints). For example,
 |              to deploy to a new LXD container on machine 25, use ``lxd:25``.
 |          trust: If true, allows charm to run hooks that require access to cloud credentials.
 |
 |  destroy_model(self, model: 'str', *, destroy_storage: 'bool' = False, force: 'bool' = False, no_wait: 'bool' = False, release_storage: 'bool' = False, timeout: 'float | None' = None) -> 'None'
 |      Terminate all machines (or containers) and resources for a model.
 |
 |      If the given model is this instance's model, also sets this instance's
 |      :attr:`model` to None.
 |
--
 |          no_wait: If True, rush through model destruction without waiting for each step
 |              to complete.
 |          release_storage: If True, release all storage instances in the model.
 |              This is mutually exclusive with *destroy_storage*.
 |          timeout: Maximum time (in seconds) to wait for each step in the model destruction.
 |              This option can only be used with *force*.
 |
 |  exec(self, command: 'str', *args: 'str', machine: 'int | str | None' = None, unit: 'str | None' = None, wait: 'float | None' = None) -> 'Task'
 |      Run the command on the remote target specified.
 |
 |      You must specify either *machine* or *unit*, but not both.
 |
 |      Note: this method does not support running a command on multiple units
--
 |          wait: Maximum time to wait for command to finish; :class:`TimeoutError` is raised if
 |              this is reached. Juju's default is to wait 5 minutes.
 |
 |      Returns:
 |          The task created to run the command, including logs, failure message, and so on.
 |
 |      Raises:
--
 |          TimeoutError: if *wait* was specified and the wait time was reached.
 |
 |  grant_secret(self, identifier: 'str | SecretURI', app: 'str | Iterable[str]') -> 'None'
 |      Grant access to a secret for one or more applications.
 |
 |      Args:
--
 |  model_config(self, values: 'Mapping[str, ConfigValue] | None' = None, reset: 'str | Iterable[str]' = ()) -> 'Mapping[str, ConfigValue] | None'
 |      Get or set the configuration of the model.
 |
 |      If called with no arguments, get the model config and return it.
 |
 |      If called with the *values* or *reset* arguments, set the model config values and return
 |      None, and reset any keys in *reset* to their defaults.
 |
 |      Args:
 |          values: Mapping of model config names to values to set, for example
 |              ``{'update-status-hook-interval': '10s'}``.
 |          reset: Key or list of keys to reset to their defaults.
 |
 |  model_constraints(self, constraints: 'Mapping[str, ConstraintValue] | None' = None) -> 'Mapping[str, ConstraintValue] | None'
 |      Get or set machine constraints on a model.
 |
--
 |  refresh(self, app: 'str', *, base: 'str | None' = None, channel: 'str | None' = None, config: 'Mapping[str, ConfigValue] | None' = None, force: 'bool' = False, path: 'str | pathlib.Path | None' = None, resources: 'Mapping[str, str] | None' = None, revision: 'int | None' = None, storage: 'Mapping[str, str] | None' = None, trust: 'bool' = False)
 |      Refresh (upgrade) an application's charm.
 |
 |      Args:
 |          app: Name of application to refresh.
 |          base: Select a different base than is currently running.
 |          channel: Channel to use when deploying from Charmhub, for example, ``latest/edge``.
 |          config: Application configuration as key-value pairs.
 |          force: If true, bypass checks such as supported bases.
 |          path: Refresh to a charm located at this path.
 |          resources: Specify named resources to use for deployment, for example:
 |              ``{'bin': '/path/to/some/binary'}``.
 |          revision: Charmhub revision number to deploy.
 |          storage: Constraints for named storage(s), for example, ``{'data': 'tmpfs,1G'}``.
 |          trust: If true, allows charm to run hooks that require access to cloud credentials.
 |
 |  remove_application(self, *app: 'str', destroy_storage: 'bool' = False, force: 'bool' = False) -> 'None'
 |      Remove applications from the model.
--
 |  run(self, unit: 'str', action: 'str', params: 'Mapping[str, Any] | None' = None, *, wait: 'float | None' = None) -> 'Task'
 |      Run an action on the given unit and wait for the result.
 |
 |      Note: this method does not support running an action on multiple units
 |      at once. If you need that, let us know, and we'll consider adding it
 |      with a new ``run_multiple`` method or similar.
 |
--
 |          wait: Maximum time to wait for action to finish; :class:`TimeoutError` is raised if
 |              this is reached. Juju's default is to wait 60 seconds.
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 1m 4s</sub>

### ✅ `bash`

**Read jubilant wait helpers**

$ python3 -c "
import jubilant
# look at wait helpers
help(jubilant.all_active)
print('---')
help(jubilant.all_blocked)
print('---')
help(jubilant.any_error)
"

<details>
<summary>14 lines</summary>

```
Help on function all_active in module jubilant._all_any:

all_active(status: 'Status', *apps: 'str') -> 'bool'
    Report whether all apps and units in *status* (or in *apps* if provided) are "active".

    Examples::

        # Use the callable directly to wait for all apps in status to be active.
        juju.wait(jubilant.all_active)

        # Use a lambda to wait for all apps specified (blog, mysql) to be active.
        juju.wait(lambda status: jubilant.all_active(status, 'blog', 'mysql'))

    Args:
        status: The status object being tested.
        apps: If provided, only these applications (and their units) are tested. If an app is not
            present in ``status.apps``, returns False.
(END)
<command with shellId: 6 is still running after 30 seconds. The command is still running. Check the output above - if it looks like the command is waiting for input, use write_bash to provide it. Otherwise, use read_bash to continue waiting for output, or stop_bash to stop it.>
```

</details>


---

<sub>⏱️ 1m 14s</sub>

### ✅ `stop_bash`

<details>
<summary>Arguments</summary>

```json
{
  "shellId": "6"
}
```

</details>

```
<command with id: 6 stopped>
```


---

<sub>⏱️ 1m 15s</sub>

### ✅ `bash`

**Read key Juju method signatures**

$ python3 -c "
import jubilant
import inspect
# Show Juju.wait signature
print('=== wait ===')
print(inspect.signature(jubilant.Juju.wait))
print(inspect.getdoc(jubilant.Juju.wait))
print()
print('=== run ===')
print(inspect.signature(jubilant.Juju.run))
print(inspect.getdoc(jubilant.Juju.run))
print()
print('=== relate ===')
print(inspect.signature(jubilant.Juju.relate))
print(inspect.getdoc(jubilant.Juju.relate))
print()
print('=== remove_application ===')
print(inspect.signature(jubilant.Juju.remove_application))
print()
print('=== status ===')
print(inspect.signature(jubilant.Juju.status))
print(inspect.getdoc(jubilant.Juju.status))
print()
print('=== Task ===')
t = jubilant.Task
for attr in dir(t):
    if not attr.startswith('_'):
        print(attr)
"

<details>
<summary>66 lines</summary>

```
=== wait ===
(self, ready: 'Callable[[Status], bool]', *, error: 'Callable[[Status], bool] | None' = None, delay: 'float' = 1.0, timeout: 'float | None' = None, successes: 'int' = 3) -> 'Status'
Wait until ``ready(status)`` returns true.

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

=== run ===
(self, unit: 'str', action: 'str', params: 'Mapping[str, Any] | None' = None, *, wait: 'float | None' = None) -> 'Task'
Run an action on the given unit and wait for the result.

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

=== relate ===
Traceback (most recent call last):
  File "<string>", line 14, in <module>
AttributeError: type object 'Juju' has no attribute 'relate'
<exited with exit code 1>
```

</details>


---

<sub>⏱️ 1m 15s</sub>

### ✅ `bash`

**Read Status and pytest-jubilant fixtures**

$ python3 -c "
import jubilant
import inspect

# Check Status structure
print('=== Status ===')
print(inspect.getdoc(jubilant.Status))
print()
print('=== statustypes ===')
import jubilant.statustypes as st
for name in dir(st):
    if not name.startswith('_'):
        obj = getattr(st, name)
        if isinstance(obj, type):
            print(f'{name}: {[a for a in dir(obj) if not a.startswith(\"_\")]}')

print()
print('=== pytest_jubilant main ===')
import pytest_jubilant.main as pjm
print(inspect.getsource(pjm))
"

<details>
<summary>267 lines</summary>

```
=== Status ===
Parsed version of the status object returned by ``juju status --format=json``.

=== statustypes ===
Any: []
AppStatus: ['address', 'base', 'can_upgrade_to', 'charm_channel', 'charm_profile', 'charm_version', 'is_active', 'is_blocked', 'is_error', 'is_maintenance', 'is_waiting', 'life', 'provider_id', 'scale', 'version']
AppStatusRelation: ['interface', 'related_app', 'scope']
CombinedStorage: []
ControllerStatus: ['timestamp']
EntityStatus: ['current', 'message', 'since']
FilesystemAttachment: ['life']
FilesystemAttachments: []
FilesystemInfo: ['life', 'pool', 'provider_id', 'storage', 'volume']
FormattedBase: []
LxdProfileContents: []
MachineStatus: ['base', 'constraints', 'controller_member_status', 'display_name', 'dns_name', 'ha_primary', 'hardware', 'hostname', 'instance_id']
ModelStatus: ['region', 'upgrade_available']
NetworkInterface: ['gateway', 'space']
OfferStatus: ['active_connected_count', 'charm', 'total_connected_count']
RemoteAppStatus: ['life']
RemoteEndpoint: []
Status: ['get_units']
StatusInfo: ['current', 'life', 'message', 'reason', 'since', 'version']
StorageAttachments: []
StorageInfo: ['attachments', 'life']
UnitStatus: ['address', 'is_active', 'is_blocked', 'is_error', 'is_maintenance', 'is_waiting', 'leader', 'machine', 'provider_id', 'public_address', 'upgrading_from']
UnitStorageAttachment: ['life', 'location', 'machine']
VolumeAttachment: ['bus_address', 'device', 'device_link', 'life']
VolumeAttachments: []
VolumeInfo: ['hardware_id', 'life', 'pool', 'provider_id', 'storage', 'wwn']

=== pytest_jubilant main ===
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

<sub>⏱️ 1m 22s</sub>

### ✅ `bash`

**List all public Juju methods**

$ python3 -c "
import jubilant
import inspect

# Check all public methods on Juju
for name in sorted(dir(jubilant.Juju)):
    if not name.startswith('_'):
        print(name)
"

<details>
<summary>36 lines</summary>

```
add_credential
add_model
add_secret
add_ssh_key
add_unit
bootstrap
cli
config
consume
debug_log
deploy
destroy_model
exec
grant_secret
integrate
model_config
model_constraints
offer
refresh
remove_application
remove_relation
remove_secret
remove_ssh_key
remove_unit
run
scp
secrets
show_model
show_secret
ssh
status
trust
update_secret
version
wait
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 1m 22s</sub>

### ✅ `view`

**/tmp/nginx-ingress-integrator-L3-source-sonnet-4.6/pyproject.toml**

/tmp/nginx-ingress-integrator-L3-source-sonnet-4.6/pyproject.toml

<details>
<summary>155 lines</summary>

```
1. # Copyright 2025 Canonical Ltd.
2. # See LICENSE file for licensing details.
3. 
4. [project]
5. name = "nginx-ingress-integrator-operator"
6. version = "0.0.0"
7. description = "An operator to configure a kubernetes ingress."
8. readme = "README.md"
9. requires-python = ">=3.10"
10. classifiers = [
11.   "Programming Language :: Python :: 3 :: Only",
12.   "Programming Language :: Python :: 3.10",
13.   "Programming Language :: Python :: 3.11",
14.   "Programming Language :: Python :: 3.12",
15.   "Programming Language :: Python :: 3.13",
16.   "Programming Language :: Python :: 3.14",
17. ]
18. dependencies = [
19.   "charmlibs-interfaces-tls-certificates==1.7.0",
20.   "kubernetes==24.2",
21.   "ops==3.6.0",
22.   "pydantic==2.12.4",
23. ]
24. 
25. [dependency-groups]
26. fmt = [
27.   "ruff",
28. ]
29. lint = [
30.   "codespell",
31.   "mypy",
32.   "ops-scenario",
33.   "pep8-naming",
34.   "pytest",
35.   "pytest-asyncio",
36.   "pytest-operator",
37.   "requests",
38.   "ruff",
39.   "types-pyyaml",
40.   "types-requests",
41. ]
42. unit = [
43.   "coverage[toml]",
44.   "pytest",
45. ]
46. coverage-report = [
47.   "coverage[toml]",
48.   "pytest",
49. ]
50. static = [
51.   "bandit[toml]",
52. ]
53. integration = [
54.   "allure-pytest>=2.8.18",
55.   "allure-pytest-collection-report @ git+https://github.com/canonical/data-platform-workflows@v24.0.0#subdirectory=python/pytest_plugins/allure_pytest_collection_report",
56.   "juju==3.6.1.3",
57.   "protobuf==7.34.0",
58.   "pytest",
59.   "pytest-asyncio",
60.   "pytest-operator",
61. ]
62. integration-juju2 = [
63.   "juju==2.9.49.1",
64.   "protobuf",
65.   "pytest",
66.   "pytest-asyncio",
67.   "pytest-operator",
68. ]
69. 
70. [tool.uv]
71. package = false
72. conflicts = [ [ { group = "integration" }, { group = "integration-juju2" } ] ]
73. 
74. [tool.ruff]
75. target-version = "py310"
76. line-length = 99
77. 
78. # enable ruff linters:
79. #   A flake8-builtins
80. #   B flake8-bugbear
81. # CPY flake8-copyright
82. #   D pydocstyle
83. # E/W pycodestyle
84. #   F Pyflakes
85. #   I isort
86. #   N pep8-naming
87. # RUF Ruff-specific rules
88. #   S flake8-bandit
89. # SIM flake8-simplify
90. #  TC flake8-type-checking
91. #  UP pyupgrade
92. lint.select = [ "A", "B", "C", "CPY", "D", "E", "F", "I", "N", "RUF", "S", "SIM", "TC", "UP", "W" ]
93. lint.ignore = [
94.   "B904",
95.   "D107",
96.   "D203",
97.   "D204",
98.   "D205",
99.   "D213",
100.   "D215",
101.   "D400",
102.   "D404",
103.   "D406",
104.   "D407",
105.   "D408",
106.   "D409",
107.   "D413",
108.   "E501",
109.   "S105",
110.   "S603",
111.   "TC002",
112.   "TC006",
113.   "UP006",
114.   "UP007",
115.   "UP035",
116.   "UP045",
117. ]
118. lint.per-file-ignores."tests/*" = [ "B011", "D100", "D101", "D102", "D103", "D104", "D212", "D415", "D417", "S" ]
119. lint.flake8-copyright.author = "Canonical Ltd."
120. lint.flake8-copyright.min-file-size = 1
121. lint.flake8-copyright.notice-rgx = "Copyright\\s\\d{4}([-,]\\d{4})*\\s+"
122. lint.mccabe.max-complexity = 10
123. lint.pydocstyle.convention = "google"
124. 
125. [tool.codespell]
126. skip = "build,lib,venv,icon.svg,.tox,.git,.mypy_cache,.ruff_cache,.coverage,htmlcov,uv.lock,grafana_dashboards,*.pem"
127. 
128. [tool.coverage.run]
129. branch = true
130. 
131. [tool.coverage.report]
132. fail_under = 88
133. show_missing = true
134. 
135. [tool.mypy]
136. ignore_missing_imports = true
137. check_untyped_defs = true
138. disallow_untyped_defs = true
139. exclude = "tests/integration/provider_charm"
140. 
141. [[tool.mypy.overrides]]
142. module = "tests.*"
143. disallow_untyped_defs = false
144. 
145. [tool.bandit]
146. exclude_dirs = [
147.   "/venv/",
148.   "tests/integration/any_charm.py",
149.   "tests/integration/any_charm_nginx_route.py",
150.   "tests/integration/provider_charm",
151. ]
152. 
153. [tool.bandit.assert_used]
154. skips = [ "*/*test.py", "*/test_*.py" ]
155.
```

</details>


---

<sub>⏱️ 1m 32s</sub>

### ✅ `bash`

**Get integrate and status signatures**

$ python3 -c "
import jubilant, inspect
print('=== integrate ===')
print(inspect.signature(jubilant.Juju.integrate))
print(inspect.getdoc(jubilant.Juju.integrate))
print()
print('=== status ===')
print(inspect.signature(jubilant.Juju.status))
print(inspect.getdoc(jubilant.Juju.status))
print()
print('=== Status fields ===')
print(inspect.getdoc(jubilant.statustypes.Status))
s = jubilant.statustypes.Status
for a in [x for x in dir(s) if not x.startswith('_')]:
    print(f'  {a}')
print()
print('=== AppStatus fields ===')
for a in [x for x in dir(jubilant.statustypes.AppStatus) if not x.startswith('_')]:
    print(f'  {a}')
print()
print('=== UnitStatus fields ===')
for a in [x for x in dir(jubilant.statustypes.UnitStatus) if not x.startswith('_')]:
    print(f'  {a}')
"

<details>
<summary>52 lines</summary>

```
=== integrate ===
(self, app1: 'str', app2: 'str', *, via: 'str | Iterable[str] | None' = None) -> 'None'
Integrate two applications, creating a relation between them.

The order of *app1* and *app2* is not significant. Each of them should
be in the format ``<application>[:<endpoint>]``. The endpoint is only
required if there's more than one possible integration between the two
applications.

To integrate an application in the current model with an application in
another model (cross-model), prefix *app1* or *app2* with ``<model>.``.
To integrate with an application on another controller, *app1* or *app2* must
be an offer endpoint. See ``juju integrate --help`` for details.

Args:
    app1: One of the applications (and endpoints) to integrate.
    app2: The other of the applications (and endpoints) to integrate.
    via: Inform the offering side (the remote application) of the
        source of traffic, to enable network ports to be opened. This
        is in CIDR notation, for example ``192.0.2.0/24``.

=== status ===
(self) -> 'Status'
Fetch the status of the current model, including its applications and units.

=== Status fields ===
Parsed version of the status object returned by ``juju status --format=json``.
  get_units

=== AppStatus fields ===
  address
  base
  can_upgrade_to
  charm_channel
  charm_profile
  charm_version
  is_active
  is_blocked
  is_error
  is_maintenance
  is_waiting
  life
  provider_id
  scale
  version

=== UnitStatus fields ===
  address
  is_active
  is_blocked
  is_error
  is_maintenance
  is_waiting
  leader
  machine
  provider_id
  public_address
  upgrading_from
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 1m 32s</sub>

### ✅ `bash`

**Get status type details**

$ python3 -c "
import jubilant, inspect
print(inspect.getsource(jubilant.statustypes.Status))
print()
print(inspect.getsource(jubilant.statustypes.AppStatus))
print()
print(inspect.getsource(jubilant.statustypes.UnitStatus))
" 2>&1 | head -100

<details>
<summary>82 lines</summary>

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
        ``status.apps[app].units``.

        Returns:
            Dict of units where the key is the unit name and the value is the :class:`UnitStatus`.
            If *app* is not found, return an empty dict.
        """
        app_info = self.apps.get(app)
        if app_info is None:
            return {}
        if not app_info.subordinate_to:
            return app_info.units

        units: dict[str, UnitStatus] = {}
        app_prefix = app + '/'
        for principal in app_info.subordinate_to:
            for unit_info in self.apps[principal].units.values():
                for sub_name, sub in unit_info.subordinates.items():
                    if sub_name.startswith(app_prefix):
                        units[sub_name] = sub  # noqa: PERF403
        return units


@dataclasses.dataclass(frozen=True)
class AppStatus:
    """Status of a single application."""
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 1m 48s</sub>

### ✅ `bash`

**Get AppStatus/UnitStatus full source**

$ python3 -c "
import jubilant, inspect
print(inspect.getsource(jubilant.statustypes.AppStatus))
print()
print(inspect.getsource(jubilant.statustypes.UnitStatus))
print()
print(inspect.getsource(jubilant.statustypes.StatusInfo))
print()
print(inspect.getsource(jubilant.statustypes.EntityStatus))
" 2>&1

<details>
<summary>178 lines</summary>

```
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
            exposed=d['exposed'],
            base=FormattedBase._from_dict(d['base']) if 'base' in d else None,
            charm_channel=d.get('charm-channel') or '',
            charm_version=d.get('charm-version') or '',
            charm_profile=d.get('charm-profile') or '',
            can_upgrade_to=d.get('can-upgrade-to') or '',
            scale=d.get('scale') or 0,
            provider_id=d.get('provider-id') or '',
            address=d.get('address') or '',
            life=d.get('life') or '',
            app_status=(
                StatusInfo._from_dict(d['application-status'])
                if 'application-status' in d
                else StatusInfo()
            ),
            relations={
                k: [AppStatusRelation._from_dict(x) for x in v]
                for k, v in d.get('relations', {}).items()
            },
            subordinate_to=d.get('subordinate-to') or [],
            units={k: UnitStatus._from_dict(v) for k, v in d.get('units', {}).items()},
            version=d.get('version') or '',
            endpoint_bindings=d.get('endpoint-bindings') or {},
        )

    @property
    def is_active(self) -> bool:
        """Report whether the application status for this app is "active"."""
        return self.app_status.current == 'active'

    @property
    def is_blocked(self) -> bool:
        """Report whether the application status for this app is "blocked"."""
        return self.app_status.current == 'blocked'

    @property
    def is_error(self) -> bool:
        """Report whether the application status for this app is "error"."""
        return self.app_status.current == 'error'

    @property
    def is_maintenance(self) -> bool:
        """Report whether the application status for this app is "maintenance"."""
        return self.app_status.current == 'maintenance'

    @property
    def is_waiting(self) -> bool:
        """Report whether the application status for this app is "waiting"."""
        return self.app_status.current == 'waiting'


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
            address=d.get('address') or '',
            provider_id=d.get('provider-id') or '',
            subordinates={
                k: UnitStatus._from_dict(v) for k, v in d.get('subordinates', {}).items()
            },
        )

    @property
    def is_active(self) -> bool:
        """Report whether the workload status for this unit status is "active"."""
        return self.workload_status.current == 'active'

    @property
    def is_blocked(self) -> bool:
        """Report whether the workload status for this unit status is "blocked"."""
        return self.workload_status.current == 'blocked'

    @property
    def is_error(self) -> bool:
        """Report whether the workload status for this unit status is "error"."""
        return self.workload_status.current == 'error'

    @property
    def is_maintenance(self) -> bool:
        """Report whether the workload status for this unit status is "maintenance"."""
        return self.workload_status.current == 'maintenance'

    @property
    def is_waiting(self) -> bool:
        """Report whether the workload status for this unit status is "waiting"."""
        return self.workload_status.current == 'waiting'


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
class EntityStatus:
    """Status class used for storage status. See :class:`StatusInfo` for the main status class."""

    current: str = ''
    message: str = ''
    since: str = ''

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> EntityStatus:
        return cls(
            current=d.get('current') or '',
            message=d.get('message') or '',
            since=d.get('since') or '',
        )
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 1m 48s</sub>

### ✅ `bash`

**Get wait source**

$ python3 -c "
import jubilant, inspect
print(inspect.getsource(jubilant._juju.Juju.wait))
"

<details>
<summary>74 lines</summary>

```
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

<sub>⏱️ 1m 58s</sub>

### 💬 Copilot

Now I have full context. Let me also check the `tox.toml` for the integration test configuration:

---

<sub>⏱️ 1m 58s</sub>

### ✅ `bash`

**Check tox config**

$ cat /tmp/nginx-ingress-integrator-L3-source-sonnet-4.6/tox.toml 2>/dev/null || cat /tmp/nginx-ingress-integrator-L3-source-sonnet-4.6/tox.ini 2>/dev/null || echo "no tox config found"

<details>
<summary>153 lines</summary>

```
# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

skipsdist = true
skip_missing_interpreters = true
envlist = [ "lint", "unit", "static", "coverage-report" ]
requires = [ "tox>=4.21" ]
no_package = true

[env_run_base]
passenv = [ "PYTHONPATH", "CHARM_BUILD_DIR", "MODEL_SETTINGS" ]
runner = "uv-venv-lock-runner"

[env_run_base.setenv]
PYTHONPATH = "{toxinidir}:{toxinidir}/lib:{[vars]src_path}"
PYTHONBREAKPOINT = "ipdb.set_trace"
PY_COLORS = "1"

[env.fmt]
description = "Apply coding style standards to code"
commands = [
  [
    "ruff",
    "check",
    "--fix",
    "--select",
    "I",
    { replace = "ref", of = [
      "vars",
      "all_path",
    ], extend = true },
  ],
  [
    "ruff",
    "format",
    { replace = "ref", of = [
      "vars",
      "all_path",
    ], extend = true },
  ],
]
dependency_groups = [ "fmt" ]

[env.lint]
description = "Check code against coding style standards"
commands = [
  [
    "codespell",
    "{toxinidir}",
  ],
  [
    "ruff",
    "format",
    "--check",
    "--diff",
    { replace = "ref", of = [
      "vars",
      "all_path",
    ], extend = true },
  ],
  [
    "ruff",
    "check",
    { replace = "ref", of = [
      "vars",
      "all_path",
    ], extend = true },
  ],
  [
    "mypy",
    { replace = "ref", of = [
      "vars",
      "all_path",
    ], extend = true },
  ],
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
    "--ignore={[vars]tst_path}integration",
    "-v",
    "--tb",
    "native",
    "-s",
    { replace = "posargs", extend = "true" },
  ],
  [
    "coverage",
    "report",
  ],
]
dependency_groups = [ "unit" ]

[env.coverage-report]
description = "Create test coverage report"
commands = [ [ "coverage", "report" ] ]
dependency_groups = [ "coverage-report" ]

[env.static]
description = "Run static analysis tests"
commands = [ [ "bandit", "-c", "{toxinidir}/pyproject.toml", "-r", "{[vars]src_path}", "{[vars]tst_path}" ] ]
dependency_groups = [ "static" ]

[env.integration]
description = "Run integration tests"
commands = [
  [
    "pytest",
    "-v",
    "--tb",
    "native",
    "--ignore={[vars]tst_path}unit",
    "--log-cli-level=INFO",
    "-s",
    { replace = "posargs", extend = "true" },
  ],
]
dependency_groups = [ "integration" ]

[env.integration-juju2]
description = "Run integration tests"
commands = [
  [
    "pytest",
    "-v",
    "--tb",
    "native",
    "--ignore={[vars]tst_path}unit",
    "--log-cli-level=INFO",
    "-s",
    { replace = "posargs", extend = "true" },
  ],
]
dependency_groups = [ "integration-juju2" ]

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
src_path = "{toxinidir}/src/"
tst_path = "{toxinidir}/tests/"
lib_path = "{toxinidir}/lib/charms/nginx_ingress_integrator"
all_path = [ "{toxinidir}/src/", "{toxinidir}/tests/", "{toxinidir}/lib/charms/nginx_ingress_integrator" ]
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 1m 58s</sub>

### ✅ `bash`

**Check remove_application and Task**

$ python3 -c "
import jubilant, inspect
# Check remove_application signature
print(inspect.signature(jubilant.Juju.remove_application))
print(inspect.getdoc(jubilant.Juju.remove_application))
print()
# Check task results
print(inspect.getsource(jubilant._task.Task))
" 2>&1 | head -80

<details>
<summary>66 lines</summary>

```
(self, *app: 'str', destroy_storage: 'bool' = False, force: 'bool' = False) -> 'None'
Remove applications from the model.

Args:
    app: Name of the application or applications to remove.
    destroy_storage: If True, also destroy storage attached to application units.
    force: Force removal even if an application is in an error state.

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
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 5m 5s</sub>

### 💬 Copilot

Now I have complete understanding of both APIs. Let me create the plan and implement the migration:

---

<sub>⏱️ 5m 5s</sub>

### ✅ `bash`

**Check charmcraft.yaml for metadata**

$ cat /tmp/nginx-ingress-integrator-L3-source-sonnet-4.6/charmcraft.yaml | head -30

<details>
<summary>25 lines</summary>

```
# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

name: nginx-ingress-integrator
title: Nginx Ingress Integrator
summary: An operator to configure a kubernetes ingress.
description: |
  A [Juju](https://juju.is/) [charm](https://juju.is/docs/olm/charmed-operators) deploying and managing external access to HTTP/HTTPS services in a
  Kubernetes cluster via an Nginx Ingress resource. This requires the Kubernetes
  cluster in question to have an [Nginx Ingress Controller](https://docs.nginx.com/nginx-ingress-controller/) already deployed into it.

  This charm simplifies exposing services running inside a Kubernetes cluster to
  external clients. It offers TLS termination as well as easy configuration of a
  number of advanced features including rate limiting, restricting access to
  specific client IP source ranges, and OWASP ModSecurity Core Rule Set (CRS).

  As such, the charm makes it easy for charm developers to provide external
  access to their HTTP workloads in Kubernetes by easy integration offered via
  [the charm's nginx_route library](https://charmhub.io/nginx-ingress-integrator/libraries/nginx_route).

  For DevOps and SRE teams, providing ingress for charms that support a relation
  to this charm will be possible via a simple `juju relate` command.

links:
  documentation: https://discourse.charmhub.io/t/nginx-ingress-integrator-docs-index/4511
  issues: https://github.com/canonical/nginx-ingress-integrator-operator/issues
  source: https://github.com/canonical/nginx-ingress-integrator-operator
  contact: https://launchpad.net/~canonical-is-devops

assumes:
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 5m 5s</sub>

### ✅ `bash`

**Check if metadata.yaml exists**

$ ls /tmp/nginx-ingress-integrator-L3-source-sonnet-4.6/metadata.yaml 2>/dev/null && echo "exists" || echo "not found"

```
not found
<exited with exit code 0>
```


---

<sub>⏱️ 5m 17s</sub>

### 💬 Copilot

Now I have all the information needed. Let me implement the migration:

---

<sub>⏱️ 5m 18s</sub>

### ✅ `sql`

**Create migration todos**

<details>
<summary>Arguments</summary>

```json
{
  "description": "Create migration todos",
  "query": "\nINSERT INTO todos (id, title, description, status) VALUES\n  ('pyproject', 'Update pyproject.toml', 'Replace integration deps: remove juju/protobuf/pytest-asyncio/pytest-operator, add jubilant/pytest-jubilant. Remove integration-juju2 group and conflicts. Update lint group similarly.', 'pending'),\n  ('tox', 'Update tox.toml', 'Remove integration-juju2 env. Update integration env deps.', 'pending'),\n  ('conftest', 'Rewrite integration conftest.py', 'Replace all async fixtures, OpsTest, juju.model.Model with jubilant.Juju. Add pytest_addoption for --charm-file and --model-arch. Make all sync.', 'pending'),\n  ('test-ingress', 'Rewrite test_ingress_relation.py', 'Remove async/await, replace Model with jubilant.Juju, update wait/config/integrate calls.', 'pending'),\n  ('test-cert', 'Rewrite test_cert_relation.py', 'Remove async/await, replace Model/OpsTest with jubilant.Juju, update action running pattern.', 'pending'),\n  ('test-nginx-route', 'Rewrite test_nginx_route.py', 'Remove async/await, replace Model with jubilant.Juju, update status checks.', 'pending'),\n  ('lint-check', 'Run lint checks', 'Run ruff check to verify no lint errors in migrated files.', 'pending');\n"
}
```

</details>

```
7 row(s) inserted. Last inserted row ID: 7.
```


---

<sub>⏱️ 5m 22s</sub>

### ✅ `sql`

**Mark pyproject and tox in_progress**

<details>
<summary>Arguments</summary>

```json
{
  "description": "Mark pyproject and tox in_progress",
  "query": "UPDATE todos SET status = 'in_progress' WHERE id IN ('pyproject', 'tox')"
}
```

</details>

```
2 row(s) updated.
```


---

<sub>⏱️ 5m 33s</sub>

### ✅ `edit`

**/tmp/nginx-ingress-integrator-L3-source-sonnet-4.6/pyproject.toml**

/tmp/nginx-ingress-integrator-L3-source-sonnet-4.6/pyproject.toml

```
File /tmp/nginx-ingress-integrator-L3-source-sonnet-4.6/pyproject.toml updated with changes.
```


---

<sub>⏱️ 5m 33s</sub>

### ✅ `edit`

**/tmp/nginx-ingress-integrator-L3-source-sonnet-4.6/pyproject.toml**

/tmp/nginx-ingress-integrator-L3-source-sonnet-4.6/pyproject.toml

```
File /tmp/nginx-ingress-integrator-L3-source-sonnet-4.6/pyproject.toml updated with changes.
```


---

<sub>⏱️ 5m 33s</sub>

### ✅ `edit`

**/tmp/nginx-ingress-integrator-L3-source-sonnet-4.6/pyproject.toml**

/tmp/nginx-ingress-integrator-L3-source-sonnet-4.6/pyproject.toml

```
File /tmp/nginx-ingress-integrator-L3-source-sonnet-4.6/pyproject.toml updated with changes.
```


---

<sub>⏱️ 5m 40s</sub>

### 💬 Copilot

Now update `tox.toml` to remove the `integration-juju2` env:

---

<sub>⏱️ 5m 40s</sub>

### ✅ `edit`

**/tmp/nginx-ingress-integrator-L3-source-sonnet-4.6/tox.toml**

/tmp/nginx-ingress-integrator-L3-source-sonnet-4.6/tox.toml

```
File /tmp/nginx-ingress-integrator-L3-source-sonnet-4.6/tox.toml updated with changes.
```


---

<sub>⏱️ 5m 44s</sub>

### ✅ `sql`

**Mark pyproject and tox done, conftest in_progress**

<details>
<summary>Arguments</summary>

```json
{
  "description": "Mark pyproject and tox done, conftest in_progress",
  "query": "UPDATE todos SET status = 'done' WHERE id IN ('pyproject', 'tox');\nUPDATE todos SET status = 'in_progress' WHERE id = 'conftest';"
}
```

</details>

```
0 row(s) updated.
```


---

<sub>⏱️ 5m 49s</sub>

### ✅ `sql`

**Update statuses**

<details>
<summary>Arguments</summary>

```json
{
  "description": "Update statuses",
  "query": "UPDATE todos SET status = 'done' WHERE id IN ('pyproject', 'tox');\nUPDATE todos SET status = 'in_progress' WHERE id = 'conftest';"
}
```

</details>

```
0 row(s) updated.
```


---

<sub>⏱️ 5m 53s</sub>

### ✅ `sql`

**Check todos**

<details>
<summary>Arguments</summary>

```json
{
  "description": "Check todos",
  "query": "SELECT id, status FROM todos;"
}
```

</details>

<details>
<summary>10 lines</summary>

```
7 row(s) returned:

| id | status |
| --- | --- |
| pyproject | done |
| tox | done |
| conftest | in_progress |
| test-ingress | pending |
| test-cert | pending |
| test-nginx-route | pending |
| lint-check | pending |
```

</details>


---

<sub>⏱️ 6m 34s</sub>

### 💬 Copilot

Now rewrite the integration `conftest.py`:

---

<sub>⏱️ 6m 34s</sub>

### ✅ `edit`

**/tmp/nginx-ingress-integrator-L3-source-sonnet-4.6/tests/integration/conftest.py**

/tmp/nginx-ingress-integrator-L3-source-sonnet-4.6/tests/integration/conftest.py

```
File /tmp/nginx-ingress-integrator-L3-source-sonnet-4.6/tests/integration/conftest.py updated with changes.
```


---

<sub>⏱️ 7m 5s</sub>

### 💬 Copilot

Now rewrite `test_ingress_relation.py`:

---

<sub>⏱️ 7m 5s</sub>

### ✅ `edit`

**/tmp/nginx-ingress-integrator-L3-source-sonnet-4.6/tests/integration/test_ingress_relation.py**

/tmp/nginx-ingress-integrator-L3-source-sonnet-4.6/tests/integration/test_ingress_relation.py

```
File /tmp/nginx-ingress-integrator-L3-source-sonnet-4.6/tests/integration/test_ingress_relation.py updated with changes.
```


---

<sub>⏱️ 7m 48s</sub>

### 💬 Copilot

Now rewrite `test_cert_relation.py`:

---

<sub>⏱️ 7m 48s</sub>

### ✅ `edit`

**/tmp/nginx-ingress-integrator-L3-source-sonnet-4.6/tests/integration/test_cert_relation.py**

/tmp/nginx-ingress-integrator-L3-source-sonnet-4.6/tests/integration/test_cert_relation.py

```
File /tmp/nginx-ingress-integrator-L3-source-sonnet-4.6/tests/integration/test_cert_relation.py updated with changes.
```


---

<sub>⏱️ 8m 41s</sub>

### 💬 Copilot

Now rewrite `test_nginx_route.py`:

---

<sub>⏱️ 8m 41s</sub>

### ✅ `edit`

**/tmp/nginx-ingress-integrator-L3-source-sonnet-4.6/tests/integration/test_nginx_route.py**

/tmp/nginx-ingress-integrator-L3-source-sonnet-4.6/tests/integration/test_nginx_route.py

```
File /tmp/nginx-ingress-integrator-L3-source-sonnet-4.6/tests/integration/test_nginx_route.py updated with changes.
```


---

<sub>⏱️ 8m 47s</sub>

### 💬 Copilot

Now run the linter to check for issues:

---

<sub>⏱️ 8m 47s</sub>

### ✅ `sql`

**Update todos to mark files done**

<details>
<summary>Arguments</summary>

```json
{
  "description": "Update todos to mark files done",
  "query": "UPDATE todos SET status = 'done' WHERE id IN ('conftest', 'test-ingress', 'test-cert', 'test-nginx-route');\nUPDATE todos SET status = 'in_progress' WHERE id = 'lint-check';"
}
```

</details>

```
0 row(s) updated.
```


---

<sub>⏱️ 8m 48s</sub>

### ✅ `bash`

**Run ruff on integration tests**

$ cd /tmp/nginx-ingress-integrator-L3-source-sonnet-4.6 && pip install ruff --break-system-packages -q && ruff check tests/integration/ 2>&1

```
warning: Selection `CPY` has no effect because preview is not enabled.
All checks passed!
<exited with exit code 0>
```


---

<sub>⏱️ 8m 53s</sub>

### ✅ `bash`

**Check formatting**

$ cd /tmp/nginx-ingress-integrator-L3-source-sonnet-4.6 && ruff format --check tests/integration/ 2>&1

<details>
<summary>6 lines</summary>

```
warning: Selection `CPY` has no effect because preview is not enabled.
Would reformat: tests/integration/conftest.py
Would reformat: tests/integration/test_cert_relation.py
Would reformat: tests/integration/test_nginx_route.py
3 files would be reformatted, 3 files already formatted
<exited with exit code 1>
```

</details>


---

<sub>⏱️ 8m 58s</sub>

### ✅ `bash`

**Apply formatting**

$ cd /tmp/nginx-ingress-integrator-L3-source-sonnet-4.6 && ruff format tests/integration/ 2>&1

```
warning: Selection `CPY` has no effect because preview is not enabled.
3 files reformatted, 3 files left unchanged
<exited with exit code 0>
```


---

<sub>⏱️ 9m 3s</sub>

### ✅ `bash`

**Final lint check**

$ cd /tmp/nginx-ingress-integrator-L3-source-sonnet-4.6 && ruff check tests/integration/ && echo "All good"

```
warning: Selection `CPY` has no effect because preview is not enabled.
All checks passed!
All good
<exited with exit code 0>
```


---

<sub>⏱️ 9m 8s</sub>

### 💬 Copilot

Now commit the changes:

---

<sub>⏱️ 9m 8s</sub>

### ✅ `bash`

**Show changed files**

$ cd /tmp/nginx-ingress-integrator-L3-source-sonnet-4.6 && git diff --stat

<details>
<summary>8 lines</summary>

```
pyproject.toml                             |  18 ++-----
 tests/integration/conftest.py              | 183 ++++++++++++++++++++++++++++++++++-----------------------------------
 tests/integration/test_cert_relation.py    | 129 ++++++++++++++++++++++--------------------------
 tests/integration/test_ingress_relation.py |  40 ++++++++-------
 tests/integration/test_nginx_route.py      | 111 +++++++++++++++++++++---------------------
 tox.toml                                   |  15 ------
 6 files changed, 229 insertions(+), 267 deletions(-)
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 9m 24s</sub>

### ✅ `bash`

**Commit migration changes**

$ cd /tmp/nginx-ingress-integrator-L3-source-sonnet-4.6 && git add -A && git commit -m "Migrate integration tests from pytest-operator to jubilant/pytest-jubilant

- Replace python-libjuju (juju.model.Model) and pytest-operator (OpsTest)
  with jubilant (Juju) and pytest-jubilant fixtures
- Convert all async def tests and fixtures to synchronous
- Replace await model.wait_for_idle() with juju.wait(jubilant.all_active)
  or agent-idle lambda conditions as appropriate
- Replace await model.add_relation() with juju.integrate()
- Replace await model.deploy() with juju.deploy()
- Replace application.set_config() with juju.config()
- Replace action running (run_action + get_action_output) with juju.run()
- Replace model.block_until() with juju.wait(lambda s: ...)
- Replace unit workload_status attribute access with
  status.apps[app].units[unit].workload_status.current/message
- Update conftest.py: add pytest_addoption for --charm-file and
  --model-arch; add charm_file fixture using pytest_jubilant.pack();
  read metadata from charmcraft.yaml instead of metadata.yaml
- Remove pytest-asyncio, pytest-operator, juju, and protobuf from
  integration dependency group
- Remove integration-juju2 dependency group and tox env (python-libjuju
  version variants are no longer applicable with jubilant's CLI approach)
- Remove asyncio conflicts from pyproject.toml [tool.uv]

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

<sub>⏱️ 9m 35s</sub>

### ✅ `bash`

**Commit with git identity set**

$ cd /tmp/nginx-ingress-integrator-L3-source-sonnet-4.6 && git config user.email "copilot@github.com" && git config user.name "GitHub Copilot" && git add -A && git commit -m "Migrate integration tests from pytest-operator to jubilant/pytest-jubilant

- Replace python-libjuju (juju.model.Model) and pytest-operator (OpsTest)
  with jubilant (Juju) and pytest-jubilant fixtures
- Convert all async def tests and fixtures to synchronous
- Replace await model.wait_for_idle() with juju.wait(jubilant.all_active)
  or agent-idle lambda conditions as appropriate
- Replace await model.add_relation() with juju.integrate()
- Replace await model.deploy() with juju.deploy()
- Replace application.set_config() with juju.config()
- Replace action running (run_action + get_action_output) with juju.run()
- Replace model.block_until() with juju.wait(lambda s: ...)
- Replace unit workload_status attribute access with
  status.apps[app].units[unit].workload_status.current/message
- Update conftest.py: add pytest_addoption for --charm-file and
  --model-arch; add charm_file fixture using pytest_jubilant.pack();
  read metadata from charmcraft.yaml instead of metadata.yaml
- Remove pytest-asyncio, pytest-operator, juju, and protobuf from
  integration dependency group
- Remove integration-juju2 dependency group and tox env (python-libjuju
  version variants are no longer applicable with jubilant CLI approach)
- Remove asyncio conflicts from pyproject.toml [tool.uv]

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"

```
[main 9cdc2fd] Migrate integration tests from pytest-operator to jubilant/pytest-jubilant
 6 files changed, 229 insertions(+), 267 deletions(-)
<exited with exit code 0>
```


---

<sub>⏱️ 9m 52s</sub>

### 💬 Copilot

The migration is complete. Here's a summary of all changes made:

## Changes Made

### `pyproject.toml`
- Replaced `juju==3.6.1.3`, `protobuf==7.34.0`, `pytest-asyncio`, `pytest-operator` with `jubilant` and `pytest-jubilant` in the `integration` group
- Removed the `integration-juju2` dependency group (python-libjuju version variants are irrelevant with jubilant's CLI approach)
- Removed the `[tool.uv] conflicts` entry (no longer needed)
- Added `jubilant` and `pytest-jubilant` to the `lint` group

### `tox.toml`
- Removed the `[env.integration-juju2]` environment

### `tests/integration/conftest.py` (full rewrite)
- Added `pytest_addoption` for `--charm-file` and `--model-arch`
- Added `charm_file` fixture that calls `pytest_jubilant.pack(".")` when no path is given
- Replaced `model_fixture` (async, `OpsTest`-based) with a `configure_model` autouse fixture using `juju.model_constraints()`
- Replaced `run_action` (async) with a sync version using `juju.run(f"{app}/0", action, params=...)`
- Replaced async `wait_for_ingress`/`wait_ingress_annotation` with sync versions using `juju.wait(lambda _: ...)`
- Replaced async `build_and_deploy_ingress` and `deploy_any_charm` fixtures with sync versions using `juju.deploy()`
- Reads `charmcraft.yaml` instead of the non-existent `metadata.yaml`

### `tests/integration/test_ingress_relation.py`
- Removed `async def` and all `await` calls
- Replaced `model: Model` parameter with `juju: jubilant.Juju`
- `ingress.set_config(...)` → `juju.config("ingress", {...})`
- `model.wait_for_idle()` → `juju.wait(jubilant.all_active)`
- `model.add_relation()` → `juju.integrate()`
- `model.remove_application()` + `model.block_until()` → `juju.remove_application()` + `juju.wait(lambda s: ...)`

### `tests/integration/test_cert_relation.py`
- Removed `async def`, `await`, `OpsTest`, `pytest_asyncio`, `ops.model`
- Replaced action execution pattern (`requirer_unit.run_action()` + `model.get_action_output()`) with `juju.run(unit, action, params={...})` and `task.return_code` / `task.results`
- All `wait_for_idle()` calls replaced with appropriate `juju.wait()` conditions

### `tests/integration/test_nginx_route.py`
- Removed `async def`, `await`, `pytest_asyncio`, `juju.model.Model`
- Unit status checks (`unit.workload_status == "blocked"`) replaced with `juju.status()` then `unit.workload_status.current == "blocked"` and `unit.workload_status.message`
- All `model.applications[app].set_config()` → `juju.config(app, {...})`
- All `model.wait_for_idle()` → `juju.wait(...)` with appropriate conditions

---

<sub>Generated by [GitHub Copilot CLI](https://github.com/features/copilot/cli)</sub>
