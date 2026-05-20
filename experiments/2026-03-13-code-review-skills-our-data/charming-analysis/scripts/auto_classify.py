#!/usr/bin/env python3
"""Auto-classify fix commits by bug area, type, and severity using heuristics.

This handles the bulk classification of 6000+ fixes. For deep pattern analysis,
we'll use Claude agents on representative samples.
"""

import json
import re
from collections import Counter
from pathlib import Path

DATA_DIR = Path("/home/ubuntu/charming-analysis/data")


def classify_bug_area(fix: dict) -> str:
    """Classify the bug area based on changed files and commit message."""
    subject = fix.get('subject', '').lower()
    body = fix.get('body', '').lower()
    changed = ' '.join(fix.get('changed_files', [])).lower()
    diff = fix.get('diff', '').lower()
    msg = subject + ' ' + body

    # Check changed files and diff content for area indicators
    checks = [
        # Charm-specific areas
        ('relation-data', [
            r'relation[_\s]data', r'relation\.data', r'set_relation_data',
            r'get_relation_data', r'relation_joined', r'relation_changed',
            r'relation_departed', r'relation_broken', r'RelationData',
        ]),
        ('pebble', [
            r'pebble', r'container\.', r'workload', r'layer',
            r'PebbleReady', r'pebble_ready', r'get_plan', r'add_layer',
            r'replan', r'push_file', r'pull_file',
        ]),
        ('secrets', [
            r'juju.?secret', r'secret_id', r'secret\.', r'add_secret',
            r'get_secret', r'set_secret', r'grant_secret',
        ]),
        ('tls-certificates', [
            r'tls', r'certificate', r'cert[\s_]', r'ssl', r'ca[\s_]cert',
            r'csr', r'private.?key', r'x509',
        ]),
        ('config-handling', [
            r'config[_\s]changed', r'charm.?config', r'config\.yaml',
            r'self\.config', r'model\.config', r'config\[', r'config\.get',
        ]),
        ('status-management', [
            r'status', r'ActiveStatus', r'BlockedStatus', r'WaitingStatus',
            r'MaintenanceStatus', r'set_status', r'unit\.status',
            r'app\.status', r'collect.?status',
        ]),
        ('storage', [
            r'storage[_\s]', r'StorageAttached', r'storage_path',
            r'juju.?storage',
        ]),
        ('actions', [
            r'action[_\s]', r'ActionEvent', r'on\..*_action',
            r'actions\.yaml',
        ]),
        ('upgrade', [
            r'upgrade', r'rollback', r'migration',
        ]),
        ('ingress-networking', [
            r'ingress', r'traefik', r'nginx', r'proxy', r'reverse.?proxy',
            r'url_prefix', r'route', r'external.?url',
        ]),
        ('database', [
            r'postgresql', r'mysql', r'mongodb', r'redis', r'database',
            r'db_relation', r'dsn', r'connection.?string', r'pgbouncer',
            r'opensearch', r'elasticsearch', r'kafka', r'zookeeper',
        ]),
        ('snap-management', [
            r'snap[\s\._]', r'snapd', r'snap\.install', r'snap\.refresh',
        ]),
        ('apt-management', [
            r'apt[\s\._]', r'dpkg', r'package.?install', r'apt\.add',
        ]),
        ('systemd', [
            r'systemd', r'systemctl', r'service[\s_]', r'daemon.?reload',
        ]),
        ('juju-interaction', [
            r'juju[\s_]', r'model\.', r'unit\.', r'app\.',
            r'leader', r'peer', r'juju.?run',
        ]),
        ('observability', [
            r'metric', r'alert', r'prometheus', r'grafana', r'loki',
            r'logging', r'tracing', r'tempo', r'dashboard',
        ]),
        ('testing', [
            r'test[_\s]', r'mock', r'pytest', r'unittest', r'assert',
            r'harness', r'scenario', r'integration.?test',
        ]),
        ('ci-build', [
            r'github.?action', r'workflow', r'ci[/\s_]', r'tox',
            r'pyproject', r'makefile', r'Makefile', r'rockcraft',
            r'charmcraft', r'\.github/',
        ]),
        ('packaging', [
            r'requirements', r'setup\.py', r'pyproject\.toml',
            r'dependencies', r'pip[\s_]', r'poetry',
        ]),
        ('container-image', [
            r'oci.?image', r'docker', r'rock', r'container.?image',
            r'image_info', r'fetch.?oci',
        ]),
        ('auth-identity', [
            r'oauth', r'oidc', r'saml', r'ldap', r'identity',
            r'authent', r'authori', r'login', r'token',
            r'credential', r'password',
        ]),
    ]

    # Score each area
    area_scores = {}
    combined = msg + ' ' + changed + ' ' + diff[:2000]  # Only first 2KB of diff

    for area, patterns in checks:
        score = 0
        for pattern in patterns:
            matches = len(re.findall(pattern, combined))
            score += matches
        if score > 0:
            area_scores[area] = score

    if area_scores:
        return max(area_scores, key=area_scores.get)

    return 'other'


def classify_bug_type(fix: dict) -> str:
    """Classify the bug type."""
    subject = fix.get('subject', '').lower()
    body = fix.get('body', '').lower()
    diff = fix.get('diff', '').lower()
    msg = subject + ' ' + body

    type_checks = [
        ('security', [r'secur', r'vuln', r'cve', r'inject', r'xss',
                       r'credential.?leak', r'password.?expos', r'secret.?leak']),
        ('data-loss', [r'data.?loss', r'data.?corrupt', r'overwrite', r'truncat']),
        ('crash', [r'crash', r'segfault', r'panic', r'traceback',
                   r'unhandled.?exception', r'keyerror', r'attributeerror',
                   r'typeerror', r'indexerror', r'valueerror', r'nameerror']),
        ('race-condition', [r'race', r'deadlock', r'concurrent', r'thread.?safe',
                            r'lock.?order']),
        ('logic-error', [r'wrong', r'incorrect', r'broken', r'should',
                          r'instead', r'rather', r'actually', r'properly',
                          r'wasn\'t', r'wasn.t', r'didn\'t', r'didn.t']),
        ('edge-case', [r'edge.?case', r'corner.?case', r'empty', r'none',
                        r'null', r'zero', r'falsy', r'missing',
                        r'optional', r'default']),
        ('type-error', [r'type.?error', r'isinstance', r'type\(', r'cast',
                         r'str\(', r'int\(', r'float\(']),
        ('config', [r'config', r'setting', r'option', r'yaml', r'toml']),
        ('api-contract', [r'api', r'interface', r'contract', r'schema',
                           r'backward', r'compat', r'deprecat']),
        ('test-fix', [r'test', r'mock', r'assert', r'fixture']),
        ('docs-fix', [r'doc', r'readme', r'comment', r'typo', r'spelling']),
        ('performance', [r'slow', r'perf', r'optim', r'cache', r'timeout',
                          r'latency', r'memory']),
    ]

    combined = msg + ' ' + diff[:1000]
    type_scores = {}
    for btype, patterns in type_checks:
        score = 0
        for pattern in patterns:
            score += len(re.findall(pattern, combined))
        if score > 0:
            type_scores[btype] = score

    if type_scores:
        return max(type_scores, key=type_scores.get)

    return 'other'


def classify_severity(fix: dict, bug_type: str) -> str:
    """Classify severity based on bug type, area, and context."""
    subject = fix.get('subject', '').lower()
    body = fix.get('body', '').lower()
    diff = fix.get('diff', '')
    msg = subject + ' ' + body

    # High severity indicators
    if bug_type in ('security', 'data-loss', 'crash', 'race-condition'):
        return 'high'

    high_indicators = [
        r'critical', r'severe', r'urgent', r'production',
        r'data.?loss', r'security', r'credential', r'password',
        r'crash', r'panic', r'deadlock',
    ]
    for pattern in high_indicators:
        if re.search(pattern, msg):
            return 'high'

    # Low severity indicators
    if bug_type in ('docs-fix', 'test-fix'):
        return 'low'

    low_indicators = [
        r'typo', r'spelling', r'cosmetic', r'minor',
        r'lint', r'format', r'style', r'whitespace',
    ]
    for pattern in low_indicators:
        if re.search(pattern, msg):
            return 'low'

    # Diff size heuristic: very small diffs are often low severity
    diff_lines = len([l for l in diff.split('\n')
                      if l.startswith('+') or l.startswith('-')])
    if diff_lines <= 4:
        return 'low'

    return 'medium'


def generate_one_liner(fix: dict, area: str, bug_type: str) -> str:
    """Generate a one-line summary from the commit subject."""
    subject = fix.get('subject', '')
    # Strip conventional commit prefix
    subject = re.sub(r'^fix(\([^)]+\))?:\s*', '', subject, flags=re.IGNORECASE)
    # Strip PR/issue references
    subject = re.sub(r'\s*\(#\d+\)\s*$', '', subject)
    subject = re.sub(r'\s*#\d+\s*$', '', subject)
    return subject.strip() or f"{bug_type} in {area}"


def main():
    all_fixes_path = DATA_DIR / "all_fixes.json"
    with open(all_fixes_path) as f:
        all_fixes = json.load(f)

    print(f"Classifying {len(all_fixes)} fixes...")

    classified = []
    for fix in all_fixes:
        area = classify_bug_area(fix)
        bug_type = classify_bug_type(fix)
        severity = classify_severity(fix, bug_type)
        one_liner = generate_one_liner(fix, area, bug_type)

        classified.append({
            'sha': fix['sha'],
            'repo': fix['repo'],
            'team': fix.get('team', ''),
            'charm_name': fix.get('charm_name', ''),
            'date': fix.get('date', ''),
            'subject': fix.get('subject', ''),
            'bug_area': area,
            'bug_type': bug_type,
            'severity': severity,
            'one_line_summary': one_liner,
            'classification_method': fix.get('classification_method', ''),
            'keyword_score': fix.get('keyword_score', 0),
        })

    # Save classified data
    classified_path = DATA_DIR / "all_classified.json"
    with open(classified_path, 'w') as f:
        json.dump(classified, f, indent=2)

    # Generate statistics
    total = len(classified)
    severity_counts = Counter(c['severity'] for c in classified)
    area_counts = Counter(c['bug_area'] for c in classified)
    type_counts = Counter(c['bug_type'] for c in classified)
    team_counts = Counter(c['team'] for c in classified)
    repo_counts = Counter(c['repo'] for c in classified)

    # Per-team breakdown
    team_severity = {}
    for c in classified:
        team = c['team']
        if team not in team_severity:
            team_severity[team] = Counter()
        team_severity[team][c['severity']] += 1

    # Cross-repo area patterns
    area_by_repo = {}
    for c in classified:
        area = c['bug_area']
        if area not in area_by_repo:
            area_by_repo[area] = set()
        area_by_repo[area].add(c['repo'])

    print(f"\n=== CLASSIFICATION SUMMARY ===")
    print(f"Total classified: {total}")
    print(f"\nSeverity: {dict(severity_counts.most_common())}")
    print(f"\nTop 15 Bug Areas:")
    for area, count in area_counts.most_common(15):
        repos_count = len(area_by_repo.get(area, set()))
        print(f"  {area}: {count} fixes across {repos_count} repos")
    print(f"\nBug Types:")
    for btype, count in type_counts.most_common():
        print(f"  {btype}: {count}")
    print(f"\nBy Team:")
    for team, count in team_counts.most_common():
        sev = team_severity.get(team, {})
        print(f"  {team}: {count} (H:{sev.get('high',0)} M:{sev.get('medium',0)} L:{sev.get('low',0)})")

    # Save stats summary
    stats = {
        'total': total,
        'severity': dict(severity_counts),
        'areas': dict(area_counts.most_common()),
        'types': dict(type_counts.most_common()),
        'teams': {team: {'total': count, 'severity': dict(team_severity.get(team, {}))}
                  for team, count in team_counts.most_common()},
        'top_repos': [{'repo': repo, 'count': count}
                      for repo, count in repo_counts.most_common(30)],
        'cross_repo_areas': {area: {'count': area_counts[area], 'repos': len(repos)}
                             for area, repos in sorted(area_by_repo.items(),
                                                        key=lambda x: len(x[1]),
                                                        reverse=True)},
    }
    stats_path = DATA_DIR / "classification_stats.json"
    with open(stats_path, 'w') as f:
        json.dump(stats, f, indent=2)

    print(f"\nSaved to {classified_path} and {stats_path}")


if __name__ == '__main__':
    main()
