# Jhack Complete Command Reference

Comprehensive reference for all jhack commands and their options.

## Command Groups

### jhack (Top Level)

Core commands available directly under `jhack`:

```bash
jhack version                 # Show jhack version
jhack show-relation <app> <app>  # Show relation databags
jhack show-stored <unit>      # Show stored state
jhack tail [unit]             # Watch events
jhack ffwd <app>              # Speed up update-status
jhack jenv                    # Print juju environment details
jhack list-endpoints <app>    # List integration endpoints
jhack sync <src> <unit>       # Sync local to remote
jhack nuke <pattern>          # Remove resources
jhack kill <unit>             # Kill running hook
jhack deploy <charm>          # Deploy with auto-resource handling
jhack fire <unit> <event>     # Fire event manually
jhack pull-cmr <offer>        # Pull cross-model relation
jhack charm-info <unit>       # Show charm version info
jhack eval <unit> <expr>      # Evaluate expression
jhack debug-log <unit>        # Unified log view
jhack script <unit> <file>    # Execute Python script
jhack pebble <args>           # Proxy pebble commands
jhack commands                # List all commands
jhack conf                    # Configuration management
```

## jhack show-relation

Display relation databags between applications or units.

```bash
# Basic usage
jhack show-relation <app1> <app2>

# Specific endpoints
jhack show-relation <app1>:<endpoint> <app2>:<endpoint>

# With units
jhack show-relation <app1/0> <app2/0>

# Options
--model, -m <name>            # Specify model
--format <format>             # Output format (table, json, yaml)
--endpoint, -e <name>         # Filter by endpoint name
```

**Examples:**
```bash
jhack show-relation myapp postgresql
jhack show-relation myapp:database postgresql:database
jhack show-relation -m production myapp postgresql
jhack show-relation --format=json myapp postgresql
```

## jhack show-stored

Visualize charm's stored state (StoredState).

```bash
jhack show-stored <unit>

# Options
--model, -m <name>            # Specify model
--format <format>             # Output format (table, json, yaml)
```

**Examples:**
```bash
jhack show-stored myapp/0
jhack show-stored myapp/leader
jhack show-stored -m prod myapp/0 --format=json
```

## jhack tail

Pretty-print events being fired on units.

```bash
jhack tail [unit]

# Options
--model, -m <name>            # Specify model
--debug, -d                   # Show debug output
--filter <pattern>            # Filter by event name
--show-defer                  # Show deferred events
--show-secrets                # Show secret values (use carefully!)
--length <n>                  # Show last N events
```

**Examples:**
```bash
jhack tail                    # All units in current model
jhack tail myapp/0            # Specific unit
jhack tail -d myapp/0         # With debug output
jhack tail --filter=config-changed  # Only config-changed events
jhack tail --length=50        # Last 50 events
```

## jhack sync

Sync local directory to remote unit via juju scp.

```bash
jhack sync <src> <unit>

# Options
--model, -m <name>            # Specify model
--no-watch                    # Don't watch for changes (one-time sync)
--exclude <pattern>           # Exclude patterns (can be repeated)
--interval <seconds>          # Watch interval (default: 1)
--dry-run                     # Show what would be synced
```

**Examples:**
```bash
jhack sync src/ myapp/0
jhack sync --src=./src --src=./lib myapp/0
jhack sync --no-watch src/ myapp/0
jhack sync --exclude="*.pyc" --exclude="__pycache__" src/ myapp/0
```

## jhack ffwd

Fast-forward update-status hook interval.

```bash
jhack ffwd <app>

# Options
--model, -m <name>            # Specify model
--interval <duration>         # Hook interval (e.g., "10s", "1m")
--stop                        # Reset to default interval
```

**Examples:**
```bash
jhack ffwd myapp --interval=10s    # Every 10 seconds
jhack ffwd myapp --interval=1m     # Every 1 minute
jhack ffwd myapp --stop            # Reset to default
```

## jhack fire

Simulate an event on a unit.

```bash
jhack utils fire <unit> <event>

# Options
--model, -m <name>            # Specify model
--relation-id <id>            # For relation events
--env VAR=VALUE               # Set environment variables (can be repeated)
```

**Events you can fire:**
- `install`, `start`, `stop`, `remove`
- `config-changed`, `upgrade-charm`
- `update-status`, `leader-elected`, `leader-settings-changed`
- `<relation>-relation-created`, `<relation>-relation-joined`
- `<relation>-relation-changed`, `<relation>-relation-departed`
- `<relation>-relation-broken`
- Custom events defined by the charm

**Examples:**
```bash
jhack utils fire myapp/0 config-changed
jhack utils fire myapp/0 database-relation-changed --relation-id=5
jhack utils fire myapp/0 upgrade-charm
jhack fire myapp/0 start --env DEBUG=true
```

## jhack nuke

Safely remove juju resources with pattern matching.

```bash
jhack nuke <pattern>

# Options
--model, -m <name>            # Specify model
--all                         # Remove all applications in model
--dry-run                     # Show what would be removed
--force, -f                   # Skip confirmation
--apps                        # Remove applications only
--relations                   # Remove relations only
--units                       # Remove units only
```

**Pattern matching:**
- Exact match: `jhack nuke myapp`
- Wildcard: `jhack nuke "test-*"` (quotes required for shell wildcards)
- Multiple: `jhack nuke app1 app2 app3`

**Examples:**
```bash
jhack nuke myapp
jhack nuke "test-*" --dry-run
jhack nuke --all --model=testing
jhack nuke myapp --relations  # Only remove relations
```

## jhack utils (Utility Commands)

### jhack utils elect

Force a unit to become leader.

```bash
jhack utils elect <unit>

# Options
--model, -m <name>            # Specify model
```

**Example:**
```bash
jhack utils elect myapp/1     # Make unit 1 the leader
```

### jhack utils print-env

Print juju environment details for bug reports.

```bash
jhack utils print-env
```

### jhack utils this-is-fine

Auto-resolve all units in error state (use with extreme caution!).

```bash
jhack utils this-is-fine

# Options
--model, -m <name>            # Specify model
```

### jhack utils record

Record events and state for later replay.

```bash
jhack utils record <unit>

# Options
--model, -m <name>            # Specify model
--stop                        # Stop recording
```

## jhack replay (Event Replay)

### jhack replay install

Install event recorder on a unit.

```bash
jhack replay install <unit>

# Options
--model, -m <name>            # Specify model
```

### jhack replay list

List captured events.

```bash
jhack replay list <unit>

# Options
--model, -m <name>            # Specify model
--format <format>             # Output format (table, json)
```

### jhack replay emit

Re-fire a captured event.

```bash
jhack replay emit <unit> <event-id>

# Options
--model, -m <name>            # Specify model
```

### jhack replay dump

Dump event data.

```bash
jhack replay dump <unit> [event-id]

# Options
--model, -m <name>            # Specify model
--all                         # Dump all events
```

### jhack replay purge

Delete captured events.

```bash
jhack replay purge <unit> [event-id]

# Options
--model, -m <name>            # Specify model
--all                         # Purge all events
```

## jhack charm (Charm Utilities)

### jhack charm update

Force-push directories into a packed .charm file.

```bash
jhack charm update <charm-file> <src-dir> [<src-dir> ...]

# Options
--dry-run                     # Show what would be updated
```

**Example:**
```bash
jhack charm update myapp.charm src/
jhack charm update myapp.charm src/ lib/
```

### jhack charm sync-packed

Watch directories and auto-update packed charm on changes.

```bash
jhack charm sync-packed

# Options
--charm <file>                # Charm file (auto-detected if not specified)
--src <dir>                   # Source directory (can be repeated)
--interval <seconds>          # Watch interval
```

**Example:**
```bash
jhack charm sync-packed --charm=myapp.charm --src=./src --src=./lib
```

### jhack charm lobotomy

Prevent charm from processing events (lobotomize).

```bash
jhack charm lobotomy <unit>

# Options
--model, -m <name>            # Specify model
--undo                        # Restore normal operation
--all                         # Lobotomize all units
```

**Example:**
```bash
jhack charm lobotomy myapp/0        # Freeze charm
jhack charm lobotomy myapp/0 --undo # Restore
```

### jhack charm sitrep

Gather and print unit status.

```bash
jhack charm sitrep <unit>

# Options
--model, -m <name>            # Specify model
--format <format>             # Output format
```

## jhack scenario (Scenario Testing)

### jhack scenario snapshot

Capture current charm state as scenario State.

```bash
jhack scenario snapshot <unit>

# Options
--model, -m <name>            # Specify model
--output, -o <file>           # Output file (default: stdout)
--format <format>             # Output format (json, yaml)
```

**Example:**
```bash
jhack scenario snapshot myapp/0 > state.json
jhack scenario snapshot myapp/0 -o tests/state.json --format=yaml
```

### jhack scenario state-apply

Apply a scenario State to a unit.

```bash
jhack scenario state-apply <unit> <state-file>

# Options
--model, -m <name>            # Specify model
```

**Example:**
```bash
jhack scenario state-apply myapp/0 state.json
```

## jhack pebble

Proxy pebble commands to remote unit containers.

```bash
jhack pebble -c <container> <unit> <pebble-command> [args]

# Options
--model, -m <name>            # Specify model
--container, -c <name>        # Container name (required)
```

**Pebble commands:**
- `plan` - Show pebble plan
- `services` - List services
- `logs <service>` - Show service logs
- `exec <command>` - Execute command in container
- `start <service>` - Start service
- `stop <service>` - Stop service
- `restart <service>` - Restart service

**Examples:**
```bash
jhack pebble -c nginx myapp/0 plan
jhack pebble -c nginx myapp/0 services
jhack pebble -c nginx myapp/0 logs nginx
jhack pebble -c nginx myapp/0 exec "ls -la /"
jhack pebble -c nginx myapp/0 restart nginx
```

## jhack debug-log

Unified view of charm and container logs.

```bash
jhack debug-log <unit>

# Options
--model, -m <name>            # Specify model
--follow, -f                  # Follow logs
--lines <n>                   # Show last N lines
```

**Example:**
```bash
jhack debug-log myapp/0
jhack debug-log -f myapp/0 --lines=100
```

## jhack eval

Evaluate Python expression in charm context.

```bash
jhack eval <unit> <expression>

# Options
--model, -m <name>            # Specify model
```

**Available in context:**
- `self` - The charm instance
- `self.unit` - Unit instance
- `self.app` - Application instance
- `self.model` - Model instance
- `self.config` - Config
- All charm attributes

**Examples:**
```bash
jhack eval myapp/0 "self.unit.status"
jhack eval myapp/0 "self.config['port']"
jhack eval myapp/0 "len(self.model.relations['database'])"
```

## jhack script

Execute Python script in charm context.

```bash
jhack script <unit> <script-file>

# Options
--model, -m <name>            # Specify model
```

**Script requirements:**
- Must define a function that takes `charm` parameter
- Function is executed with charm instance

**Example script:**
```python
def run(charm):
    print(f"Status: {charm.unit.status}")
    print(f"Leader: {charm.unit.is_leader()}")
    return charm.config.get('port')
```

**Usage:**
```bash
jhack script myapp/0 debug.py
```

## jhack chaos (Chaos Testing)

### jhack chaos mancioppi

Stress test through rapid relation/scale changes.

```bash
jhack chaos mancioppi <app>

# Options
--model, -m <name>            # Specify model
--duration <seconds>          # Test duration
--intensity <level>           # Chaos intensity (1-10)
```

### jhack chaos flicker

Rapid scaling up/down.

```bash
jhack chaos flicker <app>

# Options
--model, -m <name>            # Specify model
--count <n>                   # Number of flicker cycles
```

## jhack conf (Configuration)

### jhack conf show

Show current jhack configuration.

```bash
jhack conf show
```

### jhack conf set

Set configuration value.

```bash
jhack conf set <key>=<value>

# Common settings
jhack conf set devmode=true   # Skip confirmations
jhack conf set devmode=false  # Require confirmations
```

### jhack conf get

Get configuration value.

```bash
jhack conf get <key>
```

## Global Options

These options work with most jhack commands:

```bash
--loglevel <level>            # Set log level (DEBUG, INFO, WARNING, ERROR)
--log-to-file <path>          # Log to file instead of stdout
```

**Example:**
```bash
jhack --loglevel=DEBUG tail myapp/0
jhack --log-to-file=jhack.log sync src/ myapp/0
```

## Return Codes

- `0` - Success
- `1` - General error
- `2` - Invalid usage/arguments
- `130` - Interrupted by user (Ctrl+C)

## Environment Variables

```bash
JUJU_MODEL                    # Default model to use
JHACK_DEVMODE                 # Enable devmode (true/false)
JHACK_LOGLEVEL                # Default log level
```
