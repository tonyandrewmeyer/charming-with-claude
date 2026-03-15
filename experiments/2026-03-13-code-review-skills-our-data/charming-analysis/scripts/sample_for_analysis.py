#!/usr/bin/env python3
"""Sample representative fixes for deep analysis by Claude agents.

Strategy: For each team, take all high-severity fixes + a sample of medium ones
from the top repos. Focus on source-code fixes (not CI/docs/test-only).
"""

import json
import re
from collections import Counter, defaultdict
from pathlib import Path

DATA_DIR = Path("/home/ubuntu/charming-analysis/data")


def is_source_fix(fix: dict) -> bool:
    """Check if this fix touches actual charm source code (not just CI/docs/tests)."""
    changed = fix.get('changed_files', [])
    subject = fix.get('subject', '').lower()

    # Skip merge commits
    if subject.startswith('merge'):
        return False

    source_file = False
    for f in changed:
        f_lower = f.lower()
        # Skip if only CI, docs, tests, or config files changed
        if any(p in f_lower for p in ['.github/', 'readme', 'license', 'changelog',
                                        '.pre-commit', 'renovate', 'dependabot']):
            continue
        if re.search(r'\.(py|yaml|yml|json|toml|cfg)$', f_lower):
            source_file = True
            break

    return source_file


def main():
    all_fixes_path = DATA_DIR / "all_fixes.json"
    with open(all_fixes_path) as f:
        all_fixes = json.load(f)

    # Group by repo
    by_repo = defaultdict(list)
    for fix in all_fixes:
        by_repo[fix['repo']].append(fix)

    # For each repo, score fixes for analysis relevance
    sampled = []
    repo_stats = []

    for repo, fixes in sorted(by_repo.items()):
        source_fixes = [f for f in fixes if is_source_fix(f)]

        if not source_fixes:
            repo_stats.append({'repo': repo, 'total': len(fixes), 'source': 0, 'sampled': 0})
            continue

        # Take all fixes for repos with <= 30 source fixes
        # For larger repos, take a representative sample
        if len(source_fixes) <= 30:
            sample = source_fixes
        else:
            # Prioritize: conventional fixes first, then by keyword score
            conv = [f for f in source_fixes if f.get('classification_method') == 'conventional']
            kw = [f for f in source_fixes if f.get('classification_method') == 'keyword']
            # Take up to 25 conventional + 5 keyword
            sample = conv[:25] + kw[:5]

        for fix in sample:
            # Trim diff to save space (keep first 8KB per fix)
            trimmed = dict(fix)
            if len(trimmed.get('diff', '')) > 8000:
                trimmed['diff'] = trimmed['diff'][:8000] + '\n... [truncated]'
            sampled.append(trimmed)

        repo_stats.append({
            'repo': repo,
            'team': fixes[0].get('team', ''),
            'total': len(fixes),
            'source': len(source_fixes),
            'sampled': len(sample)
        })

    # Save sampled fixes
    sample_path = DATA_DIR / "sampled_fixes.json"
    with open(sample_path, 'w') as f:
        json.dump(sampled, f, indent=2, default=str)

    # Save repo stats
    stats_path = DATA_DIR / "sample_stats.json"
    with open(stats_path, 'w') as f:
        json.dump(repo_stats, f, indent=2)

    print(f"Sampled {len(sampled)} fixes from {len([r for r in repo_stats if r.get('sampled', 0) > 0])} repos")
    print(f"Total source fixes across all repos: {sum(r.get('source', 0) for r in repo_stats)}")

    # Team breakdown
    team_samples = Counter()
    for fix in sampled:
        team_samples[fix.get('team', 'unknown')] += 1
    print(f"\nBy team:")
    for team, count in team_samples.most_common():
        print(f"  {team}: {count}")


if __name__ == '__main__':
    main()
