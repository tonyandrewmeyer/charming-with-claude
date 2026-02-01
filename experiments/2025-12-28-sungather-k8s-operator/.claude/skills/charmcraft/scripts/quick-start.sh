#!/bin/bash
# Charmcraft Quick Start Helper
# This script helps initialise and set up a new charm project with best practices

set -e

# Colours for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Helper functions
error() {
    echo -e "${RED}Error: $1${NC}" >&2
    exit 1
}

success() {
    echo -e "${GREEN}✓ $1${NC}"
}

info() {
    echo -e "${YELLOW}→ $1${NC}"
}

# Check if charmcraft is installed
if ! command -v charmcraft &> /dev/null; then
    error "charmcraft not found. Install with: sudo snap install charmcraft --classic"
fi

# Parse arguments
PROFILE="kubernetes"
NAME=""
AUTHOR=""
INIT_GIT=true

show_help() {
    cat << EOF
Charmcraft Quick Start Helper

Usage: ./quick-start.sh [OPTIONS]

Options:
    -n, --name NAME          Charm name (required)
    -p, --profile PROFILE    Charm profile (default: kubernetes)
    -a, --author AUTHOR      Author name (default: from git config)
    --no-git                 Don't initialise git repository
    -h, --help               Show this help message

Profiles:
    kubernetes               Kubernetes charm (default)
    machine                  Machine charm
    django-framework         Django app charm
    fastapi-framework        FastAPI app charm
    flask-framework          Flask app charm
    go-framework             Go app charm
    spring-boot-framework    Spring Boot charm

Example:
    ./quick-start.sh -n my-webapp -p kubernetes -a "Your Name"
EOF
}

while [[ $# -gt 0 ]]; do
    case $1 in
        -n|--name)
            NAME="$2"
            shift 2
            ;;
        -p|--profile)
            PROFILE="$2"
            shift 2
            ;;
        -a|--author)
            AUTHOR="$2"
            shift 2
            ;;
        --no-git)
            INIT_GIT=false
            shift
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            error "Unknown option: $1
Use --help for usage information"
            ;;
    esac
done

# Validate required arguments
if [ -z "$NAME" ]; then
    error "Charm name is required. Use -n or --name"
fi

# Validate NAME to prevent path traversal attacks
# Allow only alphanumeric characters, hyphens, and underscores
# Name must start with alphanumeric character to avoid confusion with command flags
if [[ ! "$NAME" =~ ^[a-zA-Z0-9][a-zA-Z0-9_-]*$ ]]; then
    error "Invalid charm name. Must start with alphanumeric character and contain only alphanumeric characters, hyphens, and underscores"
fi

# Get author from git config if not provided
if [ -z "$AUTHOR" ]; then
    AUTHOR=$(git config user.name 2>/dev/null || echo "")
    if [ -z "$AUTHOR" ]; then
        error "Author name required. Use -a/--author or set git config user.name"
    fi
fi

info "Creating charm: $NAME"
info "Profile: $PROFILE"
info "Author: $AUTHOR"

# Create directory
mkdir -p "$NAME"
cd "$NAME" || error "Failed to cd into $NAME"

# Initialise charm
info "Initialising charm with charmcraft..."
charmcraft init --profile="$PROFILE" --name="$NAME" --author="$AUTHOR" --force
success "Charm initialised"

# Create additional recommended files
info "Creating additional files..."

# SECURITY.md
cat > SECURITY.md << 'EOF'
# Security Policy

## Reporting a Vulnerability

Please report security vulnerabilities using GitHub's private vulnerability reporting feature:

1. Go to the repository's Security tab
2. Click "Report a vulnerability"
3. Fill in the details

Alternatively, email the maintainers directly.

Do not open public issues for security vulnerabilities.

## Supported Versions

Only the latest version receives security updates.
EOF
success "Created SECURITY.md"

# CODE_OF_CONDUCT.md
cat > CODE_OF_CONDUCT.md << 'EOF'
# Code of Conduct

## Our Pledge

We are committed to providing a welcoming and inspiring community for all.

## Our Standards

Examples of behaviour that contributes to creating a positive environment include:

* Using welcoming and inclusive language
* Being respectful of differing viewpoints and experiences
* Gracefully accepting constructive criticism
* Focusing on what is best for the community

## Enforcement

Project maintainers are responsible for clarifying the standards of acceptable behavior and are expected to take appropriate and fair corrective action in response to any instances of unacceptable behaviour.

## Attribution

This Code of Conduct is adapted from the Contributor Covenant, version 1.4.
EOF
success "Created CODE_OF_CONDUCT.md"

# CHANGELOG.md
cat > CHANGELOG.md << 'EOF'
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial charm implementation

[Unreleased]: https://github.com/canonical/CHANGEME/commits/main
EOF
success "Created CHANGELOG.md"

# TUTORIAL.md
cat > TUTORIAL.md << EOF
# ${NAME} Tutorial

This tutorial will walk you through deploying and using the ${NAME} charm.

## Prerequisites

- A Juju controller (run \`juju bootstrap\` if you don't have one)
- Access to a cloud or local Juju model

## Deploy the charm

\`\`\`bash
# Create a model
juju add-model ${NAME}-demo

# Deploy the charm
juju deploy ${NAME}

# Watch deployment progress
juju status --watch 1s
\`\`\`

## Configure the charm

\`\`\`bash
# See available configuration options
juju config ${NAME}

# Set configuration (example)
# juju config ${NAME} some-option=value
\`\`\`

## Integrate with other charms

\`\`\`bash
# Example: Integrate with PostgreSQL
# juju deploy postgresql
# juju integrate ${NAME} postgresql
\`\`\`

## Run actions

\`\`\`bash
# List available actions
juju actions ${NAME}

# Run an action (example)
# juju run ${NAME}/0 some-action
\`\`\`

## Clean up

\`\`\`bash
# Remove the application
juju remove-application ${NAME}

# Destroy the model
juju destroy-model ${NAME}-demo
\`\`\`

## Next steps

- Review the [README](README.md) for more information
- Check the [API documentation](https://charmhub.io/CHANGEME/docs)
- Join the community on [Discourse](https://discourse.charmhub.io/)
EOF
success "Created TUTORIAL.md"

# Update .gitignore
cat >> .gitignore << 'EOF'

# Charm build artifacts
*.charm
__pycache__/
*.py[cod]
*$py.class

# Virtual environments
venv/
env/
ENV/

# Testing
.tox/
.pytest_cache/
.coverage
htmlcov/

# IDE
.vscode/
.idea/
*.swp
*.swo

# Claude Code
.claude/settings.local.json

# OS
.DS_Store
Thumbs.db
EOF
success "Updated .gitignore"

# Initialise git repository
if [ "$INIT_GIT" = true ]; then
    info "Initialising git repository..."
    git init
    git add .
    git commit -m "chore: initial charm scaffold

Generated using charmcraft init with ${PROFILE} profile.

🤖 Generated with Claude Code"
    success "Git repository initialised"
fi

# Create pre-commit config
cat > .pre-commit-config.yaml << 'EOF'
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      - id: check-merge-conflict
      - id: check-case-conflict
      - id: mixed-line-ending

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.9
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
EOF
success "Created .pre-commit-config.yaml"

# Summary
echo ""
success "Charm project initialised successfully!"
echo ""
info "Next steps:"
echo "  1. cd $NAME"
echo "  2. Review and customise charmcraft.yaml"
echo "  3. Edit src/charm.py to implement your charm logic"
echo "  4. Update README.md with charm-specific documentation"
echo "  5. Run 'tox -e lint' to check code quality"
echo "  6. Run 'tox -e unit' to run unit tests"
echo "  7. Run 'charmcraft pack' to build the charm"
echo ""
info "Recommended: Install pre-commit hooks"
echo "  pip install pre-commit"
echo "  pre-commit install"
echo ""
info "Documentation:"
echo "  Charmcraft: https://documentation.ubuntu.com/charmcraft/"
echo "  Ops: https://documentation.ubuntu.com/ops/"
echo "  Juju: https://documentation.ubuntu.com/juju/latest/"
