#!/usr/bin/env python3
"""Score experiment responses using Claude as a judge.

Reads raw results from results/raw/, sends each response + gold standard
to Claude for scoring, and saves scorecards to results/scored/.

Usage:
    python scripts/score_responses.py
    python scripts/score_responses.py --resume       # skip already-scored
    python scripts/score_responses.py --dry-run      # preview what would be scored
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

EXPERIMENT_DIR = Path(__file__).parent.parent
RAW_DIR = EXPERIMENT_DIR / "results" / "raw"
SCORED_DIR = EXPERIMENT_DIR / "results" / "scored"
GOLD_STANDARDS_FILE = EXPERIMENT_DIR / "gold-standards.md"

# JSON schema for judge output
SCORE_SCHEMA = json.dumps({
    "type": "object",
    "properties": {
        "correctness": {
            "type": "integer",
            "description": "0=wrong/fabricated, 1=partially correct, 2=fully correct",
            "minimum": 0,
            "maximum": 2,
        },
        "specificity": {
            "type": "integer",
            "description": "0=vague/generic, 1=some specifics, 2=precise API usage",
            "minimum": 0,
            "maximum": 2,
        },
        "hallucination": {
            "type": "integer",
            "description": "0=invented APIs/params, 1=minor inaccuracies, 2=no hallucinations",
            "minimum": 0,
            "maximum": 2,
        },
        "currency": {
            "type": "integer",
            "description": "0=deprecated/removed APIs, 1=older but valid, 2=current recommended",
            "minimum": 0,
            "maximum": 2,
        },
        "correctness_notes": {
            "type": "string",
            "description": "Brief explanation of correctness score",
        },
        "hallucination_notes": {
            "type": "string",
            "description": "List any hallucinated APIs, parameters, or facts",
        },
        "overall_notes": {
            "type": "string",
            "description": "Any other notable observations",
        },
    },
    "required": [
        "correctness",
        "specificity",
        "hallucination",
        "currency",
        "correctness_notes",
        "hallucination_notes",
    ],
})

# For synthesis tasks, use a different schema
SYNTHESIS_SCORE_SCHEMA = json.dumps({
    "type": "object",
    "properties": {
        "runs_correctly": {
            "type": "integer",
            "description": "0=syntax errors/missing imports, 1=minor issues, 2=would run as-is",
            "minimum": 0,
            "maximum": 2,
        },
        "idiomatic": {
            "type": "integer",
            "description": "0=not recognisable as ops charm, 1=some patterns, 2=follows conventions",
            "minimum": 0,
            "maximum": 2,
        },
        "complete": {
            "type": "integer",
            "description": "0=missing major components, 1=structure but missing details, 2=all features",
            "minimum": 0,
            "maximum": 2,
        },
        "hallucination_free": {
            "type": "integer",
            "description": "0=invented APIs, 1=minor API inaccuracies, 2=all API usage correct",
            "minimum": 0,
            "maximum": 2,
        },
        "notes": {
            "type": "string",
            "description": "Key observations about the code quality and correctness",
        },
    },
    "required": [
        "runs_correctly",
        "idiomatic",
        "complete",
        "hallucination_free",
        "notes",
    ],
})


def load_gold_standard(question_id: str) -> str:
    """Extract the gold standard for a specific question from the markdown file."""
    content = GOLD_STANDARDS_FILE.read_text()
    # Find the section for this question
    marker = f"## {question_id}:"
    start = content.find(marker)
    if start == -1:
        return f"Gold standard not found for {question_id}"

    # Find the next section or end of file
    next_section = content.find("\n---\n", start + 1)
    if next_section == -1:
        return content[start:]
    return content[start:next_section]


def build_judge_prompt(question: str, response: str, gold_standard: str, is_synthesis: bool) -> str:
    """Build the prompt for the judge."""
    if is_synthesis:
        return f"""You are scoring a code generation response against a gold standard.

## Question Asked
{question}

## Gold Standard Answer
{gold_standard}

## Agent's Response
{response}

## Scoring Instructions
Score the response on these dimensions (0-2 each):
- **runs_correctly**: Would this code run without errors? (0=syntax errors/missing imports, 1=minor fixable issues, 2=runs as-is)
- **idiomatic**: Does it follow ops charm conventions? (0=not recognisable, 1=some patterns, 2=idiomatic)
- **complete**: Are all requested features implemented? (0=missing major parts, 1=structure only, 2=complete)
- **hallucination_free**: Is all API usage factually correct? (0=invented APIs, 1=minor inaccuracies, 2=all correct)

IMPORTANT — hallucination scoring:
- A hallucination is an API, method, parameter, class, or event that does NOT actually exist in the framework.
- Extra correct details that go beyond the gold standard are NOT hallucinations — score them 2.
- Real APIs used in an unusual way are NOT hallucinations — score them 2 and note it elsewhere if relevant.
- Only score 0 if the response includes something genuinely fabricated that does not exist.
- Score 1 only if there are minor inaccuracies (e.g., wrong default value), not for extra correct content.

IMPORTANT — completeness scoring:
- If the response describes what code would do but does not actually include the code, score complete as 0 or 1.
- The question asks the agent to "write" code, so the code must be present in the response.

Pay attention to the scoring notes in the gold standard.

Respond with ONLY a JSON object (no markdown fencing, no other text):
{{"runs_correctly": <0-2>, "idiomatic": <0-2>, "complete": <0-2>, "hallucination_free": <0-2>, "notes": "<brief notes>"}}"""
    else:
        return f"""You are scoring an information retrieval response against a gold standard.

## Question Asked
{question}

## Gold Standard Answer
{gold_standard}

## Agent's Response
{response}

## Scoring Instructions
Score the response on these dimensions (0-2 each):
- **correctness**: Is the answer factually correct? (0=wrong/fabricated, 1=partially correct, 2=fully correct)
- **specificity**: Does it use precise, framework-specific details? (0=vague/generic, 1=some specifics, 2=precise API names/params)
- **hallucination**: Does it invent APIs, parameters, or facts? (0=invented APIs/params, 1=minor inaccuracies, 2=nothing hallucinated)
- **currency**: Does it use current/recommended APIs? (0=fully removed APIs, 1=older but still valid, 2=current best practice)

IMPORTANT — hallucination scoring:
- A hallucination is an API, method, parameter, class, or event that does NOT actually exist in the framework.
- Extra correct details that go beyond the gold standard are NOT hallucinations — score them 2.
- The gold standard is not exhaustive. Real APIs, parameters, and features that exist but are not mentioned in the gold standard are NOT hallucinations.
- Only score 0 if the response includes something genuinely fabricated that does not exist.
- Score 1 only for minor factual inaccuracies (e.g., wrong default value, wrong type), not for extra correct content.

IMPORTANT — correctness scoring:
- The gold standard may not be exhaustive. If the response includes correct additional detail beyond the gold standard, that is NOT a correctness error — score 2.
- Score 1 for answers that are partially correct but miss key details from the gold standard.
- Score 0 only for answers that are fundamentally wrong or fabricated.

IMPORTANT — currency scoring:
- Score 1 (not 0) for older patterns that still work (e.g., deprecated but functional APIs).
- Score 0 only for APIs or patterns that have been fully removed and no longer function.

Compare against the gold standard, but remember it is a reference, not an exhaustive list of all valid answers.

Respond with ONLY a JSON object (no markdown fencing, no other text):
{{"correctness": <0-2>, "specificity": <0-2>, "hallucination": <0-2>, "currency": <0-2>, "correctness_notes": "<brief>", "hallucination_notes": "<list any hallucinated items or 'none'>"}}"""


def score_response(session_id: str, record: dict) -> dict | None:
    """Score a single response using Claude as judge."""
    claude_output = record.get("claude_output", {})
    response = claude_output.get("result", "")

    if not response or claude_output.get("is_error"):
        return {
            "session_id": session_id,
            "error": "No valid response to score",
            "scores": None,
        }

    question_id = record["question_id"]
    is_synthesis = question_id.startswith("S")
    gold_standard = load_gold_standard(question_id)

    prompt = build_judge_prompt(
        question=record["question"],
        response=response,
        gold_standard=gold_standard,
        is_synthesis=is_synthesis,
    )

    cmd = [
        "claude",
        "-p",
        "--output-format", "json",
        "--model", "sonnet",
        "--max-budget-usd", "0.50",
        "--no-session-persistence",
        "--dangerously-skip-permissions",
        prompt,
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,
        )
        judge_output = json.loads(result.stdout)
        result_text = judge_output.get("result", "")
        # Strip markdown code fences if present
        result_text = result_text.strip()
        if result_text.startswith("```"):
            result_text = "\n".join(result_text.split("\n")[1:])
        if result_text.endswith("```"):
            result_text = "\n".join(result_text.split("\n")[:-1])
        scores = json.loads(result_text.strip())
    except (subprocess.TimeoutExpired, json.JSONDecodeError, ValueError) as e:
        return {
            "session_id": session_id,
            "error": str(e),
            "scores": None,
        }

    return {
        "session_id": session_id,
        "question_id": question_id,
        "condition": record["condition"],
        "model": record["model"],
        "run_number": record["run_number"],
        "is_synthesis": is_synthesis,
        "scores": scores,
        "judge_cost_usd": judge_output.get("total_cost_usd"),
        "judge_usage": judge_output.get("usage"),
    }


def main():
    parser = argparse.ArgumentParser(description="Score experiment responses")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if not RAW_DIR.exists():
        print(f"No results found at {RAW_DIR}")
        sys.exit(1)

    SCORED_DIR.mkdir(parents=True, exist_ok=True)

    sessions = sorted(RAW_DIR.iterdir())
    if args.resume:
        sessions = [
            s for s in sessions
            if not (SCORED_DIR / s.name / "scorecard.json").exists()
        ]

    total = len(sessions)
    print(f"Scoring {total} sessions")

    if args.dry_run:
        for s in sessions:
            print(f"  Would score: {s.name}")
        return

    for i, session_dir in enumerate(sessions):
        result_file = session_dir / "result.json"
        if not result_file.exists():
            continue

        with open(result_file) as f:
            record = json.load(f)

        print(f"[{i+1}/{total}] Scoring {session_dir.name}...", end=" ", flush=True)
        scorecard = score_response(session_dir.name, record)

        if scorecard:
            scored_session_dir = SCORED_DIR / session_dir.name
            scored_session_dir.mkdir(parents=True, exist_ok=True)
            with open(scored_session_dir / "scorecard.json", "w") as f:
                json.dump(scorecard, f, indent=2)

            if scorecard.get("scores"):
                scores = scorecard["scores"]
                score_vals = [v for v in scores.values() if isinstance(v, int)]
                print(f"scores={score_vals}")
            else:
                print(f"error: {scorecard.get('error', 'unknown')}")
        else:
            print("failed")

    print(f"\nDone. Scorecards saved to {SCORED_DIR}")


if __name__ == "__main__":
    main()
