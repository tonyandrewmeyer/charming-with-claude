# GitHub Copilot Instructions

## Repository Overview

This repository is an experimental project for exploring and improving AI-assisted development of [Juju charms](https://juju.is/). The primary focus is on **documentation and guidance files** rather than production code.

**Purpose**: Test, evaluate, and document how effectively AI coding assistants (Claude Code, GitHub Copilot) can develop Juju charms with proper guidance.

## Repository Structure

```
charming-with-claude/
├── .github/
│   └── copilot-instructions.md    # This file
├── claude-instructions/            # Reusable Claude Code configuration
│   ├── CLAUDE.md                  # Template guidance for charm projects
│   └── .claude/commands/          # Custom commands for charm development
├── experiments/                   # Individual charm development experiments
│   └── YYYY-MM-DD-charm-name/     # Format: date + charm name
├── CLAUDE.md                      # Claude Code guidance for this repo
├── README.md                      # Project overview
└── READTHEM.md                   # Curated AI/LLM development reading list
```

### Key Directories

- **claude-instructions/**: Contains reusable Claude Code configuration templates that can be copied into charm projects. This is the "source of truth" for charm development guidance.
- **experiments/**: Self-contained charm development experiments. Each experiment is independent and may be incomplete or intentionally experimental.

## Primary Focus: Documentation Quality

This repository is primarily composed of **text and markdown files**, not code. When working on issues or reviewing pull requests, prioritise documentation quality over code-specific concerns.

## Critical: UK English Spelling

**All documentation in this repository MUST use UK English spelling conventions.**

Common differences to watch for:
- Use "favour" not "favor"
- Use "colour" not "color"
- Use "organise" not "organize"
- Use "analyse" not "analyze"
- Use "behaviour" not "behavior"
- Use "licence" (noun) and "license" (verb), not "license" for both
- Use "centre" not "center"
- Use "-ise" endings not "-ize" (e.g., "optimise" not "optimize")
- Use "-ogue" not "-og" (e.g., "catalogue" not "catalog")

Flag any US spelling as a **critical issue** that must be corrected before merging.

## Documentation Review Criteria

When reviewing markdown and documentation files, assess:

1. **Spelling and Grammar**
   - Verify UK English spelling throughout
   - Check for grammatical errors and typos
   - Ensure consistent terminology

2. **Clarity and Readability**
   - Are instructions clear and easy to follow?
   - Is the structure logical and well-organised?
   - Are examples helpful and accurate?

3. **Completeness**
   - Does the documentation cover all necessary information?
   - Are there gaps or missing context?
   - Are cross-references accurate?

4. **Formatting**
   - Proper markdown syntax
   - Consistent heading hierarchy
   - Appropriate use of lists, code blocks, and emphasis

5. **Accuracy**
   - Are technical details correct?
   - Do file paths and commands work as documented?
   - Are links valid and pointing to the right resources?

## Code Review (When Applicable)

For the small amount of code in this repository (primarily Python charm code in experiments):

1. Follow Python best practices and PEP 8 style
2. Ensure Juju charm conventions are followed
3. Verify proper error handling
4. Check for security issues
5. Validate that tests are present and meaningful

## Repository-Specific Considerations

- **Experiments**: Individual experiments may be incomplete or intentionally experimental—focus review on whether the experiment is documented appropriately
- **Claude Instructions**: Changes to `CLAUDE.md` or `.claude/commands/` files should be clear and actionable for AI assistants
- **Structure**: Verify new experiments follow the `YYYY-MM-DD-charm-name` naming convention

## Development Workflows

### Creating a New Experiment

When asked to create a new charm experiment:

1. Create directory in `experiments/` with format `YYYY-MM-DD-charm-name` (use current date)
2. Copy `claude-instructions/CLAUDE.md` to the experiment directory
3. Copy `claude-instructions/.claude/` directory to the experiment directory
4. Create a README.md documenting the experiment's purpose and goals
5. If developing a Juju charm, run `charmcraft init` inside the experiment directory
6. Make any necessary adjustments to CLAUDE.md for the specific experiment

### Updating Claude Instructions

When improving the reusable Claude guidance:

1. Update files in `claude-instructions/` directory (not individual experiments)
2. Document what changed and why in commit messages
3. Consider whether custom commands in `.claude/commands/` need updates
4. Update experiment copies if the changes are significant and the experiment is active

### Git Workflow

- Use conventional commit messages (e.g., `docs:`, `feat:`, `fix:`)
- Commit to the main branch for updates to `claude-instructions/` or repository documentation
- Each experiment may have its own branching strategy as documented in its README

## Testing and Validation

This repository has minimal automated testing as it's primarily documentation. When making changes:

1. **Documentation changes**: Verify markdown syntax, check links, ensure UK English spelling
2. **Experiment changes**: Ensure the experiment directory structure is correct and README is updated
3. **Claude instructions changes**: Validate that instructions are clear, actionable, and follow UK English conventions
4. **Python code** (in experiments): Follow PEP 8 style, verify Juju charm conventions, check for proper error handling

## Common Tasks

### Good Tasks for Copilot Coding Agent

- Improving documentation clarity and completeness
- Fixing typos and spelling errors (especially US → UK English)
- Adding new experiments with proper structure
- Updating claude-instructions based on experiment learnings
- Enhancing READTHEM.md with new relevant articles
- Creating or improving README files for experiments

### Tasks to Approach Carefully

- Modifying charm code in experiments (requires Juju knowledge)
- Changing the structure of claude-instructions templates
- Making breaking changes to `.claude/commands/` files
- Altering experiment results or conclusions

## About Juju Charms

[Juju](https://juju.is/) is an open-source orchestration engine for software operators. Charms are operator code packages containing logic for deploying, integrating, scaling, and maintaining applications on any cloud or infrastructure.

When working with charm code:
- Charms are typically written in Python using the [Operator Framework](https://juju.is/docs/sdk)
- Use `charmcraft` CLI for charm operations (init, pack, etc.)
- Charms follow specific structural conventions (see `claude-instructions/CLAUDE.md`)
- The goal in this repo is experimentation and learning, not production-ready charms

## Tone and Style

- Use a constructive and helpful tone
- Be specific in feedback (provide line numbers or examples)
- Suggest improvements rather than just identifying problems
- Remember: documentation quality directly impacts usability
