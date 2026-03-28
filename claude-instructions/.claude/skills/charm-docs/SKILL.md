---
name: charm-docs
description: Canonical charm documentation guidelines. Use when writing or reviewing charm READMEs, Charmhub content, or CONTRIBUTING files. Covers structure, templates, and Diataxis-based documentation.
license: default
compatibility: universal
allowed-tools: Read Grep Glob
---

# Charm Documentation Guidelines

These guidelines standardise documentation structure and content for Juju charms, covering the README file and Charmhub documentation. They extend the general Canonical documentation standards.

Based on spec DOC009.

---

## Documentation Types

A charm's documentation typically includes:
- **README**: description of the repository/project, stored with source code
- **Charmhub content**: information published on charmhub.io (description, resources, integrations, libraries, configurations, actions tabs)
- **Config files**: serialised data for parsing (e.g. `charmcraft.yaml`)
- **CONTRIBUTING file**: guidance for building, testing, and contributing

---

## README File

### General Guidance
- Give an **overview** of key aspects, but avoid multiple sources of truth — link instead of duplicating
- Keep the README **independent of Charmhub** — equally useful offline, for unlisted charms, or older versions
- Link to resources **inside the repository** where possible (e.g. `charmcraft.yaml` over Charmhub tabs)
- Keep the README **up to date** with charm code — incorporate into release checklists or CI checks

### README Template

```markdown
# <Charm name>
<!-- Badges -->

<!-- 1-2 sentence description. Include the workload software
     and substrate (VM/K8s). -->

Like any Juju charm, this charm supports one-line deployment,
configuration, integration, scaling, and more.
For Charmed {Name}, this includes:
<!-- List or summary of app-specific features -->

For information about how to deploy, integrate, and manage
this charm, see the Official [<Charm name> Documentation](<link>).

## Get started
<!-- Brief summary of what the user will achieve. -->
<!-- Software and hardware prerequisites. -->

### (Optional) Set up
<!-- Environment setup steps (e.g. via Multipass).
     Link to Juju docs, noting only deviations. -->

### (Optional) Deploy
<!-- Deployment steps. -->

### Basic operations
<!-- Brief walkthrough of configurations, operations,
     or integrations (scaling, TLS, etc.) -->
<!-- (Optional) Link to charmcraft.yaml -->

## (Optional) Integrations
<!-- Required or highly recommended integrations.
     Link to Charmhub for the full list. -->

## Learn more
* <!-- Link to official documentation -->
* <!-- Link to developer documentation -->
* <!-- (Optional) Official webpage/blog -->
* <!-- (Optional) Troubleshooting/FAQ -->

## Project and community
* <!-- GitHub issues -->
* <!-- Launchpad (if applicable) -->
* <!-- Contribution guides -->
* <!-- Contact info, e.g. Matrix channel -->

## (Optional) Licensing and trademark
```

---

## Charmhub Content

### Single-page description tab
Use when charm documentation lives elsewhere or is simple enough for one page.

**Case 1 — external docs**:
```markdown
# <Charm name>

<!-- 1-2 sentence description with workload and substrate. -->

For information about how to deploy, integrate, and manage
this charm, see the Official [<Charm name> Documentation](<link>).
```

**Case 2 — all docs on Charmhub**:
Follow the same structure as the README, with adjustments:
- Add "documentation" to the title
- No link to external docs
- Point `charmcraft.yaml` references to Charmhub tabs instead

### Multi-page description tab (Diataxis)

For charms with complex operations, structure documentation using [Diataxis](https://diataxis.fr/):

- **Index/Overview**: landing page with standard home page guidelines
- **Tutorial**: end-to-end guided journey from setup to teardown. Every charm wrapping a standalone workload should have one, even if minimal
- **How-to**: concise guides for specific goals (more practical than educational)
- **Reference**: release notes, lookup tables. Often minimal since configurations, libraries, and actions are already on Charmhub tabs
- **Explanation**: reasoning, architecture, complex features — context and "why"

Each Diataxis section with more than one page should have a **dedicated landing page**.

Not every category is always required — determine what is relevant and categorise accordingly.

### Cross-referencing
- For all generic Juju behaviour, **link to Juju docs** rather than duplicating
- Charm docs should focus on the **charm-specific** story: configs, integrations, and actions particular to the workload
- Avoid trying to educate users about Juju in general

---

## CONTRIBUTING File

Provide guidance for:
- Building the charm
- Running tests
- Contributing to source code and documentation
- Any project-specific conventions
