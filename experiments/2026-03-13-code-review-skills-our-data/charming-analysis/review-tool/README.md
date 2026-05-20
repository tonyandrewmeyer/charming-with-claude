# Charm Bug Review Tool

A local web application, terminal UI, and CLI for reviewing, triaging, and tracking bug findings produced by the `charm-find-bugs` agent skill. It parses structured markdown validation reports, stores findings in SQLite, and provides a web UI, a Textual-based TUI, and a command-line interface for human review.

## What It Does

The tool supports the iterative improvement loop for the `charm-find-bugs` skill:

1. **Import** — Parses `skill_validation_*.md` files (structured markdown reports of bugs found by the skill across Juju charm repositories) and loads them into a local SQLite database.
2. **Review** — Presents each finding in a two-panel web UI where a reviewer can read the issue, evidence, and recommended fix, then mark it as **reviewed** (true positive) or **false positive**.
3. **Track** — Maintains review progress, statistics by severity/repo/round, and reviewer notes.
4. **Export** — Dumps all findings and their review status as JSON for downstream analysis or feeding back into skill improvement.

## Usage

### Setup

```bash
uv pip install -e .
```

### Import findings

Import a single validation file:

```bash
review-tool import path/to/skill_validation_grafana.md --round 1
```

Or import all known validation files at once:

```bash
review-tool import-all
```

The `import-all` command expects the data files to live at `../../data/` relative to the package root, and uses the filename-to-repo mapping in `config.py`.

### Start the TUI

```bash
review-tool tui
```

The TUI provides the same two-panel review workflow in the terminal, built with [Textual](https://textual.textualize.io/). Filter by severity, status, or repo using the dropdown selects at the top. Navigate the findings table, then review with keyboard shortcuts shown in the footer: `r` reviewed, `f` false positive, `p` pending, `n` focus notes, `d` back to table, `q` quit.

### Start the web UI

```bash
review-tool serve              # http://0.0.0.0:8000
review-tool serve --port 9000  # custom port
```

The web UI has two main views:

- **Dashboard** (`/`) — progress bar, breakdowns by severity, repository, and round.
- **Findings** (`/findings`) — two-panel review interface with filter dropdowns (severity, status, repo, round). Select a finding on the left to see full details on the right. Keyboard shortcuts: `j`/`k` to navigate, `r` to mark reviewed, `f` to mark false positive, `n` to focus notes, `Space`/`]` for next unreviewed.

### CLI commands

| Command | Description |
|---------|-------------|
| `review-tool import <file> --round N` | Import a single validation file |
| `review-tool import-all` | Import all known validation files |
| `review-tool list [--severity X] [--status X] [--repo X] [--round N]` | List findings with optional filters |
| `review-tool show <id>` | Show full details of a finding |
| `review-tool review <id> --status reviewed\|false_positive\|pending [--notes "..."]` | Update review status |
| `review-tool stats` | Print summary statistics |
| `review-tool export [-o file.json]` | Export all findings as JSON |
| `review-tool serve [--port N] [--host H]` | Start the web server |
| `review-tool tui` | Start the terminal UI |

## Design and Architecture

### Stack

- **FastAPI** + **Uvicorn** for the async web server
- **SQLite** (via `aiosqlite` for async, `sqlite3` for CLI) as the data store — single-file `review.db` with WAL mode
- **Jinja2** templates with **htmx** for a responsive, SPA-like UI without a JS build step
- **Pygments** for syntax-highlighted Python code blocks in evidence/fix sections
- **Pico CSS** for minimal, classless styling
- **Textual** for the terminal UI
- **Click** for the CLI

### Module layout

```
review_tool/
├── app.py          # FastAPI app factory, lifespan, template setup
├── cli.py          # Click CLI group (serve, tui, import, list, show, review, stats, export)
├── config.py       # Paths, round/repo mappings
├── db.py           # Schema, sync + async DB helpers (init, insert, query, update)
├── models.py       # Pydantic models (FindingCreate, FindingUpdate, FindingOut, Stats)
├── parser.py       # Markdown parser for skill_validation_*.md files
├── tui.py          # Textual TUI app (two-panel review interface in the terminal)
├── routes/
│   ├── api.py      # JSON REST API (/api/findings, /api/stats, /api/import, /api/export)
│   └── pages.py    # HTML page routes (dashboard, findings list, detail, review actions)
├── templates/
│   ├── base.html
│   ├── index.html          # Dashboard
│   ├── findings.html       # Two-panel review page
│   └── partials/           # htmx partials (finding_row, finding_detail, findings_list, stats_bar)
└── static/
    └── style.css           # Severity badges, two-panel layout, code highlighting, keyboard hints
```

### Data model

The database has three tables:

- **findings** — one row per bug finding, keyed by `(repo, bug_id)`. Tracks category, severity, location, evidence, recommended fix, review status, reviewer notes, and timestamps.
- **confirmed_safe** — locations the skill flagged that were confirmed as not bugs.
- **import_log** — tracks which source files have been imported and their counts (used for deduplication).

### Key design choices

- **Dual sync/async DB layer** — the CLI and TUI use synchronous SQLite directly; the web server uses `aiosqlite`. Both share the same schema and helper patterns.
- **htmx-driven UI** — partial HTML responses keep the UI snappy without a JavaScript framework. Filters, row selection, and review actions all use htmx swaps.
- **Markdown parser with regex** — `parser.py` extracts structured fields from the `#### [BUG-NNN]` format used by the skill's validation reports, handling code blocks, severity levels, and confirmed-safe sections.
- **Deduplication on import** — the `UNIQUE(repo, bug_id)` constraint prevents duplicate findings; re-imports are safe.
