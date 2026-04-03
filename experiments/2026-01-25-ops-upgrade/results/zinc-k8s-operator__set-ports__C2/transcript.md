# 🤖 Copilot CLI Session

> [!NOTE]
> - **Session ID:** `d5e178b0-ace9-40d6-896c-2e6107cf1d8a`  
> - **Started:** 4/3/2026, 9:29:10 AM  
> - **Duration:** 2m 37s  
> - **Exported:** 4/3/2026, 9:31:48 AM  

---

<sub>⏱️ 5s</sub>

### 👤 User

ops 2.7.0 added a declarative Unit.set_ports() API that replaces the imperative open_port()/close_port() pattern. Instead of tracking which ports to open and close individually, charms declare the full set of desired ports and ops handles the diff. Learn how to use that feature and update this charm to make use of it.

---

<sub>⏱️ 18s</sub>

### ✅ `task`

**Explore charm port usage**

<details>
<summary>Arguments</summary>

```json
{
  "name": "explore-charm",
  "agent_type": "explore",
  "description": "Explore charm port usage",
  "prompt": "In the repository at /tmp/ops-upgrade-experiment/zinc-k8s-operator__set-ports__C2, find all usages of open_port, close_port, opened_ports, and any port-related logic. Show me:\n1. The full content of any files that use these port APIs\n2. What charm events trigger port opening/closing\n3. The charm's overall structure (what src/ contains)\n4. Any existing tests related to ports\n\nBe thorough - show file paths and relevant code sections with line numbers.",
  "mode": "background"
}
```

</details>

```
Agent started in background with agent_id: explore-charm. You can use read_agent tool with this agent_id to check status and retrieve results. Instruct the user to use /tasks to manage the background agent.
```


---

<sub>⏱️ 21s</sub>

### ✅ `web_search`

**ops 2.7.0 Unit.set_ports() declarative API replace open_port close_port example usage**

<details>
<summary>Arguments</summary>

```json
{
  "query": "ops 2.7.0 Unit.set_ports() declarative API replace open_port close_port example usage"
}
```

</details>

```
{"type":"","text":{"value":"","annotations":null},"bing_searches":null,"annotations":null}
```


---

<sub>⏱️ 31s</sub>

### ✅ `web_fetch`

**https://ops.readthedocs.io/en/latest/reference/ops.html#ops.Unit.set_ports**

<details>
<summary>Arguments</summary>

```json
{
  "url": "https://ops.readthedocs.io/en/latest/reference/ops.html#ops.Unit.set_ports"
}
```

</details>

<details>
<summary>42 lines</summary>

```
Contents of https://ops.readthedocs.io/en/latest/reference/ops.html#ops.Unit.set_ports:
The API to respond to Juju events and manage the application.

This API provides core features to your charm, including:

*   [`CharmBase`](#ops.CharmBase "ops.CharmBase"), the base class for charms and [`Object`](#ops.Object "ops.Object"), the base class for charm libraries.
    
*   [`EventBase`](#ops.EventBase "ops.framework.EventBase") class and individual event types, like the [`ActionEvent`](#ops.ActionEvent "ops.ActionEvent") class.
    
*   [`Framework`](#ops.Framework "ops.Framework") class, the main interface for the charm to ops library infrastructure, including:
    
    *   [`on`](#ops.Framework.on "ops.Framework.on") shorthand property used to [`observe()`](#ops.Framework.observe "ops.Framework.observe") and react to Juju events.
        
    *   [`model`](#ops.Framework.model "ops.Framework.model") attribute to get hold of the Model instance.
        
*   [`Model`](#ops.Model "ops.model.Model") class that represents the Juju model, accessible as `self.model` in a charm, including:
    
    *   [`app`](#ops.Model.app "ops.Model.app") attribute, representing the application associated with the charm.
        
    *   [`unit`](#ops.Model.unit "ops.Model.unit") attribute, representing the unit of the application the charm is running on.
        
    *   [`relations`](#ops.Model.relations "ops.Model.relations") attribute, which provides access to relations (integrations) defined in the charm, allowing interaction with other applications.
        
*   [`Container`](#ops.Container "ops.Container") class to control Kubernetes workloads, including:
    
    *   [`add_layer()`](#ops.Container.add_layer "ops.Container.add_layer") and [`replan()`](#ops.Container.replan "ops.Container.replan") methods to update Pebble configuration.
        
    *   [`pull()`](#ops.Container.pull "ops.Container.pull") and [`push()`](#ops.Container.push "ops.Container.push") methods to copy data to and from a container, respectively.
        
    *   [`exec()`](#ops.Container.exec "ops.Container.exec") method to run arbitrary commands inside the container.
        
*   [`StatusBase`](#ops.StatusBase "ops.StatusBase") class and individual status types, like the [`ActiveStatus`](#ops.ActiveStatus "ops.ActiveStatus") class.
    

_class_ ops.ActionEvent(_handle: [Handle](#ops.Handle "ops.framework.Handle")_, _id: [str](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.14)") | [None](https://docs.python.org/3/library/constants.html#None "(in Python v3.14)") \= None_)[\[source\]](../../_modules/ops/charm/#ActionEvent)[¶](#ops.ActionEvent "Link to this definition")

Bases: [`EventBase`](#ops.EventBase "ops.framework.EventBase")

Events raised by Juju when an administrator invokes a Juju Action.

This class is the data type of events triggered when an administrator invokes a Juju Action. Callbacks bound to these events may be used for responding to the administrator’s Juju Action request.

To read the parameters for the action, see the instance variable [`params`](#ops.ActionEvent.params "ops.ActionEvent.params"). To respond with the result of the action, call [`set_results()`](#ops.ActionEvent.set_results "ops.ActionEvent.set_results"). To add progress messages that are visible as the action is progressing use [`log()`](#ops.ActionEvent.log "ops.ActionEvent.log").

defer() → [NoReturn](https://docs.python.org/3/library/typing.html#typing.NoReturn "(in Python v3.14)")[\[source\]](../../_modules/ops/charm/#ActionEvent.defer)[¶](#ops.ActionEvent.defer "Link to this definition")

Action events are not deferrable like other events.

This is because an action runs synchronously and the administrator is waiting for the result.

Raises:

[**RuntimeError**](https://docs.python.org/3/library/exceptions.html#RuntimeError "(in Python v3.14)") – always.

fail(_message: [str](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.14)") \= ''_)[\[source\]](../../_modules/ops/charm/#ActionEvent.fail)[¶](#ops.ActionEvent.fail "Link to this definition")

Report that this action has failed.

Parameters:

**message** – Optional message to record why it has failed.

id_: [str](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.14)")_ _\= ''_[¶](#ops.ActionEvent.id "Link to this definition")

The Juju ID of the action invocation.

load\_params(

_cls: [type](https://docs.python.org/3/library/functions.html#type "(in Python v3.14)")\[\_T\]_,

_\*args: [Any](https://docs.python.org/3/library/typing.html#typing.Any "(in Python v3.14)")_,

_errors: [Literal](https://docs.python.org/3/library/typing.html#typing.Literal "(in Python v3.14)")\['raise', 'fail'\] \= 'raise'_,

_\*\*kwargs: [Any](https://docs.python.org/3/library/typing.html#typing.Any "(in Python v3.14)")_,

) → \_T[\[source\]](../../_modules/ops/charm/#ActionEvent.load_params)[¶](#ops.ActionEvent.load_params "Link to this definition")

Load the action parameters into an instance of an action class.

The raw Juju action parameters are passed to the 

<note>Content truncated. Call the fetch tool with a start_index of 5000 to get more content.</note>
```

</details>


---

<sub>⏱️ 38s</sub>

### ✅ `web_fetch`

**https://ops.readthedocs.io/en/latest/reference/ops.html#ops.Unit.set_ports**

<details>
<summary>Arguments</summary>

```json
{
  "url": "https://ops.readthedocs.io/en/latest/reference/ops.html#ops.Unit.set_ports",
  "start_index": 5000,
  "max_length": 8000
}
```

</details>

<details>
<summary>75 lines</summary>

```
Contents of https://ops.readthedocs.io/en/latest/reference/ops.html#ops.Unit.set_ports:
action class’s `__init__` method as keyword arguments, with dashes in names converted to underscores.

For dataclasses and Pydantic `BaseModel` subclasses, only fields in the Juju action parameters that have a matching field in the class are passed as arguments.

For example:

class BackupParams(pydantic.BaseModel):
    filename: str

def \_on\_do\_backup(self, event: ops.ActionEvent):
    params \= event.load\_params(BackupParams)
    \# params.filename contains the value passed by the Juju user.

Any additional positional or keyword arguments will be passed through to the action class `__init__`.

Parameters:

*   **cls** – A class that will accept the Juju parameters as keyword arguments, and raise `ValueError` if validation fails.
    
*   **errors** – what to do if the parameters are invalid. If `fail`, this will set the action to failed with an appropriate message and then immediately exit. If `raise`, `load_params` will not catch any exceptions, leaving the charm to handle errors.
    
*   **args** – positional arguments to pass through to the action class.
    
*   **kwargs** – keyword arguments to pass through to the action class.
    

Returns:

An instance of the action class that was provided in the `cls` argument with the provided parameter values.

Raises:

[**ValueError**](https://docs.python.org/3/library/exceptions.html#ValueError "(in Python v3.14)") – if `errors` is set to `raise` and instantiating the action class raises a ValueError.

log(_message: [str](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.14)")_)[\[source\]](../../_modules/ops/charm/#ActionEvent.log)[¶](#ops.ActionEvent.log "Link to this definition")

Send a message that a user will see while the action is running.

Parameters:

**message** – The message for the user.

params_: [dict](https://docs.python.org/3/library/stdtypes.html#dict "(in Python v3.14)")\[[str](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.14)"), [Any](https://docs.python.org/3/library/typing.html#typing.Any "(in Python v3.14)")\]_[¶](#ops.ActionEvent.params "Link to this definition")

The parameters passed to the action.

restore(_snapshot: [dict](https://docs.python.org/3/library/stdtypes.html#dict "(in Python v3.14)")\[[str](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.14)"), [Any](https://docs.python.org/3/library/typing.html#typing.Any "(in Python v3.14)")\]_)[\[source\]](../../_modules/ops/charm/#ActionEvent.restore)[¶](#ops.ActionEvent.restore "Link to this definition")

Used by the framework to record the action.

Not meant to be called directly by charm code.

set\_results(_results: [dict](https://docs.python.org/3/library/stdtypes.html#dict "(in Python v3.14)")\[[str](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.14)"), [Any](https://docs.python.org/3/library/typing.html#typing.Any "(in Python v3.14)")\]_)[\[source\]](../../_modules/ops/charm/#ActionEvent.set_results)[¶](#ops.ActionEvent.set_results "Link to this definition")

Report the result of the action.

Juju eventually only accepts a str:str mapping, so we will attempt to flatten any more complex data structure like so:

*   `{'a': 'b'}` becomes `'a'='b'`
    
*   `{'a': {'b': 'c'}}` becomes `'a.b'='c'`
    
*   `{'a': {'b': 'c', 'd': 'e'}}` becomes `'a.b'='c', 'a.d' = 'e'`
    
*   `{'a.b': 'c', 'a.d': 'e'}` is equivalent to the previous example
    

Note that duplicate keys are not allowed, so this is invalid:

{'a': {'b': 'c'}, 'a.b': 'c'}

Note that the resulting keys must start and end with lowercase alphanumeric, and can only contain lowercase alphanumeric, hyphens and periods.

Because results are passed to Juju using the command line, the maximum size is around 100KB. However, actions results are designed to be small: a few key-value pairs shown in the Juju CLI. If larger content is needed, store it in a file and use something like `juju scp`.

If any exceptions occur whilst the action is being handled, juju will gather any stdout/stderr data (and the return code) and inject them into the results object. Thus, the results object might contain the following keys, additionally to those specified by the charm code:

*   Stdout
    
*   Stderr
    
*   Stdout-encoding
    
*   Stderr-encoding
    
*   ReturnCode
    

Parameters:

**results** – The result of the action as a Dict

Raises:

*   [**ModelError**](#ops.ModelError "ops.ModelError") – if a reserved key is used.
    
*   [**ValueError**](https://docs.python.org/3/library/exceptions.html#ValueError "(in Python v3.14)") – if `results` has a mix of dotted/non-dotted keys that expand out to result in duplicate keys, for example: `{'a': {'b': 1}, 'a.b': 2}`. Also raised if a dict is passed with a key that fails to meet the format requirements.
    
*   [**OSError**](https://docs.python.org/3/library/exceptions.html#OSError "(in Python v3.14)") – if extremely large (>100KB) results are provided.
    

snapshot() → [dict](https://docs.python.org/3/library/stdtypes.html#dict "(in Python v3.14)")\[[str](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.14)"), [Any](https://docs.python.org/3/library/typing.html#typing.Any "(in Python v3.14)")\][\[source\]](../../_modules/ops/charm/#ActionEvent.snapshot)[¶](#ops.ActionEvent.snapshot "Link to this definition")

Used by the framework to serialize the event to disk.

Not meant to be called by charm code.

_class_ ops.ActionMeta(_name: [str](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.14)")_, _raw: [dict](https://docs.python.org/3/library/stdtypes.html#dict "(in Python v3.14)")\[[str](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.14)"), [Any](https://docs.python.org/3/library/typing.html#typing.Any "(in Python v3.14)")\] | [None](https://docs.python.org/3/library/constants.html#None "(in Python v3.14)") \= None_)[\[source\]](../../_modules/ops/charm/#ActionMeta)[¶](#ops.ActionMeta "Link to this definition")

Bases: [`object`](https://docs.python.org/3/library/functions.html#object "(in Python v3.14)")

Object containing metadata about an action’s definition.

_class_ ops.ActiveStatus(_message: [str](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.14)") \= ''_)[\[source\]](../../_modules/ops/model/#ActiveStatus)[¶](#ops.ActiveStatus "Link to this definition")

Bases: [`StatusBase`](#ops.StatusBase "ops.model.StatusBase")

The unit or application is ready and active.

Set this status when the charm is correctly offering all the services it has been asked to offer. If the unit or application is operational but some feature (like high availability) is in a degraded state, set “active” with an appropriate message.

name_: [Literal](https://docs.python.org/3/library/typing.html#typing.Literal "(in Python v3.14)")\['active', 'blocked', 'maintenance', 'waiting', 'error', 'unknown'\]_ _\= 'active'_[¶](#ops.ActiveStatus.name "Link to this definition")

_class_ ops.Application(

_name: [str](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.14)")_,

_meta: [CharmMeta](#ops.CharmMeta "ops.charm.CharmMeta")_,

_backend: \_ModelBackend_,

_cache: \_ModelCache_,

)[\[source\]](../../_modules/ops/model/#Application)[¶](#ops.Application "Link to this definition")

Bases: [`object`](https://docs.python.org/3/library/functions.html#object "(in Python v3.14)")

Represents a named application in the model.

This might be this charm’s application, or might be an application this charm is integrated with.

Don’t instantiate Application objects directly. To get the application that this unit is part of, use [`CharmBase.app`](#ops.CharmBase.app "ops.CharmBase.app"). To get an application by name, use [`Model.get_app()`](#ops.Model.get_app "ops.Model.get_app").

add\_secret(

_content: [dict](https://docs.python.org/3/library/stdtypes.html#dict "(in Python v3.14)")\[[str](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.14)"), [str](https://docs.python.org/3/li

<note>Content truncated. Call the fetch tool with a start_index of 13000 to get more content.</note>
```

</details>


---

<sub>⏱️ 39s</sub>

### ❌ `web_fetch`

**https://ops.readthedocs.io/en/latest/howto/manage-ports.html**

<details>
<summary>Arguments</summary>

```json
{
  "url": "https://ops.readthedocs.io/en/latest/howto/manage-ports.html"
}
```

</details>

```
Error: Failed to fetch https://ops.readthedocs.io/en/latest/howto/manage-ports.html - status code 404
```


---

<sub>⏱️ 45s</sub>

### ❌ `web_fetch`

**https://ops.readthedocs.io/en/latest/howto/manage-network-ports.html**

<details>
<summary>Arguments</summary>

```json
{
  "url": "https://ops.readthedocs.io/en/latest/howto/manage-network-ports.html"
}
```

</details>

```
Error: Failed to fetch https://ops.readthedocs.io/en/latest/howto/manage-network-ports.html - status code 404
```


---

<sub>⏱️ 1m 14s</sub>

### ✅ `read_agent`

**Explore agent (Explore charm port usage)**

<details>
<summary>Arguments</summary>

```json
{
  "agent_id": "explore-charm",
  "wait": true,
  "timeout": 30
}
```

</details>

```
Agent is still running after waiting 30s. agent_id: explore-charm, agent_type: explore, status: running, description: Explore charm port usage, elapsed: 55s, total_turns: 0, tool_calls_completed: 19, (timed out waiting for completion) You will be automatically notified when this agent completes — no need to poll.
```


---

<sub>⏱️ 1m 20s</sub>

### ✅ `web_fetch`

**https://ops.readthedocs.io/en/latest/howto/**

<details>
<summary>Arguments</summary>

```json
{
  "url": "https://ops.readthedocs.io/en/latest/howto/"
}
```

</details>

<details>
<summary>55 lines</summary>

```
Contents of https://ops.readthedocs.io/en/latest/howto/:
These guides walk you through writing charms using Ops.

## Managing charms[¶](#managing-charms "Link to this heading")

As you write your charm, you’ll use tools and resources from around the charming ecosystem.

*   [Manage charms](manage-charms/)

Once your charm is ready for wide production use, your next goal should be to get it publicly listed on Charmhub, so that it is visible in searches.

*   [Make your charm discoverable](make-your-charm-discoverable/)
    

## Writing charm code and tests[¶](#writing-charm-code-and-tests "Link to this heading")

Your charm is Python code that depends on Ops, with standard structures for handling events, status, and errors. As you write your charm, make sure to follow best practices.

*   [Write and structure charm code](write-and-structure-charm-code/)

Unit tests check that your charm correctly handles simulated events from Juju.

*   [Write unit tests for a charm](write-unit-tests-for-a-charm/)

Integration tests check that your charm works correctly when deployed to a real Juju model.

*   [Write integration tests for a charm](write-integration-tests-for-a-charm/)

Juju provides a variety of debugging tools, which Ops integrates with.

*   [Log from your charm](log-from-your-charm/)
*   [Debug your charm](debug-your-charm/)

## Managing machine workloads[¶](#managing-machine-workloads "Link to this heading")

Your charm is responsible for interacting with a workload.

*   [Run workloads with a machine charm](run-workloads-with-a-charm-machines/)

## Managing containers[¶](#managing-containers "Link to this heading")

In a Kubernetes charm, your charm manages the workload by defining the [Pebble](https://documentation.ubuntu.com/pebble/ "(in Pebble)") service configuration. Your charm can also use Pebble to run commands and read and write files in the workload container.

*   [Manage the workload container](manage-containers/manage-the-workload-container/)
    
*   [Manage files in the workload container](manage-containers/manage-files-in-the-workload-container/)
    

Pebble can regularly check that the workload is healthy and report back to your charm.

*   [Manage Pebble health checks](manage-containers/manage-pebble-health-checks/)
    

Custom notices enable the workload to tell your charm that something has happened.

*   [Manage Pebble custom notices](manage-containers/manage-pebble-custom-notices/)
    

Your charm can configure Pebble so that you can access metrics for services and health checks.

*   [Manage Pebble metrics](manage-containers/manage-pebble-metrics/)
    

## Managing features[¶](#managing-features "Link to this heading")

Ops features broadly map to Juju features.

*   [Manage storage](manage-storage/)
*   [Manage resources](manage-resources/)
*   [Manage actions](manage-actions/)
*   [Manage configuration](manage-configuration/)
*   [Manage relations](manage-relations/)
*   [Manage leadership changes](manage-leadership-changes/)
*   [Manage libraries](manage-libraries/)
*   [Manage interfaces](manage-interfaces/)
*   [Manage secrets](manage-secrets/)
*   [Manage stored state](manage-stored-state/)
*   [Manage opened ports](manage-opened-ports/)
*   [Manage the charm version](manage-the-charm-version/)
*   [Manage the workload version](manage-the-workload-version/)

## Tracing[¶](#tracing "Link to this heading")

Ops enables you to trace your charm code and send data to sources such as the [Canonical Observability Stack](https://documentation.ubuntu.com/observability/).

*   [Trace your charm](trace-your-charm/)

## Migration guides[¶](#migration-guides "Link to this heading")

Harness is a deprecated framework for writing unit tests. You should migrate to state-transition tests.

*   [Migrate unit tests from Harness](migrate/migrate-unit-tests-from-harness/)
    

pytest-operator and python-libjuju are deprecated. You should migrate integration tests to Jubilant.

*   [Migrate integration tests from pytest-operator](migrate/migrate-integration-tests-from-pytest-operator/)
    

Hooks-based charms use script files instead of Python code with Ops. You should migrate to Ops.

*   [Migrate from a hooks-based charm](migrate/migrate-from-a-hooks-based-charm/)
```

</details>


---

<sub>⏱️ 1m 26s</sub>

### ✅ `web_fetch`

**https://ops.readthedocs.io/en/latest/howto/manage-opened-ports/**

<details>
<summary>Arguments</summary>

```json
{
  "url": "https://ops.readthedocs.io/en/latest/howto/manage-opened-ports/",
  "max_length": 10000
}
```

</details>

<details>
<summary>44 lines</summary>

```
Contents of https://ops.readthedocs.io/en/latest/howto/manage-opened-ports/:
Juju manages the IP of each unit, so you need to instruct Juju if you want the charm to have a stable address. Typically, charms manage this by offering to integrate with an ingress charm, but you may also wish to have the charm itself open a port.

## Implement the feature[¶](#implement-the-feature "Link to this heading")

Use [`ops.Unit.set_ports`](../../reference/ops/#ops.Unit.set_ports "ops.Unit.set_ports") to to declare which ports should be open. For example, to set an open TCP port based on a configuration value, do the following in your `config-changed` observer in `src/charm.py`:

def \_on\_holistic\_handler(self, \_: ops.EventBase):
    port \= cast(int, self.config\['server-port'\])
    self.unit.set\_ports(port)

`ops` also offers [`ops.Unit.open_port`](../../reference/ops/#ops.Unit.open_port "ops.Unit.open_port") and [`ops.Unit.close_port`](../../reference/ops/#ops.Unit.close_port "ops.Unit.close_port") methods, but the declarative approach is typically simpler.

## Test the feature[¶](#test-the-feature "Link to this heading")

You’ll want to add unit and integration tests.

### Write unit tests[¶](#write-unit-tests "Link to this heading")

In your unit tests, use the [`ops.testing.State.opened_ports`](../../reference/ops-testing/#ops.testing.State.opened_ports "ops.testing.State.opened_ports") component of the input `State` to specify which ports are already open when the event is run. Ports that are not listed are assumed to be closed. After events that modify which ports are open, assert that the output `State` has the correct set of ports.

For example, in `tests/unit/test_charm.py`, this verifies that when the `config-changed` event runs, the only opened port is 8000 (for TCP):

def test\_open\_port():
    ctx \= testing.Context(MyCharm)
    state\_in \= testing.State()
    state\_out \= ctx.run(ctx.on.config\_changed(), state\_in)
    assert state\_out.opened\_ports \== {testing.TCPPort(8000)}

### Write integration tests[¶](#write-integration-tests "Link to this heading")

To verify that the correct ports are open in an integration test, deploy your charm as usual, and then try to connect to the appropriate ports.

By adding the following test to your `tests/integration/test_charm.py` file, you can verify that your charm opens a port specified in the configuration, but prohibits using port 22:

def is\_port\_open(host: str, port: int) \-> bool:
    """Check if a port is opened in a particular host."""
    try:
        with socket.create\_connection((host, port), timeout\=5):
            return True  \# If connection succeeds, the port is open
    except (ConnectionRefusedError, TimeoutError):
        return False  \# If connection fails, the port is closed

def test\_open\_ports(juju: jubilant.Juju):
    """Verify that setting the server-port in the charm's opens that port.

    Assert blocked status in case of port 22 and active status for others.
    """
    \# Get the public address of the app:
    address \= juju.status().apps\["your-app"\].units\["your-app/0"\].public\_address
    \# Validate that initial port is opened:
    assert is\_port\_open(address, 8000)

    \# Set the port to 22 and validate the app goes to blocked status with the port not opened:
    juju.config("your-app", {"server-port": "22"})
    juju.wait(jubilant.all\_blocked)
    assert not is\_port\_open(address, 22)

    \# Set the port to 6789 and validate the app goes to active status with the port opened.
    juju.config("your-app", {"server-port": "6789"})
    juju.wait(jubuilant.all\_active)
    assert is\_port\_open(address, 6789)
```

</details>


---

<sub>⏱️ 1m 30s</sub>

### 💬 Copilot

Good, I have the docs. Now let me wait for the explore agent to finish.

---

<sub>⏱️ 1m 30s</sub>

### ✅ `read_agent`

**Explore agent (Explore charm port usage)**

<details>
<summary>Arguments</summary>

```json
{
  "agent_id": "explore-charm",
  "wait": true,
  "timeout": 60
}
```

</details>

<details>
<summary>280 lines</summary>

````
Agent completed. agent_id: explore-charm, agent_type: explore, status: completed, description: Explore charm port usage, elapsed: 72s, total_turns: 0, duration: 72s

Excellent! Now let me create a comprehensive report with all the information:

## Comprehensive Port-Related Analysis

### 1. **Port API Usage Summary**

**Files using port APIs:**
- `/tmp/ops-upgrade-experiment/zinc-k8s-operator__set-ports__C2/src/charm.py` (Line 70)
- `/tmp/ops-upgrade-experiment/zinc-k8s-operator__set-ports__C2/tests/unit/test_charm.py` (Line 44)

**Key Finding:** Only `open_port()` is used. There is **NO usage of `close_port()` or `opened_ports` API** in the charm code itself (only in the test assertions).

---

### 2. **Full Content of Port-Related Files**

#### **A. `/tmp/ops-upgrade-experiment/zinc-k8s-operator__set-ports__C2/src/charm.py`**

**Line 70 - Port Opening:**
```python
70:        self.unit.open_port(protocol="tcp", port=self._zinc.port)
```

**Context (Lines 62-72):**
```python
62.     def _on_zinc_pebble_ready(self, event: ops.WorkloadEvent):
63.         """Define and start a workload using the Pebble API."""
64.         password = self._generated_password()
65.         self._container.make_dir(self._zinc.log_dir, make_parents=True, permissions=0o755)
66.         self._container.add_layer("zinc", self._zinc.pebble_layer(password), combine=True)
67.         self._container.replan()
68. 
69.         self.unit.set_workload_version(self._zinc.version)
70.         self.unit.open_port(protocol="tcp", port=self._zinc.port)
71. 
72.         self.unit.status = ops.ActiveStatus()
```

**Complete File (104 lines):**
```python
#!/usr/bin/env python3
# Copyright 2024 Jon Seager (@jnsgruk)
# See LICENSE file for licensing details.

"""Charmed Operator for Zinc; a lightweight elasticsearch alternative."""

import logging
import secrets

import ops
from charms.grafana_k8s.v0.grafana_dashboard import GrafanaDashboardProvider
from charms.loki_k8s.v0.loki_push_api import LogProxyConsumer
from charms.parca_k8s.v0.parca_scrape import ProfilingEndpointProvider
from charms.prometheus_k8s.v0.prometheus_scrape import MetricsEndpointProvider
from charms.traefik_k8s.v2.ingress import IngressPerAppRequirer

from zinc import Zinc

logger = logging.getLogger(__name__)


class ZincCharm(ops.CharmBase):
    """Charmed Operator for Zinc; a lightweight elasticsearch alternative."""

    def __init__(self, *args):
        super().__init__(*args)
        self.framework.observe(self.on.zinc_pebble_ready, self._on_zinc_pebble_ready)
        self.framework.observe(self.on.update_status, self._on_update_status)

        self._container = self.unit.get_container("zinc")
        self._zinc = Zinc()

        # Provide ability for Zinc to be scraped by Prometheus using prometheus_scrape
        self._scraping = MetricsEndpointProvider(
            self,
            relation_name="metrics-endpoint",
            jobs=[{"static_configs": [{"targets": [f"*:{self._zinc.port}"]}]}],
        )

        # Enable log forwarding for Loki and other charms that implement loki_push_api
        self._logging = LogProxyConsumer(
            self, relation_name="log-proxy", log_files=[self._zinc.log_path]
        )

        # Provide grafana dashboards over a relation interface
        self._grafana_dashboards = GrafanaDashboardProvider(
            self, relation_name="grafana-dashboard"
        )

        # Enable profiling over a relation with Parca
        self._profiling = ProfilingEndpointProvider(
            self, jobs=[{"static_configs": [{"targets": [f"*:{self._zinc.port}"]}]}]
        )

        self._ingress = IngressPerAppRequirer(
            self,
            host=f"{self.app.name}.{self.model.name}.svc.cluster.local",
            port=self._zinc.port,
            strip_prefix=True,
        )

    def _on_zinc_pebble_ready(self, event: ops.WorkloadEvent):
        """Define and start a workload using the Pebble API."""
        password = self._generated_password()
        self._container.make_dir(self._zinc.log_dir, make_parents=True, permissions=0o755)
        self._container.add_layer("zinc", self._zinc.pebble_layer(password), combine=True)
        self._container.replan()

        self.unit.set_workload_version(self._zinc.version)
        self.unit.open_port(protocol="tcp", port=self._zinc.port)

        self.unit.status = ops.ActiveStatus()

    def _on_update_status(self, _):
        """Update the status of the application."""
        if self._container.can_connect() and self._container.get_services("zinc"):
            self.unit.set_workload_version(self._zinc.version)

    def _generated_password(self) -> str:
        """Report the generated admin password; generate one if it doesn't exist."""
        # If the peer relation is not ready, just return an empty string
        relation = self.model.get_relation("zinc-peers")
        if not relation:
            return ""

        # If the secret already exists, grab its content and return it
        secret_id = relation.data[self.app].get("initial-admin-password", None)
        if secret_id:
            secret = self.model.get_secret(id=secret_id)
            return secret.peek_content().get("password")

        if self.unit.is_leader():
            content = {"password": secrets.token_urlsafe(24)}
            secret = self.app.add_secret(content)
            # Store the secret id in the peer relation for other units if required
            relation.data[self.app]["initial-admin-password"] = secret.id
            return content["password"]
        else:
            return ""


if __name__ == "__main__":  # pragma: nocover
    ops.main(ZincCharm)
```

#### **B. `/tmp/ops-upgrade-experiment/zinc-k8s-operator__set-ports__C2/src/zinc.py`**

**Port Property (Lines 56-58):**
```python
56.     @property
57.     def port(self) -> int:
58.         """Report the TCP port that Zinc is bound to."""
59.         return self._port
```

**Port Definition (Line 18):**
```python
18.     _port = 4080
```

**Complete File (84 lines):**
```python
#!/usr/bin/env python3
# Copyright 2024 Jon Seager (@jnsgruk)
# See LICENSE file for licensing details.

"""Assist with client interactions with Zinc."""

import json
import logging
import time
import urllib.request

logger = logging.getLogger(__name__)


class Zinc:
    """Represent a Zinc instance in the workload."""

    _port = 4080
    _log_path = "/var/lib/zincsearch/zinc.log"
    _log_dir = "/var/lib/zincsearch"

    def pebble_layer(self, initial_password) -> dict:
        """Return a Pebble layer for managing Zinc."""
        return {
            "services": {
                "zinc": {
                    "override": "replace",
                    "summary": "zinc",
                    # go-runner achieves the equivalent of:`bash -c '/bin/zinc | tee PATH'`, but
                    # without including bash etc. in the image.
                    "command": f"/bin/go-runner --log-file={self.log_path} --also-stdout=true --redirect-stderr=true /bin/zincsearch",
                    "startup": "enabled",
                    "environment": {
                        "ZINC_DATA_PATH": "/var/lib/zincsearch",
                        "ZINC_FIRST_ADMIN_USER": "admin",
                        "ZINC_FIRST_ADMIN_PASSWORD": initial_password,
                        "ZINC_PROMETHEUS_ENABLE": True,
                        "ZINC_TELEMETRY": False,
                        "ZINC_PROFILER": True,
                    },
                }
            },
        }

    @property
    def log_path(self) -> str:
        """Report the path that Zinc is configured to output logs."""
        return self._log_path

    @property
    def log_dir(self) -> str:
        """Report the directory that Zinc is configured to output logs."""
        return self._log_dir

    @property
    def port(self) -> int:
        """Report the TCP port that Zinc is bound to."""
        return self._port

    @property
    def version(self) -> str:
        """Reports the current Zinc version."""
        try:
            return self._request_version()
        # Catching Exception is not ideal, but we don't care much for the error here, and just
        # default to setting a blank version since there isn't much the admin can do!
        except Exception as e:
            logger.warning("unable to get version from API: %s", str(e))
            logger.debug(e, exc_info=True)
            return ""

    def _request_version(self) -> str:
        """Fetch the version from the running workload using the Zinc API."""
        retries = 0
        while True:
            try:
                res = urllib.request.urlopen(f"http://localhost:{self._port}/version")
                return json.loads(res.read().decode())["version"]
            except Exception:
                if retries == 3:
                    raise
                retries += 1
                time.sleep(3)
```

---

### 3. **Charm Events Triggering Port Operations**

**Event:** `zinc_pebble_ready`
- **Trigger:** Container workload readiness event
- **Handler:** `_on_zinc_pebble_ready()` (Line 62)
- **Port Action:** `self.unit.open_port(protocol="tcp", port=self._zinc.port)` (Line 70)
- **Port Number:** 4080 (TCP)

**Event:** `update_status`
- **Trigger:** Periodic status update event
- **Handler:** `_on_update_status()` (Line 74)
- **Port Action:** None (only updates workload version)

---

### 4. **Charm's Overall Structure**

**`src/` Contents:**
```
src/
├── charm.py                          # Main charm handler (104 lines)
├── zinc.py                           # Zinc utility class (84 lines)
├── grafana_dashboards/
│   └── zinc.json.tmpl                # Grafana dashboard template
├── loki_alert_rules/
│   └── .gitkeep
└── prometheus_alert_rules/
    ├── .gitkeep
    └── zinc_missing.rule             # Prometheus alert rule
```

**Key Components:**
- **charm.py:** Main `ZincCharm` class extending `ops.CharmBase`
  - Observes 2 events: `zinc_pebble_ready` and `update_status`
  - Manages container lifecycle and port exposure
  - Integrates with observability relations (Prometheus, Grafana, Parca)
  - Integrates with Loki for log forwarding and Traefik for ingress
  - Manages admin password via peer relation secrets

- **zinc.py:** `Zinc` utility class
  - Port constant: `_port = 4080`
  - Manages pebble layer configuration
  - Provides port property: `port(self) -> int`
  - Fetches Zinc version from API using the port number

---

### 5. **Port-Related Tests**

#### **A. Unit Tests: `/tmp/ops-upgrade-experiment/zinc-k8s-operator__set-ports__C2/tests/unit/test_charm.py`**

**Test: `test_zinc_pebble_ready()` (Lines 36-46)**
```python
def test_zinc_pebble_ready(loaded_ctx):
    ctx, container = loaded_ctx
    state = State(containers=[container])

    result = ctx.run(ctx.on.pebble_ready(container=container), state)

    assert result.get_container("zinc").layers["zinc"] == Zinc().pebble_layer("")
    assert result.get_container("zinc").service_statuses == {"zinc": ServiceStatus.ACTIVE}
    assert result.opened_ports == frozenset({TCPPort(4080)})  # ← PORT ASSERTION (Line 44)
    assert result.workload_version == "0.2.6"
    assert result.unit_status == ActiveStatus()
```

**Key Assertion (Line 44):**
```python
assert result.opened_ports == frozenset({TCPPort(4080)})
```
This verifies that when `zinc_pebble_ready` event occurs, port 4080 is opened as a TCP port.

#### **B. Unit Tests: `/tmp/ops-upgrade-experiment/zinc-k8s-operator__set-ports__C2/tests/unit/test_zinc.py`**

**Test: `test_property_port_returns_int()` (Lines 38-39)**
```python
def test_property_port_returns_int(zinc):
    assert isinstance(zinc.port, int)
```
Verifies the `port` property returns an integer.

**Additional Tests (6 tests total):**
- `test_property_pebble_layer()` - Validates pebble layer configuration
- `test_property_port_returns_str()` - Validates log path property
- `test_version_returns_str()` - Validates version property
- `test_version_returns_empty_string_when_request_fails()` - Error handling
- `test_zinc_password_*()` - Password management tests (3 tests)

---

### 6. **Summary of Port Usage Patterns**

| Aspect | Details |
|--------|---------|
| **Open Port** | ✓ Used in `_on_zinc_pebble_ready()` at line 70 |
| **Close Port** | ✗ Not used anywhere in codebase |
| **Port Number** | 4080 (TCP), defined in `zinc.py` line 18 |
| **Port Property** | `self._zinc.port` property returns int (zinc.py:56-58) |
| **Event Trigger** | `zinc_pebble_ready` workload event |
| **Test Coverage** | Yes - `test_zinc_pebble_ready()` asserts `opened_ports == frozenset({TCPPort(4080)})` |
| **Integration Points** | Prometheus scraping, Parca profiling, Traefik ingress all use port 4080 |
````

</details>


---

<sub>⏱️ 1m 31s</sub>

### ℹ️ Notification

Background agent "Explore charm port usage" (explore) completed

<details>
<summary>Detail</summary>

In the repository at /tmp/ops-upgrade-experiment/zinc-k8s-operator__set-ports__C2, find all usages of open_port, close_port, opened_ports, and any port-related logic. Show me:
1. The full content of any files that use these port APIs
2. What charm events trigger port opening/closing
3. The charm's overall structure (what src/ contains)
4. Any existing tests related to ports

Be thorough - show file paths and relevant code sections with line numbers.

</details>

---

<sub>⏱️ 1m 42s</sub>

### ✅ `view`

**view the file at /tmp/ops-upgrade-experiment/zinc-k8s-operator__set-ports__C2/src/charm.py.**

/tmp/ops-upgrade-experiment/zinc-k8s-operator__set-ports__C2/src/charm.py (lines 62-73)

<details>
<summary>12 lines</summary>

```
62.     def _on_zinc_pebble_ready(self, event: ops.WorkloadEvent):
63.         """Define and start a workload using the Pebble API."""
64.         password = self._generated_password()
65.         self._container.make_dir(self._zinc.log_dir, make_parents=True, permissions=0o755)
66.         self._container.add_layer("zinc", self._zinc.pebble_layer(password), combine=True)
67.         self._container.replan()
68. 
69.         self.unit.set_workload_version(self._zinc.version)
70.         self.unit.open_port(protocol="tcp", port=self._zinc.port)
71. 
72.         self.unit.status = ops.ActiveStatus()
73.
```

</details>


---

<sub>⏱️ 1m 48s</sub>

### ✅ `edit`

**edit the file at /tmp/ops-upgrade-experiment/zinc-k8s-operator__set-ports__C2/src/charm.py.**

/tmp/ops-upgrade-experiment/zinc-k8s-operator__set-ports__C2/src/charm.py

```
File /tmp/ops-upgrade-experiment/zinc-k8s-operator__set-ports__C2/src/charm.py updated with changes.
```


---

<sub>⏱️ 1m 54s</sub>

### 💬 Copilot

Now let's run the tests to verify:

---

<sub>⏱️ 1m 55s</sub>

### ✅ `bash`

**Run unit tests**

$ cd /tmp/ops-upgrade-experiment/zinc-k8s-operator__set-ports__C2 && uv run pytest tests/unit/ -q 2>&1

<details>
<summary>30 lines</summary>

```
Using CPython 3.12.3 interpreter at: /usr/bin/python3
Creating virtual environment at: .venv
░░░░░░░░░░░░░░░░░░░░ [0/0] Installing wheels...                                                                         ░░░░░░░░░░░░░░░░░░░░ [0/18] Installing wheels...                                                                        ░░░░░░░░░░░░░░░░░░░░ [0/18] typing-extensions==4.15.0                                                                   █░░░░░░░░░░░░░░░░░░░ [1/18] typing-extensions==4.15.0                                                                   █░░░░░░░░░░░░░░░░░░░ [1/18] cosl==1.4.0                                                                                 ██░░░░░░░░░░░░░░░░░░ [2/18] cosl==1.4.0                                                                                 ██░░░░░░░░░░░░░░░░░░ [2/18] ops==2.23.2                                                                                 ███░░░░░░░░░░░░░░░░░ [3/18] ops==2.23.2                                                                                 ███░░░░░░░░░░░░░░░░░ [3/18] referencing==0.36.2                                                                         ████░░░░░░░░░░░░░░░░ [4/18] referencing==0.36.2                                                                         ████░░░░░░░░░░░░░░░░ [4/18] pyyaml==6.0.3                                                                               █████░░░░░░░░░░░░░░░ [5/18] pyyaml==6.0.3                                                                               █████░░░░░░░░░░░░░░░ [5/18] rpds-py==0.27.1                                                                             ██████░░░░░░░░░░░░░░ [6/18] rpds-py==0.27.1                                                                             ██████░░░░░░░░░░░░░░ [6/18] tenacity==9.1.2                                                                             ███████░░░░░░░░░░░░░ [7/18] tenacity==9.1.2                                                                             ███████░░░░░░░░░░░░░ [7/18] importlib-metadata==8.7.0                                                                   ████████░░░░░░░░░░░░ [8/18] importlib-metadata==8.7.0                                                                   ████████░░░░░░░░░░░░ [8/18] pydantic-core==2.41.5                                                                       ██████████░░░░░░░░░░ [9/18] pydantic-core==2.41.5                                                                       Installed 18 packages in 3ms

======================================================== ERRORS ========================================================
______________________________________ ERROR collecting tests/unit/test_charm.py _______________________________________
ImportError while importing test module '/tmp/ops-upgrade-experiment/zinc-k8s-operator__set-ports__C2/tests/unit/test_charm.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
/usr/lib/python3.12/importlib/__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
tests/unit/test_charm.py:10: in <module>
    from charm import ZincCharm
E   ModuleNotFoundError: No module named 'charm'
_______________________________________ ERROR collecting tests/unit/test_zinc.py _______________________________________
ImportError while importing test module '/tmp/ops-upgrade-experiment/zinc-k8s-operator__set-ports__C2/tests/unit/test_zinc.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
/usr/lib/python3.12/importlib/__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
tests/unit/test_zinc.py:8: in <module>
    from zinc import Zinc
E   ModuleNotFoundError: No module named 'zinc'
=============================================== short test summary info ================================================
ERROR tests/unit/test_charm.py
ERROR tests/unit/test_zinc.py
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! Interrupted: 2 errors during collection !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
2 errors in 0.11s
<exited with exit code 2>
```

</details>


---

<sub>⏱️ 2m 2s</sub>

### ✅ `bash`

**Run unit tests with src path**

$ cd /tmp/ops-upgrade-experiment/zinc-k8s-operator__set-ports__C2 && uv run pytest tests/unit/ -q --import-mode=importlib 2>&1 || uv run python -m pytest tests/unit/ -q --pythonpath src 2>&1

<details>
<summary>22 lines</summary>

```
======================================================== ERRORS ========================================================
______________________________________ ERROR collecting tests/unit/test_charm.py _______________________________________
ImportError while importing test module '/tmp/ops-upgrade-experiment/zinc-k8s-operator__set-ports__C2/tests/unit/test_charm.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
tests/unit/test_charm.py:10: in <module>
    from charm import ZincCharm
E   ModuleNotFoundError: No module named 'charm'
_______________________________________ ERROR collecting tests/unit/test_zinc.py _______________________________________
ImportError while importing test module '/tmp/ops-upgrade-experiment/zinc-k8s-operator__set-ports__C2/tests/unit/test_zinc.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
tests/unit/test_zinc.py:8: in <module>
    from zinc import Zinc
E   ModuleNotFoundError: No module named 'zinc'
=============================================== short test summary info ================================================
ERROR tests/unit/test_charm.py
ERROR tests/unit/test_zinc.py
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! Interrupted: 2 errors during collection !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
2 errors in 0.10s
/tmp/ops-upgrade-experiment/zinc-k8s-operator__set-ports__C2/.venv/bin/python3: No module named pytest
<exited with exit code 1>
```

</details>


---

<sub>⏱️ 2m 7s</sub>

### ✅ `bash`

**Check pytest config**

$ cd /tmp/ops-upgrade-experiment/zinc-k8s-operator__set-ports__C2 && cat pyproject.toml | grep -A20 '\[tool.pytest'

<details>
<summary>20 lines</summary>

```
[tool.pytest.ini_options]
minversion = "6.0"
log_cli_level = "INFO"

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
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 2m 13s</sub>

### ✅ `bash`

**Run unit tests with PYTHONPATH**

$ cd /tmp/ops-upgrade-experiment/zinc-k8s-operator__set-ports__C2 && PYTHONPATH=src uv run pytest tests/unit/ -q 2>&1

<details>
<summary>18 lines</summary>

```
======================================================== ERRORS ========================================================
______________________________________ ERROR collecting tests/unit/test_charm.py _______________________________________
ImportError while importing test module '/tmp/ops-upgrade-experiment/zinc-k8s-operator__set-ports__C2/tests/unit/test_charm.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
/usr/lib/python3.12/importlib/__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
tests/unit/test_charm.py:10: in <module>
    from charm import ZincCharm
src/charm.py:11: in <module>
    from charms.grafana_k8s.v0.grafana_dashboard import GrafanaDashboardProvider
E   ModuleNotFoundError: No module named 'charms'
=============================================== short test summary info ================================================
ERROR tests/unit/test_charm.py
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
1 error in 0.11s
<exited with exit code 2>
```

</details>


---

<sub>⏱️ 2m 18s</sub>

### ✅ `bash`

**Run unit tests with lib path**

$ cd /tmp/ops-upgrade-experiment/zinc-k8s-operator__set-ports__C2 && ls lib/ && PYTHONPATH=src:lib uv run pytest tests/unit/ -q 2>&1

```
charms
...........                                                                                                      [100%]
11 passed in 0.16s
<exited with exit code 0>
```


---

<sub>⏱️ 2m 30s</sub>

### 💬 Copilot

All 11 tests pass. Now commit the change:

---

<sub>⏱️ 2m 30s</sub>

### ✅ `bash`

**Commit the change**

$ cd /tmp/ops-upgrade-experiment/zinc-k8s-operator__set-ports__C2 && git diff && git commit -am "refactor: use Unit.set_ports() instead of open_port()

Replace the imperative open_port() call with the declarative
set_ports() API introduced in ops 2.7.0. This approach declares
the full desired set of open ports; ops handles the diff.

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"

<details>
<summary>13 lines</summary>

```diff
diff --git a/src/charm.py b/src/charm.py
index af5ebd3..3c470e6 100755
--- a/src/charm.py
+++ b/src/charm.py
@@ -67,7 +67,7 @@ class ZincCharm(ops.CharmBase):
         self._container.replan()
 
         self.unit.set_workload_version(self._zinc.version)
-        self.unit.open_port(protocol="tcp", port=self._zinc.port)
+        self.unit.set_ports(self._zinc.port)
 
         self.unit.status = ops.ActiveStatus()
 
[detached HEAD 10dab36] refactor: use Unit.set_ports() instead of open_port()
 1 file changed, 1 insertion(+), 1 deletion(-)
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 2m 37s</sub>

### ✅ `task_complete`

**Replaced `self.unit.open_port(protocol="tcp", port=self._...**

<details>
<summary>Arguments</summary>

```json
{
  "summary": "Replaced `self.unit.open_port(protocol=\"tcp\", port=self._zinc.port)` with `self.unit.set_ports(self._zinc.port)` in `src/charm.py`.\n\n`Unit.set_ports()` is the declarative API added in ops 2.7.0 — you pass it the full desired set of open ports and ops reconciles the diff, rather than manually tracking open/close calls. Passing a plain integer defaults to TCP, so the behaviour is identical.\n\nAll 11 unit tests pass."
}
```

</details>

```
Replaced `self.unit.open_port(protocol="tcp", port=self._zinc.port)` with `self.unit.set_ports(self._zinc.port)` in `src/charm.py`.

`Unit.set_ports()` is the declarative API added in ops 2.7.0 — you pass it the full desired set of open ports and ops reconciles the diff, rather than manually tracking open/close calls. Passing a plain integer defaults to TCP, so the behaviour is identical.

All 11 unit tests pass.
```


---

<sub>⏱️ 2m 37s</sub>

### ✓ Task Complete

Replaced `self.unit.open_port(protocol="tcp", port=self._zinc.port)` with `self.unit.set_ports(self._zinc.port)` in `src/charm.py`.

`Unit.set_ports()` is the declarative API added in ops 2.7.0 — you pass it the full desired set of open ports and ops reconciles the diff, rather than manually tracking open/close calls. Passing a plain integer defaults to TCP, so the behaviour is identical.

All 11 unit tests pass.

---

<sub>Generated by [GitHub Copilot CLI](https://github.com/features/copilot/cli)</sub>
