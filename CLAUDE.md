# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with files in this repository.

## Repository Purpose

This is a meta-repository for experimenting with and improving Claude Code's ability to develop Juju charms. It contains:

- **claude-instructions/**: Reusable Claude guidance files, custom commands, and a CLAUDE.md template for charm projects
- **experiments/**: Individual charm development attempts, each a self-contained experiment
- **READTHEM.md**: Curated reading list about AI/LLM development and coding practices

## Repository Structure

### claude-instructions/

Contains reusable Claude Code configuration for charm development:

- `CLAUDE.md`: Template guidance file for charm projects (comprehensive charm development instructions)
- `.claude/commands/`: Custom commands for common charm development tasks
  - `document.md`: Documentation generation
  - `review.md` and `review-git.md`: Code review workflows
  - `visualise.md`: Architecture visualisation
  - `clean.md`: Cleanup operations
  - `summary.md`: Project summaries

When starting a new charm experiment, copy these files to the experiment directory to provide Claude with charm-specific guidance.

### experiments/

Each subdirectory is a self-contained charm development experiment. Experiments should:

- Be dated (e.g., `2025-08-01-mosquitto-operator`)
- Include their own copy of the claude-instructions files
- Contain a README.md documenting the experiment's goals and outcomes
- Have their own CLAUDE.md with any experiment-specific adjustments
- Link out to the results of the experiment

## Working in This Repository

### Creating a New Experiment

1. Create a new directory in `experiments/` with format `YYYY-MM-DD-charm-name`
2. Copy `claude-instructions/CLAUDE.md` and `claude-instructions/.claude/` to the new experiment directory
3. Create a README.md documenting the experiment's purpose
4. If developing a charm, run `charmcraft init` inside the experiment directory
5. Make any necessary adjustments to CLAUDE.md for the specific experiment

### Improving the Claude Instructions

When you discover improvements to how Claude develops charms:

1. Update `claude-instructions/CLAUDE.md` with the improved guidance
2. Document what changed and why in commit messages
3. Consider whether custom commands in `.claude/commands/` need updates

### Git Workflow

- Use conventional commit messages
- Commit to the main branch for updates to `claude-instructions/` or repository documentation
- Each experiment may have its own branching strategy as documented in its README

## Key Principles

This repository exists to:

1. **Experiment**: Test Claude Code's capabilities for charm development
2. **Learn**: Identify where Claude struggles to inform both instruction improvements and Juju/charmcraft tooling enhancements
3. **Document**: Record findings in experiment READMEs to help others
4. **Improve**: Iteratively refine the claude-instructions based on experiment outcomes

When working on experiments, the goal is not to produce production-ready charms, but to evaluate how effective Claude Code can be with good guidance and tooling.

## Notes

- The `.claude/settings.local.json` file should never be committed (add to `.gitignore`)
- Experiment transcripts may be valuable to commit for future reference
