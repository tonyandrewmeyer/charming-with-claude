# Charmcraft Agent Skill

An expert Claude skill for developing Juju charms using charmcraft.

## Overview

This skill provides comprehensive guidance for working with charmcraft, the tool for building, testing, and publishing Juju charms. It covers everything from project initialisation to publishing on Charmhub.

## What This Skill Provides

- **Complete workflow guidance**: From `charmcraft init` to publishing on Charmhub
- **Best practices**: Following Canonical charm development standards
- **Troubleshooting**: Common issues and their solutions
- **Reference documentation**: Detailed charmcraft.yaml configuration guide
- **Integration with Ops framework**: Proper charm development patterns
- **Quality assurance**: Testing and analysis workflows

## When This Skill Activates

Claude will automatically use this skill when you:

- Ask about charmcraft commands or workflows
- Mention charm development or Juju
- Need help with charmcraft.yaml configuration
- Want to publish to Charmhub
- Request charm library management
- Ask about charm testing or building

Example triggers:
- "How do I initialise a new Kubernetes charm?"
- "Help me publish my charm to Charmhub"
- "What should go in charmcraft.yaml?"
- "How do I fetch charm libraries?"
- "Build and test my charm"

## Skill Structure

```
charmcraft/
├── SKILL.md                              # Main skill instructions
├── README.md                             # This file
├── references/
│   ├── charmcraft-yaml-reference.md     # Complete charmcraft.yaml guide
│   └── troubleshooting.md               # Common issues and solutions
└── scripts/
    └── quick-start.sh                    # Helper script for new projects
```

## Usage Examples

### Initialise a New Charm

**User**: "Create a new Kubernetes charm for a web application"

**Claude** (using this skill):
```bash
charmcraft init --profile=kubernetes --name=my-webapp
```

Then provides guidance on customising charmcraft.yaml and implementing the charm.

### Build and Publish Workflow

**User**: "Build my charm and publish it to the edge channel"

**Claude** (using this skill):
```bash
# Build the charm
charmcraft pack

# Analyse for issues
charmcraft analyse ./my-charm_ubuntu-22.04-amd64.charm

# Upload and release to edge
charmcraft upload ./my-charm_ubuntu-22.04-amd64.charm --release=edge
```

### Library Management

**User**: "Add the PostgreSQL client library to my charm"

**Claude** (using this skill):
1. Updates charmcraft.yaml:
```yaml
charm-libs:
  - lib: postgresql.postgres_client
    version: "0"
```

2. Fetches the library:
```bash
charmcraft fetch-libs
```

3. Provides usage examples from the library documentation.

## Progressive Disclosure

This skill uses Claude's progressive disclosure feature:

1. **Level 1 (Metadata)**: Always loaded - skill description tells Claude when to use it
2. **Level 2 (SKILL.md)**: Loaded when charmcraft-related queries detected
3. **Level 3 (References)**: Loaded on-demand when specific topics needed:
   - `references/charmcraft-yaml-reference.md` - For configuration questions
   - `references/troubleshooting.md` - For error/problem solving
   - `scripts/quick-start.sh` - For new project setup

This ensures only relevant content is loaded, keeping context usage efficient.

## Integration with Existing Projects

This skill works well with:

- **Ops framework documentation**: Automatically references ops.testing and Pebble docs
- **Juju commands**: Provides context for testing deployed charms
- **Python development**: Integrates with tox, pytest, ruff, and pyright
- **Git workflows**: Follows conventional commits and changelog practices

## Best Practices Followed

This skill enforces:

- ✅ Always use `optional: true` for required relations
- ✅ Run `charmcraft analyse` before uploading
- ✅ Test on edge before promoting to stable
- ✅ Use `tox` for local quality checks
- ✅ Follow channel progression: edge → beta → candidate → stable
- ✅ Keep uv.lock in version control
- ✅ Use conventional commits
- ✅ Comprehensive testing (unit + integration)

## Customisation

You can customise this skill by:

1. **Adding project-specific patterns**: Edit SKILL.md to include your team's conventions
2. **Adding more references**: Create additional .md files in `references/`
3. **Adding helper scripts**: Add automation scripts to `scripts/`
4. **Adjusting for your stack**: Update framework-specific guidance

## Compatibility

- **charmcraft**: Works with charmcraft 2.0+, charmcraft 4+ recommended
- **Juju**: Covers Juju 3.6 and 4.x patterns
- **Ops framework**: Current ops library patterns
- **Python**: Python 3.10+ (aligns with charm requirements)

## Contributing

To improve this skill:

1. Keep SKILL.md focused on common workflows
2. Move detailed information to reference files
3. Add troubleshooting entries as you encounter issues
4. Update examples to reflect current best practices
5. Test with actual charm development workflows

## Related Skills

This skill pairs well with:

- **Git/GitHub skills**: For version control and CI/CD
- **Python development skills**: For charm implementation
- **Kubernetes skills**: For understanding K8s charm deployment
- **Testing skills**: For comprehensive test coverage

## License

Apache 2.0

## Version

1.0.0 - Initial release

## Support

- **Charmcraft docs**: https://documentation.ubuntu.com/charmcraft/
- **Juju docs**: https://documentation.ubuntu.com/juju/latest/
- **Ops docs**: https://documentation.ubuntu.com/ops/
- **Discourse**: https://discourse.charmhub.io/
