#!/usr/bin/env python3
"""
Generate per-commit bug fix summary markdown files.
Includes ALL fixes (source, tests, docs, CI) with categorization.
"""
import json
import os
import re
from collections import Counter

def classify_bug_area(files_changed, subject, diff):
    """Classify what area of the codebase the bug is in."""
    areas = set()
    files = files_changed.split('\n') if files_changed else []

    for f in files:
        f = f.strip()
        if not f:
            continue
        if 'pebble' in f.lower():
            areas.add('pebble')
        if 'testing' in f.lower() or 'harness' in f.lower():
            areas.add('testing-framework')
        if 'scenario' in f.lower():
            areas.add('scenario')
        if 'model' in f.lower() and 'ops/' in f:
            areas.add('model')
        if 'framework' in f.lower():
            areas.add('framework')
        if 'storage' in f.lower():
            areas.add('storage')
        if 'main' in f.lower() and 'ops/' in f:
            areas.add('main/dispatch')
        if 'charm' in f.lower() and 'ops/' in f:
            areas.add('charm')
        if 'jujucontext' in f.lower() or '_juju_context' in f.lower():
            areas.add('juju-context')
        if 'secret' in f.lower():
            areas.add('secrets')
        if 'relation' in f.lower():
            areas.add('relations')
        if 'log' in f.lower() and 'ops/' in f:
            areas.add('logging')
        if re.search(r'\.(yaml|yml)$', f) and ('.github' in f or 'ci' in f.lower()):
            areas.add('ci')
        if 'setup.' in f or 'pyproject' in f or 'tox' in f:
            areas.add('packaging/build')
        if f.startswith('test') or '/test' in f:
            areas.add('tests')
        if 'doc' in f.lower() or f.endswith('.rst') or f.endswith('.md'):
            areas.add('docs')
        if 'action' in f.lower():
            areas.add('actions')

    # Subject-based hints
    subj_lower = subject.lower()
    if 'secret' in subj_lower:
        areas.add('secrets')
    if 'relation' in subj_lower:
        areas.add('relations')
    if 'pebble' in subj_lower or 'container' in subj_lower:
        areas.add('pebble')
    if 'storage' in subj_lower:
        areas.add('storage')
    if 'harness' in subj_lower:
        areas.add('testing-framework')
    if 'testing' in subj_lower:
        areas.add('testing-framework')
    if 'action' in subj_lower:
        areas.add('actions')
    if 'config' in subj_lower:
        areas.add('config')
    if 'status' in subj_lower:
        areas.add('status')
    if 'network' in subj_lower or 'binding' in subj_lower:
        areas.add('networking')
    if 'security' in subj_lower or 'sqlite' in subj_lower or 'permission' in subj_lower:
        areas.add('security')
    if 'type' in subj_lower and ('annotation' in subj_lower or 'hint' in subj_lower):
        areas.add('type-annotations')
    if 'ci' in subj_lower or 'workflow' in subj_lower:
        areas.add('ci')
    if 'doc' in subj_lower:
        areas.add('docs')

    return sorted(areas) if areas else ['general']


def classify_fix_category(subject, files_changed, diff, message):
    """Categorize what kind of fix this is: source, test, docs, ci, build, etc."""
    subject_lower = subject.lower()
    files = [f.strip() for f in files_changed.split('\n') if f.strip()]

    categories = set()

    # Check files
    src_files = [f for f in files if f.startswith('ops/') and 'test' not in f.lower()]
    test_files = [f for f in files if 'test' in f.lower() or f.startswith('test')]
    doc_files = [f for f in files if f.endswith(('.md', '.rst')) or 'doc' in f.lower()]
    ci_files = [f for f in files if '.github' in f or 'ci' in f.lower()]
    build_files = [f for f in files if any(x in f for x in ['setup.', 'pyproject', 'tox', 'Makefile', 'requirements'])]

    if src_files:
        categories.add('source-fix')
    if test_files:
        categories.add('test-fix')
    if doc_files:
        categories.add('docs-fix')
    if ci_files:
        categories.add('ci-fix')
    if build_files:
        categories.add('build-fix')

    # Subject-based overrides
    if re.search(r'fix (ci|lint|fmt|tox)', subject_lower):
        categories.add('ci-fix')
    if re.search(r'(doc|spelling|typo|docstring)', subject_lower):
        categories.add('docs-fix')
    if re.search(r'fix.*(test|utest|itest)', subject_lower):
        categories.add('test-fix')

    return sorted(categories) if categories else ['source-fix']


def classify_bug_type(subject, diff, message):
    """Classify the type of bug."""
    types = set()
    combined = (subject + ' ' + message).lower()

    if any(w in combined for w in ['keyerror', 'key error', 'attributeerror', 'attribute error',
                                     'typeerror', 'type error', 'nameerror', 'indexerror']):
        types.add('exception-handling')
    if any(w in combined for w in ['crash', 'traceback', 'unhandled']):
        types.add('crash')
    if any(w in combined for w in ['type annotation', 'type hint', 'return type', 'mypy', 'pyright']):
        types.add('type-annotation')
    if any(w in combined for w in ['race', 'concurrent', 'deadlock', 'threading']):
        types.add('concurrency')
    if any(w in combined for w in ['security', 'permission', 'injection', 'sanitiz', 'escap', 'credential',
                                     'sqlite', '0o600']):
        types.add('security')
    if any(w in combined for w in ['memory', 'leak', 'resource', 'cleanup', 'temporary file']):
        types.add('resource-management')
    if any(w in combined for w in ['compat', 'python 3.', 'juju version', 'backward', 'older version']):
        types.add('compatibility')
    if any(w in combined for w in ['wrong value', 'incorrect', 'wrong result', 'returns wrong']):
        types.add('incorrect-result')
    if any(w in combined for w in ['cache', 'stale', 'invalidat']):
        types.add('caching')
    if any(w in combined for w in ['missing', 'not found', 'undefined']):
        types.add('missing-handling')
    if any(w in combined for w in ['immutab', 'mutabl', 'copy', 'shallow', 'deep copy', 'copies']):
        types.add('mutability')
    if any(w in combined for w in ['parsing', 'parse', 'format', 'datetime', 'rfc3339']):
        types.add('parsing')
    if any(w in combined for w in ['import', 'circular', 'cyclic']):
        types.add('import-issue')
    if any(w in combined for w in ['dispatch', 'hook', 'event emission', 'event handling']):
        types.add('event-dispatch')
    if any(w in combined for w in ['api', 'juju', 'tool-', 'hook-tool']):
        types.add('juju-api-interaction')

    return sorted(types) if types else ['logic-error']


def classify_severity(subject, diff, message):
    """Estimate severity."""
    combined = (subject + ' ' + message).lower()

    if any(w in combined for w in ['security', 'permission', 'injection', 'credential', 'sqlite', '0o600']):
        return 'high'
    if any(w in combined for w in ['crash', 'startup', 'dispatch fail', 'unhandled exception', 'traceback',
                                     'data loss', 'corrupt', 'silent fail']):
        return 'high'
    if any(w in combined for w in ['keyerror', 'typeerror', 'attributeerror']):
        return 'medium'
    if any(w in combined for w in ['wrong', 'incorrect', 'broken', 'regression']):
        return 'medium'
    if any(w in combined for w in ['cache', 'stale', 'mutab']):
        return 'medium'
    if any(w in combined for w in ['type annotation', 'type hint', 'docstring', 'typo', 'doc ', 'spelling']):
        return 'low'
    if any(w in combined for w in ['ci', 'lint', 'fmt', 'badge']):
        return 'low'
    return 'medium'


def is_actual_bugfix(commit):
    """Determine if a non-conventional commit is actually a bug fix."""
    if commit['source'] == 'conventional':
        return True

    subject = commit['subject'].lower()
    diff = commit['diff']

    # Strong signals it IS a fix
    fix_signals = [
        r'\bfix\b', r'\bfixed\b', r'\bfixes\b', r'\bfixing\b',
        r'\bbug\b', r'\bbugfix\b',
        r'\bcorrect\b', r'\bcorrected\b',
        r'\bpatch\b', r'\bworkaround\b',
        r'\bregression\b', r'\bbroken\b',
        r'\bprevent\b.*\b(error|crash|fail)',
        r'\bhandle\b.*\b(error|exception|missing)',
        r'\bavoid\b.*\b(error|crash|fail)',
        r'\bensure\b',
        r'\bdon.t\b.*\b(crash|fail)',
    ]

    has_fix_signal = any(re.search(pat, subject) for pat in fix_signals)

    # Strong signals it is NOT a fix
    not_fix_signals = [
        r'^merge (pull|branch|remote)',
        r'^bump version', r'^release\b',
        r'^reorganis', r'^move\b',
        r'^expose\b', r'^add\b(?!.*missing)',
        r'^remove dep',
        r'^use a slightly',
        r'^handle (both|the changes)',  # compatibility work, not bug fix
    ]

    has_not_fix = any(re.search(pat, subject) for pat in not_fix_signals)

    if has_fix_signal and not has_not_fix:
        return True

    # For borderline cases, check if it has meaningful diff
    if has_not_fix:
        return False

    # Score-based for remaining
    score = 0
    if 'fix' in subject:
        score += 2
    if 'error' in subject or 'bug' in subject:
        score += 2
    if 'correct' in subject:
        score += 1
    if any(w in subject for w in ['properly', 'actually', 'should']):
        score += 1
    if len(diff) > 100:
        score += 1

    return score >= 2


def summarize_diff_changes(diff):
    """Extract a human-readable summary of what changed in the diff."""
    if not diff.strip():
        return "No Python file changes in diff."

    lines = diff.split('\n')
    added = [l[1:].strip() for l in lines if l.startswith('+') and not l.startswith('+++')]
    removed = [l[1:].strip() for l in lines if l.startswith('-') and not l.startswith('---')]

    meaningful_added = [l for l in added if l and not l.startswith('#')]
    meaningful_removed = [l for l in removed if l and not l.startswith('#')]

    return {
        'lines_added': len(added),
        'lines_removed': len(removed),
        'meaningful_added': len(meaningful_added),
        'meaningful_removed': len(meaningful_removed),
    }


def main():
    with open('/home/ubuntu/operstor-analysis/all_fix_candidates.json') as f:
        commits = json.load(f)

    outdir = '/home/ubuntu/operstor-analysis/commit-summaries'
    os.makedirs(outdir, exist_ok=True)

    included = []
    excluded = []

    for commit in commits:
        if not is_actual_bugfix(commit):
            excluded.append(commit)
            continue

        areas = classify_bug_area(commit['files_changed'], commit['subject'], commit['diff'])
        bug_types = classify_bug_type(commit['subject'], commit['diff'], commit['message'])
        severity = classify_severity(commit['subject'], commit['diff'], commit['message'])
        fix_categories = classify_fix_category(commit['subject'], commit['files_changed'], commit['diff'], commit['message'])
        diff_stats = summarize_diff_changes(commit['diff'])

        commit['areas'] = areas
        commit['bug_types'] = bug_types
        commit['severity'] = severity
        commit['fix_categories'] = fix_categories
        commit['diff_stats'] = diff_stats
        included.append(commit)

        # Write individual markdown file
        sha_short = commit['sha'][:8]
        filename = f"{commit['date']}_{sha_short}.md"

        with open(os.path.join(outdir, filename), 'w') as f:
            f.write(f"# {commit['subject']}\n\n")
            f.write(f"- **Commit**: [{commit['sha'][:12]}](https://github.com/canonical/operator/commit/{commit['sha']})\n")
            f.write(f"- **Date**: {commit['date']}\n")
            f.write(f"- **Areas**: {', '.join(areas)}\n")
            f.write(f"- **Bug Types**: {', '.join(bug_types)}\n")
            f.write(f"- **Severity**: {severity}\n")
            f.write(f"- **Fix Categories**: {', '.join(fix_categories)}\n")
            if isinstance(diff_stats, dict):
                f.write(f"- **Lines Changed**: +{diff_stats['lines_added']}/-{diff_stats['lines_removed']}\n")
            f.write(f"- **Source**: {commit['source']}\n\n")

            f.write(f"## Commit Message\n\n")
            f.write(f"```\n{commit['message']}\n```\n\n")

            f.write(f"## Files Changed\n\n")
            for fpath in commit['files_changed'].split('\n'):
                if fpath.strip():
                    f.write(f"- `{fpath.strip()}`\n")
            f.write('\n')

            f.write(f"## Diff\n\n")
            f.write(f"```diff\n{commit['diff'][:20000]}\n```\n")

    # Write index
    with open('/home/ubuntu/operstor-analysis/commit-summaries/INDEX.md', 'w') as f:
        f.write("# Bug Fix Commit Index — canonical/operator\n\n")
        f.write(f"Total bug fix commits analyzed: **{len(included)}**\n\n")

        # Summary stats
        f.write("## Statistics\n\n")

        sev_counts = Counter(c['severity'] for c in included)
        f.write(f"| Severity | Count |\n|----------|-------|\n")
        for s in ['high', 'medium', 'low']:
            f.write(f"| {s} | {sev_counts.get(s, 0)} |\n")
        f.write('\n')

        cat_counts = Counter()
        for c in included:
            for cat in c['fix_categories']:
                cat_counts[cat] += 1
        f.write(f"| Fix Category | Count |\n|-------------|-------|\n")
        for cat, count in cat_counts.most_common():
            f.write(f"| {cat} | {count} |\n")
        f.write('\n')

        area_counts = Counter()
        for c in included:
            for a in c['areas']:
                area_counts[a] += 1
        f.write(f"| Area | Count |\n|------|-------|\n")
        for area, count in area_counts.most_common(20):
            f.write(f"| {area} | {count} |\n")
        f.write('\n')

        type_counts = Counter()
        for c in included:
            for t in c['bug_types']:
                type_counts[t] += 1
        f.write(f"| Bug Type | Count |\n|----------|-------|\n")
        for btype, count in type_counts.most_common():
            f.write(f"| {btype} | {count} |\n")
        f.write('\n')

        # All commits table sorted by date
        f.write("## All Bug Fix Commits\n\n")
        f.write("| Date | Commit | Severity | Categories | Subject | Areas | Bug Types |\n")
        f.write("|------|--------|----------|------------|---------|-------|-----------|\n")
        for c in sorted(included, key=lambda x: x['date'], reverse=True):
            sha_short = c['sha'][:8]
            link = f"[{sha_short}](https://github.com/canonical/operator/commit/{c['sha']})"
            areas_str = ', '.join(c['areas'])
            types_str = ', '.join(c['bug_types'])
            cats_str = ', '.join(c['fix_categories'])
            subj = c['subject'].replace('|', '\\|')[:80]
            sev = c['severity']
            f.write(f"| {c['date']} | {link} | {sev} | {cats_str} | {subj} | {areas_str} | {types_str} |\n")

    # Save the filtered data for pattern analysis
    # Remove diff from JSON to keep it manageable (diffs are in individual files)
    summary_data = []
    for c in included:
        entry = {k: v for k, v in c.items() if k != 'diff'}
        summary_data.append(entry)

    with open('/home/ubuntu/operstor-analysis/filtered_fixes.json', 'w') as f:
        json.dump(summary_data, f, indent=2)

    # Also keep full data for deep analysis
    with open('/home/ubuntu/operstor-analysis/filtered_fixes_full.json', 'w') as f:
        json.dump(included, f, indent=2)

    print(f"Included: {len(included)} bug fixes")
    print(f"Excluded: {len(excluded)} non-bug-fix commits")
    print(f"\nSeverity: {dict(sev_counts)}")
    print(f"Categories: {dict(cat_counts.most_common())}")
    print(f"\nTop areas: {area_counts.most_common(15)}")
    print(f"\nTop bug types: {type_counts.most_common(15)}")


if __name__ == '__main__':
    main()
