#!/usr/bin/env python3
"""TUI tool for human review of scored experiment responses.

Presents question, agent response, gold standard, and judge scores
side by side. Reviewer can confirm or override each dimension score.

Usage:
    source /tmp/review-venv/bin/activate
    python scripts/review_tool.py
    python scripts/review_tool.py --sample 0.33   # review 33% sample
    python scripts/review_tool.py --condition C    # filter by condition
    python scripts/review_tool.py --resume         # skip already-reviewed
"""

import argparse
import json
import random
import sys
from pathlib import Path

from textual import on
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import (
    Footer,
    Header,
    Input,
    Label,
    Markdown,
    Static,
)

EXPERIMENT_DIR = Path(__file__).parent.parent
RAW_DIR = EXPERIMENT_DIR / "results" / "raw"
SCORED_DIR = EXPERIMENT_DIR / "results" / "scored"
REVIEW_DIR = EXPERIMENT_DIR / "results" / "reviewed"
GOLD_STANDARDS_FILE = EXPERIMENT_DIR / "gold-standards.md"

# Score dimension names per type
IR_DIMS = ["correctness", "specificity", "hallucination", "currency"]
SYNTH_DIMS = ["runs_correctly", "idiomatic", "complete", "hallucination_free"]

DIM_LABELS = {
    "correctness": "Correctness (0=wrong, 1=partial, 2=correct)",
    "specificity": "Specificity (0=vague, 1=some, 2=precise)",
    "hallucination": "Hallucination (0=invented, 1=minor, 2=none)",
    "currency": "Currency (0=deprecated, 1=older, 2=current)",
    "runs_correctly": "Runs correctly (0=errors, 1=minor, 2=as-is)",
    "idiomatic": "Idiomatic (0=not charm, 1=some, 2=conventions)",
    "complete": "Complete (0=missing, 1=partial, 2=all features)",
    "hallucination_free": "Hallucination-free (0=invented, 1=minor, 2=correct)",
}


def load_gold_standard(question_id: str) -> str:
    content = GOLD_STANDARDS_FILE.read_text()
    marker = f"## {question_id}:"
    start = content.find(marker)
    if start == -1:
        return f"Gold standard not found for {question_id}"
    next_section = content.find("\n---\n", start + 1)
    if next_section == -1:
        return content[start:]
    return content[start:next_section]


def load_review_items(
    sample_rate: float = 1.0,
    condition: str | None = None,
    model: str | None = None,
    resume: bool = False,
    seed: int = 42,
) -> list[dict]:
    items = []
    if not SCORED_DIR.exists():
        return items

    for session_dir in sorted(SCORED_DIR.iterdir()):
        scorecard_file = session_dir / "scorecard.json"
        if not scorecard_file.exists():
            continue

        scorecard = json.loads(scorecard_file.read_text())
        if not scorecard.get("scores"):
            continue

        # Filters
        if condition and scorecard.get("condition") != condition:
            continue
        if model and scorecard.get("model") != model:
            continue
        if resume and (REVIEW_DIR / session_dir.name / "review.json").exists():
            continue

        # Load raw result
        raw_result_file = RAW_DIR / session_dir.name / "result.json"
        if not raw_result_file.exists():
            continue
        raw = json.loads(raw_result_file.read_text())

        items.append({
            "session_id": session_dir.name,
            "question_id": scorecard["question_id"],
            "condition": scorecard["condition"],
            "model": scorecard["model"],
            "run_number": scorecard["run_number"],
            "is_synthesis": scorecard.get("is_synthesis", False),
            "question": raw["question"],
            "response": raw.get("claude_output", {}).get("result", ""),
            "judge_scores": scorecard["scores"],
            "gold_standard": load_gold_standard(scorecard["question_id"]),
        })

    # Sample
    if sample_rate < 1.0:
        rng = random.Random(seed)
        k = max(1, int(len(items) * sample_rate))
        items = rng.sample(items, k)

    # Sort by total judge score ascending (perfect scores last)
    def _total_score(item):
        dims = SYNTH_DIMS if item["is_synthesis"] else IR_DIMS
        return sum(item["judge_scores"].get(d, 0) for d in dims)

    items.sort(key=_total_score)

    return items


class ScoreDisplay(Static):
    """Shows a single score dimension with judge value and override."""

    def __init__(self, dim: str, judge_value: int, human_value: int | None = None):
        self.dim = dim
        self.judge_value = judge_value
        self.human_value = human_value if human_value is not None else judge_value
        super().__init__()

    def render(self) -> str:
        label = DIM_LABELS.get(self.dim, self.dim)
        marker = "✓" if self.human_value == self.judge_value else "✎"
        return f"{marker} {label}: judge={self.judge_value}  human=[bold]{self.human_value}[/bold]"


class ReviewApp(App):
    CSS = """
    #main {
        height: 1fr;
    }
    #left-panel {
        width: 1fr;
        border-right: solid $primary;
    }
    #right-panel {
        width: 1fr;
    }
    .panel-scroll {
        height: 1fr;
    }
    #scores-panel {
        height: auto;
        max-height: 18;
        border-top: solid $primary;
        padding: 1;
    }
    #human-note {
        margin-top: 1;
    }
    #status-bar {
        height: 1;
        dock: bottom;
        background: $accent;
        color: $text;
        padding: 0 1;
    }
    .panel-title {
        text-style: bold;
        color: $text;
        background: $surface;
        padding: 0 1;
        width: 100%;
    }
    #notes-display {
        color: $text-muted;
        padding: 0 1;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("n", "next_item", "Next"),
        Binding("p", "prev_item", "Previous"),
        Binding("a", "accept_all", "Accept all"),
        Binding("1", "cycle_dim_1", "Dim 1"),
        Binding("2", "cycle_dim_2", "Dim 2"),
        Binding("3", "cycle_dim_3", "Dim 3"),
        Binding("4", "cycle_dim_4", "Dim 4"),
        Binding("s", "save_review", "Save"),
        Binding("c", "focus_note", "Comment"),
        Binding("tab", "focus_next", "Focus next", show=False),
        Binding("escape", "unfocus_note", "Back to keys", show=False),
    ]

    def __init__(self, items: list[dict]):
        super().__init__()
        self.items = items
        self.current_index = 0
        self.human_scores: dict[str, dict[str, int]] = {}  # session_id -> {dim: score}
        self.human_notes: dict[str, str] = {}  # session_id -> note
        self.saved_count = 0

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(id="main"):
            with Horizontal():
                with Vertical(id="left-panel"):
                    yield Label("Agent Response", classes="panel-title")
                    with VerticalScroll(classes="panel-scroll"):
                        yield Markdown("", id="response-md")
                with Vertical(id="right-panel"):
                    yield Label("Gold Standard", classes="panel-title")
                    with VerticalScroll(classes="panel-scroll"):
                        yield Markdown("", id="gold-md")
            with Vertical(id="scores-panel"):
                yield Static("", id="scores-display")
                yield Static("", id="notes-display")
                yield Input(placeholder="Press [c] to add a note explaining score overrides...", id="human-note")
        yield Static("", id="status-bar")
        yield Footer()

    def on_mount(self) -> None:
        self.title = "Experiment Review Tool"
        self._load_item()

    def _get_dims(self) -> list[str]:
        if not self.items:
            return IR_DIMS
        item = self.items[self.current_index]
        return SYNTH_DIMS if item["is_synthesis"] else IR_DIMS

    def _get_human_scores(self) -> dict[str, int]:
        item = self.items[self.current_index]
        sid = item["session_id"]
        if sid not in self.human_scores:
            # Initialise from judge scores
            dims = self._get_dims()
            self.human_scores[sid] = {
                d: item["judge_scores"].get(d, 0) for d in dims
            }
        return self.human_scores[sid]

    def _load_item(self) -> None:
        if not self.items:
            self.query_one("#response-md", Markdown).update("No items to review.")
            self.query_one("#gold-md", Markdown).update("")
            self.query_one("#scores-display", Static).update("No items.")
            self.query_one("#status-bar", Static).update("Empty queue")
            return

        item = self.items[self.current_index]
        dims = self._get_dims()
        human = self._get_human_scores()

        # Response panel
        header = (
            f"**{item['question_id']}** | "
            f"Condition {item['condition']} | "
            f"{item['model']} | "
            f"Run {item['run_number']}\n\n"
            f"**Question:** {item['question']}\n\n---\n\n"
        )
        self.query_one("#response-md", Markdown).update(header + item["response"])

        # Gold standard panel
        self.query_one("#gold-md", Markdown).update(item["gold_standard"])

        # Scores
        lines = []
        for i, d in enumerate(dims):
            judge_val = item["judge_scores"].get(d, 0)
            human_val = human.get(d, judge_val)
            marker = "✓" if human_val == judge_val else "✎"
            label = DIM_LABELS.get(d, d)
            lines.append(
                f"[{i+1}] {marker} {label}: "
                f"judge={judge_val}  human=[bold]{human_val}[/bold]"
            )
        self.query_one("#scores-display", Static).update("\n".join(lines))

        # Judge notes
        notes_parts = []
        for key in ("correctness_notes", "hallucination_notes", "notes"):
            val = item["judge_scores"].get(key, "")
            if val:
                notes_parts.append(f"{key}: {val}")
        self.query_one("#notes-display", Static).update(
            "\n".join(notes_parts) if notes_parts else ""
        )

        # Restore note for this item
        note_input = self.query_one("#human-note", Input)
        note_input.value = self.human_notes.get(item["session_id"], "")

        # Status
        reviewed = sum(
            1 for it in self.items
            if (REVIEW_DIR / it["session_id"] / "review.json").exists()
        )
        self.query_one("#status-bar", Static).update(
            f"  [{self.current_index + 1}/{len(self.items)}]  "
            f"Saved: {self.saved_count}  "
            f"Reviewed: {reviewed}/{len(self.items)}  "
            f"Keys: [n]ext [p]rev [1-4] cycle score [a]ccept all [c]omment [s]ave [q]uit"
        )

    def _has_changes(self) -> bool:
        """Check if current item has notes or any human score differs from judge."""
        if not self.items:
            return False
        item = self.items[self.current_index]
        sid = item["session_id"]
        if self.human_notes.get(sid, ""):
            return True
        dims = self._get_dims()
        human = self._get_human_scores()
        for d in dims:
            if human.get(d, item["judge_scores"].get(d, 0)) != item["judge_scores"].get(d, 0):
                return True
        return False

    def _auto_save_if_changed(self) -> None:
        """Save current review if there are any changes from judge scores or notes."""
        if self._has_changes():
            self._save_current()

    def _cycle_dim(self, dim_index: int) -> None:
        dims = self._get_dims()
        if dim_index >= len(dims):
            return
        dim = dims[dim_index]
        human = self._get_human_scores()
        current = human.get(dim, 0)
        human[dim] = (current + 1) % 3
        self._auto_save_if_changed()
        self._load_item()

    def action_cycle_dim_1(self) -> None:
        self._cycle_dim(0)

    def action_cycle_dim_2(self) -> None:
        self._cycle_dim(1)

    def action_cycle_dim_3(self) -> None:
        self._cycle_dim(2)

    def action_cycle_dim_4(self) -> None:
        self._cycle_dim(3)

    def action_focus_note(self) -> None:
        """Focus the note input field."""
        self.query_one("#human-note", Input).focus()

    def action_unfocus_note(self) -> None:
        """Unfocus the note input and return to key bindings."""
        self.set_focus(None)
        self._auto_save_if_changed()
        self._load_item()

    @on(Input.Changed, "#human-note")
    def _on_note_changed(self, event: Input.Changed) -> None:
        """Store the note as the user types."""
        if self.items:
            sid = self.items[self.current_index]["session_id"]
            self.human_notes[sid] = event.value

    def action_accept_all(self) -> None:
        """Accept all judge scores as-is and save."""
        item = self.items[self.current_index]
        dims = self._get_dims()
        self.human_scores[item["session_id"]] = {
            d: item["judge_scores"].get(d, 0) for d in dims
        }
        self._save_current()
        self.action_next_item()

    def action_next_item(self) -> None:
        if self.current_index < len(self.items) - 1:
            self.current_index += 1
            self._load_item()

    def action_prev_item(self) -> None:
        if self.current_index > 0:
            self.current_index -= 1
            self._load_item()

    def action_save_review(self) -> None:
        self._save_current()
        self._load_item()

    def _save_current(self) -> None:
        item = self.items[self.current_index]
        human = self._get_human_scores()
        dims = self._get_dims()

        # Calculate agreement
        agreements = {}
        for d in dims:
            judge_val = item["judge_scores"].get(d, 0)
            human_val = human.get(d, judge_val)
            agreements[d] = judge_val == human_val

        note = self.human_notes.get(item["session_id"], "")

        review = {
            "session_id": item["session_id"],
            "question_id": item["question_id"],
            "condition": item["condition"],
            "model": item["model"],
            "run_number": item["run_number"],
            "judge_scores": {d: item["judge_scores"].get(d, 0) for d in dims},
            "human_scores": human,
            "human_note": note if note else None,
            "agreements": agreements,
            "all_agreed": all(agreements.values()),
        }

        review_dir = REVIEW_DIR / item["session_id"]
        review_dir.mkdir(parents=True, exist_ok=True)
        with open(review_dir / "review.json", "w") as f:
            json.dump(review, f, indent=2)

        self.saved_count += 1


def print_agreement_summary():
    """Print agreement stats from completed reviews."""
    if not REVIEW_DIR.exists():
        print("No reviews found.")
        return

    total = 0
    agreed = 0
    dim_agreement: dict[str, list[bool]] = {}

    for review_dir in sorted(REVIEW_DIR.iterdir()):
        review_file = review_dir / "review.json"
        if not review_file.exists():
            continue
        review = json.loads(review_file.read_text())
        total += 1
        if review.get("all_agreed"):
            agreed += 1
        for dim, agree in review.get("agreements", {}).items():
            dim_agreement.setdefault(dim, []).append(agree)

    if total == 0:
        print("No reviews found.")
        return

    print(f"\nAgreement Summary ({total} reviews)")
    print(f"  Overall agreement: {agreed}/{total} ({agreed/total*100:.0f}%)")
    print(f"\n  Per dimension:")
    for dim, vals in sorted(dim_agreement.items()):
        agree_count = sum(vals)
        print(f"    {dim}: {agree_count}/{len(vals)} ({agree_count/len(vals)*100:.0f}%)")


def main():
    parser = argparse.ArgumentParser(description="Review scored responses")
    parser.add_argument(
        "--sample", type=float, default=0.33,
        help="Fraction of sessions to review (default: 0.33)",
    )
    parser.add_argument("--condition", help="Filter by condition (A/B/C/D)")
    parser.add_argument("--model", help="Filter by model (sonnet/opus)")
    parser.add_argument("--resume", action="store_true", help="Skip already reviewed")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for sampling")
    parser.add_argument(
        "--summary", action="store_true",
        help="Print agreement summary and exit",
    )
    args = parser.parse_args()

    if args.summary:
        print_agreement_summary()
        return

    items = load_review_items(
        sample_rate=args.sample,
        condition=args.condition,
        model=args.model,
        resume=args.resume,
        seed=args.seed,
    )

    if not items:
        print("No items to review. Run score_responses.py first.")
        sys.exit(1)

    print(f"Loaded {len(items)} items for review")
    app = ReviewApp(items)
    app.run()

    # Print summary on exit
    print_agreement_summary()


if __name__ == "__main__":
    main()
