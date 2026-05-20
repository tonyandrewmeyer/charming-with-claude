#!/usr/bin/env python3
"""Prepare fix data into batches for Claude agent analysis.

Groups fixes by team and splits into manageable batch files (~30 fixes each)
with just the info needed for classification (subject, diff summary, changed files).
"""

import json
from collections import defaultdict
from pathlib import Path

DATA_DIR = Path("/home/ubuntu/charming-analysis/data")
BATCH_DIR = DATA_DIR / "batches"
BATCH_DIR.mkdir(exist_ok=True)

MAX_BATCH_SIZE = 40  # fixes per batch


def summarize_diff(diff: str, max_lines: int = 60) -> str:
    """Extract just the meaningful changed lines from a diff."""
    if not diff:
        return "(no diff available)"

    lines = diff.split('\n')
    summary_lines = []
    current_file = None

    for line in lines:
        if line.startswith('diff --git'):
            # Extract filename
            parts = line.split(' b/')
            if len(parts) > 1:
                current_file = parts[-1]
                summary_lines.append(f"\n--- {current_file} ---")
        elif line.startswith('@@'):
            summary_lines.append(line)
        elif line.startswith('+') and not line.startswith('+++'):
            summary_lines.append(line)
        elif line.startswith('-') and not line.startswith('---'):
            summary_lines.append(line)

        if len(summary_lines) >= max_lines:
            summary_lines.append('... (truncated)')
            break

    return '\n'.join(summary_lines)


def main():
    sample_path = DATA_DIR / "sampled_fixes.json"
    with open(sample_path) as f:
        fixes = json.load(f)

    # Group by team
    by_team = defaultdict(list)
    for fix in fixes:
        by_team[fix.get('team', 'unknown')].append(fix)

    batch_idx = 0
    batch_manifest = []

    for team, team_fixes in sorted(by_team.items()):
        # Group by repo within team
        by_repo = defaultdict(list)
        for fix in team_fixes:
            by_repo[fix['repo']].append(fix)

        current_batch = []
        current_batch_repos = set()

        for repo, repo_fixes in sorted(by_repo.items()):
            for fix in repo_fixes:
                entry = {
                    'sha': fix['sha'][:12],
                    'repo': fix['repo'],
                    'team': team,
                    'date': fix.get('date', '')[:10],
                    'subject': fix.get('subject', ''),
                    'body': fix.get('body', '')[:500],
                    'changed_files': fix.get('changed_files', []),
                    'diff_summary': summarize_diff(fix.get('diff', ''), max_lines=40),
                }
                current_batch.append(entry)
                current_batch_repos.add(repo)

                if len(current_batch) >= MAX_BATCH_SIZE:
                    batch_path = BATCH_DIR / f"batch_{batch_idx:03d}.json"
                    with open(batch_path, 'w') as f:
                        json.dump(current_batch, f, indent=2)
                    batch_manifest.append({
                        'batch_id': batch_idx,
                        'team': team,
                        'repos': sorted(current_batch_repos),
                        'count': len(current_batch),
                        'path': str(batch_path),
                    })
                    batch_idx += 1
                    current_batch = []
                    current_batch_repos = set()

        # Flush remaining
        if current_batch:
            batch_path = BATCH_DIR / f"batch_{batch_idx:03d}.json"
            with open(batch_path, 'w') as f:
                json.dump(current_batch, f, indent=2)
            batch_manifest.append({
                'batch_id': batch_idx,
                'team': team,
                'repos': sorted(current_batch_repos),
                'count': len(current_batch),
                'path': str(batch_path),
            })
            batch_idx += 1
            current_batch = []
            current_batch_repos = set()

    # Save manifest
    manifest_path = DATA_DIR / "batch_manifest.json"
    with open(manifest_path, 'w') as f:
        json.dump(batch_manifest, f, indent=2)

    print(f"Created {batch_idx} batches")
    for b in batch_manifest:
        print(f"  Batch {b['batch_id']:3d}: {b['team']:20s} {b['count']:3d} fixes from {', '.join(b['repos'][:3])}{'...' if len(b['repos']) > 3 else ''}")


if __name__ == '__main__':
    main()
