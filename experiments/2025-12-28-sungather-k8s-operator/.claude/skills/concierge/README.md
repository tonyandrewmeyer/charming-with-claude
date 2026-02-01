# Concierge Agent Skill

An expert Claude skill for provisioning charm development and testing environments using concierge.

## Overview

This skill provides comprehensive guidance for using concierge, an opinionated utility for automating the setup of charm development machines. It handles everything from installing craft tools to bootstrapping Juju controllers across multiple providers.

## What This Skill Provides

- **Quick environment setup**: Use presets for instant configuration
- **Complete provider support**: LXD, MicroK8s, K8s, Google Cloud
- **Craft tool installation**: charmcraft, snapcraft, rockcraft
- **Juju controller bootstrap**: Automatic controller setup
- **Custom configuration**: Flexible YAML-based configuration
- **Environment restoration**: Safe cleanup and removal

## When This Skill Activates

Claude will automatically use this skill when you:

- Ask about setting up a charm development environment
- Mention concierge or environment provisioning
- Need help with Juju controller bootstrapping
- Want to install craft tools and providers
- Request environment cleanup or restoration

Example triggers:
- "Set up a charm development environment"
- "Prepare my machine for charm development"
- "How do I bootstrap Juju controllers?"
- "Install charmcraft and all the dev tools"
- "Set up MicroK8s for testing charms"

## Skill Structure

```
concierge/
├── SKILL.md                      # Main skill instructions
├── README.md                     # This file
└── references/
    ├── presets.md                # Detailed preset comparison
    └── configuration.md          # Complete YAML schema
```

## Usage Examples

### Quick Development Setup

**User**: "Set up a complete charm development environment"

**Claude** (using this skill):
```bash
# Install concierge
sudo snap install --classic concierge

# Prepare full development environment
concierge prepare -p dev --extra-snaps=jhack

# Verify setup
concierge status
```

### Custom Environment

**User**: "I need a K8s environment with specific tool versions"

**Claude** (using this skill):
```bash
# Create custom configuration
cat > concierge.yaml <<EOF
juju:
  channel: "3.6/stable"

providers:
  k8s:
    enable: true
    bootstrap: true
    channel: "1.31/stable"

host:
  snaps:
    - name: jhack
      channel: latest/stable
EOF

# Prepare with custom config
concierge prepare -c concierge.yaml
```

### Machine Charm Development

**User**: "Set me up for traditional machine charm development"

**Claude** (using this skill):
```bash
concierge prepare -p machine
```

Explains that this preset installs:
- Juju
- LXD (bootstrapped)
- Charmcraft
- Snapcraft

## Progressive Disclosure

This skill uses Claude's progressive disclosure feature:

1. **Level 1 (Metadata)**: Always loaded - skill description tells Claude when to use it
2. **Level 2 (SKILL.md)**: Loaded when concierge-related queries detected
3. **Level 3 (References)**: Loaded on-demand for specific topics:
   - `references/presets.md` - Detailed preset comparison and use cases
   - `references/configuration.md` - Complete YAML schema and examples

This ensures only relevant content is loaded, keeping context usage efficient.

## The Five Presets

| Preset | Best For | Includes |
|--------|----------|----------|
| **dev** | Full-featured development | Juju, K8s, LXD, all craft tools, jhack |
| **machine** | Traditional machine charms | Juju, LXD, charmcraft, snapcraft |
| **k8s** | Kubernetes charm development | Juju, K8s, LXD*, charmcraft, rockcraft |
| **microk8s** | Lightweight K8s development | Juju, MicroK8s, LXD*, charmcraft, rockcraft |
| **crafts** | Build-only (no Juju) | LXD, all craft tools |

*LXD installed but not bootstrapped (only for charmcraft build backend)

**For detailed preset information, see [references/presets.md](references/presets.md)**

## Key Features Covered

### Environment Provisioning
- Preset-based configuration
- Custom YAML configuration
- Channel overrides
- Extra package installation

### Provider Management
- LXD setup and bootstrap
- MicroK8s configuration
- K8s cluster setup
- Google Cloud integration

### Tool Installation
- Craft tools (charmcraft, snapcraft, rockcraft)
- Juju installation and bootstrap
- Additional snaps and debs
- Development utilities (jhack, etc.)

### Lifecycle Management
- Status checking
- Environment restoration
- Safe cleanup

## Best Practices Followed

This skill enforces:

- ✅ Choose appropriate preset for use case
- ✅ Verify status after preparation
- ✅ Use custom config files for team consistency
- ✅ Add jhack for rapid development
- ✅ Never run restore on production machines
- ✅ Use verbose logging when troubleshooting
- ✅ Test configurations in VMs first
- ✅ Document custom setups

## Integration with Existing Projects

This skill works well with:

- **Charmcraft skill**: Automatically prepares environment for charm development
- **Jhack skill**: Includes jhack in dev preset for rapid iteration
- **CI/CD workflows**: Automated environment setup
- **Team development**: Shared configuration files

## Common Workflows

1. **New developer onboarding**: `concierge prepare -p dev`
2. **CI/CD setup**: `concierge prepare -p dev --extra-snaps=astral-uv/latest/edge`
3. **K8s testing**: `concierge prepare -p k8s`
4. **Build server**: `concierge prepare -p crafts --disable-juju`
5. **Cleanup**: `concierge restore`

## Customisation

You can customise this skill by:

1. **Adding team presets**: Document standard team configurations
2. **Adding troubleshooting entries**: Update references with common issues
3. **Adding example configs**: Include project-specific YAML examples
4. **Adding automation scripts**: Helper scripts for common setups

## Compatibility

- **Concierge**: Latest stable version
- **Operating System**: Ubuntu 22.04, 24.04 (primary test targets)
- **Juju**: 3.6+, 4.0+ supported
- **Providers**: LXD 5.x, MicroK8s 1.30+, K8s 1.30+
- **Craft tools**: Latest stable versions

## Safety Warnings

**⚠️ IMPORTANT: Restore Behaviour**

The `concierge restore` command:
- Does NOT preserve pre-existing configurations
- Removes everything installed by `prepare`
- Cannot distinguish between before/after prepare state
- Should NEVER be run on production machines

Always test restore in a VM or container first.

## Contributing

To improve this skill:

1. Keep SKILL.md focused on common workflows
2. Move detailed information to reference files
3. Add troubleshooting entries as issues are discovered
4. Update examples to reflect current best practices
5. Test with actual development workflows

## Related Skills

This skill pairs well with:

- **charmcraft**: For charm building and publishing after environment setup
- **jhack**: For rapid development once environment is ready
- **Git/GitHub skills**: For managing configuration files
- **CI/CD skills**: For automating environment provisioning

## License

Apache 2.0

## Version

1.0.0 - Initial release

## Support

- **Concierge GitHub**: https://github.com/canonical/concierge
- **Juju docs**: https://documentation.ubuntu.com/juju/latest/
- **Charmcraft docs**: https://documentation.ubuntu.com/charmcraft/
- **Discourse**: https://discourse.charmhub.io/
