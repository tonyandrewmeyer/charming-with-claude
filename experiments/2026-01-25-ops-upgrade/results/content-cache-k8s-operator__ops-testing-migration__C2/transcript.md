# 🤖 Copilot CLI Session

> [!NOTE]
> - **Session ID:** `e8acc2e3-0ae3-452a-a2db-2023fdf0c5ed`  
> - **Started:** 4/3/2026, 10:58:42 AM  
> - **Duration:** 14m 57s  
> - **Exported:** 4/3/2026, 11:13:40 AM  

---

<sub>⏱️ 5s</sub>

### 👤 User

ops 2.17.0 introduced ops[testing] extras, exposing Scenario-based testing as ops.testing. This provides a declarative, state-transition-based testing model to replace the deprecated Harness. Learn how to use that feature and update this charm to make use of it.

---

<sub>⏱️ 15s</sub>

### ✅ `task`

**Explore charm test structure**

<details>
<summary>Arguments</summary>

```json
{
  "name": "explore-codebase",
  "agent_type": "explore",
  "description": "Explore charm test structure",
  "prompt": "Explore the repository at /tmp/ops-upgrade-experiment/content-cache-k8s-operator__ops-testing-migration__C2 and answer:\n1. What Python version and ops version are used? (check pyproject.toml, tox.toml, charmcraft.yaml)\n2. What test files exist under tests/? Show full content of each test file.\n3. What does src/ contain? Show the charm source files.\n4. What does the charm do? (check metadata.yaml, config.yaml, actions.yaml)\n5. What testing framework is currently used? (Harness-based or Scenario-based?)\n6. Are there any existing imports from ops.testing or ops.testing.harness?\nPlease provide file contents, not just summaries.",
  "mode": "background"
}
```

</details>

```
Agent started in background with agent_id: explore-codebase. You can use read_agent tool with this agent_id to check status and retrieve results. Instruct the user to use /tasks to manage the background agent.
```


---

<sub>⏱️ 27s</sub>

### ✅ `web_search`

**ops 2.17.0 ops.testing Scenario-based testing API how to use**

<details>
<summary>Arguments</summary>

```json
{
  "query": "ops 2.17.0 ops.testing Scenario-based testing API how to use"
}
```

</details>

````
{"type":"text","text":{"value":"It appears there is no direct, detailed guide from the top results about using the scenario-based testing API in \"ops.testing\" for version 2.17.0 specifically. There may be some confusion around the term \"ops\" since there are various frameworks with \"ops\" in their name. If you are referring to the scenario-based testing API in a particular library (like TensorFlow, RT-Thread, or another operations/testing framework), documentation for scenario-based or behavior-driven testing may differ.\n\n**General Steps for Using a Scenario-based Testing API (commonly found patterns):**\n\n1. **Install the Required Package:** Ensure that you have the `ops` (or relevant framework) library installed for version 2.17.0.\n\n2. **Import the Scenario Testing API:** Typically, you import relevant modules such as:\n```python\nfrom ops.testing import Scenario, given, when, then\n```\n\n3. **Define a Scenario/Test Case:** \n   - Use scenario decorators or classes to define your scenario.\n   - Write given-when-then steps to describe the scenario.\n\n4. **Example Pseudocode:**\n```python\nimport ops.testing as testing\n\nclass MyServiceScenario(testing.Scenario):\n    def setup(self):\n        # Setup context: the state before test\n        self.resource = create_resource()\n\n    def test_scenario(self):\n        # Given initial state\n        self.given(self.resource.state == \"INITIAL\")\n        \n        # When some action is performed\n        self.when(self.resource.perform_action(\"start\"))\n        \n        # Then assert final state\n        self.then(self.resource.state == \"RUNNING\")\n```\n5. **Run the Tests:** Use a test runner (pytest, unittest, built-in runner) to execute your scenarios.\n\n**To Get Official or More Accurate Documentation:**  \n- Find the official documentation or GitHub repository for the `ops.testing` package specific to your technology stack.\n- Look under sections labeled \"Scenario Testing\", \"Behavior Driven Testing\", or \"ops.testing\" API.\n\n**If you specify which 'ops' framework (context: Python ML, cloud ops, embedded, etc.)** you’re using, I can provide you with framework-specific instructions or examples.\n\n**Summary:**  \n- Import the scenario-based APIs.\n- Define setup, given, when, then steps.\n- Use your framework’s recommended method to run scenarios.\n\nIf your framework has unique terminology or a custom approach, please provide more details (or a link) and I can help you further! None of the top search results gave step-by-step usage for ops.testing’s scenario-based API for version 2.17.0, so consulting the official documentation or repository for specifics is highly recommended.","annotations":[]},"bing_searches":[{"text":"ops 2.17.0 ops.testing Scenario-based testing API how to use","url":"https://www.bing.com/search?q=ops+2.17.0+ops.testing+Scenario-based+testing+API+how+to+use"}],"annotations":null}
````


---

<sub>⏱️ 33s</sub>

### ❌ `web_fetch`

**https://ops.readthedocs.io/en/latest/ops-testing.html**

<details>
<summary>Arguments</summary>

```json
{
  "url": "https://ops.readthedocs.io/en/latest/ops-testing.html",
  "max_length": 15000
}
```

</details>

```
Error: Failed to fetch https://ops.readthedocs.io/en/latest/ops-testing.html - status code 404
```


---

<sub>⏱️ 32s</sub>

### ✅ `web_fetch`

**https://github.com/canonical/operator/blob/main/ops/testing.py**

<details>
<summary>Arguments</summary>

```json
{
  "url": "https://github.com/canonical/operator/blob/main/ops/testing.py",
  "max_length": 5000
}
```

</details>

<details>
<summary>86 lines</summary>

```
Contents of https://github.com/canonical/operator/blob/main/ops/testing.py:
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
            
            
            
            ](https://github.

<note>Content truncated. Call the fetch tool with a start_index of 5000 to get more content.</note>
```

</details>


---

<sub>⏱️ 41s</sub>

### ✅ `web_fetch`

**https://ops.readthedocs.io/en/latest/reference/ops-testing.html**

<details>
<summary>Arguments</summary>

```json
{
  "max_length": 15000,
  "url": "https://ops.readthedocs.io/en/latest/reference/ops-testing.html"
}
```

</details>

<details>
<summary>130 lines</summary>

```
Contents of https://ops.readthedocs.io/en/latest/reference/ops-testing.html:
Install ops with the `testing` extra to use this API; for example: `pip install ops[testing]`

To learn how to test a particular feature, such as relations, see the relevant how-to guide. For example, How to manage relations > [Test the feature](../../howto/manage-relations/#manage-relations-test-the-feature).

See also:

*   [How to write unit tests for a charm](../../howto/write-unit-tests-for-a-charm/)
    
*   [Testing](../../explanation/testing/) - A summary of types of charm tests
    

State-transition tests (previously called ‘Scenario’ tests) expect you to define the Juju state all at once, define the Juju context against which to test the charm, and fire a single event on the charm to execute its logic. The tests can then assert that the Juju state has changed as expected.

Unlike integration tests, state-transition tests do not deploy your charm with a real Juju controller and model. Instead, your charm code is run using the ‘Scenario’ testing framework. These are the primary form of unit tests that you should write for a charm.

A very simple test, where the charm has no config, no relations, the unit is the leader, and has a start handler that sets the status to active might look like this:

from ops import testing

def test\_base():
    ctx \= testing.Context(MyCharm)
    state \= testing.State(leader\=True)
    out \= ctx.run(ctx.on.start(), state)
    assert out.unit\_status \== testing.ActiveStatus()

These ‘state-transition’ tests give charm authors a way to test how the state changes in reaction to events. They are not necessarily tests of individual methods or functions; they are testing the ‘contract’ of the charm: given a certain state, when a certain event happens, the charm should transition to another state.

Writing these tests should nudge you into thinking of a charm as a black-box ‘input to output’ function. The inputs are:

*   Event ([`CharmEvents`](#ops.testing.CharmEvents "ops.testing.CharmEvents")): why am I, the charm, being executed?
    
*   [`State`](#ops.testing.State "ops.testing.State"): am I the leader? what is my relation data? what is my config?
    
*   [`Context`](#ops.testing.Context "ops.testing.Context"): what relations can I have? what containers can I have?
    

The output is another `State`: the state after the charm has interacted with the mocked Juju model. The output state is the same type of data structure as the input state.

![Transition diagram, with the input state and event on the left, the context including the charm in the centre, and the state out on the right](https://raw.githubusercontent.com/canonical/ops-scenario/main/resources/state-transition-model.png)

Writing unit tests for a charm, then, means verifying that:

*   the output state (as compared with the input state) is as expected
    
*   the charm does not raise uncaught exceptions while handling the event
    

When the testing framework runs the event, the input state isn’t modified. Instead, the output state is a new [`State`](#ops.testing.State "ops.testing.State") object. `State` objects are generally immutable - but be careful when working with `dict` attributes, as they don’t enforce immutability.

A test consists of three broad steps:

*   **Arrange**:
    
    *   declare the context
        
    *   declare the input state
        
    
*   **Act**:
    
    *   run an event (obtain the output state, given the input state and the event)
        
    
*   **Assert**:
    
    *   verify that the output state is what you expect it to be
        
    *   verify that the charm has seen a certain sequence of statuses, events, and juju-log calls
        
    

This API for testing was previously called ‘Scenario’.

_class_ ops.testing.ActionFailed(

_message: [str](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.14)")_,

_output: [ActionOutput](../ops-testing-harness/#ops.testing.ActionOutput "ops.testing.ActionOutput") | [None](https://docs.python.org/3/library/constants.html#None "(in Python v3.14)") \= None_,

_\*_,

_state: [State](#ops.testing.State "ops.testing.State") | [None](https://docs.python.org/3/library/constants.html#None "(in Python v3.14)") \= None_,

)[\[source\]](../../_modules/ops/_private/harness/#ActionFailed)[¶](#ops.testing.ActionFailed "Link to this definition")

Bases: [`Exception`](https://docs.python.org/3/library/exceptions.html#Exception "(in Python v3.14)")

Raised when `event.fail()` is called during an action handler.

message_: [str](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.14)")_[¶](#ops.testing.ActionFailed.message "Link to this definition")

Optional details of the failure, as provided by [`ops.ActionEvent.fail()`](../ops/#ops.ActionEvent.fail "ops.ActionEvent.fail").

output_: [ActionOutput](../ops-testing-harness/#ops.testing.ActionOutput "ops.testing.ActionOutput")_[¶](#ops.testing.ActionFailed.output "Link to this definition")

Any logs and results set by the Charm.

When using Context.run, both logs and results will be empty - these can be found in Context.action\_logs and Context.action\_results.

state_: [State](#ops.testing.State "ops.testing.State") | [None](https://docs.python.org/3/library/constants.html#None "(in Python v3.14)")_[¶](#ops.testing.ActionFailed.state "Link to this definition")

The Juju state after the action has been run.

When using Harness.run\_action, this will be `None`.

_class_ ops.testing.ActiveStatus(_message: [str](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.14)") \= ''_)[\[source\]](../../_modules/scenario/state/#ActiveStatus)[¶](#ops.testing.ActiveStatus "Link to this definition")

Bases: `_EntityStatus`, [`ActiveStatus`](../ops/#ops.ActiveStatus "ops.model.ActiveStatus")

The unit or application is ready and active.

Set this status when the charm is correctly offering all the services it has been asked to offer. If the unit or application is operational but some feature (like high availability) is in a degraded state, set “active” with an appropriate message.

name_: Literal\['active'\]_ _\= 'active'_[¶](#ops.testing.ActiveStatus.name "Link to this definition")

_class_ ops.testing.Address(_value: [str](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.14)")_, _\*_, _hostname: [str](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.14)") \= ''_, _cidr: [str](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.14)") \= ''_)[\[source\]](../../_modules/scenario/state/#Address)[¶](#ops.testing.Address "Link to this definition")

Bases: [`object`](https://docs.python.org/3/library/functions.html#object "(in Python v3.14)")

An address in a Juju network space.

_property_ address[¶](#ops.testing.Address.address "Link to this definition")

A deprecated alias for [`value`](#ops.testing.Address.value "ops.testing.Address.value").

cidr_: [str](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.14)")_ _\= ''_[¶](#ops.testing.Address.cidr "Link to this definition")

The CIDR of the address in [`value`](#ops.testing.Address.value "ops.testing.Address.value").

hostname_: [str](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.14)")_ _\= ''_[¶](#ops.testing.Address.hostname "Link to this definition")

A host name that maps to the address in [`value`](#ops.testing.Address.value "ops.testing.Address.value").

value_: [str](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.14)")_[¶](#ops.testing.Address.value "Link to this definition")

The IP address in the space.

_class_ ops.testing.BindAddress(

_addresses: [Sequence](https://docs.python.org/3/library/collections.abc.html#collections.abc.Sequence "(in Python v3.14)")\[[Address](#ops.testing.Address "scenario.state.Address")\]_,

_\*_,

_interface\_name: [str](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.14)") \= ''_,

_mac\_address: [str](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.14)") | [None](https://docs.python.org/3/library/constants.html#None "(in Python v3.14)") \= None_,

)[\[source\]](../../_modules/scenario/state/#BindAddress)[¶](#ops.testing.BindAddress "Link to this definition")

Bases: [`object`](https://docs.python.org/3/library/functions.html#object "(in Python v3.14)")

An address bound to a network interface in a Juju space.

addresses_: [Sequence](https://docs.python.org/3/library/collections.abc.html#collections.abc.Sequence "(in Python v3.14)")\[[Address](#ops.testing.Address "scenario.state.Address")\]_[¶](#ops.testing.BindAddress.addresses "Link to this definition")

The addresses in the space.

interface\_name_: [str](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.14)")_ _\= ''_[¶](#ops.testing.BindAddress.interface_name "Link to this definition")

The name of the network interface.

mac\_address_: [str](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.14)") | [None](https://docs.python.org/3/library/constants.html#None "(in Python v3.14)")_ _\= None_[¶](#ops.testing.BindAddress.mac_address "Link to this definition")

The MAC address of the interface.

_class_ ops.testing.BlockedStatus(_message: [str](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.14)") \= ''_)[\[source\]](../../_modules/scenario/state/#BlockedStatus)[¶](#ops.testing.BlockedStatus "Link to this definition")

Bases: `_EntityStatus`, [`BlockedStatus`](../ops/#ops.BlockedStatus "ops.model.BlockedStatus")

The unit or application requires manual intervention.

Set this status when an administrator has to manually intervene to unblock the charm to let it proceed.

name_: Literal\['blocked'\]_ _\= 'blocked'_[¶](#ops.testing.BlockedStatus.name "Link to this definition")

_class_ ops.testing.CharmEvents[\[source\]](../../_modules/scenario/context/#CharmEvents)[¶](#ops.testing.CharmEvents "Link to this definition")

Bases: [`object`](https://docs.python.org/3/library/functions.html#object "(in Python v3.14)")

Events generated by Juju or ops pertaining to the application lifecycle.

The events listed as attributes of this class should be accessed via the [`Context.on`](#ops.testing.Context.on "ops.testing.Context.on") attribute. For example:

ctx.run(ctx.on.config\_changed(), state)

This behaves similarly to the [`ops.CharmEvents`](../ops/#ops.CharmEvents "ops.CharmEvents") class but is much simpler as there are no dynamically named attributes, and no `__getattr__` version to get events. In addition, all of the attributes are methods, which are used to connect the event to the specific object that they relate to (or, for simpler events like “start” or “stop”, take no arguments).

_static_ action(

_name: [str](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.14)")_,

_params: Mapping\[[str](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.14)"), AnyJson\] | [None](https://docs.python.org/3/library/constants.html#None "(in Python v3.14)") \= None_,

_id: [str](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.14)") | [None](https://docs.python.org/3/library/constants.html#None "(in Python v3.14)") \= None_,

)[\[source\]](../../_modules/scenario/context/#CharmEvents.action)[¶](#ops.testing.CharmEvents.action "Link to this definition")

Events raised by Juju when an administrator invokes a Juju Action.

This class is the data type of events triggered when an administrator invokes a Juju Action. Callbacks bound to these events may be used for responding to the administrator’s Juju Action request.

To read the parameters for the action, see the instance variable [`params`](../ops/#ops.ActionEvent.params "ops.ActionEvent.params"). To respond with the result of the action, call [`set_results()`](../ops/#ops.ActionEvent.set_results "ops.ActionEvent.set_results"). To add progress messages that are visible as the action is progressing use [`log()`](../ops/#ops.ActionEvent.log "ops.ActionEvent.log").

_static_ collect\_app\_status()[\[source\]](../../_modules/scenario/context/#CharmEvents.collect_app_status)[¶](#ops.testing.CharmEvents.collect_app_status "Link to this definition")

Event triggered at the end of every hook to collect app statuses for evaluation.

_static_ collect\_unit\_status()[\[source\]](../../_modules/scenario/context/#CharmEvents.collect_unit_status)[¶](#ops.testing.CharmEvents.collect_unit_status "Link to this definition")

Event triggered at the end of every hook to collect unit statuses for evaluation.

_static_ config\_changed()[\[source\]](../../_modules/scenario/context/#CharmEvents.config_changed)[¶](#ops.testing.CharmEvents.config_changed "Link to this definition")

Event triggered when a configuration change occurs.

This event will fire in several situations:

*   When the admin reconfigures the charm using the Juju CLI, for example `juju config mycharm foo=bar`. This event notifies the charm of its new configuration. (The event itself, however, is not aware of _what_ specifically has changed in the config).
    
*   Right after the unit starts up for the first time. This event notifies the charm of its initial configuration. Typically, this event will fire between an [`InstallEvent`](../ops/#ops.InstallEvent "ops.InstallEvent") and a [`StartEvent`](../ops/#ops.StartEvent "ops.StartEvent") during the startup sequence (when a unit is first deployed), but in general it will fire whenever the unit is (re)started, for example after pod churn on Kubernetes, on unit rescheduling, on unit upgrade or refresh, and so on.
    
*   As a specific instance of the above point: when networking changes (if the machine reboots and comes up with a different IP).
    
*   When the app config changes, for example when juju trust is run.
    

Any callback method bound to this event cannot assume that the software has already been started; it should not start stopped software, but should (if appropriate) restart running software to take configuration changes into account.

See also: [Juju | Hook | config-changed](https://documentation.ubuntu.com/juju/3.6/reference/hook/#config-changed).

_static_ custom(

_event: [BoundEvent](../ops/#ops.BoundEvent "ops.framework.BoundEvent")_,

_\*args: [Any](https://docs.python.org/3/library/typing.html#typing.Any "(in Python v3.14)")_,

_\*\*kwargs: [Any](https://docs.python.org/3/library/typing.html#typing.Any "(in Python v3.14)")_,

)[\[source\]](../../_modules/scenario/context/#CharmEvents.custom)[¶](#ops.testing.CharmEvents.custom "Link to this definition")

Event triggered by a charm library.

For example, suppose that a library uses a `DatabaseRequirer` object to emit a `DatabaseReadyEvent` event, with charm code:

class MyCharm(ops.CharmBase):
    def \_\_init\_\_(self, framework: ops.Framework):
        super().\_\_init\_\_(framework)
        self.db \= DatabaseRequirer(self, 'db-relation')
        framework.observe(self.db.on.ready, self.\_on\_db\_ready)

To emit a `DatabaseReadyEvent` event:

ctx.run(ctx.on.custom(
    Data

<note>Content truncated. Call the fetch tool with a start_index of 15000 to get more content.</note>
```

</details>


---

<sub>⏱️ 39s</sub>

### ✅ `web_fetch`

**https://raw.githubusercontent.com/canonical/operator/main/testing/README.md**

<details>
<summary>Arguments</summary>

```json
{
  "max_length": 15000,
  "url": "https://raw.githubusercontent.com/canonical/operator/main/testing/README.md"
}
```

</details>

<details>
<summary>109 lines</summary>

````
Content type text/plain; charset=utf-8 cannot be simplified to markdown. Here is the raw content:
Contents of https://raw.githubusercontent.com/canonical/operator/main/testing/README.md:
# ops-scenario, the unit testing framework for ops charms

`ops-scenario` is a Python library that provides state-transition testing for
[Ops](https://documentation.ubuntu.com/ops/latest/) charms. These tests are higher level than
typical unit tests, but run at similar speeds and are the recommended approach
for testing charms within requiring a full [Juju](https://canonical.com/juju) installation.

Test are written in the arrange/act/assert pattern, arranging an object
representing the current Juju state, acting by emulating an event from Juju, and
then asserting on the (simulated) output Juju state.

## Writing tests

Here's a test that verifies that a unit is active after the `start` event, with a very minimal initial state:

```python
from ops import testing

# 'src/charm.py' typically contains the charm class.
from charm import MyCharm

def test_start():
    ctx = testing.Context(MyCharm)
    state_in = testing.State()
    state_out = ctx.run(ctx.on.start(), state_in)
    assert state_out.unit_status == testing.ActiveStatus()
```

More comprehensive tests will include relations, containers, secrets, and other
components in the input state, and assertions against both the output state and
the context. The 'act' stage remains a simple single call, although additional
arguments may be required for the event, such as the relation or container that
triggered it. For example:

```python
import pytest
from ops import testing

from charm import MyCharm

@pytest.mark.parametrize(
    'leader',
    [pytest.param(True, id='leader'), pytest.param(False, id='non-leader')],
)
def test_(leader: bool):
    # Arrange:
    ctx = testing.Context(MyCharm)
    relation = testing.Relation('db', local_app_data={'hostname': 'example.com'})
    peer_relation = testing.PeerRelation('peer')
    container = testing.Container('workload', can_connect=True)
    relation_secret = testing.Secret({'certificate': 'xxxxxxxx'})
    user_secret = testing.Secret({'username': 'admin', 'password': 'xxxxxxxx'})
    config = {'port': 8443, 'admin-credentials': 'secret:1234'}
    state_in = testing.State(
        leader=leader,
        config=config,
        relations={relation, peer_relation},
        containers={container},
        secrets={relation_secret, user_secret},
        unit_status=testing.BlockedStatus(),
        workload_version='1.0.1',
    )

    # Act:
    state_out = ctx.run(ctx.on.relation_changed(relation), state_in)

    # Assert:
    assert testing.JujuLogLine(level='INFO', message='Distributing secret.') in ctx.juju_log
    peer_relation_out = state_out.get_relation(peer_relation.id)
    assert peer_relation_out.peers_data[0] == {'secret_id': relation_secret.id}
```

You don't have to use pytest for your charm tests, but it's what we recommend.
pytest's `assert`-based approach is a straightforward way to write tests, and
its fixtures are helpful for structuring setup and teardown.

## Installation

For charm tests, install the testing framework by adding the `testing` extra of
ops in your unit testing environment. For example, in `pyproject.toml`:

```toml
[dependency-groups]
test = ['ops[testing]<4.0']
```

Ops checks if `ops-scenario` is installed, and, if so, makes the classes
(such as `Context`, `State`, and `Relation`) available in the `ops.testing`
namespace. Use `from ops import testing` rather than importing the `scenario`
package.

`ops-scenario` supports the same platforms and Python versions as ops itself.

## Documentation

 * To get started, work through our ['Write your first Kubernetes charm' tutorial](https://documentation.ubuntu.com/ops/latest/tutorial/from-zero-to-hero-write-your-first-kubernetes-charm/create-a-minimal-kubernetes-charm/#write-unit-tests-for-your-charm), following the instructions for adding
   unit tests at the end of each chapter.
 * When you need to write a test that involves specific ops functionality,
   refer to our [how-to guides](https://documentation.ubuntu.com/ops/latest/howto/)
   which all conclude with examples of tests of the ops functionality.
 * Use our extensive [reference documentation](https://documentation.ubuntu.com/ops/latest/reference/ops-testing/#ops-testing) when you need to know how each `testing` object works. These
   docs are also available via the standard Python `help()` functionality and in
   your IDE.

[**Read the full documentation**](https://documentation.ubuntu.com/ops/latest/)

## Community

`ops-scenario` is a member of the Charming family. It's an open source project
that warmly welcomes community contributions, suggestions, fixes and
constructive feedback.

* Read our [code of conduct](https://ubuntu.com/community/ethos/code-of-conduct):
  As a community we adhere to the Ubuntu code of conduct.
* [Get support](https://discourse.charmhub.io/): Discourse is the go-to forum
  for all Ops-related discussions, including around testing.
* Join our [online chat](https://matrix.to/#/#charmhub-charmdev:ubuntu.com):
  Meet us in the #charmhub-charmdev channel on Matrix.
* [Report bugs](https://github.com/canonical/operator/issues): We want to know
  about the problems so we can fix them.
* [Contribute docs](https://github.com/canonical/operator/blob/main/HACKING.md#contributing-documentation):
  Get started on GitHub.

## Contributing and developing

Anyone can contribute to ops and `ops-scenario`. It's best to start by
[opening an issue](https://github.com/canonical/operator/issues) with a clear
description of the problem or feature request, but you can also
[open a pull request](https://github.com/canonical/operator/pulls) directly.

Read our [guide](./CONTRIBUTING.md) for more details on how to work on and
contribute to `ops-scenario`.

Currently, releases of `ops-scenario` are done in lockstep with releases of ops
itself, with matching minor and bugfix release numbers. The ops documentation
outlines how to create a new release.
````

</details>


---

<sub>⏱️ 1m 46s</sub>

### ✅ `read_agent`

**Explore agent (Explore charm test structure)**

<details>
<summary>Arguments</summary>

```json
{
  "agent_id": "explore-codebase",
  "wait": true,
  "timeout": 60
}
```

</details>

```
Agent is still running after waiting 60s. agent_id: explore-codebase, agent_type: explore, status: running, description: Explore charm test structure, elapsed: 91s, total_turns: 0, tool_calls_completed: 20, (timed out waiting for completion) You will be automatically notified when this agent completes — no need to poll.
```


---

<sub>⏱️ 1m 55s</sub>

### ✅ `bash`

**List test files and pyproject.toml**

$ find /tmp/ops-upgrade-experiment/content-cache-k8s-operator__ops-testing-migration__C2/tests -type f | sort && echo "---" && cat /tmp/ops-upgrade-experiment/content-cache-k8s-operator__ops-testing-migration__C2/pyproject.toml

<details>
<summary>134 lines</summary>

```
/tmp/ops-upgrade-experiment/content-cache-k8s-operator__ops-testing-migration__C2/tests/conftest.py
/tmp/ops-upgrade-experiment/content-cache-k8s-operator__ops-testing-migration__C2/tests/files/nginx_config.txt
/tmp/ops-upgrade-experiment/content-cache-k8s-operator__ops-testing-migration__C2/tests/files/nginx_config_backend_site_name.txt
/tmp/ops-upgrade-experiment/content-cache-k8s-operator__ops-testing-migration__C2/tests/files/nginx_config_client_max_body_size.txt
/tmp/ops-upgrade-experiment/content-cache-k8s-operator__ops-testing-migration__C2/tests/files/nginx_config_proxy_cache_revalidate.txt
/tmp/ops-upgrade-experiment/content-cache-k8s-operator__ops-testing-migration__C2/tests/integration/any_charm.py
/tmp/ops-upgrade-experiment/content-cache-k8s-operator__ops-testing-migration__C2/tests/integration/conftest.py
/tmp/ops-upgrade-experiment/content-cache-k8s-operator__ops-testing-migration__C2/tests/integration/test_core.py
/tmp/ops-upgrade-experiment/content-cache-k8s-operator__ops-testing-migration__C2/tests/unit/test_charm.py
---
# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

[project]
name = "content-cache-k8s-operator"
version = "0.0.0"
description = "HTTP cache service useful for building CDNs.\n"
readme = "README.md"
requires-python = ">=3.10"
classifiers = [
  "Programming Language :: Python :: 3 :: Only",
  "Programming Language :: Python :: 3.10",
  "Programming Language :: Python :: 3.11",
  "Programming Language :: Python :: 3.12",
  "Programming Language :: Python :: 3.13",
  "Programming Language :: Python :: 3.14",
]
dependencies = [
  "cosl==1.6.1",
  "ops==3.6.0",
  "tabulate==0.10.0",
]

[dependency-groups]
fmt = [
  "ruff",
]
lint = [
  "codespell",
  "mypy",
  "pep8-naming",
  "ruff",
]
unit = [
  "coverage[toml]",
  "pytest",
]
coverage-report = [
  "coverage[toml]",
  "pytest",
]
static = [
  "bandit[toml]",
]
integration = [
  "allure-pytest>=2.8.18",
  "allure-pytest-collection-report @ git+https://github.com/canonical/data-platform-workflows@v24.0.0#subdirectory=python/pytest_plugins/allure_pytest_collection_report",
  "juju",
  "pillow",
  "pytest",
  "pytest-cov",
  "pytest-operator",
  "python-keystoneclient",
  "python-swiftclient",
  "requests",
]

[tool.uv]
package = false

[tool.ruff]
target-version = "py310"
line-length = 99

# enable ruff linters:
#   A flake8-builtins
#   B flake8-bugbear
# CPY flake8-copyright
#   D pydocstyle
# E/W pycodestyle
#   F Pyflakes
#   I isort
#   N pep8-naming
# RUF Ruff-specific rules
#   S flake8-bandit
# SIM flake8-simplify
#  TC flake8-type-checking
#  UP pyupgrade
lint.select = [ "A", "B", "C", "CPY", "D", "E", "F", "I", "N", "RUF", "S", "SIM", "TC", "UP", "W" ]
lint.ignore = [
  "B904",
  "D107",
  "D203",
  "D204",
  "D205",
  "D213",
  "D215",
  "D400",
  "D404",
  "D406",
  "D407",
  "D408",
  "D409",
  "D413",
  "E501",
  "S105",
  "S603",
  "TC002",
  "TC006",
  "UP006",
  "UP007",
  "UP035",
  "UP045",
]
lint.per-file-ignores."tests/*" = [ "B011", "D100", "D101", "D102", "D103", "D104", "D212", "D415", "D417", "S" ]
lint.flake8-copyright.author = "Canonical Ltd."
lint.flake8-copyright.min-file-size = 1
lint.flake8-copyright.notice-rgx = "Copyright\\s\\d{4}([-,]\\d{4})*\\s+"
lint.mccabe.max-complexity = 10
lint.pydocstyle.convention = "google"

[tool.codespell]
skip = "build,lib,venv,icon.svg,.tox,.git,.mypy_cache,.ruff_cache,.coverage,htmlcov,uv.lock,grafana_dashboards"

[tool.mypy]
exclude = [ "^tests/integration/conftest\\.py$" ]
ignore_missing_imports = true
follow_imports = "silent"

[tool.pytest.ini_options]
minversion = "6.0"
log_cli_level = "INFO"

[tool.coverage.run]
branch = true

[tool.coverage.report]
fail_under = 88
show_missing = true

[tool.bandit]
exclude_dirs = [ "/venv/", "tests/integration/any_charm.py" ]

[tool.bandit.assert_used]
skips = [ "*/*test.py", "*/test_*.py" ]
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 1m 55s</sub>

### ✅ `bash`

**List source files**

$ find /tmp/ops-upgrade-experiment/content-cache-k8s-operator__ops-testing-migration__C2/src -type f | sort

<details>
<summary>6 lines</summary>

```
/tmp/ops-upgrade-experiment/content-cache-k8s-operator__ops-testing-migration__C2/src/charm.py
/tmp/ops-upgrade-experiment/content-cache-k8s-operator__ops-testing-migration__C2/src/file_reader.py
/tmp/ops-upgrade-experiment/content-cache-k8s-operator__ops-testing-migration__C2/src/grafana_dashboards/content-cache.json
/tmp/ops-upgrade-experiment/content-cache-k8s-operator__ops-testing-migration__C2/src/loki_alert_rules/.gitkeep
/tmp/ops-upgrade-experiment/content-cache-k8s-operator__ops-testing-migration__C2/src/prometheus_alert_rules/content_cache_missing.rule
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 1m 59s</sub>

### ✅ `bash`

**Read test file**

$ cat /tmp/ops-upgrade-experiment/content-cache-k8s-operator__ops-testing-migration__C2/tests/unit/test_charm.py

<details>
<summary>19 lines</summary>

```
Output too large to read at once (23.7 KB). Saved to: /tmp/copilot-tool-output-1775167242694-m7pxov.txt
Consider using tools like grep (for searching), head/tail (for viewing start/end), view with view_range (for specific sections), or jq (for JSON) to examine portions of the output.

Preview (first 500 chars):
# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.
import copy
import io
from datetime import datetime, timedelta
from unittest import mock

import pytest
from ops.model import ActiveStatus, BlockedStatus, MaintenanceStatus
from ops.testing import Harness

from charm import CONTAINER_PORT, ContentCacheCharm

BASE_CONFIG = {
    "site": "mysite.local",
    "backend": "http://mybackend.local:80",
    "cache_max_size": "10G",
    "cache_use_stale": "error timeout updating htt
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 2m 0s</sub>

### ✅ `bash`

**Read conftest and charm source**

$ cat /tmp/ops-upgrade-experiment/content-cache-k8s-operator__ops-testing-migration__C2/tests/conftest.py && echo "---" && cat /tmp/ops-upgrade-experiment/content-cache-k8s-operator__ops-testing-migration__C2/src/charm.py

<details>
<summary>430 lines</summary>

```
# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

"""General configuration module for tests."""

import pytest


def pytest_addoption(parser: pytest.Parser):
    """Process parameters for integration tests.

    Args:
        parser: Pytest parser used to add arguments to console commands
    """
    # --openstack-rc points to an openstack credential file in the "rc" file style
    # Here's an example of that file
    # $ echo ~/openrc
    # export OS_REGION_NAME=RegionOne
    # export OS_PROJECT_DOMAIN_ID=default
    # export OS_AUTH_URL=http://10.0.0.1/identity
    # export OS_TENANT_NAME=demo
    # export OS_USER_DOMAIN_ID=default
    # export OS_USERNAME=demo
    # export OS_VOLUME_API_VERSION=3
    # export OS_AUTH_TYPE=password
    # export OS_PROJECT_NAME=demo
    # export OS_PASSWORD=nomoresecret
    # export OS_IDENTITY_API_VERSION=3
    parser.addoption("--charm-file", action="store")
    parser.addoption("--openstack-rc", action="store", default="")
    parser.addoption("--content-cache-image", action="store", default="")
---
#!/usr/bin/env python3

# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

"""Charm for Content-cache on Kubernetes."""

import hashlib
import itertools
import logging
from collections import Counter
from datetime import datetime, timedelta
from urllib.parse import urlparse

import ops.pebble
from charms.grafana_k8s.v0.grafana_dashboard import GrafanaDashboardProvider
from charms.loki_k8s.v0.loki_push_api import LogProxyConsumer
from charms.nginx_ingress_integrator.v0.nginx_route import (
    _NginxRouteCharmEvents,
    provide_nginx_route,
    require_nginx_route,
)
from charms.prometheus_k8s.v0.prometheus_scrape import MetricsEndpointProvider
from ops.charm import ActionEvent, CharmBase, ConfigChangedEvent, UpgradeCharmEvent
from ops.main import main
from ops.model import ActiveStatus, BlockedStatus, MaintenanceStatus, WaitingStatus
from tabulate import tabulate  # type: ignore[import-untyped]

from file_reader import readlines_reverse

logger = logging.getLogger(__name__)

CACHE_PATH = "/var/lib/nginx/proxy/cache"
CONTAINER_NAME = "content-cache"
EXPORTER_CONTAINER_NAME = "nginx-prometheus-exporter"
CONTAINER_PORT = 8080
REQUIRED_JUJU_CONFIGS = ["backend"]
REQUIRED_INGRESS_RELATION_FIELDS = {"service-hostname", "service-name", "service-port"}


class ContentCacheCharm(CharmBase):
    """Charm the service.

    Attrs:
        on: Ingress Charm Events
        ERROR_LOG_PATH: NGINX error log
        ACCESS_LOG_PATH: NGINX access log
        _metrics_endpoint: Provider of metrics for Prometheus charm
        _logging: Requirer of logs for Loki charm
        _grafana_dashboards: Dashboard Provider for Grafana charm
        unit: Charm's designated juju unit
        model: Charm's designated juju model
    """

    on = _NginxRouteCharmEvents()
    ERROR_LOG_PATH = "/var/log/nginx/error.log"
    ACCESS_LOG_PATH = "/var/log/nginx/access.log"

    def __init__(self, *args):
        """Init function for the charm.

        Args:
            args: Variable list of positional arguments passed to the parent constructor.
        """
        super().__init__(*args)

        self.framework.observe(self.on.start, self._on_start)
        self.framework.observe(self.on.config_changed, self._on_config_changed)
        self.framework.observe(self.on.upgrade_charm, self._on_upgrade_charm)
        self.framework.observe(
            self.on.report_visits_by_ip_action, self._report_visits_by_ip_action
        )
        self.framework.observe(
            self.on.content_cache_pebble_ready, self._on_content_cache_pebble_ready
        )
        # Provide ability for Content-cache to be scraped by Prometheus using prometheus_scrape
        self._metrics_endpoint = MetricsEndpointProvider(
            self, jobs=[{"static_configs": [{"targets": ["*:9113"]}]}]
        )

        # Enable log forwarding for Loki and other charms that implement loki_push_api
        self._logging = LogProxyConsumer(
            self,
            relation_name="logging",
            log_files=[self.ACCESS_LOG_PATH, self.ERROR_LOG_PATH],
            container_name=CONTAINER_NAME,
        )

        # Provide grafana dashboards over a relation interface
        self._grafana_dashboards = GrafanaDashboardProvider(
            self, relation_name="grafana-dashboard"
        )
        ingress_config = self._make_ingress_config()
        require_nginx_route(
            charm=self,
            max_body_size=ingress_config.get("max-body-size", None),
            service_hostname=ingress_config.get("service-hostname"),
            service_name=ingress_config.get("service-name"),
            service_port=ingress_config.get("service-port"),
            tls_secret_name=ingress_config.get("tls-secret-name", None),
        )
        provide_nginx_route(
            charm=self,
            on_nginx_route_available=self._on_config_changed,
            on_nginx_route_broken=self._on_config_changed,
            nginx_route_relation_name="nginx-proxy",
        )
        self.framework.observe(self.on.nginx_route_available, self._on_config_changed)

    def _on_content_cache_pebble_ready(self, event) -> None:
        """Handle content_cache_pebble_ready event and configure workload container.

        Args:
            event: Event triggering the pebble ready hook for the content-cache container.
        """
        msg = "Configuring workload container (content-cache-pebble-ready)"
        logger.info(msg)
        self.model.unit.status = MaintenanceStatus(msg)
        self.on.config_changed.emit()

    def _on_start(self, event) -> None:
        """Handle workload container started.

        Args:
            event: start event.
        """
        logger.info("Starting workload container (start)")
        self.model.unit.status = ActiveStatus()

    def _on_config_changed(self, event) -> None:
        """Handle config_changed event and reconfigure workload container.

        Args:
            event: config-changed event.
        """
        msg = "Configuring workload container (config-changed)"
        logger.info(msg)
        self.model.unit.status = MaintenanceStatus(msg)
        self.configure_workload_container(event)

    def _report_visits_by_ip_action(self, event: ActionEvent) -> None:
        """Handle the report-visits-by-ip action.

        Args:
            event: the Juju action event fired when the action executes.
        """
        results = self._report_visits_by_ip()
        event.set_results({"ips": tabulate(results, headers=["IP", "Requests"], tablefmt="grid")})

    @staticmethod
    def _filter_lines(line: str) -> bool:
        """Filter the log lines by date.

        Args:
            line: A log line from the log file.

        Returns:
            Indicates if the line must be included or not.
        """
        line_elements = line.split()

        if len(line_elements) < 4:
            return False

        timestamp_str = line_elements[3].lstrip("[").rstrip("]")
        try:
            timestamp = datetime.strptime(timestamp_str, "%d/%b/%Y:%H:%M:%S")
        except ValueError:
            return False

        return timestamp > (datetime.now() - timedelta(minutes=20))

    def _get_ip(self, line: str) -> str:
        """Return the IP address of a log line.

        Args:
            line: The log line previously filtered.

        Returns:
            an IP address.

        Raises:
            ValueError: if the method encounters an empty line,
                filtering should happen in filter_lines anyway.
        """
        if line:
            return line.split()[0]
        raise ValueError

    def _report_visits_by_ip(self) -> list[tuple[str, int]]:
        """Report requests to nginx grouped and ordered by IP and report action result.

        Returns:
            A list of tuples composed of an IP address and the number of visits to that IP.
        """
        container = self.unit.get_container(CONTAINER_NAME)
        reversed_lines = filter(None, readlines_reverse(container.pull(self.ACCESS_LOG_PATH)))
        line_list = itertools.takewhile(self._filter_lines, reversed_lines)
        ip_list = map(self._get_ip, line_list)

        return Counter(ip_list).most_common()

    def _on_upgrade_charm(self, event: UpgradeCharmEvent) -> None:
        """Handle upgrade_charm event and reconfigure workload container.

        Args:
            event: upgrade-charm event.
        """
        msg = "Configuring workload container (upgrade-charm)"
        logger.info(msg)
        self.model.unit.status = MaintenanceStatus(msg)
        self.configure_workload_container(event)

    def configure_workload_container(self, event: ConfigChangedEvent | UpgradeCharmEvent) -> None:
        """Configure/set up workload container inside pod.

        Args:
            event: config-changed or upgrade-charm event.
        """
        missing = sorted(self._missing_charm_configs())
        if missing:
            msg = f"Required config(s) empty: {', '.join(missing)}"
            logger.warning(msg)
            self.unit.status = BlockedStatus(msg)
            return
        env_config = self._make_env_config()
        if env_config is None:
            logger.debug("Ingress hasn't been configured yet, waiting")
            event.defer()
            return
        pebble_config = self._make_pebble_config(env_config)
        nginx_config = self._make_nginx_config(env_config)
        exporter_config = self._get_nginx_prometheus_exporter_pebble_config()

        container = self.unit.get_container(CONTAINER_NAME)
        if container.can_connect():
            msg = "Updating Nginx site config"
            logger.info(msg)
            self.unit.status = MaintenanceStatus(msg)
            container.push("/etc/nginx/sites-enabled/default", nginx_config)
            container.make_dir(CACHE_PATH, make_parents=True)

            services = container.get_plan().to_dict().get("services", {})
            if services != pebble_config["services"]:
                msg = "Updating pebble layer config"
                logger.info(msg)
                self.unit.status = MaintenanceStatus(msg)
                container.add_layer(CONTAINER_NAME, pebble_config, combine=True)  # type: ignore[arg-type]
                container.add_layer(EXPORTER_CONTAINER_NAME, exporter_config, combine=True)  # type: ignore[arg-type]
                container.pebble.replan_services()
        else:
            self.unit.status = WaitingStatus("Waiting for Pebble to start")
            event.defer()
            return

        msg = "Ready"
        logger.info(msg)
        self.unit.status = ActiveStatus(msg)

    def _generate_keys_zone(self, name):
        """Generate hashed name to be used by Nginx's key zone.

        Args:
            name: Site name to be encoded.

        Returns:
            A hashed name to be used by Nginx's key zone.
        """
        hashed_value = hashlib.md5(name.encode("UTF-8"), usedforsecurity=False)
        hashed_name = hashed_value.hexdigest()[0:12]
        return f"{hashed_name}-cache"

    def _get_nginx_prometheus_exporter_pebble_config(self) -> ops.pebble.LayerDict:
        """Generate pebble config for the nginx-prometheus-exporter container.

        Returns:
            Pebble layer config for the nginx-prometheus-exporter layer.
        """
        return {
            "summary": "Nginx prometheus exporter",
            "description": "Prometheus exporter for nginx",
            "services": {
                EXPORTER_CONTAINER_NAME: {
                    "override": "replace",
                    "summary": "Nginx Prometheus Exporter",
                    "command": (
                        "nginx-prometheus-exporter"
                        f" -nginx.scrape-uri=http://localhost:{CONTAINER_PORT}/stub_status"
                    ),
                    "startup": "enabled",
                    "requires": [CONTAINER_NAME],
                },
            },
            "checks": {
                "nginx-exporter-up": {
                    "override": "replace",
                    "level": "alive",
                    "http": {"url": "http://localhost:9113/metrics"},
                },
            },
        }

    def _make_ingress_config(self) -> dict:
        """Return an assembled K8s ingress.

        Returns:
            An Ingress config dict.
        """
        config = self.model.config

        ingress = {
            "service-hostname": "mysite.local",
            "service-name": self.app.name,
            "service-port": CONTAINER_PORT,
        }

        site = config.get("site")

        relation = self.model.get_relation("nginx-proxy")
        if relation:
            # in case the relation app is not available yet
            prev_site = site
            site = relation.data[relation.app].get("service-hostname", prev_site)

        if site:
            ingress["service-hostname"] = site

        client_max_body_size = config.get("client_max_body_size")
        if client_max_body_size:
            ingress["max-body-size"] = client_max_body_size

        tls_secret_name = config.get("tls_secret_name")
        if tls_secret_name:
            ingress["tls-secret-name"] = tls_secret_name

        return ingress

    def _make_env_config(self, domain="svc.cluster.local") -> dict | None:
        """Return dict to be used as as runtime environment variables.

        Args:
            domain: domain used for the content-cache

        Returns:
            Charm's environment config
        """
        config = self.model.config
        relation = self.model.get_relation("nginx-proxy")
        if relation and relation.data[relation.app] and relation.units:
            if any(
                relation.data[relation.app].get(nginx_config) is None
                for nginx_config in REQUIRED_INGRESS_RELATION_FIELDS
            ):
                return None
            site = relation.data[relation.app].get("service-hostname")
            svc_name = relation.data[relation.app].get("service-name")
            svc_port = relation.data[relation.app].get("service-port")
            backend_site_name = relation.data[relation.app].get("service-hostname")
            clients = []
            for peer in relation.units:
                unit_name = peer.name.replace("/", "-")
                service_url = f"{unit_name}.{svc_name}-endpoints.{self.model.name}.{domain}"
                clients.append(f"http://{service_url}:{svc_port}")
            # XXX: Will need to deal with multiple units at some point
            backend = clients[0]
        elif relation:
            return None
        else:
            backend = str(config["backend"])
            backend_site_name = (
                str(config["backend_site_name"]) if config.get("backend_site_name") else None
            )
            if not backend_site_name:
                backend_site_name = urlparse(backend).hostname
            site = str(config["site"]) if config.get("site") else self.app.name

        cache_all_configs = ""
        if not config["cache_all"]:
            cache_all_configs = "proxy_ignore_headers Cache-Control Expires"

        client_max_body_size = config["client_max_body_size"]

        proxy_cache_revalidate = "off"
        if config.get("proxy_cache_revalidate", False):
            proxy_cache_revalidate = "on"

        env_config = {
            "CONTAINER_PORT": CONTAINER_PORT,
            "CONTENT_CACHE_BACKEND": backend,
            "CONTENT_CACHE_SITE": site,
            # https://bugs.launchpad.net/juju/+bug/1894782
            "JUJU_POD_NAME": self.unit.name,
            "JUJU_POD_NAMESPACE": self.model.name,
            "JUJU_POD_SERVICE_ACCOUNT": self.app.name,
            # Include nginx / charm configs as environment variables
            # to pass to the pebble services and ensure it restarts
            # nginx on changes.
            "NGINX_BACKEND": backend,
            "NGINX_CACHE_ALL": cache_all_configs,
            "NGINX_BACKEND_SITE_NAME": backend_site_name,
            "NGINX_CACHE_INACTIVE_TIME": config.get("cache_inactive_time", "10m"),
            "NGINX_CACHE_MAX_SIZE": config.get("cache_max_size", "10G"),
            "NGINX_CACHE_PATH": CACHE_PATH,
            "NGINX_CACHE_REVALIDATE": proxy_cache_revalidate,
            "NGINX_CACHE_USE_STALE": config["cache_use_stale"],
            "NGINX_CACHE_VALID": config["cache_valid"],
            "NGINX_CLIENT_MAX_BODY_SIZE": client_max_body_size,
            "NGINX_KEYS_ZONE": self._generate_keys_zone(site),
            "NGINX_SITE_NAME": site,
        }

        return env_config

    def _make_pebble_config(self, env_config) -> dict:
        """Generate our pebble config layer.

        Args:
            env_config: Charm's environment config

        Returns:
            content-cache container pebble layer config
        """
        pebble_config = {
            "summary": "content-cache layer",
            "description": "Pebble config layer for content-cache",
            "services": {
                CONTAINER_NAME: {
                    "override": "replace",
                    "summary": "content-cache",
                    "command": "/srv/content-cache/entrypoint.sh",
                    "startup": "enabled",
                    "environment": env_config,
                },
            },
            "checks": {
                CONTAINER_NAME: {
                    "override": "replace",
                    "exec": {"command": "ps -A | grep nginx"},
                    "threshold": 1,
                }
            },
        }
        return pebble_config

    def _make_nginx_config(self, env_config: dict) -> str:
        """Grab the NGINX template and fill it with our env config.

        Args:
            env_config: Charm's environment config

        Returns:
            A fully configured NGINX conf file
        """
        with open("content-cache_rock/nginx_cfg.tmpl", encoding="utf-8") as file:
            content = file.read()

        nginx_config = content.format(**env_config)
        return nginx_config

    def _missing_charm_configs(self) -> list[str]:
        """Check and return list of required but missing configs.

        Returns:
            Missing settings in the required juju configs.
        """
        relation = self.model.get_relation("nginx-proxy")
        if relation:
            return []
        config = self.model.config
        missing = [
            setting
            for setting in REQUIRED_JUJU_CONFIGS
            if setting not in config or not config[setting]
        ]

        return sorted(missing)


if __name__ == "__main__":  # pragma: no cover
    main(ContentCacheCharm, use_juju_for_storage=True)
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 2m 0s</sub>

### ℹ️ Notification

Background agent "Explore charm test structure" (explore) completed

<details>
<summary>Detail</summary>

Explore the repository at /tmp/ops-upgrade-experiment/content-cache-k8s-operator__ops-testing-migration__C2 and answer:
1. What Python version and ops version are used? (check pyproject.toml, tox.toml, charmcraft.yaml)
2. What test files exist under tests/? Show full content of each test file.
3. What does src/ contain? Show the charm source files.
4. What does the charm do? (check metadata.yaml, config.yaml, actions.yaml)
5. What testing framework is currently used? (Harness-based or Scenario-based?)
6. Are there any existing imports from ops.testing or ops.testing.harness?
Please provide file contents, not just summaries.

</details>

---

<sub>⏱️ 2m 8s</sub>

### ✅ `bash`

**Read the test file**

$ cat /tmp/copilot-tool-output-1775167242694-m7pxov.txt

<details>
<summary>19 lines</summary>

```
Output too large to read at once (23.7 KB). Saved to: /tmp/copilot-tool-output-1775167251608-5va8x5.txt
Consider using tools like grep (for searching), head/tail (for viewing start/end), view with view_range (for specific sections), or jq (for JSON) to examine portions of the output.

Preview (first 500 chars):
# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.
import copy
import io
from datetime import datetime, timedelta
from unittest import mock

import pytest
from ops.model import ActiveStatus, BlockedStatus, MaintenanceStatus
from ops.testing import Harness

from charm import CONTAINER_PORT, ContentCacheCharm

BASE_CONFIG = {
    "site": "mysite.local",
    "backend": "http://mybackend.local:80",
    "cache_max_size": "10G",
    "cache_use_stale": "error timeout updating htt
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 2m 9s</sub>

### ✅ `bash`

**Read metadata, actions, and config**

$ cat /tmp/ops-upgrade-experiment/content-cache-k8s-operator__ops-testing-migration__C2/metadata.yaml && echo "---" && cat /tmp/ops-upgrade-experiment/content-cache-k8s-operator__ops-testing-migration__C2/actions.yaml && echo "---" && cat /tmp/ops-upgrade-experiment/content-cache-k8s-operator__ops-testing-migration__C2/config.yaml

<details>
<summary>131 lines</summary>

```
# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

name: content-cache-k8s
display-name: Content-cache
description: |
  A [Juju](https://juju.is/) [charm](https://juju.is/docs/olm/charmed-operators) deploying and managing
  service for caching content, built on top of [Nginx](https://www.nginx.com/), configurable to cache
  any http or https web site and useful for building content delivery networks (CDN).

  This charm simplifies initial deployment and caching operations on Kubernetes,
  such as scaling the number of cache instances and cache configuration changes.
  It allows for deployment on many different Kubernetes platforms, from [MicroK8s](https://microk8s.io) to
  [Charmed Kubernetes](https://ubuntu.com/kubernetes) and public cloud Kubernetes
  offerings.

  This service was developed to provide front-end caching for web sites run by
  Canonical's IS team, and to reduce the need for third-party CDNs by providing
  high-bandwidth access to web sites via this caching front-end. 
  
  Currently used for a number of services including [the Snap Store](https://snapcraft.io/store),
  the majority of Canonical's web properties including [ubuntu.com](https://ubuntu.com) and
  [canonical.com](https://canonical.com), and [Ubuntu Extended Security Maintenance](https://ubuntu.com/security/esm).
  For DevOps or SRE teams this charm will make operating it simple and straightforward through Juju's clean interface.
summary: |
  HTTP cache service useful for building CDNs.
docs: https://discourse.charmhub.io/t/content-cache-documentation-overview/3992
maintainers:
  - https://launchpad.net/~content-cache-charmers
assumes:
  - k8s-api
issues: https://github.com/canonical/content-cache-k8s-operator/issues
source: https://github.com/canonical/content-cache-k8s-operator

containers:
  content-cache:
    resource: content-cache-image

resources:
  content-cache-image:
    type: oci-image
    description: Docker image for content-cache to run

provides:
  metrics-endpoint:
    interface: prometheus_scrape
    optional: true
  grafana-dashboard:
    interface: grafana_dashboard
    optional: true
  nginx-proxy:
    interface: nginx-route
    limit: 1

requires:
  logging:
    interface: loki_push_api
    limit: 1
    optional: true
  nginx-route:
    interface: nginx-route
    limit: 1
    optional: true
---
# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

report-visits-by-ip:
  description: Look at the proxy log and list the IPs that visited the proxy the most in the last 20 minutes.
---
# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

options:
  site:
    type: string
    description: >
      Required if no nginx-proxy relation is established. The site name, e.g. "mysite.local".
      If the backend is set and this option is empty then the site will default to the application
      name.
  backend:
    type: string
    description: >
      Required if no nginx-proxy relation is established. The backend to use for site, e.g. "http://mybackend.local:80".
    default: ""
  backend_site_name:
    type: string
    description: >
      Backend site name, e.g. mybackend.local. If none given, will
      work out from the configured 'backend' config above.
    default: ""
  cache_all:
    type: boolean
    description: >
      By default, we respect upstream cache headers (Cache-Control
      and Expires). This overrides that and enables caching even if
      upstream tells us not to.
      WARNING: It won't cache when Vary: * and Set-Cookies headers are sent in the responses.
      This option overrides the backend cache time instructions (Expires or max-age) by setting
      a cache time to 1h (which could be less than the caching instructed by the backend)
    default: False
  cache_inactive_time:
    type: string
    description: >
      The maximum age/time inactive objects are stored in cache.
    default: "10m"
  cache_max_size:
    type: string
    description: >
      The size of the Nginx storage cache.
    default: "10G"
  cache_use_stale:
    type: string
    description: >
      Determines in which cases a stale cached response can be used
      during communication with the proxied server.
    default: "error timeout updating http_500 http_502 http_503 http_504"
  cache_valid:
    type: string
    description: >
      Sets caching time for different response codes.
    default: "200 1h"
  client_max_body_size:
    type: string
    description: >
      Override max. request body size (default 1m).
    default: "1m"
  tls_secret_name:
    type: string
    description: >
      The name of the K8s secret to be associated with the ingress resource.
    default: ""
  proxy_cache_revalidate:
    type: boolean
    description: >
      Enables revalidation of expired cache items using conditional requests with the
      "If-Modified-Since" and "If-None-Match" header fields.
      If the proxied server returns 304 (Not Modified), the cached item will be updated
      without re-downloading the entire content, improving performance.
    default: False
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 2m 14s</sub>

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/content-cache-k8s-operator__ops-testing-migration__C2/tests/unit/test_charm.py.**

/tmp/ops-upgrade-experiment/content-cache-k8s-operator__ops-testing-migration__C2/tests/unit/test_charm.py

```
File too large to read at once (23.4 KB). Consider using the grep tool to search within the file, or view with view_range to read specific sections.
```


---

<sub>⏱️ 2m 21s</sub>

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/content-cache-k8s-operator__ops-testing-migration__C2/tests/unit/test_charm.py.**

/tmp/ops-upgrade-experiment/content-cache-k8s-operator__ops-testing-migration__C2/tests/unit/test_charm.py (lines 1-150)

<details>
<summary>150 lines</summary>

```
1. # Copyright 2025 Canonical Ltd.
2. # See LICENSE file for licensing details.
3. import copy
4. import io
5. from datetime import datetime, timedelta
6. from unittest import mock
7. 
8. import pytest
9. from ops.model import ActiveStatus, BlockedStatus, MaintenanceStatus
10. from ops.testing import Harness
11. 
12. from charm import CONTAINER_PORT, ContentCacheCharm
13. 
14. BASE_CONFIG = {
15.     "site": "mysite.local",
16.     "backend": "http://mybackend.local:80",
17.     "cache_max_size": "10G",
18.     "cache_use_stale": "error timeout updating http_500 http_502 http_503 http_504",
19.     "cache_valid": "200 1h",
20. }
21. CACHE_PATH = "/var/lib/nginx/proxy/cache"
22. CONTAINER_NAME = "content-cache"
23. JUJU_ENV_CONFIG = {
24.     "JUJU_POD_NAME": "content-cache-k8s/0",
25.     "JUJU_POD_NAMESPACE": None,
26.     "JUJU_POD_SERVICE_ACCOUNT": "content-cache-k8s",
27.     "NGINX_BACKEND_SITE_NAME": "mybackend.local",
28.     "NGINX_CACHE_ALL": False,
29.     "NGINX_CACHE_INACTIVE_TIME": "10m",
30.     "NGINX_CACHE_MAX_SIZE": "10G",
31.     "NGINX_CACHE_PATH": "/var/lib/nginx/proxy/cache",
32.     "NGINX_CACHE_REVALIDATE": "off",
33.     "NGINX_CACHE_USE_STALE": "error timeout updating http_500 http_502 http_503 http_504",
34.     "NGINX_CACHE_VALID": "200 1h",
35.     "NGINX_CLIENT_MAX_BODY_SIZE": "1m",
36. }
37. INGRESS_CONFIG = {
38.     "max-body-size": "1m",
39.     "service-hostname": "mysite.local",
40.     "service-name": "content-cache-k8s",
41.     "service-port": CONTAINER_PORT,
42. }
43. PEBBLE_CONFIG = {
44.     "summary": "content-cache layer",
45.     "description": "Pebble config layer for content-cache",
46.     "services": {
47.         CONTAINER_NAME: {
48.             "override": "replace",
49.             "summary": "content-cache",
50.             "command": "/srv/content-cache/entrypoint.sh",
51.             "startup": "enabled",
52.             "environment": "",
53.         },
54.     },
55.     "checks": {
56.         CONTAINER_NAME: {
57.             "override": "replace",
58.             "exec": {"command": "ps -A | grep nginx"},
59.             "threshold": 1,
60.         }
61.     },
62. }
63. 
64. DATE_NOW = datetime.now().strftime("%d/%b/%Y:%H:%M:%S")
65. DATE_20 = (datetime.now() - timedelta(minutes=20, seconds=5)).strftime("%d/%b/%Y:%H:%M:%S")
66. DATE_19 = (datetime.now() - timedelta(minutes=19, seconds=55)).strftime("%d/%b/%Y:%H:%M:%S")
67. 
68. 
69. class TestCharm:
70.     """Unit test battery for the content-cache charm.
71. 
72.     Attrs:
73.         config: Base configuration for content-cache charm.
74.         harness: Test harness.
75.     """
76. 
77.     @pytest.fixture(autouse=True)
78.     def init_tests(self):
79.         self.config = copy.deepcopy(BASE_CONFIG)
80.         self.harness = Harness(ContentCacheCharm)
81.         self.harness.begin()
82.         yield
83.         self.harness.cleanup()
84. 
85.     @mock.patch("charm.ContentCacheCharm.configure_workload_container")
86.     def test_on_content_cache_pebble_ready(self, configure_workload_container):
87.         """
88.         arrange: content_cache_pebble_ready event is received
89.         act: configure workload container
90.         assert: workload is called just once
91.         """
92.         config = self.config
93.         harness = self.harness
94.         harness.disable_hooks()
95.         harness.update_config(config)
96.         harness.charm.on.content_cache_pebble_ready.emit(mock.Mock())
97.         assert harness.charm.unit.status == MaintenanceStatus(
98.             "Configuring workload container (config-changed)"
99.         )
100.         configure_workload_container.assert_called_once()
101. 
102.     def test_on_start(self):
103.         """
104.         arrange: workload container started
105.         act: change unit status
106.         assert: unit status is Started
107.         """
108.         harness = self.harness
109.         harness.charm.on.start.emit()
110.         assert harness.charm.unit.status == ActiveStatus()
111. 
112.     @mock.patch("charm.ContentCacheCharm.configure_workload_container")
113.     def test_on_config_changed(self, configure_workload_container):
114.         """
115.         arrange: config is changed
116.         act: update config
117.         assert: workload is called just once
118.         """
119.         config = self.config
120.         harness = self.harness
121.         harness.update_config(config)
122.         assert harness.charm.unit.status == MaintenanceStatus(
123.             "Configuring workload container (config-changed)"
124.         )
125.         configure_workload_container.assert_called_once()
126. 
127.     @mock.patch("charm.ContentCacheCharm.configure_workload_container")
128.     def test_on_upgrade_charm(self, configure_workload_container):
129.         """
130.         arrange: charm is upgraded
131.         act: configure workload container
132.         assert: workload is called just once
133.         """
134.         harness = self.harness
135.         harness.charm.on.upgrade_charm.emit()
136.         assert harness.charm.unit.status == MaintenanceStatus(
137.             "Configuring workload container (upgrade-charm)"
138.         )
139.         configure_workload_container.assert_called_once()
140. 
141.     @mock.patch("charm.ContentCacheCharm._make_nginx_config")
142.     @mock.patch("charm.ContentCacheCharm._make_pebble_config")
143.     @mock.patch("ops.model.Container.add_layer")
144.     @mock.patch("ops.model.Container.get_service")
145.     @mock.patch("ops.model.Container.make_dir")
146.     @mock.patch("ops.model.Container.push")
147.     @mock.patch("ops.model.Container.get_plan")
148.     @mock.patch("ops.model.Container.pebble")
149.     @mock.patch("ops.model.Container.can_connect")
150.     def test_configure_workload_container(
```

</details>


---

<sub>⏱️ 2m 21s</sub>

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/content-cache-k8s-operator__ops-testing-migration__C2/tests/unit/test_charm.py.**

/tmp/ops-upgrade-experiment/content-cache-k8s-operator__ops-testing-migration__C2/tests/unit/test_charm.py (lines 150-350)

<details>
<summary>201 lines</summary>

```
150.     def test_configure_workload_container(
151.         self,
152.         can_connect,
153.         pebble,
154.         get_plan,
155.         push,
156.         make_dir,
157.         get_service,
158.         add_layer,
159.         make_pebble_config,
160.         make_nginx_config,
161.     ):
162.         """
163.         arrange: config is changed
164.         act: configure workload container
165.         assert: unit status is Ready
166.         """
167.         config = self.config
168.         harness = self.harness
169.         harness.update_config(config)
170.         make_pebble_config.assert_called_once()
171.         make_nginx_config.assert_called_once()
172.         assert add_layer.call_count == 2
173.         assert harness.charm.unit.status, ActiveStatus("Ready")
174. 
175.     @mock.patch("ops.model.Container.pull")
176.     @pytest.mark.parametrize(
177.         "test_input,expected",
178.         [
179.             ("", []),
180.             (
181.                 f"10.10.10.11 - - [{DATE_NOW}\n"
182.                 f"10.10.10.11 - - [{DATE_NOW}\n"
183.                 f"10.10.10.11 - - [{DATE_NOW}\n"
184.                 f"10.10.10.12 - - [{DATE_NOW}\n"
185.                 f"10.10.10.12 - - [{DATE_NOW}",
186.                 [("10.10.10.11", 3), ("10.10.10.12", 2)],
187.             ),
188.             (
189.                 f"10.10.10.11 - - [{DATE_NOW}\n"
190.                 f"10.10.10.11 - - [{DATE_NOW}\n"
191.                 f"10.10.10.11 - - [{DATE_NOW}",
192.                 [("10.10.10.11", 3)],
193.             ),
194.             (f"10.10.10.11 - - [{DATE_NOW}", [("10.10.10.11", 1)]),
195.             (
196.                 f"10.10.10.12 - - [{DATE_20}\n10.10.10.10 - - [{DATE_19}\n",
197.                 [("10.10.10.10", 1)],
198.             ),
199.         ],
200.     )
201.     def test_report_visits_by_ip(self, mock_pull, test_input, expected):
202.         """
203.         arrange: some nginx log lines are simulated
204.         act: process the log line
205.         assert: only the log lines logged less than 20 minutes ago are accepted
206.         """
207.         mock_pull.return_value = io.StringIO(test_input)
208.         action = self.harness.charm._report_visits_by_ip()
209.         assert action == expected
210. 
211.     @pytest.mark.parametrize(
212.         "test_input,expected", [(f"10.10.10.11 - - [{DATE_NOW}", "10.10.10.11")]
213.     )
214.     def test_get_ip(self, test_input, expected):
215.         """
216.         arrange: some nginx log lines are simulated
217.         act: process the log line
218.         assert: return the IP of the log line
219.         """
220.         action = self.harness.charm._get_ip(test_input)
221.         assert action == expected
222. 
223.     @pytest.mark.parametrize(
224.         "test_input,expected",
225.         [
226.             (f"10.10.10.11 - - [{DATE_19}", True),
227.             ("", False),
228.             (f"10.10.10.11 - - [{DATE_20}", False),
229.         ],
230.     )
231.     def test_filter_lines(self, test_input, expected):
232.         """
233.         arrange: a nginx log line is simulated
234.         act: process the log line
235.         assert: only the line logged less than 20 minutes ago is accepted.
236.         """
237.         action = self.harness.charm._filter_lines(test_input)
238.         assert action == expected
239. 
240.     @mock.patch("charm.ContentCacheCharm._make_pebble_config")
241.     @mock.patch("ops.model.Container.add_layer")
242.     @mock.patch("ops.model.Container.get_service")
243.     @mock.patch("ops.model.Container.make_dir")
244.     @mock.patch("ops.model.Container.push")
245.     @mock.patch("ops.model.Container.pebble")
246.     def test_configure_workload_container_container_not_running(
247.         self, pebble, push, make_dir, get_service, add_layer, make_pebble_config
248.     ):
249.         """
250.         arrange: config is changed
251.         act: check if service is running and is not
252.         assert: services are not replanned
253.         """
254.         config = self.config
255.         harness = self.harness
256.         harness.update_config(config)
257.         make_pebble_config.assert_called_once()
258.         get_service.return_value.is_running.return_value = False
259.         harness.update_config(config)
260.         pebble.replan_services().assert_not_called()
261. 
262.     @mock.patch("charm.ContentCacheCharm._make_pebble_config")
263.     @mock.patch("ops.model.Container.add_layer")
264.     @mock.patch("ops.model.Container.get_service")
265.     @mock.patch("ops.model.Container.make_dir")
266.     @mock.patch("ops.model.Container.push")
267.     @mock.patch("ops.model.Container.get_plan")
268.     @mock.patch("ops.model.Container.pebble")
269.     @mock.patch("ops.model.Container.can_connect")
270.     def test_configure_workload_container_pebble_services_already_configured(
271.         self,
272.         can_connect,
273.         pebble,
274.         get_plan,
275.         push,
276.         make_dir,
277.         get_service,
278.         add_layer,
279.         make_pebble_config,
280.     ):
281.         """
282.         arrange: config is changed
283.         act: check if current config is different
284.         assert: services are replanned again
285.         """
286.         config = self.config
287.         harness = self.harness
288. 
289.         config = copy.deepcopy(BASE_CONFIG)
290.         make_pebble_config.return_value = {"services": "content-cache"}
291.         harness.update_config(config)
292.         make_pebble_config.assert_called_once()
293.         assert add_layer.call_count == 2
294.         assert harness.charm.unit.status == ActiveStatus("Ready")
295. 
296.     @mock.patch("charm.ContentCacheCharm._make_pebble_config")
297.     @mock.patch("ops.model.Container.add_layer")
298.     @mock.patch("ops.model.Container.get_service")
299.     @mock.patch("ops.model.Container.make_dir")
300.     @mock.patch("ops.model.Container.push")
301.     @mock.patch("ops.model.Container.get_plan")
302.     @mock.patch("ops.model.Container.pebble")
303.     @mock.patch("ops.model.Container.can_connect")
304.     @mock.patch("ops.model.Container.isdir")
305.     def test_configure_workload_container_has_cache_directory(
306.         self,
307.         can_connect,
308.         pebble,
309.         get_plan,
310.         push,
311.         make_dir,
312.         get_service,
313.         add_layer,
314.         make_pebble_config,
315.         isdir,
316.     ):
317.         """
318.         arrange: workload container is ready
319.         act: check if cache dir is created
320.         assert: cache directory is created
321.         """
322.         config = self.config
323.         harness = self.harness
324. 
325.         config = copy.deepcopy(BASE_CONFIG)
326.         harness.update_config(config)
327.         assert make_pebble_config.call_count == 2
328.         assert harness.charm.unit.status == ActiveStatus("Ready")
329.         container = harness.charm.unit.get_container(CONTAINER_NAME)
330.         assert container.isdir(CACHE_PATH)
331. 
332.     @mock.patch("charm.ContentCacheCharm._make_pebble_config")
333.     @mock.patch("ops.model.Container.add_layer")
334.     @mock.patch("ops.model.Container.get_service")
335.     @mock.patch("ops.model.Container.make_dir")
336.     @mock.patch("ops.model.Container.push")
337.     @mock.patch("ops.model.Container.get_plan")
338.     @mock.patch("ops.model.Container.pebble")
339.     @mock.patch("ops.model.Container.can_connect")
340.     def test_configure_workload_container_empty_config(
341.         self,
342.         can_connect,
343.         pebble,
344.         get_plan,
345.         push,
346.         make_dir,
347.         get_service,
348.         add_layer,
349.         make_pebble_config,
350.     ):
```

</details>


---

<sub>⏱️ 2m 28s</sub>

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/content-cache-k8s-operator__ops-testing-migration__C2/tests/unit/test_charm.py.**

/tmp/ops-upgrade-experiment/content-cache-k8s-operator__ops-testing-migration__C2/tests/unit/test_charm.py (lines 350-600)

<details>
<summary>251 lines</summary>

```
350.     ):
351.         """
352.         arrange: config is changed
353.         act: there is no change
354.         assert: charm replans services charm is ready as expected
355.         """
356.         config = self.config
357.         harness = self.harness
358. 
359.         config = copy.deepcopy(BASE_CONFIG)
360.         make_pebble_config.return_value = {"services": {}}
361.         harness.update_config(config)
362.         assert harness.charm.unit.status == ActiveStatus("Ready")
363. 
364.     @mock.patch("charm.ContentCacheCharm._make_pebble_config")
365.     def test_configure_workload_container_missing_configs(self, make_pebble_config):
366.         """
367.         arrange: config is empty
368.         act: raises exception
369.         assert: unit status is Blocked
370.         """
371.         config = self.config
372.         harness = self.harness
373.         config["backend"] = None
374.         harness.update_config(config)
375.         make_pebble_config.assert_not_called()
376.         assert harness.charm.unit.status == BlockedStatus("Required config(s) empty: backend")
377. 
378.     def test_generate_keys_zone(self):
379.         """
380.         arrange: set value for env variable NGINX_KEYS_ZONE
381.         act: generate keys zone
382.         assert: keys zone is generated as expected
383.         """
384.         harness = self.harness
385.         harness.disable_hooks()
386.         expected = "39c631ffb52d-cache"
387.         assert harness.charm._generate_keys_zone("mysite.local") == expected
388.         expected = "8b79f9e4b3e8-cache"
389.         assert (
390.             harness.charm._generate_keys_zone("my-really-really-really-long-site-name.local")
391.             == expected
392.         )
393.         expected = "d41d8cd98f00-cache"
394.         assert harness.charm._generate_keys_zone("") == expected
395. 
396.     def test_make_ingress_config(self):
397.         """
398.         arrange: set ingress config
399.         act: generate ingress config
400.         assert: ingress config is generated as expected
401.         """
402.         config = self.config
403.         harness = self.harness
404.         harness.disable_hooks()
405.         harness.update_config(config)
406.         expected = copy.deepcopy(INGRESS_CONFIG)
407.         assert harness.charm._make_ingress_config() == expected
408. 
409.     def test_make_ingress_config_client_max_body_size(self):
410.         """
411.         arrange: set ingress config overriding client_max_body_size
412.         act: generate ingress config
413.         assert: client_max_body_size is overridden as expected
414.         """
415.         config = self.config
416.         harness = self.harness
417.         harness.disable_hooks()
418.         config["client_max_body_size"] = "50m"
419.         harness.update_config(config)
420.         expected = copy.deepcopy(INGRESS_CONFIG)
421.         expected["max-body-size"] = "50m"
422.         assert harness.charm._make_ingress_config() == expected
423. 
424.     def test_make_ingress_config_tls_secret(self):
425.         """
426.         arrange: set tls_secret_name ingress config
427.         act: generate tls_secret_name ingress config
428.         assert: tls_secret_name is correct
429.         """
430.         config = self.config
431.         harness = self.harness
432.         harness.disable_hooks()
433.         config["tls_secret_name"] = "mysite-com-tls"  # nosec
434.         harness.update_config(config)
435.         expected = copy.deepcopy(INGRESS_CONFIG)
436.         expected["tls-secret-name"] = "mysite-com-tls"  # nosec
437.         assert harness.charm._make_ingress_config() == expected
438. 
439.     def test_make_ingress_config_with_proxy_relation(self):
440.         """
441.         arrange: set nginx-proxy relation
442.         act: verify ingress config
443.         assert: ingress config is generated as expected
444.         """
445.         harness = self.harness
446.         expected = copy.deepcopy(INGRESS_CONFIG)
447.         assert harness.charm._make_ingress_config() == expected
448.         relation_id = harness.add_relation("nginx-proxy", "hello-kubecon")
449.         harness.add_relation_unit(relation_id, "hello-kubecon/0")
450.         relations_data = {
451.             "service-name": "test-proxy",
452.             "service-hostname": "foo.internal",
453.             "service-port": "80",
454.         }
455.         harness.update_relation_data(relation_id, "hello-kubecon", relations_data)
456.         new_ingress_config = harness.charm._make_ingress_config()
457.         assert new_ingress_config["service-hostname"] == relations_data["service-hostname"]
458. 
459.     def test_make_env_config(self):
460.         """
461.         arrange: define env variables
462.         act: set env variables
463.         assert: env variables are correct
464.         """
465.         config = self.config
466.         harness = self.harness
467.         harness.disable_hooks()
468.         harness.update_config(config)
469.         expected = JUJU_ENV_CONFIG
470.         expected["CONTAINER_PORT"] = 8080
471.         expected["CONTENT_CACHE_BACKEND"] = "http://mybackend.local:80"
472.         expected["CONTENT_CACHE_SITE"] = "mysite.local"
473.         expected["NGINX_BACKEND"] = "http://mybackend.local:80"
474.         expected["NGINX_KEYS_ZONE"] = harness.charm._generate_keys_zone("mysite.local")
475.         expected["NGINX_SITE_NAME"] = "mysite.local"
476.         expected["NGINX_CACHE_ALL"] = "proxy_ignore_headers Cache-Control Expires"
477.         assert harness.charm._make_env_config() == expected
478. 
479.     def test_make_env_config_with_proxy_relation(self):
480.         """
481.         arrange: set nginx-proxy relation
482.         act: verify env config
483.         assert: env config is generated as expected
484.         """
485.         config = self.config
486.         harness = self.harness
487.         harness.disable_hooks()
488.         harness.update_config(config)
489.         current_env_config = harness.charm._make_env_config()
490.         current_site = current_env_config["CONTENT_CACHE_SITE"]
491.         assert current_site == "mysite.local"
492.         relation_id = harness.add_relation("nginx-proxy", "hello-kubecon")
493.         harness.add_relation_unit(relation_id, "hello-kubecon/0")
494.         relations_data = {
495.             "service-name": "test-proxy",
496.             "service-hostname": "foo.internal",
497.             "service-port": "80",
498.         }
499.         harness.update_relation_data(relation_id, "hello-kubecon", relations_data)
500.         new_env_config = harness.charm._make_env_config()
501.         new_site = new_env_config["CONTENT_CACHE_SITE"]
502.         assert new_site == relations_data["service-hostname"]
503. 
504.     def test_make_pebble_config(self):
505.         """
506.         arrange: define pebble config
507.         act: set pebble config
508.         assert: pebble config is correct
509.         """
510.         config = self.config
511.         harness = self.harness
512.         harness.disable_hooks()
513.         harness.update_config(config)
514.         env_config = harness.charm._make_env_config()
515.         expected = PEBBLE_CONFIG
516.         expected["services"]["content-cache"]["environment"] = harness.charm._make_env_config()
517.         assert harness.charm._make_pebble_config(env_config) == expected
518. 
519.     def test_make_nginx_config(self):
520.         """
521.         arrange: define nginx config
522.         act: set nginx config
523.         assert: ensure envConfig returned is correct
524.         """
525.         config = self.config
526.         harness = self.harness
527.         harness.disable_hooks()
528.         harness.update_config(config)
529.         env_config = harness.charm._make_env_config()
530.         with open("tests/files/nginx_config.txt") as f:
531.             expected = f.read()
532.             assert harness.charm._make_nginx_config(env_config) == expected
533. 
534.     def test_make_nginx_config_backend_site_name(self):
535.         """
536.         arrange: define nginx config with charm config backend_site_config
537.         act: set nginx config
538.         assert: ensure envConfig returned is correct
539.         """
540.         config = self.config
541.         harness = self.harness
542.         harness.disable_hooks()
543.         config["backend_site_name"] = "myoverridebackendsitename.local"
544.         harness.update_config(config)
545.         env_config = harness.charm._make_env_config()
546.         with open("tests/files/nginx_config_backend_site_name.txt") as f:
547.             expected = f.read()
548.             assert harness.charm._make_nginx_config(env_config) == expected
549. 
550.     def test_make_nginx_config_client_max_body_size(self):
551.         """
552.         arrange: define nginx config with charm config client_max_body_size
553.         act: set nginx config
554.         assert: ensure envConfig returned is correct
555.         """
556.         config = self.config
557.         harness = self.harness
558.         harness.disable_hooks()
559.         config["client_max_body_size"] = "50m"
560.         harness.update_config(config)
561.         env_config = harness.charm._make_env_config()
562.         with open("tests/files/nginx_config_client_max_body_size.txt") as f:
563.             expected = f.read()
564.             assert harness.charm._make_nginx_config(env_config) == expected
565. 
566.     def test_missing_charm_configs(self):
567.         """
568.         arrange: define charm config with missing field
569.         act: set charm config
570.         assert: ensure required configs present and return those missing
571.         """
572.         config = self.config
573.         harness = self.harness
574.         harness.disable_hooks()
575.         # None missing, all required configs set.
576.         harness.update_config(config)
577.         expected = []
578.         assert harness.charm._missing_charm_configs() == expected
579. 
580.     def test_missing_charm_configs_missing_all(self):
581.         """
582.         arrange: define charm config with all missing
583.         act: set charm config
584.         assert: ensure required configs present and return those missing
585.         """
586.         config = self.config
587.         harness = self.harness
588.         harness.disable_hooks()
589.         config.pop("backend")
590.         harness.update_config(config)
591.         expected = ["backend"]
592.         assert harness.charm._missing_charm_configs() == expected
593. 
594.     def test_missing_charm_configs_unset_all(self):
595.         """
596.         arrange: define charm config with all unset
597.         act: set charm config
598.         assert: ensure required configs present and return those missing
599.         """
600.         config = self.config
```

</details>


---

<sub>⏱️ 2m 32s</sub>

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/content-cache-k8s-operator__ops-testing-migration__C2/tests/unit/test_charm.py.**

/tmp/ops-upgrade-experiment/content-cache-k8s-operator__ops-testing-migration__C2/tests/unit/test_charm.py (lines 600-750)

<details>
<summary>52 lines</summary>

```
600.         config = self.config
601.         harness = self.harness
602.         harness.disable_hooks()
603.         config["backend"] = None
604.         harness.update_config(config)
605.         expected = ["backend"]
606.         assert harness.charm._missing_charm_configs() == expected
607. 
608.     def test_make_env_config_with_proxy_cache_revalidate(self):
609.         """
610.         arrange: define configuration with proxy_cache_revalidate enabled
611.         act: generate environment configuration
612.         assert: env variable NGINX_CACHE_REVALIDATE is set correctly
613.         """
614.         config = self.config
615.         harness = self.harness
616.         harness.disable_hooks()
617.         config["proxy_cache_revalidate"] = True
618.         harness.update_config(config)
619.         env_config = harness.charm._make_env_config()
620.         assert env_config["NGINX_CACHE_REVALIDATE"] == "on"
621. 
622.     def test_make_env_config_without_proxy_cache_revalidate(self):
623.         """
624.         arrange: define configuration with proxy_cache_revalidate disabled
625.         act: generate environment configuration
626.         assert: env variable NGINX_CACHE_REVALIDATE is set to off
627.         """
628.         config = self.config
629.         harness = self.harness
630.         harness.disable_hooks()
631.         config["proxy_cache_revalidate"] = False
632.         harness.update_config(config)
633.         env_config = harness.charm._make_env_config()
634.         assert env_config["NGINX_CACHE_REVALIDATE"] == "off"
635. 
636.     def test_make_nginx_config_proxy_cache_revalidate(self):
637.         """
638.         arrange: define nginx config with proxy_cache_revalidate enabled
639.         act: set nginx config
640.         assert: ensure nginx config contains proxy_cache_revalidate on
641.         """
642.         config = self.config
643.         harness = self.harness
644.         harness.disable_hooks()
645.         config["proxy_cache_revalidate"] = True
646.         harness.update_config(config)
647.         env_config = harness.charm._make_env_config()
648.         with open("tests/files/nginx_config_proxy_cache_revalidate.txt") as f:
649.             expected = f.read()
650.             assert harness.charm._make_nginx_config(env_config) == expected
651.
```

</details>


---

<sub>⏱️ 4m 11s</sub>

### 💬 Copilot

Now I have everything I need. Let me fetch some more specific API details and then write the migration.

---

<sub>⏱️ 4m 12s</sub>

### ✅ `web_fetch`

**https://ops.readthedocs.io/en/latest/howto/write-unit-tests-for-a-charm/**

<details>
<summary>Arguments</summary>

```json
{
  "max_length": 10000,
  "url": "https://ops.readthedocs.io/en/latest/howto/write-unit-tests-for-a-charm/"
}
```

</details>

<details>
<summary>126 lines</summary>

```
Contents of https://ops.readthedocs.io/en/latest/howto/write-unit-tests-for-a-charm/:
## Set up your environment[¶](#set-up-your-environment "Link to this heading")

First of all, install the Ops testing framework. To do this in a virtual environment while we’re developing, use `pip` or a different package manager. For example:

pip install ops\[testing\]

Or using `pyproject.toml`:

\[dependency-groups\]
test \= \[
  "ops\[testing\]",
\]

## Create the charm and test files[¶](#create-the-charm-and-test-files "Link to this heading")

So that we have a charm to test, declare a placeholder charm type in `charm.py`:

class MyCharm(ops.CharmBase):
    pass

Then open a new `test_foo.py` file for the test code and import the [`ops.testing`](../../reference/ops-testing/#ops-testing) framework:

import ops
from ops import testing

## Write a test[¶](#write-a-test "Link to this heading")

To write a test function, use a `Context` object to encapsulate the charm type (`MyCharm`) and any necessary metadata. The test should then define the initial `State` and call `Context.run` with an `event` and initial `State`.

This follows the typical test structure:

*   Arrange inputs, mock necessary functions/system calls, and initialise the charm
    
*   Act by calling `Context.run`
    
*   Assert expected outputs or function calls.
    

For example, suppose that `MyCharm` uses `Container.Push` to write a YAML config file on the pebble-ready event:

def \_on\_pebble\_ready(self, event: ops.PebbleReadyEvent):
    container \= event.workload
    container.push('/etc/config.yaml', 'message: Hello, world!', make\_dirs\=True)
    \# ...

A test for this behaviour might look like:

import yaml
from ops import testing

from charm import MyCharm

def test\_pebble\_ready\_writes\_config\_file():
    """Test that on pebble-ready, a config file is written."""
    \# Arrange: setting up the inputs
    ctx \= testing.Context(MyCharm)
    container \= testing.Container(name\="some-container", can\_connect\=True)
    state\_in \= testing.State(
        containers\=\[container\],
        leader\=True,
    )

    \# Act:
    state\_out \= ctx.run(ctx.on.pebble\_ready(container\=container), state\_in)

    \# Assert:
    container\_fs \= state\_out.get\_container("some-container").get\_filesystem(ctx)
    cfg\_file \= container\_fs / "etc" / "config.yaml"
    config \= yaml.safe\_load(cfg\_file.read\_text())
    assert config\["message"\] \== "Hello, world!"

Note

If you prefer to use unittest, you should rewrite this as a method of a `TestCase` subclass.

To start with a `State` that has components based on the charm’s metadata, use the `State.from_context` method. For example, with this `charmcraft.yaml` file:

name: my-charm
containers:
  workload:
    resource: workload-image
peers:
  group-chat:
    interface: gossip

Using `State.from_context` will automatically add in a `testing.Container` and `testing.PeerRelation`. For example:

def test\_peer\_changed():
    ctx \= testing.Context(MyCharm)
    \# We can pass in all of the arguments for \`State()\` as well.
    state\_in \= testing.State.from\_context(ctx, leader\=True)
    rel\_in \= state\_in.get\_relations('group-chat')\[0\]
    state\_out \= ctx.run(ctx.on.relation\_changed(rel), state\_in)
    rel\_out \= state\_out.get\_relation(rel.in)
    assert rel\_out.peers\_data...

Note

If your `charmcraft.yaml` uses a charmcraft extension (e.g. `extensions: [flask-framework]`), the metadata, config, and actions that the extension adds are automatically merged in when the testing framework loads the charm spec. You do not need to manually specify them.

If your `charmcraft.yaml` defines keys that overlap with what the extension provides (e.g. a config option with the same name), the testing framework will raise a `ValueError`, matching the behaviour of `charmcraft pack`. Rename or remove the overlapping keys to fix this.

## Generate tests from a deployed model[¶](#generate-tests-from-a-deployed-model "Link to this heading")

If your test needs realistic relation inputs from a deployed model, you can use `jhack scenario snapshot` to capture state, then adapt the generated data to `ops.testing` code.

For a workflow focused on relation debugging, see [Generate tests from a deployed model](../manage-relations/#generate-tests-from-a-deployed-model).

## Mock beyond the State[¶](#mock-beyond-the-state "Link to this heading")

If you wish to use the framework to test an existing charm type, you will probably need to mock out certain calls that are not covered by the `State` data structure. In that case, you will have to manually mock, patch or otherwise simulate those calls.

For example, suppose that the charm we’re testing uses the [lightkube client](https://github.com/gtsystem/lightkube) to talk to Kubernetes. To mock that object, modify the test file to contain:

from unittest.mock import MagicMock, patch

import pytest
from ops import testing

from charm import MyCharm

@pytest.fixture
def my\_charm():
    with patch("charm.lightkube.Client"):
        yield MyCharm

Then you should rewrite the test to pass the patched charm type to the `Context`, instead of the unpatched one. In code:

def test\_charm\_runs(my\_charm):
    \# Arrange:
    \#  Create a Context to specify what code we will be running
    ctx \= testing.Context(my\_charm)
    \# ...

Note

If you use pytest, you should put the `my_charm` fixture in a top level `conftest.py`, as it will likely be shared between all your unit tests.

## Reuse state[¶](#reuse-state "Link to this heading")

Each test is typically an isolated test of how your charm responds to a single event. However, sometimes it’s more convenient to simulate several events in the same test. For example, to check what happens when your charm receives events in a particular order.

After checking a `State` object that `ctx.run` returns, you can provide the same state as input to another simulated event. If you need to modify the state between the events, create a new `State` object instead of modifying the original `State` object. For example:

state\_out \= ctx.run(...)  \# The State we want to reuse.
relation \= state\_out.get\_relation(...)  \# A relation we want to modify.

\# Copy and modify the relation data.
new\_local\_app\_data \= relation.local\_app\_data.copy()
new\_local\_app\_data\["foo"\] \= "bar"

\# Create a new State.
new\_relation \= dataclasses.replace(relation, local\_app\_data\=new\_local\_app\_data)
new\_state \= dataclasses.replace(state\_out, relations\={new\_relation})

## Access the charm instance[¶](#access-the-charm-instance "Link to this heading")

If you need to access the charm instance in a test, use the `testing.Context` instance as a context manager, then access `mgr.charm`. When setting up the context manager, use an event the charm doesn’t observe, such as `update_status`. For example:

\# Charm code

class Charm(CharmBase):
    def workload\_is\_ready(self):
        ...  \# Some business logic.
        return True

\# Testing code

def test\_charm\_reports\_workload\_ready():
    ctx \= testing.Context(Charm)
    state\_in \= testing.State(...)  \# Some state to represent a ready workload.
    with ctx(ctx.on.update\_status(), state\_in) as mgr:
        assert mgr.charm.workload\_is\_ready()
        ...

## Run your tests[¶](#run-your-tests "Link to this heading")

Run all your tests with:

tox -e unit

## Examples[¶](#examples "Link to this heading")

Machine charms:

*   Our [machine-tinyproxy](https://github.com/canonical/operator/tree/main/examples/machine-tinyproxy/tests/unit) example charm, from [Write your first machine charm](../../tutorial/write-your-first-machine-charm/#machine-charm-tutorial)
    
*   [ubuntu-manpages-operator](https://github.com/canonical/ubuntu-manpages-operator/tree/main/tests/unit)
    

Kubernetes charms:

*   Our [k8s-3-postgresql](https://github.com/canonical/operator/tree/main/examples/k8s-3-postgresql/tests/unit) example charm, from the [Integrate your charm with PostgreSQL](../../tutorial/from-zero-to-hero-write-your-first-kubernetes-charm/integrate-your-charm-with-postgresql/#integrate-your-charm-with-postgresql) chapter in our Kubernetes charm tutorial (the charms from other chapters also have unit tests)
    
*   Our [httpbin-demo](https://github.com/canonical/operator/tree/main/examples/httpbin-demo/tests/unit) example charm
```

</details>


---

<sub>⏱️ 4m 12s</sub>

### ✅ `bash`

**Check ops version and testing API**

$ cd /tmp/ops-upgrade-experiment/content-cache-k8s-operator__ops-testing-migration__C2 && pip show ops 2>/dev/null | grep Version && pip show ops-scenario 2>/dev/null | grep Version && python -c "from ops import testing; help(testing.Context.manager)" 2>&1 | head -30

```
Version: 3.5.1
Version: 8.7.0
bash: python: command not found
<exited with exit code 0>
```


---

<sub>⏱️ 5m 31s</sub>

### ✅ `bash`

**Check content-cache_rock and tox config**

$ ls /tmp/ops-upgrade-experiment/content-cache-k8s-operator__ops-testing-migration__C2/content-cache_rock/ && echo "---" && cat /tmp/ops-upgrade-experiment/content-cache-k8s-operator__ops-testing-migration__C2/tox.toml

<details>
<summary>140 lines</summary>

```
entrypoint.sh  nginx-logging-format.conf  nginx_cfg.tmpl  rockcraft.yaml
---
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
TZ = "UTC"

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
all_path = [ "{toxinidir}/src/", "{toxinidir}/tests/" ]
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 12m 57s</sub>

### ✅ `bash`

**Check available status classes in ops.testing**

$ cd /tmp/ops-upgrade-experiment/content-cache-k8s-operator__ops-testing-migration__C2 && python3 -c "from ops import testing; print(dir(testing))" 2>&1 | tr ',' '\n' | grep -i status

<details>
<summary>7 lines</summary>

```
'ActiveStatus'
 'BlockedStatus'
 'ErrorStatus'
 'MaintenanceStatus'
 'UnknownStatus'
 'WaitingStatus'
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 13m 5s</sub>

### 💬 Copilot

Good, `testing.WaitingStatus` is available. Now let me write the full migrated test file:

---

<sub>⏱️ 13m 5s</sub>

### ✅ `bash`

**Check Context API signatures**

$ cd /tmp/ops-upgrade-experiment/content-cache-k8s-operator__ops-testing-migration__C2 && python3 -c "
from ops import testing
import inspect
# Check Context.__call__ signature
print(inspect.signature(testing.Context.__call__))
# Check Context.run signature
print(inspect.signature(testing.Context.run))
" 2>&1

```
(self, event: '_Event', state: 'State') -> 'Manager[CharmType]'
(self, event: '_Event', state: 'State') -> 'State'
<exited with exit code 0>
```


---

<sub>⏱️ 13m 14s</sub>

### ✅ `bash`

**Check Manager class**

$ cd /tmp/ops-upgrade-experiment/content-cache-k8s-operator__ops-testing-migration__C2 && python3 -c "
from ops import testing
import inspect
# Check Manager
print(inspect.getmembers(testing.Context.__call__(testing.Context.__new__(testing.Context), None, None).__class__ if False else type('M', (), {'charm': None, 'run': None}), predicate=inspect.isfunction))
# Just look at what Context.on provides
ctx = testing.Context.__new__(testing.Context)
" 2>&1 | head -5

python3 -c "
from ops import testing
import inspect
# What does Manager look like?
import scenario
print([x for x in dir(scenario) if 'Manager' in x or 'manager' in x])
" 2>&1

```
[]
['Manager']
<exited with exit code 0>
```


---

<sub>⏱️ 14m 57s</sub>

### ℹ️ Info

Operation cancelled by user

---

<sub>Generated by [GitHub Copilot CLI](https://github.com/features/copilot/cli)</sub>
