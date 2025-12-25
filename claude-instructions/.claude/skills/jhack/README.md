# Jhack Agent Skill

An expert Claude skill for Juju charm development using jhack utilities.

## Overview

This skill provides comprehensive guidance for using jhack, a collection of developer utilities that streamline Juju charm development, debugging, and testing workflows.

## What This Skill Provides

- **Rapid development workflows**: Sync code and test in seconds
- **Debugging utilities**: Inspect relations, state, and events
- **Event manipulation**: Fire, capture, and replay events
- **Testing integration**: Scenario snapshots and chaos testing
- **Complete command reference**: All jhack commands documented
- **Troubleshooting guide**: Solutions for common issues

## Installation

### For Claude Code

1. Copy the `jhack` directory to your Claude skills location:

```bash
# Personal skills (available globally)
cp -r jhack ~/.claude/skills/

# Project-specific skills (available in one project)
cp -r jhack /path/to/project/.claude/skills/
```

2. The skill will be detected automatically.

### For Claude API

Create a zip file and upload via the Skills API:

```bash
# Create zip file
cd jhack
zip -r ../jhack-skill.zip .

# Upload using the Claude API
# POST /v1/skills with the zip file
```

### For Claude.ai

1. Create a zip file:
```bash
cd jhack
zip -r ../jhack-skill.zip .
```

2. Go to Settings > Features in Claude.ai
3. Upload the zip file
4. The skill will be available in your conversations

## When This Skill Activates

Claude will automatically use this skill when you:

- Ask about jhack commands or workflows
- Mention charm debugging or development
- Need help with Juju charm testing
- Want to inspect relations or state
- Request event replay or scenario testing

Example triggers:
- "How do I sync my code to a running charm?"
- "Show me the relation data between myapp and postgresql"
- "How can I capture and replay production events?"
- "Help me debug this charm integration"
- "What's the fastest way to test charm changes?"

## Skill Structure

```
jhack/
├── SKILL.md                              # Main skill instructions (~3000 tokens)
├── README.md                             # This file
├── references/
│   ├── command-reference.md              # Complete command documentation
│   └── troubleshooting.md                # Common issues and solutions
└── scripts/
    └── (future helper scripts)
```

## Usage Examples

### Rapid Development

**User**: "I'm editing charm code and want to test changes quickly"

**Claude** (using this skill):
```bash
# Start syncing code to running unit
jhack sync src/ myapp/0

# Edit code locally, then fire event to test
jhack utils fire myapp/0 config-changed

# Watch events in real-time
jhack tail -d myapp/0
```

### Debugging Relations

**User**: "My charm isn't getting database credentials from postgresql"

**Claude** (using this skill):
```bash
# Check what data is being shared
jhack show-relation myapp postgresql

# Verify the relation endpoint names
jhack list-endpoints myapp
jhack list-endpoints postgresql

# Fire relation event manually
jhack utils fire myapp/0 database-relation-changed

# Watch for the event execution
jhack tail -d myapp/0
```

### Capturing Production Issues

**User**: "Something went wrong in production, how do I debug it?"

**Claude** (using this skill):
```bash
# Install event recorder
jhack replay install myapp/0

# Wait for issue to occur, then list events
jhack replay list myapp/0

# Dump the problematic event
jhack replay dump myapp/0 15

# Replay it locally for debugging
jhack replay emit test-myapp/0 15
```

## Progressive Disclosure

This skill uses Claude's progressive disclosure feature:

1. **Level 1 (Metadata)**: Always loaded - skill description tells Claude when to use it
2. **Level 2 (SKILL.md)**: Loaded when jhack-related queries detected (~3000 tokens)
3. **Level 3 (References)**: Loaded on-demand for specific topics:
   - `references/command-reference.md` - Complete command documentation
   - `references/troubleshooting.md` - Debugging and solutions

This ensures only relevant content is loaded, keeping context usage efficient.

## Key Commands Covered

- **Inspection**: `show-relation`, `show-stored`, `tail`, `charm-info`
- **Development**: `sync`, `fire`, `ffwd`
- **Replay**: `replay install`, `replay list`, `replay emit`
- **Scenario**: `scenario snapshot`, `scenario state-apply`
- **Pebble**: Shortcuts for K8s container operations
- **Debugging**: `debug-log`, `eval`, `script`
- **Manipulation**: `lobotomy`, `elect`, `nuke`
- **Chaos**: `mancioppi`, `flicker`

## Integration with Other Tools

This skill works well with:

- **Charmcraft skill**: For charm building and publishing
- **Juju**: Native juju commands for deployment
- **Tox**: Local quality checks before testing

## Best Practices Enforced

- ✅ Use `sync` for rapid iteration
- ✅ Watch events with `tail -d` for debugging
- ✅ Capture production issues with `replay`
- ✅ Test with realistic state using `scenario snapshot`
- ✅ Enable devmode only in development
- ✅ Use `--dry-run` before destructive operations
- ✅ Verify patterns before `nuke` operations

## Requirements

- **jhack**: Installed locally (snap or uv)
- **juju**: Active Juju controller and model
- **SSH access**: To deployed units
- **Network**: For model operations

## Compatibility

- **jhack**: Latest version recommended
- **Juju**: 2.9+ (3.x recommended)
- **Charms**: Ops framework based (Python charms)

## Contributing

To improve this skill:

1. Keep SKILL.md focused on common workflows
2. Move detailed information to reference files
3. Add troubleshooting entries as you encounter issues
4. Update examples to reflect current best practices
5. Test with actual charm development workflows

## Related Skills

This skill pairs well with:

- **charmcraft**: For building and packaging charms
- **Git/GitHub skills**: For version control
- **Python development skills**: For charm implementation
- **Testing skills**: For comprehensive test coverage

## License

Apache 2.0

## Version

1.0.0 - Initial release

## Support

- **Jhack GitHub**: https://github.com/canonical/jhack
- **Juju docs**: https://documentation.ubuntu.com/juju/3.6/
- **Ops framework**: https://documentation.ubuntu.com/ops/
- **Discourse**: https://discourse.charmhub.io/
