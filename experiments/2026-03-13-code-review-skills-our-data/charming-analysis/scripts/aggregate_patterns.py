#!/usr/bin/env python3
"""Analyze aggregate patterns across all classified fixes.

Identifies cross-repo and cross-team patterns from the auto-classification.
"""

import json
from collections import Counter, defaultdict
from pathlib import Path

DATA_DIR = Path("/home/ubuntu/charming-analysis/data")


def main():
    with open(DATA_DIR / "all_classified.json") as f:
        classified = json.load(f)

    with open(DATA_DIR / "all_fixes.json") as f:
        all_fixes = json.load(f)

    # Index fixes by sha for diff lookup
    fix_by_sha = {f['sha']: f for f in all_fixes}

    total = len(classified)
    print(f"Analyzing {total} classified fixes...\n")

    # 1. Which bug areas appear across the most repos?
    area_repos = defaultdict(set)
    area_teams = defaultdict(set)
    area_severity = defaultdict(Counter)
    for c in classified:
        area_repos[c['bug_area']].add(c['repo'])
        area_teams[c['bug_area']].add(c['team'])
        area_severity[c['bug_area']][c['severity']] += 1

    print("=== Cross-Repo Bug Areas (appearing in 10+ repos) ===")
    universal_areas = []
    for area in sorted(area_repos, key=lambda a: len(area_repos[a]), reverse=True):
        repos = area_repos[area]
        teams = area_teams[area]
        sev = area_severity[area]
        if len(repos) >= 10:
            total_area = sum(sev.values())
            print(f"  {area}: {total_area} fixes in {len(repos)} repos across {len(teams)} teams "
                  f"(H:{sev.get('high',0)} M:{sev.get('medium',0)} L:{sev.get('low',0)})")
            universal_areas.append({
                'area': area,
                'fix_count': total_area,
                'repo_count': len(repos),
                'team_count': len(teams),
                'severity': dict(sev),
            })

    # 2. Which bug types are most common in high-severity fixes?
    print("\n=== High-Severity Fix Analysis ===")
    high_sev = [c for c in classified if c['severity'] == 'high']
    high_types = Counter(c['bug_type'] for c in high_sev)
    high_areas = Counter(c['bug_area'] for c in high_sev)
    high_teams = Counter(c['team'] for c in high_sev)
    high_repos = Counter(c['repo'] for c in high_sev)

    print(f"Total high-severity: {len(high_sev)}")
    print(f"  Types: {dict(high_types.most_common(10))}")
    print(f"  Areas: {dict(high_areas.most_common(10))}")
    print(f"  Teams: {dict(high_teams.most_common())}")
    print(f"  Top repos:")
    for repo, count in high_repos.most_common(15):
        print(f"    {repo}: {count}")

    # 3. Conventional vs keyword commit patterns by team
    print("\n=== Commit Convention Adoption ===")
    team_conv = defaultdict(lambda: {'conventional': 0, 'keyword': 0})
    for c in classified:
        team_conv[c['team']][c['classification_method']] += 1

    for team, counts in sorted(team_conv.items()):
        total_t = counts['conventional'] + counts['keyword']
        conv_pct = counts['conventional'] * 100 // total_t if total_t else 0
        print(f"  {team}: {conv_pct}% conventional ({counts['conventional']}/{total_t})")

    # 4. Temporal patterns - are certain bug types increasing or decreasing?
    print("\n=== Temporal Patterns ===")
    year_counts = defaultdict(Counter)
    for c in classified:
        year = c.get('date', '')[:4]
        if year:
            year_counts[year][c['bug_type']] += 1

    for year in sorted(year_counts):
        total_y = sum(year_counts[year].values())
        top = year_counts[year].most_common(3)
        print(f"  {year}: {total_y} fixes (top: {', '.join(f'{t}:{c}' for t,c in top)})")

    # 5. Find most prolific fix patterns in commit subjects
    print("\n=== Common Fix Patterns in Commit Subjects ===")
    subject_words = Counter()
    for c in classified:
        subject = c.get('subject', '').lower()
        # Extract 2-word and 3-word phrases
        words = subject.split()
        for i in range(len(words) - 1):
            bigram = ' '.join(words[i:i+2])
            if any(kw in bigram for kw in ['fix', 'bug', 'correct', 'wrong', 'missing', 'broken']):
                subject_words[bigram] += 1

    print("  Common fix-related phrases:")
    for phrase, count in subject_words.most_common(20):
        print(f"    '{phrase}': {count}")

    # Save aggregate analysis
    analysis = {
        'total_fixes': total,
        'universal_areas': universal_areas,
        'high_severity': {
            'count': len(high_sev),
            'types': dict(high_types.most_common()),
            'areas': dict(high_areas.most_common()),
            'teams': dict(high_teams.most_common()),
            'top_repos': [{'repo': r, 'count': c} for r, c in high_repos.most_common(20)],
        },
        'convention_adoption': {
            team: {'conventional_pct': counts['conventional'] * 100 // (counts['conventional'] + counts['keyword']) if (counts['conventional'] + counts['keyword']) else 0,
                   'total': counts['conventional'] + counts['keyword']}
            for team, counts in team_conv.items()
        },
        'temporal': {year: dict(counts) for year, counts in sorted(year_counts.items())},
    }

    with open(DATA_DIR / "aggregate_analysis.json", 'w') as f:
        json.dump(analysis, f, indent=2)

    print(f"\nSaved to {DATA_DIR / 'aggregate_analysis.json'}")


if __name__ == '__main__':
    main()
