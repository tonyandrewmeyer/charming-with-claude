#!/usr/bin/env python3
"""Run the llms.txt experiment: 23 questions × 5 conditions × 2 models × 3 runs.

Usage:
    # Full run
    python scripts/run_experiment.py

    # Pilot run (1 run, subset of questions)
    python scripts/run_experiment.py --runs 1 --questions Q1,Q5,S1

    # Single condition/model
    python scripts/run_experiment.py --conditions A --models sonnet

    # Resume from where you left off (skips existing results)
    python scripts/run_experiment.py --resume
"""

import argparse
import json
import os
import random
import shutil
import subprocess
import sys
import time
from pathlib import Path

EXPERIMENT_DIR = Path(__file__).parent.parent
SCRIPTS_DIR = EXPERIMENT_DIR / "scripts"
RESULTS_DIR = EXPERIMENT_DIR / "results" / "raw"
QUESTIONS_FILE = SCRIPTS_DIR / "questions.json"

HOSTS_MARKER = "# llms-txt-experiment"
HOSTS_ENTRY = f"127.0.0.1 documentation.ubuntu.com {HOSTS_MARKER}"

NGINX_LOG = Path.home() / "llms-txt-experiment" / "logs" / "access.log"

# Condition prompts
CONDITION_PROMPTS = {
    "A": "You are writing a Juju charm.",
    "B": None,  # Uses CLAUDE.md + skills (no explicit system prompt override)
    "C": (
        "You are writing a Juju charm. "
        "Documentation is available at documentation.ubuntu.com and supports "
        "the llms.txt standard."
    ),
    "D": None,  # Uses CLAUDE.md + skills + llms.txt hint appended
    "E": (
        "You are writing a Juju charm. "
        "Documentation is available at documentation.ubuntu.com."
    ),  # Like C but no llms.txt hint — tests content negotiation (markdown format) without discovery index
}

# Conditions that need /etc/hosts override (local docs with llms.txt + content negotiation)
LOCAL_DOCS_CONDITIONS = {"C", "D", "E"}

# Conditions that use CLAUDE.md + skills
INSTRUCTIONS_CONDITIONS = {"B", "D"}

MODEL_MAP = {
    "sonnet": "sonnet",
    "opus": "opus",
}


def load_questions() -> list[dict]:
    with open(QUESTIONS_FILE) as f:
        return json.load(f)


def enable_local_docs():
    """Add /etc/hosts entry to redirect documentation.ubuntu.com to localhost."""
    with open("/etc/hosts") as f:
        content = f.read()
    if HOSTS_MARKER not in content:
        subprocess.run(
            ["sudo", "tee", "-a", "/etc/hosts"],
            input=HOSTS_ENTRY + "\n",
            capture_output=True,
            text=True,
        )
        print("  [infra] Local docs enabled")


def disable_local_docs():
    """Remove /etc/hosts entry."""
    subprocess.run(
        ["sudo", "sed", "-i", f"/{HOSTS_MARKER}/d", "/etc/hosts"],
        capture_output=True,
    )
    print("  [infra] Local docs disabled")


def rotate_nginx_log(session_id: str):
    """Copy nginx access log and truncate for this session."""
    session_log_dir = RESULTS_DIR / session_id
    session_log_dir.mkdir(parents=True, exist_ok=True)
    if NGINX_LOG.exists():
        shutil.copy2(NGINX_LOG, session_log_dir / "access.log")
        # Truncate
        subprocess.run(
            ["sudo", "truncate", "-s", "0", str(NGINX_LOG)],
            capture_output=True,
        )


def setup_workdir(condition: str) -> Path:
    """Create an isolated working directory for a session."""
    import tempfile

    workdir = Path(tempfile.mkdtemp(prefix="llmstxt-"))

    if condition in INSTRUCTIONS_CONDITIONS:
        # Copy CLAUDE.md and skills from claude-instructions/
        claude_instructions = (
            Path.home()
            / "charming-with-claude"
            / "claude-instructions"
        )
        claude_md_src = claude_instructions / "CLAUDE.md"
        if claude_md_src.exists():
            shutil.copy2(claude_md_src, workdir / "CLAUDE.md")

            # If condition D, append llms.txt hint to CLAUDE.md
            if condition == "D":
                with open(workdir / "CLAUDE.md", "a") as f:
                    f.write(
                        "\n\n## Documentation\n\n"
                        "Documentation for the Juju charm ecosystem is available at "
                        "documentation.ubuntu.com and supports the llms.txt standard. "
                        "You can fetch llms.txt files from documentation.ubuntu.com/ops/, "
                        "documentation.ubuntu.com/pebble/, "
                        "documentation.ubuntu.com/jubilant/, "
                        "documentation.ubuntu.com/charmlibs/, "
                        "and documentation.ubuntu.com/charmcraft/ "
                        "to get an overview of available documentation.\n"
                    )

        # Copy skills directory
        skills_src = claude_instructions / ".claude"
        if skills_src.exists():
            shutil.copytree(skills_src, workdir / ".claude")

    return workdir


def run_session(
    question: dict,
    condition: str,
    model: str,
    run_number: int,
    session_id: str,
) -> dict:
    """Run a single Claude Code session and capture results."""
    workdir = setup_workdir(condition)

    # Truncate nginx log before session
    if NGINX_LOG.exists():
        subprocess.run(
            ["sudo", "truncate", "-s", "0", str(NGINX_LOG)],
            capture_output=True,
        )

    # Build claude command
    # Note: we don't use --bare because it requires ANTHROPIC_API_KEY
    # (OAuth auth is skipped in bare mode). Instead, we use
    # --no-session-persistence and run in a clean temp workdir for isolation.
    cmd = [
        "claude",
        "-p",
        "--output-format", "json",
        "--dangerously-skip-permissions",
        "--model", MODEL_MAP[model],
        "--max-budget-usd", "2.00",
        "--no-session-persistence",
    ]

    # Set system prompt based on condition
    if condition in ("A", "E"):
        cmd.extend(["--system-prompt", CONDITION_PROMPTS[condition]])
    elif condition == "C":
        cmd.extend(["--system-prompt", CONDITION_PROMPTS["C"]])
    elif condition in ("B", "D"):
        # CLAUDE.md is in the workdir and will be auto-discovered.
        # Use --append-system-prompt for the base charm instruction.
        cmd.extend([
            "--append-system-prompt",
            "You are writing a Juju charm.",
        ])

    # The question itself
    cmd.append(question["question"])

    # Run with timeout
    start_time = time.time()
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300,  # 5 minute timeout per session
            cwd=str(workdir),
        )
        wall_time_ms = int((time.time() - start_time) * 1000)
        stdout = result.stdout
        stderr = result.stderr
    except subprocess.TimeoutExpired:
        wall_time_ms = 300_000
        stdout = ""
        stderr = "TIMEOUT"

    # Parse JSON output
    try:
        claude_output = json.loads(stdout)
    except (json.JSONDecodeError, ValueError):
        claude_output = {"result": stdout, "is_error": True, "parse_error": True}

    # Capture nginx log for this session
    rotate_nginx_log(session_id)

    # Clean up workdir
    shutil.rmtree(workdir, ignore_errors=True)

    # Build result record
    record = {
        "session_id": session_id,
        "question_id": question["id"],
        "category": question["category"],
        "question": question["question"],
        "condition": condition,
        "model": model,
        "run_number": run_number,
        "wall_time_ms": wall_time_ms,
        "claude_output": claude_output,
        "stderr": stderr if stderr else None,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
    }

    return record


def save_result(record: dict):
    """Save a session result to disk."""
    session_dir = RESULTS_DIR / record["session_id"]
    session_dir.mkdir(parents=True, exist_ok=True)
    with open(session_dir / "result.json", "w") as f:
        json.dump(record, f, indent=2)


def build_run_plan(
    questions: list[dict],
    conditions: list[str],
    models: list[str],
    runs: int,
    seed: int = 42,
) -> list[dict]:
    """Build a randomised run plan."""
    plan = []
    for run_number in range(1, runs + 1):
        for question in questions:
            for condition in conditions:
                for model in models:
                    session_id = (
                        f"{question['id']}_{condition}_{model}_run{run_number}"
                    )
                    plan.append({
                        "question": question,
                        "condition": condition,
                        "model": model,
                        "run_number": run_number,
                        "session_id": session_id,
                    })

    # Randomise order within each run
    rng = random.Random(seed)
    # Group by run, shuffle within each run
    by_run: dict[int, list] = {}
    for item in plan:
        by_run.setdefault(item["run_number"], []).append(item)
    result = []
    for run_num in sorted(by_run):
        items = by_run[run_num]
        rng.shuffle(items)
        result.extend(items)

    return result


def main():
    parser = argparse.ArgumentParser(description="Run the llms.txt experiment")
    parser.add_argument(
        "--runs", type=int, default=3, help="Number of runs (default: 3)"
    )
    parser.add_argument(
        "--conditions",
        default="A,B,C,D,E",
        help="Comma-separated conditions (default: A,B,C,D,E)",
    )
    parser.add_argument(
        "--models",
        default="sonnet,opus",
        help="Comma-separated models (default: sonnet,opus)",
    )
    parser.add_argument(
        "--questions",
        default=None,
        help="Comma-separated question IDs to run (default: all)",
    )
    parser.add_argument(
        "--resume", action="store_true", help="Skip sessions with existing results"
    )
    parser.add_argument(
        "--seed", type=int, default=42, help="Random seed for run order"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Print plan without running"
    )
    args = parser.parse_args()

    conditions = [c.strip() for c in args.conditions.split(",")]
    models = [m.strip() for m in args.models.split(",")]

    all_questions = load_questions()
    if args.questions:
        question_ids = {q.strip() for q in args.questions.split(",")}
        questions = [q for q in all_questions if q["id"] in question_ids]
    else:
        questions = all_questions

    plan = build_run_plan(questions, conditions, models, args.runs, args.seed)

    if args.resume:
        plan = [
            p for p in plan
            if not (RESULTS_DIR / p["session_id"] / "result.json").exists()
        ]

    total = len(plan)
    print(f"Plan: {total} sessions")
    print(f"  Questions: {len(questions)}")
    print(f"  Conditions: {conditions}")
    print(f"  Models: {models}")
    print(f"  Runs: {args.runs}")

    if args.dry_run:
        for i, item in enumerate(plan):
            print(
                f"  [{i+1}/{total}] {item['session_id']}: "
                f"{item['question']['id']} cond={item['condition']} "
                f"model={item['model']}"
            )
        return

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    # Track which DNS state we're in to minimise switches
    current_local_docs = False

    try:
        for i, item in enumerate(plan):
            need_local = item["condition"] in LOCAL_DOCS_CONDITIONS

            # Switch DNS if needed
            if need_local and not current_local_docs:
                enable_local_docs()
                current_local_docs = True
            elif not need_local and current_local_docs:
                disable_local_docs()
                current_local_docs = False

            print(
                f"[{i+1}/{total}] {item['session_id']} "
                f"(cond={item['condition']}, model={item['model']})"
            )

            record = run_session(
                question=item["question"],
                condition=item["condition"],
                model=item["model"],
                run_number=item["run_number"],
                session_id=item["session_id"],
            )

            save_result(record)

            # Print summary
            co = record.get("claude_output", {})
            usage = co.get("usage", {})
            cost = co.get("total_cost_usd", "?")
            tokens_in = usage.get("input_tokens", "?")
            tokens_out = usage.get("output_tokens", "?")
            print(
                f"  -> cost=${cost}, tokens={tokens_in}/{tokens_out}, "
                f"wall={record['wall_time_ms']}ms"
            )

    finally:
        # Always clean up DNS
        if current_local_docs:
            disable_local_docs()

    print(f"\nDone. {total} sessions saved to {RESULTS_DIR}")


if __name__ == "__main__":
    main()
