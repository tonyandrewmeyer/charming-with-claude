# General diagrams

# Inspired by https://github.com/wcygan/dotfiles

Analyses code and architecture to generate explanatory diagrams.

## Usage

```
/visualise <target>
/visualise <target> --type <flowchart|sequence|erd|architecture>
/visualise <target> --format <mermaid|plantuml|graphviz>
/visualise <target> --output <file.md>
```

**Default Output Location**: `/docs/diagrams/` directory

## Description

This command transforms complex code, logic, and system architectures into clear, visual diagrams. A picture is worth a thousand lines of code - this command makes systems easier to understand, debug, and communicate about.

### What it generates:

#### 1. Code Flow Visualization

Analyses functions and methods to create flowcharts:

* Function analysis (for example, Python code to Mermaid flowcharts)
* Charm relationships (for example, a relationship diagram showing this charm at the heart and the required and optional requirer/provider integrations that are possible)
* System architecture diagrams (for example as a Mermaid graph)
* API interaction sequences (for example, sequences of Juju events as a Mermaid sequence diagram)

## Output Formats

### Mermaid (Default)

Generates Mermaid.js diagrams that render in GitHub, GitLab, and VS Code:

````markdown
# Function Flow Analysis

```mermaid
flowchart TD
    A[Start] --> B[Process]
    B --> C[End]
```
````

### Graphviz DOT

Generates DOT files for complex dependency graphs:

```dot
digraph Dependencies {
    rankdir=TB;
    node [shape=box];
    
    "auth-service" -> "database";
    "user-service" -> "auth-service";
    "user-service" -> "database";
    "payment-service" -> "user-service";
    "api-gateway" -> "auth-service";
    "api-gateway" -> "user-service";
    "api-gateway" -> "payment-service";
}
```

## Examples

### Visualize a function:

```
/visualize ./src/charm.py:MyCharm._on_install
```

### Visualise integrations:

```
/visualize charmcraft.yaml --type=erd
```

### Generate system architecture:

```
/visualize . --type architecture
```

### Create API sequence diagram:

```
/visualize ./src/charm.py --type sequence
```

### Output to specific file:

```
/visualize ./src/charm.py --output docs/diagrams/auth-flow.md
```

## Advanced Features

### Interactive Diagrams

Generates interactive diagrams with clickable elements:

```mermaid
flowchart TD
    A["Start"] --> B["Process"]
    B --> C["End"]
    
    click A "https://github.com/org/repo/blob/main/src/start.py" "View Source"
    click B "https://github.com/org/repo/blob/main/src/process.py" "View Source"
    click C "https://github.com/org/repo/blob/main/src/end.py" "View Source"
```

### Complexity Analysis

Annotates diagrams with complexity metrics:

```mermaid
flowchart TD
    A["Login Function<br/>Complexity: 3"] --> B{"Valid User?"}
    B -->|Yes| C["Success<br/>Path: 1"]
    B -->|No| D["Retry<br/>Path: 2"]
    D --> E{"Max Retries?"}
    E -->|Yes| F["Lock Account<br/>Path: 3"]
    E -->|No| A
```

### Dependency Analysis

Shows dependency relationships and potential circular dependencies:

```mermaid
graph TD
    A[auth] --> B[database]
    C[user] --> A
    C --> B
    D[payment] --> C
    E[notification] --> C
    F[api] --> A
    F --> C
    F --> D
    F --> E
    
    style A fill:#ff9999
    style C fill:#ff9999
    
    classDef warning fill:#ffeb3b,stroke:#f57f17,stroke-width:2px
    class A,C warning
```
