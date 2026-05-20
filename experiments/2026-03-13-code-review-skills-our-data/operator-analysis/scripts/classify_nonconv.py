#!/usr/bin/env python3
"""Classify non-conventional commits as likely bug fixes vs not."""
import re

BUG_KEYWORDS = [
    r'\bfix\b', r'\bfixed\b', r'\bfixes\b', r'\bfixing\b',
    r'\bbug\b', r'\bbugfix\b',
    r'\bcorrect\b', r'\bcorrected\b', r'\bcorrection\b',
    r'\bpatch\b', r'\bpatched\b',
    r'\bresolve[ds]?\b', r'\bworkaround\b',
    r'\bregression\b', r'\bbroken\b', r'\bbreak\b',
    r'\berror\b', r'\bcrash\b', r'\bfail\b',
    r'\bhandle\b.*\b(error|exception|edge|case)\b',
    r'\bprevent\b', r'\bavoid\b',
    r'\bensure\b', r'\bguard\b',
    r'\bwrong\b', r'\bincorrect\b', r'\binvalid\b',
    r'\bmissing\b', r'\btypo\b',
    r'\bnone\s*(check|guard|handling)\b',
    r'\bkey\s*error\b', r'\battribute\s*error\b', r'\btype\s*error\b',
    r'\boff.by.one\b', r'\brace\b', r'\bdeadlock\b',
    r'\bsecurity\b', r'\bvulnerab\b', r'\bexploit\b',
    r'\bsanitiz\b', r'\bescap\b',
    r'\bdon.t\b.*\b(crash|fail|error|break)\b',
    r'\bshould\b.*\bnot\b', r'\bshould\b.*\binstead\b',
    r'\bactually\b', r'\bproperly\b',
]

# Keywords that suggest NOT a bug fix
NOT_BUG_KEYWORDS = [
    r'^Merge\b', r'^Bump\b', r'^Update\b.*\bdep', r'^Add\s+(new\s+)?feature',
    r'^Remove\s+deprecated', r'^Reorganis', r'^Move\b',
    r'\brefactor\b', r'\bcleanup\b', r'\bclean up\b',
    r'\bdocument', r'\bREADME\b', r'\bchangelog\b',
    r'\bbump\s+version\b', r'\brelease\b',
]

likely_fixes = []
maybe_fixes = []
not_fixes = []

with open('/home/ubuntu/operstor-analysis/nonconventional_commits.txt') as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        parts = line.split('|||')
        if len(parts) < 3:
            continue
        sha, subject, date = parts[0], parts[1], parts[2]

        # Skip merge commits with no useful info
        if subject.startswith('Merge pull request') or subject.startswith('Merge branch') or subject.startswith('Merge remote'):
            not_fixes.append((sha, subject, date))
            continue

        subject_lower = subject.lower()

        # Check for NOT bug fix signals
        is_not_bug = False
        for pat in NOT_BUG_KEYWORDS:
            if re.search(pat, subject, re.IGNORECASE):
                is_not_bug = True
                break

        # Check for bug fix signals
        bug_score = 0
        for pat in BUG_KEYWORDS:
            if re.search(pat, subject_lower):
                bug_score += 1

        if bug_score >= 2:
            likely_fixes.append((sha, subject, date, bug_score))
        elif bug_score >= 1 and not is_not_bug:
            maybe_fixes.append((sha, subject, date, bug_score))
        else:
            not_fixes.append((sha, subject, date))

print(f"Likely fixes: {len(likely_fixes)}")
print(f"Maybe fixes: {len(maybe_fixes)}")
print(f"Not fixes: {len(not_fixes)}")

print("\n=== LIKELY FIXES ===")
for sha, subj, date, score in likely_fixes:
    print(f"{sha[:8]} [{date}] (score={score}) {subj}")

print("\n=== MAYBE FIXES ===")
for sha, subj, date, score in maybe_fixes:
    print(f"{sha[:8]} [{date}] (score={score}) {subj}")

# Write out the combined list for further processing
with open('/home/ubuntu/operstor-analysis/candidate_nonconv_fixes.txt', 'w') as f:
    for sha, subj, date, score in likely_fixes + maybe_fixes:
        f.write(f"{sha}|||{subj}|||{date}|||{score}\n")
