# 🤖 Copilot CLI Session

> [!NOTE]
> - **Session ID:** `f71b2d47-53cb-4730-a310-ae86abd189f3`  
> - **Started:** 4/3/2026, 9:40:03 AM  
> - **Duration:** 7m 43s  
> - **Exported:** 4/3/2026, 9:47:47 AM  

---

<sub>⏱️ 5s</sub>

### 👤 User

This charm could benefit from action-testing. There is a skill available for applying this change.

---

<sub>⏱️ 17s</sub>

### 📦 task (Completed)

### ✅ `bash`

**Find YAML files to locate charmcraft.yaml and actions.yaml**

$ find /tmp/ops-upgrade-experiment/indico-operator__action-testing__C1pf -type f -name "*.yaml" -o -name "*.yml" | head -20

<details>
<summary>21 lines</summary>

```
/tmp/ops-upgrade-experiment/indico-operator__action-testing__C1pf/nginx_rock/rockcraft.yaml
/tmp/ops-upgrade-experiment/indico-operator__action-testing__C1pf/.licenserc.yaml
/tmp/ops-upgrade-experiment/indico-operator__action-testing__C1pf/docs/release-notes/artifacts/2604_refactor_integration_tests.yaml
/tmp/ops-upgrade-experiment/indico-operator__action-testing__C1pf/docs/release-notes/artifacts/pr0494.yaml
/tmp/ops-upgrade-experiment/indico-operator__action-testing__C1pf/docs/release-notes/artifacts/pr0622.yaml
/tmp/ops-upgrade-experiment/indico-operator__action-testing__C1pf/docs/release-notes/artifacts/pr0707.yaml
/tmp/ops-upgrade-experiment/indico-operator__action-testing__C1pf/docs/release-notes/artifacts/pr0713.yaml
/tmp/ops-upgrade-experiment/indico-operator__action-testing__C1pf/docs/release-notes/artifacts/2604_terraform_updates.yaml
/tmp/ops-upgrade-experiment/indico-operator__action-testing__C1pf/docs/release-notes/artifacts/pr0640.yaml
/tmp/ops-upgrade-experiment/indico-operator__action-testing__C1pf/docs/release-notes/artifacts/pr0645.yaml
/tmp/ops-upgrade-experiment/indico-operator__action-testing__C1pf/docs/release-notes/artifacts/pr0480.yaml
/tmp/ops-upgrade-experiment/indico-operator__action-testing__C1pf/docs/release-notes/artifacts/2604_migrate_architecture_docs.yaml
/tmp/ops-upgrade-experiment/indico-operator__action-testing__C1pf/docs/release-notes/artifacts/pr0653.yaml
/tmp/ops-upgrade-experiment/indico-operator__action-testing__C1pf/docs/release-notes/artifacts/2604_allure_updates.yaml
/tmp/ops-upgrade-experiment/indico-operator__action-testing__C1pf/docs/release-notes/artifacts/pr0479.yaml
/tmp/ops-upgrade-experiment/indico-operator__action-testing__C1pf/docs/release-notes/artifacts/pr0466.yaml
/tmp/ops-upgrade-experiment/indico-operator__action-testing__C1pf/docs/release-notes/artifacts/pr0606.yaml
/tmp/ops-upgrade-experiment/indico-operator__action-testing__C1pf/docs/release-notes/artifacts/2604_upgrade_terraform_module.yaml
/tmp/ops-upgrade-experiment/indico-operator__action-testing__C1pf/docs/release-notes/artifacts/pr0706.yaml
/tmp/ops-upgrade-experiment/indico-operator__action-testing__C1pf/docs/release-notes/artifacts/2604_copilot_instructions.yaml
<exited with exit code 0>
```

</details>


### ✅ `bash`

**Find test files**

$ find /tmp/ops-upgrade-experiment/indico-operator__action-testing__C1pf -type f -name "*test*.py" | head -20

<details>
<summary>19 lines</summary>

```
/tmp/ops-upgrade-experiment/indico-operator__action-testing__C1pf/tests/conftest.py
/tmp/ops-upgrade-experiment/indico-operator__action-testing__C1pf/tests/integration/conftest.py
/tmp/ops-upgrade-experiment/indico-operator__action-testing__C1pf/tests/integration/test_charm.py
/tmp/ops-upgrade-experiment/indico-operator__action-testing__C1pf/tests/integration/test_s3.py
/tmp/ops-upgrade-experiment/indico-operator__action-testing__C1pf/tests/integration/test_loki.py
/tmp/ops-upgrade-experiment/indico-operator__action-testing__C1pf/tests/integration/test_actions.py
/tmp/ops-upgrade-experiment/indico-operator__action-testing__C1pf/tests/integration/test_saml.py
/tmp/ops-upgrade-experiment/indico-operator__action-testing__C1pf/tests/unit/conftest.py
/tmp/ops-upgrade-experiment/indico-operator__action-testing__C1pf/tests/unit/test_on_leader_elected.py
/tmp/ops-upgrade-experiment/indico-operator__action-testing__C1pf/tests/unit_harness/conftest.py
/tmp/ops-upgrade-experiment/indico-operator__action-testing__C1pf/tests/unit_harness/test_base.py
/tmp/ops-upgrade-experiment/indico-operator__action-testing__C1pf/tests/unit_harness/test_state.py
/tmp/ops-upgrade-experiment/indico-operator__action-testing__C1pf/tests/unit_harness/test_saml_observer.py
/tmp/ops-upgrade-experiment/indico-operator__action-testing__C1pf/tests/unit_harness/test_database_observer.py
/tmp/ops-upgrade-experiment/indico-operator__action-testing__C1pf/tests/unit_harness/test_smtp_observer.py
/tmp/ops-upgrade-experiment/indico-operator__action-testing__C1pf/tests/unit_harness/test_s3_observer.py
/tmp/ops-upgrade-experiment/indico-operator__action-testing__C1pf/tests/unit_harness/test_actions.py
/tmp/ops-upgrade-experiment/indico-operator__action-testing__C1pf/tests/unit_harness/test_core.py
<exited with exit code 0>
```

</details>


### ✅ `bash`

**Find charm.py and dependency files**

$ find /tmp/ops-upgrade-experiment/indico-operator__action-testing__C1pf -type f -name "charm.py" -o -name "pyproject.toml" -o -name "requirements.txt"

```
/tmp/ops-upgrade-experiment/indico-operator__action-testing__C1pf/requirements.txt
/tmp/ops-upgrade-experiment/indico-operator__action-testing__C1pf/pyproject.toml
/tmp/ops-upgrade-experiment/indico-operator__action-testing__C1pf/src/charm.py
<exited with exit code 0>
```


### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/indico-operator__action-testing__C1pf.**

/tmp/ops-upgrade-experiment/indico-operator__action-testing__C1pf

<details>
<summary>37 lines</summary>

```
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


### 💬 Copilot

Now let me get the key files in parallel:

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/indico-operator__action-testing__C1pf/actions.yaml.**

/tmp/ops-upgrade-experiment/indico-operator__action-testing__C1pf/actions.yaml

<details>
<summary>23 lines</summary>

```
1. # Copyright 2025 Canonical Ltd.
2. # See LICENSE file for licensing details.
3. 
4. refresh-external-resources:
5.   description: Pull changes from the customization repository, reload uWSGI and upgrade the external plugins
6. add-admin:
7.   description: Add an admin to Indico
8.   params:
9.     email:
10.       type: string
11.       description: User email.
12.     password:
13.       type: string
14.       description: User password.
15.   required: [email, password]
16. anonymize-user:
17.   description: Anonymize stored personal data to facilitate GDPR compliance
18.   params:
19.     email:
20.       type: string
21.       description: User email (or a list of emails separated by comma). Maximum of 50 emails.
22.   required: [email]
23.
```

</details>


### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/indico-operator__action-testing__C1pf/pyproject.toml.**

/tmp/ops-upgrade-experiment/indico-operator__action-testing__C1pf/pyproject.toml

<details>
<summary>57 lines</summary>

```
1. # Copyright 2025 Canonical Ltd.
2. # See LICENSE file for licensing details.
3. 
4. [tool.bandit]
5. exclude_dirs = ["/venv/"]
6. [tool.bandit.assert_used]
7. skips = ["*/*test.py", "*/test_*.py", "*tests/*.py"]
8. 
9. # Testing tools configuration
10. [tool.coverage.run]
11. branch = true
12. 
13. # Formatting tools configuration
14. [tool.black]
15. line-length = 99
16. target-version = ["py38"]
17. 
18. [tool.coverage.report]
19. fail_under = 97
20. show_missing = true
21. 
22. # Linting tools configuration
23. [tool.flake8]
24. max-line-length = 99
25. max-doc-length = 99
26. max-complexity = 10
27. exclude = [".git", "__pycache__", ".tox", "build", "dist", "*.egg_info", "venv"]
28. select = ["E", "W", "F", "C", "N", "R", "D", "H"]
29. # Ignore W503, E501 because using black creates errors with this
30. # Ignore D107 Missing docstring in __init__
31. ignore = ["W503", "E501", "D107"]
32. # D100, D101, D102, D103: Ignore missing docstrings in tests
33. per-file-ignores = ["tests/*:D100,D101,D102,D103,D104,D205,D212,D415"]
34. docstring-convention = "google"
35. # Check for properly formatted copyright header in each file
36. copyright-check = "True"
37. copyright-author = "Canonical Ltd."
38. copyright-regexp = "Copyright\\s\\d{4}([-,]\\d{4})*\\s+%(author)s"
39. 
40. [tool.isort]
41. line_length = 99
42. profile = "black"
43. 
44. [tool.mypy]
45. ignore_missing_imports = true
46. explicit_package_bases = true
47. namespace_packages = true
48. 
49. [tool.pylint]
50. disable = "wrong-import-order"
51. 
52. [tool.pytest.ini_options]
53. pythonpath = [
54.   "lib",
55.   "src"
56. ]
57.
```

</details>


### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/indico-operator__action-testing__C1pf/requirements.txt.**

/tmp/ops-upgrade-experiment/indico-operator__action-testing__C1pf/requirements.txt

```
1. pydantic==1.10.26
2. ops>=2.0.0,<3.0.0
3. 
```


### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/indico-operator__action-testing__C1pf/tests/unit_harness/test_actions.py.**

/tmp/ops-upgrade-experiment/indico-operator__action-testing__C1pf/tests/unit_harness/test_actions.py

<details>
<summary>394 lines</summary>

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
21.     """Indico charm unit tests."""
22. 
23.     @patch.object(Container, "exec")
24.     @patch("charm.secrets")
25.     def test_refresh_external_resources_when_customization_and_plugins_set(
26.         self, mock_secrets, mock_exec
27.     ):
28.         """
29.         arrange: charm created and relations established
30.         act: configure the external resources and trigger the refresh action
31.         assert: the customization sources are pulled and the plugins upgraded
32.         """
33.         mock_exec.return_value = MagicMock(wait_output=MagicMock(return_value=("", None)))
34.         mock_secrets.token_hex.return_value = "123456"
35.         self.harness.disable_hooks()
36.         self.set_relations_and_leader()
37.         self.harness.update_config(
38.             {
39.                 "customization_sources_url": "https://example.com/custom",
40.                 "external_plugins": "git+https://example.git/#subdirectory=themes_cern",
41.             }
42.         )
43. 
44.         charm: IndicoOperatorCharm = typing.cast(IndicoOperatorCharm, self.harness.charm)
45.         with self.assertLogs(level="INFO") as logger:
46.             charm._refresh_external_resources(MagicMock())
47. 
48.             mock_exec.assert_any_call(
49.                 ["git", "pull"],
50.                 working_dir="/srv/indico/custom",
51.                 user="indico",
52.                 environment={},
53.             )
54.             mock_exec.assert_any_call(
55.                 [
56.                     "pip",
57.                     "install",
58.                     "--upgrade",
59.                     "-c",
60.                     "/tmp/constraints-123456.txt",  # nosec B108
61.                     "git+https://example.git/#subdirectory=themes_cern",
62.                 ],
63.                 environment={},
64.             )
65.             expected_logs = [
66.                 "INFO:charm:About to run: pip install --upgrade "
67.                 "-c /tmp/constraints-123456.txt "
68.                 "git+https://example.git/#subdirectory=themes_cern",
69.                 "INFO:charm:Output was: ",
70.             ]
71.             assert logger.output == expected_logs
72. 
73.     @patch.object(Container, "exec")
74.     def test_add_admin(self, mock_exec):
75.         """
76.         arrange: an email and a password
77.         act: when the _on_add_admin_action method is executed
78.         assert: the indico command to add the user is executed with the appropriate parameters.
79.         """
80.         mock_exec.return_value = MagicMock(wait_output=MagicMock(return_value=("", None)))
81. 
82.         self.set_relations_and_leader()
83.         self.harness.disable_hooks()
84. 
85.         container = self.harness.model.unit.get_container("indico")
86. 
87.         charm: IndicoOperatorCharm = typing.cast(IndicoOperatorCharm, self.harness.charm)
88. 
89.         email = "sample@email.com"
90.         password = token_hex(16)
91.         event = MagicMock(spec=ActionEvent)
92.         event.params = {
93.             "email": email,
94.             "password": password,
95.         }
96. 
97.         def event_store_failure(failure_message: str) -> None:
98.             """Define a failure message for the event.
99. 
100.             Args:
101.                 failure_message: failure message content to be defined.
102.             """
103.             event.fail_message = failure_message
104. 
105.         event.fail = event_store_failure
106. 
107.         indico_env_config = charm._get_indico_env_config_str(container)
108.         expected_cmd = [
109.             "/usr/bin/indico",
110.             "autocreate",
111.             "admin",
112.             email,
113.             password,
114.         ]
115. 
116.         charm._add_admin_action(event)
117. 
118.         mock_exec.assert_any_call(
119.             expected_cmd,
120.             user="indico",
121.             working_dir="/srv/indico",
122.             environment=indico_env_config,
123.         )
124. 
125.     @patch.object(Container, "exec")
126.     def test_add_admin_fail(self, mock_exec):
127.         """
128.         arrange: an email and a password
129.         act: when the _on_add_admin_action method is executed
130.         assert: the indico command to add the user is executed with the appropriate parameters.
131.         """
132.         mock_wo = MagicMock(
133.             return_value=("", None),
134.         )
135. 
136.         stdout_mock = "CRASH"
137. 
138.         # I'm disabling unused-argument here because some could be passed to the mock
139.         def mock_wo_side_effect(*args, **kwargs):  # pylint: disable=unused-argument
140.             """Mock wo side effect.
141. 
142.             Args:
143.                 args: Variable list of positional arguments passed to the parent constructor.
144.                 kwargs: a `dict` of the extra arguments passed to the function.
145. 
146.             Returns:
147.                 unittest.mock DEFAULT built-in.
148. 
149.             Raises:
150.                 ExecError: Execution error fired if conditions are met.
151.             """
152.             if isinstance(mock_wo.cmd, list) and "autocreate" in mock_wo.cmd:
153.                 raise ExecError(command=mock_wo.cmd, exit_code=42, stdout=stdout_mock, stderr="")
154.             return DEFAULT
155. 
156.         mock_wo.side_effect = mock_wo_side_effect
157. 
158.         # I'm disabling unused-argument here because some could be passed to the mock
159.         def mock_exec_side_effect(*args, **kwargs):  # pylint: disable=unused-argument
160.             """Mock execution side effect.
161. 
162.             Args:
163.                 args: Variable list of positional arguments passed to the parent constructor.
164.                 kwargs: a `dict` of the extra arguments passed to the function.
165. 
166.             Returns:
167.                 unittest.mock DEFAULT built-in.
168.             """
169.             mock_wo.cmd = args[0]
170.             return DEFAULT
171. 
172.         mock_exec.side_effect = mock_exec_side_effect
173.         mock_exec.return_value = MagicMock(
174.             wait_output=mock_wo,
175.         )
176. 
177.         self.set_relations_and_leader()
178.         self.harness.disable_hooks()
179. 
180.         container = self.harness.model.unit.get_container("indico")
181. 
182.         charm: IndicoOperatorCharm = typing.cast(IndicoOperatorCharm, self.harness.charm)
183. 
184.         email = "sample@email.com"
185.         password = token_hex(16)
186.         event = MagicMock(spec=ActionEvent)
187.         event.params = {
188.             "email": email,
189.             "password": password,
190.         }
191. 
192.         def event_store_failure(failure_message: str) -> None:
193.             """Define a failure message for the event.
194. 
195.             Args:
196.                 failure_message: failure message content to be defined.
197.             """
198.             event.fail_message = failure_message
199. 
200.         event.fail = event_store_failure
201. 
202.         indico_env_config = charm._get_indico_env_config_str(container)
203.         expected_cmd = [
204.             "/usr/bin/indico",
205.             "autocreate",
206.             "admin",
207.             email,
208.             password,
209.         ]
210. 
211.         charm._add_admin_action(event)
212.         assert event.fail_message == f"Failed to create admin {email}: '{stdout_mock}'"
213. 
214.         mock_exec.assert_any_call(
215.             expected_cmd,
216.             user="indico",
217.             working_dir="/srv/indico",
218.             environment=indico_env_config,
219.         )
220. 
221.     def _set_indico(self) -> IndicoOperatorCharm:
222.         """Set Indico Charm
223. 
224.         Returns:
225.             IndicoOperatorCharm: Indico charm configured
226.         """
227.         charm: IndicoOperatorCharm = typing.cast(IndicoOperatorCharm, self.harness.charm)
228.         charm._get_installed_plugins = MagicMock(return_value="")
229.         charm._get_indico_secret_key_from_relation = MagicMock(return_value="")
230.         self.harness.container_pebble_ready("indico")
231.         return charm
232. 
233.     def _anonymize_user(self, emails: str, mock_event: MagicMock, mock_exec: MagicMock):
234.         """Execute anonymize user action
235. 
236.         Args:
237.             emails: email list parameter to be used
238.             mock_event (MagicMock): event mock
239.             mock_exec (MagicMock): Container exec mock
240.         """
241.         charm = self._set_indico()
242.         charm._anonymize_user_action(mock_event)
243. 
244.         def validate_command(email: str):
245.             """Check if the command was called.
246. 
247.             Args:
248.                 email: email parameter to be used
249.             """
250.             # Check if command was called
251.             expected_cmd = [
252.                 "/usr/bin/indico",
253.                 "anonymize",
254.                 "user",
255.                 email,
256.             ]
257.             container = self.harness.model.unit.get_container("indico")
258.             indico_env_config = charm._get_indico_env_config_str(container)
259.             mock_exec.assert_any_call(
260.                 expected_cmd,
261.                 user="indico",
262.                 working_dir="/srv/indico",
263.                 environment=indico_env_config,
264.             )
265. 
266.         for email in emails.split(","):
267.             validate_command(email)
268. 
269.         # Check if event results was properly set
270.         mock_event.set_results.assert_called_with({"user": f"{emails}", "output": f"{emails}"})
271. 
272.     @patch.object(Container, "exec")
273.     def test_anonymize_user(self, mock_exec):
274.         """
275.         arrange: an email
276.         act: when the _on_anonymize_user_action method is executed
277.         assert: the indico command to anonymize the user is executed with the appropriate
278.             parameters and the event results is set as expected
279.         """
280.         email = token_hex(16)
281.         mock_exec.return_value = MagicMock(wait_output=MagicMock(return_value=(f"{email}", None)))
282.         mock_event = MagicMock(spec=ActionEvent)
283.         mock_event.params = {
284.             "email": email,
285.         }
286.         self._anonymize_user(email, mock_event, mock_exec)
287. 
288.     def _generate_emails_mock(self, emails: str) -> typing.Iterator[MagicMock]:
289.         """Generate list of mocks accordingly to list of emails
290. 
291.         Args:
292.             emails (str): list of emails
293. 
294.         Yields:
295.             Iterator[MagicMock]: Mock of exec that returns email
296.         """
297.         for email in emails.split(EMAIL_LIST_SEPARATOR):
298.             wait_output = MagicMock(return_value=(email, None))
299.             yield MagicMock(wait_output=wait_output)
300. 
301.     @patch.object(Container, "exec")
302.     def test_anonymize_user_list(self, mock_exec):
303.         """
304.         arrange: an list of 5 emails
305.         act: when the _on_anonymize_user_action method is executed
306.         assert: the indico command to anonymize the user is executed with the appropriate
307.             parameters and the event results is set as expected
308.         """
309.         emails = EMAIL_LIST_SEPARATOR.join([token_hex(16) for _ in range(5)])
310.         mock_event = MagicMock(spec=ActionEvent)
311.         mock_event.params = {
312.             "email": emails,
313.         }
314.         mock_exec.side_effect = list(self._generate_emails_mock(emails))
315.         self._anonymize_user(emails, mock_event, mock_exec)
316. 
317.     @patch.object(Container, "exec")
318.     def test_anonymize_user_maximum_reached(self, mock_exec):
319.         """
320.         arrange: an list of 51 emails
321.         act: when the _on_anonymize_user_action method is executed
322.         assert: the indico command to anonymize the user is executed with the appropriate
323.             parameters and the event results is set as expected
324.         """
325.         charm = self._set_indico()
326.         emails = EMAIL_LIST_SEPARATOR.join([token_hex(16) for _ in range(EMAIL_LIST_MAX + 1)])
327.         mock_event = MagicMock(spec=ActionEvent)
328.         mock_event.params = {
329.             "email": emails,
330.         }
331.         mock_exec.return_value = MagicMock(wait_output=MagicMock(return_value=("", None)))
332. 
333.         charm._anonymize_user_action(mock_event)
334.         expected_argument = (
335.             f"Failed to anonymize user: List of more than {EMAIL_LIST_MAX} emails are not allowed"
336.         )
337.         # Pylint does not understand that the mock supports this call
338.         mock_event.fail.assert_called_with(expected_argument)  # pylint: disable=no-member
339. 
340.     @patch.object(Container, "exec")
341.     def test_anonymize_user_fail(self, mock_exec):
342.         """
343.         arrange: an email
344.         act: when the _on_anonymize_user_action method is executed
345.         assert: the indico command to anonymize the user is executed with the appropriate
346.             parameters and the event results is set as expected
347.         """
348.         charm = self._set_indico()
349. 
350.         # Set Mock
351.         email = token_hex(16)
352.         error_msg = "Execution error"
353.         expected_cmd = [
354.             "/usr/bin/indico",
355.             "anonymize",
356.             "user",
357.             email,
358.         ]
359.         expected_exception = ExecError(
360.             command=" ".join(expected_cmd), exit_code=42, stdout=f"{error_msg}", stderr=""
361.         )
362.         wait_output = MagicMock(side_effect=expected_exception)
363.         mock_exec.return_value = MagicMock(wait_output=wait_output)
364.         # Set and trigger the event
365.         mock_event = MagicMock(spec=ActionEvent)
366.         mock_event.params = {
367.             "email": email,
368.         }
369. 
370.         charm._anonymize_user_action(mock_event)
371. 
372.         # Check if command was called
373.         container = self.harness.model.unit.get_container("indico")
374.         indico_env_config = charm._get_indico_env_config_str(container)
375.         mock_exec.assert_any_call(
376.             expected_cmd,
377.             user="indico",
378.             working_dir="/srv/indico",
379.             environment=indico_env_config,
380.         )
381. 
382.         # Check if event fail was properly set
383.         expected_argument = "Failed to anonymize one or more users, please verify the results."
384.         # Pylint does not understand that the mock supports this call
385.         mock_event.fail.assert_called_with(expected_argument)  # pylint: disable=no-member
386. 
387.         # Check if event results was properly set
388.         mock_event.set_results.assert_called_with(
389.             {
390.                 "user": f"{email}",
391.                 "output": f"Failed to anonymize user {email}: '{error_msg}'",
392.             }
393.         )
394.
```

</details>


### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/indico-operator__action-testing__C1pf/tests/integration/test_actions.py.**

/tmp/ops-upgrade-experiment/indico-operator__action-testing__C1pf/tests/integration/test_actions.py

<details>
<summary>89 lines</summary>

```
1. #!/usr/bin/env python3
2. # Copyright 2025 Canonical Ltd.
3. # See LICENSE file for licensing details.
4. 
5. """Indico charm actions integration tests."""
6. 
7. from secrets import token_hex
8. 
9. import juju.action
10. import pytest
11. import pytest_asyncio
12. from ops import Application
13. 
14. ADMIN_USER_EMAIL = "sample@email.com"
15. ADMIN_USER_EMAIL_FAIL = "sample2@email.com"
16. 
17. 
18. @pytest_asyncio.fixture(scope="module")
19. async def add_admin(app: Application):
20.     """
21.     arrange: given charm in its initial state
22.     act: run the add-admin action
23.     assert: check the output in the action result
24.     """
25.     assert hasattr(app, "units")
26. 
27.     assert app.units[0]
28. 
29.     email = ADMIN_USER_EMAIL
30.     email_fail = ADMIN_USER_EMAIL_FAIL
31.     # This is a test password
32.     password = token_hex(16)
33. 
34.     # Application actually does have units
35.     action: juju.action.Action = await app.units[0].run_action(  # type: ignore
36.         "add-admin", email=email, password=password
37.     )
38.     await action.wait()
39.     assert action.status == "completed"
40.     assert action.results["user"] == email
41.     assert f'Admin with email "{email}" correctly created' in action.results["output"]
42.     action2: juju.action.Action = await app.units[0].run_action(  # type: ignore
43.         "add-admin", email=email_fail, password=password
44.     )
45.     await action2.wait()
46.     assert action2.status == "completed"
47.     assert action2.results["user"] == email_fail
48.     assert f'Admin with email "{email_fail}" correctly created' in action2.results["output"]
49. 
50. 
51. @pytest.mark.asyncio
52. @pytest.mark.abort_on_fail
53. @pytest.mark.usefixtures("add_admin")
54. async def test_anonymize_user(app: Application):
55.     """
56.     arrange: admin user created
57.     act: run the anonymize-user action
58.     assert: check the output in the action result
59.     """
60.     # Application actually does have units
61.     action_anonymize: juju.action.Action = await app.units[0].run_action(  # type: ignore
62.         "anonymize-user", email=ADMIN_USER_EMAIL
63.     )
64.     await action_anonymize.wait()
65.     assert action_anonymize.status == "completed"
66.     assert action_anonymize.results["user"] == ADMIN_USER_EMAIL
67.     expected_words = [ADMIN_USER_EMAIL, "correctly anonymized"]
68.     assert all(word in action_anonymize.results["output"] for word in expected_words)
69. 
70. 
71. @pytest.mark.asyncio
72. @pytest.mark.abort_on_fail
73. @pytest.mark.usefixtures("add_admin")
74. async def test_anonymize_user_fail(app: Application):
75.     """
76.     arrange: admin user created
77.     act: run the anonymize-user action
78.     assert: check the output in the action result
79.     """
80.     # Application actually does have units
81.     action_anonymize: juju.action.Action = await app.units[0].run_action(  # type: ignore
82.         "anonymize-user", email=f",{ADMIN_USER_EMAIL_FAIL}"
83.     )
84.     await action_anonymize.wait()
85.     assert action_anonymize.status == "failed"
86.     assert action_anonymize.results["user"] == f",{ADMIN_USER_EMAIL_FAIL}"
87.     expected_words = [ADMIN_USER_EMAIL_FAIL, "correctly anonymized", "Failed to anonymize user"]
88.     assert all(word in action_anonymize.results["output"] for word in expected_words)
89.
```

</details>


### 💬 Copilot

Now let me check the charm.py file to find action handler method names:

### ✅ `bash`

**Find action handler methods in charm.py**

$ grep -n "def _.*_action\|def _on_.*_action\|@charm.action_handler" /tmp/ops-upgrade-experiment/indico-operator__action-testing__C1pf/src/charm.py | head -30

```
836:    def _refresh_external_resources_action(self, event: ActionEvent) -> None:
898:    def _add_admin_action(self, event: ActionEvent) -> None:
976:    def _anonymize_user_action(self, event: ActionEvent) -> None:
<exited with exit code 0>
```


### ✅ `bash`

**Find action test patterns in unit_harness test file**

$ grep -n "run_action\|_action\.emit\|_backend._action" /tmp/ops-upgrade-experiment/indico-operator__action-testing__C1pf/tests/unit_harness/test_actions.py

```

<exited with exit code 1>
```


### ✅ `bash`

**Check for action patterns in unit tests**

$ grep -n "run_action\|_action\.emit\|_backend._action" /tmp/ops-upgrade-experiment/indico-operator__action-testing__C1pf/tests/unit/test_on_leader_elected.py

```

<exited with exit code 1>
```


### 💬 Copilot

Let me view the charm.py file to see the action handlers and how they are wired:

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/indico-operator__action-testing__C1pf/src/charm.py.**

/tmp/ops-upgrade-experiment/indico-operator__action-testing__C1pf/src/charm.py (lines 1-100)

<details>
<summary>100 lines</summary>

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
51. 
52. class InvalidRedisNameError(Exception):
53.     """Represents invalid redis name error."""
54. 
55. 
56. class IndicoOperatorCharm(CharmBase):  # pylint: disable=too-many-instance-attributes
57.     """Charm for Indico on kubernetes.
58. 
59.     Attrs:
60.         on: Redis relation charm events.
61.     """
62. 
63.     on = RedisRelationCharmEvents()
64. 
65.     def __init__(self, *args):
66.         """Construct.
67. 
68.         Args:
69.             args: Arguments passed to the CharmBase parent constructor.
70.         """
71.         super().__init__(*args)
72.         self.database = DatabaseObserver(self)
73.         self.s3 = S3Observer(self)
74.         self.smtp = SmtpObserver(self)
75.         self.saml = SamlObserver(self)
76.         try:
77.             self.state = State.from_charm(
78.                 self,
79.                 s3_relation_data=self.s3.s3.get_s3_connection_info(),
80.                 smtp_relation_data=self.smtp.smtp.get_relation_data(),
81.                 saml_relation_data=self.saml.saml.get_relation_data(),
82.             )
83.         except CharmConfigInvalidError as exc:
84.             self.unit.status = ops.BlockedStatus(exc.msg)
85.             return
86.         self.framework.observe(self.on.config_changed, self._on_config_changed)
87.         self.framework.observe(self.on.leader_elected, self._on_leader_elected)
88.         self.framework.observe(self.on.indico_pebble_ready, self._on_pebble_ready)
89.         self.framework.observe(self.on.indico_nginx_pebble_ready, self._on_pebble_ready)
90.         self.framework.observe(
91.             self.on.refresh_external_resources_action, self._refresh_external_resources_action
92.         )
93.         # self.framework.observe(self.on.update_status, self._refresh_external_resources)
94.         self.framework.observe(self.on.add_admin_action, self._add_admin_action)
95.         self.framework.observe(self.on.anonymize_user_action, self._anonymize_user_action)
96.         self.redis_broker = RedisRequires(self, "redis-broker")
97.         self.framework.observe(
98.             self.redis_broker.charm.on.redis_relation_updated, self._on_config_changed
99.         )
100.         self.redis_cache = RedisRequires(self, "redis-cache")
```

</details>


### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/indico-operator__action-testing__C1pf/src/charm.py.**

/tmp/ops-upgrade-experiment/indico-operator__action-testing__C1pf/src/charm.py (lines 830-1050)

<details>
<summary>175 lines</summary>

```
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
846.         """Handle leader-elected event."""
847.         peer_relation = self.model.get_relation("indico-peers")
848.         secret_value = repr(os.urandom(32))
849.         if (
850.             peer_relation
851.             and not self._has_secrets()
852.             and not peer_relation.data[self.app].get("secret-key")
853.         ):
854.             peer_relation.data[self.app].update({"secret-key": secret_value})
855.         elif (
856.             peer_relation
857.             and self._has_secrets()
858.             and not peer_relation.data[self.app].get("secret-id")
859.         ):
860.             secret = self.app.add_secret({"secret-key": secret_value})
861.             peer_relation.data[self.app].update({"secret-id": typing.cast(str, secret.id)})
862.         if peer_relation and not peer_relation.data[self.app].get("celery-unit"):
863.             peer_relation.data[self.app].update({"celery-unit": self.unit.name})
864. 
865.     def _on_peer_relation_departed(self, event: RelationDepartedEvent) -> None:
866.         """Handle the peer relation departed event.
867. 
868.         Args:
869.             event: the event triggering the handler.
870.         """
871.         peer_relation = self.model.get_relation("indico-peers")
872.         if (
873.             self.unit.is_leader()
874.             and peer_relation
875.             and event.departing_unit
876.             and peer_relation.data[self.app].get("celery-unit") == event.departing_unit.name
877.         ):
878.             if self.unit != event.departing_unit:
879.                 peer_relation.data[self.app].update({"celery-unit": self.unit.name})
880.                 container = self.unit.get_container("indico")
881.                 if self._are_relations_ready(event) and container.can_connect():
882.                     self._config_pebble(container)
883.             else:
884.                 # Leadership election will select a new celery-unit
885.                 peer_relation.data[self.app].update({"celery-unit": ""})
886. 
887.     def _has_secrets(self) -> bool:
888.         """Check if current Juju version supports secrets.
889. 
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
1001. 
1002. if __name__ == "__main__":  # pragma: no cover
1003.     main(IndicoOperatorCharm, use_juju_for_storage=True)
1004.
```

</details>


### 💬 Copilot

Now let me check the test base class to understand the testing patterns:

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/indico-operator__action-testing__C1pf/tests/unit_harness/test_base.py.**

/tmp/ops-upgrade-experiment/indico-operator__action-testing__C1pf/tests/unit_harness/test_base.py

<details>
<summary>88 lines</summary>

```
1. # Copyright 2025 Canonical Ltd.
2. # See LICENSE file for licensing details.
3. 
4. """Indico charm unit tests."""
5. 
6. # pylint:disable=protected-access
7. 
8. import unittest
9. from typing import List
10. 
11. from ops.testing import Harness
12. 
13. from charm import IndicoOperatorCharm
14. 
15. 
16. class TestBase(unittest.TestCase):
17.     """Indico charm unit tests."""
18. 
19.     def setUp(self):
20.         """Set up test environment."""
21.         self.harness = Harness(IndicoOperatorCharm)
22.         self.addCleanup(self.harness.cleanup)
23.         self.harness.begin()
24. 
25.     def set_up_all_relations(self):
26.         """Set up all relations for the charm."""
27.         # pylint: disable=duplicate-code
28.         self.harness.add_relation(
29.             "database",
30.             "postgresql",
31.             app_data={
32.                 "database": "indico",
33.                 "endpoints": "postgresql-k8s-primary.local:5432",
34.                 "password": "somepass",  # nosec
35.                 "username": "user1",
36.             },
37.         )
38. 
39.         self.harness.add_relation("indico-peers", self.harness.charm.app.name)
40.         redis_broker_relation_id = self.harness.add_relation(
41.             "redis-broker",
42.             "redis-broker",
43.             unit_data={"hostname": "broker-host", "port": "1010"},
44.             app_data={"leader-host": "broker-host"},
45.         )
46.         self.harness.add_relation_unit(redis_broker_relation_id, "redis-broker/1")
47.         self.harness.update_relation_data(
48.             redis_broker_relation_id,
49.             "redis-broker/1",
50.             {"hostname": "broker-host-1", "port": "1010"},
51.         )
52.         redis_cache_relation_id = self.harness.add_relation(
53.             "redis-cache",
54.             "redis-cache",
55.             unit_data={"hostname": "cache-host", "port": "1011"},
56.             app_data={"leader-host": "cache-host"},
57.         )
58.         self.harness.add_relation_unit(redis_cache_relation_id, "redis-cache/1")
59.         self.harness.update_relation_data(
60.             redis_cache_relation_id,
61.             "redis-cache/1",
62.             {"hostname": "cache-host-1", "port": "1011"},
63.         )
64. 
65.         self.nginx_route_relation_id = self.harness.add_relation(  # pylint: disable=W0201
66.             "nginx-route", "ingress"
67.         )
68. 
69.     def is_ready(self, apps: List[str]):
70.         """Waiting for all applications to be ready.
71. 
72.         Args:
73.             apps: List of applications.
74.         """
75.         for app_name in apps:
76.             self.harness.container_pebble_ready(app_name)
77. 
78.     def set_relations_and_leader(self):
79.         """Set Indico relations, the leader and check container readiness."""
80.         self.set_up_all_relations()
81.         self.harness.set_leader(True)
82.         self.is_ready(
83.             [
84.                 "indico",
85.                 "indico-nginx",
86.             ]
87.         )
88.
```

</details>


### ✅ `bash`

**Search for any run_action or emit patterns in tests**

$ grep -r "run_action\|\.emit(" /tmp/ops-upgrade-experiment/indico-operator__action-testing__C1pf/tests/ 2>/dev/null | head -20

<details>
<summary>9 lines</summary>

```
/tmp/ops-upgrade-experiment/indico-operator__action-testing__C1pf/tests/integration/conftest.py:    action_sync_s3_credentials = await s3_integrator.units[0].run_action(  # type: ignore
/tmp/ops-upgrade-experiment/indico-operator__action-testing__C1pf/tests/integration/test_s3.py:    action: juju.action.Action = await s3_integrator.units[0].run_action(  # type: ignore
/tmp/ops-upgrade-experiment/indico-operator__action-testing__C1pf/tests/integration/test_actions.py:    action: juju.action.Action = await app.units[0].run_action(  # type: ignore
/tmp/ops-upgrade-experiment/indico-operator__action-testing__C1pf/tests/integration/test_actions.py:    action2: juju.action.Action = await app.units[0].run_action(  # type: ignore
/tmp/ops-upgrade-experiment/indico-operator__action-testing__C1pf/tests/integration/test_actions.py:    action_anonymize: juju.action.Action = await app.units[0].run_action(  # type: ignore
/tmp/ops-upgrade-experiment/indico-operator__action-testing__C1pf/tests/integration/test_actions.py:    action_anonymize: juju.action.Action = await app.units[0].run_action(  # type: ignore
/tmp/ops-upgrade-experiment/indico-operator__action-testing__C1pf/tests/unit_harness/test_database_observer.py:    harness.charm.database.database.on.database_created.emit(relation)
/tmp/ops-upgrade-experiment/indico-operator__action-testing__C1pf/tests/unit_harness/test_database_observer.py:    harness.charm.database.database.on.endpoints_changed.emit(relation)
<exited with exit code 0>
```

</details>


### 💬 Copilot

Perfect! Now I have all the information. Let me compile the complete answer:

## Exploration Summary

### 1. **Actions Defined in actions.yaml**

The charm defines three actions:

1. **`refresh-external-resources`** - Pull changes from customization repository, reload uWSGI and upgrade external plugins (no parameters)
2. **`add-admin`** - Add an admin to Indico
   - Parameters: `email` (string), `password` (string)
   - Required: both email and password
3. **`anonymize-user`** - Anonymize stored personal data to facilitate GDPR compliance
   - Parameters: `email` (string) - User email or comma-separated list (max 50 emails)
   - Required: email

### 2. **Current Action Test Patterns**

The codebase uses **direct action handler method invocation** rather than ops testing framework's `harness.run_action()`:

- **Direct method calls with mocked events**: Tests manually call the action handler methods (e.g., `charm._add_admin_action(event)`) instead of using `harness.run_action()`
- **Manual ActionEvent mocks**: Creates `MagicMock(spec=ActionEvent)` with `params` dict and manually implements `event.fail()` and `event.set_results()`
- **Container exec mocking**: Uses `@patch.object(Container, "exec")` to mock command execution
- **Integration tests use real `run_action()`**: Only integration tests use the proper `await app.units[0].run_action()` API

**NO instances of:**
- `harness._backend._action_results`
- `harness.charm.on.*_action.emit()`
- `harness.run_action()` in unit tests

### 3. **Test Files Containing Action Tests**

- `/tmp/ops-upgrade-experiment/indico-operator__action-testing__C1pf/tests/unit_harness/test_actions.py` (unit tests)
- `/tmp/ops-upgrade-experiment/indico-operator__action-testing__C1pf/tests/integration/test_actions.py` (integration tests)

### 4. **Action Handler Method Names in src/charm.py**

- `_refresh_external_resources_action(self, event: ActionEvent)` - Line 836
- `_add_admin_action(self, event: ActionEvent)` - Line 898
- `_anonymize_user_action(self, event: ActionEvent)` - Line 976

### 5. **Full Content of Action Test Functions**

#### Unit Test: `test_add_admin()`
```python
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

    def event_store_failure(failure_message: str) -\> None:
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
```

#### Unit Test: `test_add_admin_fail()`
```python
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

    def event_store_failure(failure_message: str) -\> None:
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
```

#### Unit Test: `test_anonymize_user()`
```python
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
```

#### Unit Test: `test_anonymize_user_list()`
```python
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
```

#### Unit Test: `test_anonymize_user_maximum_reached()`
```python
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
```

#### Unit Test: `test_anonymize_user_fail()`
```python
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
```

#### Integration Test: `test_anonymize_user()`
```python
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
```

#### Integration Test: `test_anonymize_user_fail()`
```python
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
```

### 6. **Version of ops**

From `/tmp/ops-upgrade-experiment/indico-operator__action-testing__C1pf/requirements.txt`:
- **`ops\>=2.0.0,\<3.0.0`**


---

<sub>⏱️ 1m 12s</sub>

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/indico-operator__action-testing__C1pf/tests/unit_harness/test_actions.py.**

/tmp/ops-upgrade-experiment/indico-operator__action-testing__C1pf/tests/unit_harness/test_actions.py

<details>
<summary>394 lines</summary>

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
21.     """Indico charm unit tests."""
22. 
23.     @patch.object(Container, "exec")
24.     @patch("charm.secrets")
25.     def test_refresh_external_resources_when_customization_and_plugins_set(
26.         self, mock_secrets, mock_exec
27.     ):
28.         """
29.         arrange: charm created and relations established
30.         act: configure the external resources and trigger the refresh action
31.         assert: the customization sources are pulled and the plugins upgraded
32.         """
33.         mock_exec.return_value = MagicMock(wait_output=MagicMock(return_value=("", None)))
34.         mock_secrets.token_hex.return_value = "123456"
35.         self.harness.disable_hooks()
36.         self.set_relations_and_leader()
37.         self.harness.update_config(
38.             {
39.                 "customization_sources_url": "https://example.com/custom",
40.                 "external_plugins": "git+https://example.git/#subdirectory=themes_cern",
41.             }
42.         )
43. 
44.         charm: IndicoOperatorCharm = typing.cast(IndicoOperatorCharm, self.harness.charm)
45.         with self.assertLogs(level="INFO") as logger:
46.             charm._refresh_external_resources(MagicMock())
47. 
48.             mock_exec.assert_any_call(
49.                 ["git", "pull"],
50.                 working_dir="/srv/indico/custom",
51.                 user="indico",
52.                 environment={},
53.             )
54.             mock_exec.assert_any_call(
55.                 [
56.                     "pip",
57.                     "install",
58.                     "--upgrade",
59.                     "-c",
60.                     "/tmp/constraints-123456.txt",  # nosec B108
61.                     "git+https://example.git/#subdirectory=themes_cern",
62.                 ],
63.                 environment={},
64.             )
65.             expected_logs = [
66.                 "INFO:charm:About to run: pip install --upgrade "
67.                 "-c /tmp/constraints-123456.txt "
68.                 "git+https://example.git/#subdirectory=themes_cern",
69.                 "INFO:charm:Output was: ",
70.             ]
71.             assert logger.output == expected_logs
72. 
73.     @patch.object(Container, "exec")
74.     def test_add_admin(self, mock_exec):
75.         """
76.         arrange: an email and a password
77.         act: when the _on_add_admin_action method is executed
78.         assert: the indico command to add the user is executed with the appropriate parameters.
79.         """
80.         mock_exec.return_value = MagicMock(wait_output=MagicMock(return_value=("", None)))
81. 
82.         self.set_relations_and_leader()
83.         self.harness.disable_hooks()
84. 
85.         container = self.harness.model.unit.get_container("indico")
86. 
87.         charm: IndicoOperatorCharm = typing.cast(IndicoOperatorCharm, self.harness.charm)
88. 
89.         email = "sample@email.com"
90.         password = token_hex(16)
91.         event = MagicMock(spec=ActionEvent)
92.         event.params = {
93.             "email": email,
94.             "password": password,
95.         }
96. 
97.         def event_store_failure(failure_message: str) -> None:
98.             """Define a failure message for the event.
99. 
100.             Args:
101.                 failure_message: failure message content to be defined.
102.             """
103.             event.fail_message = failure_message
104. 
105.         event.fail = event_store_failure
106. 
107.         indico_env_config = charm._get_indico_env_config_str(container)
108.         expected_cmd = [
109.             "/usr/bin/indico",
110.             "autocreate",
111.             "admin",
112.             email,
113.             password,
114.         ]
115. 
116.         charm._add_admin_action(event)
117. 
118.         mock_exec.assert_any_call(
119.             expected_cmd,
120.             user="indico",
121.             working_dir="/srv/indico",
122.             environment=indico_env_config,
123.         )
124. 
125.     @patch.object(Container, "exec")
126.     def test_add_admin_fail(self, mock_exec):
127.         """
128.         arrange: an email and a password
129.         act: when the _on_add_admin_action method is executed
130.         assert: the indico command to add the user is executed with the appropriate parameters.
131.         """
132.         mock_wo = MagicMock(
133.             return_value=("", None),
134.         )
135. 
136.         stdout_mock = "CRASH"
137. 
138.         # I'm disabling unused-argument here because some could be passed to the mock
139.         def mock_wo_side_effect(*args, **kwargs):  # pylint: disable=unused-argument
140.             """Mock wo side effect.
141. 
142.             Args:
143.                 args: Variable list of positional arguments passed to the parent constructor.
144.                 kwargs: a `dict` of the extra arguments passed to the function.
145. 
146.             Returns:
147.                 unittest.mock DEFAULT built-in.
148. 
149.             Raises:
150.                 ExecError: Execution error fired if conditions are met.
151.             """
152.             if isinstance(mock_wo.cmd, list) and "autocreate" in mock_wo.cmd:
153.                 raise ExecError(command=mock_wo.cmd, exit_code=42, stdout=stdout_mock, stderr="")
154.             return DEFAULT
155. 
156.         mock_wo.side_effect = mock_wo_side_effect
157. 
158.         # I'm disabling unused-argument here because some could be passed to the mock
159.         def mock_exec_side_effect(*args, **kwargs):  # pylint: disable=unused-argument
160.             """Mock execution side effect.
161. 
162.             Args:
163.                 args: Variable list of positional arguments passed to the parent constructor.
164.                 kwargs: a `dict` of the extra arguments passed to the function.
165. 
166.             Returns:
167.                 unittest.mock DEFAULT built-in.
168.             """
169.             mock_wo.cmd = args[0]
170.             return DEFAULT
171. 
172.         mock_exec.side_effect = mock_exec_side_effect
173.         mock_exec.return_value = MagicMock(
174.             wait_output=mock_wo,
175.         )
176. 
177.         self.set_relations_and_leader()
178.         self.harness.disable_hooks()
179. 
180.         container = self.harness.model.unit.get_container("indico")
181. 
182.         charm: IndicoOperatorCharm = typing.cast(IndicoOperatorCharm, self.harness.charm)
183. 
184.         email = "sample@email.com"
185.         password = token_hex(16)
186.         event = MagicMock(spec=ActionEvent)
187.         event.params = {
188.             "email": email,
189.             "password": password,
190.         }
191. 
192.         def event_store_failure(failure_message: str) -> None:
193.             """Define a failure message for the event.
194. 
195.             Args:
196.                 failure_message: failure message content to be defined.
197.             """
198.             event.fail_message = failure_message
199. 
200.         event.fail = event_store_failure
201. 
202.         indico_env_config = charm._get_indico_env_config_str(container)
203.         expected_cmd = [
204.             "/usr/bin/indico",
205.             "autocreate",
206.             "admin",
207.             email,
208.             password,
209.         ]
210. 
211.         charm._add_admin_action(event)
212.         assert event.fail_message == f"Failed to create admin {email}: '{stdout_mock}'"
213. 
214.         mock_exec.assert_any_call(
215.             expected_cmd,
216.             user="indico",
217.             working_dir="/srv/indico",
218.             environment=indico_env_config,
219.         )
220. 
221.     def _set_indico(self) -> IndicoOperatorCharm:
222.         """Set Indico Charm
223. 
224.         Returns:
225.             IndicoOperatorCharm: Indico charm configured
226.         """
227.         charm: IndicoOperatorCharm = typing.cast(IndicoOperatorCharm, self.harness.charm)
228.         charm._get_installed_plugins = MagicMock(return_value="")
229.         charm._get_indico_secret_key_from_relation = MagicMock(return_value="")
230.         self.harness.container_pebble_ready("indico")
231.         return charm
232. 
233.     def _anonymize_user(self, emails: str, mock_event: MagicMock, mock_exec: MagicMock):
234.         """Execute anonymize user action
235. 
236.         Args:
237.             emails: email list parameter to be used
238.             mock_event (MagicMock): event mock
239.             mock_exec (MagicMock): Container exec mock
240.         """
241.         charm = self._set_indico()
242.         charm._anonymize_user_action(mock_event)
243. 
244.         def validate_command(email: str):
245.             """Check if the command was called.
246. 
247.             Args:
248.                 email: email parameter to be used
249.             """
250.             # Check if command was called
251.             expected_cmd = [
252.                 "/usr/bin/indico",
253.                 "anonymize",
254.                 "user",
255.                 email,
256.             ]
257.             container = self.harness.model.unit.get_container("indico")
258.             indico_env_config = charm._get_indico_env_config_str(container)
259.             mock_exec.assert_any_call(
260.                 expected_cmd,
261.                 user="indico",
262.                 working_dir="/srv/indico",
263.                 environment=indico_env_config,
264.             )
265. 
266.         for email in emails.split(","):
267.             validate_command(email)
268. 
269.         # Check if event results was properly set
270.         mock_event.set_results.assert_called_with({"user": f"{emails}", "output": f"{emails}"})
271. 
272.     @patch.object(Container, "exec")
273.     def test_anonymize_user(self, mock_exec):
274.         """
275.         arrange: an email
276.         act: when the _on_anonymize_user_action method is executed
277.         assert: the indico command to anonymize the user is executed with the appropriate
278.             parameters and the event results is set as expected
279.         """
280.         email = token_hex(16)
281.         mock_exec.return_value = MagicMock(wait_output=MagicMock(return_value=(f"{email}", None)))
282.         mock_event = MagicMock(spec=ActionEvent)
283.         mock_event.params = {
284.             "email": email,
285.         }
286.         self._anonymize_user(email, mock_event, mock_exec)
287. 
288.     def _generate_emails_mock(self, emails: str) -> typing.Iterator[MagicMock]:
289.         """Generate list of mocks accordingly to list of emails
290. 
291.         Args:
292.             emails (str): list of emails
293. 
294.         Yields:
295.             Iterator[MagicMock]: Mock of exec that returns email
296.         """
297.         for email in emails.split(EMAIL_LIST_SEPARATOR):
298.             wait_output = MagicMock(return_value=(email, None))
299.             yield MagicMock(wait_output=wait_output)
300. 
301.     @patch.object(Container, "exec")
302.     def test_anonymize_user_list(self, mock_exec):
303.         """
304.         arrange: an list of 5 emails
305.         act: when the _on_anonymize_user_action method is executed
306.         assert: the indico command to anonymize the user is executed with the appropriate
307.             parameters and the event results is set as expected
308.         """
309.         emails = EMAIL_LIST_SEPARATOR.join([token_hex(16) for _ in range(5)])
310.         mock_event = MagicMock(spec=ActionEvent)
311.         mock_event.params = {
312.             "email": emails,
313.         }
314.         mock_exec.side_effect = list(self._generate_emails_mock(emails))
315.         self._anonymize_user(emails, mock_event, mock_exec)
316. 
317.     @patch.object(Container, "exec")
318.     def test_anonymize_user_maximum_reached(self, mock_exec):
319.         """
320.         arrange: an list of 51 emails
321.         act: when the _on_anonymize_user_action method is executed
322.         assert: the indico command to anonymize the user is executed with the appropriate
323.             parameters and the event results is set as expected
324.         """
325.         charm = self._set_indico()
326.         emails = EMAIL_LIST_SEPARATOR.join([token_hex(16) for _ in range(EMAIL_LIST_MAX + 1)])
327.         mock_event = MagicMock(spec=ActionEvent)
328.         mock_event.params = {
329.             "email": emails,
330.         }
331.         mock_exec.return_value = MagicMock(wait_output=MagicMock(return_value=("", None)))
332. 
333.         charm._anonymize_user_action(mock_event)
334.         expected_argument = (
335.             f"Failed to anonymize user: List of more than {EMAIL_LIST_MAX} emails are not allowed"
336.         )
337.         # Pylint does not understand that the mock supports this call
338.         mock_event.fail.assert_called_with(expected_argument)  # pylint: disable=no-member
339. 
340.     @patch.object(Container, "exec")
341.     def test_anonymize_user_fail(self, mock_exec):
342.         """
343.         arrange: an email
344.         act: when the _on_anonymize_user_action method is executed
345.         assert: the indico command to anonymize the user is executed with the appropriate
346.             parameters and the event results is set as expected
347.         """
348.         charm = self._set_indico()
349. 
350.         # Set Mock
351.         email = token_hex(16)
352.         error_msg = "Execution error"
353.         expected_cmd = [
354.             "/usr/bin/indico",
355.             "anonymize",
356.             "user",
357.             email,
358.         ]
359.         expected_exception = ExecError(
360.             command=" ".join(expected_cmd), exit_code=42, stdout=f"{error_msg}", stderr=""
361.         )
362.         wait_output = MagicMock(side_effect=expected_exception)
363.         mock_exec.return_value = MagicMock(wait_output=wait_output)
364.         # Set and trigger the event
365.         mock_event = MagicMock(spec=ActionEvent)
366.         mock_event.params = {
367.             "email": email,
368.         }
369. 
370.         charm._anonymize_user_action(mock_event)
371. 
372.         # Check if command was called
373.         container = self.harness.model.unit.get_container("indico")
374.         indico_env_config = charm._get_indico_env_config_str(container)
375.         mock_exec.assert_any_call(
376.             expected_cmd,
377.             user="indico",
378.             working_dir="/srv/indico",
379.             environment=indico_env_config,
380.         )
381. 
382.         # Check if event fail was properly set
383.         expected_argument = "Failed to anonymize one or more users, please verify the results."
384.         # Pylint does not understand that the mock supports this call
385.         mock_event.fail.assert_called_with(expected_argument)  # pylint: disable=no-member
386. 
387.         # Check if event results was properly set
388.         mock_event.set_results.assert_called_with(
389.             {
390.                 "user": f"{email}",
391.                 "output": f"Failed to anonymize user {email}: '{error_msg}'",
392.             }
393.         )
394.
```

</details>


---

<sub>⏱️ 1m 12s</sub>

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/indico-operator__action-testing__C1pf/requirements.txt.**

/tmp/ops-upgrade-experiment/indico-operator__action-testing__C1pf/requirements.txt

```
1. pydantic==1.10.26
2. ops>=2.0.0,<3.0.0
3. 
```


---

<sub>⏱️ 1m 20s</sub>

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/indico-operator__action-testing__C1pf/tests/unit_harness/test_base.py.**

/tmp/ops-upgrade-experiment/indico-operator__action-testing__C1pf/tests/unit_harness/test_base.py

<details>
<summary>88 lines</summary>

```
1. # Copyright 2025 Canonical Ltd.
2. # See LICENSE file for licensing details.
3. 
4. """Indico charm unit tests."""
5. 
6. # pylint:disable=protected-access
7. 
8. import unittest
9. from typing import List
10. 
11. from ops.testing import Harness
12. 
13. from charm import IndicoOperatorCharm
14. 
15. 
16. class TestBase(unittest.TestCase):
17.     """Indico charm unit tests."""
18. 
19.     def setUp(self):
20.         """Set up test environment."""
21.         self.harness = Harness(IndicoOperatorCharm)
22.         self.addCleanup(self.harness.cleanup)
23.         self.harness.begin()
24. 
25.     def set_up_all_relations(self):
26.         """Set up all relations for the charm."""
27.         # pylint: disable=duplicate-code
28.         self.harness.add_relation(
29.             "database",
30.             "postgresql",
31.             app_data={
32.                 "database": "indico",
33.                 "endpoints": "postgresql-k8s-primary.local:5432",
34.                 "password": "somepass",  # nosec
35.                 "username": "user1",
36.             },
37.         )
38. 
39.         self.harness.add_relation("indico-peers", self.harness.charm.app.name)
40.         redis_broker_relation_id = self.harness.add_relation(
41.             "redis-broker",
42.             "redis-broker",
43.             unit_data={"hostname": "broker-host", "port": "1010"},
44.             app_data={"leader-host": "broker-host"},
45.         )
46.         self.harness.add_relation_unit(redis_broker_relation_id, "redis-broker/1")
47.         self.harness.update_relation_data(
48.             redis_broker_relation_id,
49.             "redis-broker/1",
50.             {"hostname": "broker-host-1", "port": "1010"},
51.         )
52.         redis_cache_relation_id = self.harness.add_relation(
53.             "redis-cache",
54.             "redis-cache",
55.             unit_data={"hostname": "cache-host", "port": "1011"},
56.             app_data={"leader-host": "cache-host"},
57.         )
58.         self.harness.add_relation_unit(redis_cache_relation_id, "redis-cache/1")
59.         self.harness.update_relation_data(
60.             redis_cache_relation_id,
61.             "redis-cache/1",
62.             {"hostname": "cache-host-1", "port": "1011"},
63.         )
64. 
65.         self.nginx_route_relation_id = self.harness.add_relation(  # pylint: disable=W0201
66.             "nginx-route", "ingress"
67.         )
68. 
69.     def is_ready(self, apps: List[str]):
70.         """Waiting for all applications to be ready.
71. 
72.         Args:
73.             apps: List of applications.
74.         """
75.         for app_name in apps:
76.             self.harness.container_pebble_ready(app_name)
77. 
78.     def set_relations_and_leader(self):
79.         """Set Indico relations, the leader and check container readiness."""
80.         self.set_up_all_relations()
81.         self.harness.set_leader(True)
82.         self.is_ready(
83.             [
84.                 "indico",
85.                 "indico-nginx",
86.             ]
87.         )
88.
```

</details>


---

<sub>⏱️ 1m 20s</sub>

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/indico-operator__action-testing__C1pf/src/charm.py.**

/tmp/ops-upgrade-experiment/indico-operator__action-testing__C1pf/src/charm.py (lines 830-1020)

<details>
<summary>175 lines</summary>

```
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
846.         """Handle leader-elected event."""
847.         peer_relation = self.model.get_relation("indico-peers")
848.         secret_value = repr(os.urandom(32))
849.         if (
850.             peer_relation
851.             and not self._has_secrets()
852.             and not peer_relation.data[self.app].get("secret-key")
853.         ):
854.             peer_relation.data[self.app].update({"secret-key": secret_value})
855.         elif (
856.             peer_relation
857.             and self._has_secrets()
858.             and not peer_relation.data[self.app].get("secret-id")
859.         ):
860.             secret = self.app.add_secret({"secret-key": secret_value})
861.             peer_relation.data[self.app].update({"secret-id": typing.cast(str, secret.id)})
862.         if peer_relation and not peer_relation.data[self.app].get("celery-unit"):
863.             peer_relation.data[self.app].update({"celery-unit": self.unit.name})
864. 
865.     def _on_peer_relation_departed(self, event: RelationDepartedEvent) -> None:
866.         """Handle the peer relation departed event.
867. 
868.         Args:
869.             event: the event triggering the handler.
870.         """
871.         peer_relation = self.model.get_relation("indico-peers")
872.         if (
873.             self.unit.is_leader()
874.             and peer_relation
875.             and event.departing_unit
876.             and peer_relation.data[self.app].get("celery-unit") == event.departing_unit.name
877.         ):
878.             if self.unit != event.departing_unit:
879.                 peer_relation.data[self.app].update({"celery-unit": self.unit.name})
880.                 container = self.unit.get_container("indico")
881.                 if self._are_relations_ready(event) and container.can_connect():
882.                     self._config_pebble(container)
883.             else:
884.                 # Leadership election will select a new celery-unit
885.                 peer_relation.data[self.app].update({"celery-unit": ""})
886. 
887.     def _has_secrets(self) -> bool:
888.         """Check if current Juju version supports secrets.
889. 
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
1001. 
1002. if __name__ == "__main__":  # pragma: no cover
1003.     main(IndicoOperatorCharm, use_juju_for_storage=True)
1004.
```

</details>


---

<sub>⏱️ 2m 37s</sub>

### ✅ `bash`

**Check installed ops version**

$ cd /tmp/ops-upgrade-experiment/indico-operator__action-testing__C1pf && pip show ops 2>/dev/null | head -5 && python3 -c "import ops; print(ops.__version__)" 2>/dev/null || echo "ops not installed"

<details>
<summary>7 lines</summary>

```
Name: ops
Version: 3.7.0
Summary: The Python library behind great charms
Home-page: 
Author: The Charm Tech team at Canonical Ltd.
3.7.0
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 2m 43s</sub>

### ✅ `bash`

**Check ActionFailed API**

$ python3 -c "from ops.testing import ActionFailed; import inspect; print(inspect.getsource(ActionFailed))"

<details>
<summary>28 lines</summary>

```
class ActionFailed(Exception):  # noqa: N818 (name doesn't end with "Error")
    """Raised when :code:`event.fail()` is called during an action handler."""

    message: str
    """Optional details of the failure, as provided by :meth:`ops.ActionEvent.fail`."""

    output: ActionOutput
    """Any logs and results set by the Charm.

    When using Context.run, both logs and results will be empty - these
    can be found in Context.action_logs and Context.action_results.
    """

    state: State | None
    """The Juju state after the action has been run.

    When using Harness.run_action, this will be ``None``.
    """

    def __init__(
        self,
        message: str,
        output: ActionOutput | None = None,
        *,
        state: State | None = None,
    ):
        self.message = message
        self.output = output or ActionOutput([], {})
        self.state = state

    def __str__(self):
        if self.message:
            return self.message
        return 'Event handler called `fail()` with no additional details.'
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 2m 50s</sub>

### 💬 Copilot

Now I have all the information I need. Let me rewrite the tests:

---

<sub>⏱️ 2m 50s</sub>

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/indico-operator__action-testing__C1pf/src/charm.py.**

/tmp/ops-upgrade-experiment/indico-operator__action-testing__C1pf/src/charm.py (lines 780-845)

<details>
<summary>66 lines</summary>

```
780.         """
781.         current_remote_url = self._get_current_customization_url()
782.         if current_remote_url != self.config["customization_sources_url"]:
783.             logging.debug(
784.                 "Removing old contents from directory %s. Previous repository: '%s'",
785.                 INDICO_CUSTOMIZATION_DIR,
786.                 current_remote_url,
787.             )
788.             process = container.exec(["rm", "-rf", INDICO_CUSTOMIZATION_DIR], user="indico")
789.             process.wait_output()
790.             process = container.exec(["mkdir", INDICO_CUSTOMIZATION_DIR], user="indico")
791.             process.wait_output()
792.             if self.config["customization_sources_url"]:
793.                 logging.debug(
794.                     "New URL repo for customization %s. Cloning contents",
795.                     self.config["customization_sources_url"],
796.                 )
797.                 self._exec_cmd_in_custom_dir(
798.                     container,
799.                     [
800.                         "git",
801.                         "clone",
802.                         typing.cast(str, self.config["customization_sources_url"]),
803.                         ".",
804.                     ],
805.                 )
806. 
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

<sub>⏱️ 4m 32s</sub>

### ✅ `bash`

**Check tox config**

$ cat /tmp/ops-upgrade-experiment/indico-operator__action-testing__C1pf/tox.ini

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

<sub>⏱️ 5m 13s</sub>

### 💬 Copilot

Now I have everything I need. The unit tests use `ops[testing]==2.21.1` (which supports `run_action`). Let me rewrite the tests:

---

<sub>⏱️ 5m 13s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/indico-operator__action-testing__C1pf/tests/unit_harness/test_actions.py.**

/tmp/ops-upgrade-experiment/indico-operator__action-testing__C1pf/tests/unit_harness/test_actions.py

```
File /tmp/ops-upgrade-experiment/indico-operator__action-testing__C1pf/tests/unit_harness/test_actions.py updated with changes.
```


---

<sub>⏱️ 5m 32s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/indico-operator__action-testing__C1pf/tests/unit_harness/test_actions.py.**

/tmp/ops-upgrade-experiment/indico-operator__action-testing__C1pf/tests/unit_harness/test_actions.py

```
File /tmp/ops-upgrade-experiment/indico-operator__action-testing__C1pf/tests/unit_harness/test_actions.py updated with changes.
```


---

<sub>⏱️ 5m 45s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/indico-operator__action-testing__C1pf/tests/unit_harness/test_actions.py.**

/tmp/ops-upgrade-experiment/indico-operator__action-testing__C1pf/tests/unit_harness/test_actions.py

```
File /tmp/ops-upgrade-experiment/indico-operator__action-testing__C1pf/tests/unit_harness/test_actions.py updated with changes.
```


---

<sub>⏱️ 6m 3s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/indico-operator__action-testing__C1pf/tests/unit_harness/test_actions.py.**

/tmp/ops-upgrade-experiment/indico-operator__action-testing__C1pf/tests/unit_harness/test_actions.py

```
File /tmp/ops-upgrade-experiment/indico-operator__action-testing__C1pf/tests/unit_harness/test_actions.py updated with changes.
```


---

<sub>⏱️ 6m 16s</sub>

### 💬 Copilot

Now update the helper and the anonymize tests:

---

<sub>⏱️ 6m 16s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/indico-operator__action-testing__C1pf/tests/unit_harness/test_actions.py.**

/tmp/ops-upgrade-experiment/indico-operator__action-testing__C1pf/tests/unit_harness/test_actions.py

```
File /tmp/ops-upgrade-experiment/indico-operator__action-testing__C1pf/tests/unit_harness/test_actions.py updated with changes.
```


---

<sub>⏱️ 6m 24s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/indico-operator__action-testing__C1pf/tests/unit_harness/test_actions.py.**

/tmp/ops-upgrade-experiment/indico-operator__action-testing__C1pf/tests/unit_harness/test_actions.py

```
File /tmp/ops-upgrade-experiment/indico-operator__action-testing__C1pf/tests/unit_harness/test_actions.py updated with changes.
```


---

<sub>⏱️ 6m 32s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/indico-operator__action-testing__C1pf/tests/unit_harness/test_actions.py.**

/tmp/ops-upgrade-experiment/indico-operator__action-testing__C1pf/tests/unit_harness/test_actions.py

```
File /tmp/ops-upgrade-experiment/indico-operator__action-testing__C1pf/tests/unit_harness/test_actions.py updated with changes.
```


---

<sub>⏱️ 6m 41s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/indico-operator__action-testing__C1pf/tests/unit_harness/test_actions.py.**

/tmp/ops-upgrade-experiment/indico-operator__action-testing__C1pf/tests/unit_harness/test_actions.py

```
File /tmp/ops-upgrade-experiment/indico-operator__action-testing__C1pf/tests/unit_harness/test_actions.py updated with changes.
```


---

<sub>⏱️ 6m 56s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/indico-operator__action-testing__C1pf/tests/unit_harness/test_actions.py.**

/tmp/ops-upgrade-experiment/indico-operator__action-testing__C1pf/tests/unit_harness/test_actions.py

```
File /tmp/ops-upgrade-experiment/indico-operator__action-testing__C1pf/tests/unit_harness/test_actions.py updated with changes.
```


---

<sub>⏱️ 7m 6s</sub>

### 💬 Copilot

Now let's run the unit tests to verify:

---

<sub>⏱️ 7m 7s</sub>

### ✅ `bash`

**Run action unit tests**

$ cd /tmp/ops-upgrade-experiment/indico-operator__action-testing__C1pf && python -m pytest tests/unit_harness/test_actions.py -v 2>&1

```
bash: python: command not found
<exited with exit code 127>
```


---

<sub>⏱️ 7m 15s</sub>

### ✅ `bash`

**Run action unit tests with python3**

$ cd /tmp/ops-upgrade-experiment/indico-operator__action-testing__C1pf && PYTHONPATH=.:lib:src python3 -m pytest tests/unit_harness/test_actions.py -v 2>&1

<details>
<summary>37 lines</summary>

```
================================================= test session starts ==================================================
platform linux -- Python 3.12.3, pytest-9.0.2, pluggy-1.6.0 -- /usr/bin/python3
cachedir: .pytest_cache
hypothesis profile 'default'
rootdir: /tmp/ops-upgrade-experiment/indico-operator__action-testing__C1pf
configfile: pyproject.toml
plugins: jubilant-1.1, interface-tester-3.4.1, hypothesis-6.151.9, asyncio-0.21.2, anyio-4.12.1, pytest_httpserver-1.1.5
asyncio: mode=Mode.STRICT
collecting ... collected 7 items                                                                                                      

tests/unit_harness/test_actions.py::TestActions::test_add_admin PASSED                                           [ 14%]
tests/unit_harness/test_actions.py::TestActions::test_add_admin_fail PASSED                                      [ 28%]
tests/unit_harness/test_actions.py::TestActions::test_anonymize_user PASSED                                      [ 42%]
tests/unit_harness/test_actions.py::TestActions::test_anonymize_user_fail PASSED                                 [ 57%]
tests/unit_harness/test_actions.py::TestActions::test_anonymize_user_list PASSED                                 [ 71%]
tests/unit_harness/test_actions.py::TestActions::test_anonymize_user_maximum_reached PASSED                      [ 85%]
tests/unit_harness/test_actions.py::TestActions::test_refresh_external_resources_when_customization_and_plugins_set PASSED [100%]

=================================================== warnings summary ===================================================
tests/unit_harness/test_actions.py::TestActions::test_add_admin
tests/unit_harness/test_actions.py::TestActions::test_add_admin_fail
tests/unit_harness/test_actions.py::TestActions::test_anonymize_user
tests/unit_harness/test_actions.py::TestActions::test_anonymize_user_fail
tests/unit_harness/test_actions.py::TestActions::test_anonymize_user_list
tests/unit_harness/test_actions.py::TestActions::test_anonymize_user_maximum_reached
tests/unit_harness/test_actions.py::TestActions::test_refresh_external_resources_when_customization_and_plugins_set
  /tmp/ops-upgrade-experiment/indico-operator__action-testing__C1pf/tests/unit_harness/test_base.py:21: PendingDeprecationWarning: Harness is deprecated. For the recommended approach, see: https://documentation.ubuntu.com/ops/latest/howto/write-unit-tests-for-a-charm/
    self.harness = Harness(IndicoOperatorCharm)

tests/unit_harness/test_actions.py::TestActions::test_add_admin
tests/unit_harness/test_actions.py::TestActions::test_add_admin_fail
tests/unit_harness/test_actions.py::TestActions::test_refresh_external_resources_when_customization_and_plugins_set
  /tmp/ops-upgrade-experiment/indico-operator__action-testing__C1pf/lib/charms/data_platform_libs/v0/data_interfaces.py:1160: DeprecationWarning: JujuVersion.from_environ() is deprecated, use self.model.juju_version instead
    self._jujuversion = JujuVersion.from_environ()

tests/unit_harness/test_actions.py: 13 warnings
  /tmp/ops-upgrade-experiment/indico-operator__action-testing__C1pf/src/charm.py:893: DeprecationWarning: JujuVersion.from_environ() is deprecated, use self.model.juju_version instead
    juju_version = JujuVersion.from_environ()

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
============================================ 7 passed, 23 warnings in 0.17s ============================================
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 7m 21s</sub>

### 💬 Copilot

All 7 tests pass. Let me also verify the full test suite isn't broken:

---

<sub>⏱️ 7m 22s</sub>

### ✅ `bash`

**Run all unit tests**

$ cd /tmp/ops-upgrade-experiment/indico-operator__action-testing__C1pf && PYTHONPATH=.:lib:src python3 -m pytest tests/unit_harness/ -v --tb=short 2>&1 | tail -20

<details>
<summary>17 lines</summary>

```
tests/unit_harness/test_s3_observer.py::test_credentials_gone_emits_config_changed_event_and_updates_charm_state
  /tmp/ops-upgrade-experiment/indico-operator__action-testing__C1pf/tests/unit_harness/test_s3_observer.py:78: PendingDeprecationWarning: Harness is deprecated. For the recommended approach, see: https://documentation.ubuntu.com/ops/latest/howto/write-unit-tests-for-a-charm/
    harness = Harness(ObservedCharm, meta=REQUIRER_METADATA)

tests/unit_harness/test_saml_observer.py::test_saml_related_emits_config_changed_event_and_updates_charm_state
  /tmp/ops-upgrade-experiment/indico-operator__action-testing__C1pf/tests/unit_harness/test_saml_observer.py:66: PendingDeprecationWarning: Harness is deprecated. For the recommended approach, see: https://documentation.ubuntu.com/ops/latest/howto/write-unit-tests-for-a-charm/
    harness = Harness(ObservedCharm, meta=REQUIRER_METADATA)

tests/unit_harness/test_smtp_observer.py::test_smtp_related_emits_config_changed_event_and_updates_charm_state
  /tmp/ops-upgrade-experiment/indico-operator__action-testing__C1pf/tests/unit_harness/test_smtp_observer.py:63: PendingDeprecationWarning: Harness is deprecated. For the recommended approach, see: https://documentation.ubuntu.com/ops/latest/howto/write-unit-tests-for-a-charm/
    harness = Harness(ObservedCharm, meta=REQUIRER_METADATA)

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ============================
FAILED tests/unit_harness/test_core.py::TestCore::test_config_changed - pydan...
FAILED tests/unit_harness/test_core.py::TestCore::test_config_changed_when_saml_groups_plugin_installed
FAILED tests/unit_harness/test_state.py::test_config_from_charm_env - pydanti...
FAILED tests/unit_harness/test_state.py::test_s3_config_get_connection_string_without_host
================== 4 failed, 37 passed, 88 warnings in 0.51s ===================
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 7m 30s</sub>

### 💬 Copilot

The 4 failing tests are pre-existing failures unrelated to my changes (pydantic issues in `test_core.py` and `test_state.py`). All 7 action tests pass.

Let me do a final review of the rewritten file:

---

<sub>⏱️ 7m 30s</sub>

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/indico-operator__action-testing__C1pf/tests/unit_harness/test_actions.py.**

/tmp/ops-upgrade-experiment/indico-operator__action-testing__C1pf/tests/unit_harness/test_actions.py

<details>
<summary>333 lines</summary>

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
12. import pytest
13. from ops.model import Container
14. from ops.pebble import ExecError
15. from ops.testing import ActionFailed
16. 
17. from charm import EMAIL_LIST_MAX, EMAIL_LIST_SEPARATOR, IndicoOperatorCharm
18. from tests.unit_harness.test_base import TestBase
19. 
20. 
21. class TestActions(TestBase):
22.     """Indico charm unit tests."""
23. 
24.     @patch.object(Container, "exec")
25.     @patch("charm.secrets")
26.     def test_refresh_external_resources_when_customization_and_plugins_set(
27.         self, mock_secrets, mock_exec
28.     ):
29.         """
30.         arrange: charm created and relations established
31.         act: configure the external resources and trigger the refresh action
32.         assert: the customization sources are pulled and the plugins upgraded
33.         """
34.         mock_exec.return_value = MagicMock(wait_output=MagicMock(return_value=("", None)))
35.         mock_secrets.token_hex.return_value = "123456"
36.         self.harness.disable_hooks()
37.         self.set_relations_and_leader()
38.         self.harness.update_config(
39.             {
40.                 "customization_sources_url": "https://example.com/custom",
41.                 "external_plugins": "git+https://example.git/#subdirectory=themes_cern",
42.             }
43.         )
44. 
45.         with self.assertLogs(level="INFO") as logger:
46.             self.harness.run_action("refresh-external-resources")
47. 
48.             mock_exec.assert_any_call(
49.                 ["git", "pull"],
50.                 working_dir="/srv/indico/custom",
51.                 user="indico",
52.                 environment={},
53.             )
54.             mock_exec.assert_any_call(
55.                 [
56.                     "pip",
57.                     "install",
58.                     "--upgrade",
59.                     "-c",
60.                     "/tmp/constraints-123456.txt",  # nosec B108
61.                     "git+https://example.git/#subdirectory=themes_cern",
62.                 ],
63.                 environment={},
64.             )
65.             expected_logs = [
66.                 "INFO:charm:About to run: pip install --upgrade "
67.                 "-c /tmp/constraints-123456.txt "
68.                 "git+https://example.git/#subdirectory=themes_cern",
69.                 "INFO:charm:Output was: ",
70.             ]
71.             assert logger.output == expected_logs
72. 
73.     @patch.object(Container, "exec")
74.     def test_add_admin(self, mock_exec):
75.         """
76.         arrange: an email and a password
77.         act: when the add-admin action is executed
78.         assert: the indico command to add the user is executed with the appropriate parameters.
79.         """
80.         mock_exec.return_value = MagicMock(wait_output=MagicMock(return_value=("", None)))
81. 
82.         self.set_relations_and_leader()
83. 
84.         container = self.harness.model.unit.get_container("indico")
85.         charm: IndicoOperatorCharm = typing.cast(IndicoOperatorCharm, self.harness.charm)
86. 
87.         email = "sample@email.com"
88.         password = token_hex(16)
89.         indico_env_config = charm._get_indico_env_config_str(container)
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
110.         arrange: an email and a password, and the add-admin command fails
111.         act: when the add-admin action is executed
112.         assert: the action fails with the appropriate message.
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
160. 
161.         container = self.harness.model.unit.get_container("indico")
162.         charm: IndicoOperatorCharm = typing.cast(IndicoOperatorCharm, self.harness.charm)
163. 
164.         email = "sample@email.com"
165.         password = token_hex(16)
166.         indico_env_config = charm._get_indico_env_config_str(container)
167.         expected_cmd = [
168.             "/usr/bin/indico",
169.             "autocreate",
170.             "admin",
171.             email,
172.             password,
173.         ]
174. 
175.         with pytest.raises(ActionFailed) as exc_info:
176.             self.harness.run_action("add-admin", {"email": email, "password": password})
177.         assert exc_info.value.message == f"Failed to create admin {email}: '{stdout_mock}'"
178. 
179.         mock_exec.assert_any_call(
180.             expected_cmd,
181.             user="indico",
182.             working_dir="/srv/indico",
183.             environment=indico_env_config,
184.         )
185. 
186.     def _set_indico(self) -> IndicoOperatorCharm:
187.         """Set Indico Charm
188. 
189.         Returns:
190.             IndicoOperatorCharm: Indico charm configured
191.         """
192.         charm: IndicoOperatorCharm = typing.cast(IndicoOperatorCharm, self.harness.charm)
193.         charm._get_installed_plugins = MagicMock(return_value="")
194.         charm._get_indico_secret_key_from_relation = MagicMock(return_value="")
195.         self.harness.container_pebble_ready("indico")
196.         return charm
197. 
198.     def _anonymize_user(self, emails: str, mock_exec: MagicMock):
199.         """Execute anonymize user action and validate results.
200. 
201.         Args:
202.             emails: email list parameter to be used
203.             mock_exec (MagicMock): Container exec mock
204.         """
205.         charm = self._set_indico()
206.         output = self.harness.run_action("anonymize-user", {"email": emails})
207. 
208.         def validate_command(email: str):
209.             """Check if the command was called.
210. 
211.             Args:
212.                 email: email parameter to be used
213.             """
214.             expected_cmd = [
215.                 "/usr/bin/indico",
216.                 "anonymize",
217.                 "user",
218.                 email,
219.             ]
220.             container = self.harness.model.unit.get_container("indico")
221.             indico_env_config = charm._get_indico_env_config_str(container)
222.             mock_exec.assert_any_call(
223.                 expected_cmd,
224.                 user="indico",
225.                 working_dir="/srv/indico",
226.                 environment=indico_env_config,
227.             )
228. 
229.         for email in emails.split(","):
230.             validate_command(email)
231. 
232.         assert output.results == {"user": f"{emails}", "output": f"{emails}"}
233. 
234.     @patch.object(Container, "exec")
235.     def test_anonymize_user(self, mock_exec):
236.         """
237.         arrange: an email
238.         act: when the anonymize-user action is executed
239.         assert: the indico command to anonymize the user is executed with the appropriate
240.             parameters and the event results is set as expected
241.         """
242.         email = token_hex(16)
243.         mock_exec.return_value = MagicMock(wait_output=MagicMock(return_value=(f"{email}", None)))
244.         self._anonymize_user(email, mock_exec)
245. 
246.     def _generate_emails_mock(self, emails: str) -> typing.Iterator[MagicMock]:
247.         """Generate list of mocks accordingly to list of emails
248. 
249.         Args:
250.             emails (str): list of emails
251. 
252.         Yields:
253.             Iterator[MagicMock]: Mock of exec that returns email
254.         """
255.         for email in emails.split(EMAIL_LIST_SEPARATOR):
256.             wait_output = MagicMock(return_value=(email, None))
257.             yield MagicMock(wait_output=wait_output)
258. 
259.     @patch.object(Container, "exec")
260.     def test_anonymize_user_list(self, mock_exec):
261.         """
262.         arrange: an list of 5 emails
263.         act: when the anonymize-user action is executed
264.         assert: the indico command to anonymize the user is executed with the appropriate
265.             parameters and the event results is set as expected
266.         """
267.         emails = EMAIL_LIST_SEPARATOR.join([token_hex(16) for _ in range(5)])
268.         mock_exec.side_effect = list(self._generate_emails_mock(emails))
269.         self._anonymize_user(emails, mock_exec)
270. 
271.     @patch.object(Container, "exec")
272.     def test_anonymize_user_maximum_reached(self, mock_exec):
273.         """
274.         arrange: an list of 51 emails
275.         act: when the anonymize-user action is executed
276.         assert: the action fails indicating the list limit has been exceeded
277.         """
278.         self._set_indico()
279.         emails = EMAIL_LIST_SEPARATOR.join([token_hex(16) for _ in range(EMAIL_LIST_MAX + 1)])
280.         mock_exec.return_value = MagicMock(wait_output=MagicMock(return_value=("", None)))
281. 
282.         expected_message = (
283.             f"Failed to anonymize user: List of more than {EMAIL_LIST_MAX} emails are not allowed"
284.         )
285.         with pytest.raises(ActionFailed) as exc_info:
286.             self.harness.run_action("anonymize-user", {"email": emails})
287.         assert exc_info.value.message == expected_message
288. 
289.     @patch.object(Container, "exec")
290.     def test_anonymize_user_fail(self, mock_exec):
291.         """
292.         arrange: an email
293.         act: when the anonymize-user action is executed and the command fails
294.         assert: the action fails with the appropriate message and results are set
295.         """
296.         charm = self._set_indico()
297. 
298.         # Set Mock
299.         email = token_hex(16)
300.         error_msg = "Execution error"
301.         expected_cmd = [
302.             "/usr/bin/indico",
303.             "anonymize",
304.             "user",
305.             email,
306.         ]
307.         expected_exception = ExecError(
308.             command=" ".join(expected_cmd), exit_code=42, stdout=f"{error_msg}", stderr=""
309.         )
310.         wait_output = MagicMock(side_effect=expected_exception)
311.         mock_exec.return_value = MagicMock(wait_output=wait_output)
312. 
313.         container = self.harness.model.unit.get_container("indico")
314.         indico_env_config = charm._get_indico_env_config_str(container)
315. 
316.         with pytest.raises(ActionFailed) as exc_info:
317.             self.harness.run_action("anonymize-user", {"email": email})
318. 
319.         mock_exec.assert_any_call(
320.             expected_cmd,
321.             user="indico",
322.             working_dir="/srv/indico",
323.             environment=indico_env_config,
324.         )
325.         assert (
326.             exc_info.value.message
327.             == "Failed to anonymize one or more users, please verify the results."
328.         )
329.         assert exc_info.value.output.results == {
330.             "user": f"{email}",
331.             "output": f"Failed to anonymize user {email}: '{error_msg}'",
332.         }
333.
```

</details>


---

<sub>⏱️ 7m 43s</sub>

### 💬 Copilot

All 7 tests pass. Here's a summary of the changes made to `tests/unit_harness/test_actions.py`:

**Imports:** Removed `from ops.charm import ActionEvent`, added `import pytest` and `from ops.testing import ActionFailed`.

**Per test:**
- `test_refresh_external_resources_*`: Replaced `charm._refresh_external_resources(MagicMock())` with `self.harness.run_action("refresh-external-resources")`.
- `test_add_admin`: Replaced manual `ActionEvent` mock + `charm._add_admin_action(event)` with `self.harness.run_action("add-admin", {...})`. Removed `harness.disable_hooks()`.
- `test_add_admin_fail`: Same replacement, plus checks failure via `pytest.raises(ActionFailed)` instead of a custom `event_store_failure` function.
- `_anonymize_user` helper: Removed `mock_event` parameter; now calls `harness.run_action("anonymize-user", ...)` and asserts `output.results`.
- `test_anonymize_user` / `test_anonymize_user_list`: Removed `mock_event` creation.
- `test_anonymize_user_maximum_reached`: Replaced `charm._anonymize_user_action(mock_event)` + `mock_event.fail.assert_called_with(...)` with `pytest.raises(ActionFailed)`.
- `test_anonymize_user_fail`: Same pattern, plus checks `exc_info.value.output.results` for the results set after the failure.

---

<sub>⏱️ 7m 43s</sub>

### ✅ `task_complete`

**Migrated all action tests in `tests/unit_harness/test_act...**

<details>
<summary>Arguments</summary>

```json
{
  "summary": "Migrated all action tests in `tests/unit_harness/test_actions.py` to use `harness.run_action()`, `ActionOutput`, and `ActionFailed` (ops 2.9+ API). All 7 tests pass."
}
```

</details>

```
Migrated all action tests in `tests/unit_harness/test_actions.py` to use `harness.run_action()`, `ActionOutput`, and `ActionFailed` (ops 2.9+ API). All 7 tests pass.
```


---

<sub>⏱️ 7m 43s</sub>

### ✓ Task Complete

Migrated all action tests in `tests/unit_harness/test_actions.py` to use `harness.run_action()`, `ActionOutput`, and `ActionFailed` (ops 2.9+ API). All 7 tests pass.

---

<sub>Generated by [GitHub Copilot CLI](https://github.com/features/copilot/cli)</sub>
