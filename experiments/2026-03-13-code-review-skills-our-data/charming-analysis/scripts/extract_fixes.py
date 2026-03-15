#!/usr/bin/env python3
"""Extract bug-fix commits from charm repositories.

For each repo, identifies fix commits via:
1. Conventional commits: messages starting with 'fix:' or 'fix(...):'
2. Non-conventional commits: keyword scoring (fix, bug, patch, correct, etc.)

Outputs a JSON file per repo in data/ with full commit metadata and diffs.
"""

import csv
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse

BASE_DIR = Path("/home/ubuntu/charming-analysis")
REPOS_DIR = BASE_DIR / "repos"
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
REPOS_DIR.mkdir(exist_ok=True)

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
    'readme': -3,
    'changelog': -3,
    'license': -3,
    'lint': -2, 'linting': -2,
    'format': -2, 'formatting': -2,
    'dependency': -2, 'dependencies': -2,
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
    if result.returncode != 0:
        print(f"  ERROR: git log failed for {repo_name}")
        return []

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
            try:
                commit_data = get_commit_data(repo_path, sha)
                commit_data['repo'] = repo_name
                commit_data['classification_method'] = classification
                commit_data['keyword_score'] = keyword_score
                fixes.append(commit_data)
                seen_shas.add(sha)
            except subprocess.TimeoutExpired:
                print(f"  TIMEOUT: {sha[:12]} in {repo_name}")
            except Exception as e:
                print(f"  ERROR: {sha[:12]} in {repo_name}: {e}")

    return fixes


def parse_repos_from_csv(csv_path: Path) -> list[dict]:
    """Parse charm repos from CSV, returning unique GitHub repos."""
    repos = []
    seen_urls = set()

    with open(csv_path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            url = row.get('Repository', '').strip().rstrip('/')
            if not url:
                continue
            # Only GitHub repos (skip launchpad, opendev)
            if 'github.com' not in url:
                continue
            if url in seen_urls:
                continue
            seen_urls.add(url)

            # Extract repo name from URL
            parsed = urlparse(url)
            path_parts = parsed.path.strip('/').split('/')
            if len(path_parts) >= 2:
                repo_name = path_parts[-1]
            else:
                continue

            repos.append({
                'name': repo_name,
                'url': url,
                'team': row.get('Team', ''),
                'charm_name': row.get('Charm Name', ''),
                'key_charm': row.get('Key Charm for this Team', '') == 'TRUE',
                'branch': row.get('Branch (if not the default)', ''),
            })

    return repos


def clone_repo(repo: dict) -> Path:
    """Clone a repo (shallow) if not already present."""
    repo_path = REPOS_DIR / repo['name']
    if repo_path.exists():
        return repo_path

    try:
        subprocess.run(
            ['git', 'clone', '--no-tags', repo['url'] + '.git', str(repo_path)],
            capture_output=True, text=True, timeout=120
        )
    except subprocess.TimeoutExpired:
        print(f"  TIMEOUT cloning {repo['name']}")
    except Exception as e:
        print(f"  ERROR cloning {repo['name']}: {e}")

    return repo_path


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else 'all'

    csv_path = BASE_DIR / "charms.csv"
    repos = parse_repos_from_csv(csv_path)
    print(f"Found {len(repos)} unique GitHub repos in CSV")

    if mode == 'clone':
        # Just clone all repos
        for i, repo in enumerate(repos):
            print(f"[{i+1}/{len(repos)}] Cloning {repo['name']}...")
            clone_repo(repo)
        return

    if mode == 'extract' or mode == 'all':
        all_fixes = []
        stats = []

        for i, repo in enumerate(repos):
            repo_path = REPOS_DIR / repo['name']
            print(f"[{i+1}/{len(repos)}] Extracting from {repo['name']}...")

            fixes = extract_repo_fixes(repo['name'], repo_path)
            if not fixes:
                stats.append({'repo': repo['name'], 'team': repo['team'], 'total': 0, 'conventional': 0, 'keyword': 0})
                continue

            # Add team metadata
            for fix in fixes:
                fix['team'] = repo['team']
                fix['charm_name'] = repo['charm_name']

            all_fixes.extend(fixes)

            conv = sum(1 for f in fixes if f['classification_method'] == 'conventional')
            kw = len(fixes) - conv
            stats.append({'repo': repo['name'], 'team': repo['team'], 'total': len(fixes), 'conventional': conv, 'keyword': kw})
            print(f"  Found {len(fixes)} fixes ({conv} conventional, {kw} keyword)")

            # Save per-repo file
            repo_file = DATA_DIR / f"{repo['name']}_fixes.json"
            with open(repo_file, 'w') as f:
                json.dump(fixes, f, indent=2, default=str)

        # Save combined file
        combined_file = DATA_DIR / "all_fixes.json"
        with open(combined_file, 'w') as f:
            json.dump(all_fixes, f, indent=2, default=str)

        # Save stats
        stats_file = DATA_DIR / "extraction_stats.json"
        with open(stats_file, 'w') as f:
            json.dump(stats, f, indent=2)

        print(f"\nTotal: {len(all_fixes)} fix candidates across {len(repos)} repos")
        print(f"\nTop repos by fix count:")
        for s in sorted(stats, key=lambda x: x['total'], reverse=True)[:20]:
            if s['total'] > 0:
                print(f"  {s['repo']}: {s['total']} ({s['conventional']} conv, {s['keyword']} kw) [{s['team']}]")


if __name__ == '__main__':
    main()
