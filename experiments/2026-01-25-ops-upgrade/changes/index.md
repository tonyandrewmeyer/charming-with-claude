# Ops Changes Catalogue

*Catalogued from the [ops CHANGES.md](https://github.com/canonical/operator/blob/main/CHANGES.md) covering releases from ops 2.23.0 (June 2025) through ops 3.6.0 (February 2026). Since ops-scenario and ops-tracing have been merged into the main ops repository (as `ops[testing]` and `ops[tracing]` respectively), all changes are tracked via the single ops changelog.*

## Summary

| Change ID | Version | Type | Complexity | Domain | Summary |
|-----------|---------|------|------------|--------|---------|
| [config-classes](config-classes.md) | 2.23.0 | Feature | Moderate | Core | Config options as Python dataclasses or Pydantic models via `load_config()` |
| [action-classes](action-classes.md) | 2.23.0 | Feature | Moderate | Core | Action parameters as Python dataclasses or Pydantic models via `load_params()` |
| [relation-data-classes](relation-data-classes.md) | 2.23.0 | Feature | Significant | Core | Relation data as typed objects via `Relation.save()` / `Relation.load()` |
| [check-info-successes](check-info-successes.md) | 2.23.0 | Feature | Trivial | Core | `CheckInfo.successes` field and `.has_run` property for Pebble health checks |
| [layer-from-rockcraft](layer-from-rockcraft.md) | 2.23.0 | Feature | Moderate | Testing | `testing.layer_from_rockcraft()` generates Pebble Layer from rockcraft.yaml |
| [testing-context-state](testing-context-state.md) | 2.23.0 | Feature | Moderate | Testing | Create a `testing.State` from the charm's metadata via the Context |
| [testing-trace-data](testing-trace-data.md) | 2.23.0 | Feature | Moderate | Testing | Expose trace data in `ops.testing` for verifying tracing instrumentation |
| [testing-app-name-unit-id](testing-app-name-unit-id.md) | 3.1.0 | Feature | Trivial | Testing | `app_name` and `unit_id` attributes on `testing.Context` |
| [security-event-logging](security-event-logging.md) | 3.2.0 | Feature (internal) | Trivial | Core | Automatic structured security audit event logging (no charm changes) |
| [opentelemetry-log-target](opentelemetry-log-target.md) | 3.2.0 | Feature | Moderate | Core | OpenTelemetry log target type for Pebble layers |
| [juju-context](juju-context.md) | 3.3.0 | Feature | Trivial–Moderate | Core | `ops.JujuContext` for typed access to the Juju hook execution context |
| [hook-commands-api](hook-commands-api.md) | 3.4.0 | Feature | Trivial | Core | Low-level `ops.hookcmds` module for direct hook command access |
| [pebble-purepath](pebble-purepath.md) | 3.4.0 | Improvement | Trivial | Core | PebbleClient file methods accept `pathlib.PurePath` |
| [deferred-events-logging](deferred-events-logging.md) | 3.4.0 | Improvement | Trivial | Core | Automatic logging of total deferred event count |
| [testing-az-principal](testing-az-principal.md) | 3.4.0 | Feature | Trivial | Testing | Set availability zone and principal unit in `testing.Context` |
| [machine-id-str](machine-id-str.md) | 3.4.0 | Breaking change | Trivial | Core | `JujuContext.machine_id` changed from `int` to `str` |
| [deprecate-charm-spec](deprecate-charm-spec.md) | 3.5.0 | Deprecation | Trivial | Testing | `testing.Context.charm_spec` deprecated |
| [testing-exception-wrapping](testing-exception-wrapping.md) | 3.5.0 | Feature | Trivial | Testing | `SCENARIO_BARE_CHARM_ERRORS` env var for bare exception propagation in tests |

## Change Distribution

### By type
- **Features**: 13
- **Improvements**: 2
- **Breaking changes**: 1
- **Deprecations**: 1

### By domain
- **Core ops**: 10 (charm code and runtime)
- **Testing (ops[testing])**: 7

### By complexity
- **Trivial**: 10 (simple adoption, often one-line changes, or no charm changes needed)
- **Moderate**: 6 (requires understanding the new API and updating multiple locations)
- **Significant**: 1 (relation data classes — requires interface compatibility analysis)

## Most Impactful for Charm Upgrades

The following changes are most likely to produce meaningful improvements when applied to existing charms (i.e. they require charm code changes and improve code quality):

1. **[config-classes](config-classes.md)** — nearly every charm has config; this is the most widely applicable.
2. **[action-classes](action-classes.md)** — most charms with actions will benefit.
3. **[relation-data-classes](relation-data-classes.md)** — high impact but requires care with interface compatibility.
4. **[layer-from-rockcraft](layer-from-rockcraft.md)** — significant test maintenance improvement for K8s charms.
5. **[testing-exception-wrapping](testing-exception-wrapping.md)** — simple win for any charm with unit tests.

Note: [security-event-logging](security-event-logging.md) and [deferred-events-logging](deferred-events-logging.md) are valuable but require no charm code changes — they activate automatically on upgrade.

## Source

* [ops CHANGES.md](https://github.com/canonical/operator/blob/main/CHANGES.md) — single changelog covering ops core, ops[testing], and ops[tracing]

All files in the `changes` folder were initially generated by Claude, but have been manually reviewed and tweaked by me.
