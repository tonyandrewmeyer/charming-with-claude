# fix(snap): handle revision as str (#92)

**Repository**: operator-libs-linux
**Commit**: [1a09b160](https://github.com/canonical/operator-libs-linux/commit/1a09b1602f60a73d3515e93143ea7c37e41abb09)
**Date**: 2023-05-17

## Classification

| Field | Value |
|-------|-------|
| Bug Area | snap |
| Bug Type | type-error |
| Severity | high |
| Fix Category | source-fix |

## Summary

Snap revision was handled as int but should be string, causing API breakage; bumped to v2

## Commit Message

Snap revisions can be strings and should be handled as strings

## Changed Files

- D	lib/charms/operator_libs_linux/v1/snap.py
- A	lib/charms/operator_libs_linux/v2/snap.py
- M	tests/integration/test_snap.py
- M	tests/unit/test_snap.py

## Diff

```diff
diff --git a/lib/charms/operator_libs_linux/v1/snap.py b/lib/charms/operator_libs_linux/v1/snap.py
deleted file mode 100644
index eacda12..0000000
--- a/lib/charms/operator_libs_linux/v1/snap.py
+++ /dev/null
@@ -1,1065 +0,0 @@
-# Copyright 2021 Canonical Ltd.
-#
-# Licensed under the Apache License, Version 2.0 (the "License");
-# you may not use this file except in compliance with the License.
-# You may obtain a copy of the License at
-#
-# http://www.apache.org/licenses/LICENSE-2.0
-#
-# Unless required by applicable law or agreed to in writing, software
-# distributed under the License is distributed on an "AS IS" BASIS,
-# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
-# See the License for the specific language governing permissions and
-# limitations under the License.
-
-"""Representations of the system's Snaps, and abstractions around managing them.
-
-The `snap` module provides convenience methods for listing, installing, refreshing, and removing
-Snap packages, in addition to setting and getting configuration options for them.
-
-In the `snap` module, `SnapCache` creates a dict-like mapping of `Snap` objects at when
-instantiated. Installed snaps are fully populated, and available snaps are lazily-loaded upon
-request. This module relies on an installed and running `snapd` daemon to perform operations over
-the `snapd` HTTP API.
-
-`SnapCache` objects can be used to install or modify Snap packages by name in a manner similar to
-using the `snap` command from the commandline.
-
-An example of adding Juju to the system with `SnapCache` and setting a config value:
-
-```python
-try:
-    cache = snap.SnapCache()
-    juju = cache["juju"]
-
-    if not juju.present:
-        juju.ensure(snap.SnapState.Latest, channel="beta")
-        juju.set({"some.key": "value", "some.key2": "value2"})
-except snap.SnapError as e:
-    logger.error("An exception occurred when installing charmcraft. Reason: %s", e.message)
-```
-
-In addition, the `snap` module provides "bare" methods which can act on Snap packages as
-simple function calls. :meth:`add`, :meth:`remove`, and :meth:`ensure` are provided, as
-well as :meth:`add_local` for installing directly from a local `.snap` file. These return
-`Snap` objects.
-
-As an example of installing several Snaps and checking details:
-
-```python
-try:
-    nextcloud, charmcraft = snap.add(["nextcloud", "charmcraft"])
-    if nextcloud.get("mode") != "production":
-        nextcloud.set({"mode": "production"})
-except snap.SnapError as e:
-    logger.error("An exception occurred when installing snaps. Reason: %s" % e.message)
-```
-"""
-
-import http.client
-import json
-import logging
-import os
-import re
-import socket
-import subprocess
-import sys
-import urllib.error
-import urllib.parse
-import urllib.request
-from collections.abc import Mapping
-from datetime import datetime, timedelta, timezone
-from enum import Enum
-from subprocess import CalledProcessError, CompletedProcess
-from typing import Any, Dict, Iterable, List, Optional, Union
-
-logger = logging.getLogger(__name__)
-
-# The unique Charmhub library identifier, never change it
-LIBID = "05394e5893f94f2d90feb7cbe6b633cd"
-
-# Increment this major API version when introducing breaking changes
-LIBAPI = 1
-
-# Increment this PATCH version before using `charmcraft publish-lib` or reset
-# to 0 if you are raising the major API version
-LIBPATCH = 12
-
-
-# Regex to locate 7-bit C1 ANSI sequences
-ansi_filter = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
-
-
-def _cache_init(func):
-    def inner(*args, **kwargs):
-        if _Cache.cache is None:
-            _Cache.cache = SnapCache()
-        return func(*args, **kwargs)
-
-    return inner
-
-
-# recursive hints seems to error out pytest
-JSONType = Union[Dict[str, Any], List[Any], str, int, float]
-
-
-class SnapService:
-    """Data wrapper for snap services."""
-
-    def __init__(
-        self,
-        daemon: Optional[str] = None,
-        daemon_scope: Optional[str] = None,
-        enabled: bool = False,
-        active: bool = False,
-        activators: List[str] = [],
-        **kwargs,
-    ):
-        self.daemon = daemon
-        self.daemon_scope = kwargs.get("daemon-scope", None) or daemon_scope
-        self.enabled = enabled
-        self.active = active
-        self.activators = activators
-
-    def as_dict(self) -> Dict:
-        """Return instance representation as dict."""
-        return {
-            "daemon": self.daemon,
-            "daemon_scope": self.daemon_scope,
-            "enabled": self.enabled,
-            "active": self.active,
-            "activators": self.activators,
-        }
-
-
-class MetaCache(type):
-    """MetaCache class used for initialising the snap cache."""
-
-    @property
-    def cache(cls) -> "SnapCache":
-        """Property for returning the snap cache."""
-        return cls._cache
-
-    @cache.setter
-    def cache(cls, cache: "SnapCache") -> None:
-        """Setter for the snap cache."""
-        cls._cache = cache
-
-    def __getitem__(cls, name) -> "Snap":
-        """Snap cache getter."""
-        return cls._cache[name]
-
-
-class _Cache(object, metaclass=MetaCache):
-    _cache = None
-
-
-class Error(Exception):
-    """Base class of most errors raised by this library."""
-
-    def __repr__(self):
-        """Represent the Error class."""
-        return "<{}.{} {}>".format(type(self).__module__, type(self).__name__, self.args)
-
-    @property
-    def name(self):
-        """Return a string representation of the model plus class."""
-        return "<{}.{}>".format(type(self).__module__, type(self).__name__)
-
-    @property
-    def message(self):
-        """Return the message passed as an argument."""
-        return self.args[0]
-
-
-class SnapAPIError(Error):
-    """Raised when an HTTP API error occurs talking to the Snapd server."""
-
-    def __init__(self, body: Dict, code: int, status: str, message: str):
-        super().__init__(message)  # Makes str(e) return message
-        self.body = body
-        self.code = code
-        self.status = status
-        self._message = message
-
-    def __repr__(self):
-        """Represent the SnapAPIError class."""
-        return "APIError({!r}, {!r}, {!r}, {!r})".format(
-            self.body, self.code, self.status, self._message
-        )
-
-
-class SnapState(Enum):
-    """The state of a snap on the system or in the cache."""
-
-    Present = "present"
-    Absent = "absent"
-    Latest = "latest"
-    Available = "available"
-
-
-class SnapError(Error):
-    """Raised when there's an error running snap control commands."""
-
-
-class SnapNotFoundError(Error):
-    """Raised when a requested snap is not known to the system."""
-
-
-class Snap(object):
-    """Represents a snap package and its properties.
-
-    `Snap` exposes the following properties about a snap:
-      - name: the name of the snap
-      - state: a `SnapState` representation of its install status
-      - channel: "stable", "candidate", "beta", and "edge" are common
-      - revision: a string representing the snap's revision
-      - confinement: "classic" or "strict"
-    """
-
-    def __init__(
-        self,
-        name,
-        state: SnapState,
-        channel: str,
-        revision: int,
-        confinement: str,
-        apps: Optional[List[Dict[str, str]]] = None,
-        cohort: Optional[str] = "",
-    ) -> None:
-        self._name = name
-        self._state = state
-        self._channel = channel
-        self._revision = revision
-        self._confinement = confinement
-        self._cohort = cohort
-        self._apps = apps or []
-        self._snap_client = SnapClient()
-
-    def __eq__(self, other) -> bool:
-        """Equality for comparison."""
-        return isinstance(other, self.__class__) and (
-            self._name,
-            self._revision,
-        ) == (other._name, other._revision)
-
-    def __hash__(self):
-        """Calculate a hash for this snap."""
-        return hash((self._name, self._revision))
-
-    def __repr__(self):
-        """Represent the object such that it can be reconstructed."""
-        return "<{}.{}: {}>".format(self.__module__, self.__class__.__name__, self.__dict__)
-
-    def __str__(self):
-        """Represent the snap object as a string."""
-        return "<{}: {}-{}.{} -- {}>".format(
-            self.__class__.__name__,
-            self._name,
-            self._revision,
-            self._channel,
-            str(self._state),
-        )
-
-    def _snap(self, command: str, optargs: Optional[Iterable[str]] = None) -> str:
-        """Perform a snap operation.
-
-        Args:
-          command: the snap command to execute
-          optargs: an (optional) list of additional arguments to pass,
-            commonly confinement or channel
-
-        Raises:
-          SnapError if there is a problem encountered
-        """
-        optargs = optargs or []
-        _cmd = ["snap", command, self._name, *optargs]
-        try:
-            return subprocess.check_output(_cmd, universal_newlines=True)
-        except CalledProcessError as e:
-            raise SnapError(
-                "Snap: {!r}; command {!r} failed with output = {!r}".format(
-                    self._name, _cmd, e.output
-                )
-            )
-
-    def _snap_daemons(
-        self,
-        command: List[str],
-        services: Optional[List[str]] = None,
-    ) -> CompletedProcess:
-        """Perform snap app commands.
-
-        Args:
-          command: the snap command to execute
-          services: the snap service to execute command on
-
-        Raises:
-          SnapError if there is a problem encountered
-        """
-        if services:
-            # an attempt to keep the command constrained to the snap instance's services
-            services = ["{}.{}".format(self._name, service) for service in services]
-        else:
-        
... [truncated]
```
