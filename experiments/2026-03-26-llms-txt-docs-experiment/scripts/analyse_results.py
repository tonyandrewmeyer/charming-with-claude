#!/usr/bin/env python3
"""Analyse scored experiment results and produce summary tables.

Usage:
    python scripts/analyse_results.py
    python scripts/analyse_results.py --output results/analysis.md
"""

import argparse
import json
import re
import statistics
import sys
from collections import defaultdict
from pathlib import Path

EXPERIMENT_DIR = Path(__file__).parent.parent
RAW_DIR = EXPERIMENT_DIR / "results" / "raw"
SCORED_DIR = EXPERIMENT_DIR / "results" / "scored"

# nginx combined log pattern
NGINX_LOG_RE = re.compile(
    r'(?P<ip>\S+) \S+ \S+ \[(?P<time>[^\]]+)\] '
    r'"(?P<method>\S+) (?P<path>\S+) \S+" (?P<status>\d+) (?P<bytes>\d+) '
    r'"[^"]*" "(?P<ua>[^"]*)"'
)

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


def parse_nginx_log(log_path: Path) -> list[dict]:
    """Parse an nginx access log into structured entries."""
    entries = []
    if not log_path.exists():
        return entries
    for line in log_path.read_text().splitlines():
        m = NGINX_LOG_RE.match(line)
        if m:
            entries.append(m.groupdict())
    return entries


def analyse_nginx_log(entries: list[dict]) -> dict:
    """Extract doc access metrics from parsed nginx log entries."""
    if not entries:
        return {
            "total_fetches": 0,
            "total_bytes": 0,
            "pages_visited": [],
            "first_page": None,
            "repos_consulted": [],
            "html_fetches": 0,
            "md_fetches": 0,
            "llms_txt_fetches": 0,
            "llms_full_fetches": 0,
            "status_404_count": 0,
        }

    pages = []
    repos = set()
    html_fetches = 0
    md_fetches = 0
    llms_txt_fetches = 0
    llms_full_fetches = 0
    status_404 = 0
    total_bytes = 0

    for e in entries:
        path = e["path"]
        status = int(e["status"])
        total_bytes += int(e.get("bytes", 0))
        pages.append(path)

        if status == 404:
            status_404 += 1

        # Classify fetch type
        if path.endswith("/llms.txt"):
            llms_txt_fetches += 1
        elif path.endswith("/llms-full.txt"):
            llms_full_fetches += 1
        elif path.endswith(".md"):
            md_fetches += 1
        elif path.endswith(".html") or "/" in path.rstrip("/"):
            html_fetches += 1

        # Extract repo from path
        parts = path.strip("/").split("/")
        if parts:
            repo = parts[0]
            if repo in ("ops", "pebble", "jubilant", "charmlibs", "charmcraft"):
                repos.add(repo)

    return {
        "total_fetches": len(entries),
        "total_bytes": total_bytes,
        "pages_visited": pages,
        "unique_pages": len(set(pages)),
        "first_page": pages[0] if pages else None,
        "repos_consulted": sorted(repos),
        "html_fetches": html_fetches,
        "md_fetches": md_fetches,
        "llms_txt_fetches": llms_txt_fetches,
        "llms_full_fetches": llms_full_fetches,
        "status_404_count": status_404,
    }


def load_all_results() -> list[dict]:
    """Load all raw results with their scorecards and nginx logs merged."""
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

        # Parse nginx access log for this session
        nginx_log = session_dir / "access.log"
        nginx_entries = parse_nginx_log(nginx_log)
        record["nginx"] = analyse_nginx_log(nginx_entries)

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

    # === Doc Access Metrics (from nginx logs) ===

    # Only analyse sessions that have nginx data with fetches
    sessions_with_nginx = [r for r in results if r.get("nginx", {}).get("total_fetches", 0) > 0]

    if sessions_with_nginx:
        lines.append("## Doc Access Patterns (nginx logs)\n")
        lines.append(
            "Metrics from nginx access logs — only available for conditions C/D "
            "(local docs with llms.txt). Conditions A/B use real internet so no "
            "nginx logs are captured.\n"
        )

        # Overall fetch stats by condition
        nginx_by_cond = defaultdict(list)
        for r in results:
            nginx_by_cond[r["condition"]].append(r.get("nginx", {}))

        lines.append("### Fetch Summary\n")
        lines.append(
            "| Condition | Mean Fetches | Mean Bytes | Mean Unique Pages "
            "| Mean 404s |"
        )
        lines.append("|---|---|---|---|---|")
        for cond in ["A", "B", "C", "D"]:
            items = nginx_by_cond[cond]
            fetches = [i.get("total_fetches", 0) for i in items]
            if not any(fetches):
                lines.append(f"| {cond} | - | - | - | - |")
                continue
            bytes_list = [i.get("total_bytes", 0) for i in items]
            unique = [i.get("unique_pages", 0) for i in items]
            fours = [i.get("status_404_count", 0) for i in items]
            lines.append(
                f"| {cond} | {statistics.mean(fetches):.1f} "
                f"| {statistics.mean(bytes_list):.0f} "
                f"| {statistics.mean(unique):.1f} "
                f"| {statistics.mean(fours):.1f} |"
            )
        lines.append("")

        # HTML vs Markdown preference
        lines.append("### Format Preference (conditions C/D only)\n")
        lines.append(
            "Does the agent prefer llms.txt, llms-full.txt, per-page .md, or HTML?\n"
        )
        lines.append(
            "| Condition | llms.txt | llms-full.txt | Per-page .md | HTML | Total |"
        )
        lines.append("|---|---|---|---|---|---|")
        for cond in ["C", "D"]:
            items = nginx_by_cond[cond]
            llms = sum(i.get("llms_txt_fetches", 0) for i in items)
            full = sum(i.get("llms_full_fetches", 0) for i in items)
            md = sum(i.get("md_fetches", 0) for i in items)
            html = sum(i.get("html_fetches", 0) for i in items)
            total = llms + full + md + html
            if total:
                lines.append(
                    f"| {cond} | {llms} ({llms/total*100:.0f}%) "
                    f"| {full} ({full/total*100:.0f}%) "
                    f"| {md} ({md/total*100:.0f}%) "
                    f"| {html} ({html/total*100:.0f}%) "
                    f"| {total} |"
                )
            else:
                lines.append(f"| {cond} | 0 | 0 | 0 | 0 | 0 |")
        lines.append("")

        # First page fetched
        lines.append("### First Page Fetched\n")
        lines.append("What does the agent reach for first?\n")
        first_pages_by_cond = defaultdict(list)
        for r in sessions_with_nginx:
            fp = r["nginx"].get("first_page")
            if fp:
                first_pages_by_cond[r["condition"]].append(fp)

        for cond in ["C", "D"]:
            fps = first_pages_by_cond.get(cond, [])
            if fps:
                lines.append(f"**Condition {cond}:**")
                counts = defaultdict(int)
                for fp in fps:
                    counts[fp] += 1
                for page, count in sorted(counts.items(), key=lambda x: -x[1]):
                    lines.append(f"- `{page}` ({count}×)")
                lines.append("")

        # Repos consulted per question category
        lines.append("### Repos Consulted by Question Category\n")
        lines.append(
            "Does llms.txt help the agent go to the right repo?\n"
        )
        repo_by_cat = defaultdict(lambda: defaultdict(list))
        for r in sessions_with_nginx:
            repos = r["nginx"].get("repos_consulted", [])
            repo_by_cat[r["category"]][r["condition"]].append(repos)

        lines.append("| Category | Condition | Repos Visited |")
        lines.append("|---|---|---|")
        for cat in ["ops_api", "pebble", "jubilant", "charmlibs", "charmcraft", "synthesis"]:
            for cond in ["C", "D"]:
                items = repo_by_cat[cat].get(cond, [])
                if items:
                    all_repos = [r for repos in items for r in repos]
                    repo_counts = defaultdict(int)
                    for r in all_repos:
                        repo_counts[r] += 1
                    summary = ", ".join(
                        f"{r}({c})" for r, c in sorted(repo_counts.items(), key=lambda x: -x[1])
                    )
                    lines.append(f"| {cat} | {cond} | {summary or 'none'} |")
        lines.append("")

        # Bytes fetched vs tokens consumed
        lines.append("### Bytes Fetched vs Tokens Consumed\n")
        lines.append(
            "Compares raw bytes from nginx with input tokens billed. "
            "Lower bytes/token ratio means the doc format is more efficient.\n"
        )
        lines.append("| Condition | Mean Bytes Fetched | Mean Input Tokens | Bytes/Token |")
        lines.append("|---|---|---|---|")
        for cond in ["C", "D"]:
            items_nginx = nginx_by_cond[cond]
            items_cond = by_condition.get(cond, [])
            bytes_list = [i.get("total_bytes", 0) for i in items_nginx if i.get("total_bytes")]
            tokens_list = [i["metrics"]["input_tokens"] for i in items_cond if i["metrics"]["input_tokens"]]
            if bytes_list and tokens_list:
                mean_bytes = statistics.mean(bytes_list)
                mean_tokens = statistics.mean(tokens_list)
                ratio = mean_bytes / mean_tokens if mean_tokens else 0
                lines.append(f"| {cond} | {mean_bytes:.0f} | {mean_tokens:.0f} | {ratio:.1f} |")
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
