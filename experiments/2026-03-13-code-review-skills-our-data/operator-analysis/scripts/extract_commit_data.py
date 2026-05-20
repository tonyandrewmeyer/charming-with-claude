#!/usr/bin/env python3
"""Extract commit data (message + diff) for all bug fix candidates."""
import subprocess
import json
import os

def get_commit_data(sha):
    """Get full commit message and diff stats for a commit."""
    # Full message
    msg = subprocess.run(
        ['git', 'log', '-1', '--format=%B', sha],
        capture_output=True, text=True
    ).stdout.strip()

    # Diff stat
    stat = subprocess.run(
        ['git', 'diff', '--stat', f'{sha}~1..{sha}', '--'],
        capture_output=True, text=True
    ).stdout.strip()

    # Full diff (limited to avoid huge diffs)
    diff = subprocess.run(
        ['git', 'diff', f'{sha}~1..{sha}', '--', '*.py'],
        capture_output=True, text=True
    ).stdout

    # Truncate very large diffs
    if len(diff) > 50000:
        diff = diff[:50000] + "\n... [TRUNCATED] ..."

    # Subject line
    subject = subprocess.run(
        ['git', 'log', '-1', '--format=%s', sha],
        capture_output=True, text=True
    ).stdout.strip()

    # Date
    date = subprocess.run(
        ['git', 'log', '-1', '--format=%ad', '--date=short', sha],
        capture_output=True, text=True
    ).stdout.strip()

    # Files changed
    files = subprocess.run(
        ['git', 'diff', '--name-only', f'{sha}~1..{sha}'],
        capture_output=True, text=True
    ).stdout.strip()

    return {
        'sha': sha,
        'subject': subject,
        'date': date,
        'message': msg,
        'stat': stat,
        'files_changed': files,
        'diff': diff,
    }

os.chdir('/home/ubuntu/operstor-analysis/operator')

# Conventional fix commits
conventional = []
with open('/home/ubuntu/operstor-analysis/conventional_fixes.txt') as f:
    for line in f:
        parts = line.strip().split('|||')
        if len(parts) >= 3:
            conventional.append(parts[0])

# Non-conventional candidates
nonconv = []
with open('/home/ubuntu/operstor-analysis/candidate_nonconv_fixes.txt') as f:
    for line in f:
        parts = line.strip().split('|||')
        if len(parts) >= 3:
            nonconv.append(parts[0])

print(f"Processing {len(conventional)} conventional fixes...")
all_commits = []
for i, sha in enumerate(conventional):
    try:
        data = get_commit_data(sha)
        data['source'] = 'conventional'
        all_commits.append(data)
    except Exception as e:
        print(f"  Error on {sha}: {e}")
    if (i+1) % 20 == 0:
        print(f"  {i+1}/{len(conventional)} done")

print(f"\nProcessing {len(nonconv)} non-conventional candidates...")
for i, sha in enumerate(nonconv):
    try:
        data = get_commit_data(sha)
        data['source'] = 'nonconventional'
        all_commits.append(data)
    except Exception as e:
        print(f"  Error on {sha}: {e}")
    if (i+1) % 20 == 0:
        print(f"  {i+1}/{len(nonconv)} done")

# Save as JSON
outpath = '/home/ubuntu/operstor-analysis/all_fix_candidates.json'
with open(outpath, 'w') as f:
    json.dump(all_commits, f, indent=2)

print(f"\nSaved {len(all_commits)} commits to {outpath}")
