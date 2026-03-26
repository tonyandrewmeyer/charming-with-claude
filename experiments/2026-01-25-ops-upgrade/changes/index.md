# Ops Changes Catalogue

*Catalogued from the [ops CHANGES.md](https://github.com/canonical/operator/blob/main/CHANGES.md). Round 1 covered releases from ops 2.23.0 (June 2025) through ops 3.6.0 (February 2026). Round 2 extends coverage back to ops 2.7.0 (September 2023). Since ops-scenario and ops-tracing have been merged into the main ops repository (as `ops[testing]` and `ops[tracing]` respectively), all changes are tracked via the single ops changelog.*

## Round 2 Additions (ops 2.7.0–2.22.0, September 2023–May 2025)

| Change ID | Version | Type | Complexity | Domain | Summary |
|-----------|---------|------|------------|--------|---------|
| [set-ports](set-ports.md) | 2.7.0 | Feature | Moderate | Core | Declarative `Unit.set_ports()` replaces imperative `open_port()` / `close_port()` |
| [pebble-log-targets](pebble-log-targets.md) | 2.9.0 | Feature | Moderate | Core | Log target support in Pebble layers for forwarding to Loki |
| [action-testing](action-testing.md) | 2.9.0 | Feature | Moderate | Testing | `Harness.run_action()` / `ActionOutput` / `ActionFailed` testing API |
| [pebble-notices](pebble-notices.md) | 2.10.0 | Feature | Moderate | Core | `PebbleCustomNoticeEvent` for event-driven workload communication |
| [relation-active](relation-active.md) | 2.10.0 | Feature / behaviour change | Trivial–Moderate | Core | `Relation.active` property; inactive relations excluded from `Model.relations` |
| [non-deferrable-lifecycle](non-deferrable-lifecycle.md) | 2.11.0 | Breaking change | Trivial–Moderate | Core | `StopEvent`, `RemoveEvent`, and all `LifecycleEvent`s now non-deferrable |
| [cloud-spec](cloud-spec.md) | 2.12.0 | Feature | Trivial | Core | `Model.get_cloud_spec()` for cloud credentials and endpoint info |
| [pebble-check-events](pebble-check-events.md) | 2.15.0 | Feature | Moderate | Core | `pebble-check-failed` and `pebble-check-recovered` events |
| [ops-testing-migration](ops-testing-migration.md) | 2.17.0 | Feature (major) | Significant | Testing | `ops[testing]` extras: Harness → Scenario migration path |
| [pebble-check-control](pebble-check-control.md) | 2.19.0 | Feature | Trivial | Core | `start_checks()` / `stop_checks()` for programmatic health check control |
| [ops-tracing-adoption](ops-tracing-adoption.md) | 2.21.0 | Feature (major) | Moderate | Core | `ops[tracing]` first-party charm tracing, replacing `charm_tracing` library |
| [databag-init-validation](databag-init-validation.md) | 2.22.0 | Behaviour change | Moderate | Core | Databag access validation enforced during `__init__`, surfacing latent bugs |

## Round 1 Catalogue (ops 2.23.0–3.6.0, June 2025–February 2026)

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

## Change Distribution (Combined)

### By type
- **Features**: 24
- **Improvements**: 2
- **Breaking changes**: 2
- **Behaviour changes**: 2
- **Deprecations**: 1

### By domain
- **Core ops**: 20 (charm code and runtime)
- **Testing (ops[testing])**: 10

### By complexity
- **Trivial**: 12
- **Trivial–Moderate**: 3
- **Moderate**: 12
- **Significant**: 2 (relation data classes, ops-testing migration)

## Most Impactful for Charm Upgrades

### Round 2 changes (broadest impact, September 2023–May 2025)

1. **[set-ports](set-ports.md)** — nearly every K8s charm manages ports; declarative API is a significant simplification.
2. **[non-deferrable-lifecycle](non-deferrable-lifecycle.md)** — breaking change that must be addressed for any charm deferring lifecycle events.
3. **[ops-testing-migration](ops-testing-migration.md)** — the most impactful long-term change; Harness → Scenario migration.
4. **[ops-tracing-adoption](ops-tracing-adoption.md)** — first-party tracing replaces community library.
5. **[pebble-check-events](pebble-check-events.md)** — reactive health monitoring for K8s charms.
6. **[pebble-notices](pebble-notices.md)** — event-driven workload communication.
7. **[databag-init-validation](databag-init-validation.md)** — may surface latent bugs; important for correctness.

### Round 1 changes (June 2025–February 2026)

1. **[config-classes](config-classes.md)** — nearly every charm has config; this is the most widely applicable.
2. **[action-classes](action-classes.md)** — most charms with actions will benefit.
3. **[relation-data-classes](relation-data-classes.md)** — high impact but requires care with interface compatibility.
4. **[layer-from-rockcraft](layer-from-rockcraft.md)** — significant test maintenance improvement for K8s charms.
5. **[testing-exception-wrapping](testing-exception-wrapping.md)** — simple win for any charm with unit tests.

Note: [security-event-logging](security-event-logging.md) and [deferred-events-logging](deferred-events-logging.md) are valuable but require no charm code changes — they activate automatically on upgrade.

## Source

* [ops CHANGES.md](https://github.com/canonical/operator/blob/main/CHANGES.md) — single changelog covering ops core, ops[testing], and ops[tracing]

All files in the `changes` folder were initially generated by Claude, but have been manually reviewed and tweaked by me.
