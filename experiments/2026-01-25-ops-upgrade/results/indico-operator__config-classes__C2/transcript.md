# 🤖 Copilot CLI Session

> **Session ID:** `a85b445b-9395-4cef-b637-eaf1f098eb73`
> **Duration:** 11m 41s
> **Exported:** 3/11/2026, 4:25:09 PM

<sub>⏱️ 4s</sub>

### 👤 User

ops 2.23.0 added support for defining charm config options as Python dataclasses or Pydantic models, loaded via CharmBase.load_config(), replacing raw dictionary access to self.config. Learn how to use that feature and update this charm to make use of it.

---

<sub>⏱️ 11s</sub>

### ✅ `view`

**/tmp/ops-upgrade-experiment/indico-operator__config-classes__C2**

/tmp/ops-upgrade-experiment/indico-operator__config-classes__C2

<details>
<summary>38 lines</summary>

```
.baseline_commit
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


---

<sub>⏱️ 12s</sub>

### ✅ `bash`

**View config.yaml**

$ cat /tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/config.yaml

<details>
<summary>36 lines</summary>

```
# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

options:
  customization_debug:
    type: boolean
    description: Enable debug for custom templates
    default: false
  customization_sources_url:
    type: string
    description: URL for the git repository containing the customization files
    default: ''
  enable_roombooking:
    type: boolean
    description: Enable the room booking plugin.
    default: false
  external_plugins:
    type: string
    description: Comma separated list of external plugins to be installed, e.g. git+https://github.com/indico/indico-plugins-cern.git/#subdirectory=themes_cern. The format of each item must be supported by pip.
    default: ''
  indico_no_reply_email:
    type: string
    description: Email address used when sending emails to users to which they should not reply.
    default: 'noreply@mydomain.local'
  indico_public_support_email:
    type: string
    description: Email address that is shown to users on the “Contact” page.
    default: 'support@mydomain.local'
  indico_support_email:
    type: string
    description: Email address of the technical manager of the Indico instance.
    default: 'support-tech@mydomain.local'
  site_url:
    type: string
    description: URL through which Indico is accessed by users.
    default: ''
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 16s</sub>

### ✅ `bash`

**View main charm file**

$ cat /tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/src/charm.py

<details>
<summary>8 lines</summary>

```
Output too large to read at once (39.1 KB). Saved to: /tmp/copilot-tool-output-1773198824329-eru1vv.txt
Consider using tools like grep (for searching), head/tail (for viewing start/end), view with view_range (for specific sections), or jq (for JSON) to examine portions of the output.

Preview (first 500 chars):
#!/usr/bin/env python3

# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

"
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 16s</sub>

### ✅ `bash`

**List src directory**

$ ls /tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/src/

```
charm.py	      grafana_dashboards      s3_observer.py	smtp_observer.py
database_observer.py  prometheus_alert_rules  saml_observer.py	state.py
<exited with exit code 0>
```


---

<sub>⏱️ 20s</sub>

### ✅ `view`

**/tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/src/charm.py**

/tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/src/charm.py

```
File too large to read at once (38.7 KB). Consider using tools like grep (for searching), head/tail (for viewing start/end), view with view_range (for specific sections), or jq (for JSON) to examine portions of the file.
```


---

<sub>⏱️ 25s</sub>

### ✅ `bash`

**Find all config usages**

$ grep -n "self\.config" /tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/src/charm.py | head -60

<details>
<summary>22 lines</summary>

```
162:        site_url = typing.cast(str, self.config["site_url"])
173:        site_url = typing.cast(str, self.config["site_url"])
184:        site_url = typing.cast(str, self.config["site_url"])
193:        site_url = typing.cast(str, self.config["site_url"])
235:                typing.cast(str, self.config["external_plugins"]).split(",")
236:                if self.config["external_plugins"]
564:            "CUSTOMIZATION_DEBUG": self.config["customization_debug"],
565:            "ENABLE_ROOMBOOKING": self.config["enable_roombooking"],
570:            "INDICO_NO_REPLY_EMAIL": self.config["indico_no_reply_email"],
571:            "INDICO_PUBLIC_SUPPORT_EMAIL": self.config["indico_public_support_email"],
572:            "INDICO_SUPPORT_EMAIL": self.config["indico_support_email"],
611:                    "entityId": self.config["site_url"],
782:        if current_remote_url != self.config["customization_sources_url"]:
792:            if self.config["customization_sources_url"]:
795:                    self.config["customization_sources_url"],
802:                        typing.cast(str, self.config["customization_sources_url"]),
820:            if self.config["customization_sources_url"]:
821:                logging.debug("Pulling changes from %s", self.config["customization_sources_url"])
829:            if self.config["external_plugins"]:
830:                logging.debug("Upgrading external plugins %s", self.config["external_plugins"])
831:                plugins = typing.cast(str, self.config["external_plugins"]).split(",")
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 25s</sub>

### ✅ `bash`

**Find config usages in other files**

$ grep -n "self\.config" /tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/src/state.py /tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/src/database_observer.py /tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/src/s3_observer.py /tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/src/smtp_observer.py /tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/src/saml_observer.py 2>/dev/null

```

<exited with exit code 1>
```


---

<sub>⏱️ 41s</sub>

### ✅ `web_search`

**ops 2.23.0 charm config dataclass Pydantic CharmBase load_config Python**

<details>
<summary>Arguments</summary>

```json
{
  "query": "ops 2.23.0 charm config dataclass Pydantic CharmBase load_config Python"
}
```

</details>

````
{"type":"text","text":{"value":"With Ops 2.23.0 for Juju charms, you can define and validate your charm's configuration using Python dataclasses or Pydantic models, which integrate tightly with the CharmBase.load_config method. This approach improves both type safety and validation logic for charm configuration, enabling better developer experience and runtime safety.\n\n### How to Define and Use Typed Config with Pydantic and CharmBase\n\n1. **Define Configuration Schema**\n\n   In your `charmcraft.yaml`, under `config`, define your configuration options, like so:\n   ```yaml\n   config:\n     options:\n       name:\n         default: Wiki\n         description: The name of the Wiki\n         type: string\n       skin:\n         default: vector\n         description: The display skin for the Wiki\n         type: string\n   ```\n\n2. **Create a Pydantic Model**\n\n   In your charm Python code, model configuration using Pydantic for validation:\n   ```python\n   from pydantic import BaseModel, Field, validator\n\n   class WikiConfig(BaseModel):\n       name: str = Field('Wiki')\n       skin: str = Field('vector')\n\n       @validator('name')\n       def validate_name(cls, v):\n           if len(v) < 4:\n               raise ValueError('Name must be at least 4 characters')\n           if \" \" in v:\n               raise ValueError('Name must not contain spaces')\n           return v\n   ```\n   Pydantic provides runtime validation and IDE-aware type checking【3:4†source】.\n\n3. **Load the Configuration in Your Charm**\n\n   Inherit from `ops.CharmBase` and use `self.load_config()` to bind and validate config:\n   ```python\n   from ops.charm import CharmBase\n\n   class WikiCharm(CharmBase):\n       def __init__(self, *args):\n           super().__init__(*args)\n           self.framework.observe(self.on.config_changed, self._on_config_changed)\n           # Will block if configuration is invalid and set charm to BlockedStatus\n           self.typed_config = self.load_config(WikiConfig, errors='blocked')\n\n       def _on_config_changed(self, event):\n           config = self.typed_config\n           # Use config.name, config.skin\n   ```\n   If config is invalid, `errors='blocked'` ensures the charm status is set to blocked, while the default (`raise`) would require you to manage `ValueError` exceptions yourself【3:0†source】【3:1†source】.\n\n### Why Use Pydantic and Typed Config?\n- **Type Safety**: Errors are caught at runtime and flagged by type checking tools.\n- **Validation**: You centralize all validation logic in the schema.\n- **Readability**: Charms become easier to maintain and reason about.\n- **Modern Python**: Pydantic and dataclasses are \"Pythonic\" and well supported across tooling.\n- **Community Support**: Pydantic and the ops framework are battle-tested by the Python and Juju ecosystems【3:4†source】【3:9†source】.\n\n### Additional Notes\n- You can also use standard Python `dataclasses` for config if you don’t need Pydantic's advanced validation【3:0†source】.\n- In charms developed with the latest best-practice structure (`charmcraft init`), this approach fits naturally into the generated files and event hooks【3:7†source】【3:2†source】.\n\n### Key Reference Links\n- [Ops Framework: Manage Configuration](https://documentation.ubuntu.com/ops/latest/howto/manage-configuration/)【3:0†source】\n- [Ops API Docs](https://ops.readthedocs.io/en/2.23/_modules/ops/charm.html)【3:1†source】\n- [Pydantic Docs](https://docs.pydantic.dev/latest/)【3:4†source】\n\nIf you need an example adapted specifically for dataclasses or want to see config integration with other charm events, let me know!","annotations":[{"text":"【3:4†source】","start_index":1409,"end_index":1421,"url_citation":{"title":"Welcome to Pydantic - Pydantic Validation","url":"https://docs.pydantic.dev/latest/"}},{"text":"【3:0†source】","start_index":2260,"end_index":2272,"url_citation":{"title":"Manage configuration - Ops documentation","url":"https://documentation.ubuntu.com/ops/latest/howto/manage-configuration/"}},{"text":"【3:1†source】","start_index":2272,"end_index":2284,"url_citation":{"title":"ops.charm - Ops 2.23 documentation","url":"https://ops.readthedocs.io/en/2.23/_modules/ops/charm.html"}},{"text":"【3:4†source】","start_index":2752,"end_index":2764,"url_citation":{"title":"Welcome to Pydantic - Pydantic Validation","url":"https://docs.pydantic.dev/latest/"}},{"text":"【3:9†source】","start_index":2764,"end_index":2776,"url_citation":{"title":"Ops documentation ¶","url":"https://documentation.ubuntu.com/ops/latest/"}},{"text":"【3:0†source】","start_index":2908,"end_index":2920,"url_citation":{"title":"Manage configuration - Ops documentation","url":"https://documentation.ubuntu.com/ops/latest/howto/manage-configuration/"}},{"text":"【3:7†source】","start_index":3074,"end_index":3086,"url_citation":{"title":"How to write and structure charm code - Ops documentation","url":"https://documentation.ubuntu.com/ops/latest/howto/write-and-structure-charm-code/"}},{"text":"【3:2†source】","start_index":3086,"end_index":3098,"url_citation":{"title":"Pure Python framework for writing Juju charms. - GitHub","url":"https://github.com/canonical/operator"}},{"text":"【3:0†source】","start_index":3237,"end_index":3249,"url_citation":{"title":"Manage configuration - Ops documentation","url":"https://documentation.ubuntu.com/ops/latest/howto/manage-configuration/"}},{"text":"【3:1†source】","start_index":3326,"end_index":3338,"url_citation":{"title":"ops.charm - Ops 2.23 documentation","url":"https://ops.readthedocs.io/en/2.23/_modules/ops/charm.html"}},{"text":"【3:4†source】","start_index":3391,"end_index":3403,"url_citation":{"title":"Welcome to Pydantic - Pydantic Validation","url":"https://docs.pydantic.dev/latest/"}}]},"bing_searches":[{"text":"ops 2.23.0 charm config dataclass Pydantic CharmBase load_config Python","url":"https://www.bing.com/search?q=ops+2.23.0+charm+config+dataclass+Pydantic+CharmBase+load_config+Python"}],"annotations":null}
````


---

<sub>⏱️ 31s</sub>

### ✅ `view`

**/tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/src/state.py**

/tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/src/state.py

<details>
<summary>240 lines</summary>

```
1. # Copyright 2025 Canonical Ltd.
2. # See LICENSE file for licensing details.
3. 
4. """Indico states."""
5. 
6. import dataclasses
7. import logging
8. import os
9. from typing import Dict, List, Optional, Tuple
10. 
11. import ops
12. from charms.saml_integrator.v0.saml import SamlRelationData
13. from charms.smtp_integrator.v0.smtp import SmtpRelationData, TransportSecurity
14. 
15. # pylint: disable=no-name-in-module
16. from pydantic import AnyHttpUrl, BaseModel, Field, HttpUrl, ValidationError
17. 
18. logger = logging.getLogger(__name__)
19. 
20. 
21. class CharmStateBaseError(Exception):
22.     """Represents an error with charm state."""
23. 
24. 
25. class CharmConfigInvalidError(CharmStateBaseError):
26.     """Exception raised when a charm configuration is found to be invalid.
27. 
28.     Attributes:
29.         msg: Explanation of the error.
30.     """
31. 
32.     def __init__(self, msg: str):
33.         """Initialize a new instance of the CharmConfigInvalidError exception.
34. 
35.         Args:
36.             msg: Explanation of the error.
37.         """
38.         self.msg = msg
39. 
40. 
41. class ProxyConfig(BaseModel):  # pylint: disable=too-few-public-methods
42.     """Configuration for accessing Indico through proxy.
43. 
44.     Attributes:
45.         http_proxy: The http proxy URL.
46.         https_proxy: The https proxy URL.
47.         no_proxy: Comma separated list of hostnames to bypass proxy.
48.     """
49. 
50.     http_proxy: Optional[HttpUrl]
51.     https_proxy: Optional[HttpUrl]
52.     no_proxy: Optional[str]
53. 
54.     @classmethod
55.     def from_env(cls) -> Optional["ProxyConfig"]:
56.         """Instantiate ProxyConfig from juju charm environment.
57. 
58.         Returns:
59.             ProxyConfig if proxy configuration is provided, None otherwise.
60.         """
61.         http_proxy = os.environ.get("JUJU_CHARM_HTTP_PROXY")
62.         https_proxy = os.environ.get("JUJU_CHARM_HTTPS_PROXY")
63.         no_proxy = os.environ.get("JUJU_CHARM_NO_PROXY")
64.         if not http_proxy and not https_proxy:
65.             return None
66.         # Mypy doesn't understand str is supposed to be converted to HttpUrl by Pydantic.
67.         return cls(
68.             http_proxy=http_proxy, https_proxy=https_proxy, no_proxy=no_proxy  # type: ignore
69.         )
70. 
71. 
72. class S3Config(BaseModel):  # pylint: disable=too-few-public-methods
73.     """S3 configuration.
74. 
75.     Attributes:
76.         bucket: the S3 bucket.
77.         host: S3 host.
78.         access_key: S3 access key.
79.         secret_key: S3 secret key.
80.     """
81. 
82.     bucket: str
83.     host: Optional[str]
84.     access_key: str
85.     secret_key: str
86. 
87.     def get_connection_string(self) -> str:
88.         """Retrieve a connection string for this instance.
89. 
90.         Returns: the connection string for this instance.
91.         """
92.         connection_string = (
93.             f"s3:bucket={self.bucket},access_key={self.access_key},"
94.             f"secret_key={self.secret_key},proxy=true"
95.         )
96.         if self.host:
97.             connection_string = f"{connection_string},host={self.host}"
98.         return connection_string
99. 
100. 
101. class SamlEndpoint(BaseModel):  # pylint: disable=too-few-public-methods
102.     """SAML configuration.
103. 
104.     Attributes:
105.         name: Endpoint name.
106.         url: Endpoint URL.
107.         binding: Endpoint binding.
108.         response_url: URL to address the response to.
109.     """
110. 
111.     name: str = Field(..., min_length=1)
112.     url: AnyHttpUrl
113.     binding: str = Field(..., min_length=1)
114.     response_url: Optional[AnyHttpUrl]
115. 
116. 
117. class SamlConfig(BaseModel):  # pylint: disable=too-few-public-methods
118.     """SAML configuration.
119. 
120.     Attributes:
121.         entity_id: SAML entity ID.
122.         metadata_url: Metadata URL.
123.         certificates: List of x509 certificates.
124.         endpoints: List of endpoints.
125.     """
126. 
127.     entity_id: str = Field(..., min_length=1)
128.     metadata_url: AnyHttpUrl
129.     certificates: Tuple[str, ...]
130.     endpoints: Tuple[SamlEndpoint, ...]
131. 
132. 
133. class SmtpConfig(BaseModel):  # pylint: disable=too-few-public-methods
134.     """SMTP configuration.
135. 
136.     Attributes:
137.         login: SMTP user.
138.         password: SMTP passwaord.
139.         port: SMTP port.
140.         host: SMTP host.
141.         use_tls: whether TLS is enabled.
142.     """
143. 
144.     login: Optional[str]
145.     password: Optional[str]
146.     port: int = Field(None, ge=1, le=65536)
147.     host: str = Field(..., min_length=1)
148.     use_tls: bool
149. 
150. 
151. @dataclasses.dataclass()
152. class State:  # pylint: disable=too-few-public-methods
153.     """The Indico operator charm state.
154. 
155.     Attributes:
156.         proxy_config: Proxy configuration.
157.         saml_config: SAML configuration.
158.         smtp_config: SMTP configuration.
159.         s3_config: S3 configuration.
160.     """
161. 
162.     proxy_config: Optional[ProxyConfig]
163.     saml_config: Optional[SamlConfig]
164.     smtp_config: Optional[SmtpConfig]
165.     s3_config: Optional[S3Config]
166. 
167.     # pylint: disable=unused-argument
168.     @classmethod
169.     def from_charm(
170.         cls,
171.         charm: ops.CharmBase,
172.         s3_relation_data: Optional[Dict[str, str]] = None,
173.         saml_relation_data: Optional[SamlRelationData] = None,
174.         smtp_relation_data: Optional[SmtpRelationData] = None,
175.     ) -> "State":
176.         """Initialize the state from charm.
177. 
178.         Args:
179.             charm: The charm root IndicoOperatorCharm.
180.             s3_relation_data: S3 relation data.
181.             saml_relation_data: SAML relation data.
182.             smtp_relation_data: SMTP relation data.
183. 
184.         Returns:
185.             Current state of Indico.
186. 
187.         Raises:
188.             CharmConfigInvalidError: if invalid state values were encountered.
189.         """
190.         try:
191.             saml_config = None
192.             if saml_relation_data:
193.                 endpoints: List[SamlEndpoint] = []
194.                 for endpoint in saml_relation_data.endpoints:
195.                     endpoints.append(
196.                         SamlEndpoint(
197.                             name=endpoint.name,
198.                             url=endpoint.url,
199.                             binding=endpoint.binding,
200.                             response_url=endpoint.response_url,
201.                         )
202.                     )
203.                 saml_config = SamlConfig(
204.                     entity_id=saml_relation_data.entity_id,
205.                     metadata_url=saml_relation_data.metadata_url,
206.                     certificates=saml_relation_data.certificates,
207.                     endpoints=tuple(endpoints),
208.                 )
209.             proxy_config = ProxyConfig.from_env()
210.             smtp_config = (
211.                 SmtpConfig(
212.                     host=smtp_relation_data.host,
213.                     port=smtp_relation_data.port,
214.                     login=smtp_relation_data.user,
215.                     password=smtp_relation_data.password,
216.                     use_tls=smtp_relation_data.transport_security is not TransportSecurity.NONE,
217.                 )
218.                 if smtp_relation_data
219.                 else None
220.             )
221.             s3_config = (
222.                 S3Config(
223.                     bucket=s3_relation_data["bucket"],
224.                     host=s3_relation_data["endpoint"],
225.                     access_key=s3_relation_data["access-key"],
226.                     secret_key=s3_relation_data["secret-key"],
227.                 )
228.                 if s3_relation_data and "access-key" in s3_relation_data
229.                 else None
230.             )
231.         except ValidationError as exc:
232.             logger.error("Invalid juju model proxy configuration, %s", exc)
233.             raise CharmConfigInvalidError("Invalid model proxy configuration.") from exc
234.         return cls(
235.             proxy_config=proxy_config,
236.             smtp_config=smtp_config,
237.             saml_config=saml_config,
238.             s3_config=s3_config,
239.         )
240.
```

</details>


---

<sub>⏱️ 48s</sub>

### ✅ `web_fetch`

**https://documentation.ubuntu.com/ops/latest/howto/manage-configuration/**

<details>
<summary>Arguments</summary>

```json
{
  "url": "https://documentation.ubuntu.com/ops/latest/howto/manage-configuration/",
  "max_length": 10000
}
```

</details>

<details>
<summary>56 lines</summary>

```
Contents of https://documentation.ubuntu.com/ops/latest/howto/manage-configuration/:
## Implement the feature[¶](#implement-the-feature "Link to this heading")

### Define a configuration option[¶](#define-a-configuration-option "Link to this heading")

In the `charmcraft.yaml` file of the charm, under `config.options`, add a configuration definition, including a name, a description, the type, and the default value.

Best practice

Don’t duplicate model-level configuration options that are controlled by [juju model-config](https://documentation.ubuntu.com/juju/3.6/reference/juju-cli/list-of-juju-cli-commands/model-config/#command-juju-model-config "(in Juju v3.6)").

The example below shows how to define two configuration options, one called `name` of type `string` and default value `Wiki`, and one called `skin` with type `string` and default value `vector`:

config:
  options:
    name:
      default: Wiki
      description: The name, or Title of the Wiki
      type: string
    skin:
      default: vector
      description: skin for the Wiki
      type: string

In the `src/charm.py` file of the charm, add a class that mirrors the configuration from `charmcraft.yaml`. This lets your static type checker and IDE know what Python type the options should be, and provides a place to do additional validation. Using the example from above:

class WikiConfig(pydantic.BaseModel):
    name: str \= pydantic.Field('Wiki')
    skin: str \= pydantic.Field('vector')

    @pydantic.validator('name')
    def validate\_name(cls, value):
        if len(value) < 4:
            raise ValueError('Name must be at least 4 characters long')
        if " " in value:
            raise ValueError('Name must not contain spaces')
        return value

### Observe the `config-changed` event and define the event handler[¶](#observe-the-config-changed-event-and-define-the-event-handler "Link to this heading")

In the `src/charm.py` file of the charm project, in the `__init__` function of the charm, set up an observer for the config changed event and pair that with an event handler:

self.framework.observe(self.on.config\_changed, self.\_on\_config\_changed)

Also in the `__init__` function, load the config into the config class that you defined. Pass `errors='blocked'` to have the charm exit after setting a blocked status if the configuration doesn’t validate against the class you defined. The default is `errors='raise'`, which means that the charm is responsible for catching any `ValueError` raised.

self.typed\_config \= self.load\_config(WikiConfig, errors\='blocked')

Then, in the body of the charm definition, define the event handler.

def \_on\_config\_changed(self, event: ops.ConfigChangedEvent):
    name \= self.typed\_config.name
    existing\_name \= self.get\_wiki\_name()
    if name \== existing\_name:
        \# Nothing to do.
        return
    logger.info('Changing wiki name to %s', name)
    self.set\_wiki\_name(name)

Caution

*   Multiple configuration values can be changed at one time through Juju, resulting in only one `config_changed` event. Thus, your charm code must be able to process more than one config value changing at a time.
    
*   If `juju config` is run with values the same as the current configuration, the `config_changed` event will not run. Therefore, if you have a single config value, there is no point in tracking its previous value – the event will only be triggered if the value changes.
    
*   Configuration cannot be changed from within the charm code. Charms, by design, aren’t able to mutate their own configuration by themselves (e.g., in order to ignore an admin-provided configuration), or to configure other applications. In Ops, one typically interacts with config via a read-only facade.
    

### Write unit tests[¶](#write-unit-tests "Link to this heading")

To verify that the `config-changed` event validates the port, pass the new config to the `State`, and, after running the event, check the unit status. For example, in your `tests/unit/test_charm.py` file, add the following test function:

from ops import testing

def test\_short\_wiki\_name():
    ctx \= testing.Context(MyCharm)

    state\_out \= ctx.run(ctx.on.config\_changed(), testing.State(config\={'name': 'ww'}))

    assert isinstance(state\_out.unit\_status, testing.BlockedStatus)

### Manually test[¶](#manually-test "Link to this heading")

To verify that the configuration option works as intended, pack your charm, update it in the Juju model, and run `juju config` followed by the name of the application deployed by your charm and then your newly defined configuration option key set to some value. For example, given the `name` key defined above, you could try:

juju config <name of application deployed by your charm> name=charming-wiki
```

</details>


---

<sub>⏱️ 47s</sub>

### ✅ `view`

**/tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/src/charm.py**

/tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/src/charm.py (lines 1-100)

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


---

<sub>⏱️ 52s</sub>

### ✅ `view`

**/tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/src/charm.py**

/tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/src/charm.py (lines 100-250)

<details>
<summary>151 lines</summary>

```
100.         self.redis_cache = RedisRequires(self, "redis-cache")
101.         self.framework.observe(
102.             self.redis_cache.charm.on.redis_relation_updated, self._on_config_changed
103.         )
104.         self.framework.observe(
105.             self.on["indico-peers"].relation_departed, self._on_peer_relation_departed
106.         )
107.         self._require_nginx_route()
108. 
109.         self._metrics_endpoint = MetricsEndpointProvider(
110.             self,
111.             jobs=[
112.                 {
113.                     "static_configs": [
114.                         {
115.                             "targets": [
116.                                 f"*:{NGINX_PROMEXP_PORT}",
117.                                 f"*:{STATSD_PROMEXP_PORT}",
118.                                 f"*:{CELERY_PROMEXP_PORT}",
119.                             ]
120.                         }
121.                     ]
122.                 }
123.             ],
124.         )
125.         self._grafana_dashboards = GrafanaDashboardProvider(self)
126.         # port 9080 conflicts with the nginx exporter
127.         charms.loki_k8s.v0.loki_push_api.HTTP_LISTEN_PORT = 9090
128.         self._logging = LogProxyConsumer(
129.             self,
130.             relation_name="logging",
131.             log_files="/srv/indico/log/*",
132.             container_name="indico",
133.         )
134. 
135.     def _require_nginx_route(self) -> None:
136.         """Require nginx ingress."""
137.         require_nginx_route(
138.             charm=self,
139.             service_hostname=self._get_external_hostname(),
140.             service_name=self.app.name,
141.             service_port=8080,
142.         )
143. 
144.     def _are_pebble_instances_ready(self) -> bool:
145.         """Check if all pebble instances are up and containers available.
146. 
147.         Returns:
148.             If the containers are up and available.
149.         """
150.         return all(
151.             self.unit.get_container(container_name).can_connect()
152.             for container_name in self.model.unit.containers
153.         )
154. 
155.     def _is_configuration_valid(self) -> Tuple[bool, str]:
156.         """Validate charm configuration.
157. 
158.         Returns:
159.             Tuple containing as first element whether the configuration is valid.
160.             and a string with the error, if any, as second element.
161.         """
162.         site_url = typing.cast(str, self.config["site_url"])
163.         if site_url and not urlparse(site_url).hostname:
164.             return False, "Configuration option site_url is not valid"
165.         return True, ""
166. 
167.     def _get_external_hostname(self) -> str:
168.         """Extract and return hostname from site_url or default to [application name].local.
169. 
170.         Returns:
171.             The site URL defined as part of the site_url configuration or a default value.
172.         """
173.         site_url = typing.cast(str, self.config["site_url"])
174.         if not site_url or not (hostname := urlparse(site_url).hostname):
175.             return f"{self.app.name}.local"
176.         return hostname
177. 
178.     def _get_external_scheme(self) -> str:
179.         """Extract and return schema from site_url.
180. 
181.         Returns:
182.             The HTTP schema.
183.         """
184.         site_url = typing.cast(str, self.config["site_url"])
185.         return urlparse(site_url).scheme if site_url else "http"
186. 
187.     def _get_external_port(self) -> Optional[int]:
188.         """Extract and return port from site_url.
189. 
190.         Returns:
191.             The port number.
192.         """
193.         site_url = typing.cast(str, self.config["site_url"])
194.         return urlparse(site_url).port
195. 
196.     def _are_relations_ready(self, _) -> bool:
197.         """Check if the needed relations are established.
198. 
199.         Returns:
200.             If the needed relations have been established.
201.         """
202.         if self.redis_broker.relation_data is None:
203.             self.unit.status = WaitingStatus("Waiting for redis-broker availability")
204.             return False
205.         if self.redis_cache.relation_data is None:
206.             self.unit.status = WaitingStatus("Waiting for redis-cache availability")
207.             return False
208.         if self.database.uri is None:
209.             self.unit.status = WaitingStatus("Waiting for database availability")
210.             return False
211.         return True
212. 
213.     def _on_pebble_ready(self, event: PebbleReadyEvent) -> None:
214.         """Handle the on pebble ready event for the containers.
215. 
216.         Args:
217.             event: Event triggering the pebble ready handler.
218.         """
219.         if not self._are_relations_ready(event) or not event.workload.can_connect():
220.             event.defer()
221.             return
222.         self._config_pebble(event.workload)
223. 
224.     def _config_pebble(self, container: Container) -> None:
225.         """Apply pebble configurations to a container.
226. 
227.         Args:
228.             container: Container to be configured by Pebble.
229.         """
230.         self.unit.status = MaintenanceStatus(f"Adding {container.name} layer to pebble")
231.         if container.name == "indico":
232.             # Plugins need to be installed before adding the layer so that
233.             # they are included in the corresponding env vars
234.             plugins = (
235.                 typing.cast(str, self.config["external_plugins"]).split(",")
236.                 if self.config["external_plugins"]
237.                 else []
238.             )
239.             self._install_plugins(container, plugins)
240.             container.add_layer(container.name, self._get_logrotate_config(), combine=True)
241.             indico_config = self._get_indico_pebble_config(container)
242.             container.add_layer(container.name, indico_config, combine=True)
243.             peer_relation = self.model.get_relation("indico-peers")
244.             if (
245.                 not peer_relation
246.                 or peer_relation.data[self.app].get("celery-unit") == self.unit.name
247.             ):
248.                 celery_config = self._get_celery_pebble_config(container)
249.                 container.add_layer("celery", celery_config, combine=True)
250.                 celery_exporter_config = self._get_celery_prometheus_exporter_pebble_config(
```

</details>


---

<sub>⏱️ 56s</sub>

### ✅ `view`

**/tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/src/charm.py**

/tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/src/charm.py (lines 540-650)

<details>
<summary>111 lines</summary>

```
540.         assert peer_relation is not None  # nosec
541.         if not self._has_secrets():
542.             secret_value = peer_relation.data[self.app].get("secret-key")
543.         else:
544.             secret_id = peer_relation.data[self.app].get("secret-id")
545.             secret = self.model.get_secret(id=secret_id)
546.             secret_value = secret.get_content().get("secret-key")
547.         return secret_value
548. 
549.     def _get_indico_env_config(self, container: Container) -> Dict:
550.         """Return an envConfig with some core configuration.
551. 
552.         Args:
553.             container: Container for which the configuration will be retrieved.
554. 
555.         Returns:
556.             Dictionary with the environment variables for the container.
557.         """
558.         available_plugins = self._get_installed_plugins(container)
559. 
560.         env_config = {
561.             "ATTACHMENT_STORAGE": "default",
562.             "CELERY_BROKER": self._get_redis_url("redis-broker"),
563.             "CE_ACCEPT_CONTENT": "json,pickle",
564.             "CUSTOMIZATION_DEBUG": self.config["customization_debug"],
565.             "ENABLE_ROOMBOOKING": self.config["enable_roombooking"],
566.             "INDICO_AUTH_PROVIDERS": str({}),
567.             "INDICO_DB_URI": self.database.uri,
568.             "INDICO_EXTRA_PLUGINS": ",".join(available_plugins),
569.             "INDICO_IDENTITY_PROVIDERS": str({}),
570.             "INDICO_NO_REPLY_EMAIL": self.config["indico_no_reply_email"],
571.             "INDICO_PUBLIC_SUPPORT_EMAIL": self.config["indico_public_support_email"],
572.             "INDICO_SUPPORT_EMAIL": self.config["indico_support_email"],
573.             "LANG": "C.UTF-8",
574.             "LC_ALL": "C.UTF-8",
575.             "LC_LANG": "C.UTF-8",
576.             "REDIS_CACHE_URL": self._get_redis_url("redis-cache"),
577.             "SECRET_KEY": self._get_indico_secret_key_from_relation(),
578.             "SERVICE_HOSTNAME": self._get_external_hostname(),
579.             "SERVICE_PORT": self._get_external_port(),
580.             "SERVICE_SCHEME": self._get_external_scheme(),
581.             "STORAGE_DICT": {
582.                 "default": "fs:/srv/indico/archive",
583.             },
584.         }
585. 
586.         if self.state.smtp_config:
587.             env_config["SMTP_LOGIN"] = self.state.smtp_config.login
588.             env_config["SMTP_PASSWORD"] = self.state.smtp_config.password
589.             env_config["SMTP_PORT"] = self.state.smtp_config.port
590.             env_config["SMTP_SERVER"] = self.state.smtp_config.host
591.             env_config["SMTP_USE_TLS"] = self.state.smtp_config.use_tls
592. 
593.         # Required for monitoring Celery
594.         celery_config = {"worker_send_task_events": True, "task_send_sent_event": True}
595.         env_config["CELERY_CONFIG"] = str(celery_config)
596. 
597.         # Piwik settings can't be configured using the config file for the time being:
598.         # https://github.com/indico/indico-plugins/issues/182
599.         # S3 available config options:
600.         # https://github.com/indico/indico-plugins/blob/master/storage_s3/README.md#available-config-options
601.         if self.state.s3_config:
602.             env_config["STORAGE_DICT"].update({"s3": self.state.s3_config.get_connection_string()})
603.             env_config["ATTACHMENT_STORAGE"] = "s3"
604.         env_config["STORAGE_DICT"] = str(env_config["STORAGE_DICT"])
605. 
606.         # SAML configuration reference https://github.com/onelogin/python3-saml
607.         if self.state.saml_config:
608.             saml_config: Dict[str, Any] = {
609.                 "strict": True,
610.                 "sp": {
611.                     "entityId": self.config["site_url"],
612.                 },
613.                 "idp": {
614.                     "entityId": self.state.saml_config.entity_id,
615.                     "x509cert": self.state.saml_config.certificates[0],
616.                 },
617.             }
618.             for endpoint in self.state.saml_config.endpoints:
619.                 # First letter needs to be lowercase
620.                 endpoint_name = endpoint.name[:1].lower() + endpoint.name[1:]
621.                 saml_config["idp"][endpoint_name] = {
622.                     "url": str(endpoint.url),
623.                     "binding": endpoint.binding,
624.                 }
625.                 if endpoint.response_url:
626.                     saml_config["idp"][endpoint_name]["response_url"] = str(endpoint.response_url)
627.             auth_providers = {"ubuntu": {"type": "saml", "saml_config": saml_config}}
628.             env_config["INDICO_AUTH_PROVIDERS"] = str(auth_providers)
629.             identity_providers = {
630.                 "ubuntu": {
631.                     "type": (
632.                         "saml_groups" if SAML_GROUPS_PLUGIN_NAME in available_plugins else "saml"
633.                     ),
634.                     "trusted_email": True,
635.                     "mapping": {
636.                         "user_name": "username",
637.                         "first_name": "fullname",
638.                         "last_name": "",
639.                         "email": "email",
640.                     },
641.                     "identifier_field": "openid",
642.                 }
643.             }
644.             env_config["INDICO_IDENTITY_PROVIDERS"] = str(identity_providers)
645.             env_config = {
646.                 **env_config,
647.                 **self._get_http_proxy_configuration(self.state.proxy_config),
648.             }
649.         return env_config
650.
```

</details>


---

<sub>⏱️ 56s</sub>

### ✅ `view`

**/tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/src/charm.py**

/tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/src/charm.py (lines 770-850)

<details>
<summary>81 lines</summary>

```
770.             user="indico",
771.             environment=self._get_http_proxy_configuration(self.state.proxy_config),
772.         )
773.         process.wait_output()
774. 
775.     def _download_customization_changes(self, container: Container) -> None:
776.         """Clone the remote repository with the customization changes.
777. 
778.         Args:
779.             container: Container in which the download will be performed.
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
846.         """Handle leader-elected event."""
847.         peer_relation = self.model.get_relation("indico-peers")
848.         secret_value = repr(os.urandom(32))
849.         if (
850.             peer_relation
```

</details>


---

<sub>⏱️ 1m 3s</sub>

### ✅ `bash`

**Check ops version requirement**

$ grep -i "ops" /tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/requirements.txt /tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/pyproject.toml 2>/dev/null | head -20

```
/tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/requirements.txt:ops>=2.0.0,<3.0.0
<exited with exit code 0>
```


---

<sub>⏱️ 1m 3s</sub>

### ✅ `bash`

**Check if load_config already used**

$ grep -n "load_config\|typed_config\|CharmConfig" /tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/src/charm.py

```
35:from state import CharmConfigInvalidError, ProxyConfig, State
83:        except CharmConfigInvalidError as exc:
<exited with exit code 0>
```


---

<sub>⏱️ 1m 8s</sub>

### ✅ `bash`

**Check installed ops version**

$ pip show ops 2>/dev/null | grep Version

```
Version: 2.23.2
<exited with exit code 0>
```


---

<sub>⏱️ 1m 8s</sub>

### ✅ `bash`

**Check charmcraft.yaml for ops**

$ grep -n "ops" /tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/charmcraft.yaml | head -20

```

<exited with exit code 0>
```


---

<sub>⏱️ 1m 12s</sub>

### ✅ `bash`

**Check load_config API**

$ python3 -c "import ops; help(ops.CharmBase.load_config)" 2>&1 | head -40

<details>
<summary>32 lines</summary>

```
Help on function load_config in module ops.charm:

load_config(self, cls: 'type[_T]', *args: 'Any', errors: "Literal['raise', 'blocked']" = 'raise', **kwargs: 'Any') -> '_T'
    Load the config into an instance of a config class.

    The raw Juju config is passed to the config class's ``__init__``, as
    keyword arguments, with the following changes:

    * ``secret`` type options have a :class:`model.Secret` value rather
      than the secret ID. Note that the secret object is not validated by
      Juju at this time, so may raise :class:`SecretNotFoundError` when it
      is used later (if the secret does not exist or the unit does not have
      permission to access it).
    * dashes in names are converted to underscores.

    For dataclasses and Pydantic ``BaseModel`` subclasses, only fields in
    the Juju config that have a matching field in the class are passed as
    arguments. Pydantic fields that have an ``alias``, or dataclasses that
    have a ``metadata{'alias'=}``, will have the alias applied when loading.

    For example::

        class Config(pydantic.BaseModel):
            # This field is called 'class' in the Juju config options.
            workload_class: str = pydantic.Field(alias='class')

        def _on_config_changed(self, event: ops.ConfigChangedEvent):
            data = self.load_config(Config, errors='blocked')
            # `data.workload_class` has the value of the Juju option `class`

    Any additional positional or keyword arguments to this method will be
    passed through to the config class ``__init__``.

    Args:
        cls: A class that will accept the Juju options as keyword arguments,
            and raise ``ValueError`` if validation fails.
        errors: what to do if the config is invalid. If ``blocked``, this
            will set the unit status to blocked with an appropriate message
            and then exit successfully (this informs Juju that
            the event was handled and it will not be retried).
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 1m 18s</sub>

### 💬 Copilot

Now I have a clear picture. Let me look at the tests and the full charm to understand what changes are needed.

---

<sub>⏱️ 1m 19s</sub>

### ✅ `bash`

**List test directories**

$ ls /tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/tests/

```
conftest.py  integration  unit	unit_harness  zap
<exited with exit code 0>
```


---

<sub>⏱️ 1m 18s</sub>

### ✅ `view`

**/tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/src/charm.py**

/tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/src/charm.py (lines 250-320)

<details>
<summary>71 lines</summary>

```
250.                 celery_exporter_config = self._get_celery_prometheus_exporter_pebble_config(
251.                     container
252.                 )
253.                 container.add_layer("celery-exporter", celery_exporter_config, combine=True)
254.             statsd_config = self._get_statsd_prometheus_exporter_pebble_config(container)
255.             container.add_layer("statsd", statsd_config, combine=True)
256.             self._download_customization_changes(container)
257.         if container.name == "indico-nginx":
258.             nginx_config = self._get_nginx_pebble_config(container)
259.             container.add_layer(container.name, nginx_config, combine=True)
260.             nginx_exporter_config = self._get_nginx_prometheus_exporter_pebble_config(container)
261.             container.add_layer("nginx", nginx_exporter_config, combine=True)
262.         self.unit.status = MaintenanceStatus(f"Starting {container.name} container")
263.         container.pebble.replan_services()
264.         if self._are_pebble_instances_ready():
265.             self.unit.set_workload_version(self._get_indico_version())
266.             self.unit.status = ActiveStatus()
267.         else:
268.             self.unit.status = WaitingStatus("Waiting for pebble")
269. 
270.     def _get_logrotate_config(self) -> ops.pebble.LayerDict:
271.         """Generate logrotate pebble layer.
272. 
273.         Returns:
274.             The logrotate pebble layer configuration.
275.         """
276.         layer = {
277.             "summary": "Logrotate service",
278.             "description": "Logrotate service",
279.             "services": {
280.                 "logrotate": {
281.                     "override": "replace",
282.                     "command": 'bash -c "while :; '
283.                     "do sleep 3600; logrotate /srv/indico/logrotate.conf; "
284.                     'done"',
285.                     "startup": "enabled",
286.                 },
287.             },
288.         }
289.         return typing.cast(ops.pebble.LayerDict, layer)
290. 
291.     def _get_indico_pebble_config(self, container: Container) -> ops.pebble.LayerDict:
292.         """Generate pebble config for the indico container.
293. 
294.         Args:
295.             container: Indico container that has the target configuration.
296. 
297.         Returns:
298.             The pebble configuration for the container.
299.         """
300.         indico_env_config = self._get_indico_env_config(container)
301.         indico_env_config["INDICO_LOGGING_CONFIG_FILE"] = "indico.logging.yaml"
302.         layer = {
303.             "summary": "Indico layer",
304.             "description": "Indico layer",
305.             "services": {
306.                 "indico": {
307.                     "override": "replace",
308.                     "summary": "Indico service",
309.                     "command": "/srv/indico/start-indico.sh",
310.                     "startup": "enabled",
311.                     "user": "indico",
312.                     "environment": indico_env_config,
313.                 },
314.             },
315.             "checks": {
316.                 "indico-ready": {
317.                     "override": "replace",
318.                     "level": "ready",
319.                     "tcp": {"port": 8081},
320.                 },
```

</details>


---

<sub>⏱️ 1m 25s</sub>

### ✅ `bash`

**List unit tests**

$ ls /tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/tests/unit/

```
__init__.py  conftest.py  test_on_leader_elected.py
<exited with exit code 0>
```


---

<sub>⏱️ 1m 25s</sub>

### ✅ `bash`

**Check config usage in tests**

$ grep -n "config\[" /tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/tests/unit/*.py 2>/dev/null | head -20

```

<exited with exit code 0>
```


---

<sub>⏱️ 1m 29s</sub>

### ✅ `bash`

**List unit harness tests**

$ ls /tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/tests/unit_harness/

```
__init__.py  pre_run_script.sh	test_base.py  test_database_observer.py  test_saml_observer.py	test_state.py
conftest.py  test_actions.py	test_core.py  test_s3_observer.py	 test_smtp_observer.py
<exited with exit code 0>
```


---

<sub>⏱️ 1m 36s</sub>

### ✅ `bash`

**Check config usage in tests**

$ grep -n "self\.config\|\"site_url\"\|\"external_plugins\"\|\"customization\"\|\"enable_roombooking\"\|\"indico_no_reply\"\|\"indico_public_support\"\|\"indico_support\"" /tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/tests/unit_harness/test_core.py | head -30

<details>
<summary>9 lines</summary>

```
129:        self.harness.update_config({"site_url": "foo"})
334:                "enable_roombooking": True,
335:                "external_plugins": "git+https://example.git/#subdirectory=themes_cern",
339:                "site_url": "https://example.local:8080",
418:        self.harness.update_config({"site_url": "https://example.local"})
437:        self.harness.update_config({"site_url": "example.local"})
458:                "external_plugins": "git+https://example.git/#subdirectory=themes_cern",
535:                "external_plugins": "git+https://example.git",
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 1m 36s</sub>

### ✅ `bash`

**Check test file size**

$ wc -l /tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/tests/unit_harness/test_core.py

```
720 /tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/tests/unit_harness/test_core.py
<exited with exit code 0>
```


---

<sub>⏱️ 1m 50s</sub>

### ✅ `bash`

**Find _is_configuration_valid usage**

$ grep -n "_is_configuration_valid" /tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/src/charm.py

```
155:    def _is_configuration_valid(self) -> Tuple[bool, str]:
692:        is_valid, error = self._is_configuration_valid()
<exited with exit code 0>
```


---

<sub>⏱️ 1m 49s</sub>

### ✅ `view`

**/tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/src/charm.py**

/tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/src/charm.py (lines 300-420)

<details>
<summary>121 lines</summary>

```
300.         indico_env_config = self._get_indico_env_config(container)
301.         indico_env_config["INDICO_LOGGING_CONFIG_FILE"] = "indico.logging.yaml"
302.         layer = {
303.             "summary": "Indico layer",
304.             "description": "Indico layer",
305.             "services": {
306.                 "indico": {
307.                     "override": "replace",
308.                     "summary": "Indico service",
309.                     "command": "/srv/indico/start-indico.sh",
310.                     "startup": "enabled",
311.                     "user": "indico",
312.                     "environment": indico_env_config,
313.                 },
314.             },
315.             "checks": {
316.                 "indico-ready": {
317.                     "override": "replace",
318.                     "level": "ready",
319.                     "tcp": {"port": 8081},
320.                 },
321.             },
322.         }
323.         return typing.cast(ops.pebble.LayerDict, layer)
324. 
325.     def _get_celery_pebble_config(self, container: Container) -> ops.pebble.LayerDict:
326.         """Generate pebble config for the celery container.
327. 
328.         Args:
329.             container: Celery container that has the target configuration.
330. 
331.         Returns:
332.             The pebble configuration for the container.
333.         """
334.         indico_env_config = self._get_indico_env_config(container)
335.         indico_env_config["INDICO_LOGGING_CONFIG_FILE"] = "celery.logging.yaml"
336.         layer = {
337.             "summary": "Indico celery layer",
338.             "description": "Indico celery layer",
339.             "services": {
340.                 "celery": {
341.                     "override": "replace",
342.                     "summary": "Indico celery",
343.                     "command": "/usr/bin/indico celery worker -B -E",
344.                     "startup": "enabled",
345.                     "user": "indico",
346.                     "environment": indico_env_config,
347.                 },
348.             },
349.             "checks": {
350.                 "ready": {
351.                     "override": "replace",
352.                     "level": "alive",
353.                     "period": "120s",
354.                     "timeout": "119s",
355.                     "exec": {
356.                         "command": "/usr/bin/indico celery inspect ping",
357.                         "environment": indico_env_config,
358.                     },
359.                 },
360.             },
361.         }
362.         return typing.cast(ops.pebble.LayerDict, layer)
363. 
364.     def _get_nginx_pebble_config(self, _) -> ops.pebble.LayerDict:
365.         """Generate pebble config for the indico-nginx container.
366. 
367.         Returns:
368.             The pebble configuration for the container.
369.         """
370.         layer = {
371.             "summary": "Indico nginx layer",
372.             "description": "Indico nginx layer",
373.             "services": {
374.                 "indico-nginx": {
375.                     "override": "replace",
376.                     "summary": "Nginx service",
377.                     "command": "/usr/sbin/nginx",
378.                     "startup": "enabled",
379.                 },
380.             },
381.             "checks": {
382.                 "nginx-ready": {
383.                     "override": "replace",
384.                     "level": "alive",
385.                     "http": {"url": "http://localhost:8080/health"},
386.                 },
387.             },
388.         }
389.         return typing.cast(ops.pebble.LayerDict, layer)
390. 
391.     def _get_redis_url(self, redis_name: str) -> Optional[str]:
392.         """Get Url for redis charm.
393. 
394.         Args:
395.             redis_name (str): Name of the redis charm to connect to.
396. 
397.         Returns:
398.             Url for the redis charm.
399. 
400.         Raises:
401.            InvalidRedisNameError: If redis name is invalid
402.         """
403.         if redis_name == "redis-broker":
404.             redis = self.redis_broker
405.         elif redis_name == "redis-cache":
406.             redis = self.redis_cache
407.         else:
408.             raise InvalidRedisNameError(f"Invalid Redis name: {redis_name}")
409. 
410.         relation = self.model.get_relation(redis.relation_name)
411.         if not relation:
412.             return None
413.         relation_app_data = relation.data[relation.app]
414.         relation_unit_data = redis.relation_data
415. 
416.         try:
417.             redis_hostname = str(
418.                 relation_app_data.get("leader-host", relation_unit_data["hostname"])
419.             )
420.             redis_port = int(relation_unit_data["port"])
```

</details>


---

<sub>⏱️ 1m 53s</sub>

### ✅ `view`

**/tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/src/charm.py**

/tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/src/charm.py (lines 680-720)

<details>
<summary>41 lines</summary>

```
680.     def _on_config_changed(self, event: HookEvent) -> None:
681.         """Handle changes in configuration.
682. 
683.         Args:
684.             event: Event triggering the configuration change handler.
685.         """
686.         if not self._are_relations_ready(event):
687.             return
688.         if not self._are_pebble_instances_ready():
689.             self.unit.status = WaitingStatus("Waiting for pebble")
690.             return
691.         self.model.unit.status = MaintenanceStatus("Configuring pod")
692.         is_valid, error = self._is_configuration_valid()
693.         if not is_valid:
694.             self.model.unit.status = BlockedStatus(error)
695.             return
696.         for container_name in self.model.unit.containers:
697.             self._config_pebble(self.unit.get_container(container_name))
698. 
699.     def _get_current_customization_url(self) -> str:
700.         """Get the current remote repository for the customization changes.
701. 
702.         Returns:
703.             The customization URL.
704.         """
705.         indico_container = self.unit.get_container("indico")
706.         process = indico_container.exec(
707.             ["git", "config", "--get", "remote.origin.url"],
708.             working_dir=INDICO_CUSTOMIZATION_DIR,
709.             user="indico",
710.         )
711.         remote_url = ""
712.         try:
713.             remote_url, _ = process.wait_output()
714.         except ExecError as ex:
715.             logging.debug(ex)
716.         return remote_url.rstrip()
717. 
718.     def _install_plugins(self, container: Container, plugins: List[str]) -> None:
719.         """Install the external plugins.
720.
```

</details>


---

<sub>⏱️ 2m 18s</sub>

### ✅ `bash`

**Check pydantic version**

$ python3 -c "import pydantic; print(pydantic.VERSION)"

```
1.10.26
<exited with exit code 0>
```


---

<sub>⏱️ 2m 18s</sub>

### ✅ `bash`

**Check pydantic imports in state.py**

$ grep -n "^from pydantic\|^import pydantic" /tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/src/state.py

```
16:from pydantic import AnyHttpUrl, BaseModel, Field, HttpUrl, ValidationError
<exited with exit code 0>
```


---

<sub>⏱️ 2m 23s</sub>

### 💬 Copilot

Good - pydantic v1, so I'll use `@validator`. Now let me run the tests to understand the baseline before making changes.

---

<sub>⏱️ 2m 24s</sub>

### ✅ `bash`

**Install requirements**

$ cd /tmp/ops-upgrade-experiment/indico-operator__config-classes__C2 && pip install -r requirements.txt -q 2>&1 | tail -5

```
See /usr/share/doc/python3.12/README.venv for more information.

note: If you believe this is a mistake, please contact your Python installation or OS distribution provider. You can override this, at the risk of breaking your Python installation or OS, by passing --break-system-packages.
hint: See PEP 668 for the detailed specification.
<exited with exit code 0>
```


---

<sub>⏱️ 2m 29s</sub>

### ✅ `bash`

**Run unit tests baseline**

$ cd /tmp/ops-upgrade-experiment/indico-operator__config-classes__C2 && python3 -m pytest tests/unit_harness/test_core.py -x -q 2>&1 | tail -30

<details>
<summary>23 lines</summary>

```
......................                                                   [100%]
=============================== warnings summary ===============================
tests/unit_harness/test_core.py::test_proxyconfig_invalid
  /tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/tests/unit_harness/test_core.py:27: PendingDeprecationWarning: Harness is deprecated. For the recommended approach, see: https://documentation.ubuntu.com/ops/2.x/howto/write-unit-tests-for-a-charm.html
    harness = Harness(IndicoOperatorCharm)

tests/unit_harness/test_core.py: 23 warnings
  /tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/tests/unit_harness/test_base.py:21: PendingDeprecationWarning: Harness is deprecated. For the recommended approach, see: https://documentation.ubuntu.com/ops/2.x/howto/write-unit-tests-for-a-charm.html
    self.harness = Harness(IndicoOperatorCharm)

tests/unit_harness/test_core.py::TestCore::test_all_pebble_services_ready
tests/unit_harness/test_core.py::TestCore::test_config_changed
tests/unit_harness/test_core.py::TestCore::test_config_changed_when_config_invalid
tests/unit_harness/test_core.py::TestCore::test_config_changed_when_pebble_not_ready
tests/unit_harness/test_core.py::TestCore::test_config_changed_when_saml_groups_plugin_installed
tests/unit_harness/test_core.py::TestCore::test_config_changed_with_external_resources
tests/unit_harness/test_core.py::TestCore::test_indico_nginx_pebble_ready
  /tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/lib/charms/data_platform_libs/v0/data_interfaces.py:1160: DeprecationWarning: JujuVersion.from_environ() is deprecated, use self.model.juju_version instead
    self._jujuversion = JujuVersion.from_environ()

tests/unit_harness/test_core.py: 33 warnings
  /tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/src/charm.py:893: DeprecationWarning: JujuVersion.from_environ() is deprecated, use self.model.juju_version instead
    juju_version = JujuVersion.from_environ()

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
22 passed, 64 warnings in 0.39s
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 2m 42s</sub>

### 💬 Copilot

Now I'll implement the changes. First, add `CharmConfig` to `state.py`, then update `charm.py` to use `load_config`.

---

<sub>⏱️ 2m 42s</sub>

### ✅ `bash`

**Check Tuple and urlparse usage in charm.py**

$ grep -n "Tuple\|urlparse" /tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/src/charm.py | head -10

<details>
<summary>9 lines</summary>

```
15:from typing import Any, Dict, Iterator, List, Optional, Tuple
16:from urllib.parse import urlparse
155:    def _is_configuration_valid(self) -> Tuple[bool, str]:
159:            Tuple containing as first element whether the configuration is valid.
163:        if site_url and not urlparse(site_url).hostname:
174:        if not site_url or not (hostname := urlparse(site_url).hostname):
185:        return urlparse(site_url).scheme if site_url else "http"
194:        return urlparse(site_url).port
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 2m 48s</sub>

### ✅ `bash`

**Check Tuple usage in charm.py**

$ grep -n "Tuple" /tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/src/charm.py

```
15:from typing import Any, Dict, Iterator, List, Optional, Tuple
155:    def _is_configuration_valid(self) -> Tuple[bool, str]:
159:            Tuple containing as first element whether the configuration is valid.
<exited with exit code 0>
```


---

<sub>⏱️ 2m 56s</sub>

### 💬 Copilot

Now let me make the changes. Starting with `state.py` to add `CharmConfig`:

---

<sub>⏱️ 2m 56s</sub>

### ✅ `edit`

**/tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/src/state.py**

/tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/src/state.py

```
File /tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/src/state.py updated with changes.
```


---

<sub>⏱️ 3m 1s</sub>

### ✅ `edit`

**/tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/src/state.py**

/tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/src/state.py

```
File /tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/src/state.py updated with changes.
```


---

<sub>⏱️ 3m 11s</sub>

### 💬 Copilot

Now add the `CharmConfig` class to `state.py` after the existing error classes and before `ProxyConfig`:

---

<sub>⏱️ 3m 11s</sub>

### ✅ `edit`

**/tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/src/state.py**

/tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/src/state.py

```
File /tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/src/state.py updated with changes.
```


---

<sub>⏱️ 3m 16s</sub>

### 💬 Copilot

Now update `charm.py` to import `CharmConfig` and use `load_config`:

---

<sub>⏱️ 3m 16s</sub>

### ✅ `edit`

**/tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/src/charm.py**

/tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/src/charm.py

```
File /tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/src/charm.py updated with changes.
```


---

<sub>⏱️ 3m 20s</sub>

### 💬 Copilot

Now add `self.typed_config = self.load_config(CharmConfig, errors='blocked')` in `__init__` right after `super().__init__(*args)`:

---

<sub>⏱️ 3m 20s</sub>

### ✅ `view`

**/tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/src/charm.py**

/tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/src/charm.py (lines 65-90)

<details>
<summary>26 lines</summary>

```
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
```

</details>


---

<sub>⏱️ 3m 24s</sub>

### ✅ `edit`

**/tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/src/charm.py**

/tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/src/charm.py

```
File /tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/src/charm.py updated with changes.
```


---

<sub>⏱️ 3m 31s</sub>

### 💬 Copilot

Now remove `_is_configuration_valid` and replace all `self.config[...]` with `self.typed_config.\<field\>`. First, remove the method:

---

<sub>⏱️ 3m 31s</sub>

### ✅ `edit`

**/tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/src/charm.py**

/tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/src/charm.py

```
File /tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/src/charm.py updated with changes.
```


---

<sub>⏱️ 3m 35s</sub>

### 💬 Copilot

Now replace `self.config[...]` references with `self.typed_config.\<field\>`:

---

<sub>⏱️ 3m 35s</sub>

### ✅ `view`

**/tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/src/charm.py**

/tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/src/charm.py (lines 156-200)

<details>
<summary>45 lines</summary>

```
156.     def _get_external_hostname(self) -> str:
157.         """Extract and return hostname from site_url or default to [application name].local.
158. 
159.         Returns:
160.             The site URL defined as part of the site_url configuration or a default value.
161.         """
162.         site_url = typing.cast(str, self.config["site_url"])
163.         if not site_url or not (hostname := urlparse(site_url).hostname):
164.             return f"{self.app.name}.local"
165.         return hostname
166. 
167.     def _get_external_scheme(self) -> str:
168.         """Extract and return schema from site_url.
169. 
170.         Returns:
171.             The HTTP schema.
172.         """
173.         site_url = typing.cast(str, self.config["site_url"])
174.         return urlparse(site_url).scheme if site_url else "http"
175. 
176.     def _get_external_port(self) -> Optional[int]:
177.         """Extract and return port from site_url.
178. 
179.         Returns:
180.             The port number.
181.         """
182.         site_url = typing.cast(str, self.config["site_url"])
183.         return urlparse(site_url).port
184. 
185.     def _are_relations_ready(self, _) -> bool:
186.         """Check if the needed relations are established.
187. 
188.         Returns:
189.             If the needed relations have been established.
190.         """
191.         if self.redis_broker.relation_data is None:
192.             self.unit.status = WaitingStatus("Waiting for redis-broker availability")
193.             return False
194.         if self.redis_cache.relation_data is None:
195.             self.unit.status = WaitingStatus("Waiting for redis-cache availability")
196.             return False
197.         if self.database.uri is None:
198.             self.unit.status = WaitingStatus("Waiting for database availability")
199.             return False
200.         return True
```

</details>


---

<sub>⏱️ 3m 40s</sub>

### ✅ `edit`

**/tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/src/charm.py**

/tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/src/charm.py

```
File /tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/src/charm.py updated with changes.
```


---

<sub>⏱️ 3m 45s</sub>

### ✅ `edit`

**/tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/src/charm.py**

/tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/src/charm.py

```
File /tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/src/charm.py updated with changes.
```


---

<sub>⏱️ 3m 49s</sub>

### ✅ `edit`

**/tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/src/charm.py**

/tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/src/charm.py

```
File /tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/src/charm.py updated with changes.
```


---

<sub>⏱️ 3m 54s</sub>

### 💬 Copilot

Now replace config accesses in `_config_pebble` (external_plugins):

---

<sub>⏱️ 3m 54s</sub>

### ✅ `view`

**/tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/src/charm.py**

/tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/src/charm.py (lines 218-240)

<details>
<summary>23 lines</summary>

```
218.         """
219.         self.unit.status = MaintenanceStatus(f"Adding {container.name} layer to pebble")
220.         if container.name == "indico":
221.             # Plugins need to be installed before adding the layer so that
222.             # they are included in the corresponding env vars
223.             plugins = (
224.                 typing.cast(str, self.config["external_plugins"]).split(",")
225.                 if self.config["external_plugins"]
226.                 else []
227.             )
228.             self._install_plugins(container, plugins)
229.             container.add_layer(container.name, self._get_logrotate_config(), combine=True)
230.             indico_config = self._get_indico_pebble_config(container)
231.             container.add_layer(container.name, indico_config, combine=True)
232.             peer_relation = self.model.get_relation("indico-peers")
233.             if (
234.                 not peer_relation
235.                 or peer_relation.data[self.app].get("celery-unit") == self.unit.name
236.             ):
237.                 celery_config = self._get_celery_pebble_config(container)
238.                 container.add_layer("celery", celery_config, combine=True)
239.                 celery_exporter_config = self._get_celery_prometheus_exporter_pebble_config(
240.                     container
```

</details>


---

<sub>⏱️ 3m 59s</sub>

### ✅ `edit`

**/tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/src/charm.py**

/tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/src/charm.py

```
File /tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/src/charm.py updated with changes.
```


---

<sub>⏱️ 4m 6s</sub>

### 💬 Copilot

Now replace the config accesses in `_get_indico_env_config`:

---

<sub>⏱️ 4m 6s</sub>

### ✅ `edit`

**/tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/src/charm.py**

/tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/src/charm.py

```
File /tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/src/charm.py updated with changes.
```


---

<sub>⏱️ 4m 10s</sub>

### 💬 Copilot

Replace `self.config["site_url"]` in the SAML section:

---

<sub>⏱️ 4m 10s</sub>

### ✅ `view`

**/tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/src/charm.py**

/tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/src/charm.py (lines 595-620)

<details>
<summary>26 lines</summary>

```
595.         # SAML configuration reference https://github.com/onelogin/python3-saml
596.         if self.state.saml_config:
597.             saml_config: Dict[str, Any] = {
598.                 "strict": True,
599.                 "sp": {
600.                     "entityId": self.config["site_url"],
601.                 },
602.                 "idp": {
603.                     "entityId": self.state.saml_config.entity_id,
604.                     "x509cert": self.state.saml_config.certificates[0],
605.                 },
606.             }
607.             for endpoint in self.state.saml_config.endpoints:
608.                 # First letter needs to be lowercase
609.                 endpoint_name = endpoint.name[:1].lower() + endpoint.name[1:]
610.                 saml_config["idp"][endpoint_name] = {
611.                     "url": str(endpoint.url),
612.                     "binding": endpoint.binding,
613.                 }
614.                 if endpoint.response_url:
615.                     saml_config["idp"][endpoint_name]["response_url"] = str(endpoint.response_url)
616.             auth_providers = {"ubuntu": {"type": "saml", "saml_config": saml_config}}
617.             env_config["INDICO_AUTH_PROVIDERS"] = str(auth_providers)
618.             identity_providers = {
619.                 "ubuntu": {
620.                     "type": (
```

</details>


---

<sub>⏱️ 4m 14s</sub>

### ✅ `edit`

**/tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/src/charm.py**

/tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/src/charm.py

```
File /tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/src/charm.py updated with changes.
```


---

<sub>⏱️ 4m 20s</sub>

### 💬 Copilot

Now update the `_on_config_changed` method to remove the `_is_configuration_valid` call:

---

<sub>⏱️ 4m 20s</sub>

### ✅ `view`

**/tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/src/charm.py**

/tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/src/charm.py (lines 668-700)

<details>
<summary>33 lines</summary>

```
668. 
669.     def _on_config_changed(self, event: HookEvent) -> None:
670.         """Handle changes in configuration.
671. 
672.         Args:
673.             event: Event triggering the configuration change handler.
674.         """
675.         if not self._are_relations_ready(event):
676.             return
677.         if not self._are_pebble_instances_ready():
678.             self.unit.status = WaitingStatus("Waiting for pebble")
679.             return
680.         self.model.unit.status = MaintenanceStatus("Configuring pod")
681.         is_valid, error = self._is_configuration_valid()
682.         if not is_valid:
683.             self.model.unit.status = BlockedStatus(error)
684.             return
685.         for container_name in self.model.unit.containers:
686.             self._config_pebble(self.unit.get_container(container_name))
687. 
688.     def _get_current_customization_url(self) -> str:
689.         """Get the current remote repository for the customization changes.
690. 
691.         Returns:
692.             The customization URL.
693.         """
694.         indico_container = self.unit.get_container("indico")
695.         process = indico_container.exec(
696.             ["git", "config", "--get", "remote.origin.url"],
697.             working_dir=INDICO_CUSTOMIZATION_DIR,
698.             user="indico",
699.         )
700.         remote_url = ""
```

</details>


---

<sub>⏱️ 4m 25s</sub>

### ✅ `edit`

**/tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/src/charm.py**

/tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/src/charm.py

```
File /tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/src/charm.py updated with changes.
```


---

<sub>⏱️ 4m 30s</sub>

### 💬 Copilot

Now replace the remaining `self.config[...]` accesses in `_download_customization_changes` and `_refresh_external_resources`:

---

<sub>⏱️ 4m 30s</sub>

### ✅ `view`

**/tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/src/charm.py**

/tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/src/charm.py (lines 757-830)

<details>
<summary>74 lines</summary>

```
757.         )
758.         process.wait_output()
759. 
760.     def _download_customization_changes(self, container: Container) -> None:
761.         """Clone the remote repository with the customization changes.
762. 
763.         Args:
764.             container: Container in which the download will be performed.
765.         """
766.         current_remote_url = self._get_current_customization_url()
767.         if current_remote_url != self.config["customization_sources_url"]:
768.             logging.debug(
769.                 "Removing old contents from directory %s. Previous repository: '%s'",
770.                 INDICO_CUSTOMIZATION_DIR,
771.                 current_remote_url,
772.             )
773.             process = container.exec(["rm", "-rf", INDICO_CUSTOMIZATION_DIR], user="indico")
774.             process.wait_output()
775.             process = container.exec(["mkdir", INDICO_CUSTOMIZATION_DIR], user="indico")
776.             process.wait_output()
777.             if self.config["customization_sources_url"]:
778.                 logging.debug(
779.                     "New URL repo for customization %s. Cloning contents",
780.                     self.config["customization_sources_url"],
781.                 )
782.                 self._exec_cmd_in_custom_dir(
783.                     container,
784.                     [
785.                         "git",
786.                         "clone",
787.                         typing.cast(str, self.config["customization_sources_url"]),
788.                         ".",
789.                     ],
790.                 )
791. 
792.     def _refresh_external_resources(self, _) -> Dict:
793.         """Pull changes from the remote repository and upgrade external plugins.
794. 
795.         Returns:
796.             Dictionary containing the execution results for each of the operations executed.
797.         """
798.         results = {
799.             "customization-changes": False,
800.             "plugin-updates": [],
801.         }
802.         container = self.unit.get_container("indico")
803.         if container.can_connect():
804.             self._download_customization_changes(container)
805.             if self.config["customization_sources_url"]:
806.                 logging.debug("Pulling changes from %s", self.config["customization_sources_url"])
807.                 self._exec_cmd_in_custom_dir(
808.                     container,
809.                     ["git", "pull"],
810.                 )
811.                 logging.debug("Reloading uWSGI")
812.                 self._exec_cmd_in_custom_dir(container, ["touch", UWSGI_TOUCH_RELOAD])
813.                 results["customization-changes"] = True
814.             if self.config["external_plugins"]:
815.                 logging.debug("Upgrading external plugins %s", self.config["external_plugins"])
816.                 plugins = typing.cast(str, self.config["external_plugins"]).split(",")
817.                 self._install_plugins(container, plugins)
818.                 results["plugin-updates"] = plugins
819.         return results
820. 
821.     def _refresh_external_resources_action(self, event: ActionEvent) -> None:
822.         """Refresh external resources and report action result.
823. 
824.         Args:
825.             event: Event triggering the refresh action.
826.         """
827.         results = self._refresh_external_resources(event)
828.         event.set_results(results)
829. 
830.     def _on_leader_elected(self, _) -> None:
```

</details>


---

<sub>⏱️ 4m 38s</sub>

### ✅ `edit`

**/tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/src/charm.py**

/tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/src/charm.py

```
File /tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/src/charm.py updated with changes.
```


---

<sub>⏱️ 4m 44s</sub>

### ✅ `edit`

**/tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/src/charm.py**

/tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/src/charm.py

```
File /tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/src/charm.py updated with changes.
```


---

<sub>⏱️ 4m 49s</sub>

### 💬 Copilot

Now remove `Tuple` from the typing imports since `_is_configuration_valid` is gone:

---

<sub>⏱️ 4m 49s</sub>

### ✅ `edit`

**/tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/src/charm.py**

/tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/src/charm.py

```
File /tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/src/charm.py updated with changes.
```


---

<sub>⏱️ 4m 54s</sub>

### 💬 Copilot

Now verify there are no remaining `self.config[` accesses:

---

<sub>⏱️ 4m 54s</sub>

### ✅ `bash`

**Check for remaining self.config accesses**

$ grep -n "self\.config\[" /tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/src/charm.py

```

<exited with exit code 1>
```


---

<sub>⏱️ 4m 59s</sub>

### 💬 Copilot

Good. Now run the tests to see if everything passes:

---

<sub>⏱️ 5m 0s</sub>

### ✅ `bash`

**Run unit tests**

$ cd /tmp/ops-upgrade-experiment/indico-operator__config-classes__C2 && python3 -m pytest tests/unit_harness/test_core.py -x -q 2>&1 | tail -30

<details>
<summary>26 lines</summary>

```
E       - example.local
E       + indico.local

tests/unit_harness/test_core.py:346: AssertionError
------------------------------ Captured log call -------------------------------
WARNING  charms.prometheus_k8s.v0.prometheus_scrape:prometheus_scrape.py:1452 2 containers are present in metadata.yaml and refresh_event was not specified. Defaulting to update_status. Metrics IP may not be set in a timely fashion.
=============================== warnings summary ===============================
tests/unit_harness/test_core.py::test_proxyconfig_invalid
  /tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/tests/unit_harness/test_core.py:27: PendingDeprecationWarning: Harness is deprecated. For the recommended approach, see: https://documentation.ubuntu.com/ops/2.x/howto/write-unit-tests-for-a-charm.html
    harness = Harness(IndicoOperatorCharm)

tests/unit_harness/test_core.py::TestCore::test_all_pebble_services_ready
tests/unit_harness/test_core.py::TestCore::test_config_changed
  /tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/tests/unit_harness/test_base.py:21: PendingDeprecationWarning: Harness is deprecated. For the recommended approach, see: https://documentation.ubuntu.com/ops/2.x/howto/write-unit-tests-for-a-charm.html
    self.harness = Harness(IndicoOperatorCharm)

tests/unit_harness/test_core.py::TestCore::test_all_pebble_services_ready
tests/unit_harness/test_core.py::TestCore::test_config_changed
  /tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/lib/charms/data_platform_libs/v0/data_interfaces.py:1160: DeprecationWarning: JujuVersion.from_environ() is deprecated, use self.model.juju_version instead
    self._jujuversion = JujuVersion.from_environ()

tests/unit_harness/test_core.py: 11 warnings
  /tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/src/charm.py:878: DeprecationWarning: JujuVersion.from_environ() is deprecated, use self.model.juju_version instead
    juju_version = JujuVersion.from_environ()

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ============================
FAILED tests/unit_harness/test_core.py::TestCore::test_config_changed - Asser...
!!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
1 failed, 2 passed, 16 warnings in 0.11s
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 5m 5s</sub>

### ✅ `bash`

**Check the failing test**

$ grep -n "test_config_changed\|example.local\|indico.local" /tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/tests/unit_harness/test_core.py | head -20

<details>
<summary>15 lines</summary>

```
216:        self.assertEqual("indico.local", updated_plan_env["SERVICE_HOSTNAME"])
268:        self.assertEqual("indico.local", updated_plan_env["SERVICE_HOSTNAME"])
293:    def test_config_changed(self, mock_secrets, mock_exec):  # pylint: disable=R0915
339:                "site_url": "https://example.local:8080",
346:        self.assertEqual("example.local", updated_plan_env["SERVICE_HOSTNAME"])
367:            "https://example.local:8080",
373:        self.assertEqual("https://example.local:8080", applied_saml_config["sp"]["entityId"])
418:        self.harness.update_config({"site_url": "https://example.local"})
425:        self.assertEqual("example.local", nginx_route_relation_data["service-hostname"])
428:    def test_config_changed_when_config_invalid(self, mock_exec):
437:        self.harness.update_config({"site_url": "example.local"})
445:    def test_config_changed_with_external_resources(self, mock_secrets, mock_exec):
479:    def test_config_changed_when_pebble_not_ready(self):
490:    def test_config_changed_when_saml_groups_plugin_installed(self, mock_exec):
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 5m 9s</sub>

### ✅ `view`

**/tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/tests/unit_harness/test_core.py**

/tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/tests/unit_harness/test_core.py (lines 293-380)

<details>
<summary>88 lines</summary>

```
293.     def test_config_changed(self, mock_secrets, mock_exec):  # pylint: disable=R0915
294.         """
295.         arrange: charm created and relations established
296.         act: trigger a valid configuration change for the charm
297.         assert: the container and the service are running and properly configured
298.         """
299.         mock_exec.return_value = MagicMock(wait_output=MagicMock(return_value=("", None)))
300.         mock_secrets.token_hex.return_value = "123456"
301. 
302.         self.set_relations_and_leader()
303.         saml_endpoints = (
304.             SamlEndpoint(
305.                 name="SingleSignOnService",
306.                 url="https://example.com/login",
307.                 binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect",
308.             ),
309.             SamlEndpoint(
310.                 name="SingleLogoutService",
311.                 url="https://example.com/logout",
312.                 binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect",
313.                 response_url="https://example.com/response",
314.             ),
315.         )
316.         saml_config = SamlConfig(
317.             entity_id="entity",
318.             metadata_url="https://example.com/metadata",
319.             certificates=("cert1,", "cert2"),
320.             endpoints=saml_endpoints,
321.         )
322.         s3_config = S3Config(
323.             bucket="test-bucket",
324.             host="s3.example.com",
325.             access_key=token_hex(16),
326.             secret_key=token_hex(16),
327.         )
328.         self.harness.charm.state.s3_config = s3_config
329.         self.harness.charm.state.saml_config = saml_config
330.         self.harness.update_config(
331.             {
332.                 "customization_debug": True,
333.                 "customization_sources_url": "https://example.com/custom",
334.                 "enable_roombooking": True,
335.                 "external_plugins": "git+https://example.git/#subdirectory=themes_cern",
336.                 "indico_support_email": "example@email.local",
337.                 "indico_public_support_email": "public@email.local",
338.                 "indico_no_reply_email": "noreply@email.local",
339.                 "site_url": "https://example.local:8080",
340.             }
341.         )
342. 
343.         updated_plan = self.harness.get_container_pebble_plan("indico").to_dict()
344.         updated_plan_env = updated_plan["services"]["indico"]["environment"]
345. 
346.         self.assertEqual("example.local", updated_plan_env["SERVICE_HOSTNAME"])
347.         self.assertTrue(updated_plan_env["ENABLE_ROOMBOOKING"])
348.         self.assertEqual("example@email.local", updated_plan_env["INDICO_SUPPORT_EMAIL"])
349.         self.assertEqual("public@email.local", updated_plan_env["INDICO_PUBLIC_SUPPORT_EMAIL"])
350.         self.assertEqual("noreply@email.local", updated_plan_env["INDICO_NO_REPLY_EMAIL"])
351.         self.assertEqual("https", updated_plan_env["SERVICE_SCHEME"])
352.         self.assertEqual(8080, updated_plan_env["SERVICE_PORT"])
353.         self.assertTrue(updated_plan_env["CUSTOMIZATION_DEBUG"])
354.         storage_dict = literal_eval(updated_plan_env["STORAGE_DICT"])
355.         self.assertEqual("s3", updated_plan_env["ATTACHMENT_STORAGE"])
356.         self.assertEqual("fs:/srv/indico/archive", storage_dict["default"])
357.         self.assertEqual(
358.             (
359.                 f"s3:bucket={s3_config.bucket},access_key={s3_config.access_key},"
360.                 f"secret_key={s3_config.secret_key},proxy=true,host={s3_config.host}"
361.             ),
362.             storage_dict["s3"],
363.         )
364.         auth_providers = literal_eval(updated_plan_env["INDICO_AUTH_PROVIDERS"])
365.         self.assertEqual("saml", auth_providers["ubuntu"]["type"])
366.         self.assertEqual(
367.             "https://example.local:8080",
368.             auth_providers["ubuntu"]["saml_config"]["sp"]["entityId"],
369.         )
370.         auth_providers = literal_eval(updated_plan_env["INDICO_AUTH_PROVIDERS"])
371.         self.assertEqual("saml", auth_providers["ubuntu"]["type"])
372.         applied_saml_config = auth_providers["ubuntu"]["saml_config"]
373.         self.assertEqual("https://example.local:8080", applied_saml_config["sp"]["entityId"])
374.         self.assertEqual(saml_config.entity_id, applied_saml_config["idp"]["entityId"])
375.         self.assertEqual(saml_config.certificates[0], applied_saml_config["idp"]["x509cert"])
376.         self.assertEqual(
377.             str(saml_config.endpoints[0].url),
378.             applied_saml_config["idp"]["singleSignOnService"]["url"],
379.         )
380.         self.assertEqual(
```

</details>


---

<sub>⏱️ 5m 25s</sub>

### ✅ `bash`

**Check load_config source**

$ python3 -c "import ops; import inspect; print(inspect.getsource(ops.CharmBase.load_config))"

<details>
<summary>82 lines</summary>

```
def load_config(
        self,
        cls: type[_T],
        *args: Any,
        errors: Literal['raise', 'blocked'] = 'raise',
        **kwargs: Any,
    ) -> _T:
        """Load the config into an instance of a config class.

        The raw Juju config is passed to the config class's ``__init__``, as
        keyword arguments, with the following changes:

        * ``secret`` type options have a :class:`model.Secret` value rather
          than the secret ID. Note that the secret object is not validated by
          Juju at this time, so may raise :class:`SecretNotFoundError` when it
          is used later (if the secret does not exist or the unit does not have
          permission to access it).
        * dashes in names are converted to underscores.

        For dataclasses and Pydantic ``BaseModel`` subclasses, only fields in
        the Juju config that have a matching field in the class are passed as
        arguments. Pydantic fields that have an ``alias``, or dataclasses that
        have a ``metadata{'alias'=}``, will have the alias applied when loading.

        For example::

            class Config(pydantic.BaseModel):
                # This field is called 'class' in the Juju config options.
                workload_class: str = pydantic.Field(alias='class')

            def _on_config_changed(self, event: ops.ConfigChangedEvent):
                data = self.load_config(Config, errors='blocked')
                # `data.workload_class` has the value of the Juju option `class`

        Any additional positional or keyword arguments to this method will be
        passed through to the config class ``__init__``.

        Args:
            cls: A class that will accept the Juju options as keyword arguments,
                and raise ``ValueError`` if validation fails.
            errors: what to do if the config is invalid. If ``blocked``, this
                will set the unit status to blocked with an appropriate message
                and then exit successfully (this informs Juju that
                the event was handled and it will not be retried).
                If ``raise``, ``load_config``
                will not catch any exceptions, leaving the charm to handle
                errors.
            args: positional arguments to pass through to the config class.
            kwargs: keyword arguments to pass through to the config class.

        Returns:
            An instance of the config class that was passed in the ``cls`` argument
            with the current config values.

        Raises:
            ValueError: if the configuration is invalid and ``errors`` is set to
                ``raise``.
        """
        from ._main import _Abort

        config: dict[str, bool | int | float | str | model.Secret] = kwargs.copy()
        try:
            fields = set(_juju_fields(cls))
        except ValueError:
            fields = None
        for key, value in self.config.items():
            attr = key.replace('-', '_')
            if fields is not None and attr not in fields:
                continue
            option_type = self.meta.config.get(key)
            # Convert secret IDs to secret objects. We create the object rather
            # that using model.get_secret so that it's entirely lazy, in the
            # same way that SecretEvent.secret is.
            if option_type and option_type.type == 'secret':
                assert isinstance(value, str)  # Juju will have made sure of this.
                value = model.Secret(
                    backend=self.model._backend,
                    id=value,
                    _secret_set_cache=self.model._cache._secret_set_cache,
                )
            config[attr] = value
        try:
            return cls(*args, **config)
        except ValueError as e:
            if errors == 'raise':
                raise
            # We exit with a zero code because we don't want Juju to retry
            # (the config needs to be fixed by the Juju user), and we don't
            # want the status we just set to be overridden by an error
            # status.
            self.unit.status = model.BlockedStatus(f'Invalid config: {e}')
            raise _Abort(0) from e
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 5m 53s</sub>

### 💬 Copilot

The issue is the Harness doesn't re-run `__init__` on config changes. I need to refresh `typed_config` in `_on_config_changed`. Let me check where config is consumed in event handlers outside `_on_config_changed`:

---

<sub>⏱️ 5m 53s</sub>

### ✅ `view`

**/tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/src/charm.py**

/tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/src/charm.py (lines 668-690)

<details>
<summary>23 lines</summary>

```
668. 
669.     def _on_config_changed(self, event: HookEvent) -> None:
670.         """Handle changes in configuration.
671. 
672.         Args:
673.             event: Event triggering the configuration change handler.
674.         """
675.         if not self._are_relations_ready(event):
676.             return
677.         if not self._are_pebble_instances_ready():
678.             self.unit.status = WaitingStatus("Waiting for pebble")
679.             return
680.         self.model.unit.status = MaintenanceStatus("Configuring pod")
681.         for container_name in self.model.unit.containers:
682.             self._config_pebble(self.unit.get_container(container_name))
683. 
684.     def _get_current_customization_url(self) -> str:
685.         """Get the current remote repository for the customization changes.
686. 
687.         Returns:
688.             The customization URL.
689.         """
690.         indico_container = self.unit.get_container("indico")
```

</details>


---

<sub>⏱️ 6m 6s</sub>

### ✅ `edit`

**/tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/src/charm.py**

/tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/src/charm.py

```
File /tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/src/charm.py updated with changes.
```


---

<sub>⏱️ 6m 12s</sub>

### ✅ `bash`

**Run tests again**

$ cd /tmp/ops-upgrade-experiment/indico-operator__config-classes__C2 && python3 -m pytest tests/unit_harness/test_core.py -x -q 2>&1 | tail -20

<details>
<summary>18 lines</summary>

```
tests/unit_harness/test_core.py::TestCore::test_config_changed
tests/unit_harness/test_core.py::TestCore::test_config_changed_when_config_invalid
  /tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/tests/unit_harness/test_base.py:21: PendingDeprecationWarning: Harness is deprecated. For the recommended approach, see: https://documentation.ubuntu.com/ops/2.x/howto/write-unit-tests-for-a-charm.html
    self.harness = Harness(IndicoOperatorCharm)

tests/unit_harness/test_core.py::TestCore::test_all_pebble_services_ready
tests/unit_harness/test_core.py::TestCore::test_config_changed
tests/unit_harness/test_core.py::TestCore::test_config_changed_when_config_invalid
  /tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/lib/charms/data_platform_libs/v0/data_interfaces.py:1160: DeprecationWarning: JujuVersion.from_environ() is deprecated, use self.model.juju_version instead
    self._jujuversion = JujuVersion.from_environ()

tests/unit_harness/test_core.py: 18 warnings
  /tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/src/charm.py:879: DeprecationWarning: JujuVersion.from_environ() is deprecated, use self.model.juju_version instead
    juju_version = JujuVersion.from_environ()

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ============================
FAILED tests/unit_harness/test_core.py::TestCore::test_config_changed_when_config_invalid
!!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
1 failed, 3 passed, 25 warnings in 0.19s
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 6m 16s</sub>

### ✅ `view`

**/tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/tests/unit_harness/test_core.py**

/tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/tests/unit_harness/test_core.py (lines 428-445)

<details>
<summary>18 lines</summary>

```
428.     def test_config_changed_when_config_invalid(self, mock_exec):
429.         """
430.         arrange: charm created and relations established
431.         act: trigger an invalid site URL configuration change for the charm
432.         assert: the unit reaches blocked status
433.         """
434.         mock_exec.return_value = MagicMock(wait_output=MagicMock(return_value=("", None)))
435. 
436.         self.set_relations_and_leader()
437.         self.harness.update_config({"site_url": "example.local"})
438.         self.assertEqual(
439.             self.harness.model.unit.status,
440.             ops.BlockedStatus("Configuration option site_url is not valid"),
441.         )
442. 
443.     @patch.object(ops.Container, "exec")
444.     @patch("charm.secrets")
445.     def test_config_changed_with_external_resources(self, mock_secrets, mock_exec):
```

</details>


---

<sub>⏱️ 6m 30s</sub>

### ✅ `bash`

**Check _Abort class**

$ python3 -c "from ops._main import _Abort; print(_Abort)"

```
<class 'ops._main._Abort'>
<exited with exit code 0>
```


---

<sub>⏱️ 6m 30s</sub>

### ✅ `bash`

**Run failing test with output**

$ cd /tmp/ops-upgrade-experiment/indico-operator__config-classes__C2 && python3 -m pytest tests/unit_harness/test_core.py::TestCore::test_config_changed_when_config_invalid -x -q -s 2>&1 | tail -20

<details>
<summary>18 lines</summary>

```
tests/unit_harness/test_core.py::TestCore::test_config_changed_when_config_invalid
  /tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/tests/unit_harness/test_base.py:21: PendingDeprecationWarning: Harness is deprecated. For the recommended approach, see: https://documentation.ubuntu.com/ops/2.x/howto/write-unit-tests-for-a-charm.html
    self.harness = Harness(IndicoOperatorCharm)

tests/unit_harness/test_core.py::TestCore::test_config_changed_when_config_invalid
  /tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/lib/charms/data_platform_libs/v0/data_interfaces.py:1160: DeprecationWarning: JujuVersion.from_environ() is deprecated, use self.model.juju_version instead
    self._jujuversion = JujuVersion.from_environ()

tests/unit_harness/test_core.py::TestCore::test_config_changed_when_config_invalid
tests/unit_harness/test_core.py::TestCore::test_config_changed_when_config_invalid
tests/unit_harness/test_core.py::TestCore::test_config_changed_when_config_invalid
tests/unit_harness/test_core.py::TestCore::test_config_changed_when_config_invalid
  /tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/src/charm.py:879: DeprecationWarning: JujuVersion.from_environ() is deprecated, use self.model.juju_version instead
    juju_version = JujuVersion.from_environ()

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ============================
FAILED tests/unit_harness/test_core.py::TestCore::test_config_changed_when_config_invalid
!!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
1 failed, 6 warnings in 0.14s
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 6m 36s</sub>

### ✅ `bash`

**Get the assertion error details**

$ cd /tmp/ops-upgrade-experiment/indico-operator__config-classes__C2 && python3 -m pytest tests/unit_harness/test_core.py::TestCore::test_config_changed_when_config_invalid -x -q -s 2>&1 | grep "AssertionError\|assert\|BlockedStatus\|Error" | head -10

<details>
<summary>11 lines</summary>

```
Juju at this time, so may raise :class:`SecretNotFoundError` when it
                and raise ``ValueError`` if validation fails.
            ValueError: if the configuration is invalid and ``errors`` is set to
        except ValueError:
                assert isinstance(value, str)  # Juju will have made sure of this.
E   pydantic.error_wrappers.ValidationError: 1 validation error for CharmConfig
pydantic/main.py:364: ValidationError
        assert: the unit reaches blocked status
          Juju at this time, so may raise :class:`SecretNotFoundError` when it
                and raise ``ValueError`` if validation fails.
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 6m 42s</sub>

### ✅ `bash`

**Check if pydantic ValidationError is a ValueError**

$ python3 -c "from pydantic import ValidationError; print(issubclass(ValidationError, ValueError))"

```
True
<exited with exit code 0>
```


---

<sub>⏱️ 6m 47s</sub>

### ✅ `bash`

**Get full error for the failing test**

$ cd /tmp/ops-upgrade-experiment/indico-operator__config-classes__C2 && python3 -m pytest tests/unit_harness/test_core.py::TestCore::test_config_changed_when_config_invalid -x 2>&1 | grep -A 10 "FAILED\|Error\|assert"

<details>
<summary>135 lines</summary>

```
Juju at this time, so may raise :class:`SecretNotFoundError` when it
          is used later (if the secret does not exist or the unit does not have
          permission to access it).
        * dashes in names are converted to underscores.
    
        For dataclasses and Pydantic ``BaseModel`` subclasses, only fields in
        the Juju config that have a matching field in the class are passed as
        arguments. Pydantic fields that have an ``alias``, or dataclasses that
        have a ``metadata{'alias'=}``, will have the alias applied when loading.
    
        For example::
--
                and raise ``ValueError`` if validation fails.
            errors: what to do if the config is invalid. If ``blocked``, this
                will set the unit status to blocked with an appropriate message
                and then exit successfully (this informs Juju that
                the event was handled and it will not be retried).
                If ``raise``, ``load_config``
                will not catch any exceptions, leaving the charm to handle
                errors.
            args: positional arguments to pass through to the config class.
            kwargs: keyword arguments to pass through to the config class.
    
--
            ValueError: if the configuration is invalid and ``errors`` is set to
                ``raise``.
        """
        from ._main import _Abort
    
        config: dict[str, bool | int | float | str | model.Secret] = kwargs.copy()
        try:
            fields = set(_juju_fields(cls))
        except ValueError:
            fields = None
        for key, value in self.config.items():
            attr = key.replace('-', '_')
            if fields is not None and attr not in fields:
                continue
            option_type = self.meta.config.get(key)
            # Convert secret IDs to secret objects. We create the object rather
            # that using model.get_secret so that it's entirely lazy, in the
            # same way that SecretEvent.secret is.
            if option_type and option_type.type == 'secret':
                assert isinstance(value, str)  # Juju will have made sure of this.
                value = model.Secret(
                    backend=self.model._backend,
                    id=value,
                    _secret_set_cache=self.model._cache._secret_set_cache,
                )
            config[attr] = value
        try:
>           return cls(*args, **config)
                   ^^^^^^^^^^^^^^^^^^^^

--
E   pydantic.error_wrappers.ValidationError: 1 validation error for CharmConfig
E   site_url
E     Configuration option site_url is not valid (type=value_error)

pydantic/main.py:364: ValidationError

The above exception was the direct cause of the following exception:

self = <unit_harness.test_core.TestCore testMethod=test_config_changed_when_config_invalid>
mock_exec = <MagicMock name='exec' id='125236074745968'>

    @patch.object(ops.Container, "exec")
    def test_config_changed_when_config_invalid(self, mock_exec):
        """
        arrange: charm created and relations established
--
        assert: the unit reaches blocked status
        """
        mock_exec.return_value = MagicMock(wait_output=MagicMock(return_value=("", None)))
    
        self.set_relations_and_leader()
>       self.harness.update_config({"site_url": "example.local"})

tests/unit_harness/test_core.py:437: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
/home/ubuntu/.local/lib/python3.12/site-packages/ops/_private/harness.py:1508: in update_config
    self._charm.on.config_changed.emit()
--
          Juju at this time, so may raise :class:`SecretNotFoundError` when it
          is used later (if the secret does not exist or the unit does not have
          permission to access it).
        * dashes in names are converted to underscores.
    
        For dataclasses and Pydantic ``BaseModel`` subclasses, only fields in
        the Juju config that have a matching field in the class are passed as
        arguments. Pydantic fields that have an ``alias``, or dataclasses that
        have a ``metadata{'alias'=}``, will have the alias applied when loading.
    
        For example::
--
                and raise ``ValueError`` if validation fails.
            errors: what to do if the config is invalid. If ``blocked``, this
                will set the unit status to blocked with an appropriate message
                and then exit successfully (this informs Juju that
                the event was handled and it will not be retried).
                If ``raise``, ``load_config``
                will not catch any exceptions, leaving the charm to handle
                errors.
            args: positional arguments to pass through to the config class.
            kwargs: keyword arguments to pass through to the config class.
    
--
            ValueError: if the configuration is invalid and ``errors`` is set to
                ``raise``.
        """
        from ._main import _Abort
    
        config: dict[str, bool | int | float | str | model.Secret] = kwargs.copy()
        try:
            fields = set(_juju_fields(cls))
        except ValueError:
            fields = None
        for key, value in self.config.items():
            attr = key.replace('-', '_')
            if fields is not None and attr not in fields:
                continue
            option_type = self.meta.config.get(key)
            # Convert secret IDs to secret objects. We create the object rather
            # that using model.get_secret so that it's entirely lazy, in the
            # same way that SecretEvent.secret is.
            if option_type and option_type.type == 'secret':
                assert isinstance(value, str)  # Juju will have made sure of this.
                value = model.Secret(
                    backend=self.model._backend,
                    id=value,
                    _secret_set_cache=self.model._cache._secret_set_cache,
                )
            config[attr] = value
        try:
            return cls(*args, **config)
        except ValueError as e:
            if errors == 'raise':
                raise
            # We exit with a zero code because we don't want Juju to retry
            # (the config needs to be fixed by the Juju user), and we don't
            # want the status we just set to be overridden by an error
            # status.
            self.unit.status = model.BlockedStatus(f'Invalid config: {e}')
>           raise _Abort(0) from e
E           ops._main._Abort

--
FAILED tests/unit_harness/test_core.py::TestCore::test_config_changed_when_config_invalid
!!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
======================== 1 failed, 6 warnings in 0.14s =========================
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 6m 56s</sub>

### ✅ `bash`

**Check how Harness handles _Abort**

$ python3 -c "from ops._private.harness import Harness; import inspect; src = inspect.getsource(Harness._run_action); print(src)" 2>/dev/null | head -30
grep -n "_Abort" /home/ubuntu/.local/lib/python3.12/site-packages/ops/_private/harness.py | head -10

```

<exited with exit code 0>
```


---

<sub>⏱️ 7m 2s</sub>

### ✅ `bash`

**Check _Abort handling in harness**

$ grep -n "_Abort\|update_config" /home/ubuntu/.local/lib/python3.12/site-packages/ops/_private/harness.py | head -20

<details>
<summary>9 lines</summary>

```
243:            harness.update_config({'log_level': 'warn'})
263:            harness.update_config({'some': 'config'})
469:            harness.update_config({'initial': 'config'})
778:                harness.update_config(unset=['foo', 'bar'])
1447:    def _update_config(
1484:    def update_config(
1505:        self._update_config(key_values, unset)
1723:                harness.update_config({'mysec': secret_id})
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 7m 6s</sub>

### ✅ `bash`

**Check update_config implementation**

$ sed -n '1484,1520p' /home/ubuntu/.local/lib/python3.12/site-packages/ops/_private/harness.py

<details>
<summary>31 lines</summary>

```
def update_config(
        self,
        key_values: Mapping[str, str | int | float | bool] | None = None,
        unset: Iterable[str] = (),
    ) -> None:
        """Update the config as seen by the charm.

        This will trigger a `config_changed` event.

        Note that the ``key_values`` mapping will only add or update configuration items.
        To remove existing ones, see the ``unset`` parameter.

        Args:
            key_values: A Mapping of key:value pairs to update in config.
            unset: An iterable of keys to remove from config.
                This sets the value to the default if defined,
                otherwise removes the key altogether.

        Raises:
            ValueError: if the key is not present in the config.
        """
        self._update_config(key_values, unset)
        if self._charm is None or not self._hooks_enabled:
            return
        self._charm.on.config_changed.emit()

    def set_leader(self, is_leader: bool = True) -> None:
        """Set whether this unit is the leader or not.

        If this charm becomes a leader then `leader_elected` will be triggered.  If :meth:`begin`
        has already been called, then the charm's peer relation should usually be added *prior* to
        calling this method (with :meth:`add_relation`) to properly initialise and make
        available relation data that leader elected hooks may want to access.

        Args:
            is_leader: Whether this unit is the leader.
        """
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 7m 41s</sub>

### ✅ `bash`

**Check _Abort base classes**

$ python3 -c "from ops._main import _Abort; print(_Abort.__bases__)"

```
(<class 'Exception'>,)
<exited with exit code 0>
```


---

<sub>⏱️ 7m 56s</sub>

### ✅ `bash`

**Test the error message format**

$ python3 -c "
from pydantic import BaseModel, validator
from urllib.parse import urlparse

class C(BaseModel):
    site_url: str = ''
    @validator('site_url')
    @classmethod
    def validate_site_url(cls, v):
        if v and not urlparse(v).hostname:
            raise ValueError('Configuration option site_url is not valid')
        return v

try:
    C(site_url='example.local')
except Exception as e:
    print(repr(str(e)))
"

```
'1 validation error for C\nsite_url\n  Configuration option site_url is not valid (type=value_error)'
<exited with exit code 0>
```


---

<sub>⏱️ 8m 20s</sub>

### 💬 Copilot

The `_Abort` exception from `errors='blocked'` isn't caught by the deprecated Harness. I'll use `errors='raise'` with manual error handling in `_on_config_changed` to keep the original clean message format:

---

<sub>⏱️ 8m 20s</sub>

### ✅ `edit`

**/tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/src/charm.py**

/tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/src/charm.py

```
File /tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/src/charm.py updated with changes.
```


---

<sub>⏱️ 8m 27s</sub>

### ✅ `bash`

**Run tests**

$ cd /tmp/ops-upgrade-experiment/indico-operator__config-classes__C2 && python3 -m pytest tests/unit_harness/test_core.py -x -q 2>&1 | tail -20

<details>
<summary>18 lines</summary>

```
tests/unit_harness/test_core.py::TestCore::test_all_pebble_services_ready
tests/unit_harness/test_core.py::TestCore::test_config_changed
tests/unit_harness/test_core.py::TestCore::test_config_changed_when_config_invalid
tests/unit_harness/test_core.py::TestCore::test_config_changed_when_pebble_not_ready
tests/unit_harness/test_core.py::TestCore::test_config_changed_when_saml_groups_plugin_installed
tests/unit_harness/test_core.py::TestCore::test_config_changed_with_external_resources
tests/unit_harness/test_core.py::TestCore::test_indico_nginx_pebble_ready
  /tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/lib/charms/data_platform_libs/v0/data_interfaces.py:1160: DeprecationWarning: JujuVersion.from_environ() is deprecated, use self.model.juju_version instead
    self._jujuversion = JujuVersion.from_environ()

tests/unit_harness/test_core.py: 33 warnings
  /tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/src/charm.py:886: DeprecationWarning: JujuVersion.from_environ() is deprecated, use self.model.juju_version instead
    juju_version = JujuVersion.from_environ()

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ============================
FAILED tests/unit_harness/test_core.py::TestCore::test_missing_relations - As...
!!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
1 failed, 12 passed, 53 warnings in 0.29s
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 8m 33s</sub>

### ✅ `bash`

**Get failing test details**

$ cd /tmp/ops-upgrade-experiment/indico-operator__config-classes__C2 && python3 -m pytest tests/unit_harness/test_core.py::TestCore::test_missing_relations -x -q 2>&1 | grep "AssertionError\|assert\|Error" | head -10

```
assert: the charm is in waiting status until all relations have been set
>       self.assertEqual(
E       AssertionError: BlockedStatus('Configuration option site_url is not valid') != WaitingStatus('Waiting for redis-broker availability')
tests/unit_harness/test_core.py:130: AssertionError
<exited with exit code 0>
```


---

<sub>⏱️ 8m 38s</sub>

### ✅ `view`

**/tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/tests/unit_harness/test_core.py**

/tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/tests/unit_harness/test_core.py (lines 115-145)

<details>
<summary>31 lines</summary>

```
115.             "redis-cache",
116.             unit_data={"hostname": cache_host, "port": cache_port},
117.         )
118.         broker_url = self.harness.charm._get_redis_url("redis-broker")
119.         cache_url = self.harness.charm._get_redis_url("redis-cache")
120.         self.assertEqual(broker_url, f"redis://{broker_host}:{broker_port}")
121.         self.assertEqual(cache_url, f"redis://{cache_host}:{cache_port}")
122. 
123.     def test_missing_relations(self):
124.         """
125.         arrange: charm created
126.         act: trigger a configuration update
127.         assert: the charm is in waiting status until all relations have been set
128.         """
129.         self.harness.update_config({"site_url": "foo"})
130.         self.assertEqual(
131.             self.harness.model.unit.status,
132.             ops.WaitingStatus("Waiting for redis-broker availability"),
133.         )
134.         self.harness.add_relation(
135.             "redis-broker",
136.             "redis-broker",
137.             unit_data={"something": "just to trigger rel-changed event"},
138.         )
139.         self.assertEqual(
140.             self.harness.model.unit.status,
141.             ops.WaitingStatus("Waiting for redis-cache availability"),
142.         )
143.         self.harness.add_relation(
144.             "redis-cache",
145.             "redis-cache",
```

</details>


---

<sub>⏱️ 8m 44s</sub>

### ✅ `bash`

**Test urlparse behavior with 'foo'**

$ python3 -c "from urllib.parse import urlparse; print(urlparse('foo').hostname)"

```
None
<exited with exit code 0>
```


---

<sub>⏱️ 9m 5s</sub>

### 💬 Copilot

The old code checked relations BEFORE validating config. I need to restore that order - validate config only after relations and pebble are ready:

---

<sub>⏱️ 9m 5s</sub>

### ✅ `edit`

**/tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/src/charm.py**

/tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/src/charm.py

```
File /tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/src/charm.py updated with changes.
```


---

<sub>⏱️ 9m 11s</sub>

### ✅ `bash`

**Run tests**

$ cd /tmp/ops-upgrade-experiment/indico-operator__config-classes__C2 && python3 -m pytest tests/unit_harness/test_core.py -x -q 2>&1 | tail -20

<details>
<summary>18 lines</summary>

```
tests/unit_harness/test_core.py: 23 warnings
  /tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/tests/unit_harness/test_base.py:21: PendingDeprecationWarning: Harness is deprecated. For the recommended approach, see: https://documentation.ubuntu.com/ops/2.x/howto/write-unit-tests-for-a-charm.html
    self.harness = Harness(IndicoOperatorCharm)

tests/unit_harness/test_core.py::TestCore::test_all_pebble_services_ready
tests/unit_harness/test_core.py::TestCore::test_config_changed
tests/unit_harness/test_core.py::TestCore::test_config_changed_when_config_invalid
tests/unit_harness/test_core.py::TestCore::test_config_changed_when_pebble_not_ready
tests/unit_harness/test_core.py::TestCore::test_config_changed_when_saml_groups_plugin_installed
tests/unit_harness/test_core.py::TestCore::test_config_changed_with_external_resources
tests/unit_harness/test_core.py::TestCore::test_indico_nginx_pebble_ready
  /tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/lib/charms/data_platform_libs/v0/data_interfaces.py:1160: DeprecationWarning: JujuVersion.from_environ() is deprecated, use self.model.juju_version instead
    self._jujuversion = JujuVersion.from_environ()

tests/unit_harness/test_core.py: 33 warnings
  /tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/src/charm.py:886: DeprecationWarning: JujuVersion.from_environ() is deprecated, use self.model.juju_version instead
    juju_version = JujuVersion.from_environ()

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
22 passed, 64 warnings in 0.36s
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 9m 17s</sub>

### 💬 Copilot

All 22 tests pass. Let me also run the full test suite to make sure nothing else is broken:

---

<sub>⏱️ 9m 18s</sub>

### ✅ `bash`

**Run all unit tests**

$ cd /tmp/ops-upgrade-experiment/indico-operator__config-classes__C2 && python3 -m pytest tests/unit_harness/ tests/unit/ -q 2>&1 | tail -15

<details>
<summary>13 lines</summary>

```
/tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/tests/unit_harness/test_s3_observer.py:78: PendingDeprecationWarning: Harness is deprecated. For the recommended approach, see: https://documentation.ubuntu.com/ops/2.x/howto/write-unit-tests-for-a-charm.html
    harness = Harness(ObservedCharm, meta=REQUIRER_METADATA)

tests/unit_harness/test_saml_observer.py::test_saml_related_emits_config_changed_event_and_updates_charm_state
  /tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/tests/unit_harness/test_saml_observer.py:66: PendingDeprecationWarning: Harness is deprecated. For the recommended approach, see: https://documentation.ubuntu.com/ops/2.x/howto/write-unit-tests-for-a-charm.html
    harness = Harness(ObservedCharm, meta=REQUIRER_METADATA)

tests/unit_harness/test_smtp_observer.py::test_smtp_related_emits_config_changed_event_and_updates_charm_state
  /tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/tests/unit_harness/test_smtp_observer.py:63: PendingDeprecationWarning: Harness is deprecated. For the recommended approach, see: https://documentation.ubuntu.com/ops/2.x/howto/write-unit-tests-for-a-charm.html
    harness = Harness(ObservedCharm, meta=REQUIRER_METADATA)

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ============================
FAILED tests/unit_harness/test_actions.py::TestActions::test_refresh_external_resources_when_customization_and_plugins_set
1 failed, 41 passed, 97 warnings in 0.48s
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 9m 25s</sub>

### ✅ `bash`

**Get failing test details**

$ cd /tmp/ops-upgrade-experiment/indico-operator__config-classes__C2 && python3 -m pytest tests/unit_harness/test_actions.py::TestActions::test_refresh_external_resources_when_customization_and_plugins_set -x -q 2>&1 | grep "AssertionError\|Error\|assert" | head -10

<details>
<summary>11 lines</summary>

```
assert: the customization sources are pulled and the plugins upgraded
        with self.assertLogs(level="INFO") as logger:
>           mock_exec.assert_any_call(
    def assert_any_call(self, /, *args, **kwargs):
        """assert the mock has been called with the specified arguments.
        The assert passes if the mock has *ever* been called, unlike
        `assert_called_with` and `assert_called_once_with` that only pass if
>           raise AssertionError(
E           AssertionError: exec(['git', 'pull'], working_dir='/srv/indico/custom', user='indico', environment={}) call not found
/usr/lib/python3.12/unittest/mock.py:1015: AssertionError
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 9m 31s</sub>

### ✅ `bash`

**Find the test**

$ grep -n "test_refresh_external_resources_when_customization_and_plugins_set" /tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/tests/unit_harness/test_actions.py

```
25:    def test_refresh_external_resources_when_customization_and_plugins_set(
<exited with exit code 0>
```


---

<sub>⏱️ 9m 30s</sub>

### ✅ `view`

**/tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/tests/unit_harness/test_actions.py**

/tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/tests/unit_harness/test_actions.py (lines 1-50)

<details>
<summary>50 lines</summary>

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
```

</details>


---

<sub>⏱️ 10m 9s</sub>

### 💬 Copilot

The issue is that `typed_config` is a stale cached attribute in the Harness. I'll make it a `@property` so it always reads the current config:

---

<sub>⏱️ 10m 9s</sub>

### ✅ `view`

**/tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/src/charm.py**

/tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/src/charm.py (lines 65-80)

<details>
<summary>16 lines</summary>

```
65.     def __init__(self, *args):
66.         """Construct.
67. 
68.         Args:
69.             args: Arguments passed to the CharmBase parent constructor.
70.         """
71.         super().__init__(*args)
72.         self.typed_config = self.load_config(CharmConfig, errors="blocked")
73.         self.database = DatabaseObserver(self)
74.         self.s3 = S3Observer(self)
75.         self.smtp = SmtpObserver(self)
76.         self.saml = SamlObserver(self)
77.         try:
78.             self.state = State.from_charm(
79.                 self,
80.                 s3_relation_data=self.s3.s3.get_s3_connection_info(),
```

</details>


---

<sub>⏱️ 10m 15s</sub>

### ✅ `edit`

**/tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/src/charm.py**

/tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/src/charm.py

```
File /tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/src/charm.py updated with changes.
```


---

<sub>⏱️ 10m 20s</sub>

### 💬 Copilot

Now find where the `IndicoOperatorCharm` class definition starts and add the property:

---

<sub>⏱️ 10m 20s</sub>

### ✅ `view`

**/tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/src/charm.py**

/tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/src/charm.py (lines 56-70)

<details>
<summary>15 lines</summary>

```
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
```

</details>


---

<sub>⏱️ 10m 26s</sub>

### ✅ `edit`

**/tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/src/charm.py**

/tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/src/charm.py

```
File /tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/src/charm.py updated with changes.
```


---

<sub>⏱️ 10m 32s</sub>

### 💬 Copilot

Now update `_on_config_changed` to validate by calling `self.typed_config` in a try/except (no longer assigning to it since it's a property):

---

<sub>⏱️ 10m 32s</sub>

### ✅ `edit`

**/tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/src/charm.py**

/tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/src/charm.py

```
File /tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/src/charm.py updated with changes.
```


---

<sub>⏱️ 10m 39s</sub>

### ✅ `bash`

**Run all tests**

$ cd /tmp/ops-upgrade-experiment/indico-operator__config-classes__C2 && python3 -m pytest tests/unit_harness/ tests/unit/ -q 2>&1 | tail -10

<details>
<summary>9 lines</summary>

```
tests/unit_harness/test_saml_observer.py::test_saml_related_emits_config_changed_event_and_updates_charm_state
  /tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/tests/unit_harness/test_saml_observer.py:66: PendingDeprecationWarning: Harness is deprecated. For the recommended approach, see: https://documentation.ubuntu.com/ops/2.x/howto/write-unit-tests-for-a-charm.html
    harness = Harness(ObservedCharm, meta=REQUIRER_METADATA)

tests/unit_harness/test_smtp_observer.py::test_smtp_related_emits_config_changed_event_and_updates_charm_state
  /tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/tests/unit_harness/test_smtp_observer.py:63: PendingDeprecationWarning: Harness is deprecated. For the recommended approach, see: https://documentation.ubuntu.com/ops/2.x/howto/write-unit-tests-for-a-charm.html
    harness = Harness(ObservedCharm, meta=REQUIRER_METADATA)

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
42 passed, 97 warnings in 0.45s
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 10m 46s</sub>

### 💬 Copilot

All 42 tests pass. Let me do a final check to ensure no `self.config[` accesses remain and verify the key changes:

---

<sub>⏱️ 10m 47s</sub>

### ✅ `bash`

**Verify no remaining raw config accesses**

$ grep -n "self\.config\[" /tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/src/charm.py && echo "FOUND" || echo "NONE FOUND - clean!"

```
NONE FOUND - clean!
<exited with exit code 0>
```


---

<sub>⏱️ 10m 47s</sub>

### ✅ `bash`

**Verify new typed config usage**

$ grep -n "typed_config\|CharmConfig\|load_config" /tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/src/charm.py

<details>
<summary>26 lines</summary>

```
35:from state import CharmConfig, CharmConfigInvalidError, ProxyConfig, State
66:    def typed_config(self) -> CharmConfig:
72:        return self.load_config(CharmConfig)
92:        except CharmConfigInvalidError as exc:
170:        site_url = self.typed_config.site_url
181:        site_url = self.typed_config.site_url
190:        site_url = self.typed_config.site_url
232:                self.typed_config.external_plugins.split(",")
233:                if self.typed_config.external_plugins
561:            "CUSTOMIZATION_DEBUG": self.typed_config.customization_debug,
562:            "ENABLE_ROOMBOOKING": self.typed_config.enable_roombooking,
567:            "INDICO_NO_REPLY_EMAIL": self.typed_config.indico_no_reply_email,
568:            "INDICO_PUBLIC_SUPPORT_EMAIL": self.typed_config.indico_public_support_email,
569:            "INDICO_SUPPORT_EMAIL": self.typed_config.indico_support_email,
608:                    "entityId": self.typed_config.site_url,
689:            _ = self.typed_config
783:        if current_remote_url != self.typed_config.customization_sources_url:
793:            if self.typed_config.customization_sources_url:
796:                    self.typed_config.customization_sources_url,
803:                        self.typed_config.customization_sources_url,
821:            if self.typed_config.customization_sources_url:
822:                logging.debug("Pulling changes from %s", self.typed_config.customization_sources_url)
830:            if self.typed_config.external_plugins:
831:                logging.debug("Upgrading external plugins %s", self.typed_config.external_plugins)
832:                plugins = self.typed_config.external_plugins.split(",")
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 10m 52s</sub>

### ✅ `bash`

**Verify CharmConfig in state.py**

$ grep -n "class CharmConfig\|typed_config\|CharmConfig" /tmp/ops-upgrade-experiment/indico-operator__config-classes__C2/src/state.py | head -10

<details>
<summary>6 lines</summary>

```
26:class CharmConfigInvalidError(CharmStateBaseError):
34:        """Initialize a new instance of the CharmConfigInvalidError exception.
42:class CharmConfig(BaseModel):  # pylint: disable=too-few-public-methods
231:            CharmConfigInvalidError: if invalid state values were encountered.
276:            raise CharmConfigInvalidError("Invalid model proxy configuration.") from exc
<exited with exit code 0>
```

</details>


---

<sub>⏱️ 11m 1s</sub>

### ❌ `store_memory`

<details>
<summary>Arguments</summary>

```json
{
  "subject": "config access pattern",
  "fact": "Charm uses CharmConfig (Pydantic model in state.py) with self.typed_config property (calls load_config(CharmConfig)) instead of raw self.config[] dict access. _on_config_changed validates with try/except ValueError.",
  "citations": "src/charm.py:66-72, src/state.py:42-84",
  "reason": "Future changes to charm config or validators should know typed config is a property via load_config(CharmConfig) rather than a cached attribute, and that validation errors are handled manually in _on_config_changed to extract the first error message from pydantic ValidationError.",
  "category": "file_specific"
}
```

</details>

```
Unable to store memory. You can continue with your task without storing this information.
```


---

<sub>⏱️ 11m 10s</sub>

### ✅ `task_complete`

**Added `CharmConfig` Pydantic model to `src/state.py` with all 8 charm config options (customization_debug, customization_sources_url, enable_roombooking, external_plugins, indico_no_reply_email, indico_public_support_email, indico_support_email, site_url) including a `@validator` for `site_url` that validates it has a valid hostname when non-empty.

Updated `src/charm.py` to:
- Import `CharmConfig` from `state`
- Add `typed_config` as a `@property` that calls `self.load_config(CharmConfig)` — using a property (rather than a cached attribute) ensures the config is always fresh regardless of whether the charm is running in the real ops framework or the deprecated Harness
- Replace all `self.config[...]` dict accesses with `self.typed_config.<field>` attribute access
- Replace the manual `_is_configuration_valid()` method with Pydantic model validation in `_on_config_changed`, which catches `ValueError`/`ValidationError` and sets `BlockedStatus` with the validation message
- Remove the now-unused `_is_configuration_valid` method and `Tuple` import

All 42 existing tests pass.**

<details>
<summary>Arguments</summary>

```json
{
  "summary": "Added `CharmConfig` Pydantic model to `src/state.py` with all 8 charm config options (customization_debug, customization_sources_url, enable_roombooking, external_plugins, indico_no_reply_email, indico_public_support_email, indico_support_email, site_url) including a `@validator` for `site_url` that validates it has a valid hostname when non-empty.\n\nUpdated `src/charm.py` to:\n- Import `CharmConfig` from `state`\n- Add `typed_config` as a `@property` that calls `self.load_config(CharmConfig)` — using a property (rather than a cached attribute) ensures the config is always fresh regardless of whether the charm is running in the real ops framework or the deprecated Harness\n- Replace all `self.config[...]` dict accesses with `self.typed_config.<field>` attribute access\n- Replace the manual `_is_configuration_valid()` method with Pydantic model validation in `_on_config_changed`, which catches `ValueError`/`ValidationError` and sets `BlockedStatus` with the validation message\n- Remove the now-unused `_is_configuration_valid` method and `Tuple` import\n\nAll 42 existing tests pass."
}
```

</details>

<details>
<summary>8 lines</summary>

```
Added `CharmConfig` Pydantic model to `src/state.py` with all 8 charm config options (customization_debug, customization_sources_url, enable_roombooking, external_plugins, indico_no_reply_email, indico_public_support_email, indico_support_email, site_url) including a `@validator` for `site_url` that validates it has a valid hostname when non-empty.

Updated `src/charm.py` to:
- Import `CharmConfig` from `state`
- Add `typed_config` as a `@property` that calls `self.load_config(CharmConfig)` — using a property (rather than a cached attribute) ensures the config is always fresh regardless of whether the charm is running in the real ops framework or the deprecated Harness
- Replace all `self.config[...]` dict accesses with `self.typed_config.<field>` attribute access
- Replace the manual `_is_configuration_valid()` method with Pydantic model validation in `_on_config_changed`, which catches `ValueError`/`ValidationError` and sets `BlockedStatus` with the validation message
- Remove the now-unused `_is_configuration_valid` method and `Tuple` import

All 42 existing tests pass.
```

</details>


---

<sub>⏱️ 11m 15s</sub>

### ℹ️ Info

Response was interrupted due to a server error. Retrying...

---

<sub>⏱️ 11m 21s</sub>

### ℹ️ Info

Response was interrupted due to a server error. Retrying...

---

<sub>⏱️ 11m 26s</sub>

### ℹ️ Info

Response was interrupted due to a server error. Retrying...

---

<sub>⏱️ 11m 31s</sub>

### ℹ️ Info

Response was interrupted due to a server error. Retrying...

---

<sub>⏱️ 11m 36s</sub>

### ℹ️ Info

Response was interrupted due to a server error. Retrying...

---

<sub>⏱️ 11m 41s</sub>

### ❌ Error

Execution failed: Error: Failed to get response from the AI model; retried 5 times (total retry wait time: 5.979855583728451 seconds) Last error: Unknown error

---

<sub>Generated by [GitHub Copilot CLI](https://github.com/features/copilot/cli)</sub>
