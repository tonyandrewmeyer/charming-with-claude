#!/usr/bin/env python3
"""Extract bug-fix commits from all Charm Tech repositories.

For each repo, identifies fix commits via:
1. Conventional commits: messages starting with 'fix:' or 'fix(...):'
2. Non-conventional commits: keyword scoring (fix, bug, patch, correct, etc.)

Outputs a JSON file per repo in data/ with full commit metadata and diffs.
"""

import json
import os
import re
import subprocess
import sys
from pathlib import Path

BASE_DIR = Path("/home/ubuntu/charm-tech-analysis")
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

REPOS = {
    "operator": BASE_DIR / "operator",
    "charmlibs": BASE_DIR / "charmlibs",
    "jubilant": BASE_DIR / "jubilant",
    "pytest-jubilant": BASE_DIR / "pytest-jubilant",
    "pebble": BASE_DIR / "pebble",
    "concierge": BASE_DIR / "concierge",
    "operator-libs-linux": BASE_DIR / "operator-libs-linux",
    "charmhub-listing-review": BASE_DIR / "charmhub-listing-review",
    "charmcraft-profile-tools": BASE_DIR / "charmcraft-profile-tools",
    "charm-ubuntu": BASE_DIR / "charm-ubuntu",
}

# Conventional fix pattern
CONV_FIX_RE = re.compile(r'^fix[\s(:]', re.IGNORECASE)

# Keyword scoring for non-conventional commits
FIX_KEYWORDS = {
    'fix': 3, 'fixed': 3, 'fixes': 3, 'fixing': 3,
    'bug': 3, 'bugfix': 3,
    'patch': 2, 'patched': 2,
    'correct': 2, 'corrected': 2, 'correction': 2,
    'repair': 2, 'repaired': 2,
    'resolve': 2, 'resolved': 2, 'resolves': 2,
    'workaround': 2,
    'regression': 3,
    'crash': 2, 'crashes': 2,
    'broken': 2, 'break': 1,
    'error': 1, 'errors': 1,
    'issue': 1, 'issues': 1,
    'wrong': 2, 'incorrect': 2,
    'handle': 1, 'handling': 1,
    'missing': 2,
    'prevent': 1, 'avoid': 1,
    'fallback': 1,
}

# Negative keywords (less likely to be fixes)
NEGATIVE_KEYWORDS = {
    'feat': -3, 'feature': -3,
    'add': -2, 'added': -2, 'adding': -2,
    'new': -2,
    'refactor': -2, 'refactored': -2,
    'docs': -3, 'doc': -3, 'documentation': -3,
    'chore': -3,
    'style': -3,
    'ci': -2,
    'test': -1, 'tests': -1,
    'bump': -3, 'version': -2,
    'merge': -3,
    'revert': -2,
    'update dependencies': -3,
    'readme': -3,
    'changelog': -3,
    'license': -3,
}

KEYWORD_THRESHOLD = 3


def score_message(message: str) -> int:
    """Score a commit message for likelihood of being a bug fix."""
    words = re.findall(r'\w+', message.lower())
    score = 0
    for word in words:
        score += FIX_KEYWORDS.get(word, 0)
        score += NEGATIVE_KEYWORDS.get(word, 0)
    # Boost if message contains issue/PR references with "fix"
    if re.search(r'fix(es|ed)?\s*#\d+', message, re.IGNORECASE):
        score += 3
    return score


def get_commit_data(repo_path: Path, sha: str) -> dict:
    """Get full commit data including diff."""
    fmt = '%H%n%an%n%ae%n%aI%n%s%n%b%n---END_BODY---'
    result = subprocess.run(
        ['git', 'log', '-1', f'--format={fmt}', sha],
        capture_output=True, text=True, cwd=repo_path, timeout=30
    )
    lines = result.stdout.split('\n')
    body_lines = []
    i = 5
    while i < len(lines) and lines[i] != '---END_BODY---':
        body_lines.append(lines[i])
        i += 1
    body = '\n'.join(body_lines).strip()

    # Get diff (limit to 50KB to avoid huge diffs)
    diff_result = subprocess.run(
        ['git', 'diff-tree', '-p', '--no-commit-id', sha],
        capture_output=True, text=True, cwd=repo_path, timeout=30
    )
    diff = diff_result.stdout[:50000]
    if len(diff_result.stdout) > 50000:
        diff += '\n... [diff truncated at 50KB]'

    # Get changed files
    files_result = subprocess.run(
        ['git', 'diff-tree', '--no-commit-id', '--name-status', '-r', sha],
        capture_output=True, text=True, cwd=repo_path, timeout=30
    )
    changed_files = files_result.stdout.strip().split('\n') if files_result.stdout.strip() else []

    return {
        'sha': lines[0] if lines else sha,
        'author': lines[1] if len(lines) > 1 else '',
        'email': lines[2] if len(lines) > 2 else '',
        'date': lines[3] if len(lines) > 3 else '',
        'subject': lines[4] if len(lines) > 4 else '',
        'body': body,
        'diff': diff,
        'changed_files': changed_files,
    }


def extract_repo_fixes(repo_name: str, repo_path: Path) -> list[dict]:
    """Extract all fix commits from a repository."""
    if not repo_path.exists():
        print(f"  SKIP: {repo_path} does not exist")
        return []

    # Get all commit SHAs and subjects
    result = subprocess.run(
        ['git', 'log', '--all', '--format=%H %s'],
        capture_output=True, text=True, cwd=repo_path, timeout=60
    )
    commits = []
    for line in result.stdout.strip().split('\n'):
        if not line.strip():
            continue
        parts = line.split(' ', 1)
        if len(parts) == 2:
            commits.append((parts[0], parts[1]))

    fixes = []
    seen_shas = set()

    for sha, subject in commits:
        if sha in seen_shas:
            continue

        is_conventional = bool(CONV_FIX_RE.match(subject))
        keyword_score = score_message(subject)

        if is_conventional or keyword_score >= KEYWORD_THRESHOLD:
            classification = 'conventional' if is_conventional else 'keyword'
            commit_data = get_commit_data(repo_path, sha)
            commit_data['repo'] = repo_name
            commit_data['classification_method'] = classification
            commit_data['keyword_score'] = keyword_score
            fixes.append(commit_data)
            seen_shas.add(sha)

    return fixes


def main():
    repo_filter = sys.argv[1] if len(sys.argv) > 1 else None

    all_fixes = []
    for repo_name, repo_path in sorted(REPOS.items()):
        if repo_filter and repo_name != repo_filter:
            continue
        print(f"Processing {repo_name}...")
        fixes = extract_repo_fixes(repo_name, repo_path)
        print(f"  Found {len(fixes)} fix candidates")
        all_fixes.extend(fixes)

        # Save per-repo file
        repo_file = DATA_DIR / f"{repo_name}_fixes.json"
        with open(repo_file, 'w') as f:
            json.dump(fixes, f, indent=2, default=str)

    # Save combined file
    combined_file = DATA_DIR / "all_fixes.json"
    with open(combined_file, 'w') as f:
        json.dump(all_fixes, f, indent=2, default=str)

    print(f"\nTotal: {len(all_fixes)} fix candidates across all repos")

    # Summary
    by_repo = {}
    for fix in all_fixes:
        repo = fix['repo']
        by_repo.setdefault(repo, {'conventional': 0, 'keyword': 0})
        by_repo[repo][fix['classification_method']] += 1

    print("\nBreakdown:")
    for repo, counts in sorted(by_repo.items()):
        total = counts['conventional'] + counts['keyword']
        print(f"  {repo}: {total} ({counts['conventional']} conventional, {counts['keyword']} keyword)")


if __name__ == '__main__':
    main()
