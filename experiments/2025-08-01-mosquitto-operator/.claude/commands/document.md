# Inspired by https://github.com/wcygan/dotfiles

Generates high-quality, user-facing documentation automatically.

## Usage

```
/document [options]
```

## Options

```
/document --readme-only          # Generate only README.md
/document --changelog-only       # Generate only CHANGELOG.md  
/document --api-docs            # Generate API documentation
/document --all                 # Generate all documentation (default)
```

## Description

This command automatically generates and maintains project documentation by analysing your codebase, configuration files, and git history.

### What it generates:

#### 1. README.md (Root Directory)

Creates comprehensive project documentation in the project root including:

**Project Overview Section:**

- Auto-detected project name and description from `charmcraft.yaml`
- Technology stack detection and badges
- Build status and version badges

**Installation Section:**

- Platform-specific installation commands (charmcraft, juju)
- Dependency requirements and version constraints

**Usage Section:**

- CLI commands from `charmcraft.yaml` actions
- Configuration examples from `charmcraft.yaml` config

**Development Section:**

- Setup instructions for new contributors
- Testing commands and coverage information
- Code style and contribution guidelines

#### 2. CHANGELOG.md (Root Directory)

Analyzes git history to create structured changelog in the project root:

**Conventional Commits Analysis:**

- Groups commits by type: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`
- Extracts breaking changes from commit footers
- Links to issues and pull requests

**Version Detection:**

- Uses git tags to determine release versions
- Calculates semantic version bumps based on commit types
- Includes release dates and contributor information

**Example Output:**

```markdown
# Changelog

## [1.2.0] - 2024-06-06

### Features

- Add user authentication system (#42)
- Implement real-time notifications (#45)

### Bug Fixes

- Fix database connection pooling issue (#48)
- Resolve memory leak in websocket handler (#50)

### Breaking Changes

- Remove deprecated `/v1/auth` endpoint
```

#### 3. User Documentation (`/docs` Directory)

User documentation uses the [Diátaxis approach](https://diataxis.fr). This means that we provide four forms of documentation:

* Tutorials: we should have one tutorial that carefully walks a user through installing, deploying, and using the charm. The tutorial helps the reader learn about the charm.
* How-to Guides: for each major feature of the charm, we should have a how-to guide. The how-to guides help readers achieve goals, like "how can I use the charm with a different database".
* Explanation: copy design guides, architecture plans, and so forth here. The reader gains understanding of the charm by reading this material. There should always be at least one document, called "Security", that outlines any use of cryptographic technology, any hardening that can be done, any security risks in using the charm, and any security best practices with regards to the charm.
* Reference: The actions, config, and any other user surface area should be covered in the reference documentation. This is information that the reader uses when they are looking for specific answers.

### Documentation Maintenance

**Automatic Updates:**

- Detects when documentation is stale compared to code
- Updates version numbers and dependency information

**Quality Checks:**

- Validates Markdown syntax and links
- Checks for broken references to code or files
- Ensures all actions and config are documented

## Examples

### Generate all documentation:

```
/document
```

### Update only README:

```
/document --readme-only
```

### Create changelog since last release:

```
/document --changelog-only
```

## Integration Features

**GitHub Integration:**

- Creates `.github/ISSUE_TEMPLATE/` and `.github/PULL_REQUEST_TEMPLATE.md`
- Sets up automated documentation updates via GitHub Actions

**Badge Generation:**

- Build status from CI providers
- Code coverage from testing tools
- Version badges from package registries
- License and language statistics

## Best Practices Applied

**Accessibility:**

- Alt text for images and diagrams
- Proper semantic HTML in generated content
- Screen reader friendly formatting
