#!/usr/bin/env python3
"""Generate individual markdown summary files from classified JSON data.

Creates one markdown file per classified fix commit in commit-summaries/,
named {date}_{sha_short}.md, matching the format from operator-analysis.
"""

import json
import os
from pathlib import Path

BASE_DIR = Path("/home/ubuntu/charm-tech-analysis")
DATA_DIR = BASE_DIR / "data"
SUMMARIES_DIR = BASE_DIR / "commit-summaries"
SUMMARIES_DIR.mkdir(exist_ok=True)

CLASSIFIED_FILES = [
    "operator_classified.json",
    "pebble_classified.json",
    "concierge_classified.json",
    "charmlibs_classified.json",
    "jubilant_classified.json",
    "pytest-jubilant_classified.json",
    "operator-libs-linux_classified.json",
    "charmhub-listing-review_classified.json",
    "charmcraft-profile-tools_classified.json",
    "charm-ubuntu_classified.json",
]

# Load the full fix data for diffs
FIX_FILES = [
    "operator_fixes.json",
    "pebble_fixes.json",
    "concierge_fixes.json",
    "charmlibs_fixes.json",
    "jubilant_fixes.json",
    "pytest-jubilant_fixes.json",
    "operator-libs-linux_fixes.json",
    "charmhub-listing-review_fixes.json",
    "charmcraft-profile-tools_fixes.json",
    "charm-ubuntu_fixes.json",
]


def load_fix_data() -> dict[str, dict]:
    """Load all fix data indexed by SHA."""
    by_sha = {}
    for fname in FIX_FILES:
        fpath = DATA_DIR / fname
        if not fpath.exists():
            continue
        with open(fpath) as f:
            for fix in json.load(f):
                by_sha[fix["sha"]] = fix
    return by_sha


def load_classified() -> list[dict]:
    """Load all classified entries."""
    all_entries = []
    for fname in CLASSIFIED_FILES:
        fpath = DATA_DIR / fname
        if not fpath.exists():
            print(f"  SKIP: {fpath} not found")
            continue
        with open(fpath) as f:
            entries = json.load(f)
            all_entries.extend(entries)
    return all_entries


def generate_summary(entry: dict, fix_data: dict | None) -> str:
    """Generate markdown summary for a single commit."""
    sha = entry.get("sha", "unknown")
    sha_short = sha[:8]
    repo = entry.get("repo", "unknown")
    date = entry.get("date", "unknown")
    subject = entry.get("subject", "")
    bug_area = entry.get("bug_area", "unknown")
    bug_type = entry.get("bug_type", "unknown")
    severity = entry.get("severity", "unknown")
    fix_category = entry.get("fix_category", "unknown")
    summary = entry.get("one_line_summary", subject)

    lines = [
        f"# {subject}",
        "",
        f"**Repository**: {repo}",
        f"**Commit**: [{sha_short}](https://github.com/canonical/{repo}/commit/{sha})",
        f"**Date**: {date}",
        "",
        "## Classification",
        "",
        f"| Field | Value |",
        f"|-------|-------|",
        f"| Bug Area | {bug_area} |",
        f"| Bug Type | {bug_type} |",
        f"| Severity | {severity} |",
        f"| Fix Category | {fix_category} |",
        "",
        "## Summary",
        "",
        summary,
        "",
    ]

    if fix_data:
        body = fix_data.get("body", "").strip()
        if body:
            lines.extend([
                "## Commit Message",
                "",
                body,
                "",
            ])

        changed_files = fix_data.get("changed_files", [])
        if changed_files:
            lines.extend([
                "## Changed Files",
                "",
            ])
            for cf in changed_files:
                lines.append(f"- {cf}")
            lines.append("")

        diff = fix_data.get("diff", "").strip()
        if diff:
            # Truncate very long diffs
            if len(diff) > 10000:
                diff = diff[:10000] + "\n... [truncated]"
            lines.extend([
                "## Diff",
                "",
                "```diff",
                diff,
                "```",
                "",
            ])

    return "\n".join(lines)


def main():
    print("Loading fix data...")
    fix_by_sha = load_fix_data()
    print(f"  Loaded {len(fix_by_sha)} fix entries")

    print("Loading classified entries...")
    classified = load_classified()
    print(f"  Loaded {len(classified)} classified entries")

    print("Generating summaries...")
    count = 0
    seen_filenames = set()
    for entry in classified:
        sha = entry.get("sha", "unknown")
        date = entry.get("date", "unknown")
        repo = entry.get("repo", "unknown")

        # Extract date prefix (YYYY-MM-DD)
        date_prefix = date[:10] if len(date) >= 10 else date
        sha_short = sha[:8]

        # Sanitise repo name (remove org prefix if present)
        repo_safe = repo.replace("/", "_").replace("\\", "_")
        filename = f"{date_prefix}_{repo_safe}_{sha_short}.md"
        # Handle duplicates
        if filename in seen_filenames:
            filename = f"{date_prefix}_{repo_safe}_{sha_short}_2.md"
        seen_filenames.add(filename)

        fix_data = fix_by_sha.get(sha)
        content = generate_summary(entry, fix_data)

        outpath = SUMMARIES_DIR / filename
        with open(outpath, "w") as f:
            f.write(content)
        count += 1

    print(f"\nGenerated {count} summary files in {SUMMARIES_DIR}")


if __name__ == "__main__":
    main()
