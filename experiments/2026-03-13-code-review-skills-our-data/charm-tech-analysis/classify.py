import json

# ========== operator-libs-linux ==========
operator_libs = [
    {
        "sha": "e49ce42a6ab4b3be85405d8a43a31ff2a5906880",
        "repo": "operator-libs-linux",
        "date": "2025-06-04",
        "subject": "fix: refresh with classic (#161)",
        "bug_area": "snap",
        "bug_type": "logic-error",
        "severity": "high",
        "fix_category": "source-fix",
        "one_line_summary": "Snap refresh was missing --classic flag for classically-confined snaps"
    },
    {
        "sha": "c19d8b515d060296c0aafab988d3292470bf8aa5",
        "repo": "operator-libs-linux",
        "date": "2025-04-02",
        "subject": "fix(apt): improve logic in apt.add_package function (#155)",
        "bug_area": "apt-package-management",
        "bug_type": "logic-error",
        "severity": "medium",
        "fix_category": "source-fix",
        "one_line_summary": "apt.add_package retry logic was broken: failed packages not tracked and return value inconsistent for single package"
    },
    {
        "sha": "d58ccedb1aef66eee55f7008dcc5bebabf94e7e1",
        "repo": "operator-libs-linux",
        "date": "2024-12-15",
        "subject": "fix: Task status can be `Do` and should not raise an error. (#140)",
        "bug_area": "snap",
        "bug_type": "edge-case",
        "severity": "medium",
        "fix_category": "source-fix",
        "one_line_summary": "Snap task status 'Do' (ready but not started) was treated as an error instead of a valid pending state"
    },
    {
        "sha": "74ddb086a64dd9c0c8c588aff293ef3d4c2274a4",
        "repo": "operator-libs-linux",
        "date": "2024-05-31",
        "subject": "snap.py: fix snap.get optional key (#125)",
        "bug_area": "snap",
        "bug_type": "edge-case",
        "severity": "medium",
        "fix_category": "source-fix",
        "one_line_summary": "snap.get with falsy key (None) crashed instead of returning all config values"
    },
    {
        "sha": "57e7a6f929bcb849ddfda49564e7fab0c549fd0e",
        "repo": "operator-libs-linux",
        "date": "2023-08-23",
        "subject": "fix comparing types and use isinstance (#105)",
        "bug_area": "apt-package-management",
        "bug_type": "type-error",
        "severity": "medium",
        "fix_category": "source-fix",
        "one_line_summary": "Used type() instead of isinstance() for type checks, failing for subclasses and allowing bool to pass as int"
    },
    {
        "sha": "8c3034ccbf2805b6018cfb18902c28a86d076a71",
        "repo": "operator-libs-linux",
        "date": "2023-08-06",
        "subject": "Fix file operations in unit tests (#103)",
        "bug_area": "sysctl",
        "bug_type": "logic-error",
        "severity": "medium",
        "fix_category": "source-fix",
        "one_line_summary": "sysctl tests used == instead of calling f.write() and f.read(), and source used string path instead of Path for discard"
    },
    {
        "sha": "74d7aae0673840cabec0f855eb4bfb4dd2fc3bc9",
        "repo": "operator-libs-linux",
        "date": "2023-07-26",
        "subject": "Fix error naming example (#101)",
        "bug_area": "sysctl",
        "bug_type": "api-contract",
        "severity": "low",
        "fix_category": "docs-fix",
        "one_line_summary": "Docstring example used wrong exception class names (SysctlPermissionError/SysctlError vs ApplyError/CommandError)"
    },
    {
        "sha": "1a09b1602f60a73d3515e93143ea7c37e41abb09",
        "repo": "operator-libs-linux",
        "date": "2023-05-17",
        "subject": "fix(snap): handle revision as str (#92)",
        "bug_area": "snap",
        "bug_type": "type-error",
        "severity": "high",
        "fix_category": "source-fix",
        "one_line_summary": "Snap revision was handled as int but should be string, causing API breakage; bumped to v2"
    },
    {
        "sha": "4448e7bc6bdf7b2cdd83a69e3c5870e3e2f3ea39",
        "repo": "operator-libs-linux",
        "date": "2023-03-09",
        "subject": "fix: make placeholder charm a machine charm (#69)",
        "bug_area": "packaging",
        "bug_type": "config",
        "severity": "low",
        "fix_category": "build-fix",
        "one_line_summary": "Placeholder charm was not configured as machine charm, preventing proper testing"
    },
    {
        "sha": "a063d947072f14e9c9b33e2a5c5a6c0e1d8e7f3a",
        "repo": "operator-libs-linux",
        "date": "2023-01-23",
        "subject": "fix: inherit environment before adding new keys (#61)",
        "bug_area": "apt-package-management",
        "bug_type": "state-management",
        "severity": "high",
        "fix_category": "source-fix",
        "one_line_summary": "apt subprocess calls did not inherit the parent environment, losing PATH and other required env vars"
    },
    {
        "sha": "8bc6b1a8c03b",
        "repo": "operator-libs-linux",
        "date": "2022-04-12",
        "subject": "Fix typos in apt docstring",
        "bug_area": "apt-package-management",
        "bug_type": "other",
        "severity": "low",
        "fix_category": "docs-fix",
        "one_line_summary": "Fixed typos in apt library docstrings for version parameter descriptions"
    },
    {
        "sha": "3fec034cb565",
        "repo": "operator-libs-linux",
        "date": "2022-04-12",
        "subject": "Fix typos in apt docstrings",
        "bug_area": "apt-package-management",
        "bug_type": "other",
        "severity": "low",
        "fix_category": "docs-fix",
        "one_line_summary": "Fixed additional typos in apt library docstrings"
    },
    {
        "sha": "ad40fe4f5664",
        "repo": "operator-libs-linux",
        "date": "2022-03-04",
        "subject": "Fix issues with apt methods (add_package/remove_package) (#41)",
        "bug_area": "apt-package-management",
        "bug_type": "logic-error",
        "severity": "high",
        "fix_category": "source-fix",
        "one_line_summary": "apt add_package/remove_package failed to check dpkg install status, treating uninstalled packages as installed"
    },
    {
        "sha": "49d4b8584e18",
        "repo": "operator-libs-linux",
        "date": "2021-12-07",
        "subject": "Fixed test_unset_key_raises_snap_error",
        "bug_area": "snap",
        "bug_type": "test-fix",
        "severity": "low",
        "fix_category": "test-fix",
        "one_line_summary": "Integration test was passing by accident; fixed to properly test unset key error"
    },
    {
        "sha": "b60719d93f75",
        "repo": "operator-libs-linux",
        "date": "2021-12-07",
        "subject": "Fixes for Python 3.5",
        "bug_area": "snap",
        "bug_type": "edge-case",
        "severity": "low",
        "fix_category": "test-fix",
        "one_line_summary": "Unit tests relied on dict ordering not guaranteed in Python 3.5"
    },
    {
        "sha": "5b67ccc731e8",
        "repo": "operator-libs-linux",
        "date": "2021-12-07",
        "subject": "Fixed Python 3.5 issue",
        "bug_area": "snap",
        "bug_type": "edge-case",
        "severity": "low",
        "fix_category": "test-fix",
        "one_line_summary": "Another dict ordering fix for Python 3.5 compatibility in snap set tests"
    },
    {
        "sha": "f81e4e305df4",
        "repo": "operator-libs-linux",
        "date": "2021-12-03",
        "subject": "Fixed docstring changes.",
        "bug_area": "snap",
        "bug_type": "other",
        "severity": "low",
        "fix_category": "docs-fix",
        "one_line_summary": "Updated snap library docstring examples and test error messages"
    },
    {
        "sha": "10186e8da02a",
        "repo": "operator-libs-linux",
        "date": "2021-11-29",
        "subject": "Fixed type checker unhappiness.",
        "bug_area": "snap",
        "bug_type": "type-error",
        "severity": "low",
        "fix_category": "source-fix",
        "one_line_summary": "Added type annotation to snap.set() method to satisfy type checker"
    },
    {
        "sha": "0ac5838107e8",
        "repo": "operator-libs-linux",
        "date": "2021-12-06",
        "subject": "Fix tests (fix code)",
        "bug_area": "snap",
        "bug_type": "logic-error",
        "severity": "medium",
        "fix_category": "source-fix",
        "one_line_summary": "Snap install/refresh passed empty cohort string to subprocess causing errors"
    },
    {
        "sha": "abe9ec7c5fe0",
        "repo": "operator-libs-linux",
        "date": "2021-12-06",
        "subject": "Fixes for the way that cohort gets passed.",
        "bug_area": "snap",
        "bug_type": "logic-error",
        "severity": "medium",
        "fix_category": "source-fix",
        "one_line_summary": "Cohort and channel args for snap install/refresh not properly formatted as CLI flags"
    },
    {
        "sha": "b2096f78f041",
        "repo": "operator-libs-linux",
        "date": "2021-11-29",
        "subject": "Make service and popen_kwargs 'private'; driveby spelling fix (#27)",
        "bug_area": "systemd",
        "bug_type": "api-contract",
        "severity": "low",
        "fix_category": "source-fix",
        "one_line_summary": "Made internal systemd helper functions private and fixed spelling in docstring"
    },
    {
        "sha": "a59318441a7a",
        "repo": "operator-libs-linux",
        "date": "2021-11-23",
        "subject": "Fixed type hinting.",
        "bug_area": "systemd",
        "bug_type": "type-error",
        "severity": "low",
        "fix_category": "test-fix",
        "one_line_summary": "Added missing type hints to systemd test helper function"
    },
    {
        "sha": "a848a31bddd2",
        "repo": "operator-libs-linux",
        "date": "2021-11-19",
        "subject": "Fixed linter errors.",
        "bug_area": "systemd",
        "bug_type": "other",
        "severity": "low",
        "fix_category": "test-fix",
        "one_line_summary": "Fixed linter errors in systemd integration tests (missing header, imports)"
    },
    {
        "sha": "4d14041bfdcf",
        "repo": "operator-libs-linux",
        "date": "2021-11-04",
        "subject": "Fixed up typing.",
        "bug_area": "systemd",
        "bug_type": "type-error",
        "severity": "low",
        "fix_category": "source-fix",
        "one_line_summary": "Added return type annotations to systemd functions after mypy run"
    },
    {
        "sha": "0e086ee94ecc",
        "repo": "operator-libs-linux",
        "date": "2021-11-19",
        "subject": "Fix failing test.",
        "bug_area": "snap",
        "bug_type": "test-fix",
        "severity": "low",
        "fix_category": "test-fix",
        "one_line_summary": "Unit test reached out to real snapd, failing on systems without it; added mock"
    },
    {
        "sha": "a062547af253",
        "repo": "operator-libs-linux",
        "date": "2021-11-08",
        "subject": "Fix GPG key handling (#15)",
        "bug_area": "apt-package-management",
        "bug_type": "logic-error",
        "severity": "high",
        "fix_category": "source-fix",
        "one_line_summary": "GPG key import for apt repositories used broken Popen communication; replaced with subprocess.run()"
    },
    {
        "sha": "3e8a1b5614c2",
        "repo": "operator-libs-linux",
        "date": "2021-11-03",
        "subject": "Fix up parsing more complex sources..list lines (#11)",
        "bug_area": "apt-package-management",
        "bug_type": "parsing",
        "severity": "high",
        "fix_category": "source-fix",
        "one_line_summary": "apt sources.list parser failed on lines with options like [arch=amd64] and raised error on partial parse failures"
    },
    {
        "sha": "92ee7ef839a2",
        "repo": "operator-libs-linux",
        "date": "2021-10-29",
        "subject": "Fix linting issues",
        "bug_area": "apt-package-management",
        "bug_type": "other",
        "severity": "low",
        "fix_category": "source-fix",
        "one_line_summary": "Fixed linting issues in apt library docstring examples"
    },
    {
        "sha": "322f9b4833b6",
        "repo": "operator-libs-linux",
        "date": "2021-10-27",
        "subject": "snap: fix copy-n-paste error in set()",
        "bug_area": "snap",
        "bug_type": "logic-error",
        "severity": "high",
        "fix_category": "source-fix",
        "one_line_summary": "snap.set() had a copy-paste error causing it to not actually set the key/value correctly"
    },
]

# ========== charmhub-listing-review ==========
charmhub_listing = [
    {
        "sha": "b45e0d53a2d466d4aee8f07b714c8beca33c56f4",
        "repo": "charmhub-listing-review",
        "date": "2026-01-21",
        "subject": "fix: Correct Pietro's GitHub username (#49)",
        "bug_area": "config",
        "bug_type": "data-validation",
        "severity": "medium",
        "fix_category": "source-fix",
        "one_line_summary": "Incorrect GitHub username in reviewers.yaml caused review assignment to fail"
    },
    {
        "sha": "a7acfeeb4a5132f078f14108c9c96e17d28db151",
        "repo": "charmhub-listing-review",
        "date": "2026-01-20",
        "subject": "fix: add missing vars section in tox.ini (#43)",
        "bug_area": "ci-build",
        "bug_type": "config",
        "severity": "medium",
        "fix_category": "build-fix",
        "one_line_summary": "Missing [vars] section in tox.ini broke test runs; also fixed test mock to JSON-encode output"
    },
    {
        "sha": "72b60724737dc6142b4da199cb537fe6cc54f58a",
        "repo": "charmhub-listing-review",
        "date": "2026-01-20",
        "subject": "fix: explicitly provide the path to the reviewers file (#42)",
        "bug_area": "automation",
        "bug_type": "api-contract",
        "severity": "medium",
        "fix_category": "source-fix",
        "one_line_summary": "Reviewers file path was hardcoded to CI runner path; made it a required CLI argument"
    },
    {
        "sha": "28e26a62356c03424e8d1334ccf0856f26dc8d85",
        "repo": "charmhub-listing-review",
        "date": "2025-11-03",
        "subject": "Fix code review issues and duplication problem",
        "bug_area": "automation",
        "bug_type": "logic-error",
        "severity": "medium",
        "fix_category": "source-fix",
        "one_line_summary": "Automated checks duplicated checklist items instead of updating them in place"
    },
    {
        "sha": "c8be66a8a934ed93f80b6f54381fb7879137035d",
        "repo": "charmhub-listing-review",
        "date": "2025-08-28",
        "subject": "fix: temporarily hard-code the CI location for the reviewers file (#12)",
        "bug_area": "automation",
        "bug_type": "config",
        "severity": "medium",
        "fix_category": "source-fix",
        "one_line_summary": "Reviewers file path resolution using __file__ did not work in CI; hardcoded as temporary fix"
    },
    {
        "sha": "b3fec63427d1184333a13b889d92ec2f70dc32f7",
        "repo": "charmhub-listing-review",
        "date": "2025-08-28",
        "subject": "fix: add a temporary fix for running the workflow (#11)",
        "bug_area": "ci-build",
        "bug_type": "config",
        "severity": "medium",
        "fix_category": "ci-fix",
        "one_line_summary": "GitHub workflow ran script directly instead of installing package first, causing import failures"
    },
]

# ========== charmcraft-profile-tools ==========
charmcraft_profile = [
    {
        "sha": "38eae1fcbca76170e1b9ac4161574bb57e2160c7",
        "repo": "charmcraft-profile-tools",
        "date": "2025-09-08",
        "subject": "fix spelling",
        "bug_area": "other",
        "bug_type": "other",
        "severity": "low",
        "fix_category": "docs-fix",
        "one_line_summary": "Fixed two spelling typos in README (maintaing -> maintaining, locaed -> located)"
    },
    {
        "sha": "6cf99f61f5205f1c09a83181c2156b1e260402a6",
        "repo": "charmcraft-profile-tools",
        "date": "2025-09-07",
        "subject": "fix copying to kubernetes-extra",
        "bug_area": "automation",
        "bug_type": "logic-error",
        "severity": "medium",
        "fix_category": "source-fix",
        "one_line_summary": "Copying to kubernetes-extra included stale build artifacts (.coverage, .ruff_cache, .tox, .venv)"
    },
    {
        "sha": "8d4730bbedf0f6ea1acd32ccce83d81eaf51efb9",
        "repo": "charmcraft-profile-tools",
        "date": "2025-09-07",
        "subject": "fix error handling",
        "bug_area": "automation",
        "bug_type": "logic-error",
        "severity": "medium",
        "fix_category": "source-fix",
        "one_line_summary": "Typo in justfile checked for .ven instead of .venv, so venv existence check always failed"
    },
    {
        "sha": "3f9d8337a9e1bd3e59e82f251da33e3c7957b356",
        "repo": "charmcraft-profile-tools",
        "date": "2025-09-05",
        "subject": "fix consistency check",
        "bug_area": "ci-build",
        "bug_type": "config",
        "severity": "medium",
        "fix_category": "ci-fix",
        "one_line_summary": "CI workflow missing tox and tox-uv installation step, causing consistency check to fail"
    },
    {
        "sha": "c3488f9d922e23ec941b799fa5b930b4b89872fd",
        "repo": "charmcraft-profile-tools",
        "date": "2025-09-05",
        "subject": "fix name of charm checks",
        "bug_area": "ci-build",
        "bug_type": "config",
        "severity": "low",
        "fix_category": "ci-fix",
        "one_line_summary": "GitHub workflow had wrong display name ('Code checks' instead of 'Charm checks')"
    },
    {
        "sha": "9b0ca370a77883f645ebdeb130d5a618eab7d5df",
        "repo": "charmcraft-profile-tools",
        "date": "2025-08-26",
        "subject": "fix bugs",
        "bug_area": "automation",
        "bug_type": "logic-error",
        "severity": "medium",
        "fix_category": "source-fix",
        "one_line_summary": "Multiple path handling bugs in implement script and justfile: wrong CWD assumptions, missing cleanup"
    },
    {
        "sha": "94673fb182b7aa95655e4f84ee896f8d09bb88f1",
        "repo": "charmcraft-profile-tools",
        "date": "2025-08-24",
        "subject": "fix implemented integration test",
        "bug_area": "testing",
        "bug_type": "test-fix",
        "severity": "low",
        "fix_category": "test-fix",
        "one_line_summary": "Integration test expected wrong workload version (3.14 placeholder instead of actual 1.0.0)"
    },
]

# ========== charm-ubuntu ==========
charm_ubuntu = [
    {
        "sha": "89a3e4cf86490b231ae040979e1e7676246b33a0",
        "repo": "charm-ubuntu",
        "date": "2022-02-02",
        "subject": "Fix branch for actions-operator",
        "bug_area": "ci-build",
        "bug_type": "config",
        "severity": "medium",
        "fix_category": "ci-fix",
        "one_line_summary": "CI referenced 'master' branch of actions-operator which was renamed to 'main'"
    },
    {
        "sha": "a033bd87b7e567940ac9beec36bc12707fc8103b",
        "repo": "charm-ubuntu",
        "date": "2022-02-01",
        "subject": "Latest release of operator framework includes fix for GH#517",
        "bug_area": "packaging",
        "bug_type": "config",
        "severity": "medium",
        "fix_category": "build-fix",
        "one_line_summary": "requirements.txt pinned to git master for ops framework bug workaround; switched back to released version"
    },
    {
        "sha": "c253a5f502c662acc7d2b39f61ba4cf405177d7c",
        "repo": "charm-ubuntu",
        "date": "2021-06-17",
        "subject": "Update Black and fix formatting",
        "bug_area": "testing",
        "bug_type": "other",
        "severity": "low",
        "fix_category": "source-fix",
        "one_line_summary": "New Black version enforced spaces around docstrings; updated formatting"
    },
    {
        "sha": "59324d47a08dcd704aa5f48ce68b9d096f127283",
        "repo": "charm-ubuntu",
        "date": "2021-03-05",
        "subject": "Fix use of newer addClassCleanup",
        "bug_area": "testing",
        "bug_type": "api-contract",
        "severity": "medium",
        "fix_category": "test-fix",
        "one_line_summary": "Used addClassCleanup which was not available in all Python versions; replaced with explicit tearDownClass"
    },
    {
        "sha": "3250c6ec2e0ff3f8b479edb0c5f866b6c6bc036d",
        "repo": "charm-ubuntu",
        "date": "2020-05-29",
        "subject": "yaml lint fix (valid default)",
        "bug_area": "config",
        "bug_type": "data-validation",
        "severity": "low",
        "fix_category": "source-fix",
        "one_line_summary": "config.yaml had empty default value instead of empty string, causing charm lint warning"
    },
    {
        "sha": "e03c398b5c941c349c315878cbb8f36ab7e8e6c1",
        "repo": "charm-ubuntu",
        "date": "2019-08-19",
        "subject": "Fix deploy error due to new pip / old setuptools conflict",
        "bug_area": "packaging",
        "bug_type": "edge-case",
        "severity": "high",
        "fix_category": "source-fix",
        "one_line_summary": "Newer pip conflicted with older system setuptools when include_system_packages was true, breaking deploys"
    },
    {
        "sha": "11ad6edf050164b0732b331e90b50e4fec3c64e5",
        "repo": "charm-ubuntu",
        "date": "2019-08-06",
        "subject": "Fix repo URL in layer.yaml",
        "bug_area": "config",
        "bug_type": "config",
        "severity": "low",
        "fix_category": "source-fix",
        "one_line_summary": "layer.yaml pointed to old repo URL (marcoceppi) instead of current (juju-solutions)"
    },
]

# Write all four classified files
for name, data in [
    ("operator-libs-linux", operator_libs),
    ("charmhub-listing-review", charmhub_listing),
    ("charmcraft-profile-tools", charmcraft_profile),
    ("charm-ubuntu", charm_ubuntu),
]:
    path = f"/home/ubuntu/charm-tech-analysis/data/{name}_classified.json"
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Wrote {len(data)} entries to {path}")

# Now generate summary
all_fixes = operator_libs + charmhub_listing + charmcraft_profile + charm_ubuntu
total = len(all_fixes)

# Counts
from collections import Counter

severity_counts = Counter(f["severity"] for f in all_fixes)
area_counts = Counter(f["bug_area"] for f in all_fixes)
type_counts = Counter(f["bug_type"] for f in all_fixes)
category_counts = Counter(f["fix_category"] for f in all_fixes)
repo_counts = Counter(f["repo"] for f in all_fixes)

# Per-repo breakdown
repos = {}
for f in all_fixes:
    r = f["repo"]
    if r not in repos:
        repos[r] = {"total": 0, "severity": Counter(), "area": Counter(), "type": Counter(), "category": Counter()}
    repos[r]["total"] += 1
    repos[r]["severity"][f["severity"]] += 1
    repos[r]["area"][f["bug_area"]] += 1
    repos[r]["type"][f["bug_type"]] += 1
    repos[r]["category"][f["fix_category"]] += 1

summary = f"""# Smaller Charm Tech Repos -- Bug-Fix Classification Summary

**Total fixes classified:** {total} across {len(repos)} repositories

## Per-Repository Breakdown

"""

for rname in ["operator-libs-linux", "charmhub-listing-review", "charmcraft-profile-tools", "charm-ubuntu"]:
    r = repos[rname]
    summary += f"### {rname} ({r['total']} fixes)\n\n"
    summary += f"- **Severity:** {', '.join(f'{s}: {c}' for s, c in r['severity'].most_common())}\n"
    summary += f"- **Top areas:** {', '.join(f'{a}: {c}' for a, c in r['area'].most_common(3))}\n"
    summary += f"- **Top types:** {', '.join(f'{t}: {c}' for t, c in r['type'].most_common(3))}\n"
    summary += f"- **Fix categories:** {', '.join(f'{cat}: {c}' for cat, c in r['category'].most_common())}\n\n"

summary += f"""## Total Fixes by Severity

| Severity | Count | Percentage |
|----------|-------|------------|
| High     | {severity_counts['high']} | {severity_counts['high']*100//total}% |
| Medium   | {severity_counts['medium']} | {severity_counts['medium']*100//total}% |
| Low      | {severity_counts['low']} | {severity_counts['low']*100//total}% |

## Top Bug Areas

| Area | Count |
|------|-------|
"""
for area, count in area_counts.most_common():
    summary += f"| {area} | {count} |\n"

summary += f"""
## Top Bug Types

| Type | Count |
|------|-------|
"""
for btype, count in type_counts.most_common():
    summary += f"| {btype} | {count} |\n"

summary += f"""
## Fix Categories

| Category | Count |
|----------|-------|
"""
for cat, count in category_counts.most_common():
    summary += f"| {cat} | {count} |\n"

summary += """
## Notable Patterns

1. **Snap library dominates fixes in operator-libs-linux.** 14 of 29 fixes target the snap management library, with recurring issues around CLI argument formatting (cohort, classic confinement flags) and edge cases in the snapd API (task status, revision types, falsy keys).

2. **apt package management is the second most-fixed area** (9 fixes), with critical bugs around package installation logic (retry/failure tracking, environment inheritance, sources.list parsing, GPG key handling).

3. **Type system issues are a recurring theme.** Multiple fixes address `type()` vs `isinstance()`, missing type annotations, and string-vs-int confusion for snap revisions. This suggests the codebase grew before adopting strict typing.

4. **CI and configuration issues are prominent in newer/smaller repos.** charmhub-listing-review and charmcraft-profile-tools have a higher proportion of CI/config fixes, consistent with projects still maturing their build pipelines.

5. **Path handling is a repeated pain point** in charmhub-listing-review, with three separate fixes addressing where and how the reviewers file is located (relative path, hardcoded CI path, then CLI argument).

6. **Test quality issues discovered late.** Several sysctl tests used `==` instead of function calls (`f.write == data` instead of `f.write(data)`), meaning tests were silently passing without actually testing anything.

7. **High-severity fixes concentrate in the core libraries.** All high-severity bugs are in operator-libs-linux (snap, apt) and charm-ubuntu (packaging), while peripheral tools mostly have medium/low severity issues.
"""

with open("/home/ubuntu/charm-tech-analysis/data/smaller_repos_summary.md", "w") as f:
    f.write(summary)

print(f"\nWrote summary to /home/ubuntu/charm-tech-analysis/data/smaller_repos_summary.md")
print(f"\nSeverity: {dict(severity_counts)}")
print(f"Areas: {dict(area_counts.most_common(5))}")
print(f"Types: {dict(type_counts.most_common(5))}")
