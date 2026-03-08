# 🤖 Copilot CLI Session

> **Session ID:** `ec2c300e-abfb-4413-af2b-65c388e8518a`
> **Duration:** 9m 31s

<sub>⏱️ 5s</sub>

### 👤 User

Migrate this charm's integration tests from pytest-operator (python-libjuju) to jubilant and pytest-jubilant. Update all test files, conftest.py, helpers, and dependencies.

Before starting, install jubilant and pytest-jubilant from PyPI (pip install jubilant pytest-jubilant) and read the source code to understand the API. The key modules are the Juju class, wait helpers (all_active, all_blocked, any_error), and the pytest-jubilant fixtures (pack, get_resources, juju fixture, temp_model_factory).

---

<sub>⏱️ 13s</sub>

### ✅ `bash`

**Install jubilant and pytest-jubilant**

$ cd /tmp/indico-L3-source-sonnet-4.6 && pip install jubilant pytest-jubilant 2>&1 | tail -5

```
See /usr/share/doc/python3.12/README.venv for more information.

note: If you believe this is a mistake, please contact your Python installation or OS distribution provider. You can override this, at the risk of breaking your Python installation or OS, by passing --break-system-packages.
hint: See PEP 668 for the detailed specification.
<exited with exit code 0>
```


---

<sub>⏱️ 12s</sub>

### ✅ `view`

**/tmp/indico-L3-source-sonnet-4.6/tests/integration**

/tmp/indico-L3-source-sonnet-4.6/tests/integration

<details>
<summary>7 lines</summary>

```
__init__.py
conftest.py
test_actions.py
test_charm.py
test_loki.py
test_s3.py
test_saml.py
```

</details>


---

<sub>⏱️ 18s</sub>

### ✅ `bash`

**Install packages with break-system-packages**

$ pip install jubilant pytest-jubilant --break-system-packages 2>&1 | tail -10

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

<sub>⏱️ 17s</sub>

### ✅ `bash`

**Read conftest.py**

$ cat /tmp/indico-L3-source-sonnet-4.6/tests/integration/conftest.py

<details>
<summary>166 lines</summary>

```
# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

"""Fixtures for Indico charm integration tests."""

import asyncio
from pathlib import Path
from secrets import token_hex

import pytest_asyncio
import yaml
from ops import Application
from pytest import Config, fixture
from pytest_operator.plugin import OpsTest


@fixture(scope="module", name="external_url")
def external_url_fixture():
    """Provides the external URL for Indico."""
    return "https://events.staging.canonical.com"


@fixture(scope="module")
def saml_email(pytestconfig: Config):
    """SAML login email address test argument for SAML integration tests"""
    email = pytestconfig.getoption("--saml-email")
    if not email:
        raise ValueError("--saml-email argument is required for selected test cases")
    return email


@fixture(scope="module")
def saml_password(pytestconfig: Config):
    """SAML login password test argument for SAML integration tests"""
    password = pytestconfig.getoption("--saml-password")
    if not password:
        raise ValueError("--saml-password argument is required for selected test cases")
    return password


@fixture(scope="module", name="metadata")
def metadata_fixture():
    """Provides charm metadata."""
    yield yaml.safe_load(Path("./metadata.yaml").read_text("utf-8"))


@fixture(scope="module", name="app_name")
def app_name_fixture(metadata):
    """Provides app name from the metadata."""
    yield metadata["name"]


@fixture(scope="module")
def requests_timeout():
    """Provides a global default timeout for HTTP requests"""
    yield 15


@pytest_asyncio.fixture(scope="module", name="app")
async def app_fixture(
    ops_test: OpsTest,
    app_name: str,
    pytestconfig: Config,
):
    """Indico charm used for integration testing.

    Builds the charm and deploys it and the relations it depends on.
    """
    assert ops_test.model
    # Deploy relations to speed up overall execution
    postgresql_config = {
        "plugin_pg_trgm_enable": str(True),
        "plugin_unaccent_enable": str(True),
        "profile": "testing",
    }
    await asyncio.gather(
        ops_test.model.deploy(
            "postgresql-k8s", channel="14/edge", config=postgresql_config, trust=True
        ),
        ops_test.model.deploy("redis-k8s", "redis-broker", channel="latest/edge"),
        ops_test.model.deploy("redis-k8s", "redis-cache", channel="latest/edge"),
        ops_test.model.deploy(
            "nginx-ingress-integrator",
            channel="latest/edge",
            revision=133,
            trust=True,
            series="focal",
        ),
    )
    resources = {
        "indico-image": pytestconfig.getoption("--indico-image"),
        "indico-nginx-image": pytestconfig.getoption("--indico-nginx-image"),
    }

    if charm := pytestconfig.getoption("--charm-file"):
        application = await ops_test.model.deploy(
            f"./{charm}",
            resources=resources,
            application_name=app_name,
            series="focal",
        )
    else:
        charm = await ops_test.build_charm(".")
        application = await ops_test.model.deploy(
            charm,
            resources=resources,
            application_name=app_name,
            config={
                "external_plugins": "https://github.com/canonical/flask-multipass-saml-groups/releases/download/1.2.2/flask_multipass_saml_groups-1.2.2-py3-none-any.whl"  # noqa: E501 pylint: disable=line-too-long
            },
            series="focal",
        )

    await asyncio.gather(
        ops_test.model.add_relation(app_name, "postgresql-k8s"),
        ops_test.model.add_relation(f"{app_name}:redis-broker", "redis-broker"),
        ops_test.model.add_relation(f"{app_name}:redis-cache", "redis-cache"),
        ops_test.model.add_relation(app_name, "nginx-ingress-integrator"),
    )
    await ops_test.model.wait_for_idle(
        apps=[
            application.name,
            "postgresql-k8s",
            "redis-broker",
            "redis-cache",
            "nginx-ingress-integrator",
        ],
        status="active",
        raise_on_error=True,
    )
    yield application


@pytest_asyncio.fixture(scope="module", name="saml_integrator")
async def saml_integrator_fixture(ops_test: OpsTest, app: Application):
    """SAML integrator charm used for integration testing."""
    assert ops_test.model
    saml_config = {
        "entity_id": "https://login.staging.ubuntu.com",
        "metadata_url": "https://login.staging.ubuntu.com/saml/metadata",
    }
    saml_integrator = await ops_test.model.deploy(
        "saml-integrator", channel="latest/stable", config=saml_config, trust=True
    )
    await ops_test.model.add_relation(app.name, saml_integrator.name)
    await ops_test.model.wait_for_idle(
        apps=[saml_integrator.name, app.name], status="active", raise_on_error=True
    )
    yield saml_integrator


@pytest_asyncio.fixture(scope="module", name="s3_integrator")
async def s3_integrator_fixture(ops_test: OpsTest, app: Application):
    """SAML integrator charm used for integration testing."""
    assert ops_test.model
    s3_config = {
        "bucket": "some-bucket",
        "endpoint": "s3.example.com",
    }
    s3_integrator = await ops_test.model.deploy(
        "s3-integrator", channel="latest/edge", config=s3_config
    )
    await ops_test.model.wait_for_idle(apps=[s3_integrator.name], idle_period=5, status="blocked")
    params = {"access-key": token_hex(16), "secret-key": token_hex(16)}
    # Application actually does have units
    action_sync_s3_credentials = await s3_integrator.units[0].run_action(  # type: ignore
        "sync-s3-credentials", **params
    )
    await action_sync_s3_credentials.wait()
    await ops_test.model.wait_for_idle(
        apps=[s3_integrator.name], status="active", raise_on_error=True
    )
    await ops_test.model.add_relation(app.name, s3_integrator.name)
    await ops_test.model.wait_for_idle(
        apps=[s3_integrator.name, app.name], status="active", raise_on_error=True
    )
    yield s3_integrator


@pytest_asyncio.fixture(scope="module", name="loki")
async def loki_fixture(ops_test: OpsTest, app: Application):
    """Loki charm used for integration testing."""
    assert ops_test.model
    loki = await ops_test.model.deploy(
        "loki-k8s", channel="1/edge", trust=True, revision=97, series="focal"
    )
    await ops_test.model.add_relation(app.name, loki.name)
    await ops_test.model.wait_for_idle(
        apps=[loki.name, app.name], status="active", raise_on_error=True
    )
    yield loki
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 23s</sub>

### ✅ `bash`

**Read test_charm.py and test_actions.py**

$ cat /tmp/indico-L3-source-sonnet-4.6/tests/integration/test_charm.py && echo "---FILE_SEPARATOR---" && cat /tmp/indico-L3-source-sonnet-4.6/tests/integration/test_actions.py

<details>
<summary>165 lines</summary>

```
#!/usr/bin/env python3
# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

"""Indico charm integration tests."""

import logging

import pytest
import requests
from ops import ActiveStatus, Application
from pytest_operator.plugin import OpsTest

from charm import CELERY_PROMEXP_PORT, NGINX_PROMEXP_PORT, STATSD_PROMEXP_PORT

ADMIN_USER_EMAIL = "sample@email.com"
ADMIN_USER_EMAIL_FAIL = "sample2@email.com"

logger = logging.getLogger()


@pytest.mark.asyncio
@pytest.mark.abort_on_fail
async def test_active(app: Application):
    """Check that the charm is active.

    Assume that the charm has already been built and is running.
    """
    # Application actually does have units
    assert app.units[0].workload_status == ActiveStatus.name  # type: ignore


@pytest.mark.asyncio
@pytest.mark.abort_on_fail
async def test_indico_is_up(ops_test: OpsTest, app: Application):
    """Check that the bootstrap page is reachable.

    Assume that the charm has already been built and is running.
    """
    assert ops_test.model
    # Read the IP address of indico
    status = await ops_test.model.get_status()
    unit = list(status.applications[app.name].units)[0]
    address = status["applications"][app.name]["units"][unit]["address"]
    # Send request to bootstrap page and set Host header to app_name (which the application
    # expects)
    response = requests.get(
        f"http://{address}:8080/bootstrap", headers={"Host": f"{app.name}.local"}, timeout=10
    )
    assert response.status_code == 200


@pytest.mark.asyncio
@pytest.mark.abort_on_fail
async def test_health_checks(app: Application):
    """Runs health checks for each container.

    Assume that the charm has already been built and is running.
    """
    container__checks_list = [("indico-nginx", 2), ("indico", 4)]
    # Application actually does have units
    indico_unit = app.units[0]  # type: ignore
    for container_checks in container__checks_list:
        container = container_checks[0]
        cmd = f"PEBBLE_SOCKET=/charm/containers/{container}/pebble.socket /charm/bin/pebble checks"
        action = await indico_unit.run(cmd, timeout=10)
        # Change this if upgrading Juju lib version to >= 3
        # See https://github.com/juju/python-libjuju/issues/707#issuecomment-1212296289
        result = action.data
        code = result["results"].get("Code")
        stdout = result["results"].get("Stdout")
        stderr = result["results"].get("Stderr")
        assert code == "0", f"{cmd} failed ({code}): {stderr or stdout}"
        # When executing the checks, `0/3` means there are 0 errors of 3.
        # Each check has it's own `0/3`, so we will count `n` times,
        # where `n` is the number of checks for that container.
        assert stdout.count("0/3") == container_checks[1]


@pytest.mark.asyncio
@pytest.mark.abort_on_fail
async def test_prom_exporters_are_up(app: Application):
    """
    arrange: given charm in its initial state
    act: when the metrics endpoints are scraped
    assert: the response is 200 (HTTP OK)
    """
    # Application actually does have units
    indico_unit = app.units[0]  # type: ignore
    prometheus_targets = [
        f"localhost:{NGINX_PROMEXP_PORT}",
        f"localhost:{STATSD_PROMEXP_PORT}",
        f"localhost:{CELERY_PROMEXP_PORT}",
    ]
    # Send request to /metrics for each target and check the response
    for target in prometheus_targets:
        cmd = f"curl -m 10 http://{target}/metrics"
        action = await indico_unit.run(cmd, timeout=15)
        # Change this if upgrading Juju lib version to >= 3
        # See https://github.com/juju/python-libjuju/issues/707#issuecomment-1212296289
        result = action.data
        code = result["results"].get("Code")
        stdout = result["results"].get("Stdout")
        stderr = result["results"].get("Stderr")
        assert code == "0", f"{cmd} failed ({code}): {stderr or stdout}"
---FILE_SEPARATOR---
#!/usr/bin/env python3
# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

"""Indico charm actions integration tests."""

from secrets import token_hex

import juju.action
import pytest
import pytest_asyncio
from ops import Application

ADMIN_USER_EMAIL = "sample@email.com"
ADMIN_USER_EMAIL_FAIL = "sample2@email.com"


@pytest_asyncio.fixture(scope="module")
async def add_admin(app: Application):
    """
    arrange: given charm in its initial state
    act: run the add-admin action
    assert: check the output in the action result
    """
    assert hasattr(app, "units")

    assert app.units[0]

    email = ADMIN_USER_EMAIL
    email_fail = ADMIN_USER_EMAIL_FAIL
    # This is a test password
    password = token_hex(16)

    # Application actually does have units
    action: juju.action.Action = await app.units[0].run_action(  # type: ignore
        "add-admin", email=email, password=password
    )
    await action.wait()
    assert action.status == "completed"
    assert action.results["user"] == email
    assert f'Admin with email "{email}" correctly created' in action.results["output"]
    action2: juju.action.Action = await app.units[0].run_action(  # type: ignore
        "add-admin", email=email_fail, password=password
    )
    await action2.wait()
    assert action2.status == "completed"
    assert action2.results["user"] == email_fail
    assert f'Admin with email "{email_fail}" correctly created' in action2.results["output"]


@pytest.mark.asyncio
@pytest.mark.abort_on_fail
@pytest.mark.usefixtures("add_admin")
async def test_anonymize_user(app: Application):
    """
    arrange: admin user created
    act: run the anonymize-user action
    assert: check the output in the action result
    """
    # Application actually does have units
    action_anonymize: juju.action.Action = await app.units[0].run_action(  # type: ignore
        "anonymize-user", email=ADMIN_USER_EMAIL
    )
    await action_anonymize.wait()
    assert action_anonymize.status == "completed"
    assert action_anonymize.results["user"] == ADMIN_USER_EMAIL
    expected_words = [ADMIN_USER_EMAIL, "correctly anonymized"]
    assert all(word in action_anonymize.results["output"] for word in expected_words)


@pytest.mark.asyncio
@pytest.mark.abort_on_fail
@pytest.mark.usefixtures("add_admin")
async def test_anonymize_user_fail(app: Application):
    """
    arrange: admin user created
    act: run the anonymize-user action
    assert: check the output in the action result
    """
    # Application actually does have units
    action_anonymize: juju.action.Action = await app.units[0].run_action(  # type: ignore
        "anonymize-user", email=f",{ADMIN_USER_EMAIL_FAIL}"
    )
    await action_anonymize.wait()
    assert action_anonymize.status == "failed"
    assert action_anonymize.results["user"] == f",{ADMIN_USER_EMAIL_FAIL}"
    expected_words = [ADMIN_USER_EMAIL_FAIL, "correctly anonymized", "Failed to anonymize user"]
    assert all(word in action_anonymize.results["output"] for word in expected_words)
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 23s</sub>

### ✅ `bash`

**Read test_loki.py, test_s3.py, and test_saml.py**

$ cat /tmp/indico-L3-source-sonnet-4.6/tests/integration/test_loki.py && echo "---FILE_SEPARATOR---" && cat /tmp/indico-L3-source-sonnet-4.6/tests/integration/test_s3.py && echo "---FILE_SEPARATOR---" && cat /tmp/indico-L3-source-sonnet-4.6/tests/integration/test_saml.py

<details>
<summary>194 lines</summary>

```
#!/usr/bin/env python3
# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

"""Indico Loki integration tests."""

import asyncio
import json
import logging
import time

import pytest
import requests
from juju.application import Application
from pytest_operator.plugin import OpsTest

logger = logging.getLogger(__name__)


@pytest.mark.asyncio
@pytest.mark.abort_on_fail
async def test_loki(loki: Application, ops_test: OpsTest):
    """
    arrange: given charm integrated with Loki.
    act: do nothing.
    assert: Loki starts to receive log files from indico.
    """
    _, status, _ = await ops_test.juju("status", "--format", "json")
    status = json.loads(status)
    loki_ip = list(status["applications"][loki.name]["units"].values())[0]["address"]
    logger.info("loki IP: %s", loki_ip)
    deadline = time.time() + 1200
    logged_files = []
    while time.time() < deadline:
        try:
            logged_files = (
                requests.get(
                    f"http://{loki_ip}:3100/loki/api/v1/label/filename/values",
                    timeout=10,
                )
                .json()
                .get("data", [])
            )
        except (requests.exceptions.RequestException, TimeoutError):
            await asyncio.sleep(1)
        if all(
            file in logged_files
            for file in ["/srv/indico/log/celery.log", "/srv/indico/log/indico.log"]
        ):
            return
    raise TimeoutError(f"Loki did not receive all log files from indico, received {logged_files}")
---FILE_SEPARATOR---
#!/usr/bin/env python3
# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

"""Indico S3 integration tests."""

import re

import juju
import pytest
import yaml
from ops import Application
from pytest_operator.plugin import OpsTest


@pytest.mark.asyncio
@pytest.mark.abort_on_fail
@pytest.mark.usefixtures("s3_integrator")
async def test_s3(app: Application, s3_integrator: Application, ops_test: OpsTest):
    """
    arrange: given charm integrated with S3.
    act: do nothing.
    assert: the pebble plan matches the S3 values as configured by the integrator.
    """
    # Application actually does have units
    return_code, stdout, _ = await ops_test.juju(
        "ssh", "--container", app.name, app.units[0].name, "pebble", "plan"  # type: ignore
    )
    assert return_code == 0
    plan = yaml.safe_load(stdout)
    indico_env = plan["services"]["indico"]["environment"]
    # STORAGE_DICT is a string representation of a Python dict
    # pylint: disable=eval-used
    storage_config = eval(indico_env["STORAGE_DICT"])  # nosec
    # Application actually does have units
    action: juju.action.Action = await s3_integrator.units[0].run_action(  # type: ignore
        "get-s3-connection-info"
    )
    await action.wait()
    assert action.status == "completed"
    # in get-s3-connection-info, access_key and secret_key are redacted
    assert re.match(
        f"s3:bucket={action.results['bucket']},"
        f"access_key=[^=]+,secret_key=[^=]+,proxy=true,host={action.results['endpoint']}",
        storage_config["s3"],
    )
---FILE_SEPARATOR---
#!/usr/bin/env python3
# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

"""Indico SAML integration tests."""

import re
import socket
from unittest.mock import patch
from urllib.parse import urlparse

import pytest
import requests
import urllib3.exceptions
from ops import Application
from pytest_operator.plugin import OpsTest


@pytest.mark.asyncio
@pytest.mark.abort_on_fail
@pytest.mark.usefixtures("saml_integrator")
async def test_saml_auth(  # pylint: disable=too-many-arguments, too-many-positional-arguments
    ops_test: OpsTest,
    app: Application,
    saml_email: str,
    saml_password: str,
    requests_timeout: float,
    external_url: str,
):
    """
    arrange: given charm in its initial state
    act: configure a SAML target url and fire SAML authentication
    assert: The SAML authentication process is executed successfully.
    """
    # The linter does not recognize set_config as a method, so this errors must be ignored.
    await app.set_config(  # type: ignore[attr-defined] # pylint: disable=W0106
        {"site_url": external_url}
    )
    # The linter does not recognize wait_for_idle as a method,
    # since ops_test has a model as Optional, so this error must be ignored.
    await ops_test.model.wait_for_idle(status="active", idle_period=15)  # type: ignore[union-attr]
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    host = urlparse(external_url).netloc
    original_getaddrinfo = socket.getaddrinfo

    def patched_getaddrinfo(*args):
        """Get address info forcing localhost as the IP.

        Args:
            args: Arguments from the getaddrinfo original method.

        Returns:
            Address information with localhost as the patched IP.
        """
        if args[0] == host:
            return original_getaddrinfo("127.0.0.1", *args[1:])
        return original_getaddrinfo(*args)

    with patch.multiple(socket, getaddrinfo=patched_getaddrinfo), requests.session() as session:
        session.get(f"https://{host}", verify=False)
        login_page = session.get(
            f"https://{host}/login",
            verify=False,
            timeout=requests_timeout,
        )
        csrf_token_matches = re.findall(
            "<input type='hidden' name='csrfmiddlewaretoken' value='([^']+)' />", login_page.text
        )
        assert csrf_token_matches, login_page.text
        saml_callback = session.post(
            "https://login.staging.ubuntu.com/+login",
            data={
                "csrfmiddlewaretoken": csrf_token_matches[0],
                "email": saml_email,
                "user-intentions": "login",
                "password": saml_password,
                "next": "/saml/process",
                "continue": "",
                "openid.usernamesecret": "",
                "RelayState": "indico.local",
            },
            headers={"Referer": login_page.url},
            timeout=requests_timeout,
        )
        saml_response_matches = re.findall(
            '<input type="hidden" name="SAMLResponse" value="([^"]+)" />', saml_callback.text
        )
        assert len(saml_response_matches), saml_callback.text
        session.post(
            f"https://{host}/multipass/saml/ubuntu/acs",
            data={
                "RelayState": "None",
                "SAMLResponse": saml_response_matches[0],
                "openid.usernamesecret": "",
            },
            verify=False,
            timeout=requests_timeout,
        )
        session.post(
            f"https://{host}/multipass/saml/ubuntu/acs",
            data={"SAMLResponse": saml_response_matches[0], "SameSite": "1"},
            verify=False,
            timeout=requests_timeout,
        )

        dashboard_page = session.get(
            f"https://{host}/register/ubuntu",
            verify=False,
            timeout=requests_timeout,
        )
        assert dashboard_page.status_code == 200
        # Revert SAML config for zap to be able to run
        await app.set_config(  # type: ignore[attr-defined] # pylint: disable=W0106
            {"site_url": ""}
        )
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 29s</sub>

### 💬 Copilot

Now let me examine the jubilant and pytest-jubilant APIs:

---

<sub>⏱️ 29s</sub>

### ✅ `bash`

**Inspect jubilant API**

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

<sub>⏱️ 29s</sub>

### ✅ `bash`

**Find jubilant source files**

$ find /home/ubuntu/.local/lib/python3.12/site-packages -name "*.py" -path "*/jubilant/*" | sort

<details>
<summary>12 lines</summary>

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
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 35s</sub>

### ✅ `bash`

**Read jubilant Juju class source**

$ cat /home/ubuntu/.local/lib/python3.12/site-packages/jubilant/_juju.py | head -400

<details>
<summary>344 lines</summary>

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

        if controller is None:
            model_name = model
        else:
            args.extend(['--controller', controller])
            model_name = f'{controller}:{model}'
        if config is not None:
            for k, v in config.items():
                args.extend(['--config', _format_config(k, v)])
        if credential is not None:
            args.extend(['--credential', credential])

        self.cli(*args, include_model=False)
        self.model = model_name

    def add_secret(
        self,
        name: str,
        content: Mapping[str, str],
        *,
        info: str | None = None,
    ) -> SecretURI:
        """Add a new named secret and return its secret URI.

        Args:
            name: Name for the secret.
            content: Key-value pairs that represent the secret content, for example
                ``{'password': 'hunter2'}``.
            info: Description for the secret.
        """
        args = ['add-secret', name]
        if info is not None:
            args.extend(['--info', info])

        with tempfile.NamedTemporaryFile('w+', dir=self._temp_dir) as file:
            _yaml.safe_dump(content, file)
            file.flush()
            args.extend(['--file', file.name])
            output = self.cli(*args)

        return SecretURI(output.strip())

    def add_ssh_key(self, *keys: str) -> None:
        """Add one or more SSH keys to the model.

        The SSH keys are added to all current and future machines in the model.

        Args:
            keys: SSH public key or keys to add. Each key should be the full
                SSH public key string (for example, ``ssh-rsa AAAAB3... user@host``).
        """
        self.cli('add-ssh-key', *keys)

    def add_unit(
        self,
        app: str,
        *,
        attach_storage: str | Iterable[str] | None = None,
        num_units: int = 1,
        to: str | Iterable[str] | None = None,
    ):
        """Add one or more units to a deployed application.

        Args:
            app: Name of application to add units to.
            attach_storage: Existing storage(s) to attach to the deployed unit, for example,
                ``foo/0`` or ``mydisk/1``. Not available for Kubernetes models.
            num_units: Number of units to add.
            to: Machine or container to deploy the unit in (bypasses constraints). For example,
                to deploy to a new LXD container on machine 25, use ``lxd:25``.
        """
        args = ['add-unit', app]

        if attach_storage:
            if isinstance(attach_storage, str):
                args.extend(['--attach-storage', attach_storage])
            else:
                args.extend(['--attach-storage', ','.join(attach_storage)])
        if num_units != 1:
            args.extend(['--num-units', str(num_units)])
        if to:
            if isinstance(to, str):
                args.extend(['--to', to])
            else:
                args.extend(['--to', ','.join(to)])

        self.cli(*args)

    def bootstrap(
        self,
        cloud: str,
        controller: str,
        *,
        bootstrap_base: str | None = None,
        bootstrap_constraints: Mapping[str, str] | None = None,
        config: Mapping[str, ConfigValue] | None = None,
        constraints: Mapping[str, str] | None = None,
        credential: str | None = None,
        force: bool = False,
        model_defaults: Mapping[str, ConfigValue] | None = None,
        storage_pool: Mapping[str, str] | None = None,
        to: str | Iterable[str] | None = None,
    ) -> None:
        """Bootstrap a controller on a cloud environment.

        To avoid interfering with CLI users, this does not switch the Juju CLI
        to the newly-created controller. In addition, ``self.model`` is not updated.

        If you want to create a new controller with a model, use :meth:`add_model`
        after calling this method, which will set ``self.model`` for future commands::

            juju = jubilant.Juju()
            juju.bootstrap('lxd', 'myctrl')
            juju.add_model('mymodel', controller='myctrl')
            # self.model will be 'myctrl.mymodel' here

        Args:
            cloud: Name of cloud to bootstrap on. Initialization consists of creating a
                "controller" model and provisioning a machine to act as controller.
            controller: Name for the controller.
            bootstrap_base: Specify the base of the bootstrap machine, for example
                ``"24.04"``.
            bootstrap_constraints: Specify bootstrap machine constraints, for example,
                ``{'mem': '8G'}``. If used, its values will also apply to any future
                controllers provisioned for high availability (HA).
            config: Controller configuration options. Model config keys only affect the
                controller model.
            constraints: Set model constraints, for example, ``{'mem': '8G', 'cores': '4'}``.
                If used, its values will be set as the default constraints for all future
                workload machines in the model, exactly as if the constraints were set with
                ``juju set-model-constraints``.
            credential: Name of cloud credential to use when bootstrapping.
            force: If True, allow bypassing of checks such as supported bases.
            model_defaults: Configuration options to set for all models.
            storage_pool: Options for an initial storage pool as key-value pairs. ``name``
                and ``type`` are required, plus any additional attributes.
            to: Placement directive indicating an instance to bootstrap.
        """
        args = ['bootstrap', cloud, controller, '--no-switch']
        if bootstrap_base is not None:
            args.extend(['--bootstrap-base', bootstrap_base])
        if bootstrap_constraints is not None:
            for k, v in bootstrap_constraints.items():
                args.extend(['--bootstrap-constraints', f'{k}={v}'])
        if config is not None:
            for k, v in config.items():
                args.extend(['--config', _format_config(k, v)])
        if constraints is not None:
            for k, v in constraints.items():
                args.extend(['--constraints', f'{k}={v}'])
        if credential is not None:
            args.extend(['--credential', credential])
        if force:
            args.append('--force')
        if model_defaults is not None:
            for k, v in model_defaults.items():
                args.extend(['--model-default', _format_config(k, v)])
        if storage_pool is not None:
            for k, v in storage_pool.items():
                args.extend(['--storage-pool', f'{k}={v}'])
        if to is not None:
            if isinstance(to, str):
                args.extend(['--to', to])
            else:
                args.extend(['--to', ','.join(to)])

        _, stderr = self._cli(*args, include_model=False)
        logger.info('bootstrap output:\n%s', stderr)

    def cli(self, *args: str, include_model: bool = True, stdin: str | None = None) -> str:
        """Run a Juju CLI command and return its standard output.

        Args:
            args: Command-line arguments (excluding ``juju``).
            include_model: If true and :attr:`model` is set, insert the ``--model`` argument
                after the first argument in *args*.
            stdin: Standard input to send to the process, if any.
        """
        stdout, _ = self._cli(*args, include_model=include_model, stdin=stdin)
        return stdout

    def _cli(
        self,
        *args: str,
        include_model: bool = True,
        stdin: str | None = None,
        log: bool = True,
        timeout: float | None = None,
    ) -> tuple[str, str]:
        """Run a Juju CLI command and return its standard output and standard error."""
        if include_model and self.model is not None:
            args = (args[0], '--model', self.model, *args[1:])
        if log:
            logger.info('cli: juju %s', shlex.join(args))
        try:
            process = subprocess.run(
                [self.cli_binary, *args],
                check=True,
                capture_output=True,
                encoding='utf-8',
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 35s</sub>

### ✅ `bash`

**Find pytest-jubilant source**

$ find /home/ubuntu/.local/lib/python3.12/site-packages -name "*.py" -path "*/pytest_jubilant*" | sort && find /home/ubuntu/.local/lib/python3.12/site-packages -name "plugin.py" -path "*jubilant*"

```
/home/ubuntu/.local/lib/python3.12/site-packages/pytest_jubilant/__init__.py
/home/ubuntu/.local/lib/python3.12/site-packages/pytest_jubilant/main.py
/home/ubuntu/.local/lib/python3.12/site-packages/pytest_jubilant/version.py
<exited with exit code 0>
```


---

<sub>⏱️ 40s</sub>

### ✅ `bash`

**Read pytest-jubilant plugin source**

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

<sub>⏱️ 40s</sub>

### ✅ `bash`

**Find key methods in jubilant Juju class**

$ grep -n "def deploy\|def wait\|def integrate\|def run\|def ssh\|def config\|def status\|run_action\|set_config\|get_status" /home/ubuntu/.local/lib/python3.12/site-packages/jubilant/_juju.py | head -80

<details>
<summary>11 lines</summary>

```
409:    def config(self, app: str, *, app_config: bool = False) -> Mapping[str, ConfigValue]: ...
412:    def config(
421:    def config(self, app: str, *, reset: str | Iterable[str]) -> None: ...
423:    def config(
522:    def deploy(
757:    def integrate(self, app1: str, app2: str, *, via: str | Iterable[str] | None = None) -> None:
1047:    def run(
1280:    def ssh(
1323:    def status(self) -> Status:
1387:    def wait(
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 46s</sub>

### ✅ `bash`

**Read deploy, config, integrate methods**

$ sed -n '400,600p' /home/ubuntu/.local/lib/python3.12/site-packages/jubilant/_juju.py

<details>
<summary>179 lines</summary>

```
encoding='utf-8',
                input=stdin,
                timeout=timeout,
            )
        except subprocess.CalledProcessError as e:
            raise CLIError(e.returncode, e.cmd, e.stdout, e.stderr) from None
        return (process.stdout, process.stderr)

    @overload
    def config(self, app: str, *, app_config: bool = False) -> Mapping[str, ConfigValue]: ...

    @overload
    def config(
        self,
        app: str,
        values: Mapping[str, ConfigValue],
        *,
        reset: str | Iterable[str] = (),
    ) -> None: ...

    @overload
    def config(self, app: str, *, reset: str | Iterable[str]) -> None: ...

    def config(
        self,
        app: str,
        values: Mapping[str, ConfigValue] | None = None,
        *,
        app_config: bool = False,
        reset: str | Iterable[str] = (),
    ) -> Mapping[str, ConfigValue] | None:
        """Get or set the configuration of a deployed application.

        If called with only the *app* argument, get the config and return it.

        If called with the *values* or *reset* arguments, set the config values and return None,
        and reset any keys in *reset* to their defaults.

        Args:
            app: Application name to get or set config for.
            values: Mapping of config names to values to set.
            app_config: When getting config, set this to True to get the
                (poorly-named) "application-config" values instead of charm config.
            reset: Key or list of keys to reset to their defaults.
        """
        if values is None and not reset:
            stdout = self.cli('config', '--format', 'json', app)
            outer = json.loads(stdout)
            inner = outer['application-config'] if app_config else outer['settings']
            result = {
                k: SecretURI(v['value']) if v['type'] == 'secret' else v['value']
                for k, v in inner.items()
                if 'value' in v
            }
            return result

        args = ['config', app]
        if values:
            args.extend(_format_config(k, v) for k, v in values.items())
        if reset:
            if not isinstance(reset, str):
                reset = ','.join(reset)
            args.extend(['--reset', reset])

        self.cli(*args)

    def consume(
        self,
        model_and_app: str,
        alias: str | None = None,
        *,
        controller: str | None = None,
        owner: str | None = None,
    ) -> None:
        """Add a remote offer to the model.

        Examples::

            juju.consume('othermodel.mysql', 'sql')
            juju.consume('othermodel.mysql', controller='ctrl2', owner='admin')

        Args:
            model_and_app: Dotted application and model name to offer endpoints for, for example
                ``othermodel.mysql``.
            alias: A local alias for the offer, for use with :meth:`integrate`. Defaults to the
                application name.
            controller: Remote offer's controller. Defaults to the current controller.
            owner: Remote model's owner. Defaults to the user that is currently logged in to the
                controller providing the offer.
        """
        offer_path = model_and_app
        if owner is not None:
            offer_path = f'{owner}/{offer_path}'
        if controller is not None:
            offer_path = f'{controller}:{offer_path}'
        args = ['consume', offer_path]
        if alias is not None:
            args.append(alias)

        self.cli(*args)

    def debug_log(self, *, limit: int = 0) -> str:
        """Return debug log messages from a model.

        For example, to create a pytest fixture which shows the last 1000 log lines if any tests
        fail::

            @pytest.fixture(scope='module')
            def juju(request: pytest.FixtureRequest):
                with jubilant.temp_model() as juju:
                    yield juju  # run the test
                    if request.session.testsfailed:
                        log = juju.debug_log(limit=1000)
                        print(log, end='')

        Args:
            limit: Limit the result to the most recent *limit* lines. Defaults to 0, meaning
                return all lines in the log.
        """
        args = ['debug-log', '--limit', str(limit)]
        return self.cli(*args)

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
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 46s</sub>

### ✅ `bash`

**Read run, ssh, status, wait methods**

$ sed -n '1040,1420p' /home/ubuntu/.local/lib/python3.12/site-packages/jubilant/_juju.py

<details>
<summary>338 lines</summary>

```
if num_units:
            if len(app_or_unit) > 1:
                raise TypeError('"app_or_unit" must be a single app name if num_units specified')
            args.extend(['--num-units', str(num_units)])

        self.cli(*args)

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

    def scp(
        self,
        source: str | pathlib.Path,
        destination: str | pathlib.Path,
        *,
        container: str | None = None,
        host_key_checks: bool = True,
        scp_options: Iterable[str] = (),
    ) -> None:
        """Securely transfer files within a model.

        Args:
            source: Source of file, in format ``[[<user>@]<target>:]<path>``.
            destination: Destination for file, in format ``[<user>@]<target>[:<path>]``.
            container: Name of container for Kubernetes charms. Defaults to the charm container.
            host_key_checks: Set to False to disable host key checking (insecure).
            scp_options: ``scp`` client options, for example ``['-r', '-C']``.
        """
        # Need this check because str is also an iterable of str.
        if isinstance(scp_options, str):
            raise TypeError('scp_options must be an iterable of str, not str')

        args = ['scp']
        if container is not None:
            args.extend(['--container', container])
        if not host_key_checks:
            args.append('--no-host-key-checks')
        args.append('--')
        args.extend(scp_options)

        source = str(source)
        destination = str(destination)
        temp_needed = (':' not in source) != (':' not in destination) and self._juju_is_snap
        if not temp_needed:
            # Simple cases: juju not snap, or local->local, or remote->remote
            args.append(source)
            args.append(destination)
            self.cli(*args)
            return

        with tempfile.NamedTemporaryFile('w+', dir=self._temp_dir) as file_temp:
            if ':' not in source:
                # Local source, remote destination
                shutil.copy(source, file_temp.name)
                args.append(file_temp.name)
                args.append(destination)
                self.cli(*args)
            else:
                # Remote source, local destination
                args.append(source)
                args.append(file_temp.name)
                self.cli(*args)
                shutil.copy(file_temp.name, destination)

    def secrets(self, *, owner: str | None = None) -> list[Secret]:
        """Get all secrets in the model.

        Args:
            owner: The owner of the secrets to retrieve.

        Returns:
            A list of all secrets in the model.
        """
        args = ['secrets']
        if owner is not None:
            args.extend(['--owner', owner])
        stdout = self.cli(*args, '--format', 'json')
        output = json.loads(stdout)
        return [
            Secret._from_dict({'uri': uri_from_juju, **obj})
            for uri_from_juju, obj in output.items()
        ]

    def show_model(self, model: str | None = None) -> ModelInfo:
        """Get information about the current model (or another model).

        Args:
            model: Name of the model or ``controller:model``. If omitted,
                return details about the current model.
        """
        args = ['show-model', '--format', 'json']
        if model is not None:
            args.append(model)
        elif self.model is not None:
            # Use this instance's model if set.
            args.append(self.model)
        stdout = self.cli(*args, include_model=False)
        results = json.loads(stdout)
        info_dict = next(iter(results.values()))
        return ModelInfo._from_dict(info_dict)

    @overload
    def show_secret(
        self,
        identifier: str | SecretURI,
        *,
        reveal: Literal[True],
        revision: int | None = None,
        revisions: Literal[False] = False,
    ) -> RevealedSecret: ...

    @overload
    def show_secret(
        self,
        identifier: str | SecretURI,
        *,
        reveal: Literal[False] = False,
        revision: int | None = None,
        revisions: Literal[False] = False,
    ) -> Secret: ...

    @overload
    def show_secret(
        self,
        identifier: str | SecretURI,
        *,
        reveal: Literal[False] = False,
        revision: None = None,
        revisions: Literal[True],
    ) -> Secret: ...

    def show_secret(
        self,
        identifier: str | SecretURI,
        *,
        reveal: bool = False,
        revision: int | None = None,
        revisions: bool = False,
    ) -> Secret | RevealedSecret:
        """Get the content of a secret.

        Args:
            identifier: Name or URI of the secret to return.
            reveal: Whether to reveal the secret content.
            revision: Revision number of the secret to reveal. If not specified,
                the latest revision is revealed.
            revisions: Whether to include all revisions of the secret. Mutually
                exclusive with *reveal* and *revision*.
        """
        args = ['show-secret', identifier, '--format', 'json']
        if reveal:
            args.append('--reveal')
        if revisions:
            args.append('--revisions')
        if revision is not None:
            args.extend(['--revision', str(revision)])
        stdout = self.cli(*args)
        output = json.loads(stdout)
        uri_from_juju, obj = next(iter(output.items()))
        secret = {'uri': uri_from_juju, **obj}
        if reveal:
            return RevealedSecret._from_dict(secret)
        return Secret._from_dict(secret)

    def ssh(
        self,
        target: str | int,
        command: str,
        *args: str,
        container: str | None = None,
        host_key_checks: bool = True,
        ssh_options: Iterable[str] = (),
        user: str | None = None,
    ) -> str:
        """Executes a command using SSH on a machine or container and returns its standard output.

        Args:
            target: Where to run the command; this is a unit name such as ``mysql/0`` or a machine
                ID such as ``0``.
            command: Command to run. Because the command is executed using the shell,
                arguments may also be included here as a single string, for example
                ``juju.ssh('mysql/0', 'echo foo', ...)``.
            args: Arguments of the command.
            container: Name of container for Kubernetes charms. Defaults to the charm container.
            host_key_checks: Set to False to disable host key checking (insecure).
            ssh_options: OpenSSH client options, for example ``['-i', '/path/to/private.key']``.
            user: User account to make connection with. Defaults to ``ubuntu`` account.
        """
        # Need this check because str is also an iterable of str.
        if isinstance(ssh_options, str):
            raise TypeError('ssh_options must be an iterable of str, not str')

        cli_args = ['ssh']
        if container is not None:
            cli_args.extend(['--container', container])
        if not host_key_checks:
            cli_args.append('--no-host-key-checks')
        if user is not None:
            cli_args.append(f'{user}@{target}')
        else:
            cli_args.append(str(target))
        cli_args.extend(ssh_options)
        cli_args.append(command)
        cli_args.extend(args)

        return self.cli(*cli_args)

    def status(self) -> Status:
        """Fetch the status of the current model, including its applications and units."""
        stdout = self.cli('status', '--format', 'json')
        result = json.loads(stdout)
        return Status._from_dict(result)

    def trust(
        self, app: str, *, remove: bool = False, scope: Literal['cluster'] | None = None
    ) -> None:
        """Set the trust status of a deployed application.

        Args:
            app: Application name to set trust status for.
            remove: Set to True to remove trust status.
            scope: On Kubernetes models, this must be set to "cluster", as the trust operation
                grants the charm full access to the cluster.
        """
        args = ['trust', app]
        if remove:
            args.append('--remove')
        if scope is not None:
            args.extend(['--scope', scope])

        self.cli(*args)

    def update_secret(
        self,
        identifier: str | SecretURI,
        content: Mapping[str, str],
        *,
        info: str | None = None,
        name: str | None = None,
        auto_prune: bool = False,
    ) -> None:
        """Update the content of a secret.

        Args:
            identifier: The name or URI of the secret to update.
            content: Key-value pairs that represent the secret content, for example
                ``{'password': 'hunter2'}``.
            info: New description for the secret.
            name: New name for the secret.
            auto_prune: automatically remove revisions that are no longer tracked by any observers.
        """
        args = ['update-secret', identifier]
        if info is not None:
            args.extend(['--info', info])
        if name is not None:
            args.extend(['--name', name])
        if auto_prune:
            args.append('--auto-prune')

        with tempfile.NamedTemporaryFile('w+', dir=self._temp_dir) as file:
            _yaml.safe_dump(content, file)
            file.flush()
            args.extend(['--file', file.name])
            self.cli(*args)

    def version(self) -> Version:
        """Return the parsed Juju CLI version."""
        stdout = self.cli('version', '--format', 'json', '--all', include_model=False)
        version_dict = json.loads(stdout)
        return Version._from_dict(version_dict)

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
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 51s</sub>

### ✅ `bash`

**Read all_active, all_blocked, any_error helpers**

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

<sub>⏱️ 51s</sub>

### ✅ `bash`

**Read status types**

$ cat /home/ubuntu/.local/lib/python3.12/site-packages/jubilant/statustypes.py | head -150

<details>
<summary>130 lines</summary>

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
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 57s</sub>

### 💬 Copilot

Now let me check the Task class and look at the existing tox.ini and requirements:

---

<sub>⏱️ 58s</sub>

### ✅ `bash`

**Read Task class**

$ cat /home/ubuntu/.local/lib/python3.12/site-packages/jubilant/_task.py

<details>
<summary>78 lines</summary>

```
from __future__ import annotations

import dataclasses
from typing import Any, Literal

from . import _pretty


class TaskError(Exception):
    """Exception raised when an action or exec command fails."""

    task: Task
    """Associated task."""

    def __init__(self, task: Task):
        self.task = task

    def __str__(self) -> str:
        return f'task error: {self.task}'


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

<sub>⏱️ 58s</sub>

### ✅ `bash`

**Read tox.ini and requirements.txt**

$ cat /tmp/indico-L3-source-sonnet-4.6/tox.ini && echo "---" && cat /tmp/indico-L3-source-sonnet-4.6/requirements.txt

<details>
<summary>172 lines</summary>

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
commands =
    isort {[vars]all_path}
    black {[vars]all_path}

[testenv:lint]
basepython = py312
description = Check code against coding style standards
deps =
    black
    codespell
    flake8
    flake8-builtins
    flake8-copyright
    flake8-docstrings
    flake8-docstrings-complete
    flake8-test-docs
    isort
    mypy
    pep8-naming
    pydocstyle>=2.10
    pylint
    pyproject-flake8
    pytest
    pytest-asyncio
    pytest-operator
    requests
    types-PyYAML
    types-requests
    -r{toxinidir}/requirements.txt
commands =
    pydocstyle {[vars]src_path}
    # uncomment the following line if this charm owns a lib
    # codespell {[vars]lib_path}
    codespell {toxinidir} --skip {toxinidir}/.git --skip {toxinidir}/.tox \
      --skip {toxinidir}/build --skip {toxinidir}/lib --skip {toxinidir}/venv \
      --skip {toxinidir}/.mypy_cache --skip {toxinidir}/icon.svg
    # pflake8 wrapper supports config from pyproject.toml
    pflake8 {[vars]all_path} --ignore=W503
    isort --check-only --diff {[vars]all_path}
    black --check --diff {[vars]all_path}
    mypy {[vars]all_path}
    pylint {[vars]all_path}

[testenv:plugins]
# Requires python3.12 installed by pyenv
setenv =
  # patched path for github runners so that tox can find python3.12
  PATH = /home/runner/.pyenv/versions/3.12.2/bin:{env:PATH}
basepython = python3.12
description = Check plugins code against coding style standards
deps =
    black
    codespell
    flake8
    flake8-builtins
    flake8-copyright
    flake8-docstrings
    flake8-docstrings-complete
    flake8-test-docs
    indico==3.3.6
    isort
    mypy
    pep8-naming
    indico_rock/plugins/autocreate
    indico_rock/plugins/anonymize
    pydocstyle>=2.10
    pylint
    pyproject-flake8
    pytest
    pytest-asyncio
    pytest-operator
    requests
    types-PyYAML
    types-requests
    ; 2024/11/19 - there is an incompatibility issue with latest websockets lib release and pylib juju
    websockets<14.0 # https://github.com/juju/python-libjuju/issues/1184
    -r{toxinidir}/requirements.txt
commands =
    codespell {[vars]plugins_path} --skip {toxinidir}/.git --skip {toxinidir}/.tox \
      --skip {toxinidir}/build --skip {toxinidir}/lib --skip {toxinidir}/venv \
      --skip {toxinidir}/.mypy_cache --skip {toxinidir}/icon.svg \
      --skip {toxinidir}/indico_rock/plugins/autocreate/.mypy_cache \
      --skip {toxinidir}/indico_rock/plugins/anonymize/.mypy_cache
    # pflake8 is disabled temporarily due to it not working with python3.12
    # # pflake8 wrapper supports config from pyproject.toml
    # pflake8 {[vars]plugins_path} --ignore=W503
    isort --check-only --diff {[vars]plugins_path}
    black --check --diff {[vars]plugins_path}
    mypy {[vars]plugins_path}
    pylint {[vars]plugins_path} --ignore-paths {[vars]plugins_path}autocreate/build,{[vars]plugins_path}anonymize/build

[testenv:unit]
description = Run unit tests
deps =
    cosl
    coverage[toml]
    pytest
    pytest-mock
    ops[testing]==2.21.1
    -r{toxinidir}/requirements.txt
commands =
    coverage run --source={[vars]src_path} \
        -m pytest --ignore={[vars]tst_path}integration -v --tb native -s {posargs}
    coverage report

[testenv:coverage-report]
description = Create test coverage report
deps =
    coverage[toml]
    pytest
    -r{toxinidir}/requirements.txt
commands =
    coverage report

[testenv:static]
description = Run static analysis tests
deps =
    bandit[toml]
    -r{toxinidir}/requirements.txt
commands =
    bandit -c {toxinidir}/pyproject.toml -r {[vars]src_path} {[vars]tst_path}

[testenv:integration]
description = Run integration tests
deps =
    -r{toxinidir}/requirements.txt
    allure-pytest>=2.8.18
    cosl
    git+https://github.com/canonical/data-platform-workflows@v24.0.0\#subdirectory=python/pytest_plugins/allure_pytest_collection_report
    juju==2.9.49.0
    pytest
    pytest-asyncio
    pytest-operator
    websockets<14.0 # https://github.com/juju/python-libjuju/issues/1184
commands =
    pytest -v --tb native --ignore={[vars]tst_path}unit --log-cli-level=INFO -s {posargs}

[testenv:src-docs]
allowlist_externals=sh
setenv =
    PYTHONPATH = {toxinidir}:{toxinidir}/lib:{[vars]src_path}
description = Generate documentation for src
deps =
    cosl
    lazydocs
    -r{toxinidir}/requirements.txt
commands =
    ; can't run lazydocs directly due to needing to run it on src/* which produces an invocation error in tox
    sh generate-src-docs.sh
---
pydantic==1.10.26
ops>=2.0.0,<3.0.0
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 1m 5s</sub>

### ✅ `bash`

**Find get_units and address fields**

$ grep -n "def get_units\|def get_\|address\|public_address" /home/ubuntu/.local/lib/python3.12/site-packages/jubilant/statustypes.py | head -30

<details>
<summary>16 lines</summary>

```
109:    public_address: str = ''
110:    address: str = ''
134:            public_address=d.get('public-address') or '',
135:            address=d.get('address') or '',
185:    address: str = ''
218:            address=d.get('address') or '',
397:    bus_address: str = ''
406:            bus_address=d.get('bus-address') or '',
511:    ip_addresses: list[str]
512:    mac_address: str
522:            ip_addresses=d['ip-addresses'],
523:            mac_address=d['mac-address'],
538:    ip_addresses: list[str] = dataclasses.field(default_factory=list)  # type: ignore
565:            ip_addresses=d.get('ip-addresses') or [],
773:    def get_units(self, app: str) -> dict[str, UnitStatus]:
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 1m 4s</sub>

### ✅ `bash`

**Read __init__.py**

$ cat /tmp/indico-L3-source-sonnet-4.6/tests/integration/__init__.py

```
# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.
<exited with exit code 0>
```


---

<sub>⏱️ 1m 11s</sub>

### ✅ `bash`

**Read get_units method**

$ sed -n '770,820p' /home/ubuntu/.local/lib/python3.12/site-packages/jubilant/statustypes.py

<details>
<summary>25 lines</summary>

```
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
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 1m 11s</sub>

### ✅ `bash`

**Check custom pytest options**

$ grep -n "conftest_options\|addoption\|charm-file\|indico-image\|saml-email\|saml-password" /tmp/indico-L3-source-sonnet-4.6/tests/integration/conftest.py

<details>
<summary>7 lines</summary>

```
26:    email = pytestconfig.getoption("--saml-email")
28:        raise ValueError("--saml-email argument is required for selected test cases")
35:    password = pytestconfig.getoption("--saml-password")
37:        raise ValueError("--saml-password argument is required for selected test cases")
91:        "indico-image": pytestconfig.getoption("--indico-image"),
95:    if charm := pytestconfig.getoption("--charm-file"):
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 1m 57s</sub>

### ✅ `bash`

**Find all conftest files and pytest config**

$ find /tmp/indico-L3-source-sonnet-4.6 -name "conftest.py" | sort && find /tmp/indico-L3-source-sonnet-4.6 -name "pytest.ini" -o -name "setup.cfg" -o -name "pyproject.toml" | xargs grep -l "addopts\|testpaths\|filterwarnings" 2>/dev/null

```
/tmp/indico-L3-source-sonnet-4.6/tests/conftest.py
/tmp/indico-L3-source-sonnet-4.6/tests/integration/conftest.py
/tmp/indico-L3-source-sonnet-4.6/tests/unit/conftest.py
/tmp/indico-L3-source-sonnet-4.6/tests/unit_harness/conftest.py
<exited with exit code 123>
```


---

<sub>⏱️ 1m 57s</sub>

### ✅ `bash`

**Check pyproject.toml for pytest settings**

$ grep -n "addopts\|testpaths\|asyncio_mode\|indico-image\|saml-email\|charm-file" /tmp/indico-L3-source-sonnet-4.6/pyproject.toml

```

<exited with exit code 1>
```


---

<sub>⏱️ 2m 3s</sub>

### ✅ `bash`

**Read top-level conftest.py**

$ cat /tmp/indico-L3-source-sonnet-4.6/tests/conftest.py

<details>
<summary>14 lines</summary>

```
# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

"""Fixtures for Indico charm tests."""


def pytest_addoption(parser):
    """Parse additional pytest options.

    Args:
        parser: Pytest parser.
    """
    parser.addoption("--charm-file", action="store")
    parser.addoption("--indico-image", action="store")
    parser.addoption("--indico-nginx-image", action="store")
    parser.addoption("--saml-email", action="store")
    parser.addoption("--saml-password", action="store")
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 2m 3s</sub>

### ✅ `bash`

**Check pyproject.toml for test options**

$ grep -n "indico-image\|saml-email\|charm-file\|addoption" /tmp/indico-L3-source-sonnet-4.6/pyproject.toml 2>/dev/null | head -20

```

<exited with exit code 0>
```


---

<sub>⏱️ 3m 28s</sub>

### ✅ `bash`

**Check for exec method in jubilant**

$ grep -n "def exec\|def run_command\|def exec_" /home/ubuntu/.local/lib/python3.12/site-packages/jubilant/_juju.py

```
665:    def exec(
670:    def exec(self, command: str, *args: str, unit: str, wait: float | None = None) -> Task: ...
672:    def exec(
<exited with exit code 0>
```


---

<sub>⏱️ 3m 28s</sub>

### ✅ `bash`

**List all methods in Juju class**

$ grep -n "def " /home/ubuntu/.local/lib/python3.12/site-packages/jubilant/_juju.py | head -50

<details>
<summary>51 lines</summary>

```
31:    def __str__(self) -> str:
86:    def __init__(
97:    def __repr__(self) -> str:
109:    def add_credential(
120:    def add_credential(
130:    def add_credential(
173:    def add_model(
216:    def add_secret(
243:    def add_ssh_key(self, *keys: str) -> None:
254:    def add_unit(
289:    def bootstrap(
370:    def cli(self, *args: str, include_model: bool = True, stdin: str | None = None) -> str:
382:    def _cli(
409:    def config(self, app: str, *, app_config: bool = False) -> Mapping[str, ConfigValue]: ...
412:    def config(
421:    def config(self, app: str, *, reset: str | Iterable[str]) -> None: ...
423:    def config(
466:    def consume(
501:    def debug_log(self, *, limit: int = 0) -> str:
508:            def juju(request: pytest.FixtureRequest):
522:    def deploy(
623:    def destroy_model(
665:    def exec(
670:    def exec(self, command: str, *args: str, unit: str, wait: float | None = None) -> Task: ...
672:    def exec(
745:    def grant_secret(self, identifier: str | SecretURI, app: str | Iterable[str]) -> None:
757:    def integrate(self, app1: str, app2: str, *, via: str | Iterable[str] | None = None) -> None:
786:    def model_config(self) -> Mapping[str, ConfigValue]: ...
789:    def model_config(
794:    def model_config(self, *, reset: str | Iterable[str]) -> None: ...
796:    def model_config(
827:    def model_constraints(self) -> Mapping[str, ConstraintValue]: ...
830:    def model_constraints(self, constraints: Mapping[str, ConstraintValue]) -> None: ...
832:    def model_constraints(
852:    def offer(
886:    def refresh(
942:    def remove_application(
964:    def remove_relation(self, app1: str, app2: str, *, force: bool = False) -> None:
982:    def remove_secret(self, identifier: str | SecretURI, *, revision: int | None = None) -> None:
994:    def remove_ssh_key(self, *ids: str) -> None:
1007:    def remove_unit(
1047:    def run(
1126:    def scp(
1180:    def secrets(self, *, owner: str | None = None) -> list[Secret]:
1199:    def show_model(self, model: str | None = None) -> ModelInfo:
1218:    def show_secret(
1228:    def show_secret(
1238:    def show_secret(
1247:    def show_secret(
1280:    def ssh(
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 3m 40s</sub>

### ✅ `bash`

**Read exec method**

$ sed -n '665,745p' /home/ubuntu/.local/lib/python3.12/site-packages/jubilant/_juju.py

<details>
<summary>71 lines</summary>

```
def exec(
        self, command: str, *args: str, machine: int | str, wait: float | None = None
    ) -> Task: ...

    @overload
    def exec(self, command: str, *args: str, unit: str, wait: float | None = None) -> Task: ...

    def exec(
        self,
        command: str,
        *args: str,
        machine: int | str | None = None,
        unit: str | None = None,
        wait: float | None = None,
    ) -> Task:
        """Run the command on the remote target specified.

        You must specify either *machine* or *unit*, but not both.

        Note: this method does not support running a command on multiple units
        at once. If you need that, let us know, and we'll consider adding it
        with a new ``exec_multiple`` method or similar.

        Args:
            command: Command to run. Because the command is executed using the shell,
                arguments may also be included here as a single string, for example
                ``juju.exec('echo foo', ...)``.
            args: Arguments of the command.
            machine: ID of machine to run the command on, for example ``0``, ``"0"``,
                or ``"0/lxd/0"``.
            unit: Name of unit to run the command on, for example ``mysql/0`` or ``mysql/leader``.
            wait: Maximum time to wait for command to finish; :class:`TimeoutError` is raised if
                this is reached. Juju's default is to wait 5 minutes.

        Returns:
            The task created to run the command, including logs, failure message, and so on.

        Raises:
            ValueError: if the machine or unit doesn't exist.
            TaskError: if the command failed.
            TimeoutError: if *wait* was specified and the wait time was reached.
        """
        if (machine is not None and unit is not None) or (machine is None and unit is None):
            raise TypeError('must specify "machine" or "unit", but not both')

        cli_args = ['exec', '--format', 'json']
        if machine is not None:
            cli_args.extend(['--machine', str(machine)])
        else:
            assert unit is not None
            cli_args.extend(['--unit', unit])
        if wait is not None:
            cli_args.extend(['--wait', f'{wait}s'])
        cli_args.append('--')
        cli_args.append(command)
        cli_args.extend(args)

        try:
            stdout, stderr = self._cli(*cli_args)
        except CLIError as exc:
            if 'timed out' in exc.stderr:
                msg = f'timed out waiting for command, stderr:\n{exc.stderr}'
                raise TimeoutError(msg) from None
            # The "juju exec" CLI command itself fails if the exec'd command fails.
            if 'task failed' not in exc.stderr:
                raise
            stdout = exc.stdout
            stderr = exc.stderr

        # Command doesn't return any stdout if no units exist.
        results: dict[str, Any] = json.loads(stdout) if stdout.strip() else {}
        if not results:
            raise ValueError(f'error running command, stderr:\n{stderr}')
        # Don't look up results[unit] directly, because if the caller specifies
        # app/leader it is returned as app/N, for example app/0.
        task_dict = next(iter(results.values()))
        task = Task._from_dict(task_dict)
        task.raise_on_failure()
        return task

    def grant_secret(self, identifier: str | SecretURI, app: str | Iterable[str]) -> None:
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 4m 23s</sub>

### ✅ `bash`

**Read pytest_jubilant __init__.py**

$ cat /home/ubuntu/.local/lib/python3.12/site-packages/pytest_jubilant/__init__.py

<details>
<summary>7 lines</summary>

```
#!/usr/bin/env python3
# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

"""Welcome to pytest-jubilant!"""

from pytest_jubilant.main import pack, get_resources

__all__ = ["pack", "get_resources"]
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 4m 33s</sub>

### 💬 Copilot

Now I have everything I need. Let me implement the migration:

---

<sub>⏱️ 4m 33s</sub>

### ✅ `sql`

**Create migration todos**

<details>
<summary>Arguments</summary>

```json
{
  "description": "Create migration todos",
  "query": "INSERT INTO todos (id, title, status) VALUES\n  ('conftest', 'Rewrite integration conftest.py', 'pending'),\n  ('test-charm', 'Migrate test_charm.py', 'pending'),\n  ('test-actions', 'Migrate test_actions.py', 'pending'),\n  ('test-loki', 'Migrate test_loki.py', 'pending'),\n  ('test-s3', 'Migrate test_s3.py', 'pending'),\n  ('test-saml', 'Migrate test_saml.py', 'pending'),\n  ('tox-ini', 'Update tox.ini deps', 'pending');"
}
```

</details>

```
7 row(s) inserted. Last inserted row ID: 7.
```


---

<sub>⏱️ 5m 14s</sub>

### ✅ `edit`

**/tmp/indico-L3-source-sonnet-4.6/tests/integration/conftest.py**

/tmp/indico-L3-source-sonnet-4.6/tests/integration/conftest.py

```
File /tmp/indico-L3-source-sonnet-4.6/tests/integration/conftest.py updated with changes.
```


---

<sub>⏱️ 5m 42s</sub>

### 💬 Copilot

Now migrate `test_charm.py`:

---

<sub>⏱️ 5m 42s</sub>

### ✅ `edit`

**/tmp/indico-L3-source-sonnet-4.6/tests/integration/test_charm.py**

/tmp/indico-L3-source-sonnet-4.6/tests/integration/test_charm.py

```
File /tmp/indico-L3-source-sonnet-4.6/tests/integration/test_charm.py updated with changes.
```


---

<sub>⏱️ 6m 3s</sub>

### 💬 Copilot

Now migrate `test_actions.py`:

---

<sub>⏱️ 6m 3s</sub>

### ✅ `edit`

**/tmp/indico-L3-source-sonnet-4.6/tests/integration/test_actions.py**

/tmp/indico-L3-source-sonnet-4.6/tests/integration/test_actions.py

```
File /tmp/indico-L3-source-sonnet-4.6/tests/integration/test_actions.py updated with changes.
```


---

<sub>⏱️ 6m 20s</sub>

### 💬 Copilot

Now migrate `test_loki.py`:

---

<sub>⏱️ 6m 20s</sub>

### ✅ `edit`

**/tmp/indico-L3-source-sonnet-4.6/tests/integration/test_loki.py**

/tmp/indico-L3-source-sonnet-4.6/tests/integration/test_loki.py

```
File /tmp/indico-L3-source-sonnet-4.6/tests/integration/test_loki.py updated with changes.
```


---

<sub>⏱️ 6m 35s</sub>

### 💬 Copilot

Now migrate `test_s3.py`:

---

<sub>⏱️ 6m 35s</sub>

### ✅ `edit`

**/tmp/indico-L3-source-sonnet-4.6/tests/integration/test_s3.py**

/tmp/indico-L3-source-sonnet-4.6/tests/integration/test_s3.py

```
File /tmp/indico-L3-source-sonnet-4.6/tests/integration/test_s3.py updated with changes.
```


---

<sub>⏱️ 7m 1s</sub>

### 💬 Copilot

Now migrate `test_saml.py`:

---

<sub>⏱️ 7m 1s</sub>

### ✅ `edit`

**/tmp/indico-L3-source-sonnet-4.6/tests/integration/test_saml.py**

/tmp/indico-L3-source-sonnet-4.6/tests/integration/test_saml.py

```
File /tmp/indico-L3-source-sonnet-4.6/tests/integration/test_saml.py updated with changes.
```


---

<sub>⏱️ 7m 8s</sub>

### 💬 Copilot

Now update `tox.ini` — replace deps in both `lint` and `integration` envs:

---

<sub>⏱️ 7m 8s</sub>

### ✅ `edit`

**/tmp/indico-L3-source-sonnet-4.6/tox.ini**

/tmp/indico-L3-source-sonnet-4.6/tox.ini

```
File /tmp/indico-L3-source-sonnet-4.6/tox.ini updated with changes.
```


---

<sub>⏱️ 7m 15s</sub>

### ✅ `edit`

**/tmp/indico-L3-source-sonnet-4.6/tox.ini**

/tmp/indico-L3-source-sonnet-4.6/tox.ini

```
File /tmp/indico-L3-source-sonnet-4.6/tox.ini updated with changes.
```


---

<sub>⏱️ 7m 23s</sub>

### ✅ `bash`

**Check tox.ini for remaining old deps**

$ grep -n "pytest-asyncio\|pytest-operator\|websockets\|jubilant\|juju==" /tmp/indico-L3-source-sonnet-4.6/tox.ini

<details>
<summary>11 lines</summary>

```
54:    jubilant
55:    pytest-jubilant
100:    pytest-asyncio
101:    pytest-operator
105:    ; 2024/11/19 - there is an incompatibility issue with latest websockets lib release and pylib juju
106:    websockets<14.0 # https://github.com/juju/python-libjuju/issues/1184
159:    juju==2.9.49.0
161:    pytest-asyncio
162:    pytest-operator
163:    websockets<14.0 # https://github.com/juju/python-libjuju/issues/1184
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 7m 30s</sub>

### ✅ `view`

**/tmp/indico-L3-source-sonnet-4.6/tox.ini**

/tmp/indico-L3-source-sonnet-4.6/tox.ini (lines 90-115)

<details>
<summary>26 lines</summary>

```
90.     indico==3.3.6
91.     isort
92.     mypy
93.     pep8-naming
94.     indico_rock/plugins/autocreate
95.     indico_rock/plugins/anonymize
96.     pydocstyle>=2.10
97.     pylint
98.     pyproject-flake8
99.     pytest
100.     pytest-asyncio
101.     pytest-operator
102.     requests
103.     types-PyYAML
104.     types-requests
105.     ; 2024/11/19 - there is an incompatibility issue with latest websockets lib release and pylib juju
106.     websockets<14.0 # https://github.com/juju/python-libjuju/issues/1184
107. commands =
108.     codespell {[vars]plugins_path} --skip {toxinidir}/.git --skip {toxinidir}/.tox \
109.       --skip {toxinidir}/build --skip {toxinidir}/lib --skip {toxinidir}/venv \
110.       --skip {toxinidir}/.mypy_cache --skip {toxinidir}/icon.svg \
111.       --skip {toxinidir}/indico_rock/plugins/autocreate/.mypy_cache \
112.       --skip {toxinidir}/indico_rock/plugins/anonymize/.mypy_cache
113.     # pflake8 is disabled temporarily due to it not working with python3.12
114.     # # pflake8 wrapper supports config from pyproject.toml
115.     # pflake8 {[vars]plugins_path} --ignore=W503
```

</details>


---

<sub>⏱️ 7m 30s</sub>

### ✅ `view`

**/tmp/indico-L3-source-sonnet-4.6/tox.ini**

/tmp/indico-L3-source-sonnet-4.6/tox.ini (lines 150-175)

<details>
<summary>26 lines</summary>

```
150.     bandit -c {toxinidir}/pyproject.toml -r {[vars]src_path} {[vars]tst_path}
151. 
152. [testenv:integration]
153. description = Run integration tests
154. deps =
155.     -r{toxinidir}/requirements.txt
156.     allure-pytest>=2.8.18
157.     cosl
158.     git+https://github.com/canonical/data-platform-workflows@v24.0.0\#subdirectory=python/pytest_plugins/allure_pytest_collection_report
159.     juju==2.9.49.0
160.     pytest
161.     pytest-asyncio
162.     pytest-operator
163.     websockets<14.0 # https://github.com/juju/python-libjuju/issues/1184
164. commands =
165.     pytest -v --tb native --ignore={[vars]tst_path}unit --log-cli-level=INFO -s {posargs}
166. 
167. [testenv:src-docs]
168. allowlist_externals=sh
169. setenv =
170.     PYTHONPATH = {toxinidir}:{toxinidir}/lib:{[vars]src_path}
171. description = Generate documentation for src
172. deps =
173.     cosl
174.     lazydocs
175.     -r{toxinidir}/requirements.txt
```

</details>


---

<sub>⏱️ 7m 37s</sub>

### 💬 Copilot

Now I'll update the `plugins` and `integration` envs:

---

<sub>⏱️ 7m 37s</sub>

### ✅ `edit`

**/tmp/indico-L3-source-sonnet-4.6/tox.ini**

/tmp/indico-L3-source-sonnet-4.6/tox.ini

```
File /tmp/indico-L3-source-sonnet-4.6/tox.ini updated with changes.
```


---

<sub>⏱️ 7m 44s</sub>

### ✅ `edit`

**/tmp/indico-L3-source-sonnet-4.6/tox.ini**

/tmp/indico-L3-source-sonnet-4.6/tox.ini

```
File /tmp/indico-L3-source-sonnet-4.6/tox.ini updated with changes.
```


---

<sub>⏱️ 7m 50s</sub>

### 💬 Copilot

Now let's verify all changes are correct and run linting:

---

<sub>⏱️ 7m 51s</sub>

### ✅ `bash`

**Check for remaining old imports/deps**

$ cd /tmp/indico-L3-source-sonnet-4.6 && grep -n "pytest-asyncio\|pytest-operator\|juju==\|websockets<\|asyncio\|OpsTest\|python-libjuju" tox.ini tests/integration/*.py

```

<exited with exit code 1>
```


---

<sub>⏱️ 7m 57s</sub>

### 💬 Copilot

Clean. Now run the linter:

---

<sub>⏱️ 7m 59s</sub>

### ✅ `bash`

**Run formatter**

$ cd /tmp/indico-L3-source-sonnet-4.6 && tox -e fmt 2>&1 | tail -15

<details>
<summary>11 lines</summary>

```
fmt: venv> /home/ubuntu/.local/share/uv/tools/tox/bin/uv venv -p /home/ubuntu/.local/share/uv/tools/tox/bin/python --allow-existing --python-preference system /tmp/indico-L3-source-sonnet-4.6/.tox/fmt
fmt: install_deps> /home/ubuntu/.local/share/uv/tools/tox/bin/uv pip install black isort
fmt: commands[0]> isort /tmp/indico-L3-source-sonnet-4.6/src/ /tmp/indico-L3-source-sonnet-4.6/tests/
fmt: commands[1]> black /tmp/indico-L3-source-sonnet-4.6/src/ /tmp/indico-L3-source-sonnet-4.6/tests/
reformatted /tmp/indico-L3-source-sonnet-4.6/tests/integration/test_actions.py
reformatted /tmp/indico-L3-source-sonnet-4.6/tests/integration/test_charm.py

All done! ✨ 🍰 ✨
2 files reformatted, 27 files left unchanged.
  fmt: OK (1.91=setup[1.55]+cmd[0.10,0.26] seconds)
  congratulations :) (1.93 seconds)
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 8m 27s</sub>

### ✅ `bash`

**Run linter**

$ cd /tmp/indico-L3-source-sonnet-4.6 && tox -e lint 2>&1 | tail -40

<details>
<summary>20 lines</summary>

```
lint: venv> /home/ubuntu/.local/share/uv/tools/tox/bin/uv venv -p /home/ubuntu/.local/share/uv/tools/tox/bin/python --allow-existing --python-preference system /tmp/indico-L3-source-sonnet-4.6/.tox/lint
lint: install_deps> /home/ubuntu/.local/share/uv/tools/tox/bin/uv pip install black codespell flake8 flake8-builtins flake8-copyright flake8-docstrings flake8-docstrings-complete flake8-test-docs isort jubilant mypy pep8-naming 'pydocstyle>=2.10' pylint pyproject-flake8 pytest pytest-jubilant requests types-PyYAML types-requests -r /tmp/indico-L3-source-sonnet-4.6/requirements.txt
lint: commands[0]> pydocstyle /tmp/indico-L3-source-sonnet-4.6/src/
lint: commands[1]> codespell /tmp/indico-L3-source-sonnet-4.6 --skip /tmp/indico-L3-source-sonnet-4.6/.git --skip /tmp/indico-L3-source-sonnet-4.6/.tox --skip /tmp/indico-L3-source-sonnet-4.6/build --skip /tmp/indico-L3-source-sonnet-4.6/lib --skip /tmp/indico-L3-source-sonnet-4.6/venv --skip /tmp/indico-L3-source-sonnet-4.6/.mypy_cache --skip /tmp/indico-L3-source-sonnet-4.6/icon.svg
lint: commands[2]> pflake8 /tmp/indico-L3-source-sonnet-4.6/src/ /tmp/indico-L3-source-sonnet-4.6/tests/ --ignore=W503
lint: commands[3]> isort --check-only --diff /tmp/indico-L3-source-sonnet-4.6/src/ /tmp/indico-L3-source-sonnet-4.6/tests/
lint: commands[4]> black --check --diff /tmp/indico-L3-source-sonnet-4.6/src/ /tmp/indico-L3-source-sonnet-4.6/tests/
All done! ✨ 🍰 ✨
29 files would be left unchanged.
lint: commands[5]> mypy /tmp/indico-L3-source-sonnet-4.6/src/ /tmp/indico-L3-source-sonnet-4.6/tests/
tests/unit_harness/test_actions.py:44: note: By default the bodies of untyped functions are not checked, consider using --check-untyped-defs  [annotation-unchecked]
tests/unit_harness/test_actions.py:87: note: By default the bodies of untyped functions are not checked, consider using --check-untyped-defs  [annotation-unchecked]
tests/unit_harness/test_actions.py:182: note: By default the bodies of untyped functions are not checked, consider using --check-untyped-defs  [annotation-unchecked]
Success: no issues found in 29 source files
lint: commands[6]> pylint /tmp/indico-L3-source-sonnet-4.6/src/ /tmp/indico-L3-source-sonnet-4.6/tests/

------------------------------------
Your code has been rated at 10.00/10

  lint: OK (20.10=setup[11.19]+cmd[0.23,0.09,0.26,0.10,0.30,2.50,5.42] seconds)
  congratulations :) (20.11 seconds)
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 8m 34s</sub>

### 💬 Copilot

Lint passes with 10/10. Let's also run unit tests to ensure nothing is broken:

---

<sub>⏱️ 8m 37s</sub>

### ✅ `bash`

**Run unit tests**

$ cd /tmp/indico-L3-source-sonnet-4.6 && tox -e unit 2>&1 | tail -20

<details>
<summary>19 lines</summary>

```
tests/unit_harness/test_smtp_observer.py::test_smtp_related_emits_config_changed_event_and_updates_charm_state
  /tmp/indico-L3-source-sonnet-4.6/tests/unit_harness/test_smtp_observer.py:63: PendingDeprecationWarning: Harness is deprecated. For the recommended approach, see: https://ops.readthedocs.io/en/latest/howto/write-unit-tests-for-a-charm.html
    harness = Harness(ObservedCharm, meta=REQUIRER_METADATA)

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
======================= 42 passed, 97 warnings in 1.06s ========================
unit: commands[1]> coverage report
Name                       Stmts   Miss Branch BrPart  Cover   Missing
----------------------------------------------------------------------
src/charm.py                 357     12     80      8    95%   408, 422-423, 673, 714-715, 818->834, 820->829, 829->834, 842-843, 882, 915->exit, 953-959
src/database_observer.py      32      0      4      0   100%
src/s3_observer.py            17      0      0      0   100%
src/saml_observer.py          14      0      0      0   100%
src/smtp_observer.py          15      0      0      0   100%
src/state.py                  73      0      8      0   100%
----------------------------------------------------------------------
TOTAL                        508     12     92      8    97%
  unit: OK (2.91=setup[1.23]+cmd[1.59,0.09] seconds)
  congratulations :) (2.93 seconds)
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 8m 45s</sub>

### 💬 Copilot

All tests pass with 97% coverage. Let me now commit the changes:

---

<sub>⏱️ 8m 46s</sub>

### ✅ `bash`

**Show changed files**

$ cd /tmp/indico-L3-source-sonnet-4.6 && git diff --stat

<details>
<summary>9 lines</summary>

```
tests/integration/conftest.py     | 156 +++++++++++++++++++++++++++++++++++++-----------------------------------------
 tests/integration/test_actions.py |  78 +++++++++++++++++----------------------
 tests/integration/test_charm.py   |  74 ++++++++++++-------------------------
 tests/integration/test_loki.py    |  15 +++-----
 tests/integration/test_s3.py      |  25 ++++---------
 tests/integration/test_saml.py    |  23 ++++--------
 tox.ini                           |  17 +++------
 7 files changed, 154 insertions(+), 234 deletions(-)
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 9m 4s</sub>

### ✅ `bash`

**Commit migration changes**

$ cd /tmp/indico-L3-source-sonnet-4.6 && git add tests/integration/ tox.ini && git commit -m "Migrate integration tests from pytest-operator to jubilant

Replace all python-libjuju / pytest-operator usage with the jubilant
and pytest-jubilant libraries:

- conftest.py: convert async fixtures to sync, replace OpsTest/Application
  with jubilant.Juju, use juju.deploy/integrate/wait/run, use pack() to
  build the charm locally, return app names (str) instead of Application
  objects
- test_charm.py: replace async tests with sync equivalents, use
  juju.status() for address lookup and juju.exec() for in-unit commands
- test_actions.py: replace run_action/await with juju.run(), catch
  TaskError for expected-failure assertions
- test_loki.py: replace ops_test.juju(status) with juju.status(), replace
  asyncio.sleep with time.sleep
- test_s3.py: replace ops_test.juju(ssh) with juju.ssh(), replace
  run_action with juju.run()
- test_saml.py: replace app.set_config/wait_for_idle with
  juju.config/juju.wait
- tox.ini: replace juju==2.9.49.0, pytest-asyncio, pytest-operator,
  websockets<14.0 with jubilant and pytest-jubilant in both lint and
  integration environments; same replacement in plugins environment

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

<sub>⏱️ 9m 15s</sub>

### ✅ `bash`

**Commit with identity configured**

$ cd /tmp/indico-L3-source-sonnet-4.6 && git config user.email "copilot@github.com" && git config user.name "Copilot" && git commit -m "Migrate integration tests from pytest-operator to jubilant

Replace all python-libjuju / pytest-operator usage with the jubilant
and pytest-jubilant libraries:

- conftest.py: convert async fixtures to sync, replace OpsTest/Application
  with jubilant.Juju, use juju.deploy/integrate/wait/run, use pack() to
  build the charm locally, return app names (str) instead of Application
  objects
- test_charm.py: replace async tests with sync equivalents, use
  juju.status() for address lookup and juju.exec() for in-unit commands
- test_actions.py: replace run_action/await with juju.run(), catch
  TaskError for expected-failure assertions
- test_loki.py: replace ops_test.juju(status) with juju.status(), replace
  asyncio.sleep with time.sleep
- test_s3.py: replace ops_test.juju(ssh) with juju.ssh(), replace
  run_action with juju.run()
- test_saml.py: replace app.set_config/wait_for_idle with
  juju.config/juju.wait
- tox.ini: replace juju==2.9.49.0, pytest-asyncio, pytest-operator,
  websockets<14.0 with jubilant and pytest-jubilant in both lint and
  integration environments; same replacement in plugins environment

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"

```
[main 3aea381] Migrate integration tests from pytest-operator to jubilant
 7 files changed, 154 insertions(+), 234 deletions(-)
<exited with exit code 0>
```


---

<sub>⏱️ 9m 31s</sub>

### 💬 Copilot

Migration complete. Here's a summary of what changed across all 7 files:

**`tests/integration/conftest.py`** — Removed `asyncio`, `pytest_asyncio`, `OpsTest`, `Application`. All fixtures converted from `async def` with `@pytest_asyncio.fixture` to plain `@fixture`. Now uses `juju: jubilant.Juju` for all Juju operations, `juju.deploy/integrate/wait` for setup, and `pack()` instead of `ops_test.build_charm()`. Fixtures now yield app name strings instead of `Application` objects.

**`test_charm.py`** — Removed `@pytest.mark.asyncio`, `async def`, `OpsTest`. Address lookup now uses `juju.status()`. Command execution uses `juju.exec()` (returns `Task` with `.stdout`/`.return_code`) instead of `unit.run()`.

**`test_actions.py`** — Replaced `run_action(...).wait()` with `juju.run(unit, action, params=...)`. For the expected-failure case, catches `TaskError` and inspects `exc.task` rather than checking `action.status == "failed"`.

**`test_loki.py`** — Replaced `ops_test.juju("status", "--format", "json")` + JSON parsing with `juju.status()` and the `Status` dataclass. `asyncio.sleep` → `time.sleep`.

**`test_s3.py`** — Replaced `ops_test.juju("ssh", "--container", ...)` with `juju.ssh(unit, cmd, container=app)`, and `run_action` with `juju.run`.

**`test_saml.py`** — Replaced `app.set_config(...)` with `juju.config(app, {...})` and `wait_for_idle` with `juju.wait(jubilant.all_active, ...)`.

**`tox.ini`** — Removed `juju==2.9.49.0`, `pytest-asyncio`, `pytest-operator`, `websockets\<14.0` from `integration` and `plugins` envs; added `jubilant` and `pytest-jubilant`. Same swap in the `lint` env for type-checking.

---

<sub>Generated by [GitHub Copilot CLI](https://github.com/features/copilot/cli)</sub>
