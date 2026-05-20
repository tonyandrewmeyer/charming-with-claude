"""Textual TUI for the review tool."""

from __future__ import annotations

import logging

from textual import work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import (
    DataTable,
    Footer,
    Header,
    Label,
    Select,
    Static,
    TextArea,
)

from review_tool.config import DB_PATH
from review_tool.db import (
    get_db_sync,
    get_finding_sync,
    get_findings_sync,
    get_stats_sync,
    init_db_sync,
    update_finding_sync,
)

SEVERITY_COLOURS = {
    "Critical": "white on dark_red",
    "High": "white on rgb(180,80,0)",
    "Medium": "black on yellow",
    "Low": "white on blue",
}

STATUS_ICONS = {
    "pending": "[dim]·[/]",
    "reviewed": "[green]✓[/]",
    "false_positive": "[red]✗[/]",
}


class StatsBar(Static):
    """Top bar showing review progress."""

    def update_stats(self, stats: dict) -> None:
        done = stats["reviewed"] + stats["false_positive"]
        total = stats["total"]
        pct = f"{100 * done / total:.0f}%" if total else "–"
        self.update(
            f" [bold]{done}[/]/{total} reviewed ({pct})  "
            f"[green]{stats['reviewed']} reviewed[/]  "
            f"[red]{stats['false_positive']} false positive[/]  "
            f"[dim]{stats['pending']} pending[/]"
        )


class FindingDetail(VerticalScroll):
    """Right-hand pane showing a single finding's details."""

    def compose(self) -> ComposeResult:
        yield Label("Select a finding from the table.", id="detail-placeholder")

    def show_finding(self, f: dict) -> None:
        self.remove_children()

        sev_style = SEVERITY_COLOURS.get(f["severity"], "")
        status_icon = STATUS_ICONS.get(f["review_status"], "?")

        lines = [
            f"[bold][{f['bug_id']}] {f['title']}[/bold]",
            f"[{sev_style}] {f['severity']} [/]  {status_icon} {f['review_status']}",
            "",
            f"[bold]Category:[/] {f['category']}",
            f"[bold]Repo:[/] {f['repo']}  [bold]Round:[/] {f['round']}",
            f"[bold]Location:[/] {f['location']}",
            f"[bold]Pattern:[/] {f['pattern']}",
        ]
        if f.get("reviewer_notes"):
            lines.extend(["", f"[bold]Reviewer notes:[/] {f['reviewer_notes']}"])

        self.mount(Static("\n".join(lines)))

        sections = [
            ("Issue", f["issue"]),
            ("Impact", f["impact"]),
            ("Evidence", f["evidence"]),
            ("Recommended Fix", f["recommended_fix"]),
        ]
        if f.get("historical_precedent"):
            sections.append(("Historical Precedent", f["historical_precedent"]))

        for title, body in sections:
            self.mount(Static(f"\n[bold underline]{title}[/]"))
            self.mount(Static(body, markup=False))

    def show_empty(self) -> None:
        self.remove_children()
        self.mount(Label("Select a finding from the table."))


class NotesInput(TextArea):
    """Text area for reviewer notes."""


log = logging.getLogger(__name__)


class ReviewApp(App):
    """Charm Bug Review TUI."""

    CSS = """
    #stats-bar {
        dock: top;
        height: 1;
        background: $surface;
        padding: 0 1;
    }

    #main {
        height: 1fr;
    }

    #filters {
        dock: top;
        height: 3;
        padding: 0 1;
        layout: horizontal;
    }

    #filters Select {
        width: 1fr;
        margin: 0 1 0 0;
    }

    #table-pane {
        width: 40%;
        border-right: solid $primary-background;
    }

    #detail-pane {
        width: 60%;
        padding: 0 1;
    }

    #notes-area {
        height: 4;
        margin: 1 0;
    }

    #review-buttons {
        height: 3;
        padding: 0 1;
        dock: bottom;
    }

    #review-buttons Label {
        margin: 0 2 0 0;
    }

    DataTable {
        height: 1fr;
    }

    FindingDetail {
        height: 1fr;
    }
    """

    BINDINGS = [
        Binding("r", "mark_reviewed", "Reviewed", show=True),
        Binding("f", "mark_false_positive", "False Positive", show=True),
        Binding("p", "mark_pending", "Pending", show=True),
        Binding("n", "focus_notes", "Notes", show=True),
        Binding("d", "focus_table", "Findings", show=True),
        Binding("q", "quit", "Quit", show=True),
    ]

    TITLE = "Charm Bug Review"

    def __init__(self) -> None:
        super().__init__()
        self._findings: list[dict] = []
        self._current_finding: dict | None = None
        self._filter_severity: str | None = None
        self._filter_status: str | None = None
        self._filter_repo: str | None = None
        self._pending_advance_id: int | None = None
        self._reloading: bool = False

    def compose(self) -> ComposeResult:
        yield Header()
        yield StatsBar(id="stats-bar")
        yield Horizontal(
            Select(
                [(s, s) for s in ("Critical", "High", "Medium", "Low")],
                prompt="All Severities",
                id="filter-severity",
                allow_blank=True,
            ),
            Select(
                [
                    ("Pending", "pending"),
                    ("Reviewed", "reviewed"),
                    ("False Positive", "false_positive"),
                ],
                prompt="All Statuses",
                id="filter-status",
                allow_blank=True,
            ),
            Select([], prompt="All Repos", id="filter-repo", allow_blank=True),
            id="filters",
        )
        yield Horizontal(
            Vertical(
                DataTable(id="findings-table", cursor_type="row"),
                id="table-pane",
            ),
            Vertical(
                FindingDetail(id="detail-pane"),
                NotesInput(id="notes-area"),
                id="right-pane",
            ),
            id="main",
        )
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one("#findings-table", DataTable)
        table.add_columns("Sev", "St", "Repo", "R", "Title")
        self._load_data(jump_to_unreviewed=True)

    @work(thread=True)
    def _load_data(self, jump_to_unreviewed: bool = False) -> None:
        try:
            log.debug(
                "Loading data (sev=%s, status=%s, repo=%s)",
                self._filter_severity,
                self._filter_status,
                self._filter_repo,
            )
            init_db_sync(DB_PATH)
            conn = get_db_sync(DB_PATH)
            stats = get_stats_sync(conn)
            all_findings = get_findings_sync(conn)
            repos = sorted({f["repo"] for f in all_findings})

            findings = get_findings_sync(
                conn,
                severity=self._filter_severity,
                status=self._filter_status,
                repo=self._filter_repo,
            )

            if jump_to_unreviewed:
                cursor = conn.execute(
                    "SELECT id FROM findings WHERE review_status = 'pending' ORDER BY id LIMIT 1"
                )
                row = cursor.fetchone()
                if row:
                    self._pending_advance_id = row["id"]

            conn.close()
            log.debug("Loaded %d findings, %d repos", len(findings), len(repos))
            self.call_from_thread(self._apply_data, stats, findings, repos)
        except Exception:
            log.exception("Failed to load data")

    def _apply_data(self, stats: dict, findings: list[dict], repos: list[str]) -> None:
        self.query_one("#stats-bar", StatsBar).update_stats(stats)

        # Populate repo filter if empty
        repo_select = self.query_one("#filter-repo", Select)
        if not repo_select._options:
            repo_select.set_options([(r, r) for r in repos])

        self._findings = findings
        table = self.query_one("#findings-table", DataTable)
        self._reloading = True
        table.clear()
        for f in findings:
            sev = f["severity"]
            st_icon = {"pending": "·", "reviewed": "✓", "false_positive": "✗"}.get(
                f["review_status"], "?"
            )
            table.add_row(
                sev,
                st_icon,
                f["repo"],
                str(f["round"]),
                f["title"][:60],
                key=str(f["id"]),
            )

        # Advance to next finding if requested (keep _reloading true
        # until after advance so queued highlight events are suppressed)
        if self._pending_advance_id is not None:
            advance_id = self._pending_advance_id
            self._pending_advance_id = None
            self._advance_to(advance_id)

        self._reloading = False

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        if event.row_key and event.row_key.value:
            self._show_finding(int(event.row_key.value))

    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        if self._reloading:
            return
        if event.row_key and event.row_key.value:
            self._show_finding(int(event.row_key.value))

    @work(thread=True)
    def _show_finding(self, finding_id: int) -> None:
        try:
            log.debug("Loading finding %d", finding_id)
            conn = get_db_sync(DB_PATH)
            finding = get_finding_sync(conn, finding_id)
            conn.close()
            if finding:
                self.call_from_thread(self._apply_finding, finding)
            else:
                log.warning("Finding %d not found in database", finding_id)
        except Exception:
            log.exception("Failed to load finding %d", finding_id)

    def _apply_finding(self, finding: dict) -> None:
        self._current_finding = finding
        self.query_one("#detail-pane", FindingDetail).show_finding(finding)
        notes_area = self.query_one("#notes-area", NotesInput)
        notes_area.load_text(finding.get("reviewer_notes", ""))

    def on_select_changed(self, event: Select.Changed) -> None:
        sel_id = event.select.id
        raw = event.value if event.value != Select.BLANK else None
        val: str | None = str(raw) if raw is not None else None
        if sel_id == "filter-severity":
            self._filter_severity = val
        elif sel_id == "filter-status":
            self._filter_status = val
        elif sel_id == "filter-repo":
            self._filter_repo = val
        self._load_data()

    def _do_review(self, status: str, advance: bool = False) -> None:
        if not self._current_finding:
            self.notify("No finding selected.", severity="warning")
            return
        finding_id = self._current_finding["id"]
        notes = self.query_one("#notes-area", NotesInput).text.strip()
        self._save_review(finding_id, status, notes, advance)

    @work(thread=True)
    def _save_review(
        self, finding_id: int, status: str, notes: str, advance: bool = False
    ) -> None:
        try:
            log.debug(
                "Saving review: finding=%d status=%s advance=%s",
                finding_id,
                status,
                advance,
            )
            conn = get_db_sync(DB_PATH)
            data: dict = {"review_status": status}
            if notes:
                data["reviewer_notes"] = notes
            update_finding_sync(conn, finding_id, data)

            next_id = None
            if advance:
                # Find the next pending finding after current
                cursor = conn.execute(
                    "SELECT id FROM findings WHERE review_status = 'pending' AND id > ? ORDER BY id LIMIT 1",
                    [finding_id],
                )
                row = cursor.fetchone()
                if not row:
                    # Wrap around
                    cursor = conn.execute(
                        "SELECT id FROM findings WHERE review_status = 'pending' ORDER BY id LIMIT 1",
                    )
                    row = cursor.fetchone()
                if row:
                    next_id = row["id"]

            conn.close()
            self.call_from_thread(self.notify, f"Marked as {status}")
            # Refresh the table, then advance
            self.call_from_thread(self._reload_and_advance, next_id)
        except Exception:
            log.exception("Failed to save review for finding %d", finding_id)

    def _reload_and_advance(self, next_id: int | None) -> None:
        """Reload table data and optionally select the next finding."""
        self._pending_advance_id = next_id
        self._load_data()

    def _advance_to(self, finding_id: int) -> None:
        """Move the table cursor to the given finding and show it."""
        table = self.query_one("#findings-table", DataTable)
        try:
            table.move_cursor(row=table.get_row_index(str(finding_id)))
            self._show_finding(finding_id)
        except Exception:
            log.debug(
                "Could not advance to finding %d (not in current view)", finding_id
            )

    def action_mark_reviewed(self) -> None:
        if self.focused and isinstance(self.focused, NotesInput):
            return
        self._do_review("reviewed", advance=True)

    def action_mark_false_positive(self) -> None:
        if self.focused and isinstance(self.focused, NotesInput):
            return
        self._do_review("false_positive", advance=True)

    def action_mark_pending(self) -> None:
        if self.focused and isinstance(self.focused, NotesInput):
            return
        self._do_review("pending")

    def action_focus_notes(self) -> None:
        if self.focused and isinstance(self.focused, NotesInput):
            return
        self.query_one("#notes-area", NotesInput).focus()

    def action_focus_table(self) -> None:
        self.query_one("#findings-table", DataTable).focus()


def run_tui() -> None:
    """Entry point for the TUI."""
    try:
        app = ReviewApp()
        app.run()
    except Exception:
        log.exception("TUI crashed")
        raise
