#!/usr/bin/env python3
"""Analyse scored experiment results and produce summary tables.

Usage:
    python scripts/analyse_results.py
    python scripts/analyse_results.py --output results/analysis.md
"""

import argparse
import json
import statistics
import sys
from collections import defaultdict
from pathlib import Path

EXPERIMENT_DIR = Path(__file__).parent.parent
RAW_DIR = EXPERIMENT_DIR / "results" / "raw"
SCORED_DIR = EXPERIMENT_DIR / "results" / "scored"

# Weights for information retrieval questions
IR_WEIGHTS = {"correctness": 3, "specificity": 2, "hallucination": 3, "currency": 1}
IR_MAX = sum(2 * w for w in IR_WEIGHTS.values())  # 18

# Weights for synthesis tasks
SYNTH_WEIGHTS = {
    "runs_correctly": 3,
    "idiomatic": 2,
    "complete": 2,
    "hallucination_free": 3,
}
SYNTH_MAX = sum(2 * w for w in SYNTH_WEIGHTS.values())  # 20


def load_all_results() -> list[dict]:
    """Load all raw results with their scorecards merged."""
    results = []
    if not RAW_DIR.exists():
        return results

    for session_dir in sorted(RAW_DIR.iterdir()):
        result_file = session_dir / "result.json"
        scorecard_file = SCORED_DIR / session_dir.name / "scorecard.json"

        if not result_file.exists():
            continue

        with open(result_file) as f:
            record = json.load(f)

        if scorecard_file.exists():
            with open(scorecard_file) as f:
                scorecard = json.load(f)
            record["scorecard"] = scorecard
        else:
            record["scorecard"] = None

        # Extract efficiency metrics from claude output
        co = record.get("claude_output", {})
        usage = co.get("usage", {})
        record["metrics"] = {
            "input_tokens": usage.get("input_tokens", 0),
            "output_tokens": usage.get("output_tokens", 0),
            "total_tokens": usage.get("input_tokens", 0) + usage.get("output_tokens", 0),
            "cost_usd": co.get("total_cost_usd", 0),
            "num_turns": co.get("num_turns", 0),
            "wall_time_ms": record.get("wall_time_ms", 0),
            "duration_api_ms": co.get("duration_api_ms", 0),
        }

        results.append(record)

    return results


def weighted_score(scores: dict, is_synthesis: bool) -> float:
    """Calculate weighted score for a response."""
    weights = SYNTH_WEIGHTS if is_synthesis else IR_WEIGHTS
    max_score = SYNTH_MAX if is_synthesis else IR_MAX
    total = 0
    for dim, weight in weights.items():
        total += scores.get(dim, 0) * weight
    return total / max_score * 100  # Normalise to percentage


def analyse_by_condition(results: list[dict]) -> dict:
    """Aggregate scores by condition."""
    by_condition = defaultdict(list)
    for r in results:
        if r.get("scorecard") and r["scorecard"].get("scores"):
            is_synth = r["question_id"].startswith("S")
            score = weighted_score(r["scorecard"]["scores"], is_synth)
            by_condition[r["condition"]].append({
                "score": score,
                "metrics": r["metrics"],
                "question_id": r["question_id"],
                "model": r["model"],
            })
    return dict(by_condition)


def analyse_by_condition_model(results: list[dict]) -> dict:
    """Aggregate scores by (condition, model)."""
    by_cm = defaultdict(list)
    for r in results:
        if r.get("scorecard") and r["scorecard"].get("scores"):
            is_synth = r["question_id"].startswith("S")
            score = weighted_score(r["scorecard"]["scores"], is_synth)
            key = (r["condition"], r["model"])
            by_cm[key].append({
                "score": score,
                "metrics": r["metrics"],
            })
    return dict(by_cm)


def format_summary(results: list[dict]) -> str:
    """Generate a markdown summary of results."""
    lines = ["# Experiment Results: llms.txt for Charm Development\n"]

    if not results:
        lines.append("No results found.\n")
        return "\n".join(lines)

    scored = [r for r in results if r.get("scorecard") and r["scorecard"].get("scores")]
    lines.append(f"**Total sessions:** {len(results)}")
    lines.append(f"**Scored sessions:** {len(scored)}")
    lines.append("")

    # Main results table: by condition
    by_condition = analyse_by_condition(results)
    lines.append("## Overall Scores by Condition\n")
    lines.append("| Condition | Mean Score (%) | Std Dev | n | Mean Tokens | Mean Cost ($) |")
    lines.append("|---|---|---|---|---|---|")
    for cond in ["A", "B", "C", "D"]:
        if cond not in by_condition:
            continue
        items = by_condition[cond]
        scores = [i["score"] for i in items]
        tokens = [i["metrics"]["total_tokens"] for i in items]
        costs = [i["metrics"]["cost_usd"] for i in items if i["metrics"]["cost_usd"]]
        mean_score = statistics.mean(scores)
        std_score = statistics.stdev(scores) if len(scores) > 1 else 0
        mean_tokens = statistics.mean(tokens)
        mean_cost = statistics.mean(costs) if costs else 0
        lines.append(
            f"| {cond} | {mean_score:.1f} | {std_score:.1f} | {len(items)} | "
            f"{mean_tokens:.0f} | {mean_cost:.4f} |"
        )
    lines.append("")

    # By condition × model
    by_cm = analyse_by_condition_model(results)
    lines.append("## Scores by Condition × Model\n")
    lines.append("| Condition | Model | Mean Score (%) | Std Dev | n | Mean Tokens |")
    lines.append("|---|---|---|---|---|---|")
    for cond in ["A", "B", "C", "D"]:
        for model in ["sonnet", "opus"]:
            key = (cond, model)
            if key not in by_cm:
                continue
            items = by_cm[key]
            scores = [i["score"] for i in items]
            tokens = [i["metrics"]["total_tokens"] for i in items]
            mean_score = statistics.mean(scores)
            std_score = statistics.stdev(scores) if len(scores) > 1 else 0
            mean_tokens = statistics.mean(tokens)
            lines.append(
                f"| {cond} | {model} | {mean_score:.1f} | {std_score:.1f} | "
                f"{len(items)} | {mean_tokens:.0f} |"
            )
    lines.append("")

    # By question category
    lines.append("## Scores by Category\n")
    by_cat_cond = defaultdict(lambda: defaultdict(list))
    for r in scored:
        is_synth = r["question_id"].startswith("S")
        score = weighted_score(r["scorecard"]["scores"], is_synth)
        by_cat_cond[r["category"]][r["condition"]].append(score)

    lines.append("| Category | Cond A | Cond B | Cond C | Cond D |")
    lines.append("|---|---|---|---|---|")
    for cat in ["ops_api", "pebble", "jubilant", "charmlibs", "charmcraft", "synthesis"]:
        row = [cat]
        for cond in ["A", "B", "C", "D"]:
            scores = by_cat_cond[cat][cond]
            if scores:
                row.append(f"{statistics.mean(scores):.1f}%")
            else:
                row.append("-")
        lines.append("| " + " | ".join(row) + " |")
    lines.append("")

    # Token efficiency comparison
    lines.append("## Token Efficiency\n")
    lines.append(
        "Token usage is a key metric — markdown docs should be smaller than HTML.\n"
    )
    lines.append("| Condition | Mean Input Tokens | Mean Output Tokens | Mean Total |")
    lines.append("|---|---|---|---|")
    for cond in ["A", "B", "C", "D"]:
        if cond not in by_condition:
            continue
        items = by_condition[cond]
        in_tok = statistics.mean([i["metrics"]["input_tokens"] for i in items])
        out_tok = statistics.mean([i["metrics"]["output_tokens"] for i in items])
        total = in_tok + out_tok
        lines.append(f"| {cond} | {in_tok:.0f} | {out_tok:.0f} | {total:.0f} |")
    lines.append("")

    # Per-question breakdown
    lines.append("## Per-Question Scores\n")
    by_q_cond = defaultdict(lambda: defaultdict(list))
    for r in scored:
        is_synth = r["question_id"].startswith("S")
        score = weighted_score(r["scorecard"]["scores"], is_synth)
        by_q_cond[r["question_id"]][r["condition"]].append(score)

    lines.append("| Question | Cond A | Cond B | Cond C | Cond D |")
    lines.append("|---|---|---|---|---|")
    for qid in ["Q1", "Q2", "Q3", "Q4", "Q5", "Q6", "Q7", "Q8", "Q9", "Q10",
                 "Q11", "Q12", "Q13", "Q14", "Q15", "Q16", "Q17", "Q18", "Q19", "Q20",
                 "S1", "S2", "S3"]:
        row = [qid]
        for cond in ["A", "B", "C", "D"]:
            scores = by_q_cond[qid][cond]
            if scores:
                row.append(f"{statistics.mean(scores):.1f}%")
            else:
                row.append("-")
        lines.append("| " + " | ".join(row) + " |")
    lines.append("")

    # Hallucination rates
    lines.append("## Hallucination Rates\n")
    lines.append("Percentage of responses with score 0 (invented APIs/params).\n")
    halluc_by_cond = defaultdict(lambda: {"total": 0, "hallucinated": 0})
    for r in scored:
        scores = r["scorecard"]["scores"]
        is_synth = r["question_id"].startswith("S")
        dim = "hallucination_free" if is_synth else "hallucination"
        halluc_by_cond[r["condition"]]["total"] += 1
        if scores.get(dim, 2) == 0:
            halluc_by_cond[r["condition"]]["hallucinated"] += 1

    lines.append("| Condition | Hallucination Rate |")
    lines.append("|---|---|")
    for cond in ["A", "B", "C", "D"]:
        data = halluc_by_cond[cond]
        if data["total"]:
            rate = data["hallucinated"] / data["total"] * 100
            lines.append(f"| {cond} | {rate:.1f}% ({data['hallucinated']}/{data['total']}) |")
    lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Analyse experiment results")
    parser.add_argument(
        "--output",
        default=None,
        help="Output file (default: print to stdout)",
    )
    args = parser.parse_args()

    results = load_all_results()
    summary = format_summary(results)

    if args.output:
        output_path = EXPERIMENT_DIR / args.output
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(summary)
        print(f"Analysis written to {output_path}")
    else:
        print(summary)


if __name__ == "__main__":
    main()
