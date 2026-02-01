# Charming with Claude

An experimental repository for exploring and improving Claude Code's ability to develop [Juju charms](https://canonical.com/juju/).

## Purpose

This repository serves as a testing ground to:

- **Experiment** with Claude Code's capabilities for charm development
- **Learn** where Claude struggles and what guidance helps it succeed
- **Document** findings to inform both instruction improvements and tooling enhancements
- **Iterate** on reusable Claude Code configurations for charm projects

The goal is not to produce production-ready charms, but to evaluate and enhance how effectively Claude Code can develop charms with proper (and minimal) guidance.

## Repository Structure

```
charming-with-claude/
├── claude-instructions/       # Reusable Claude Code configuration
│   ├── CLAUDE.md              # Template guidance for charm projects
│   ├── README.md              # Guidance for using the Claude configuration
│   ├── INSTALL-SKILLS.md      # Instructions for using Claude skills from this repo
│   └── .claude/commands/      # Custom commands for charm development
│   └── .claude/skills/        # Custom skills for charm development
│   └── .claude/settings.json  # Starting settings for charm development
├── experiments/               # Individual charm development experiments
│   └── 2025-08-01-mosquitto-operator/
│   └── 2025-12-23-beszel-k8s-operator/
├── READTHEM.md                # Curated reading list on AI/LLM development
└── CLAUDE.md                  # Claude Code guidance for this repository
```

### experiments/

Each subdirectory is a self-contained charm development experiment. Experiments follow the format `YYYY-MM-DD-charm-name` and include:

- Their own copy of claude-instructions files (as they were at the start of development)
- README.md documenting goals and outcomes
- Links to experiment results

**Current experiments:**
- [2025-08-01-mosquitto-operator](experiments/2025-08-01-mosquitto-operator/)
- [2025-12-23-beszel-k8s-operator](experiments/2025-12-23-beszel-k8s-operator/)

### READTHEM.md

A curated [reading list](READTHEM.md) of articles and blogs about AI/LLM development, coding practices, and the evolving landscape of AI-assisted development.

## Quick Start

### Creating a New Experiment

1. Create a new directory in `experiments/`:
   ```bash
   mkdir experiments/$(date +%Y-%m-%d)-your-charm-name
   cd experiments/$(date +%Y-%m-%d)-your-charm-name
   ```

2. Copy Claude configuration:
   ```bash
   cp ../../claude-instructions/CLAUDE.md .
   cp -r ../../claude-instructions/.claude .
   ```

3. Initialize your charm:
   ```bash
   charmcraft init
   ```

4. Create a README.md documenting your experiment's purpose

5. Start developing with Claude Code!

### Working with Claude Code

If you're using Claude Code in this repository or an experiment, see [CLAUDE.md](CLAUDE.md) for detailed guidance specific to this project.

## Contributing

When you discover improvements to how Claude develops charms:

1. Update `claude-instructions/CLAUDE.md` with improved guidance
2. Document what changed and why in commit messages
3. Consider whether custom commands need updates
4. Share findings in experiment READMEs

## About Juju Charms

[Juju](https://canonical.com/juju/) is an open-source orchestration engine for software operators. Charms are operator code packages that contain all the logic for deploying, integrating, scaling, and maintaining applications on any cloud or infrastructure.

## Licence

This repository is licensed under the [Creative Commons Attribution 4.0 International Licence](LICENSE) (CC BY 4.0).

You are free to use, share, and adapt the content with appropriate attribution.
