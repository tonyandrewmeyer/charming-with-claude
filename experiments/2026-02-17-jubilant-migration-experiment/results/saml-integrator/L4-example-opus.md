# 🤖 Copilot CLI Session

> **Session ID:** `fdab7f7b-0354-435c-8576-821e4668485f`
> **Started:** 3/7/2026, 12:24:12 PM
> **Duration:** 7m 37s
> **Exported:** 3/7/2026, 12:31:50 PM

<sub>⏱️ 4s</sub>

### 👤 User

Migrate this charm's integration tests from pytest-operator (python-libjuju) to jubilant and pytest-jubilant. Update all test files, conftest.py, and dependencies.

For a working example of what jubilant integration tests look like, clone https://github.com/canonical/wordpress-k8s-operator and study its tests/integration/ directory. Pay attention to how conftest.py sets up the juju fixture, how tests use juju.deploy(), juju.wait(), juju.integrate(), and how pytest-jubilant's pack() and get_resources() are used.

---

<sub>⏱️ 16s</sub>

### 💬 Copilot





---

<sub>⏱️ 16s</sub>

### ✅ `task`

**Explore current integration tests**

<details>
<summary>Arguments</summary>

```json
{
  "agent_type": "explore",
  "prompt": "Explore the integration test directory in /tmp/saml-integrator-L4-opus. I need to understand:\n\n1. List ALL files under tests/integration/ (full paths)\n2. Show the FULL content of every Python file in tests/integration/ including conftest.py, test files, and any helper modules\n3. Show the FULL content of pyproject.toml and tox.toml (for understanding current dependencies and test configuration)\n4. Show the FULL content of charmcraft.yaml and metadata.yaml\n5. Check if there's a src/ directory and show its structure\n\nBe thorough - show complete file contents, not summaries.",
  "description": "Explore current integration tests",
  "mode": "background"
}
```

</details>

```
Agent started in background with agent_id: agent-0. You can use read_agent tool with this agent_id to check status and retrieve results. Instruct the user to use /tasks to manage the background agent.
```


---

<sub>⏱️ 17s</sub>

### ✅ `bash`

**Clone wordpress-k8s-operator reference**

$ cd /tmp && git clone --depth=1 https://github.com/canonical/wordpress-k8s-operator.git wordpress-k8s-ref 2>&1 | tail -3

```
Cloning into 'wordpress-k8s-ref'...
<exited with exit code 0>
```


---

<sub>⏱️ 24s</sub>

### ✅ `task`

**Explore wordpress-k8s-operator reference**

<details>
<summary>Arguments</summary>

```json
{
  "agent_type": "explore",
  "description": "Explore wordpress-k8s-operator reference",
  "mode": "background",
  "prompt": "Explore the wordpress-k8s-operator reference at /tmp/wordpress-k8s-ref. I need to understand how jubilant and pytest-jubilant are used for integration tests. Show me:\n\n1. The FULL content of tests/integration/conftest.py\n2. The FULL content of ALL test files in tests/integration/ (every .py file)\n3. The FULL content of pyproject.toml (specifically the test dependencies and jubilant-related config)\n4. The FULL content of tox.toml or tox.ini if they exist\n5. Any other relevant configuration for integration tests\n\nBe thorough - show complete file contents, not summaries. I need to understand every pattern used."
}
```

</details>

```
Agent started in background with agent_id: agent-1. You can use read_agent tool with this agent_id to check status and retrieve results. Instruct the user to use /tasks to manage the background agent.
```


---

<sub>⏱️ 1m 29s</sub>

### ✅ `read_agent`

<details>
<summary>Arguments</summary>

```json
{
  "agent_id": "agent-0",
  "wait": true,
  "timeout": 60
}
```

</details>

```
Agent is still running after waiting 60s. agent_id: agent-0, agent_type: explore, status: running, description: Explore current integration tests, elapsed: 73s, (timed out waiting for completion) You will be automatically notified when this agent completes — no need to poll.
```


---

<sub>⏱️ 1m 24s</sub>

### ✅ `read_agent`

<details>
<summary>Arguments</summary>

```json
{
  "agent_id": "agent-1",
  "wait": true,
  "timeout": 60
}
```

</details>

<details>
<summary>143 lines</summary>

````
Agent completed. agent_id: agent-1, agent_type: explore, status: completed, description: Explore wordpress-k8s-operator reference, elapsed: 60s, duration: 60s

Result:
Based on my exploration of the codebase, I need to inform you that **jubilant and pytest-jubilant are NOT used in this wordpress-k8s-operator reference repository**. Let me provide you with a comprehensive summary of what IS in the integration test structure:

## Summary: Integration Test Configuration

**IMPORTANT:** There are **NO references to "jubilant" or "pytest-jubilant"** anywhere in this codebase. The project uses standard testing tools instead.

---

## Complete File Contents

### 1. FULL conftest.py
Located at: `/tmp/wordpress-k8s-ref/tests/integration/conftest.py`

This file contains module-scoped pytest fixtures using:
- `pytest` and `pytest_asyncio` for async fixture management
- `pytest_operator.plugin.OpsTest` for Juju charm testing
- Custom fixtures for:
  - **Database**: `prepare_mysql`, `prepare_machine_mysql`
  - **Ingress**: `prepare_nginx_ingress`
  - **Observability**: `prepare_prometheus`, `prepare_loki`, `prepare_swift`, `prepare_grafana`
  - **Infrastructure**: `model`, `kube_config`, `machine_controller`, `machine_model`, `wordpress`
  - **OpenStack**: `openstack_environment`, `swift_conn`, `swift_config`

---

### 2. ALL Integration Test Files

**Test Files in `/tmp/wordpress-k8s-ref/tests/integration/`:**

1. **test_core.py** (164 lines)
   - `test_wordpress_up` - Verify WordPress service is running
   - `test_wordpress_functionality` - Test login, post creation, comments
   - `test_change_upload_limit` - Test upload limit configuration
   - `test_openstack_object_storage_plugin` - Test Swift integration
   - `test_apache_config` - Test Apache configuration
   - `test_uploads_owner` - Verify uploads directory permissions

2. **test_ingress.py** (72 lines)
   - `test_ingress` - Test Nginx ingress integration
   - `test_ingress_modsecurity` - Test ModSecurity annotations in Kubernetes ingress

3. **test_addon.py** (115 lines)
   - `test_wordpress_install_uninstall_themes` - Test theme installation/removal
   - `test_wordpress_theme_installation_error` - Test error handling for invalid themes
   - `test_wordpress_install_uninstall_plugins` - Test plugin installation/removal
   - `test_wordpress_plugin_installation_error` - Test error handling for invalid plugins

4. **test_external.py** (91 lines)
   - `test_akismet_plugin` - Test Akismet spam detection integration
   - `test_openid_plugin` - Test Launchpad OpenID integration

5. **test_machine.py** (40 lines)
   - `test_database_endpoints_changed` - Test MySQL endpoint switching with machine charm

6. **test_cos_grafana.py** (67 lines)
   - `test_grafana_integration` - Test Grafana dashboard integration

7. **test_cos_loki.py** (69 lines)
   - `test_loki_integration` - Test Loki logging integration

8. **test_cos_prometheus.py** (34 lines)
   - `test_prometheus_integration` - Test Prometheus metrics integration

9. **helper.py** (690 lines)
   - **WordpressClient**: HTTP client for WordPress REST API testing
     - Login/logout handling
     - WordPress NONCE generation
     - Post/comment management
     - Theme/plugin listing
     - Media upload
     - Launchpad OpenID authentication
   - **WordpressApp**: Wrapper for Juju WordPress application
     - Unit IP retrieval
     - Configuration management
     - Admin password retrieval
     - Kubernetes pod access
   - **Utility Functions**: `retry` decorator, `wait_for`, `get_mysql_primary_unit`

---

### 3. FULL pyproject.toml

The project uses dependency groups (not classical extras):

**Test Dependencies (integration group)**:
```toml
[dependency-groups]
integration = [
   "allure-pytest>=2.8.18",
   "allure-pytest-collection-report @ git+https://github.com/canonical/data-platform-workflows@v24.0.0#subdirectory=python/pytest_plugins/allure_pytest_collection_report",
   "juju>=2.9,<3",
   "kubernetes",
   "pillow",
   "pytest==9.0.2",
   "pytest-cov",
   "pytest-operator",
   "python-keystoneclient",
   "python-swiftclient",
   "types-pyyaml",
   "types-requests",
   "websockets<17",
]
```

**Key testing frameworks** (not jubilant):
- `pytest==9.0.2` - Test framework
- `pytest-operator` - Juju charm testing plugin
- `pytest-cov` - Coverage reporting
- `allure-pytest` - Allure test reporting

---

### 4. FULL tox.toml

The project uses `tox>=4.21` with `uv-venv-lock-runner`:

**Integration test environments**:
```toml
[env.integration]
description = "Run integration tests"
commands = [
  [
    "pytest",
    "{[vars]tst_path}",
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

[env.integration-juju3]
description = "Run integration tests using Juju 3"
# Similar command structure for Juju 3.6.1.3
```

---

## Key Patterns & Characteristics

### Test Markers
```python
@pytest.mark.usefixtures("prepare_mysql")
@pytest.mark.abort_on_fail
@pytest.mark.requires_secret  # For tests requiring external secrets
```

### Fixture Pattern
Module-scoped fixtures with async/await:
```python
@pytest_asyncio.fixture(scope="module")
async def wordpress_fixture(...) -> WordpressApp:
    # Setup and yield
    yield app
    # Teardown
```

### Integration Testing Style
- **Arrangement-Action-Assertion** docstring format
- Uses `pytest_operator.OpsTest` for Juju model management
- Async/await throughout for Juju operations
- HTTP requests via `requests` library for testing WordPress
- Kubernetes client for pod inspection

### No Direct Test Runners or Plugins Called "jubilant"
The codebase uses:
- **pytest-operator** - The primary Juju charm testing plugin
- **allure-pytest** - For test reporting
- Standard pytest features - markers, fixtures, assertions

---

**Conclusion**: This codebase **does not use jubilant or pytest-jubilant**. It's a standard pytest-based integration test suite for Juju charms, using `pytest-operator` as the primary integration testing plugin for Kubernetes/Juju charm testing.
````

</details>


---

<sub>⏱️ 1m 34s</sub>

### 💬 Copilot





---

<sub>⏱️ 1m 36s</sub>

### ✅ `read_agent`

<details>
<summary>Arguments</summary>

```json
{
  "agent_id": "agent-0",
  "timeout": 60,
  "wait": true
}
```

</details>

<details>
<summary>14 lines</summary>

````
Output too large to read at once (28.5 KB). Saved to: /tmp/1772839548992-copilot-tool-output-47ph1h.txt
Consider using tools like grep (for searching), head/tail (for viewing start/end), view with view_range (for specific sections), or jq (for JSON) to examine portions of the output.

Preview (first 500 chars):
Agent completed. agent_id: agent-0, agent_type: explore, status: completed, description: Explore current integration tests, elapsed: 80s, duration: 80s

Result:
## Complete Exploration Summary

### 1. **ALL FILES IN tests/integration/ (Full Paths)**

```
/tmp/saml-integrator-L4-opus/tests/integration/__init__.py
/tmp/saml-integrator-L4-opus/tests/integration/conftest.py
/tmp/saml-integrator-L4-opus/tests/integration/any_charm.py
/tmp/saml-integrator-L4-opus/tests/integration/test_charm.py
```

-
````

</details>


---

<sub>⏱️ 1m 46s</sub>

### ✅ `web_search`

**pytest-jubilant jubilant juju charm integration testing Python library**

<details>
<summary>Arguments</summary>

```json
{
  "query": "pytest-jubilant jubilant juju charm integration testing Python library"
}
```

</details>

````
{"type":"text","text":{"value":"The `pytest-jubilant` or simply `jubilant` library is a modern, Pythonic library specifically created for integration testing of Juju charms. Here’s a breakdown of what it offers and how it compares to previous approaches in the Juju/charm ecosystem:\n\n### What is Jubilant?\n\n- Jubilant is a Python library that wraps the Juju CLI, making it easy to drive Juju (the Canonical orchestration platform) from your Python integration tests.\n- It’s primarily recommended for use in charm integration testing and provides methods that map closely to Juju CLI commands, but in a type-annotated and more Pythonic manner【3:0†jubilant · PyPI†https://pypi.org/project/jubilant/】【3:1†Jubilant, the joyful library for driving Juju - GitHub†https://github.com/canonical/jubilant】.\n\n### Why use Jubilant over `pytest-operator`?\n\n- **Simpler API**: Jubilant avoids many pain points that came with the older python-libjuju and pytest-operator, such as websocket errors, asynchronous programming requirements, and complex API surfaces.\n- **Direct CLI Wrapping**: It uses Python’s `subprocess.run` to interface directly with the stable Juju CLI, which proves to be simpler and more robust for the use case of integration testing charms【3:8†Don’t fear Python subprocess or Go codegen†https://benhoyt.com/writings/jubilant/】.\n- **No Async Requirement**: Unlike `python-libjuju`, you don’t have to work with asyncio.\n- **Easier Migration**: Guides are available to help you move your current pytest-operator-based tests to Jubilant【3:2†How to migrate from pytest-operator to Jubilant†https://documentation.ubuntu.com/jubilant/how-to/migrate-from-pytest-operator/】【3:3†How-to guides - Jubilant documentation†https://canonical-jubilant.readthedocs-hosted.com/how-to/】.\n\n### Installation and Usage\n\n1. **Install with pip**:\n   ```bash\n   pip install jubilant\n   ```\n   You also need the Juju CLI installed on your system.\n\n2. **Example Integration Test**\n   ```python\n   import jubilant\n   import pytest\n\n   @pytest.fixture(scope='module')\n   def juju():\n       with jubilant.temp_model() as juju:\n           yield juju\n\n   def test_deploy(juju: jubilant.Juju):\n       juju.deploy('snappass-test')\n       status = juju.wait(jubilant.all_active)\n       address = status.apps['snappass-test'].units['snappass-test/0'].address\n       response = requests.get(f'http://{address}:5000/', timeout=10)\n       response.raise_for_status()\n       assert 'snappass' in response.text.lower()\n   ```\n   - `jubilant.temp_model()` manages model setup/teardown.\n   - `juju.deploy()` and `juju.wait()` simplify the process of waiting for deployment.\n\n3. **Pytest Integration**:\n   - You can use Jubilant with pytest, structuring your test fixtures and setup as shown above. While it's not mandatory to use pytest, it's the recommended approach due to its fixture system and assertion style【3:0†jubilant · PyPI†https://pypi.org/project/jubilant/】.\n\n### Key Features\n\n- **1:1 Mapping to Juju CLI**: All major Juju operations are available as type-annotated Python methods.\n- **Improved Reliability**: Since it drives the actual Juju CLI, it avoids issues with breaking APIs or unstable websocket connections.\n- **Easy Integration with Current Tools**: It works seamlessly with pytest and other Python testing tools.\n\n### Migration from `pytest-operator`\n\n- Update your dependencies to include jubilant and remove `pytest-operator`/`python-libjuju`.\n- Define your own pytest fixtures (as Jubilant does not provide these out of the box).\n- Refactor tests to use the new, synchronous, and more robust API.\n\nFor full documentation and transition guidance, see:\n- [Jubilant on PyPI](https://pypi.org/project/jubilant/)\n- [Jubilant GitHub repository](https://github.com/canonical/jubilant)\n- [Migration guide](https://documentation.ubuntu.com/jubilant/how-to/migrate-from-pytest-operator/)【3:2†How to migrate from pytest-operator to Jubilant†https://documentation.ubuntu.com/jubilant/how-to/migrate-from-pytest-operator/】\n\n**In summary:** Jubilant is now the recommended way to write integration tests for Juju charms in Python, offering a more robust and approachable interface than its predecessors【3:4†Jubilant-backports, the joyful library for integration-testing charms ...†https://libraries.io/pypi/jubilant-backports】【3:9†jubilant - PyPI Package Security Analysis - Socket†https://socket.dev/pypi/package/jubilant】.","annotations":[{"text":"【3:0†jubilant · PyPI†https://pypi.org/project/jubilant/】","start_index":609,"end_index":665,"url_citation":{"title":"jubilant · PyPI","url":"https://pypi.org/project/jubilant/"}},{"text":"【3:1†Jubilant, the joyful library for driving Juju - GitHub†https://github.com/canonical/jubilant】","start_index":665,"end_index":763,"url_citation":{"title":"Jubilant, the joyful library for driving Juju - GitHub","url":"https://github.com/canonical/jubilant"}},{"text":"【3:8†Don’t fear Python subprocess or Go codegen†https://benhoyt.com/writings/jubilant/】","start_index":1214,"end_index":1301,"url_citation":{"title":"Don’t fear Python subprocess or Go codegen","url":"https://benhoyt.com/writings/jubilant/"}},{"text":"【3:2†How to migrate from pytest-operator to Jubilant†https://documentation.ubuntu.com/jubilant/how-to/migrate-from-pytest-operator/】","start_index":1507,"end_index":1639,"url_citation":{"title":"How to migrate from pytest-operator to Jubilant","url":"https://documentation.ubuntu.com/jubilant/how-to/migrate-from-pytest-operator/"}},{"text":"【3:3†How-to guides - Jubilant documentation†https://canonical-jubilant.readthedocs-hosted.com/how-to/】","start_index":1639,"end_index":1741,"url_citation":{"title":"How-to guides - Jubilant documentation","url":"https://canonical-jubilant.readthedocs-hosted.com/how-to/"}},{"text":"【3:0†jubilant · PyPI†https://pypi.org/project/jubilant/】","start_index":2844,"end_index":2900,"url_citation":{"title":"jubilant · PyPI","url":"https://pypi.org/project/jubilant/"}},{"text":"【3:2†How to migrate from pytest-operator to Jubilant†https://documentation.ubuntu.com/jubilant/how-to/migrate-from-pytest-operator/】","start_index":3836,"end_index":3968,"url_citation":{"title":"How to migrate from pytest-operator to Jubilant","url":"https://documentation.ubuntu.com/jubilant/how-to/migrate-from-pytest-operator/"}},{"text":"【3:4†Jubilant-backports, the joyful library for integration-testing charms ...†https://libraries.io/pypi/jubilant-backports】","start_index":4147,"end_index":4271,"url_citation":{"title":"Jubilant-backports, the joyful library for integration-testing charms ...","url":"https://libraries.io/pypi/jubilant-backports"}},{"text":"【3:9†jubilant - PyPI Package Security Analysis - Socket†https://socket.dev/pypi/package/jubilant】","start_index":4271,"end_index":4368,"url_citation":{"title":"jubilant - PyPI Package Security Analysis - Socket","url":"https://socket.dev/pypi/package/jubilant"}}]},"bing_searches":[{"text":"pytest-jubilant jubilant juju charm integration testing Python library","url":"https://www.bing.com/search?q=pytest-jubilant+jubilant+juju+charm+integration+testing+Python+library"}],"annotations":null}
````


---

<sub>⏱️ 1m 52s</sub>

### 💬 Copilot





---

<sub>⏱️ 1m 52s</sub>

### ✅ `bash`

**Read agent-0 full output**

$ cat /tmp/1772839548992-copilot-tool-output-47ph1h.txt

<details>
<summary>5 lines</summary>

```
Output too large to read at once (28.8 KB). Saved to: /tmp/copilot-tool-output-1772839565171-ttz6vo.txt
Consider using tools like grep (for searching), head/tail (for viewing start/end), view with view_range (for specific sections), or jq (for JSON) to examine portions of the output.

Preview (first 500 chars):
Agent completed. agent_id: agent-0, agent_type: explore, status: completed, description: Explore cur
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 1m 52s</sub>

### ✅ `web_fetch`

**https://documentation.ubuntu.com/jubilant/how-to/migrate-from-pytest-operator/**

<details>
<summary>Arguments</summary>

```json
{
  "url": "https://documentation.ubuntu.com/jubilant/how-to/migrate-from-pytest-operator/",
  "max_length": 20000
}
```

</details>

<details>
<summary>243 lines</summary>

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
    old \= juju.model\_config()\['update-status-hook-interval'\]
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

**https://pypi.org/project/pytest-jubilant/**

<details>
<summary>Arguments</summary>

```json
{
  "url": "https://pypi.org/project/pytest-jubilant/",
  "max_length": 10000
}
```

</details>

```
Contents of https://pypi.org/project/pytest-jubilant/:
A required part of this site couldn’t load. This may be due to a browser extension, network issues, or browser settings. Please check your connection, disable any ad blockers, or try using a different browser.
```


---

<sub>⏱️ 1m 58s</sub>

### ✅ `bash`

**Read full agent-0 output**

$ cat /tmp/copilot-tool-output-1772839565171-ttz6vo.txt

<details>
<summary>5 lines</summary>

```
Output too large to read at once (28.9 KB). Saved to: /tmp/copilot-tool-output-1772839571419-ds8stn.txt
Consider using tools like grep (for searching), head/tail (for viewing start/end), view with view_range (for specific sections), or jq (for JSON) to examine portions of the output.

Preview (first 500 chars):
Agent completed. agent_id: agent-0, agent_type: explore, status: completed, description: Explore cur
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 1m 59s</sub>

### ✅ `web_fetch`

**https://github.com/canonical/jubilant**

<details>
<summary>Arguments</summary>

```json
{
  "max_length": 15000,
  "url": "https://github.com/canonical/jubilant"
}
```

</details>

<details>
<summary>61 lines</summary>

````
Contents of https://github.com/canonical/jubilant:
## Jubilant, the joyful library for driving Juju

[](#jubilant-the-joyful-library-for-driving-juju)

Jubilant is a Python library that wraps the [Juju](https://juju.is/) CLI, primarily for use in charm integration tests. It provides methods that map 1:1 to Juju CLI commands, but with a type-annotated, Pythonic interface.

You should consider switching to Jubilant if your integration tests currently use [pytest-operator](https://github.com/charmed-kubernetes/pytest-operator) (and they probably do). Jubilant has an API you'll pick up quickly, and it avoids some of the pain points of [python-libjuju](https://github.com/juju/python-libjuju/), such as websocket failures and having to use `async`. Read our [design goals](https://documentation.ubuntu.com/jubilant/explanation/design-goals).

Jubilant 1.0.0 was released in April 2025. We'll avoid making breaking changes to the API after this point.

[**Read the full documentation**](https://documentation.ubuntu.com/jubilant/)

## Using Jubilant

[](#using-jubilant)

Jubilant is published to PyPI, so you can install and use it with your favorite Python package manager:

```
$ pip install jubilant
# or
$ uv add jubilant
```

Because Jubilant calls the Juju CLI, you'll also need to [install Juju](https://documentation.ubuntu.com/juju/3.6/howto/manage-juju/index.html#install-juju).

To use Jubilant in Python code:

import jubilant

juju \= jubilant.Juju()
juju.deploy('snappass-test')
juju.wait(jubilant.all\_active)

\# Or only wait for specific applications:
juju.wait(lambda status: jubilant.all\_active(status, 'snappass-test', 'another-app'))

Below is an example of a charm integration test. First we define a module-scoped [pytest fixture](https://docs.pytest.org/en/stable/explanation/fixtures.html) named `juju` which creates a temporary model and runs the test with a `Juju` instance pointing at that model. Jubilant's`temp_model` context manager creates the model during test setup and destroys it during teardown:

\# conftest.py
@pytest.fixture(scope\='module')
def juju():
    with jubilant.temp\_model() as juju:
        yield juju

\# test\_deploy.py
def test\_deploy(juju: jubilant.Juju):        \# Use the "juju" fixture
    juju.deploy('snappass-test')             \# Deploy the charm
    status \= juju.wait(jubilant.all\_active)  \# Wait till the app and unit are 'active'

    \# Hit the Snappass HTTP endpoint to ensure it's up and running.
    address \= status.apps\['snappass-test'\].units\['snappass-test/0'\].address
    response \= requests.get(f'http://{address}:5000/', timeout\=10)
    response.raise\_for\_status()
    assert 'snappass' in response.text.lower()

You don't have to use pytest with Jubilant, but it's what we recommend. Pytest's `assert`\-based approach is a straight-forward way to write tests, and its fixtures are helpful for structuring setup and teardown.

## Contributing and developing

[](#contributing-and-developing)

Anyone can contribute to Jubilant. It's best to start by [opening an issue](https://github.com/canonical/jubilant/issues) with a clear description of the problem or feature request, but you can also [open a pull request](https://github.com/canonical/jubilant/pulls) directly.

Jubilant uses [`uv`](https://docs.astral.sh/uv/) to manage Python dependencies and tools, so you'll need to [install uv](https://docs.astral.sh/uv/#installation) to work on the library. You'll also need `make` to run local development tasks (but you probably have `make` installed already).

After that, clone the Jubilant codebase and use `make all` to run various checks and the unit tests:

```
$ git clone https://github.com/canonical/jubilant
Cloning into 'jubilant'...
...
$ cd jubilant
$ make all
...
========== 107 passed in 0.26s ==========
```

To contribute a code change, write your fix or feature, add tests and docs, then run `make all` before you push and create a PR. Once you create a PR, GitHub will also run the integration tests, which takes several minutes.

## Doing a release

[](#doing-a-release)

To create a new release of Jubilant:

1.  Update the `__version__` field in [`jubilant/__init__.py`](https://github.com/canonical/jubilant/blob/main/jubilant/__init__.py) to the new version you want to release.
2.  Push up a PR with this change and get it reviewed and merged.
3.  Create a [new release](https://github.com/canonical/jubilant/releases/new) on GitHub with good release notes. The tag should start with a `v`, like `v1.2.3`. Once you've created the release, the [`publish.yaml` workflow](https://github.com/canonical/jubilant/blob/main/.github/workflows/publish.yaml) will automatically publish it to PyPI.
4.  Once the publish workflow has finished, check that the new version appears in the [PyPI version history](https://pypi.org/project/jubilant/#history).
````

</details>


---

<sub>⏱️ 2m 10s</sub>

### ✅ `web_search`

**pytest-jubilant PyPI package "pytest_jubilant" pack get_resources charm testing**

<details>
<summary>Arguments</summary>

```json
{
  "query": "pytest-jubilant PyPI package \"pytest_jubilant\" pack get_resources charm testing"
}
```

</details>

````
{"type":"text","text":{"value":"The `pytest-jubilant` PyPI package (imported as `pytest_jubilant`) is a pytest plugin specifically designed for charm integration testing using Juju and the Jubilant library. It facilitates and extends the workflow for charm testing, making it easier to migrate from the older `pytest-operator` approach.\n\n### Key Features of `pytest-jubilant`:\n\n1. **Fixtures for Juju and Charm Testing**\n   - The core fixture is `juju`, which is module- or model-scoped. By default, it uses a temporary Juju model for isolation and tears it down after test execution, unless you override with command-line options (`--keep-models`, `--no-teardown`, etc).\n   - Example:\n     ```python\n     from jubilant import Juju, all_active\n\n     def test_deploy(juju: Juju):\n         juju.deploy(\"./foo.charm\", \"foo\")\n         juju.wait(lambda status: all_active(status, \"foo\"), timeout=1000)\n     ```\n   - This shows how you can deploy and test charms in isolated environments, making integration testing much more reproducible and safer for parallel and automated CI/CD pipelines【3:0†pytest-jubilant · PyPI†https://pypi.org/project/pytest-jubilant/】【3:1†GitHub - canonical/jubilant: Jubilant is a Pythonic wrapper around the ...†https://github.com/canonical/jubilant】.\n\n2. **Temporary Model Management**\n   - The fixture `temp_model_factory` lets you manage multiple models per test module, supporting cross-model relations and complex scenarios more easily.\n   - Example:\n     ```python\n     @pytest.fixture\n     def istio(temp_model_factory):\n         yield temp_model_factory.get_juju(suffix=\"istio\")\n     ```\n\n3. **Pytest Command-Line Options**\n   - Customize how models are created, managed, and torn down. For example:\n     - `--model`: Set explicit model names.\n     - `--keep-models`: Skip teardown for debugging failed test environments.\n     - `--no-teardown`: Useful when running tests on pre-existing models.\n     - `--switch`: Automatically switch to the relevant Juju model for live inspection during tests【3:0†pytest-jubilant · PyPI†https://pypi.org/project/pytest-jubilant/】.\n\n4. **Migration from pytest-operator**\n   - If you previously used the `pytest-operator` and `python-libjuju`, you’re encouraged to migrate to Jubilant and `pytest-jubilant`. Jubilant provides a Pythonic, type-annotated API that closely matches the Juju CLI and avoids common problems such as dealing with asyncio or WebSocket issues【3:1†GitHub - canonical/jubilant: Jubilant is a Pythonic wrapper around the ...†https://github.com/canonical/jubilant】【3:5†How to migrate from pytest-operator to Jubilant†https://canonical-jubilant.readthedocs-hosted.com/how-to/migrate-from-pytest-operator/】.\n\n### `get_resources` Functionality\n\nThere is no specific mention of a `get_resources` function provided by the `pytest_jubilant` package itself in official documentation or code snippets. If you’re referring to resources in the context of Juju or charm testing (such as bundle assets, charm files, or resource files), you would typically use the standard Juju CLI or the announced interfaces of the Jubilant library rather than a direct `get_resources` call from this plugin.\n\n### In Summary\n\n- Use `pytest_jubilant` for robust, repeatable charm integration testing in Juju environments, with powerful fixtures and command-line options to control model lifecycles.\n- If you want to migrate from `pytest-operator`, this plugin and the Jubilant library make it smooth and more Pythonic【3:5†How to migrate from pytest-operator to Jubilant†https://canonical-jubilant.readthedocs-hosted.com/how-to/migrate-from-pytest-operator/】.\n- There isn’t an explicit `get_resources` function built into the testing pack; resource management is usually handled at the Juju or charm level.\n\nYou can find further documentation, usage guides, and API references on:\n- [PyPI for pytest-jubilant](https://pypi.org/project/pytest-jubilant/)【3:0†source】\n- [GitHub repository for canonical/jubilant](https://github.com/canonical/jubilant)【3:1†source】\n- [Migration guide from pytest-operator](https://canonical-jubilant.readthedocs-hosted.com/how-to/migrate-from-pytest-operator/)【3:5†source】","annotations":[{"text":"【3:0†pytest-jubilant · PyPI†https://pypi.org/project/pytest-jubilant/】","start_index":1053,"end_index":1123,"url_citation":{"title":"pytest-jubilant · PyPI","url":"https://pypi.org/project/pytest-jubilant/"}},{"text":"【3:1†GitHub - canonical/jubilant: Jubilant is a Pythonic wrapper around the ...†https://github.com/canonical/jubilant】","start_index":1123,"end_index":1241,"url_citation":{"title":"GitHub - canonical/jubilant: Jubilant is a Pythonic wrapper around the ...","url":"https://github.com/canonical/jubilant"}},{"text":"【3:0†pytest-jubilant · PyPI†https://pypi.org/project/pytest-jubilant/】","start_index":1994,"end_index":2064,"url_citation":{"title":"pytest-jubilant · PyPI","url":"https://pypi.org/project/pytest-jubilant/"}},{"text":"【3:1†GitHub - canonical/jubilant: Jubilant is a Pythonic wrapper around the ...†https://github.com/canonical/jubilant】","start_index":2399,"end_index":2517,"url_citation":{"title":"GitHub - canonical/jubilant: Jubilant is a Pythonic wrapper around the ...","url":"https://github.com/canonical/jubilant"}},{"text":"【3:5†How to migrate from pytest-operator to Jubilant†https://canonical-jubilant.readthedocs-hosted.com/how-to/migrate-from-pytest-operator/】","start_index":2517,"end_index":2657,"url_citation":{"title":"How to migrate from pytest-operator to Jubilant","url":"https://canonical-jubilant.readthedocs-hosted.com/how-to/migrate-from-pytest-operator/"}},{"text":"【3:5†How to migrate from pytest-operator to Jubilant†https://canonical-jubilant.readthedocs-hosted.com/how-to/migrate-from-pytest-operator/】","start_index":3442,"end_index":3582,"url_citation":{"title":"How to migrate from pytest-operator to Jubilant","url":"https://canonical-jubilant.readthedocs-hosted.com/how-to/migrate-from-pytest-operator/"}},{"text":"【3:0†source】","start_index":3876,"end_index":3888,"url_citation":{"title":"pytest-jubilant · PyPI","url":"https://pypi.org/project/pytest-jubilant/"}},{"text":"【3:1†source】","start_index":3972,"end_index":3984,"url_citation":{"title":"GitHub - canonical/jubilant: Jubilant is a Pythonic wrapper around the ...","url":"https://github.com/canonical/jubilant"}},{"text":"【3:5†source】","start_index":4113,"end_index":4125,"url_citation":{"title":"How to migrate from pytest-operator to Jubilant","url":"https://canonical-jubilant.readthedocs-hosted.com/how-to/migrate-from-pytest-operator/"}}]},"bing_searches":[{"text":"search(\"pytest-jubilant PyPI package \"pytest_jubilant\" pack get_resources charm testing\")","url":"https://www.bing.com/search?q=search%28%22pytest-jubilant+PyPI+package+%22pytest_jubilant%22+pack+get_resources+charm+testing%22%29"}],"annotations":null}
````


---

<sub>⏱️ 2m 16s</sub>

### ✅ `bash`

**Search agent output for relevant terms**

$ grep -n "pytest-jubilant\|pytest_jubilant\|pack\|get_resources" /tmp/copilot-tool-output-1772839571419-ds8stn.txt 2>/dev/null | head -30

<details>
<summary>7 lines</summary>

```
74:        config={"python-packages": "pydantic>=2.12.5", "src-overwrite": json.dumps(src_overwrite)},
254:package = false
328:explicit_package_bases = true
329:namespace_packages = true
350:no_package = true
1012:- **SamlRelationData**: Model for the full SAML relation data package (entity_id, metadata_url, certificates, endpoints)
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 2m 29s</sub>

### ✅ `web_search`

**site:pypi.org "pytest-jubilant" pack get_resources charm**

<details>
<summary>Arguments</summary>

```json
{
  "query": "site:pypi.org \"pytest-jubilant\" pack get_resources charm"
}
```

</details>

````
{"type":"text","text":{"value":"Based on the references found, here's the information regarding the terms you've asked about:\n\n- **pytest-jubilant** is a pytest plugin that helps transition from pytest-operator to Jubilant, a Pythonic wrapper around the Juju CLI designed primarily for charm integration tests. It introduces fixtures and utilities for managing Juju models and executing integration tests for charms【3:0†pytest-jubilant · PyPI†https://pypi.org/project/pytest-jubilant/】【3:2†GitHub - canonical/jubilant...†https://github.com/canonical/jubilant】【3:7†jubilant · PyPI†https://pypi.org/project/jubilant/】【3:4†Jubilant documentation†https://documentation.ubuntu.com/jubilant/】【3:1†How to migrate from pytest-operator to Jubilant†https://canonical-jubilant.readthedocs-hosted.com/how-to/migrate-from-pytest-operator/】.\n\n### Relevant Features\n\n#### 1. **Fixtures for Charm Testing**\n   - The main fixture is `juju`, which by default uses a temporary model that is set up and torn down for each test context.\n   - Additional fixtures such as `temp_model_factory` allow managing multiple Juju models in tests, for instance, for cross-model relations.\n   - Usage Example:\n     ```python\n     from jubilant import Juju, all_active\n     def test_deploy(juju: Juju):\n         juju.deploy(\"./foo.charm\", \"foo\")\n         juju.wait(lambda status: all_active(status, \"foo\"), timeout=1000)\n     ```\n\n#### 2. **Model Management**\n   - Command-line options let you control model lifecycles during test runs:\n     - `--model` to use a fixed model name,\n     - `--keep-models` to skip teardown,\n     - `--no-teardown` to avoid destroying models you care about,\n     - `--switch` to switch your Juju CLI context into the model created by the test.\n\n#### 3. **Migrating from `pytest-operator`**\n   - Jubilant and the pytest-jubilant plugin provide similar APIs to make it easier to port existing integration tests from pytest-operator. The migration guide provides step-by-step assistance【3:1†source】.\n\n#### 4. **Resource Management**\n   - If your question about `get_resources` refers to working with Juju model/application resources, Jubilant (and by extension, pytest-jubilant) exposes the Juju CLI, so most interactions with charm resources are performed via the `juju` object methods or `juju.cli()` calls (e.g., running `juju resources` as a subprocess).\n   - There is no explicit mention of a `get_resources` method in the plugin; instead, resource handling is performed via direct CLI commands (e.g., `juju.resources('your-charm')` via the CLI).\n\n#### 5. **Using with Packs and Charms**\n   - Tests can deploy local charms (`.charm` files) or integrate charms/packs into Juju models using the patterns demonstrated. You interact with pre-built charm packs by specifying their paths or names in deployment calls.\n\nIf you need to work with charm resources as part of your integration workflow, you'd typically use Juju's resource management via the CLI within your tests, leveraging the methods and fixtures provided by Jubilant. If you have a more specific question about handling resources or packs, please clarify further!\n\nFurther reading and detailed usages can be found in the [pytest-jubilant PyPI entry][3:0†source], [Jubilant documentation][3:4†source], and the [migration how-to][3:1†source].","annotations":[{"text":"【3:0†pytest-jubilant · PyPI†https://pypi.org/project/pytest-jubilant/】","start_index":383,"end_index":453,"url_citation":{"title":"pytest-jubilant · PyPI","url":"https://pypi.org/project/pytest-jubilant/"}},{"text":"【3:2†GitHub - canonical/jubilant...†https://github.com/canonical/jubilant】","start_index":453,"end_index":527,"url_citation":{"title":"GitHub - canonical/jubilant: Jubilant is a Pythonic wrapper around the ...","url":"https://github.com/canonical/jubilant"}},{"text":"【3:7†jubilant · PyPI†https://pypi.org/project/jubilant/】","start_index":527,"end_index":583,"url_citation":{"title":"jubilant · PyPI","url":"https://pypi.org/project/jubilant/"}},{"text":"【3:4†Jubilant documentation†https://documentation.ubuntu.com/jubilant/】","start_index":583,"end_index":654,"url_citation":{"title":"Jubilant documentation","url":"https://documentation.ubuntu.com/jubilant/"}},{"text":"【3:1†How to migrate from pytest-operator to Jubilant†https://canonical-jubilant.readthedocs-hosted.com/how-to/migrate-from-pytest-operator/】","start_index":654,"end_index":794,"url_citation":{"title":"How to migrate from pytest-operator to Jubilant","url":"https://canonical-jubilant.readthedocs-hosted.com/how-to/migrate-from-pytest-operator/"}},{"text":"【3:1†source】","start_index":1947,"end_index":1959,"url_citation":{"title":"How to migrate from pytest-operator to Jubilant","url":"https://canonical-jubilant.readthedocs-hosted.com/how-to/migrate-from-pytest-operator/"}}]},"bing_searches":[{"text":"search(\"site:pypi.org \"pytest-jubilant\" pack get_resources charm\")","url":"https://www.bing.com/search?q=search%28%22site%3Apypi.org+%22pytest-jubilant%22+pack+get_resources+charm%22%29"}],"annotations":null}
````


---

<sub>⏱️ 2m 34s</sub>

### 💬 Copilot

Now let me read the actual source files and find more about pytest-jubilant's API:

---

<sub>⏱️ 2m 34s</sub>

### ✅ `view`

**/tmp/saml-integrator-L4-opus/tests/integration**

/tmp/saml-integrator-L4-opus/tests/integration

```
__init__.py
any_charm.py
conftest.py
test_charm.py
```


---

<sub>⏱️ 2m 35s</sub>

### ✅ `web_fetch`

**https://github.com/canonical/jubilant/tree/main/jubilant**

<details>
<summary>Arguments</summary>

```json
{
  "max_length": 20000,
  "url": "https://github.com/canonical/jubilant/tree/main/jubilant"
}
```

</details>

<details>
<summary>117 lines</summary>

```
Contents of https://github.com/canonical/jubilant/tree/main/jubilant:
*   *   AI CODE CREATION
        
        *   [
            
            GitHub CopilotWrite better code with AI
            
            
            
            ](https://github.com/features/copilot)
        *   [
            
            GitHub SparkBuild and deploy intelligent apps
            
            
            
            ](https://github.com/features/spark)
        *   [
            
            GitHub ModelsManage and compare prompts
            
            
            
            ](https://github.com/features/models)
        *   [
            
            MCP RegistryNewIntegrate external tools
            
            
            
            ](https://github.com/mcp)
        
    *   DEVELOPER WORKFLOWS
        
        *   [
            
            ActionsAutomate any workflow
            
            
            
            ](https://github.com/features/actions)
        *   [
            
            CodespacesInstant dev environments
            
            
            
            ](https://github.com/features/codespaces)
        *   [
            
            IssuesPlan and track work
            
            
            
            ](https://github.com/features/issues)
        *   [
            
            Code ReviewManage code changes
            
            
            
            ](https://github.com/features/code-review)
        
    *   APPLICATION SECURITY
        
        *   [
            
            GitHub Advanced SecurityFind and fix vulnerabilities
            
            
            
            ](https://github.com/security/advanced-security)
        *   [
            
            Code securitySecure your code as you build
            
            
            
            ](https://github.com/security/advanced-security/code-security)
        *   [
            
            Secret protectionStop leaks before they start
            
            
            
            ](https://github.com/security/advanced-security/secret-protection)
        
    *   EXPLORE
        
        *   [Why GitHub](https://github.com/why-github)
        *   [Documentation](https://docs.github.com)
        *   [Blog](https://github.blog)
        *   [Changelog](https://github.blog/changelog)
        *   [Marketplace](https://github.com/marketplace)
        
    
    [View all features](https://github.com/features)
    
*   *   BY COMPANY SIZE
        
        *   [Enterprises](https://github.com/enterprise)
        *   [Small and medium teams](https://github.com/team)
        *   [Startups](https://github.com/enterprise/startups)
        *   [Nonprofits](https://github.com/solutions/industry/nonprofits)
        
    *   BY USE CASE
        
        *   [App Modernization](https://github.com/solutions/use-case/app-modernization)
        *   [DevSecOps](https://github.com/solutions/use-case/devsecops)
        *   [DevOps](https://github.com/solutions/use-case/devops)
        *   [CI/CD](https://github.com/solutions/use-case/ci-cd)
        *   [View all use cases](https://github.com/solutions/use-case)
        
    *   BY INDUSTRY
        
        *   [Healthcare](https://github.com/solutions/industry/healthcare)
        *   [Financial services](https://github.com/solutions/industry/financial-services)
        *   [Manufacturing](https://github.com/solutions/industry/manufacturing)
        *   [Government](https://github.com/solutions/industry/government)
        *   [View all industries](https://github.com/solutions/industry)
        
    
    [View all solutions](https://github.com/solutions)
    
*   *   EXPLORE BY TOPIC
        
        *   [AI](https://github.com/resources/articles?topic=ai)
        *   [Software Development](https://github.com/resources/articles?topic=software-development)
        *   [DevOps](https://github.com/resources/articles?topic=devops)
        *   [Security](https://github.com/resources/articles?topic=security)
        *   [View all topics](https://github.com/resources/articles)
        
    *   EXPLORE BY TYPE
        
        *   [Customer stories](https://github.com/customer-stories)
        *   [Events & webinars](https://github.com/resources/events)
        *   [Ebooks & reports](https://github.com/resources/whitepapers)
        *   [Business insights](https://github.com/solutions/executive-insights)
        *   [GitHub Skills](https://skills.github.com)
        
    *   SUPPORT & SERVICES
        
        *   [Documentation](https://docs.github.com)
        *   [Customer support](https://support.github.com)
        *   [Community forum](https://github.com/orgs/community/discussions)
        *   [Trust center](https://github.com/trust-center)
        *   [Partners](https://github.com/partners)
        
    
    [View all resources](https://github.com/resources)
    
*   *   COMMUNITY
        
        *   [
            
            GitHub SponsorsFund open source developers
            
            
            
            ](https://github.com/sponsors)
        
    *   PROGRAMS
        
        *   [Security Lab](https://securitylab.github.com)
        *   [Maintainer Community](https://maintainers.github.com)
        *   [Accelerator](https://github.com/accelerator)
        *   [Archive Program](https://archiveprogram.github.com)
        
    *   REPOSITORIES
        
        *   [Topics](https://github.com/topics)
        *   [Trending](https://github.com/trending)
        *   [Collections](https://github.com/collections)
        
    
*   *   ENTERPRISE SOLUTIONS
        
        *   [
            
            Enterprise platformAI-powered developer platform
            
            
            
            ](https://github.com/enterprise)
        
    *   AVAILABLE ADD-ONS
        
        *   [
            
            GitHub Advanced SecurityEnterprise-grade security features
            
            
            
            ](https://github.com/security/advanced-security)
        *   [
            
            Copilot for BusinessEnterprise-grade AI features
            
            
            
            ](https://github.com/features/copilot/copilot-business)
        *   [
            
            Premium SupportEnterprise-grade 24/7 support
            
            
            
            ](https://github.com/premium-support)
        
    
*   [Pricing](https://github.com/pricing)

## Provide feedback

We read every piece of feedback, and take your input very seriously.

Include my email address so I can be contacted

## Saved searches

## Use saved searches to filter your results more quickly

[Sign in](/login?return_to=https%3A%2F%2Fgithub.com%2Fcanonical%2Fjubilant%2Ftree%2Fmain%2Fjubilant)

[Sign up](/signup?ref_cta=Sign+up&ref_loc=header+logged+out&ref_page=%2F%3Cuser-name%3E%2F%3Crepo-name%3E%2Ffiles%2Fdisambiguate&source=header-repo&source_repo=canonical%2Fjubilant)

Appearance settings
```

</details>


---

<sub>⏱️ 2m 35s</sub>

### ❌ `web_fetch`

**https://github.com/canonical/pytest-jubilant**

<details>
<summary>Arguments</summary>

```json
{
  "max_length": 15000,
  "url": "https://github.com/canonical/pytest-jubilant"
}
```

</details>

```
Error: Failed to fetch https://github.com/canonical/pytest-jubilant - status code 404
```


---

<sub>⏱️ 2m 42s</sub>

### ✅ `view`

**/tmp/saml-integrator-L4-opus/tests/integration/conftest.py**

/tmp/saml-integrator-L4-opus/tests/integration/conftest.py

<details>
<summary>58 lines</summary>

```
1. # Copyright 2025 Canonical Ltd.
2. # See LICENSE file for licensing details.
3. 
4. """Fixtures for the SAML Integrator charm integration tests."""
5. 
6. import json
7. from pathlib import Path
8. 
9. import pytest_asyncio
10. import yaml
11. from pytest import Config, fixture
12. from pytest_operator.plugin import OpsTest
13. 
14. 
15. @fixture(scope="module", name="app_name")
16. def app_name_fixture():
17.     """Provide app name from the metadata."""
18.     metadata = yaml.safe_load(Path("./metadata.yaml").read_text("utf-8"))
19.     yield metadata["name"]
20. 
21. 
22. @pytest_asyncio.fixture(scope="module")
23. async def app(ops_test: OpsTest, pytestconfig: Config, app_name: str):
24.     """SAML Integrator charm used for integration testing.
25. 
26.     Build the charm and deploy it along with Anycharm.
27.     """
28.     charm = pytestconfig.getoption("--charm-file")
29.     assert ops_test.model
30.     application = await ops_test.model.deploy(
31.         f"./{charm}",
32.         application_name=app_name,
33.     )
34.     yield application
35. 
36. 
37. @pytest_asyncio.fixture(scope="module")
38. async def any_charm(ops_test: OpsTest):
39.     """SAML Integrator charm used for integration testing.
40. 
41.     Build the charm and deploy it along with Anycharm.
42.     """
43.     path_lib = "lib/charms/saml_integrator/v0/saml.py"
44.     saml_lib = Path(path_lib).read_text(encoding="utf8")
45.     any_charm_script = Path("tests/integration/any_charm.py").read_text(encoding="utf8")
46.     src_overwrite = {
47.         "saml.py": saml_lib,
48.         "any_charm.py": any_charm_script,
49.     }
50.     assert ops_test.model
51.     application = await ops_test.model.deploy(
52.         "any-charm",
53.         application_name="any",
54.         channel="beta",
55.         config={"python-packages": "pydantic>=2.12.5", "src-overwrite": json.dumps(src_overwrite)},
56.     )
57.     yield application
58.
```

</details>


---

<sub>⏱️ 2m 42s</sub>

### ✅ `view`

**/tmp/saml-integrator-L4-opus/tests/integration/test_charm.py**

/tmp/saml-integrator-L4-opus/tests/integration/test_charm.py

<details>
<summary>52 lines</summary>

```
1. #!/usr/bin/env python3
2. # Copyright 2025 Canonical Ltd.
3. # See LICENSE file for licensing details.
4. 
5. """SAML Integrator charm integration tests."""
6. 
7. import ops
8. import pytest
9. from pytest_operator.plugin import OpsTest
10. 
11. 
12. @pytest.mark.asyncio
13. @pytest.mark.abort_on_fail
14. async def test_active(ops_test: OpsTest, app: ops.Application):
15.     """Check that the charm is active.
16. 
17.     Assume that the charm has already been built and is running.
18.     """
19.     await app.set_config(  # type: ignore[attr-defined]
20.         {
21.             "entity_id": "https://login.staging.ubuntu.com",
22.             "fingerprint": "",
23.             "metadata_url": "https://login.staging.ubuntu.com/saml/metadata",
24.         }
25.     )
26.     status_name = ops.ActiveStatus.name  # type: ignore[has-type]
27.     assert ops_test.model
28.     await ops_test.model.wait_for_idle(status=status_name, raise_on_error=True)
29.     assert app.units[0].workload_status == status_name  # type: ignore
30. 
31. 
32. @pytest.mark.asyncio
33. @pytest.mark.abort_on_fail
34. async def test_relation(ops_test: OpsTest, app: ops.Application, any_charm: ops.Application):
35.     """Check that the charm is active once related to another charm.
36. 
37.     Assume that the charm has already been built and is running.
38.     """
39.     relation_name = f"{app.name}:saml"
40.     assert ops_test.model
41.     await ops_test.model.add_relation(f"{any_charm.name}:require-saml", relation_name)
42.     await app.set_config(  # type: ignore[attr-defined]
43.         {
44.             "entity_id": "https://login.staging.ubuntu.com",
45.             "fingerprint": "",
46.             "metadata_url": "https://login.staging.ubuntu.com/saml/metadata",
47.         }
48.     )
49.     status_name = ops.ActiveStatus.name  # type: ignore[has-type]
50.     await ops_test.model.wait_for_idle(status=status_name, raise_on_error=True)
51.     assert app.units[0].workload_status == status_name  # type: ignore
52.
```

</details>


---

<sub>⏱️ 2m 42s</sub>

### ✅ `view`

**/tmp/saml-integrator-L4-opus/tests/integration/any_charm.py**

/tmp/saml-integrator-L4-opus/tests/integration/any_charm.py

<details>
<summary>29 lines</summary>

```
1. # Copyright 2025 Canonical Ltd.
2. # See LICENSE file for licensing details.
3. 
4. # pylint: disable=import-error,consider-using-with,no-member
5. 
6. """This code snippet is used to be loaded into any-charm which is used for integration tests."""
7. 
8. from any_charm_base import AnyCharmBase
9. 
10. import saml
11. 
12. 
13. class AnyCharm(AnyCharmBase):  # pylint: disable=too-few-public-methods
14.     """Execute a simple charm workload to test the saml relation.
15. 
16.     Attrs:
17.         saml: The attribute that mimics a real SAML relation.
18.     """
19. 
20.     def __init__(self, *args, **kwargs):
21.         """Init function for the class.
22. 
23.         Args:
24.             args: Variable list of positional arguments passed to the parent constructor.
25.             kwargs: Variable list of positional keyword arguments passed to the parent constructor.
26.         """
27.         super().__init__(*args, **kwargs)
28.         self.saml = saml.SamlRequires(self)
29.
```

</details>


---

<sub>⏱️ 2m 42s</sub>

### ✅ `view`

**/tmp/saml-integrator-L4-opus/tests/integration/__init__.py**

/tmp/saml-integrator-L4-opus/tests/integration/__init__.py

```
1. # Copyright 2025 Canonical Ltd.
2. # See LICENSE file for licensing details.
3. 
```


---

<sub>⏱️ 2m 42s</sub>

### ✅ `view`

**/tmp/saml-integrator-L4-opus/pyproject.toml**

/tmp/saml-integrator-L4-opus/pyproject.toml

<details>
<summary>151 lines</summary>

```
1. # Copyright 2025 Canonical Ltd.
2. # See LICENSE file for licensing details.
3. 
4. [project]
5. name = "saml-integrator-operator"
6. version = "0.0.0"
7. description = "SAML Integrator to abstract SAML IdP details."
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
19.   "lxml==6.0.2",
20.   "ops==3.6.0",
21.   "pydantic==2.12.5",
22.   "signxml==4.3.0",
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
39.   "types-mock",
40.   "types-pyyaml",
41.   "types-requests",
42. ]
43. unit = [
44.   "coverage[toml]",
45.   "pytest",
46. ]
47. coverage-report = [
48.   "coverage[toml]",
49.   "pytest",
50. ]
51. static = [
52.   "bandit[toml]",
53. ]
54. interface = [
55.   "ops-scenario",
56.   "pytest",
57.   "pytest-interface-tester",
58. ]
59. integration = [
60.   "allure-pytest>=2.8.18",
61.   "allure-pytest-collection-report @ git+https://github.com/canonical/data-platform-workflows@v24.0.0#subdirectory=python/pytest_plugins/allure_pytest_collection_report",
62.   "juju",
63.   "pytest",
64.   "pytest-asyncio",
65.   "pytest-operator",
66. ]
67. 
68. [tool.uv]
69. package = false
70. 
71. [tool.ruff]
72. target-version = "py310"
73. line-length = 99
74. 
75. # enable ruff linters:
76. #   A flake8-builtins
77. #   B flake8-bugbear
78. # CPY flake8-copyright
79. #   D pydocstyle
80. # E/W pycodestyle
81. #   F Pyflakes
82. #   I isort
83. #   N pep8-naming
84. # RUF Ruff-specific rules
85. #   S flake8-bandit
86. # SIM flake8-simplify
87. #  TC flake8-type-checking
88. #  UP pyupgrade
89. lint.select = [ "A", "B", "C", "CPY", "D", "E", "F", "I", "N", "RUF", "S", "SIM", "TC", "UP", "W" ]
90. lint.ignore = [
91.   "B904",
92.   "D107",
93.   "D203",
94.   "D204",
95.   "D205",
96.   "D213",
97.   "D215",
98.   "D400",
99.   "D404",
100.   "D406",
101.   "D407",
102.   "D408",
103.   "D409",
104.   "D413",
105.   "E501",
106.   "S105",
107.   "S603",
108.   "TC002",
109.   "TC006",
110.   "UP006",
111.   "UP007",
112.   "UP035",
113.   "UP045",
114. ]
115. lint.per-file-ignores."tests/*" = [ "B011", "D100", "D101", "D102", "D103", "D104", "D212", "D415", "D417", "S" ]
116. lint.flake8-copyright.author = "Canonical Ltd."
117. lint.flake8-copyright.min-file-size = 1
118. lint.flake8-copyright.notice-rgx = "Copyright\\s\\d{4}([-,]\\d{4})*\\s+"
119. lint.mccabe.max-complexity = 10
120. lint.pydocstyle.convention = "google"
121. 
122. [tool.codespell]
123. skip = "build,lib,venv,icon.svg,.tox,.git,.mypy_cache,.ruff_cache,.coverage,htmlcov,uv.lock,grafana_dashboards"
124. 
125. [tool.pytest.ini_options]
126. minversion = "6.0"
127. log_cli_level = "INFO"
128. markers = [ "requires_secrets: mark tests that require external secrets" ]
129. pythonpath = [
130.   "lib",
131.   "src"
132. ]
133. 
134. [tool.coverage.run]
135. branch = true
136. 
137. [tool.coverage.report]
138. fail_under = 99
139. show_missing = true
140. 
141. [tool.mypy]
142. ignore_missing_imports = true
143. explicit_package_bases = true
144. namespace_packages = true
145. 
146. [tool.bandit]
147. exclude_dirs = [ "/venv/" ]
148. 
149. [tool.bandit.assert_used]
150. skips = [ "*/*test.py", "*/test_*.py", "*tests/*.py" ]
151.
```

</details>


---

<sub>⏱️ 2m 42s</sub>

### ✅ `view`

**/tmp/saml-integrator-L4-opus/tox.toml**

/tmp/saml-integrator-L4-opus/tox.toml

<details>
<summary>167 lines</summary>

```
1. # Copyright 2025 Canonical Ltd.
2. # See LICENSE file for licensing details.
3. 
4. skipsdist = true
5. skip_missing_interpreters = true
6. envlist = [ "lint", "unit", "static", "interface", "coverage-report" ]
7. requires = [ "tox>=4.21" ]
8. no_package = true
9. 
10. [env_run_base]
11. passenv = [ "PYTHONPATH", "CHARM_BUILD_DIR", "MODEL_SETTINGS" ]
12. runner = "uv-venv-lock-runner"
13. 
14. [env_run_base.setenv]
15. PYTHONPATH = "{toxinidir}:{toxinidir}/lib:{[vars]src_path}"
16. PYTHONBREAKPOINT = "ipdb.set_trace"
17. PY_COLORS = "1"
18. 
19. [env.fmt]
20. description = "Apply coding style standards to code"
21. commands = [
22.   [
23.     "ruff",
24.     "check",
25.     "--fix",
26.     "--select",
27.     "I",
28.     { replace = "ref", of = [
29.       "vars",
30.       "all_path",
31.     ], extend = true },
32.   ],
33.   [
34.     "ruff",
35.     "format",
36.     { replace = "ref", of = [
37.       "vars",
38.       "all_path",
39.     ], extend = true },
40.   ],
41. ]
42. dependency_groups = [ "fmt" ]
43. 
44. [env.lint]
45. description = "Check code against coding style standards"
46. commands = [
47.   [
48.     "codespell",
49.     "{toxinidir}",
50.   ],
51.   [
52.     "ruff",
53.     "format",
54.     "--check",
55.     "--diff",
56.     { replace = "ref", of = [
57.       "vars",
58.       "all_path",
59.     ], extend = true },
60.   ],
61.   [
62.     "ruff",
63.     "check",
64.     { replace = "ref", of = [
65.       "vars",
66.       "all_path",
67.     ], extend = true },
68.   ],
69.   [
70.     "mypy",
71.     { replace = "ref", of = [
72.       "vars",
73.       "all_path",
74.     ], extend = true },
75.   ],
76. ]
77. dependency_groups = [ "lint" ]
78. 
79. [env.unit]
80. description = "Run unit tests"
81. commands = [
82.   [
83.     "coverage",
84.     "run",
85.     "--source={[vars]src_path},{[vars]lib_path}",
86.     "-m",
87.     "pytest",
88.     "--ignore={[vars]tst_path}integration",
89.     "--ignore={[vars]tst_path}interface",
90.     "-v",
91.     "--tb",
92.     "native",
93.     "-s",
94.     { replace = "posargs", extend = "true" },
95.   ],
96.   [
97.     "coverage",
98.     "report",
99.   ],
100. ]
101. dependency_groups = [ "unit" ]
102. 
103. [env.coverage-report]
104. description = "Create test coverage report"
105. commands = [ [ "coverage", "report" ] ]
106. dependency_groups = [ "coverage-report" ]
107. 
108. [env.static]
109. description = "Run static analysis tests"
110. commands = [ [ "bandit", "-c", "{toxinidir}/pyproject.toml", "-r", "{[vars]src_path}", "{[vars]tst_path}" ] ]
111. dependency_groups = [ "static" ]
112. 
113. [env.interface]
114. description = "Run unit tests"
115. commands = [
116.   [
117.     "pytest",
118.     "-v",
119.     "--tb",
120.     "native",
121.     "{[vars]tst_path}/interface",
122.     "--log-cli-level=INFO",
123.     "-s",
124.     { replace = "posargs", extend = "true" },
125.   ],
126. ]
127. dependency_groups = [ "interface" ]
128. 
129. [env.integration]
130. description = "Run integration tests"
131. commands = [
132.   [
133.     "pytest",
134.     "-v",
135.     "--tb",
136.     "native",
137.     "--ignore={[vars]tst_path}unit",
138.     "--ignore={[vars]tst_path}interface",
139.     "--log-cli-level=INFO",
140.     "-s",
141.     { replace = "posargs", extend = "true" },
142.   ],
143. ]
144. dependency_groups = [ "integration" ]
145. 
146. [env.lint-fix]
147. description = "Apply coding style standards to code"
148. commands = [
149.   [
150.     "ruff",
151.     "check",
152.     "--fix",
153.     "--fix-only",
154.     { replace = "ref", of = [
155.       "vars",
156.       "all_path",
157.     ], extend = true },
158.   ],
159. ]
160. dependency_groups = [ "lint" ]
161. 
162. [vars]
163. src_path = "{toxinidir}/src/"
164. tst_path = "{toxinidir}/tests/"
165. lib_path = "{toxinidir}/lib/charms/saml_integrator"
166. all_path = [ "{toxinidir}/src/", "{toxinidir}/tests/", "{toxinidir}/lib/charms/saml_integrator" ]
167.
```

</details>


---

<sub>⏱️ 2m 42s</sub>

### ✅ `view`

**/tmp/saml-integrator-L4-opus/charmcraft.yaml**

/tmp/saml-integrator-L4-opus/charmcraft.yaml

<details>
<summary>20 lines</summary>

```
1. # Copyright 2025 Canonical Ltd.
2. # See LICENSE file for licensing details.
3. 
4. # Learn more about charmcraft.yaml configuration at:
5. # https://juju.is/docs/sdk/charmcraft-config
6. type: "charm"
7. bases:
8.   - build-on:
9.       - name: "ubuntu"
10.         channel: "22.04"
11.     run-on:
12.       - name: "ubuntu"
13.         channel: "22.04"
14. parts:
15.   charm:
16.     source: .
17.     plugin: uv
18.     build-snaps:
19.     - astral-uv
20.
```

</details>


---

<sub>⏱️ 2m 42s</sub>

### ✅ `view`

**/tmp/saml-integrator-L4-opus/metadata.yaml**

/tmp/saml-integrator-L4-opus/metadata.yaml

<details>
<summary>32 lines</summary>

```
1. # Copyright 2025 Canonical Ltd.
2. # See LICENSE file for licensing details.
3. 
4. name: saml-integrator
5. display-name: SAML Integrator
6. summary: SAML Integrator to abstract SAML IdP details.
7. description: |
8.   A [Juju](https://juju.is/) [charm](https://juju.is/docs/olm/charmed-operators)
9.   deploying and managing a SAML Integrator on Kubernetes and bare metal. SAML is an XML-based
10.   open-standard for transferring identity data between two parties: an identity
11.   provider (IdP) and a service provider (SP).
12. 
13.   This charm simplifies configuration of SAML SPs by providing a single point
14.   of configuration for all the requirers using the same SAML entity. It can be
15.   deployed on many different Kubernetes platforms, from [MicroK8s](https://microk8s.io)
16.   to [Charmed Kubernetes](https://ubuntu.com/kubernetes) and public cloud Kubernetes
17.   offerings.
18. 
19.   As such, the charm makes it easy to manage and propagate SAML configuration, while
20.   giving the freedom to deploy on the Kubernetes platform of their choice.
21. 
22.   For DevOps or SRE teams this charm will make operating any charm leveraging SAML
23.   authentication simple and straightforward through Juju's clean interface.
24. docs: https://discourse.charmhub.io/t/saml-integrator-documentation-overview/11293
25. issues: https://github.com/canonical/saml-integrator-operator/issues
26. maintainers:
27.   - https://launchpad.net/~canonical-is-devops
28. source: https://github.com/canonical/saml-integrator-operator
29. provides:
30.   saml:
31.     interface: saml
32.
```

</details>


---

<sub>⏱️ 2m 50s</sub>

### 💬 Copilot

Now let me search for pytest-jubilant specifically to understand `pack()` and `get_resources()`:

---

<sub>⏱️ 2m 50s</sub>

### ✅ `web_fetch`

**https://pypi.org/project/pytest-jubilant/**

<details>
<summary>Arguments</summary>

```json
{
  "max_length": 15000,
  "url": "https://pypi.org/project/pytest-jubilant/",
  "raw": true
}
```

</details>

<details>
<summary>90 lines</summary>

```
Here is the raw content:
Contents of https://pypi.org/project/pytest-jubilant/:
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta
      http-equiv="Content-Security-Policy"
      content="default-src 'self'; img-src 'self' data:; media-src 'self' data:; object-src 'none'; style-src 'self' 'sha256-o4vzfmmUENEg4chMjjRP9EuW9ucGnGIGVdbl8d0SHQQ='; script-src 'self' 'sha256-KXex2o39zxtnzVWK4H5rW07g2+BlwSPtn+aguzsWkNg=';"
    />
    <link
      href="/_fs-ch-1T1wmsGaOgGaSxcX/assets/inter-var.woff2"
      rel="preload"
      as="font"
      type="font/woff2"
      crossorigin
    />
    <link href="/_fs-ch-1T1wmsGaOgGaSxcX/assets/styles.css" rel="stylesheet" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Client Challenge</title>
    <style>
      #loading-error {
        font-size: 16px;
        font-family: 'Inter', sans-serif;
        margin-top: 10px;
        margin-left: 10px;
        display: none;
      }
    </style>
  </head>
  <body>
    <noscript>
      <div class="noscript-container">
        <div class="noscript-content">
          <img
            src="/_fs-ch-1T1wmsGaOgGaSxcX/assets/errorIcon.svg"
            alt=""
            role="presentation"
            class="error-icon"
          />
          <span class="noscript-span"
            >JavaScript is disabled in your browser.</span
          >
          <p>Please enable JavaScript to proceed.</p>
        </div>
      </div>
    </noscript>
    <div id="loading-error" role="alert" aria-live="polite">
      A required part of this site couldn’t load. This may be due to a browser
      extension, network issues, or browser settings. Please check your
      connection, disable any ad blockers, or try using a different browser.
    </div>
    <script>
      function loadScript(src) {
        return new Promise((resolve, reject) => {
          const script = document.createElement('script');
          script.onload = resolve;
          script.onerror = (event) => {
            console.error('Script load error event:', event);
            document.getElementById('loading-error').style.display = 'block';
            loadingError.setAttribute('aria-hidden', 'false');
            reject(
              new Error(
                `Failed to load script: ${src}, Please contact the service administrator.`
              )
            );
          };
          script.src = src;
          document.body.appendChild(script);
        });
      }

      loadScript('/_fs-ch-1T1wmsGaOgGaSxcX/errors.js')
        .then(() => {
          const script = document.createElement('script');
          script.src = '/_fs-ch-1T1wmsGaOgGaSxcX/script.js?reload=true';
          script.onerror = (event) => {
            console.error('Script load error event:', event);
            const errorMsg = new Error(
              `Failed to load script: ${script.src}. Please contact the service administrator.`
            );
            console.error(errorMsg);
            handleScriptError();
          };
          document.body.appendChild(script);
        })
        .catch((error) => {
          console.error(error);
        });
    </script>
  </body>
</html>
```

</details>


---

<sub>⏱️ 2m 51s</sub>

### ✅ `github-mcp-server-search_code`

**pytest_jubilant pack get_resources org:canonical**

<details>
<summary>Arguments</summary>

```json
{
  "query": "pytest_jubilant pack get_resources org:canonical"
}
```

</details>

```
Output too large to read at once (38.6 KB). Saved to: /tmp/1772839623845-copilot-tool-output-kiffo3.txt
Consider using tools like grep (for searching), head/tail (for viewing start/end), view with view_range (for specific sections), or jq (for JSON) to examine portions of the output.

Preview (first 500 chars):
{"total_count":8,"incomplete_results":false,"items":[{"name":"conftest.py","path":"tests/integration/conftest.py","sha":"760ee5909385c07f3cb4fc40476b52dd3cebdbc8","html_url":"https://github.com/canonical/parca-k8s-operator/blob/dbd1d4875822864aa11ba5dea56c3fa93a481ebc/tests/integration/conftest.py","repository":{"id":519003246,"node_id":"R_kgDOHu9cbg","owner":{"login":"canonical","id":53057619,"node_id":"MDEyOk9yZ2FuaXphdGlvbjUzMDU3NjE5","avatar_url":"https://avatars.githubusercontent.com/u/5305
```


---

<sub>⏱️ 2m 56s</sub>

### ✅ `bash`

**Parse search results**

$ head -200 /tmp/1772839623845-copilot-tool-output-kiffo3.txt | python3 -c "import sys,json; data=json.load(sys.stdin); [print(f'{it[\"repository\"][\"full_name\"]} - {it[\"path\"]}') for it in data['items']]"

<details>
<summary>9 lines</summary>

```
canonical/parca-k8s-operator - tests/integration/conftest.py
canonical/tempo-operators - tests/integration/test_tracing_integration.py
canonical/litmus-operators - tests/integration/helpers.py
canonical/pyroscope-operators - tests/integration/helpers.py
canonical/istio-beacon-k8s-operator - tests/integration/conftest.py
canonical/tempo-operators - tests/integration/helpers.py
canonical/sloth-k8s-operator - tests/integration/conftest.py
canonical/cos-coordinated-workers - tests/integration/conftest.py
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 3m 2s</sub>

### ✅ `github-mcp-server-get_file_contents`

**tests/integration/conftest.py**

<details>
<summary>Arguments</summary>

```json
{
  "owner": "canonical",
  "repo": "parca-k8s-operator",
  "path": "tests/integration/conftest.py"
}
```

</details>

<details>
<summary>22 lines</summary>

```
successfully downloaded text file (SHA: 760ee5909385c07f3cb4fc40476b52dd3cebdbc8)# Copyright 2021 Canonical Ltd.
# See LICENSE file for licensing details.

import logging
import os
from pathlib import Path

from pytest import fixture
from pytest_jubilant import get_resources, pack

logger= logging.getLogger("conftest")

@fixture(scope="module")
def parca_charm():
    """Parca charm used for integration testing."""
    if charm := os.getenv("CHARM_PATH"):
        logger.info("using parca charm from env")
        return charm
    elif Path(charm:="./parca-k8s_ubuntu@24.04-amd64.charm").exists():
        logger.info("using existing parca charm from ./")
        return charm
    logger.info("packing from ./")
    return pack("./")


@fixture(scope="module")
def parca_resources():
    return get_resources("./")
```

</details>


---

<sub>⏱️ 3m 2s</sub>

### ✅ `github-mcp-server-get_file_contents`

**tests/integration/conftest.py**

<details>
<summary>Arguments</summary>

```json
{
  "owner": "canonical",
  "repo": "sloth-k8s-operator",
  "path": "tests/integration/conftest.py"
}
```

</details>

<details>
<summary>22 lines</summary>

```
successfully downloaded text file (SHA: f1aced195d8d947e3b9e4d459ba053c1fc716238)# Copyright 2021 Canonical Ltd.
# See LICENSE file for licensing details.

import logging
import os
from pathlib import Path

from pytest import fixture
from pytest_jubilant import get_resources, pack

logger = logging.getLogger("conftest")


@fixture(scope="module")
def sloth_charm():
    """Sloth charm used for integration testing."""
    if charm := os.getenv("CHARM_PATH"):
        logger.info("using sloth charm from env")
        return charm
    elif Path(charm := "./sloth-k8s_ubuntu@24.04-amd64.charm").exists():
        logger.info("using existing sloth charm from ./")
        return charm
    logger.info("packing from ./")
    return pack("./")


@fixture(scope="module")
def sloth_resources():
    return get_resources("./")
```

</details>


---

<sub>⏱️ 3m 7s</sub>

### ✅ `github-mcp-server-search_code`

**pytest_jubilant juju.deploy juju.wait juju.integrate org:canonical language:python**

<details>
<summary>Arguments</summary>

```json
{
  "query": "pytest_jubilant juju.deploy juju.wait juju.integrate org:canonical language:python"
}
```

</details>

```
Output too large to read at once (29.0 KB). Saved to: /tmp/1772839639854-copilot-tool-output-a2iz7k.txt
Consider using tools like grep (for searching), head/tail (for viewing start/end), view with view_range (for specific sections), or jq (for JSON) to examine portions of the output.

Preview (first 500 chars):
{"total_count":6,"incomplete_results":false,"items":[{"name":"test_service_mesh.py","path":"tests/integration/test_service_mesh.py","sha":"459762affee6c360ad7e4514272e2c4a20889f03","html_url":"https://github.com/canonical/cos-coordinated-workers/blob/e781d7b21a091492cfa7a7f66ed91cf5c57874be/tests/integration/test_service_mesh.py","repository":{"id":979263067,"node_id":"R_kgDOOl5eWw","owner":{"login":"canonical","id":53057619,"node_id":"MDEyOk9yZ2FuaXphdGlvbjUzMDU3NjE5","avatar_url":"https://avat
```


---

<sub>⏱️ 3m 11s</sub>

### 💬 Copilot

Let me get a complete test file example:

---

<sub>⏱️ 3m 12s</sub>

### ✅ `github-mcp-server-get_file_contents`

**tests/integration**

<details>
<summary>Arguments</summary>

```json
{
  "owner": "canonical",
  "path": "tests/integration",
  "repo": "sloth-k8s-operator"
}
```

</details>

```
[{"type":"file","size":741,"name":"conftest.py","path":"tests/integration/conftest.py","sha":"f1aced195d8d947e3b9e4d459ba053c1fc716238","url":"https://api.github.com/repos/canonical/sloth-k8s-operator/contents/tests/integration/conftest.py?ref=a649a13084adf6245b2a60816ad08754a9323f0b","git_url":"https://api.github.com/repos/canonical/sloth-k8s-operator/git/blobs/f1aced195d8d947e3b9e4d459ba053c1fc716238","html_url":"https://github.com/canonical/sloth-k8s-operator/blob/a649a13084adf6245b2a60816ad08754a9323f0b/tests/integration/conftest.py","download_url":"https://raw.githubusercontent.com/canonical/sloth-k8s-operator/a649a13084adf6245b2a60816ad08754a9323f0b/tests/integration/conftest.py"},{"type":"file","size":1604,"name":"helpers.py","path":"tests/integration/helpers.py","sha":"568ae77daada1f945a582296256f15bbcdd35ca8","url":"https://api.github.com/repos/canonical/sloth-k8s-operator/contents/tests/integration/helpers.py?ref=a649a13084adf6245b2a60816ad08754a9323f0b","git_url":"https://api.github.com/repos/canonical/sloth-k8s-operator/git/blobs/568ae77daada1f945a582296256f15bbcdd35ca8","html_url":"https://github.com/canonical/sloth-k8s-operator/blob/a649a13084adf6245b2a60816ad08754a9323f0b/tests/integration/helpers.py","download_url":"https://raw.githubusercontent.com/canonical/sloth-k8s-operator/a649a13084adf6245b2a60816ad08754a9323f0b/tests/integration/helpers.py"},{"type":"file","size":349,"name":"test-slo-validation.feature","path":"tests/integration/test-slo-validation.feature","sha":"939e1adbeb1595441e3cc72dcd8189786192bf17","url":"https://api.github.com/repos/canonical/sloth-k8s-operator/contents/tests/integration/test-slo-validation.feature?ref=a649a13084adf6245b2a60816ad08754a9323f0b","git_url":"https://api.github.com/repos/canonical/sloth-k8s-operator/git/blobs/939e1adbeb1595441e3cc72dcd8189786192bf17","html_url":"https://github.com/canonical/sloth-k8s-operator/blob/a649a13084adf6245b2a60816ad08754a9323f0b/tests/integration/test-slo-validation.feature","download_url":"https://raw.githubusercontent.com/canonical/sloth-k8s-operator/a649a13084adf6245b2a60816ad08754a9323f0b/tests/integration/test-slo-validation.feature"},{"type":"file","size":966,"name":"test_basic.py","path":"tests/integration/test_basic.py","sha":"6f0c3e5b94c044e9b52b90b6706c29749411fcf0","url":"https://api.github.com/repos/canonical/sloth-k8s-operator/contents/tests/integration/test_basic.py?ref=a649a13084adf6245b2a60816ad08754a9323f0b","git_url":"https://api.github.com/repos/canonical/sloth-k8s-operator/git/blobs/6f0c3e5b94c044e9b52b90b6706c29749411fcf0","html_url":"https://github.com/canonical/sloth-k8s-operator/blob/a649a13084adf6245b2a60816ad08754a9323f0b/tests/integration/test_basic.py","download_url":"https://raw.githubusercontent.com/canonical/sloth-k8s-operator/a649a13084adf6245b2a60816ad08754a9323f0b/tests/integration/test_basic.py"},{"type":"file","size":9183,"name":"test_slo_to_rules.py","path":"tests/integration/test_slo_to_rules.py","sha":"42d25edc74eae63ea5d6702b1ff7ba21a5c27a1e","url":"https://api.github.com/repos/canonical/sloth-k8s-operator/contents/tests/integration/test_slo_to_rules.py?ref=a649a13084adf6245b2a60816ad08754a9323f0b","git_url":"https://api.github.com/repos/canonical/sloth-k8s-operator/git/blobs/42d25edc74eae63ea5d6702b1ff7ba21a5c27a1e","html_url":"https://github.com/canonical/sloth-k8s-operator/blob/a649a13084adf6245b2a60816ad08754a9323f0b/tests/integration/test_slo_to_rules.py","download_url":"https://raw.githubusercontent.com/canonical/sloth-k8s-operator/a649a13084adf6245b2a60816ad08754a9323f0b/tests/integration/test_slo_to_rules.py"},{"type":"file","size":3616,"name":"test_slo_validation.py","path":"tests/integration/test_slo_validation.py","sha":"f06d5da1822307523b5800fc50c937ebe6a6881d","url":"https://api.github.com/repos/canonical/sloth-k8s-operator/contents/tests/integration/test_slo_validation.py?ref=a649a13084adf6245b2a60816ad08754a9323f0b","git_url":"https://api.github.com/repos/canonical/sloth-k8s-operator/git/blobs/f06d5da1822307523b5800fc50c937ebe6a6881d","html_url":"https://github.com/canonical/sloth-k8s-operator/blob/a649a13084adf6245b2a60816ad08754a9323f0b/tests/integration/test_slo_validation.py","download_url":"https://raw.githubusercontent.com/canonical/sloth-k8s-operator/a649a13084adf6245b2a60816ad08754a9323f0b/tests/integration/test_slo_validation.py"}]
```


---

<sub>⏱️ 3m 17s</sub>

### ✅ `github-mcp-server-get_file_contents`

**tests/integration/test_basic.py**

<details>
<summary>Arguments</summary>

```json
{
  "owner": "canonical",
  "path": "tests/integration/test_basic.py",
  "repo": "sloth-k8s-operator"
}
```

</details>

<details>
<summary>34 lines</summary>

```
successfully downloaded text file (SHA: 6f0c3e5b94c044e9b52b90b6706c29749411fcf0)#!/usr/bin/env python3
# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

"""Basic integration test for Sloth charm."""

import jubilant
import pytest
from jubilant import Juju

from tests.integration.helpers import SLOTH

TIMEOUT = 600


@pytest.mark.setup
def test_setup(juju: Juju, sloth_charm, sloth_resources):
    """Deploy sloth."""
    juju.deploy(
        sloth_charm,
        SLOTH,
        resources=sloth_resources,
        trust=True,
    )

    juju.wait(
        lambda status: status.apps[SLOTH].is_active,
        error=jubilant.any_error,
        delay=10,
        successes=1,
        timeout=TIMEOUT,
    )


def test_sloth_is_running(juju: Juju):
    """Test that sloth is running and active."""
    status = juju.status()
    assert SLOTH in status.apps
    assert status.apps[SLOTH].is_active


@pytest.mark.teardown
def test_teardown(juju: Juju):
    """Clean up deployed charms."""
    juju.remove_application(SLOTH)
```

</details>


---

<sub>⏱️ 3m 17s</sub>

### ✅ `github-mcp-server-get_file_contents`

**pyproject.toml**

<details>
<summary>Arguments</summary>

```json
{
  "owner": "canonical",
  "path": "pyproject.toml",
  "repo": "sloth-k8s-operator"
}
```

</details>

<details>
<summary>76 lines</summary>

```
successfully downloaded text file (SHA: 4b89d29065325bee5f519739ab9c5af674496a2b)# Testing tools configuration
[project]
name = "sloth-k8s-operator"
version = "0.0.0"
requires-python = ">=3.12"

dependencies = [
    "ops[tracing]",
    "pydantic>=2,<3",
    "cosl",
    "charmlibs-interfaces-sloth",
    # ---PYDEPS---
    # lib/charms/tls_certificates_interface/v4/tls_certificates.py
    "cryptography",
    "lightkube>=0.19.1",
]

[project.optional-dependencies]
dev = [
    # ---UNIT TESTS---
    "coverage[toml]",
    "pytest",
    "ops[testing]",
    # ---INTEGRATION TESTS---
    "pydantic",
    "jubilant",
    "pytest-jubilant",
    "pytest-bdd",
    "tenacity",
    "minio",
    "requests",
    # ---LINTING---
    "ruff",
    "pyright",
]

[tool.coverage.run]
branch = true

[tool.coverage.report]
show_missing = true

[tool.pytest.ini_options]
minversion = "6.0"
log_cli_level = "INFO"
addopts = "--tb=native --verbose --capture=no --log-cli-level=INFO"
markers = [
    "setup: marks certain integration tests as setup tests (deselect with '-m \"not setup\"')",
    "teardown: marks certain integration tests as teardown tests",
]


# Linting tools configuration
[tool.ruff]
line-length = 99
extend-exclude = ["__pycache__", "*.egg_info"]

[tool.ruff.lint]
select = ["E", "W", "F", "C", "N", "D", "I001"]
ignore = ["E501", "D107"]
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
per-file-ignores = { "tests/*" = ["D100", "D101", "D102", "D103", "D104"] }

[tool.ruff.lint.mccabe]
max-complexity = 10

[tool.ruff.lint.pydocstyle]
convention = "google"

[tool.pyright]
extraPaths = ["src", "lib"]
pythonPlatform = "All"

[tool.codespell]
skip = ".git,.tox,build,venv*"
ignore-words-list = "assertIn"
```

</details>


---

<sub>⏱️ 4m 4s</sub>

### ✅ `web_fetch`

**https://documentation.ubuntu.com/jubilant/reference/jubilant/**

<details>
<summary>Arguments</summary>

```json
{
  "max_length": 20000,
  "url": "https://documentation.ubuntu.com/jubilant/reference/jubilant/"
}
```

</details>

<details>
<summary>324 lines</summary>

```
Contents of https://documentation.ubuntu.com/jubilant/reference/jubilant/:
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

Run the command on the remote target specified.

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
    
*  

<note>Content truncated. Call the fetch tool with a start_index of 20000 to get more content.</note>
```

</details>


---

<sub>⏱️ 5m 24s</sub>

### 💬 Copilot

Now I have a thorough understanding of both the current code and the jubilant API. Let me create a plan and implement the migration.

---

<sub>⏱️ 5m 24s</sub>

### ✅ `create`

**/home/ubuntu/.copilot/session-state/fdab7f7b-0354-435c-8576-821e4668485f/plan.md**

/home/ubuntu/.copilot/session-state/fdab7f7b-0354-435c-8576-821e4668485f/plan.md

```
Created file /home/ubuntu/.copilot/session-state/fdab7f7b-0354-435c-8576-821e4668485f/plan.md with 1235 characters
```


---

<sub>⏱️ 5m 53s</sub>

### 💬 Copilot

Now let me implement all the changes:

---

<sub>⏱️ 5m 53s</sub>

### ✅ `edit`

**/tmp/saml-integrator-L4-opus/tests/integration/conftest.py**

/tmp/saml-integrator-L4-opus/tests/integration/conftest.py

```
File /tmp/saml-integrator-L4-opus/tests/integration/conftest.py updated with changes.
```


---

<sub>⏱️ 5m 53s</sub>

### ✅ `edit`

**/tmp/saml-integrator-L4-opus/tests/integration/test_charm.py**

/tmp/saml-integrator-L4-opus/tests/integration/test_charm.py

```
File /tmp/saml-integrator-L4-opus/tests/integration/test_charm.py updated with changes.
```


---

<sub>⏱️ 6m 1s</sub>

### 💬 Copilot

Now update the dependencies:

---

<sub>⏱️ 6m 1s</sub>

### ✅ `edit`

**/tmp/saml-integrator-L4-opus/pyproject.toml**

/tmp/saml-integrator-L4-opus/pyproject.toml

```
File /tmp/saml-integrator-L4-opus/pyproject.toml updated with changes.
```


---

<sub>⏱️ 6m 1s</sub>

### ✅ `edit`

**/tmp/saml-integrator-L4-opus/pyproject.toml**

/tmp/saml-integrator-L4-opus/pyproject.toml

```
File /tmp/saml-integrator-L4-opus/pyproject.toml updated with changes.
```


---

<sub>⏱️ 6m 6s</sub>

### 💬 Copilot

Now let me verify the changes look correct and run linting:

---

<sub>⏱️ 6m 6s</sub>

### ✅ `view`

**/tmp/saml-integrator-L4-opus/tests/integration/conftest.py**

/tmp/saml-integrator-L4-opus/tests/integration/conftest.py

<details>
<summary>57 lines</summary>

```
1. # Copyright 2025 Canonical Ltd.
2. # See LICENSE file for licensing details.
3. 
4. """Fixtures for the SAML Integrator charm integration tests."""
5. 
6. import json
7. import logging
8. import os
9. from pathlib import Path
10. 
11. import jubilant
12. from pytest import fixture
13. from pytest_jubilant import pack
14. 
15. logger = logging.getLogger("conftest")
16. 
17. APP_NAME = "saml-integrator"
18. 
19. 
20. @fixture(scope="module", name="charm")
21. def charm_fixture():
22.     """Provide the path to the charm file."""
23.     if charm := os.getenv("CHARM_PATH"):
24.         logger.info("using charm from CHARM_PATH env var")
25.         return charm
26.     logger.info("packing charm from ./")
27.     return pack("./")
28. 
29. 
30. @fixture(scope="module", name="app")
31. def app_fixture(juju: jubilant.Juju, charm: str):
32.     """Deploy the SAML Integrator charm for integration testing."""
33.     juju.deploy(
34.         charm,
35.         APP_NAME,
36.     )
37.     yield APP_NAME
38. 
39. 
40. @fixture(scope="module", name="any_charm_app")
41. def any_charm_fixture(juju: jubilant.Juju):
42.     """Deploy the any-charm for testing SAML relations."""
43.     path_lib = "lib/charms/saml_integrator/v0/saml.py"
44.     saml_lib = Path(path_lib).read_text(encoding="utf8")
45.     any_charm_script = Path("tests/integration/any_charm.py").read_text(encoding="utf8")
46.     src_overwrite = {
47.         "saml.py": saml_lib,
48.         "any_charm.py": any_charm_script,
49.     }
50.     juju.deploy(
51.         "any-charm",
52.         "any",
53.         channel="beta",
54.         config={"python-packages": "pydantic>=2.12.5", "src-overwrite": json.dumps(src_overwrite)},
55.     )
56.     yield "any"
57.
```

</details>


---

<sub>⏱️ 6m 6s</sub>

### ✅ `view`

**/tmp/saml-integrator-L4-opus/tests/integration/test_charm.py**

/tmp/saml-integrator-L4-opus/tests/integration/test_charm.py

<details>
<summary>38 lines</summary>

```
1. #!/usr/bin/env python3
2. # Copyright 2025 Canonical Ltd.
3. # See LICENSE file for licensing details.
4. 
5. """SAML Integrator charm integration tests."""
6. 
7. import jubilant
8. 
9. 
10. SAML_CONFIG = {
11.     "entity_id": "https://login.staging.ubuntu.com",
12.     "fingerprint": "",
13.     "metadata_url": "https://login.staging.ubuntu.com/saml/metadata",
14. }
15. 
16. 
17. def test_active(juju: jubilant.Juju, app: str):
18.     """Check that the charm is active.
19. 
20.     Assume that the charm has already been built and is running.
21.     """
22.     juju.config(app, SAML_CONFIG)
23.     juju.wait(lambda status: jubilant.all_active(status, app), error=jubilant.any_error)
24.     status = juju.status()
25.     assert status.apps[app].is_active
26. 
27. 
28. def test_relation(juju: jubilant.Juju, app: str, any_charm_app: str):
29.     """Check that the charm is active once related to another charm.
30. 
31.     Assume that the charm has already been built and is running.
32.     """
33.     juju.integrate(f"{any_charm_app}:require-saml", f"{app}:saml")
34.     juju.config(app, SAML_CONFIG)
35.     juju.wait(lambda status: jubilant.all_active(status, app), error=jubilant.any_error)
36.     status = juju.status()
37.     assert status.apps[app].is_active
38.
```

</details>


---

<sub>⏱️ 6m 6s</sub>

### ✅ `view`

**/tmp/saml-integrator-L4-opus/pyproject.toml**

/tmp/saml-integrator-L4-opus/pyproject.toml (lines 25-67)

<details>
<summary>43 lines</summary>

```
25. [dependency-groups]
26. fmt = [
27.   "ruff",
28. ]
29. lint = [
30.   "codespell",
31.   "jubilant",
32.   "mypy",
33.   "ops-scenario",
34.   "pep8-naming",
35.   "pytest",
36.   "pytest-jubilant",
37.   "requests",
38.   "ruff",
39.   "types-mock",
40.   "types-pyyaml",
41.   "types-requests",
42. ]
43. unit = [
44.   "coverage[toml]",
45.   "pytest",
46. ]
47. coverage-report = [
48.   "coverage[toml]",
49.   "pytest",
50. ]
51. static = [
52.   "bandit[toml]",
53. ]
54. interface = [
55.   "ops-scenario",
56.   "pytest",
57.   "pytest-interface-tester",
58. ]
59. integration = [
60.   "allure-pytest>=2.8.18",
61.   "allure-pytest-collection-report @ git+https://github.com/canonical/data-platform-workflows@v24.0.0#subdirectory=python/pytest_plugins/allure_pytest_collection_report",
62.   "jubilant",
63.   "pytest",
64.   "pytest-jubilant",
65. ]
66. 
67. [tool.uv]
```

</details>


---

<sub>⏱️ 6m 12s</sub>

### 💬 Copilot

Good. Now let me run the linter to check for any issues:

---

<sub>⏱️ 6m 12s</sub>

### ✅ `bash`

**Run ruff linter on integration tests**

$ cd /tmp/saml-integrator-L4-opus && pip install ruff 2>&1 | tail -1 && ruff check tests/integration/ 2>&1

```
bash: pip: command not found
bash: ruff: command not found
<exited with exit code 127>
```


---

<sub>⏱️ 6m 16s</sub>

### ✅ `bash`

**Install and run ruff**

$ cd /tmp/saml-integrator-L4-opus && pip3 install ruff 2>&1 | tail -1 && python3 -m ruff check tests/integration/ 2>&1

```
bash: pip3: command not found
/usr/bin/python3: No module named ruff
<exited with exit code 1>
```


---

<sub>⏱️ 6m 21s</sub>

### ✅ `bash`

**Check available tooling**

$ which python3 && python3 --version && which uv 2>/dev/null || which uvx 2>/dev/null || (curl -LsSf https://astral.sh/uv/install.sh | sh 2>&1 | tail -3)

```
/usr/bin/python3
Python 3.12.3
/snap/bin/uv
<exited with exit code 0>
```


---

<sub>⏱️ 6m 25s</sub>

### ✅ `bash`

**Run ruff via uv**

$ cd /tmp/saml-integrator-L4-opus && uv run ruff check tests/integration/ 2>&1

<details>
<summary>6 lines</summary>

```
Using CPython 3.12.3 interpreter at: /usr/bin/python3
Creating virtual environment at: .venv
⠋ Resolving dependencies...                                                                                             ⠙ Resolving dependencies...                                                                                             ⠋ Resolving dependencies...                                                                                             ⠙ Resolving dependencies...                                                                                             ⠋ Resolving dependencies...                                                                                             ⠙ Resolving dependencies...                                                                                             ⠙ saml-integrator-operator==0.0.0                                                                                       ⠙ saml-integrator-operator==0.0.0                                                                                       ⠙ saml-integrator-operator==0.0.0                                                                                       ⠙ saml-integrator-operator==0.0.0                                                                                       ⠙ saml-integrator-operator==0.0.0                                                                                       ⠙ saml-integrator-operator==0.0.0                                                                                       ⠙ saml-integrator-operator==0.0.0                                                                                       ⠙ saml-integrator-operator==0.0.0                                                                                       ⠙ allure-pytest-collection-report==0.1.0                                                                                ⠙ lxml==6.0.2                                                                                                           ⠙ ops==3.6.0                                                                                                            ⠙ pydantic==2.12.5                                                                                                      ⠙ signxml==4.3.0                                                                                                        ⠙ pydantic-core==2.41.5                                                                                                 ⠙ coverage==7.12.0                                                                                                      ⠙ coverage==7.12.0                                                                                                      ⠙ pytest==9.0.1                                                                                                         ⠙ ruff==0.14.6                                                                                                          ⠙ allure-pytest==2.15.0                                                                                                 ⠙ click==8.3.1                                                                                                          ░░░░░░░░░░░░░░░░░░░░ [0/0] Installing wheels...                                                                         ░░░░░░░░░░░░░░░░░░░░ [0/17] Installing wheels...                                                                        ░░░░░░░░░░░░░░░░░░░░ [0/17] pydantic-core==2.41.5                                                                       █░░░░░░░░░░░░░░░░░░░ [1/17] pydantic-core==2.41.5                                                                       █░░░░░░░░░░░░░░░░░░░ [1/17] ops==3.6.0                                                                                  ██░░░░░░░░░░░░░░░░░░ [2/17] ops==3.6.0                                                                                  ██░░░░░░░░░░░░░░░░░░ [2/17] typing-extensions==4.15.0                                                                   ███░░░░░░░░░░░░░░░░░ [3/17] typing-extensions==4.15.0                                                                   ███░░░░░░░░░░░░░░░░░ [3/17] typing-inspection==0.4.2                                                                    ████░░░░░░░░░░░░░░░░ [4/17] typing-inspection==0.4.2                                                                    ████░░░░░░░░░░░░░░░░ [4/17] certifi==2025.11.12                                                                         █████░░░░░░░░░░░░░░░ [5/17] certifi==2025.11.12                                                                         █████░░░░░░░░░░░░░░░ [5/17] cffi==2.0.0                                                                                 ███████░░░░░░░░░░░░░ [6/17] cffi==2.0.0                                                                                 ███████░░░░░░░░░░░░░ [6/17] opentelemetry-api==1.38.0                                                                   ████████░░░░░░░░░░░░ [7/17] opentelemetry-api==1.38.0                                                                   ████████░░░░░░░░░░░░ [7/17] pyyaml==6.0.3                                                                               █████████░░░░░░░░░░░ [8/17] pyyaml==6.0.3                                                                               █████████░░░░░░░░░░░ [8/17] cryptography==46.0.3                                                                        ██████████░░░░░░░░░░ [9/17] cryptography==46.0.3                                                                        Installed 17 packages in 2ms
error: Failed to spawn: `ruff`
  Caused by: No such file or directory (os error 2)
<exited with exit code 2>
```

</details>


---

<sub>⏱️ 6m 30s</sub>

### ✅ `bash`

**Sync lint deps and run ruff**

$ cd /tmp/saml-integrator-L4-opus && uv sync --group lint 2>&1 | tail -5 && uv run ruff check tests/integration/ 2>&1

<details>
<summary>18 lines</summary>

```
+ ruff==0.14.6
 + types-mock==5.2.0.20250924
 + types-pyyaml==6.0.12.20250915
 + types-requests==2.32.4.20250913
 + urllib3==2.5.0
warning: Selection `CPY` has no effect because preview is not enabled.
I001 [*] Import block is un-sorted or un-formatted
 --> tests/integration/test_charm.py:7:1
  |
5 | """SAML Integrator charm integration tests."""
6 |
7 | import jubilant
  | ^^^^^^^^^^^^^^^
  |
help: Organize imports

Found 1 error.
[*] 1 fixable with the `--fix` option.
<exited with exit code 1>
```

</details>


---

<sub>⏱️ 6m 35s</sub>

### ✅ `bash`

**Fix ruff issues**

$ cd /tmp/saml-integrator-L4-opus && uv run ruff check --fix tests/integration/ 2>&1 && uv run ruff format tests/integration/ 2>&1

```
warning: Selection `CPY` has no effect because preview is not enabled.
Found 1 error (1 fixed, 0 remaining).
warning: Selection `CPY` has no effect because preview is not enabled.
4 files left unchanged
<exited with exit code 0>
```


---

<sub>⏱️ 6m 39s</sub>

### ✅ `bash`

**Verify ruff passes**

$ cd /tmp/saml-integrator-L4-opus && uv run ruff check tests/integration/ 2>&1

```
warning: Selection `CPY` has no effect because preview is not enabled.
All checks passed!
<exited with exit code 0>
```


---

<sub>⏱️ 6m 43s</sub>

### 💬 Copilot

Let me verify the fixed file looks right:

---

<sub>⏱️ 6m 43s</sub>

### ✅ `view`

**/tmp/saml-integrator-L4-opus/tests/integration/test_charm.py**

/tmp/saml-integrator-L4-opus/tests/integration/test_charm.py

<details>
<summary>37 lines</summary>

```
1. #!/usr/bin/env python3
2. # Copyright 2025 Canonical Ltd.
3. # See LICENSE file for licensing details.
4. 
5. """SAML Integrator charm integration tests."""
6. 
7. import jubilant
8. 
9. SAML_CONFIG = {
10.     "entity_id": "https://login.staging.ubuntu.com",
11.     "fingerprint": "",
12.     "metadata_url": "https://login.staging.ubuntu.com/saml/metadata",
13. }
14. 
15. 
16. def test_active(juju: jubilant.Juju, app: str):
17.     """Check that the charm is active.
18. 
19.     Assume that the charm has already been built and is running.
20.     """
21.     juju.config(app, SAML_CONFIG)
22.     juju.wait(lambda status: jubilant.all_active(status, app), error=jubilant.any_error)
23.     status = juju.status()
24.     assert status.apps[app].is_active
25. 
26. 
27. def test_relation(juju: jubilant.Juju, app: str, any_charm_app: str):
28.     """Check that the charm is active once related to another charm.
29. 
30.     Assume that the charm has already been built and is running.
31.     """
32.     juju.integrate(f"{any_charm_app}:require-saml", f"{app}:saml")
33.     juju.config(app, SAML_CONFIG)
34.     juju.wait(lambda status: jubilant.all_active(status, app), error=jubilant.any_error)
35.     status = juju.status()
36.     assert status.apps[app].is_active
37.
```

</details>


---

<sub>⏱️ 6m 48s</sub>

### 💬 Copilot

Good - ruff just removed the blank line after the import. Now let me also run mypy on the integration tests and check the full lint suite:

---

<sub>⏱️ 6m 48s</sub>

### ✅ `bash`

**Run full ruff check**

$ cd /tmp/saml-integrator-L4-opus && uv run ruff check src/ tests/ lib/charms/saml_integrator 2>&1

```
warning: Selection `CPY` has no effect because preview is not enabled.
All checks passed!
<exited with exit code 0>
```


---

<sub>⏱️ 6m 52s</sub>

### 💬 Copilot

Now let me also regenerate the `uv.lock` since the dependencies changed:

---

<sub>⏱️ 6m 52s</sub>

### ✅ `bash`

**Regenerate uv.lock**

$ cd /tmp/saml-integrator-L4-opus && uv lock 2>&1 | tail -5

```
Resolved 59 packages in 0.58ms
<exited with exit code 0>
```


---

<sub>⏱️ 6m 59s</sub>

### 💬 Copilot

Now let me verify there are no remaining references to the old libraries:

---

<sub>⏱️ 6m 59s</sub>

### ✅ `grep`

**/tmp/saml-integrator-L4-opus/tests**

"pytest.operator|pytest_operator|pytest.asyncio|pytest_asyncio|python.libjuju|ops_test|OpsTest|abort_on_fail" (/tmp/saml-integrator-L4-opus/tests)

```
No matches found.
```


---

<sub>⏱️ 6m 59s</sub>

### ✅ `grep`

**/tmp/saml-integrator-L4-opus/pyproject.toml**

"pytest-operator|pytest-asyncio|\"juju\"" (/tmp/saml-integrator-L4-opus/pyproject.toml)

```
No matches found.
```


---

<sub>⏱️ 7m 3s</sub>

### 💬 Copilot

No old references remain. Let me do a final review of all changed files and commit:

---

<sub>⏱️ 7m 4s</sub>

### ✅ `bash`

**Review all changes**

$ cd /tmp/saml-integrator-L4-opus && git --no-pager diff --stat && echo "---" && git --no-pager diff

<details>
<summary>7 lines</summary>

```
Output too large to read at once (132.3 KB). Saved to: /tmp/copilot-tool-output-1772839876730-p7j0rl.txt
Consider using tools like grep (for searching), head/tail (for viewing start/end), view with view_range (for specific sections), or jq (for JSON) to examine portions of the output.

Preview (first 500 chars):
 pyproject.toml                  |   9 +-
 tests/integration/conftest.py   |  59 +++---
 tests/integ
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 7m 8s</sub>

### ✅ `bash`

**Review code changes only**

$ cd /tmp/saml-integrator-L4-opus && git --no-pager diff -- pyproject.toml tests/integration/conftest.py tests/integration/test_charm.py

<details>
<summary>177 lines</summary>

```diff
diff --git a/pyproject.toml b/pyproject.toml
index 59170c2..92dce70 100644
--- a/pyproject.toml
+++ b/pyproject.toml
@@ -28,12 +28,12 @@ fmt = [
 ]
 lint = [
   "codespell",
+  "jubilant",
   "mypy",
   "ops-scenario",
   "pep8-naming",
   "pytest",
-  "pytest-asyncio",
-  "pytest-operator",
+  "pytest-jubilant",
   "requests",
   "ruff",
   "types-mock",
@@ -59,10 +59,9 @@ interface = [
 integration = [
   "allure-pytest>=2.8.18",
   "allure-pytest-collection-report @ git+https://github.com/canonical/data-platform-workflows@v24.0.0#subdirectory=python/pytest_plugins/allure_pytest_collection_report",
-  "juju",
+  "jubilant",
   "pytest",
-  "pytest-asyncio",
-  "pytest-operator",
+  "pytest-jubilant",
 ]
 
 [tool.uv]
diff --git a/tests/integration/conftest.py b/tests/integration/conftest.py
index e933368..abdac82 100644
--- a/tests/integration/conftest.py
+++ b/tests/integration/conftest.py
@@ -4,42 +4,42 @@
 """Fixtures for the SAML Integrator charm integration tests."""
 
 import json
+import logging
+import os
 from pathlib import Path
 
-import pytest_asyncio
-import yaml
-from pytest import Config, fixture
-from pytest_operator.plugin import OpsTest
+import jubilant
+from pytest import fixture
+from pytest_jubilant import pack
 
+logger = logging.getLogger("conftest")
 
-@fixture(scope="module", name="app_name")
-def app_name_fixture():
-    """Provide app name from the metadata."""
-    metadata = yaml.safe_load(Path("./metadata.yaml").read_text("utf-8"))
-    yield metadata["name"]
+APP_NAME = "saml-integrator"
 
 
-@pytest_asyncio.fixture(scope="module")
-async def app(ops_test: OpsTest, pytestconfig: Config, app_name: str):
-    """SAML Integrator charm used for integration testing.
+@fixture(scope="module", name="charm")
+def charm_fixture():
+    """Provide the path to the charm file."""
+    if charm := os.getenv("CHARM_PATH"):
+        logger.info("using charm from CHARM_PATH env var")
+        return charm
+    logger.info("packing charm from ./")
+    return pack("./")
 
-    Build the charm and deploy it along with Anycharm.
-    """
-    charm = pytestconfig.getoption("--charm-file")
-    assert ops_test.model
-    application = await ops_test.model.deploy(
-        f"./{charm}",
-        application_name=app_name,
-    )
-    yield application
 
+@fixture(scope="module", name="app")
+def app_fixture(juju: jubilant.Juju, charm: str):
+    """Deploy the SAML Integrator charm for integration testing."""
+    juju.deploy(
+        charm,
+        APP_NAME,
+    )
+    yield APP_NAME
 
-@pytest_asyncio.fixture(scope="module")
-async def any_charm(ops_test: OpsTest):
-    """SAML Integrator charm used for integration testing.
 
-    Build the charm and deploy it along with Anycharm.
-    """
+@fixture(scope="module", name="any_charm_app")
+def any_charm_fixture(juju: jubilant.Juju):
+    """Deploy the any-charm for testing SAML relations."""
     path_lib = "lib/charms/saml_integrator/v0/saml.py"
     saml_lib = Path(path_lib).read_text(encoding="utf8")
     any_charm_script = Path("tests/integration/any_charm.py").read_text(encoding="utf8")
@@ -47,11 +47,10 @@ async def any_charm(ops_test: OpsTest):
         "saml.py": saml_lib,
         "any_charm.py": any_charm_script,
     }
-    assert ops_test.model
-    application = await ops_test.model.deploy(
+    juju.deploy(
         "any-charm",
-        application_name="any",
+        "any",
         channel="beta",
         config={"python-packages": "pydantic>=2.12.5", "src-overwrite": json.dumps(src_overwrite)},
     )
-    yield application
+    yield "any"
diff --git a/tests/integration/test_charm.py b/tests/integration/test_charm.py
index de64441..25628da 100644
--- a/tests/integration/test_charm.py
+++ b/tests/integration/test_charm.py
@@ -4,48 +4,33 @@
 
 """SAML Integrator charm integration tests."""
 
-import ops
-import pytest
-from pytest_operator.plugin import OpsTest
+import jubilant
 
+SAML_CONFIG = {
+    "entity_id": "https://login.staging.ubuntu.com",
+    "fingerprint": "",
+    "metadata_url": "https://login.staging.ubuntu.com/saml/metadata",
+}
 
-@pytest.mark.asyncio
-@pytest.mark.abort_on_fail
-async def test_active(ops_test: OpsTest, app: ops.Application):
+
+def test_active(juju: jubilant.Juju, app: str):
     """Check that the charm is active.
 
     Assume that the charm has already been built and is running.
     """
-    await app.set_config(  # type: ignore[attr-defined]
-        {
-            "entity_id": "https://login.staging.ubuntu.com",
-            "fingerprint": "",
-            "metadata_url": "https://login.staging.ubuntu.com/saml/metadata",
-        }
-    )
-    status_name = ops.ActiveStatus.name  # type: ignore[has-type]
-    assert ops_test.model
-    await ops_test.model.wait_for_idle(status=status_name, raise_on_error=True)
-    assert app.units[0].workload_status == status_name  # type: ignore
-
-
-@pytest.mark.asyncio
-@pytest.mark.abort_on_fail
-async def test_relation(ops_test: OpsTest, app: ops.Application, any_charm: ops.Application):
+    juju.config(app, SAML_CONFIG)
+    juju.wait(lambda status: jubilant.all_active(status, app), error=jubilant.any_error)
+    status = juju.status()
+    assert status.apps[app].is_active
+
+
+def test_relation(juju: jubilant.Juju, app: str, any_charm_app: str):
     """Check that the charm is active once related to another charm.
 
     Assume that the charm has already been built and is running.
     """
-    relation_name = f"{app.name}:saml"
-    assert ops_test.model
-    await ops_test.model.add_relation(f"{any_charm.name}:require-saml", relation_name)
-    await app.set_config(  # type: ignore[attr-defined]
-        {
-            "entity_id": "https://login.staging.ubuntu.com",
-            "fingerprint": "",
-            "metadata_url": "https://login.staging.ubuntu.com/saml/metadata",
-        }
-    )
-    status_name = ops.ActiveStatus.name  # type: ignore[has-type]
-    await ops_test.model.wait_for_idle(status=status_name, raise_on_error=True)
-    assert app.units[0].workload_status == status_name  # type: ignore
+    juju.integrate(f"{any_charm_app}:require-saml", f"{app}:saml")
+    juju.config(app, SAML_CONFIG)
+    juju.wait(lambda status: jubilant.all_active(status, app), error=jubilant.any_error)
+    status = juju.status()
+    assert status.apps[app].is_active
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 7m 18s</sub>

### 💬 Copilot

Everything looks clean. Let me commit:

---

<sub>⏱️ 7m 19s</sub>

### ✅ `bash`

**Commit changes**

$ cd /tmp/saml-integrator-L4-opus && git add pyproject.toml uv.lock tests/integration/conftest.py tests/integration/test_charm.py && git commit -m "Migrate integration tests from pytest-operator to jubilant

Replace pytest-operator (python-libjuju) with jubilant and pytest-jubilant
for integration testing:

- conftest.py: Use synchronous fixtures with jubilant.Juju, pack() from
  pytest-jubilant for charm building, CHARM_PATH env var support
- test_charm.py: Remove async/await, use juju.config(), juju.wait(),
  juju.integrate(), and jubilant.all_active/any_error helpers
- pyproject.toml: Replace juju, pytest-asyncio, pytest-operator deps with
  jubilant and pytest-jubilant in both lint and integration groups
- uv.lock: Regenerated for new dependencies

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>" 2>&1

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

<sub>⏱️ 7m 25s</sub>

### ✅ `bash`

**Commit with identity configured**

$ cd /tmp/saml-integrator-L4-opus && git config user.email "copilot@github.com" && git config user.name "Copilot" && git commit -m "Migrate integration tests from pytest-operator to jubilant

Replace pytest-operator (python-libjuju) with jubilant and pytest-jubilant
for integration testing:

- conftest.py: Use synchronous fixtures with jubilant.Juju, pack() from
  pytest-jubilant for charm building, CHARM_PATH env var support
- test_charm.py: Remove async/await, use juju.config(), juju.wait(),
  juju.integrate(), and jubilant.all_active/any_error helpers
- pyproject.toml: Replace juju, pytest-asyncio, pytest-operator deps with
  jubilant and pytest-jubilant in both lint and integration groups
- uv.lock: Regenerated for new dependencies

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>" 2>&1

```
[main 444fc72] Migrate integration tests from pytest-operator to jubilant
 4 files changed, 70 insertions(+), 878 deletions(-)
<exited with exit code 0>
```


---

<sub>⏱️ 7m 29s</sub>

### 💬 Copilot

Let me clean up the reference repo:

---

<sub>⏱️ 7m 29s</sub>

### ✅ `bash`

**Clean up reference repo**

$ rm -rf /tmp/wordpress-k8s-ref

```

<exited with exit code 0>
```


---

<sub>⏱️ 7m 37s</sub>

### 💬 Copilot

Migration complete. Here's what changed:

- **`tests/integration/conftest.py`**: Replaced async `pytest_asyncio`/`OpsTest` fixtures with synchronous ones using `jubilant.Juju`. Uses `pack()` from `pytest-jubilant` for charm building (with `CHARM_PATH` env var fallback). The `juju` fixture is provided automatically by `pytest-jubilant`.

- **`tests/integration/test_charm.py`**: Removed all `async`/`await`, `@pytest.mark.asyncio`, and `ops`/`pytest-operator` imports. Uses `juju.config()`, `juju.wait(jubilant.all_active, error=jubilant.any_error)`, and `juju.integrate()`.

- **`pyproject.toml`** + **`uv.lock`**: Replaced `juju`, `pytest-asyncio`, `pytest-operator` with `jubilant` and `pytest-jubilant` in both `lint` and `integration` dependency groups.

---

<sub>Generated by [GitHub Copilot CLI](https://github.com/features/copilot/cli)</sub>
