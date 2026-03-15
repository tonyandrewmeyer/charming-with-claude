#!/usr/bin/env python3
"""
Audit current code for known bug patterns found in historical fixes.
Checks the current HEAD of canonical/operator for potential issues.
"""
import os
import re
import ast
import json
import sys

REPO_DIR = '/home/ubuntu/operstor-analysis/operator'

class PatternChecker:
    def __init__(self):
        self.findings = []

    def add_finding(self, file, line, pattern, description, severity, evidence=""):
        self.findings.append({
            'file': file,
            'line': line,
            'pattern': pattern,
            'description': description,
            'severity': severity,
            'evidence': evidence,
        })

    def check_file(self, filepath, content, lines):
        relpath = os.path.relpath(filepath, REPO_DIR)
        self.check_mutable_defaults(relpath, content, lines)
        self.check_shared_dict_mutation(relpath, content, lines)
        self.check_missing_none_checks(relpath, content, lines)
        self.check_file_resource_cleanup(relpath, content, lines)
        self.check_subprocess_injection(relpath, content, lines)
        self.check_bare_except(relpath, content, lines)
        self.check_permission_issues(relpath, content, lines)
        self.check_datetime_parsing(relpath, content, lines)
        self.check_dict_key_access(relpath, content, lines)
        self.check_secret_patterns(relpath, content, lines)
        self.check_relation_data_patterns(relpath, content, lines)
        self.check_copy_patterns(relpath, content, lines)

    def check_mutable_defaults(self, filepath, content, lines):
        """Pattern: mutable default arguments (common source of bugs in ops)."""
        for i, line in enumerate(lines, 1):
            # Look for def foo(x=[]) or def foo(x={})
            if re.search(r'def\s+\w+\([^)]*=\s*(\[\]|\{\}|\bdict\(\)|\blist\(\))', line):
                # Skip test files for lower noise
                self.add_finding(filepath, i, 'mutable-default-arg',
                    'Mutable default argument - can cause shared state bugs',
                    'medium', line.strip())

    def check_shared_dict_mutation(self, filepath, content, lines):
        """Pattern: returning or storing dicts without copying."""
        for i, line in enumerate(lines, 1):
            # Direct dict assignment without copy
            if re.search(r'self\._\w+\s*=\s*(data|config|meta|relation_data)\b', line):
                # Check if .copy() is used nearby
                if '.copy()' not in line and 'dict(' not in line and 'copy.deepcopy' not in line:
                    self.add_finding(filepath, i, 'shared-dict-no-copy',
                        'Dict stored without copying - mutations may leak',
                        'medium', line.strip())

    def check_missing_none_checks(self, filepath, content, lines):
        """Pattern: accessing attributes/methods on potentially None values."""
        for i, line in enumerate(lines, 1):
            # Accessing .something on optional returns without None check
            if re.search(r'\.get\([^)]+\)\.\w+', line):
                if 'or ' not in line and 'if ' not in lines[max(0,i-2)]:
                    self.add_finding(filepath, i, 'potential-none-access',
                        'Chained access on .get() result which could be None',
                        'low', line.strip())

    def check_file_resource_cleanup(self, filepath, content, lines):
        """Pattern: file handles not closed properly."""
        for i, line in enumerate(lines, 1):
            if re.search(r'open\(', line) and 'with ' not in line:
                # Check if it's an assignment that's later closed
                if re.search(r'\w+\s*=\s*open\(', line):
                    self.add_finding(filepath, i, 'file-not-in-context-manager',
                        'File opened without context manager - may leak on exception',
                        'low', line.strip())

    def check_subprocess_injection(self, filepath, content, lines):
        """Pattern: shell=True or string formatting in subprocess calls."""
        for i, line in enumerate(lines, 1):
            if 'shell=True' in line and ('subprocess' in line or 'Popen' in line):
                self.add_finding(filepath, i, 'shell-injection-risk',
                    'subprocess with shell=True - potential command injection',
                    'high', line.strip())
            # String formatting in subprocess args
            if re.search(r'subprocess\.\w+\(\s*f["\']', line) or re.search(r'subprocess\.\w+\([^)]*%\s', line):
                self.add_finding(filepath, i, 'subprocess-format-string',
                    'Formatted string in subprocess call - potential injection',
                    'high', line.strip())

    def check_bare_except(self, filepath, content, lines):
        """Pattern: bare except clauses that could hide bugs."""
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped == 'except:' or re.match(r'^except\s*:\s*$', stripped):
                self.add_finding(filepath, i, 'bare-except',
                    'Bare except clause - may hide unexpected exceptions',
                    'medium', line.strip())

    def check_permission_issues(self, filepath, content, lines):
        """Pattern: file creation without explicit permissions."""
        for i, line in enumerate(lines, 1):
            # Check for file writes without explicit mode
            if re.search(r'open\([^)]+,\s*["\']w', line):
                if 'mode=' not in line and 'os.chmod' not in content[max(0,i-3):min(len(lines),i+3)] if isinstance(content, list) else True:
                    pass  # This is too noisy for a static check

    def check_datetime_parsing(self, filepath, content, lines):
        """Pattern: datetime parsing that doesn't handle edge cases."""
        for i, line in enumerate(lines, 1):
            # Using strptime or fromisoformat without error handling
            if 'strptime' in line or 'fromisoformat' in line:
                # Check if there's a try/except around it
                context = '\n'.join(lines[max(0,i-5):min(len(lines),i+2)])
                if 'try' not in context and 'except' not in context:
                    self.add_finding(filepath, i, 'unprotected-datetime-parsing',
                        'Datetime parsing without error handling - may fail on edge cases',
                        'low', line.strip())

    def check_dict_key_access(self, filepath, content, lines):
        """Pattern: dict[key] access that could raise KeyError."""
        # This is too noisy to check generically, so focus on specific patterns
        pass

    def check_secret_patterns(self, filepath, content, lines):
        """Pattern: secret handling issues."""
        for i, line in enumerate(lines, 1):
            # Logging secret content
            if re.search(r'log.*secret.*content|log.*get_content', line, re.IGNORECASE):
                self.add_finding(filepath, i, 'secret-content-logged',
                    'Secret content may be logged',
                    'high', line.strip())

    def check_relation_data_patterns(self, filepath, content, lines):
        """Pattern: relation data access issues."""
        for i, line in enumerate(lines, 1):
            # Writing non-string values to relation data
            if re.search(r'relation.*data.*\[.*\]\s*=\s*(?!.*str\(|.*["\'])', line):
                pass  # Too noisy

    def check_copy_patterns(self, filepath, content, lines):
        """Pattern: places where data should be copied but isn't."""
        for i, line in enumerate(lines, 1):
            if re.search(r'return\s+self\._(?:meta|config|data|state)\b', line):
                if '.copy()' not in line and 'copy.deepcopy' not in line:
                    self.add_finding(filepath, i, 'return-internal-state',
                        'Returning internal state without copying - mutations may leak',
                        'medium', line.strip())


def main():
    checker = PatternChecker()

    # Walk all Python files in ops/ and testing/
    for root, dirs, files in os.walk(os.path.join(REPO_DIR, 'ops')):
        dirs[:] = [d for d in dirs if d != '__pycache__']
        for fname in files:
            if not fname.endswith('.py'):
                continue
            fpath = os.path.join(root, fname)
            try:
                with open(fpath) as f:
                    content = f.read()
                lines = content.split('\n')
                checker.check_file(fpath, content, lines)
            except Exception as e:
                print(f"Error reading {fpath}: {e}")

    for root, dirs, files in os.walk(os.path.join(REPO_DIR, 'testing', 'src')):
        dirs[:] = [d for d in dirs if d != '__pycache__']
        for fname in files:
            if not fname.endswith('.py'):
                continue
            fpath = os.path.join(root, fname)
            try:
                with open(fpath) as f:
                    content = f.read()
                lines = content.split('\n')
                checker.check_file(fpath, content, lines)
            except Exception as e:
                print(f"Error reading {fpath}: {e}")

    # Sort by severity
    sev_order = {'high': 0, 'medium': 1, 'low': 2}
    checker.findings.sort(key=lambda x: sev_order.get(x['severity'], 3))

    # Save findings
    with open('/home/ubuntu/operstor-analysis/code_audit_findings.json', 'w') as f:
        json.dump(checker.findings, f, indent=2)

    # Print summary
    from collections import Counter
    sev_counts = Counter(f['severity'] for f in checker.findings)
    pat_counts = Counter(f['pattern'] for f in checker.findings)

    print(f"Total findings: {len(checker.findings)}")
    print(f"Severity: {dict(sev_counts)}")
    print(f"Patterns: {dict(pat_counts.most_common())}")
    print()

    for f in checker.findings:
        print(f"[{f['severity'].upper()}] {f['file']}:{f['line']} - {f['pattern']}: {f['description']}")
        print(f"  {f['evidence']}")
        print()


if __name__ == '__main__':
    main()
