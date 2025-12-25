# Jhack Troubleshooting Guide

Common issues and solutions when using jhack.

## Installation and Setup Issues

### "jhack: command not found"

**Problem**: Jhack not installed or not in PATH.

**Solutions:**
```bash
# Check if installed
which jhack

# Install via snap
sudo snap install jhack

# Verify installation
jhack version
```

### "Unable to connect to juju"

**Problem**: Juju not configured or model not selected.

**Solutions:**
```bash
# Check juju status
juju status

# List models
juju models

# Switch model
juju switch <model-name>

# Bootstrap if needed
juju bootstrap <cloud> <controller>
```

## Sync Issues

### "Sync not pushing changes"

**Problem**: File watching not detecting changes or sync failing.

**Solutions:**
```bash
# Check unit is accessible
juju ssh myapp/0

# Verify source path exists
ls -la src/

# Use verbose logging
jhack --loglevel=DEBUG sync src/ myapp/0

# Try one-time sync
jhack sync --no-watch src/ myapp/0

# Check for file permission issues
ls -la src/
```

### "Changes sync but don't take effect"

**Problem**: Charm cached or not reloading.

**Solutions:**
```bash
# Fire config-changed to reload
jhack fire myapp/0 config-changed

# Or restart charm
juju exec myapp/0 -- ./dispatch stop
juju exec myapp/0 -- ./dispatch start

# For Python changes, might need to clear __pycache__
juju ssh myapp/0 -- 'find /var/lib/juju/agents -name "*.pyc" -delete'
juju ssh myapp/0 -- 'find /var/lib/juju/agents -type d -name __pycache__ -exec rm -rf {} +'
```

### "Permission denied when syncing"

**Problem**: SSH or file permissions.

**Solutions:**
```bash
# Check SSH access
juju ssh myapp/0

# Verify juju status
juju status myapp/0

# Check file permissions locally
ls -la src/

# Ensure files are readable
chmod -R u+r src/
```

## Event and Monitoring Issues

### "tail shows no events"

**Problem**: Wrong model, unit, or events not firing.

**Solutions:**
```bash
# Verify model
juju models
juju switch <model>

# Check unit exists
juju status

# Ensure unit is active
juju status myapp/0

# Try firing an event
jhack fire myapp/0 config-changed

# Watch with debug
jhack tail -d myapp/0
```

### "tail output is garbled"

**Problem**: Terminal width or color issues.

**Solutions:**
```bash
# Disable colors
jhack tail --no-color myapp/0

# Specify terminal width
export COLUMNS=120
jhack tail myapp/0

# Use alternative format
jhack tail --format=simple myapp/0
```

### "fire event doesn't work"

**Problem**: Invalid event name or unit state.

**Solutions:**
```bash
# Verify event name (no hyphens at start, use underscores)
jhack fire myapp/0 config_changed  # Wrong
jhack fire myapp/0 config-changed  # Correct

# Check unit is active
juju status myapp/0

# Check for hook errors
juju debug-log --include=myapp/0

# Verify relation ID for relation events
juju show-unit myapp/0 | grep relation-id
jhack fire myapp/0 database-relation-changed --relation-id=5
```

## Relation and State Issues

### "show-relation shows no data"

**Problem**: Relation not established or using wrong names.

**Solutions:**
```bash
# List all relations
juju status --relations

# Check relation exists
juju show-unit myapp/0

# Use correct relation name (check charmcraft.yaml)
jhack list-endpoints myapp

# Try with specific endpoints
jhack show-relation myapp:database postgresql:database

# Verify relation is joined
juju status
```

### "show-stored returns empty"

**Problem**: Charm hasn't set stored state or using wrong unit.

**Solutions:**
```bash
# Verify unit is running
juju status myapp/0

# Check charm uses StoredState
# (inspect src/charm.py for self.stored definitions)

# Try leader unit
jhack show-stored myapp/leader

# Fire event that sets state
jhack fire myapp/0 config-changed
jhack show-stored myapp/0
```

## Replay Issues

### "replay install fails"

**Problem**: Permissions or charm structure.

**Solutions:**
```bash
# Verify unit is accessible
juju ssh myapp/0

# Check charm is Python-based (replay requires Ops framework)
jhack charm-info myapp/0

# Try with sudo (if needed)
# Note: Usually not needed, check permissions
```

### "replay list shows no events"

**Problem**: Recorder not active or no events captured.

**Solutions:**
```bash
# Ensure recorder installed
jhack replay install myapp/0

# Fire some events
jhack fire myapp/0 config-changed
jhack fire myapp/0 update-status

# Wait a moment, then list
jhack replay list myapp/0

# Check database path
juju ssh myapp/0 -- ls -la /tmp/jhack*
```

### "replay emit doesn't fire event"

**Problem**: Invalid event ID or state mismatch.

**Solutions:**
```bash
# List available events first
jhack replay list myapp/0

# Use correct event ID from list
jhack replay emit myapp/0 5

# Dump event to inspect
jhack replay dump myapp/0 5

# Check unit is still active
juju status myapp/0
```

## Scenario Issues

### "snapshot fails or incomplete"

**Problem**: Charm state not accessible or serialization error.

**Solutions:**
```bash
# Verify unit is active
juju status myapp/0

# Check with debug logging
jhack --loglevel=DEBUG scenario snapshot myapp/0

# Try specific format
jhack scenario snapshot myapp/0 --format=yaml

# Ensure ops-scenario installed
pip install ops-scenario
```

### "state-apply doesn't work"

**Problem**: Invalid state file or incompatible version.

**Solutions:**
```bash
# Verify state file is valid JSON/YAML
python3 -c "import json; json.load(open('state.json'))"

# Check state matches charm version
jhack charm-info myapp/0

# Try with debug logging
jhack --loglevel=DEBUG scenario state-apply myapp/0 state.json
```

## Pebble Issues

### "pebble command fails"

**Problem**: Not a Kubernetes charm or wrong container name.

**Solutions:**
```bash
# Verify it's a K8s charm
juju status myapp/0 | grep kubernetes

# List containers
juju ssh myapp/0 -- ls /etc/

# Try with correct container name
juju ssh --container=mycontainer myapp/0 -- pebble version

# Use jhack with correct container
jhack pebble -c mycontainer myapp/0 plan
```

### "pebble exec permission denied"

**Problem**: Container permissions or security context.

**Solutions:**
```bash
# Check pebble is running
jhack pebble -c mycontainer myapp/0 version

# Try simpler command
jhack pebble -c mycontainer myapp/0 exec "whoami"

# Check container status
juju status myapp/0
```

## Debug and Script Issues

### "eval returns error"

**Problem**: Invalid expression or charm state.

**Solutions:**
```bash
# Use simple expression first
jhack eval myapp/0 "1 + 1"

# Check charm instance available
jhack eval myapp/0 "type(self)"

# Verify attribute exists
jhack eval myapp/0 "dir(self)" | grep config

# Use quotes properly
jhack eval myapp/0 'self.config["port"]'  # Correct
```

### "script fails to execute"

**Problem**: Script syntax or missing function.

**Solutions:**
```bash
# Verify script defines run() function
cat myscript.py

# Example correct script:
cat > test.py << 'EOF'
def run(charm):
    print(f"Unit: {charm.unit.name}")
    return True
EOF

# Test script
jhack script myapp/0 test.py

# Check with debug
jhack --loglevel=DEBUG script myapp/0 test.py
```

## Destructive Operation Issues

### "nuke requires confirmation"

**Problem**: Devmode not enabled.

**Solutions:**
```bash
# Enable devmode
jhack conf set devmode=true

# Or use --force
jhack nuke myapp --force

# Or use --dry-run first
jhack nuke "test-*" --dry-run
jhack nuke "test-*"  # Then confirm
```

### "nuke pattern doesn't match"

**Problem**: Shell glob expansion or pattern syntax.

**Solutions:**
```bash
# Use quotes for wildcards
jhack nuke "test-*"  # Correct
jhack nuke test-*    # Wrong (shell expands before jhack sees it)

# Test pattern first with dry-run
jhack nuke "test-*" --dry-run

# List what exists
juju status

# Use exact name if only one
jhack nuke test-app-1
```

### "kill doesn't stop hook"

**Problem**: Hook already finished or unit unresponsive.

**Solutions:**
```bash
# Check if hook is running
juju status myapp/0

# Try force resolution
juju resolve myapp/0 --no-retry

# Check debug-log
juju debug-log --include=myapp/0 --lines=50

# As last resort, remove and redeploy
jhack nuke myapp
juju deploy ...
```

## Chaos Testing Issues

### "chaos commands too aggressive"

**Problem**: Default intensity too high for your charm.

**Solutions:**
```bash
# Use lower intensity
jhack chaos mancioppi myapp --intensity=3

# Shorter duration
jhack chaos mancioppi myapp --duration=60

# Start with flicker (simpler)
jhack chaos flicker myapp --count=5
```

### "charm breaks during chaos"

**Problem**: This is the point! You found bugs.

**Solutions:**
```bash
# Capture events before chaos
jhack replay install myapp/0

# Run chaos
jhack chaos mancioppi myapp

# Analyze failures
juju debug-log --include=myapp
jhack replay list myapp/0

# Fix issues in charm code
# Test fixes with replay
jhack replay emit myapp/0 <failing-event-id>
```

## Configuration Issues

### "devmode setting not persisting"

**Problem**: Configuration not saved or wrong path.

**Solutions:**
```bash
# Check current config
jhack conf show

# Set devmode
jhack conf set devmode=true

# Verify
jhack conf get devmode

# Check config file location
ls -la ~/.config/jhack/
```

### "logs not writing to file"

**Problem**: Permission or path issues.

**Solutions:**
```bash
# Use absolute path
jhack --log-to-file=/tmp/jhack.log tail myapp/0

# Check directory exists and is writable
ls -la /tmp/
touch /tmp/test && rm /tmp/test

# Use relative path
jhack --log-to-file=./jhack.log tail myapp/0
```

## Performance Issues

### "sync is very slow"

**Problem**: Large files or many files being watched.

**Solutions:**
```bash
# Exclude large directories
jhack sync --exclude="*.charm" --exclude=".tox" src/ myapp/0

# Increase interval
jhack sync --interval=5 src/ myapp/0

# Sync specific subdirectories only
jhack sync src/charm.py myapp/0

# Use sync-packed for packed charms
jhack charm sync-packed --charm=myapp.charm
```

### "tail uses too much CPU"

**Problem**: Too many events or debug output.

**Solutions:**
```bash
# Remove -d flag
jhack tail myapp/0  # Without debug

# Filter events
jhack tail --filter=config-changed myapp/0

# Limit to specific unit
jhack tail myapp/0  # Not all units

# Reduce update-status frequency
jhack ffwd myapp --interval=5m
```

## Model and Controller Issues

### "Wrong model being used"

**Problem**: Default model set incorrectly.

**Solutions:**
```bash
# Check current model
juju models

# Switch model
juju switch <model-name>

# Or specify in command
jhack -m mymodel show-stored myapp/0

# Set default
juju switch <model-name>
export JUJU_MODEL=<model-name>
```

### "Controller not responding"

**Problem**: Controller issues or network problems.

**Solutions:**
```bash
# Check controller status
juju controllers

# Try reconnecting
juju logout
juju login

# Check network
ping <controller-ip>

# Restart controller if self-hosted
juju kill-controller <controller> --force
juju bootstrap ...
```

## Getting Help

### Enable Debug Logging

For any issue, start with debug logging:

```bash
jhack --loglevel=DEBUG <command>
jhack --log-to-file=debug.log --loglevel=DEBUG <command>
```

### Check Juju Environment

```bash
# Print environment details
jhack jenv

# Check juju status
juju status --relations

# Check debug-log
juju debug-log --lines=100
```

### Common Diagnostic Commands

```bash
# Verify jhack version
jhack version

# Check configuration
jhack conf show

# Test basic connectivity
jhack show-stored myapp/0

# Verify model
juju models
juju switch <model>

# Check unit status
juju status myapp/0
```

### Reporting Issues

When reporting jhack bugs:

1. Jhack version: `jhack version`
2. Juju version: `juju version`
3. Environment: `jhack jenv`
4. Full error output with `--loglevel=DEBUG`
5. Steps to reproduce
6. Expected vs actual behavior

Report at: https://github.com/canonical/jhack/issues -- **ALWAYS ASK FIRST**

## Safety Reminders

1. **Use devmode carefully**: `jhack conf set devmode=false` in production
2. **Test destructive commands**: Use `--dry-run` first
3. **Verify patterns**: Check `nuke` patterns with dry-run
4. **Backup state**: Capture snapshots before major changes
5. **Monitor chaos tests**: Watch for unexpected failures
6. **Check before running `jhack utils this-is-fine`**: Understand why units errored first
