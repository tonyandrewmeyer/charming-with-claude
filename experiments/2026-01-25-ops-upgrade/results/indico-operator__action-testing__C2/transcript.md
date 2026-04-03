# 🤖 Copilot CLI Session

> [!NOTE]
> - **Session ID:** `0c1143e1-9b98-4d3b-8c32-26f5190730d8`  
> - **Started:** 4/3/2026, 9:47:50 AM  
> - **Duration:** 10m 45s  
> - **Exported:** 4/3/2026, 9:58:36 AM  

---

<sub>⏱️ 6s</sub>

### 👤 User

ops 2.9.0 introduced Harness.run_action() which returns an ActionOutput object (or raises ActionFailed), replacing the older pattern of manually triggering action events and inspecting results via the backend. Learn how to use that feature and update this charm to make use of it.

---

<sub>⏱️ 15s</sub>

### ✅ `bash`

**Find test files and check for action patterns**

$ find /tmp/ops-upgrade-experiment/indico-operator__action-testing__C2/tests -name "*.py" | sort && echo "---" && grep -r "run_action\|ActionOutput\|ActionFailed\|begin_with_initial_hooks\|_run\|charm_exec\|action_event" /tmp/ops-upgrade-experiment/indico-operator__action-testing__C2/tests --include="*.py" -l

<details>
<summary>29 lines</summary>

```
/tmp/ops-upgrade-experiment/indico-operator__action-testing__C2/tests/conftest.py
/tmp/ops-upgrade-experiment/indico-operator__action-testing__C2/tests/integration/__init__.py
/tmp/ops-upgrade-experiment/indico-operator__action-testing__C2/tests/integration/conftest.py
/tmp/ops-upgrade-experiment/indico-operator__action-testing__C2/tests/integration/test_actions.py
/tmp/ops-upgrade-experiment/indico-operator__action-testing__C2/tests/integration/test_charm.py
/tmp/ops-upgrade-experiment/indico-operator__action-testing__C2/tests/integration/test_loki.py
/tmp/ops-upgrade-experiment/indico-operator__action-testing__C2/tests/integration/test_s3.py
/tmp/ops-upgrade-experiment/indico-operator__action-testing__C2/tests/integration/test_saml.py
/tmp/ops-upgrade-experiment/indico-operator__action-testing__C2/tests/unit/__init__.py
/tmp/ops-upgrade-experiment/indico-operator__action-testing__C2/tests/unit/conftest.py
/tmp/ops-upgrade-experiment/indico-operator__action-testing__C2/tests/unit/test_on_leader_elected.py
/tmp/ops-upgrade-experiment/indico-operator__action-testing__C2/tests/unit_harness/__init__.py
/tmp/ops-upgrade-experiment/indico-operator__action-testing__C2/tests/unit_harness/conftest.py
/tmp/ops-upgrade-experiment/indico-operator__action-testing__C2/tests/unit_harness/test_actions.py
/tmp/ops-upgrade-experiment/indico-operator__action-testing__C2/tests/unit_harness/test_base.py
/tmp/ops-upgrade-experiment/indico-operator__action-testing__C2/tests/unit_harness/test_core.py
/tmp/ops-upgrade-experiment/indico-operator__action-testing__C2/tests/unit_harness/test_database_observer.py
/tmp/ops-upgrade-experiment/indico-operator__action-testing__C2/tests/unit_harness/test_s3_observer.py
/tmp/ops-upgrade-experiment/indico-operator__action-testing__C2/tests/unit_harness/test_saml_observer.py
/tmp/ops-upgrade-experiment/indico-operator__action-testing__C2/tests/unit_harness/test_smtp_observer.py
/tmp/ops-upgrade-experiment/indico-operator__action-testing__C2/tests/unit_harness/test_state.py
/tmp/ops-upgrade-experiment/indico-operator__action-testing__C2/tests/zap/add_header_request.py
/tmp/ops-upgrade-experiment/indico-operator__action-testing__C2/tests/zap/hook.py
---
/tmp/ops-upgrade-experiment/indico-operator__action-testing__C2/tests/integration/conftest.py
/tmp/ops-upgrade-experiment/indico-operator__action-testing__C2/tests/integration/test_s3.py
/tmp/ops-upgrade-experiment/indico-operator__action-testing__C2/tests/integration/test_actions.py
/tmp/ops-upgrade-experiment/indico-operator__action-testing__C2/tests/unit_harness/test_core.py
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 22s</sub>

### ✅ `bash`

**Read the action test file**

$ cat /tmp/ops-upgrade-experiment/indico-operator__action-testing__C2/tests/unit_harness/test_actions.py

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

<sub>⏱️ 22s</sub>

### ✅ `bash`

**Check action patterns in test_core**

$ grep -n "action\|Action" /tmp/ops-upgrade-experiment/indico-operator__action-testing__C2/tests/unit_harness/test_core.py | head -40

```

<exited with exit code 0>
```


---

<sub>⏱️ 29s</sub>

### ✅ `bash`

**Check action patterns in charm.py**

$ grep -n "action\|Action" /tmp/ops-upgrade-experiment/indico-operator__action-testing__C2/src/charm.py | head -60

<details>
<summary>19 lines</summary>

```
25:from ops.charm import ActionEvent, CharmBase, HookEvent, PebbleReadyEvent, RelationDepartedEvent
91:            self.on.refresh_external_resources_action, self._refresh_external_resources_action
94:        self.framework.observe(self.on.add_admin_action, self._add_admin_action)
95:        self.framework.observe(self.on.anonymize_user_action, self._anonymize_user_action)
836:    def _refresh_external_resources_action(self, event: ActionEvent) -> None:
837:        """Refresh external resources and report action result.
840:            event: Event triggering the refresh action.
898:    def _add_admin_action(self, event: ActionEvent) -> None:
902:            event: Event triggered by the add_admin action
926:                logger.exception("Action add-admin failed: %s", ex.stdout)
933:    def _execute_anonymize_cmd(self, event: ActionEvent) -> Iterator[str]:
937:            event (ActionEvent): Event triggered by the anonymize-user action
954:                    "Action anonymize-user failed: cannot connect to the Indico workload container"
971:                logger.exception("Action anonymize-user failed: %s", ex.stdout)
976:    def _anonymize_user_action(self, event: ActionEvent) -> None:
979:        If find an error, the action will fail. All the results will be set until the error
983:            event: Event triggered by the anonymize-user action
990:            logger.error("Action anonymize-user failed: %s", max_reached_msg)
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 29s</sub>

### ✅ `bash`

**Check ops version and tox unit config**

$ grep -n "ops" /tmp/ops-upgrade-experiment/indico-operator__action-testing__C2/requirements.txt && cat /tmp/ops-upgrade-experiment/indico-operator__action-testing__C2/tox.ini | grep -A5 "unit"

<details>
<summary>21 lines</summary>

```
2:ops>=2.0.0,<3.0.0
envlist = lint, unit, static, coverage-report

[vars]
src_path = {toxinidir}/src/
tst_path = {toxinidir}/tests/
plugins_path = {toxinidir}/indico_rock/plugins/
--
[testenv:unit]
description = Run unit tests
deps =
    cosl
    coverage[toml]
    pytest
    pytest-mock
--
    pytest -v --tb native --ignore={[vars]tst_path}unit --log-cli-level=INFO -s {posargs}

[testenv:src-docs]
allowlist_externals=sh
setenv =
    PYTHONPATH = {toxinidir}:{toxinidir}/lib:{[vars]src_path}
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 39s</sub>

### ✅ `bash`

**Check unit_harness conftest and test_base**

$ cat /tmp/ops-upgrade-experiment/indico-operator__action-testing__C2/tests/unit_harness/conftest.py && echo "---" && cat /tmp/ops-upgrade-experiment/indico-operator__action-testing__C2/tests/unit_harness/test_base.py

<details>
<summary>100 lines</summary>

```
# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

"""Fixtures for unit tests."""

from secrets import token_hex

import pytest

import state


@pytest.fixture(scope="function", name="proxy_config")
def proxy_config_fixture(monkeypatch: pytest.MonkeyPatch):
    """Proxy configuration with authentication and no_proxy values."""
    # Mypy doesn't understand str is supposed to be converted to HttpUrl by Pydantic.
    proxy_config = state.ProxyConfig(
        http_proxy=f"http://testusername:{token_hex(16)}@httptest.internal:3127",  # type: ignore
        https_proxy=f"http://testusername:{token_hex(16)}@httpstest.internal:3127",  # type: ignore
        no_proxy="noproxy.host1,noproxy.host2",
    )
    monkeypatch.setattr(
        state.os,
        "environ",
        {
            "JUJU_CHARM_HTTP_PROXY": str(proxy_config.http_proxy),
            "JUJU_CHARM_HTTPS_PROXY": str(proxy_config.https_proxy),
            "JUJU_CHARM_NO_PROXY": str(proxy_config.no_proxy),
        },
    )
    return proxy_config
---
# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

"""Indico charm unit tests."""

# pylint:disable=protected-access

import unittest
from typing import List

from ops.testing import Harness

from charm import IndicoOperatorCharm


class TestBase(unittest.TestCase):
    """Indico charm unit tests."""

    def setUp(self):
        """Set up test environment."""
        self.harness = Harness(IndicoOperatorCharm)
        self.addCleanup(self.harness.cleanup)
        self.harness.begin()

    def set_up_all_relations(self):
        """Set up all relations for the charm."""
        # pylint: disable=duplicate-code
        self.harness.add_relation(
            "database",
            "postgresql",
            app_data={
                "database": "indico",
                "endpoints": "postgresql-k8s-primary.local:5432",
                "password": "somepass",  # nosec
                "username": "user1",
            },
        )

        self.harness.add_relation("indico-peers", self.harness.charm.app.name)
        redis_broker_relation_id = self.harness.add_relation(
            "redis-broker",
            "redis-broker",
            unit_data={"hostname": "broker-host", "port": "1010"},
            app_data={"leader-host": "broker-host"},
        )
        self.harness.add_relation_unit(redis_broker_relation_id, "redis-broker/1")
        self.harness.update_relation_data(
            redis_broker_relation_id,
            "redis-broker/1",
            {"hostname": "broker-host-1", "port": "1010"},
        )
        redis_cache_relation_id = self.harness.add_relation(
            "redis-cache",
            "redis-cache",
            unit_data={"hostname": "cache-host", "port": "1011"},
            app_data={"leader-host": "cache-host"},
        )
        self.harness.add_relation_unit(redis_cache_relation_id, "redis-cache/1")
        self.harness.update_relation_data(
            redis_cache_relation_id,
            "redis-cache/1",
            {"hostname": "cache-host-1", "port": "1011"},
        )

        self.nginx_route_relation_id = self.harness.add_relation(  # pylint: disable=W0201
            "nginx-route", "ingress"
        )

    def is_ready(self, apps: List[str]):
        """Waiting for all applications to be ready.

        Args:
            apps: List of applications.
        """
        for app_name in apps:
            self.harness.container_pebble_ready(app_name)

    def set_relations_and_leader(self):
        """Set Indico relations, the leader and check container readiness."""
        self.set_up_all_relations()
        self.harness.set_leader(True)
        self.is_ready(
            [
                "indico",
                "indico-nginx",
            ]
        )
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 39s</sub>

### ✅ `bash`

**Read action handler code in charm.py**

$ sed -n '836,1000p' /tmp/ops-upgrade-experiment/indico-operator__action-testing__C2/src/charm.py

<details>
<summary>146 lines</summary>

```
def _refresh_external_resources_action(self, event: ActionEvent) -> None:
        """Refresh external resources and report action result.

        Args:
            event: Event triggering the refresh action.
        """
        results = self._refresh_external_resources(event)
        event.set_results(results)

    def _on_leader_elected(self, _) -> None:
        """Handle leader-elected event."""
        peer_relation = self.model.get_relation("indico-peers")
        secret_value = repr(os.urandom(32))
        if (
            peer_relation
            and not self._has_secrets()
            and not peer_relation.data[self.app].get("secret-key")
        ):
            peer_relation.data[self.app].update({"secret-key": secret_value})
        elif (
            peer_relation
            and self._has_secrets()
            and not peer_relation.data[self.app].get("secret-id")
        ):
            secret = self.app.add_secret({"secret-key": secret_value})
            peer_relation.data[self.app].update({"secret-id": typing.cast(str, secret.id)})
        if peer_relation and not peer_relation.data[self.app].get("celery-unit"):
            peer_relation.data[self.app].update({"celery-unit": self.unit.name})

    def _on_peer_relation_departed(self, event: RelationDepartedEvent) -> None:
        """Handle the peer relation departed event.

        Args:
            event: the event triggering the handler.
        """
        peer_relation = self.model.get_relation("indico-peers")
        if (
            self.unit.is_leader()
            and peer_relation
            and event.departing_unit
            and peer_relation.data[self.app].get("celery-unit") == event.departing_unit.name
        ):
            if self.unit != event.departing_unit:
                peer_relation.data[self.app].update({"celery-unit": self.unit.name})
                container = self.unit.get_container("indico")
                if self._are_relations_ready(event) and container.can_connect():
                    self._config_pebble(container)
            else:
                # Leadership election will select a new celery-unit
                peer_relation.data[self.app].update({"celery-unit": ""})

    def _has_secrets(self) -> bool:
        """Check if current Juju version supports secrets.

        Returns:
            If secrets are supported or not.
        """
        juju_version = JujuVersion.from_environ()
        # Because we're only using secrets in a peer relation we don't need to
        # check if the other end of a relation also supports secrets...
        return juju_version.has_secrets

    def _add_admin_action(self, event: ActionEvent) -> None:
        """Add a new user to Indico.

        Args:
            event: Event triggered by the add_admin action
        """
        container = self.unit.get_container("indico")
        indico_env_config = self._get_indico_env_config_str(container)

        cmd = [
            "/usr/bin/indico",
            "autocreate",
            "admin",
            event.params["email"],
            event.params["password"],
        ]

        if container.can_connect():
            process = container.exec(
                cmd,
                user="indico",
                working_dir="/srv/indico",
                environment=indico_env_config,
            )
            try:
                output = process.wait_output()
                event.set_results({"user": f"{event.params['email']}", "output": output})
            except ExecError as ex:
                logger.exception("Action add-admin failed: %s", ex.stdout)

                event.fail(
                    # Parameter validation errors are printed to stdout
                    f"Failed to create admin {event.params['email']}: {ex.stdout!r}"
                )

    def _execute_anonymize_cmd(self, event: ActionEvent) -> Iterator[str]:
        """Execute anonymize command for each email.

        Args:
            event (ActionEvent): Event triggered by the anonymize-user action

        Yields:
            Iterator[str]: Output of each command execution
        """
        container = self.unit.get_container("indico")
        indico_env_config = self._get_indico_env_config_str(container)
        for email in event.params["email"].split(EMAIL_LIST_SEPARATOR):
            cmd = [
                "/usr/bin/indico",
                "anonymize",
                "user",
                email,
            ]

            if not container.can_connect():
                logger.error(
                    "Action anonymize-user failed: cannot connect to the Indico workload container"
                )
                self.unit.status = WaitingStatus(
                    "Waiting to be able to connect to workload container"
                )
                return

            process = container.exec(
                cmd,
                user="indico",
                working_dir="/srv/indico",
                environment=indico_env_config,
            )
            try:
                out = process.wait_output()
                yield out[0].replace("\n", "")
            except ExecError as ex:
                logger.exception("Action anonymize-user failed: %s", ex.stdout)
                fail_msg = f"Failed to anonymize user {event.params['email']}: {ex.stdout!r}"
                event.fail("Failed to anonymize one or more users, please verify the results.")
                yield fail_msg

    def _anonymize_user_action(self, event: ActionEvent) -> None:
        """Anonymize user in Indico.

        If find an error, the action will fail. All the results will be set until the error
        has happened.

        Args:
            event: Event triggered by the anonymize-user action
        """
        if len(event.params["email"].split(EMAIL_LIST_SEPARATOR)) > EMAIL_LIST_MAX:
            max_reached_msg = (
                "Failed to anonymize user: "
                f"List of more than {EMAIL_LIST_MAX} emails are not allowed"
            )
            logger.error("Action anonymize-user failed: %s", max_reached_msg)
            event.fail(max_reached_msg)
            return
        output_list = list(self._execute_anonymize_cmd(event))
        event.set_results(
            {
                "user": f"{event.params['email']}",
                "output": EMAIL_LIST_SEPARATOR.join(output_list),
            }
        )
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 48s</sub>

### 💬 Copilot

Now I have a clear picture. Let me look at the existing new-style unit tests and the ops docs for `run_action`:

---

<sub>⏱️ 48s</sub>

### ✅ `bash`

**Read new-style unit tests**

$ cat /tmp/ops-upgrade-experiment/indico-operator__action-testing__C2/tests/unit/conftest.py && echo "---" && cat /tmp/ops-upgrade-experiment/indico-operator__action-testing__C2/tests/unit/test_on_leader_elected.py

<details>
<summary>56 lines</summary>

```
# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

"""Fixtures for unit tests."""

import pytest
from ops import pebble, testing


@pytest.fixture(scope="function", name="base_state")
def base_state_fixture():
    """State with container and config file set."""
    pebble_layer = pebble.Layer(
        {
            "summary": "indico layer",
            "description": "pebble config layer for indico",
            "services": {
                "indico": {},
            },
        }
    )
    yield {
        "leader": True,
        "containers": {
            # mypy throws an error because it validates against ops.Container.
            testing.Container(  # type: ignore[call-arg]
                name="indico",
                can_connect=True,
                layers={"indico": pebble_layer},
                service_statuses={"indico": pebble.ServiceStatus.ACTIVE},
            )
        },
    }
---
# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

"""Indico charm unit tests."""

from unittest.mock import MagicMock, patch

import ops
from ops import testing

from charm import IndicoOperatorCharm


@patch.object(ops.JujuVersion, "from_environ")
def test_on_leader_elected_when_secrets_supported(mock_juju_env, base_state: dict):
    """
    arrange: charm created, leader selected and secrets supported
    act: re-trigger the leader elected event
    assert: the peer relation containers the secret-key
    """
    mock_juju_env.return_value = MagicMock(has_secrets=True)
    base_state["relations"] = [testing.PeerRelation("indico-peers")]
    state = testing.State(**base_state)
    context = testing.Context(
        charm_type=IndicoOperatorCharm,
    )

    state = context.run(context.on.leader_elected(), state)

    secret_id = state.get_relations("indico-peers")[0].local_app_data["secret-id"]
    context.run(context.on.leader_elected(), state)

    assert state.get_relations("indico-peers")[0].local_app_data["secret-id"]
    assert secret_id == state.get_relations("indico-peers")[0].local_app_data["secret-id"]
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 48s</sub>

### ✅ `bash`

**Check installed ops version**

$ python3 -c "import ops; print(ops.__version__)" 2>/dev/null || pip show ops 2>/dev/null | grep Version

```
3.7.0
<exited with exit code 0>
```


---

<sub>⏱️ 1m 2s</sub>

### ✅ `bash`

**Check Harness.run_action API**

$ python3 -c "import ops.testing; help(ops.testing.Harness.run_action)" 2>/dev/null | head -30

<details>
<summary>25 lines</summary>

```
Help on function run_action in module ops._private.harness:

run_action(self, action_name: 'str', params: 'dict[str, Any] | None' = None) -> 'ActionOutput'
    Simulates running a charm action, as with ``juju run``.

    Use this only after calling :meth:`begin`.

    Validates that no required parameters are missing, and that additional
    parameters are not provided if that is not permitted. Does not validate
    the types of the parameters - you can use the
    `jsonschema <https://github.com/python-jsonschema/jsonschema>`_ package to
    do this in your tests; for example::

        schema = harness.charm.meta.actions["action-name"].parameters
        try:
            jsonschema.validate(instance=params, schema=schema)
        except jsonschema.ValidationError:
            # Do something about the invalid params.
            ...
        harness.run_action("action-name", params)

    Args:
        action_name: the name of the action to run, as found in ``actions.yaml``.
        params: override the default parameter values found in ``actions.yaml``.
            If a parameter is not in ``params``, or ``params`` is ``None``, then
            the default value from ``actions.yaml`` will be used.

    Raises:
        ActionFailed: if :meth:`ops.ActionEvent.fail` is called. Note that this will
          be raised at the end of the ``run_action`` call, not immediately when
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 1m 2s</sub>

### ✅ `bash`

**Check Context action methods**

$ python3 -c "import ops.testing; print([x for x in dir(ops.testing.Context) if 'action' in x.lower()])"

```
['run_action']
<exited with exit code 0>
```


---

<sub>⏱️ 1m 40s</sub>

### ✅ `bash`

**Get full Harness.run_action docs**

$ python3 -c "import ops.testing; help(ops.testing.Harness.run_action)" 2>/dev/null

<details>
<summary>27 lines</summary>

```
Help on function run_action in module ops._private.harness:

run_action(self, action_name: 'str', params: 'dict[str, Any] | None' = None) -> 'ActionOutput'
    Simulates running a charm action, as with ``juju run``.

    Use this only after calling :meth:`begin`.

    Validates that no required parameters are missing, and that additional
    parameters are not provided if that is not permitted. Does not validate
    the types of the parameters - you can use the
    `jsonschema <https://github.com/python-jsonschema/jsonschema>`_ package to
    do this in your tests; for example::

        schema = harness.charm.meta.actions["action-name"].parameters
        try:
            jsonschema.validate(instance=params, schema=schema)
        except jsonschema.ValidationError:
            # Do something about the invalid params.
            ...
        harness.run_action("action-name", params)

    Args:
        action_name: the name of the action to run, as found in ``actions.yaml``.
        params: override the default parameter values found in ``actions.yaml``.
            If a parameter is not in ``params``, or ``params`` is ``None``, then
            the default value from ``actions.yaml`` will be used.

    Raises:
        ActionFailed: if :meth:`ops.ActionEvent.fail` is called. Note that this will
          be raised at the end of the ``run_action`` call, not immediately when
          :code:`fail()` is called, to match the run-time behaviour.
(END)
<command with shellId: 11 is still running after 30 seconds. The command is still running. Check the output above - if it looks like the command is waiting for input, use write_bash to provide it. Otherwise, use read_bash to continue waiting for output, or stop_bash to stop it.>
```

</details>


---

<sub>⏱️ 1m 11s</sub>

### ✅ `bash`

**Check ActionOutput and ActionFailed APIs**

$ python3 -c "from ops.testing import ActionFailed, ActionOutput; help(ActionOutput)" 2>/dev/null | head -30 && python3 -c "from ops.testing import ActionFailed; help(ActionFailed)" 2>/dev/null | head -20

<details>
<summary>49 lines</summary>

```
Help on class ActionOutput in module ops._private.harness:

class ActionOutput(builtins.object)
 |  ActionOutput(logs: 'list[str]', results: 'dict[str, Any]') -> None
 |
 |  Contains the logs and results from a :meth:`Harness.run_action` call.
 |
 |  Methods defined here:
 |
 |  __delattr__(self, name)
 |      Implement delattr(self, name).
 |
 |  __eq__(self, other)
 |      Return self==value.
 |
 |  __hash__(self)
 |      Return hash(self).
 |
 |  __init__(self, logs: 'list[str]', results: 'dict[str, Any]') -> None
 |      Initialize self.  See help(type(self)) for accurate signature.
 |
 |  __repr__(self)
 |      Return repr(self).
 |
 |  __setattr__(self, name, value)
 |      Implement setattr(self, name, value).
 |
 |  ----------------------------------------------------------------------
 |  Data descriptors defined here:
 |
Help on class ActionFailed in module ops._private.harness:

class ActionFailed(builtins.Exception)
 |  ActionFailed(message: 'str', output: 'ActionOutput | None' = None, *, state: 'State | None' = None)
 |
 |  Raised when :code:`event.fail()` is called during an action handler.
 |
 |  Method resolution order:
 |      ActionFailed
 |      builtins.Exception
 |      builtins.BaseException
 |      builtins.object
 |
 |  Methods defined here:
 |
 |  __init__(self, message: 'str', output: 'ActionOutput | None' = None, *, state: 'State | None' = None)
 |      Initialize self.  See help(type(self)) for accurate signature.
 |
 |  __str__(self)
 |      Return str(self).
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 1m 44s</sub>

### ✅ `stop_bash`

<details>
<summary>Arguments</summary>

```json
{
  "shellId": "11"
}
```

</details>

```
<command with id: 11 stopped>
```


---

<sub>⏱️ 1m 55s</sub>

### 💬 Copilot

Now I have a full picture. Let me check the `_refresh_external_resources_action` handler and the `actions.yaml` file:

---

<sub>⏱️ 1m 55s</sub>

### ✅ `bash`

**Read actions.yaml**

$ cat /tmp/ops-upgrade-experiment/indico-operator__action-testing__C2/actions.yaml

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

<sub>⏱️ 1m 55s</sub>

### ✅ `bash`

**Check refresh action tests in test_core**

$ grep -n "_refresh_external_resources\b" /tmp/ops-upgrade-experiment/indico-operator__action-testing__C2/tests/unit_harness/test_core.py | head -20

```

<exited with exit code 0>
```


---

<sub>⏱️ 2m 2s</sub>

### ✅ `bash`

**Check refresh action in test_core**

$ grep -n "refresh_external_resources\|run_action\|ActionOutput\|ActionFailed" /tmp/ops-upgrade-experiment/indico-operator__action-testing__C2/tests/unit_harness/test_core.py | head -20

```

<exited with exit code 0>
```


---

<sub>⏱️ 2m 9s</sub>

### ✅ `bash`

**Check refresh action tests**

$ grep -n "refresh_external_resources\|ActionOutput\|ActionFailed" /tmp/ops-upgrade-experiment/indico-operator__action-testing__C2/tests/unit_harness/test_actions.py

```
25:    def test_refresh_external_resources_when_customization_and_plugins_set(
46:            charm._refresh_external_resources(MagicMock())
<exited with exit code 0>
```


---

<sub>⏱️ 2m 31s</sub>

### 💬 Copilot

Let me look at `_refresh_external_resources` in detail:

---

<sub>⏱️ 2m 32s</sub>

### ✅ `bash`

**Find refresh_external_resources method**

$ grep -n "_refresh_external_resources" /tmp/ops-upgrade-experiment/indico-operator__action-testing__C2/src/charm.py

<details>
<summary>6 lines</summary>

```
91:            self.on.refresh_external_resources_action, self._refresh_external_resources_action
93:        # self.framework.observe(self.on.update_status, self._refresh_external_resources)
807:    def _refresh_external_resources(self, _) -> Dict:
836:    def _refresh_external_resources_action(self, event: ActionEvent) -> None:
842:        results = self._refresh_external_resources(event)
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 2m 38s</sub>

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/indico-operator__action-testing__C2/src/charm.py.**

/tmp/ops-upgrade-experiment/indico-operator__action-testing__C2/src/charm.py (lines 807-845)

<details>
<summary>39 lines</summary>

```
807.     def _refresh_external_resources(self, _) -> Dict:
808.         """Pull changes from the remote repository and upgrade external plugins.
809. 
810.         Returns:
811.             Dictionary containing the execution results for each of the operations executed.
812.         """
813.         results = {
814.             "customization-changes": False,
815.             "plugin-updates": [],
816.         }
817.         container = self.unit.get_container("indico")
818.         if container.can_connect():
819.             self._download_customization_changes(container)
820.             if self.config["customization_sources_url"]:
821.                 logging.debug("Pulling changes from %s", self.config["customization_sources_url"])
822.                 self._exec_cmd_in_custom_dir(
823.                     container,
824.                     ["git", "pull"],
825.                 )
826.                 logging.debug("Reloading uWSGI")
827.                 self._exec_cmd_in_custom_dir(container, ["touch", UWSGI_TOUCH_RELOAD])
828.                 results["customization-changes"] = True
829.             if self.config["external_plugins"]:
830.                 logging.debug("Upgrading external plugins %s", self.config["external_plugins"])
831.                 plugins = typing.cast(str, self.config["external_plugins"]).split(",")
832.                 self._install_plugins(container, plugins)
833.                 results["plugin-updates"] = plugins
834.         return results
835. 
836.     def _refresh_external_resources_action(self, event: ActionEvent) -> None:
837.         """Refresh external resources and report action result.
838. 
839.         Args:
840.             event: Event triggering the refresh action.
841.         """
842.         results = self._refresh_external_resources(event)
843.         event.set_results(results)
844. 
845.     def _on_leader_elected(self, _) -> None:
```

</details>


---

<sub>⏱️ 5m 44s</sub>

### ✅ `bash`

**Check EMAIL_LIST_SEPARATOR constant**

$ grep -n "EMAIL_LIST_SEPARATOR\|EMAIL_LIST_MAX" /tmp/ops-upgrade-experiment/indico-operator__action-testing__C2/src/charm.py | head -5

<details>
<summary>6 lines</summary>

```
41:EMAIL_LIST_MAX = 50
42:EMAIL_LIST_SEPARATOR = ","
944:        for email in event.params["email"].split(EMAIL_LIST_SEPARATOR):
985:        if len(event.params["email"].split(EMAIL_LIST_SEPARATOR)) > EMAIL_LIST_MAX:
988:                f"List of more than {EMAIL_LIST_MAX} emails are not allowed"
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 6m 22s</sub>

### 💬 Copilot

Now let me run the existing tests to understand the baseline:

---

<sub>⏱️ 6m 25s</sub>

### ✅ `bash`

**Run existing action tests**

$ cd /tmp/ops-upgrade-experiment/indico-operator__action-testing__C2 && pip install tox -q 2>/dev/null; tox -e unit -- tests/unit_harness/test_actions.py -v 2>&1 | tail -30

<details>
<summary>28 lines</summary>

```
/tmp/ops-upgrade-experiment/indico-operator__action-testing__C2/tests/unit_harness/test_base.py:21: PendingDeprecationWarning: Harness is deprecated. For the recommended approach, see: https://ops.readthedocs.io/en/latest/howto/write-unit-tests-for-a-charm.html
    self.harness = Harness(IndicoOperatorCharm)

tests/unit_harness/test_actions.py::TestActions::test_add_admin
tests/unit_harness/test_actions.py::TestActions::test_add_admin_fail
tests/unit_harness/test_actions.py::TestActions::test_refresh_external_resources_when_customization_and_plugins_set
  /tmp/ops-upgrade-experiment/indico-operator__action-testing__C2/lib/charms/data_platform_libs/v0/data_interfaces.py:1160: DeprecationWarning: JujuVersion.from_environ() is deprecated, use self.model.juju_version instead
    self._jujuversion = JujuVersion.from_environ()

tests/unit_harness/test_actions.py: 13 warnings
  /tmp/ops-upgrade-experiment/indico-operator__action-testing__C2/src/charm.py:893: DeprecationWarning: JujuVersion.from_environ() is deprecated, use self.model.juju_version instead
    juju_version = JujuVersion.from_environ()

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
======================== 7 passed, 23 warnings in 0.24s ========================
unit: commands[1]> coverage report
Name                       Stmts   Miss Branch BrPart  Cover   Missing
----------------------------------------------------------------------
src/charm.py                 357     60     80     17    78%   83-85, 162-165, 176, 209-210, 408, 422-423, 544-546, 587-591, 602-603, 608-645, 673, 691-697, 714-715, 792->exit, 818->834, 820->829, 829->834, 842-843, 855-861, 862->exit, 871-885, 915->exit, 953-959
src/database_observer.py      32      2      4      1    92%   54, 73
src/s3_observer.py            17      2      0      0    88%   38, 43
src/saml_observer.py          14      1      0      0    93%   39
src/smtp_observer.py          15      1      0      0    93%   40
src/state.py                  73     13      8      2    77%   38, 67, 92-98, 193-203, 231-233
----------------------------------------------------------------------
TOTAL                        508     79     92     20    80%
Coverage failure: total of 80 is less than fail-under=97
unit: exit 2 (0.09 seconds) /tmp/ops-upgrade-experiment/indico-operator__action-testing__C2> coverage report pid=64915
  unit: FAIL code 2 (2.25=setup[1.14]+cmd[1.03,0.09] seconds)
  evaluation failed :( (2.27 seconds)
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 6m 48s</sub>

### ✅ `bash`

**Read full tox.ini**

$ cat /tmp/ops-upgrade-experiment/indico-operator__action-testing__C2/tox.ini

<details>
<summary>169 lines</summary>

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
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 7m 2s</sub>

### ✅ `bash`

**Check ops version in tox unit env**

$ python3 -m pip show ops 2>/dev/null | grep Version && ls /tmp/ops-upgrade-experiment/indico-operator__action-testing__C2/.tox/unit/lib/python*/site-packages/ops 2>/dev/null | head -3 || echo "tox env not found"

```
Version: 3.7.0
__init__.py
__pycache__
_main.py
<exited with exit code 0>
```


---

<sub>⏱️ 7m 2s</sub>

### ✅ `bash`

**Verify ActionFailed and ActionOutput work**

$ python3 -c "import ops.testing; from ops.testing import ActionFailed, ActionOutput; print('ActionFailed:', ActionFailed.__module__); o = ActionOutput(logs=[], results={}); print('ActionOutput.results:', o.results)"

```
ActionFailed: ops._private.harness
ActionOutput.results: {}
<exited with exit code 0>
```


---

<sub>⏱️ 7m 24s</sub>

### 💬 Copilot

Now I have everything I need. Let me implement the changes to `tests/unit_harness/test_actions.py`:

---

<sub>⏱️ 7m 24s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/indico-operator__action-testing__C2/tests/unit_harness/test_actions.py.**

/tmp/ops-upgrade-experiment/indico-operator__action-testing__C2/tests/unit_harness/test_actions.py

```
File /tmp/ops-upgrade-experiment/indico-operator__action-testing__C2/tests/unit_harness/test_actions.py updated with changes.
```


---

<sub>⏱️ 7m 31s</sub>

### 💬 Copilot

Now update `test_refresh_external_resources_when_customization_and_plugins_set`:

---

<sub>⏱️ 7m 31s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/indico-operator__action-testing__C2/tests/unit_harness/test_actions.py.**

/tmp/ops-upgrade-experiment/indico-operator__action-testing__C2/tests/unit_harness/test_actions.py

```
File /tmp/ops-upgrade-experiment/indico-operator__action-testing__C2/tests/unit_harness/test_actions.py updated with changes.
```


---

<sub>⏱️ 7m 39s</sub>

### 💬 Copilot

Now update `test_add_admin`:

---

<sub>⏱️ 7m 39s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/indico-operator__action-testing__C2/tests/unit_harness/test_actions.py.**

/tmp/ops-upgrade-experiment/indico-operator__action-testing__C2/tests/unit_harness/test_actions.py

```
File /tmp/ops-upgrade-experiment/indico-operator__action-testing__C2/tests/unit_harness/test_actions.py updated with changes.
```


---

<sub>⏱️ 7m 47s</sub>

### 💬 Copilot

Now view the test_add_admin section to fix the `indico_env_config` reference that's still in the `assert_any_call`:

---

<sub>⏱️ 7m 47s</sub>

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/indico-operator__action-testing__C2/tests/unit_harness/test_actions.py.**

/tmp/ops-upgrade-experiment/indico-operator__action-testing__C2/tests/unit_harness/test_actions.py (lines 62-110)

<details>
<summary>49 lines</summary>

```
62.                 environment={},
63.             )
64.             expected_logs = [
65.                 "INFO:charm:About to run: pip install --upgrade "
66.                 "-c /tmp/constraints-123456.txt "
67.                 "git+https://example.git/#subdirectory=themes_cern",
68.                 "INFO:charm:Output was: ",
69.             ]
70.             assert logger.output == expected_logs
71. 
72.     @patch.object(Container, "exec")
73.     def test_add_admin(self, mock_exec):
74.         """
75.         arrange: an email and a password
76.         act: when the _on_add_admin_action method is executed
77.         assert: the indico command to add the user is executed with the appropriate parameters.
78.         """
79.         mock_exec.return_value = MagicMock(wait_output=MagicMock(return_value=("", None)))
80. 
81.         self.set_relations_and_leader()
82.         self.harness.disable_hooks()
83. 
84.         container = self.harness.model.unit.get_container("indico")
85. 
86.         charm: IndicoOperatorCharm = typing.cast(IndicoOperatorCharm, self.harness.charm)
87. 
88.         email = "sample@email.com"
89.         password = token_hex(16)
90.         expected_cmd = [
91.             "/usr/bin/indico",
92.             "autocreate",
93.             "admin",
94.             email,
95.             password,
96.         ]
97. 
98.         self.harness.run_action("add-admin", {"email": email, "password": password})
99. 
100.         mock_exec.assert_any_call(
101.             expected_cmd,
102.             user="indico",
103.             working_dir="/srv/indico",
104.             environment=indico_env_config,
105.         )
106. 
107.     @patch.object(Container, "exec")
108.     def test_add_admin_fail(self, mock_exec):
109.         """
110.         arrange: an email and a password
```

</details>


---

<sub>⏱️ 7m 59s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/indico-operator__action-testing__C2/tests/unit_harness/test_actions.py.**

/tmp/ops-upgrade-experiment/indico-operator__action-testing__C2/tests/unit_harness/test_actions.py

```
File /tmp/ops-upgrade-experiment/indico-operator__action-testing__C2/tests/unit_harness/test_actions.py updated with changes.
```


---

<sub>⏱️ 8m 3s</sub>

### 💬 Copilot

Now update `test_add_admin_fail` - replace the event mock and direct method call with `run_action`:

---

<sub>⏱️ 8m 3s</sub>

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/indico-operator__action-testing__C2/tests/unit_harness/test_actions.py.**

/tmp/ops-upgrade-experiment/indico-operator__action-testing__C2/tests/unit_harness/test_actions.py (lines 107-200)

<details>
<summary>94 lines</summary>

```
107.     @patch.object(Container, "exec")
108.     def test_add_admin_fail(self, mock_exec):
109.         """
110.         arrange: an email and a password
111.         act: when the _on_add_admin_action method is executed
112.         assert: the indico command to add the user is executed with the appropriate parameters.
113.         """
114.         mock_wo = MagicMock(
115.             return_value=("", None),
116.         )
117. 
118.         stdout_mock = "CRASH"
119. 
120.         # I'm disabling unused-argument here because some could be passed to the mock
121.         def mock_wo_side_effect(*args, **kwargs):  # pylint: disable=unused-argument
122.             """Mock wo side effect.
123. 
124.             Args:
125.                 args: Variable list of positional arguments passed to the parent constructor.
126.                 kwargs: a `dict` of the extra arguments passed to the function.
127. 
128.             Returns:
129.                 unittest.mock DEFAULT built-in.
130. 
131.             Raises:
132.                 ExecError: Execution error fired if conditions are met.
133.             """
134.             if isinstance(mock_wo.cmd, list) and "autocreate" in mock_wo.cmd:
135.                 raise ExecError(command=mock_wo.cmd, exit_code=42, stdout=stdout_mock, stderr="")
136.             return DEFAULT
137. 
138.         mock_wo.side_effect = mock_wo_side_effect
139. 
140.         # I'm disabling unused-argument here because some could be passed to the mock
141.         def mock_exec_side_effect(*args, **kwargs):  # pylint: disable=unused-argument
142.             """Mock execution side effect.
143. 
144.             Args:
145.                 args: Variable list of positional arguments passed to the parent constructor.
146.                 kwargs: a `dict` of the extra arguments passed to the function.
147. 
148.             Returns:
149.                 unittest.mock DEFAULT built-in.
150.             """
151.             mock_wo.cmd = args[0]
152.             return DEFAULT
153. 
154.         mock_exec.side_effect = mock_exec_side_effect
155.         mock_exec.return_value = MagicMock(
156.             wait_output=mock_wo,
157.         )
158. 
159.         self.set_relations_and_leader()
160.         self.harness.disable_hooks()
161. 
162.         container = self.harness.model.unit.get_container("indico")
163. 
164.         charm: IndicoOperatorCharm = typing.cast(IndicoOperatorCharm, self.harness.charm)
165. 
166.         email = "sample@email.com"
167.         password = token_hex(16)
168.         event = MagicMock(spec=ActionEvent)
169.         event.params = {
170.             "email": email,
171.             "password": password,
172.         }
173. 
174.         def event_store_failure(failure_message: str) -> None:
175.             """Define a failure message for the event.
176. 
177.             Args:
178.                 failure_message: failure message content to be defined.
179.             """
180.             event.fail_message = failure_message
181. 
182.         event.fail = event_store_failure
183. 
184.         indico_env_config = charm._get_indico_env_config_str(container)
185.         expected_cmd = [
186.             "/usr/bin/indico",
187.             "autocreate",
188.             "admin",
189.             email,
190.             password,
191.         ]
192. 
193.         charm._add_admin_action(event)
194.         assert event.fail_message == f"Failed to create admin {email}: '{stdout_mock}'"
195. 
196.         mock_exec.assert_any_call(
197.             expected_cmd,
198.             user="indico",
199.             working_dir="/srv/indico",
200.             environment=indico_env_config,
```

</details>


---

<sub>⏱️ 8m 10s</sub>

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/indico-operator__action-testing__C2/tests/unit_harness/test_actions.py.**

/tmp/ops-upgrade-experiment/indico-operator__action-testing__C2/tests/unit_harness/test_actions.py (lines 200-220)

<details>
<summary>21 lines</summary>

```
200.             environment=indico_env_config,
201.         )
202. 
203.     def _set_indico(self) -> IndicoOperatorCharm:
204.         """Set Indico Charm
205. 
206.         Returns:
207.             IndicoOperatorCharm: Indico charm configured
208.         """
209.         charm: IndicoOperatorCharm = typing.cast(IndicoOperatorCharm, self.harness.charm)
210.         charm._get_installed_plugins = MagicMock(return_value="")
211.         charm._get_indico_secret_key_from_relation = MagicMock(return_value="")
212.         self.harness.container_pebble_ready("indico")
213.         return charm
214. 
215.     def _anonymize_user(self, emails: str, mock_event: MagicMock, mock_exec: MagicMock):
216.         """Execute anonymize user action
217. 
218.         Args:
219.             emails: email list parameter to be used
220.             mock_event (MagicMock): event mock
```

</details>


---

<sub>⏱️ 8m 18s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/indico-operator__action-testing__C2/tests/unit_harness/test_actions.py.**

/tmp/ops-upgrade-experiment/indico-operator__action-testing__C2/tests/unit_harness/test_actions.py

```
File /tmp/ops-upgrade-experiment/indico-operator__action-testing__C2/tests/unit_harness/test_actions.py updated with changes.
```


---

<sub>⏱️ 8m 26s</sub>

### 💬 Copilot

Now remove the unused `container` and `charm` lines in `test_add_admin_fail` that are now duplicated:

---

<sub>⏱️ 8m 26s</sub>

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/indico-operator__action-testing__C2/tests/unit_harness/test_actions.py.**

/tmp/ops-upgrade-experiment/indico-operator__action-testing__C2/tests/unit_harness/test_actions.py (lines 154-205)

<details>
<summary>52 lines</summary>

```
154.         mock_exec.side_effect = mock_exec_side_effect
155.         mock_exec.return_value = MagicMock(
156.             wait_output=mock_wo,
157.         )
158. 
159.         self.set_relations_and_leader()
160.         self.harness.disable_hooks()
161. 
162.         container = self.harness.model.unit.get_container("indico")
163. 
164.         charm: IndicoOperatorCharm = typing.cast(IndicoOperatorCharm, self.harness.charm)
165. 
166.         email = "sample@email.com"
167.         password = token_hex(16)
168.         container = self.harness.model.unit.get_container("indico")
169.         charm: IndicoOperatorCharm = typing.cast(IndicoOperatorCharm, self.harness.charm)
170.         indico_env_config = charm._get_indico_env_config_str(container)
171.         expected_cmd = [
172.             "/usr/bin/indico",
173.             "autocreate",
174.             "admin",
175.             email,
176.             password,
177.         ]
178. 
179.         with self.assertRaises(ActionFailed) as cm:
180.             self.harness.run_action("add-admin", {"email": email, "password": password})
181.         self.assertEqual(cm.exception.message, f"Failed to create admin {email}: '{stdout_mock}'")
182. 
183.         mock_exec.assert_any_call(
184.             expected_cmd,
185.             user="indico",
186.             working_dir="/srv/indico",
187.             environment=indico_env_config,
188.         )
189. 
190.     def _set_indico(self) -> IndicoOperatorCharm:
191.         """Set Indico Charm
192. 
193.         Returns:
194.             IndicoOperatorCharm: Indico charm configured
195.         """
196.         charm: IndicoOperatorCharm = typing.cast(IndicoOperatorCharm, self.harness.charm)
197.         charm._get_installed_plugins = MagicMock(return_value="")
198.         charm._get_indico_secret_key_from_relation = MagicMock(return_value="")
199.         self.harness.container_pebble_ready("indico")
200.         return charm
201. 
202.     def _anonymize_user(self, emails: str, mock_event: MagicMock, mock_exec: MagicMock):
203.         """Execute anonymize user action
204. 
205.         Args:
```

</details>


---

<sub>⏱️ 8m 35s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/indico-operator__action-testing__C2/tests/unit_harness/test_actions.py.**

/tmp/ops-upgrade-experiment/indico-operator__action-testing__C2/tests/unit_harness/test_actions.py

```
File /tmp/ops-upgrade-experiment/indico-operator__action-testing__C2/tests/unit_harness/test_actions.py updated with changes.
```


---

<sub>⏱️ 8m 41s</sub>

### 💬 Copilot

Now update the `_anonymize_user` helper method and the tests that use it:

---

<sub>⏱️ 8m 41s</sub>

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/indico-operator__action-testing__C2/tests/unit_harness/test_actions.py.**

/tmp/ops-upgrade-experiment/indico-operator__action-testing__C2/tests/unit_harness/test_actions.py (lines 195-285)

<details>
<summary>91 lines</summary>

```
195.         self.harness.container_pebble_ready("indico")
196.         return charm
197. 
198.     def _anonymize_user(self, emails: str, mock_event: MagicMock, mock_exec: MagicMock):
199.         """Execute anonymize user action
200. 
201.         Args:
202.             emails: email list parameter to be used
203.             mock_event (MagicMock): event mock
204.             mock_exec (MagicMock): Container exec mock
205.         """
206.         charm = self._set_indico()
207.         charm._anonymize_user_action(mock_event)
208. 
209.         def validate_command(email: str):
210.             """Check if the command was called.
211. 
212.             Args:
213.                 email: email parameter to be used
214.             """
215.             # Check if command was called
216.             expected_cmd = [
217.                 "/usr/bin/indico",
218.                 "anonymize",
219.                 "user",
220.                 email,
221.             ]
222.             container = self.harness.model.unit.get_container("indico")
223.             indico_env_config = charm._get_indico_env_config_str(container)
224.             mock_exec.assert_any_call(
225.                 expected_cmd,
226.                 user="indico",
227.                 working_dir="/srv/indico",
228.                 environment=indico_env_config,
229.             )
230. 
231.         for email in emails.split(","):
232.             validate_command(email)
233. 
234.         # Check if event results was properly set
235.         mock_event.set_results.assert_called_with({"user": f"{emails}", "output": f"{emails}"})
236. 
237.     @patch.object(Container, "exec")
238.     def test_anonymize_user(self, mock_exec):
239.         """
240.         arrange: an email
241.         act: when the _on_anonymize_user_action method is executed
242.         assert: the indico command to anonymize the user is executed with the appropriate
243.             parameters and the event results is set as expected
244.         """
245.         email = token_hex(16)
246.         mock_exec.return_value = MagicMock(wait_output=MagicMock(return_value=(f"{email}", None)))
247.         mock_event = MagicMock(spec=ActionEvent)
248.         mock_event.params = {
249.             "email": email,
250.         }
251.         self._anonymize_user(email, mock_event, mock_exec)
252. 
253.     def _generate_emails_mock(self, emails: str) -> typing.Iterator[MagicMock]:
254.         """Generate list of mocks accordingly to list of emails
255. 
256.         Args:
257.             emails (str): list of emails
258. 
259.         Yields:
260.             Iterator[MagicMock]: Mock of exec that returns email
261.         """
262.         for email in emails.split(EMAIL_LIST_SEPARATOR):
263.             wait_output = MagicMock(return_value=(email, None))
264.             yield MagicMock(wait_output=wait_output)
265. 
266.     @patch.object(Container, "exec")
267.     def test_anonymize_user_list(self, mock_exec):
268.         """
269.         arrange: an list of 5 emails
270.         act: when the _on_anonymize_user_action method is executed
271.         assert: the indico command to anonymize the user is executed with the appropriate
272.             parameters and the event results is set as expected
273.         """
274.         emails = EMAIL_LIST_SEPARATOR.join([token_hex(16) for _ in range(5)])
275.         mock_event = MagicMock(spec=ActionEvent)
276.         mock_event.params = {
277.             "email": emails,
278.         }
279.         mock_exec.side_effect = list(self._generate_emails_mock(emails))
280.         self._anonymize_user(emails, mock_event, mock_exec)
281. 
282.     @patch.object(Container, "exec")
283.     def test_anonymize_user_maximum_reached(self, mock_exec):
284.         """
285.         arrange: an list of 51 emails
```

</details>


---

<sub>⏱️ 8m 52s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/indico-operator__action-testing__C2/tests/unit_harness/test_actions.py.**

/tmp/ops-upgrade-experiment/indico-operator__action-testing__C2/tests/unit_harness/test_actions.py

```
File /tmp/ops-upgrade-experiment/indico-operator__action-testing__C2/tests/unit_harness/test_actions.py updated with changes.
```


---

<sub>⏱️ 9m 0s</sub>

### 💬 Copilot

Now update `test_anonymize_user` and `test_anonymize_user_list` to remove `mock_event`:

---

<sub>⏱️ 9m 0s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/indico-operator__action-testing__C2/tests/unit_harness/test_actions.py.**

/tmp/ops-upgrade-experiment/indico-operator__action-testing__C2/tests/unit_harness/test_actions.py

```
File /tmp/ops-upgrade-experiment/indico-operator__action-testing__C2/tests/unit_harness/test_actions.py updated with changes.
```


---

<sub>⏱️ 9m 5s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/indico-operator__action-testing__C2/tests/unit_harness/test_actions.py.**

/tmp/ops-upgrade-experiment/indico-operator__action-testing__C2/tests/unit_harness/test_actions.py

```
File /tmp/ops-upgrade-experiment/indico-operator__action-testing__C2/tests/unit_harness/test_actions.py updated with changes.
```


---

<sub>⏱️ 9m 10s</sub>

### 💬 Copilot

Now update `test_anonymize_user_maximum_reached` and `test_anonymize_user_fail`:

---

<sub>⏱️ 9m 10s</sub>

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/indico-operator__action-testing__C2/tests/unit_harness/test_actions.py.**

/tmp/ops-upgrade-experiment/indico-operator__action-testing__C2/tests/unit_harness/test_actions.py (lines 271-360)

<details>
<summary>78 lines</summary>

```
271.     @patch.object(Container, "exec")
272.     def test_anonymize_user_maximum_reached(self, mock_exec):
273.         """
274.         arrange: an list of 51 emails
275.         act: when the _on_anonymize_user_action method is executed
276.         assert: the indico command to anonymize the user is executed with the appropriate
277.             parameters and the event results is set as expected
278.         """
279.         charm = self._set_indico()
280.         emails = EMAIL_LIST_SEPARATOR.join([token_hex(16) for _ in range(EMAIL_LIST_MAX + 1)])
281.         mock_event = MagicMock(spec=ActionEvent)
282.         mock_event.params = {
283.             "email": emails,
284.         }
285.         mock_exec.return_value = MagicMock(wait_output=MagicMock(return_value=("", None)))
286. 
287.         charm._anonymize_user_action(mock_event)
288.         expected_argument = (
289.             f"Failed to anonymize user: List of more than {EMAIL_LIST_MAX} emails are not allowed"
290.         )
291.         # Pylint does not understand that the mock supports this call
292.         mock_event.fail.assert_called_with(expected_argument)  # pylint: disable=no-member
293. 
294.     @patch.object(Container, "exec")
295.     def test_anonymize_user_fail(self, mock_exec):
296.         """
297.         arrange: an email
298.         act: when the _on_anonymize_user_action method is executed
299.         assert: the indico command to anonymize the user is executed with the appropriate
300.             parameters and the event results is set as expected
301.         """
302.         charm = self._set_indico()
303. 
304.         # Set Mock
305.         email = token_hex(16)
306.         error_msg = "Execution error"
307.         expected_cmd = [
308.             "/usr/bin/indico",
309.             "anonymize",
310.             "user",
311.             email,
312.         ]
313.         expected_exception = ExecError(
314.             command=" ".join(expected_cmd), exit_code=42, stdout=f"{error_msg}", stderr=""
315.         )
316.         wait_output = MagicMock(side_effect=expected_exception)
317.         mock_exec.return_value = MagicMock(wait_output=wait_output)
318.         # Set and trigger the event
319.         mock_event = MagicMock(spec=ActionEvent)
320.         mock_event.params = {
321.             "email": email,
322.         }
323. 
324.         charm._anonymize_user_action(mock_event)
325. 
326.         # Check if command was called
327.         container = self.harness.model.unit.get_container("indico")
328.         indico_env_config = charm._get_indico_env_config_str(container)
329.         mock_exec.assert_any_call(
330.             expected_cmd,
331.             user="indico",
332.             working_dir="/srv/indico",
333.             environment=indico_env_config,
334.         )
335. 
336.         # Check if event fail was properly set
337.         expected_argument = "Failed to anonymize one or more users, please verify the results."
338.         # Pylint does not understand that the mock supports this call
339.         mock_event.fail.assert_called_with(expected_argument)  # pylint: disable=no-member
340. 
341.         # Check if event results was properly set
342.         mock_event.set_results.assert_called_with(
343.             {
344.                 "user": f"{email}",
345.                 "output": f"Failed to anonymize user {email}: '{error_msg}'",
346.             }
347.         )
348.
```

</details>


---

<sub>⏱️ 9m 27s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/indico-operator__action-testing__C2/tests/unit_harness/test_actions.py.**

/tmp/ops-upgrade-experiment/indico-operator__action-testing__C2/tests/unit_harness/test_actions.py

```
File /tmp/ops-upgrade-experiment/indico-operator__action-testing__C2/tests/unit_harness/test_actions.py updated with changes.
```


---

<sub>⏱️ 9m 34s</sub>

### 💬 Copilot

Now also update the test docstrings that still refer to the old method names, and fix the `test_add_admin` docstring:

---

<sub>⏱️ 9m 34s</sub>

### ❌ `edit`

**edit the file at /tmp/ops-upgrade-experiment/indico-operator__action-testing__C2/tests/unit_harness/test_actions.py.**

/tmp/ops-upgrade-experiment/indico-operator__action-testing__C2/tests/unit_harness/test_actions.py

```
Multiple matches found
```


---

<sub>⏱️ 9m 39s</sub>

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/indico-operator__action-testing__C2/tests/unit_harness/test_actions.py.**

/tmp/ops-upgrade-experiment/indico-operator__action-testing__C2/tests/unit_harness/test_actions.py (lines 72-115)

<details>
<summary>44 lines</summary>

```
72.     @patch.object(Container, "exec")
73.     def test_add_admin(self, mock_exec):
74.         """
75.         arrange: an email and a password
76.         act: when the _on_add_admin_action method is executed
77.         assert: the indico command to add the user is executed with the appropriate parameters.
78.         """
79.         mock_exec.return_value = MagicMock(wait_output=MagicMock(return_value=("", None)))
80. 
81.         self.set_relations_and_leader()
82.         self.harness.disable_hooks()
83. 
84.         container = self.harness.model.unit.get_container("indico")
85.         charm: IndicoOperatorCharm = typing.cast(IndicoOperatorCharm, self.harness.charm)
86.         indico_env_config = charm._get_indico_env_config_str(container)
87. 
88.         email = "sample@email.com"
89.         password = token_hex(16)
90.         expected_cmd = [
91.             "/usr/bin/indico",
92.             "autocreate",
93.             "admin",
94.             email,
95.             password,
96.         ]
97. 
98.         self.harness.run_action("add-admin", {"email": email, "password": password})
99. 
100.         mock_exec.assert_any_call(
101.             expected_cmd,
102.             user="indico",
103.             working_dir="/srv/indico",
104.             environment=indico_env_config,
105.         )
106. 
107.     @patch.object(Container, "exec")
108.     def test_add_admin_fail(self, mock_exec):
109.         """
110.         arrange: an email and a password
111.         act: when the _on_add_admin_action method is executed
112.         assert: the indico command to add the user is executed with the appropriate parameters.
113.         """
114.         mock_wo = MagicMock(
115.             return_value=("", None),
```

</details>


---

<sub>⏱️ 9m 46s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/indico-operator__action-testing__C2/tests/unit_harness/test_actions.py.**

/tmp/ops-upgrade-experiment/indico-operator__action-testing__C2/tests/unit_harness/test_actions.py

```
File /tmp/ops-upgrade-experiment/indico-operator__action-testing__C2/tests/unit_harness/test_actions.py updated with changes.
```


---

<sub>⏱️ 9m 54s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/indico-operator__action-testing__C2/tests/unit_harness/test_actions.py.**

/tmp/ops-upgrade-experiment/indico-operator__action-testing__C2/tests/unit_harness/test_actions.py

```
File /tmp/ops-upgrade-experiment/indico-operator__action-testing__C2/tests/unit_harness/test_actions.py updated with changes.
```


---

<sub>⏱️ 10m 2s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/indico-operator__action-testing__C2/tests/unit_harness/test_actions.py.**

/tmp/ops-upgrade-experiment/indico-operator__action-testing__C2/tests/unit_harness/test_actions.py

```
File /tmp/ops-upgrade-experiment/indico-operator__action-testing__C2/tests/unit_harness/test_actions.py updated with changes.
```


---

<sub>⏱️ 10m 9s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/indico-operator__action-testing__C2/tests/unit_harness/test_actions.py.**

/tmp/ops-upgrade-experiment/indico-operator__action-testing__C2/tests/unit_harness/test_actions.py

```
File /tmp/ops-upgrade-experiment/indico-operator__action-testing__C2/tests/unit_harness/test_actions.py updated with changes.
```


---

<sub>⏱️ 10m 14s</sub>

### 💬 Copilot

Now run the tests to verify:

---

<sub>⏱️ 10m 16s</sub>

### ✅ `bash`

**Run updated action tests**

$ cd /tmp/ops-upgrade-experiment/indico-operator__action-testing__C2 && tox -e unit -- tests/unit_harness/test_actions.py -v 2>&1 | tail -30

<details>
<summary>28 lines</summary>

```
/tmp/ops-upgrade-experiment/indico-operator__action-testing__C2/tests/unit_harness/test_base.py:21: PendingDeprecationWarning: Harness is deprecated. For the recommended approach, see: https://ops.readthedocs.io/en/latest/howto/write-unit-tests-for-a-charm.html
    self.harness = Harness(IndicoOperatorCharm)

tests/unit_harness/test_actions.py::TestActions::test_add_admin
tests/unit_harness/test_actions.py::TestActions::test_add_admin_fail
tests/unit_harness/test_actions.py::TestActions::test_refresh_external_resources_when_customization_and_plugins_set
  /tmp/ops-upgrade-experiment/indico-operator__action-testing__C2/lib/charms/data_platform_libs/v0/data_interfaces.py:1160: DeprecationWarning: JujuVersion.from_environ() is deprecated, use self.model.juju_version instead
    self._jujuversion = JujuVersion.from_environ()

tests/unit_harness/test_actions.py: 13 warnings
  /tmp/ops-upgrade-experiment/indico-operator__action-testing__C2/src/charm.py:893: DeprecationWarning: JujuVersion.from_environ() is deprecated, use self.model.juju_version instead
    juju_version = JujuVersion.from_environ()

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
======================== 7 passed, 23 warnings in 0.17s ========================
unit: commands[1]> coverage report
Name                       Stmts   Miss Branch BrPart  Cover   Missing
----------------------------------------------------------------------
src/charm.py                 357     58     80     17    79%   83-85, 162-165, 176, 209-210, 408, 422-423, 544-546, 587-591, 602-603, 608-645, 673, 691-697, 714-715, 792->exit, 818->834, 820->829, 829->834, 855-861, 862->exit, 871-885, 915->exit, 953-959
src/database_observer.py      32      2      4      1    92%   54, 73
src/s3_observer.py            17      2      0      0    88%   38, 43
src/saml_observer.py          14      1      0      0    93%   39
src/smtp_observer.py          15      1      0      0    93%   40
src/state.py                  73     13      8      2    77%   38, 67, 92-98, 193-203, 231-233
----------------------------------------------------------------------
TOTAL                        508     77     92     20    80%
Coverage failure: total of 80 is less than fail-under=97
unit: exit 2 (0.09 seconds) /tmp/ops-upgrade-experiment/indico-operator__action-testing__C2> coverage report pid=64968
  unit: FAIL code 2 (0.64=setup[0.01]+cmd[0.55,0.09] seconds)
  evaluation failed :( (0.66 seconds)
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 10m 22s</sub>

### 💬 Copilot

All 7 tests pass. The coverage failure is expected when running only the actions tests. Let me run the full test suite:

---

<sub>⏱️ 10m 24s</sub>

### ✅ `bash`

**Run full test suite**

$ cd /tmp/ops-upgrade-experiment/indico-operator__action-testing__C2 && tox -e unit 2>&1 | tail -25

<details>
<summary>23 lines</summary>

```
harness = Harness(ObservedCharm, meta=REQUIRER_METADATA)

tests/unit_harness/test_saml_observer.py::test_saml_related_emits_config_changed_event_and_updates_charm_state
  /tmp/ops-upgrade-experiment/indico-operator__action-testing__C2/tests/unit_harness/test_saml_observer.py:66: PendingDeprecationWarning: Harness is deprecated. For the recommended approach, see: https://ops.readthedocs.io/en/latest/howto/write-unit-tests-for-a-charm.html
    harness = Harness(ObservedCharm, meta=REQUIRER_METADATA)

tests/unit_harness/test_smtp_observer.py::test_smtp_related_emits_config_changed_event_and_updates_charm_state
  /tmp/ops-upgrade-experiment/indico-operator__action-testing__C2/tests/unit_harness/test_smtp_observer.py:63: PendingDeprecationWarning: Harness is deprecated. For the recommended approach, see: https://ops.readthedocs.io/en/latest/howto/write-unit-tests-for-a-charm.html
    harness = Harness(ObservedCharm, meta=REQUIRER_METADATA)

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
======================= 42 passed, 97 warnings in 0.94s ========================
unit: commands[1]> coverage report
Name                       Stmts   Miss Branch BrPart  Cover   Missing
----------------------------------------------------------------------
src/charm.py                 357     10     80      8    96%   408, 422-423, 673, 714-715, 818->834, 820->829, 829->834, 882, 915->exit, 953-959
src/database_observer.py      32      0      4      0   100%
src/s3_observer.py            17      0      0      0   100%
src/saml_observer.py          14      0      0      0   100%
src/smtp_observer.py          15      0      0      0   100%
src/state.py                  73      0      8      0   100%
----------------------------------------------------------------------
TOTAL                        508     10     92      8    97%
  unit: OK (1.33=setup[0.01]+cmd[1.24,0.08] seconds)
  congratulations :) (1.35 seconds)
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 10m 30s</sub>

### 💬 Copilot

All 42 tests pass with 97% coverage. Let me view the final state of the updated file to confirm it's clean:

---

<sub>⏱️ 10m 30s</sub>

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/indico-operator__action-testing__C2/tests/unit_harness/test_actions.py.**

/tmp/ops-upgrade-experiment/indico-operator__action-testing__C2/tests/unit_harness/test_actions.py (lines 1-20)

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
12. from ops.model import Container
13. from ops.pebble import ExecError
14. from ops.testing import ActionFailed
15. 
16. from charm import EMAIL_LIST_MAX, EMAIL_LIST_SEPARATOR, IndicoOperatorCharm
17. from tests.unit_harness.test_base import TestBase
18. 
19. 
20. class TestActions(TestBase):
```

</details>


---

<sub>⏱️ 10m 45s</sub>

### 💬 Copilot

All tests pass. Here's a summary of what was changed in `tests/unit_harness/test_actions.py`:

**What changed:**
- Replaced `from ops.charm import ActionEvent` with `from ops.testing import ActionFailed`
- **`test_refresh_external_resources`**: Replaced `charm._refresh_external_resources(MagicMock())` with `self.harness.run_action("refresh-external-resources")`
- **`test_add_admin`**: Replaced manual `ActionEvent` mock + direct `charm._add_admin_action(event)` call with `self.harness.run_action("add-admin", {"email": ..., "password": ...})`
- **`test_add_admin_fail`**: Replaced custom `event.fail` stub + `assert event.fail_message == ...` with `assertRaises(ActionFailed)` + `cm.exception.message`
- **`_anonymize_user` helper**: Removed `mock_event` parameter; replaced `charm._anonymize_user_action(mock_event)` + `mock_event.set_results.assert_called_with(...)` with `run_action(...)` + `assertEqual(output.results, ...)`
- **`test_anonymize_user` / `test_anonymize_user_list`**: Removed manual event mock creation; updated helper call signatures
- **`test_anonymize_user_maximum_reached`**: Replaced `mock_event.fail.assert_called_with(...)` with `assertRaises(ActionFailed)` + `cm.exception.message`
- **`test_anonymize_user_fail`**: Replaced dual `mock_event.fail/set_results` assertions with `assertRaises(ActionFailed)` checking both `cm.exception.message` and `cm.exception.output.results`

---

<sub>⏱️ 10m 45s</sub>

### ✅ `task_complete`

**Updated `tests/unit_harness/test_actions.py` to use `Harn...**

<details>
<summary>Arguments</summary>

```json
{
  "summary": "Updated `tests/unit_harness/test_actions.py` to use `Harness.run_action()` (introduced in ops 2.9.0) instead of the old pattern of manually constructing `ActionEvent` mocks and calling action handler methods directly.\n\n**Key changes:**\n- Swapped `from ops.charm import ActionEvent` → `from ops.testing import ActionFailed`\n- All 5 action tests now call `self.harness.run_action(\"action-name\", params)` which returns an `ActionOutput(logs, results)` on success, or raises `ActionFailed(message, output)` on failure\n- Success assertions use `output.results` instead of `mock_event.set_results.assert_called_with(...)`\n- Failure assertions use `assertRaises(ActionFailed)` + `cm.exception.message` / `cm.exception.output.results` instead of custom `event.fail` stubs or `mock_event.fail.assert_called_with(...)`\n- Removed all manual `MagicMock(spec=ActionEvent)` construction and `event.params` setup\n\nAll 42 unit tests pass with 97% coverage."
}
```

</details>

<details>
<summary>8 lines</summary>

```
Updated `tests/unit_harness/test_actions.py` to use `Harness.run_action()` (introduced in ops 2.9.0) instead of the old pattern of manually constructing `ActionEvent` mocks and calling action handler methods directly.

**Key changes:**
- Swapped `from ops.charm import ActionEvent` → `from ops.testing import ActionFailed`
- All 5 action tests now call `self.harness.run_action("action-name", params)` which returns an `ActionOutput(logs, results)` on success, or raises `ActionFailed(message, output)` on failure
- Success assertions use `output.results` instead of `mock_event.set_results.assert_called_with(...)`
- Failure assertions use `assertRaises(ActionFailed)` + `cm.exception.message` / `cm.exception.output.results` instead of custom `event.fail` stubs or `mock_event.fail.assert_called_with(...)`
- Removed all manual `MagicMock(spec=ActionEvent)` construction and `event.params` setup

All 42 unit tests pass with 97% coverage.
```

</details>


---

<sub>⏱️ 10m 45s</sub>

### ✓ Task Complete

Updated `tests/unit_harness/test_actions.py` to use `Harness.run_action()` (introduced in ops 2.9.0) instead of the old pattern of manually constructing `ActionEvent` mocks and calling action handler methods directly.

**Key changes:**
- Swapped `from ops.charm import ActionEvent` → `from ops.testing import ActionFailed`
- All 5 action tests now call `self.harness.run_action("action-name", params)` which returns an `ActionOutput(logs, results)` on success, or raises `ActionFailed(message, output)` on failure
- Success assertions use `output.results` instead of `mock_event.set_results.assert_called_with(...)`
- Failure assertions use `assertRaises(ActionFailed)` + `cm.exception.message` / `cm.exception.output.results` instead of custom `event.fail` stubs or `mock_event.fail.assert_called_with(...)`
- Removed all manual `MagicMock(spec=ActionEvent)` construction and `event.params` setup

All 42 unit tests pass with 97% coverage.

---

<sub>Generated by [GitHub Copilot CLI](https://github.com/features/copilot/cli)</sub>
