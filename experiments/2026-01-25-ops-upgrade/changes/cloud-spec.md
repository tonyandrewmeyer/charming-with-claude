# cloud-spec

## Version
ops 2.12.0

## Type
Feature

## Summary
`Model.get_cloud_spec()` introduced, allowing charms to retrieve cloud credentials and endpoint information using Juju's `credential-get` hook command. Charms that need cloud provider details (e.g. for provisioning resources) no longer need to work around the lack of this API.

## Before
```python
import json
import subprocess

import ops


class MyCharm(ops.CharmBase):
    def _get_cloud_credentials(self):
        # Had to shell out to get cloud credentials
        try:
            result = subprocess.run(
                ["credential-get", "--format", "json"],
                capture_output=True, text=True, check=True,
            )
            return json.loads(result.stdout)
        except subprocess.CalledProcessError:
            return None
```

## After
```python
import ops


class MyCharm(ops.CharmBase):
    def _get_cloud_credentials(self):
        try:
            cloud_spec = self.model.get_cloud_spec()
            return cloud_spec
        except ops.ModelError:
            return None
```

## Why Upgrade
- **Clean API**: no need to shell out to `credential-get`.
- **Typed**: returns a `CloudSpec` object with typed fields (`type`, `name`, `credential`, `endpoint`, etc.).
- **Testable**: can be mocked cleanly in unit tests.

## Complexity
Trivial — a direct API replacement for charms already using `credential-get`.

## Detection
Search for `credential-get` subprocess calls, or for charms that interact with cloud provider APIs and might benefit from cloud credential access.

## Exemplar Charms
- Relatively niche — only charms that need cloud-level credentials use this.
- Search for `get_cloud_spec()` across canonical/ repos.

## Pitfalls
- Only works on cloud models (not local/LXD) — charms must handle the `ModelError` when credentials aren't available.
- The trust configuration must be set for the charm to access cloud credentials.
- Not all cloud providers expose the same fields in `CloudSpec`.
