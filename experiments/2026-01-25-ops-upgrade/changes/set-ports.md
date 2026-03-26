# set-ports

## Version
ops 2.7.0

## Type
Feature

## Summary
New declarative `Unit.set_ports()` API replaces the imperative `open_port()` / `close_port()` pattern. Instead of tracking which ports to open and close individually, charms declare the full set of desired ports and ops handles the diff.

## Before
```python
import ops

class MyCharm(ops.CharmBase):
    def _on_config_changed(self, event: ops.ConfigChangedEvent):
        # Imperative: must track what's open and manually open/close
        port = int(self.config["port"])
        # Close old port if it changed
        for opened in self.unit.opened_ports():
            if opened.port != port:
                self.unit.close_port("tcp", opened.port)
        self.unit.open_port("tcp", port)
```

## After
```python
import ops

class MyCharm(ops.CharmBase):
    def _on_config_changed(self, event: ops.ConfigChangedEvent):
        # Declarative: state the desired ports, ops handles the rest
        port = int(self.config["port"])
        self.unit.set_ports(ops.Port("tcp", port))
```

## Why Upgrade
- **Simpler**: no need to track currently-open ports and compute the diff manually.
- **Idempotent**: calling `set_ports()` with the same ports is a no-op.
- **Correct by default**: avoids bugs where ports leak open after config changes or relation departures.
- **Declarative style**: aligns with the general direction of ops towards declarative charm patterns.

## Complexity
Moderate

## Detection
Search for `open_port(` or `close_port(` in charm code. Charms that manage multiple ports or change ports dynamically benefit most.

## Exemplar Charms
- [canonical/catalogue-k8s-operator](https://github.com/canonical/catalogue-k8s-operator) (src/charm.py) — Simplest pattern: `self.unit.set_ports(80)` in `__init__`. Single literal port.
- [canonical/sdcore-amf-operator](https://github.com/canonical/sdcore-amf-operator) (src/charm.py) — Multiple named constant ports: `self.unit.set_ports(PROMETHEUS_PORT, SBI_PORT, SCTP_GRPC_PORT)`.
- [canonical/sdcore-smf-operator](https://github.com/canonical/sdcore-smf-operator) (src/charm.py) — Mixed protocols: bare integers for TCP plus explicit `Port(port=PFCP_PORT, protocol="udp")` for UDP. Most advanced pattern.

**Notable**: adoption is strong — many charms (pgbouncer, karma-k8s, cos-configuration-k8s, pollen, multiple sdcore charms) have adopted `set_ports()`. This is the best-adopted feature in the round 2 catalogue.

## Pitfalls
- `set_ports()` replaces *all* open ports — if you call it with a subset, ports not in the list are closed. This is intentional but can surprise charms that open ports in multiple places.
- `OpenPort` was renamed to `Port` in the same release. Both work, but `Port` is the canonical name.
- Charms that open ports across multiple event handlers need to consolidate the logic or maintain a set of desired ports.
