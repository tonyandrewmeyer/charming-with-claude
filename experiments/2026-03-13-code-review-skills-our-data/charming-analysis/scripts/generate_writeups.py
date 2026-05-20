#!/usr/bin/env python3
"""Generate per-repo team writeup files from skill_validation_*.md data."""

import json
import re
import subprocess
from collections import defaultdict
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
REPOS_DIR = Path(__file__).parent.parent / "repos"
OUTPUT_DIR = Path(__file__).parent.parent / "writeups"

TOTAL_REPOS = 42  # total repos reviewed

# Per-repo file intro (no background — that's in the email)
REPO_INTRO = """\
# Bug Findings: {repo_name}

## Summary

- **Findings**: {total} ({severity_summary})

Note that the severity was picked by AI and I don't necessarily agree with all of them, but it's a handy base classification.

(If there's anything that looks to me (not just AI) like a security finding, they were excluded and I'll handle them separately.)

## Findings
"""

# Draft email per team
EMAIL_TEMPLATE = """\
Hi!

Hope you're doing well! Also apologies for disturbing you at a busy time of year.

I've been doing some experimentation into building a skill that finds bugs in charms, based on all the bugs that have already been fixed. You don't need to read all the gory details, but they are in the [Charming with Claude](https://github.com/tonyandrewmeyer/charming-with-claude) experiment "2026-03-13-code-review-skills-our-data" if you do.

After validating the skill against repos not used in its construction, I ran it across {total_repos} repositories. I've attached the findings for your repos below. Each finding includes the location, a description of the issue, its impact, the relevant code, and a suggested fix.

I have not verified these findings against the running charm — they are based on static analysis of the source code at the time of review. Some may be mitigated by runtime conditions not visible in the code, or may have already been addressed.

I don't want to open a bunch of issues or PRs in your repos with what might turn out to be AI slop. On the other hand, if there are actual bugs here, it would be good to solve them. Also, somewhat selfishly, I would love extra data on any false positives to feed back into the skill, to try to make it something actually useful across charming.

Basically: the ball is in your court. You can ignore these, you can review them and open issues yourself (in many cases Copilot should be able to provide a draft fix; these aren't complex issues). You can ask me to open issues and/or PRs.

Your repos with findings:

{repo_list}

Ngā mihi,
Tony
"""

SEVERITY_ORDER = ["Critical", "High", "Medium", "Low"]

PEBBLE_ENV_CAVEAT_NONE = (
    "\n\n> **Note**: `None` values in Pebble environment dicts do cause `add_layer` "
    "to fail. However, non-string values like `int`, `bool`, and `float` are "
    "silently coerced to strings by Pebble's Go YAML decoder (see "
    "[pebble-non-string-env.md](https://github.com/tonyandrewmeyer/charming-with-claude"
    "/blob/main/experiments/2026-03-13-code-review-skills-our-data/charming-analysis"
    "/pebble-non-string-env.md) for details). The `None` part of this finding is "
    "a real crash; the non-string part is a code quality issue with no runtime impact.\n"
)

PEBBLE_ENV_CAVEAT_NON_STRING_ONLY = (
    "\n\n> **Note**: Pebble silently coerces non-string scalar values (`int`, `bool`, "
    "`float`) to strings via its Go YAML decoder — so this does not crash at runtime "
    "(see [pebble-non-string-env.md](https://github.com/tonyandrewmeyer/charming-with-claude"
    "/blob/main/experiments/2026-03-13-code-review-skills-our-data/charming-analysis"
    "/pebble-non-string-env.md) for details). "
    "It is still technically incorrect and relies on undocumented behaviour, but "
    "the practical impact is minimal.\n"
)

PEBBLE_ENV_CAVEAT_BYTES = (
    "\n\n> **Note**: Non-string scalar values (`int`, `bool`, `float`) in Pebble "
    "environment dicts are silently coerced to strings by Pebble's Go YAML decoder "
    "(see [pebble-non-string-env.md](https://github.com/tonyandrewmeyer/charming-with-claude"
    "/blob/main/experiments/2026-03-13-code-review-skills-our-data/charming-analysis"
    "/pebble-non-string-env.md) for details). "
    "However, `bytes` objects may not be handled the same way.\n"
)


def build_repo_to_team_map() -> dict[str, str]:
    """Build a mapping from repo directory name to team using batch_manifest.json."""
    manifest_path = DATA_DIR / "batch_manifest.json"
    manifest = json.loads(manifest_path.read_text())

    repo_to_team = {}
    for batch in manifest:
        team = batch["team"]
        for repo in batch["repos"]:
            if repo not in repo_to_team:
                repo_to_team[repo] = team
    return repo_to_team


def get_github_url(repo_dir_name: str) -> str | None:
    """Get the GitHub base URL for a repo."""
    repo_path = REPOS_DIR / repo_dir_name
    if not repo_path.exists():
        return None
    try:
        result = subprocess.run(
            ["git", "-C", str(repo_path), "remote", "get-url", "origin"],
            capture_output=True, text=True, check=True,
        )
        url = result.stdout.strip().removesuffix(".git")
        # Get the default branch
        result2 = subprocess.run(
            ["git", "-C", str(repo_path), "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True, text=True, check=True,
        )
        branch = result2.stdout.strip()
        return f"{url}/blob/{branch}"
    except subprocess.CalledProcessError:
        return None


def get_repo_dir_name(repo_name: str) -> str | None:
    """Map the repo name from the validation file to the directory name in repos/."""
    # Direct match
    if (REPOS_DIR / repo_name).exists():
        return repo_name

    # Try common variations
    variations = [
        repo_name,
        f"{repo_name}-operator",
        f"{repo_name}-k8s-operator",
    ]
    for v in variations:
        if (REPOS_DIR / v).exists():
            return v

    # Known mappings for tricky names
    known = {
        "grafana-agent": "grafana-agent-k8s-operator",
        "seldon-core": "seldon-core-operator",
        "zookeeper": "zookeeper-k8s-operator",
        "sdcore-amf-k8s-operator": "sdcore-amf-operator",
    }
    if repo_name in known and (REPOS_DIR / known[repo_name]).exists():
        return known[repo_name]

    # Fuzzy: check all repo dirs for a substring match
    core = repo_name.replace("-operator", "").replace("-k8s", "")
    for d in sorted(REPOS_DIR.iterdir()):
        if d.is_dir() and core in d.name:
            return d.name

    return None


def parse_validation_file(filepath: Path) -> dict:
    """Parse a skill_validation_*.md file into structured data."""
    text = filepath.read_text()

    # Extract repo name from header
    header_match = re.match(r"## Bug Review:\s*(.+)", text)
    repo_name = header_match.group(1).strip() if header_match else filepath.stem

    # Clean up repo name (remove " src/ directory", " src/", trailing slashes, parentheticals, etc.)
    repo_name = re.sub(r"\s*(src/?|src/ directory|--.*|\(.*\))", "", repo_name).strip()
    repo_name = repo_name.rstrip("/").strip()
    # Special cases
    repo_name = repo_name.replace("directory", "").strip()

    # Extract summary line
    findings_match = re.search(
        r"\*\*Findings\*\*:\s*(\d+)\s*\(([^)]+)\)", text
    )
    total = int(findings_match.group(1)) if findings_match else 0
    severity_summary = findings_match.group(2) if findings_match else ""

    # Extract areas
    areas_match = re.search(
        r"\*\*Code areas reviewed\*\*:\s*(.+)", text
    )
    areas = areas_match.group(1).strip() if areas_match else ""

    # Split into findings section and confirmed safe section
    findings_text = text
    confirmed_safe_idx = text.find("### Confirmed Safe")
    if confirmed_safe_idx >= 0:
        findings_text = text[:confirmed_safe_idx]

    # Parse individual findings
    finding_pattern = re.compile(
        r"####\s+\[([^\]]+)\]\s+(.+?)\s*\((\w+)\)\s*\n(.*?)(?=####|\Z)",
        re.DOTALL,
    )

    findings = []
    for match in finding_pattern.finditer(findings_text):
        bug_id = match.group(1)
        title_raw = match.group(2).strip()
        severity = match.group(3)
        body = match.group(4).strip()

        # Determine if this is a security finding
        is_security = "Security --" in title_raw or "Security —" in title_raw

        # Clean up title: remove category prefix like "Action Handler -- "
        title = re.sub(r"^.*?--\s*", "", title_raw).strip()
        # Get category
        category_match = re.match(r"^(.*?)\s*--", title_raw)
        category = category_match.group(1).strip() if category_match else ""

        findings.append({
            "bug_id": bug_id,
            "title": title,
            "category": category,
            "severity": severity,
            "body": body,
            "is_security": is_security,
        })

    return {
        "repo_name": repo_name,
        "total": total,
        "severity_summary": severity_summary,
        "areas": areas,
        "findings": findings,
    }


def make_github_link(location: str, github_base: str | None) -> str:
    """Convert a location like `src/charm.py:358` to a GitHub link."""
    if not github_base:
        return f"`{location}`"

    # Parse file:line
    loc_match = re.match(r"`?([^`:]+?)(?::(\d+))?`?$", location.strip())
    if not loc_match:
        return f"`{location}`"

    filepath = loc_match.group(1)
    line = loc_match.group(2)

    if line:
        # Could be multiple lines like "425,449,474,498"
        lines = line.split(",")
        first_line = lines[0].strip()
        return f"[`{filepath}:{line}`]({github_base}/{filepath}#L{first_line})"
    else:
        return f"[`{filepath}`]({github_base}/{filepath})"


def transform_finding_body(body: str, github_base: str | None) -> str:
    """Transform a finding body from internal format to writeup format."""
    lines = body.split("\n")
    output_lines = []
    skip_until_next_field = False

    i = 0
    while i < len(lines):
        line = lines[i]

        # Skip Pattern line
        if line.startswith("- **Pattern**:"):
            i += 1
            continue

        # Skip Historical precedent
        if line.startswith("- **Historical precedent**:"):
            i += 1
            continue

        # Transform Location to include GitHub link
        loc_match = re.match(r"- \*\*Location\*\*:\s*(.+)", line)
        if loc_match:
            location = loc_match.group(1).strip()
            # Handle multiple locations (e.g., "src/charm.py:425,449,474,498")
            linked = make_github_link(location, github_base)
            output_lines.append(f"**Location**: {linked}")
            output_lines.append("")
            i += 1
            continue

        # Transform field markers from "- **X**:" to "**X**:"
        field_match = re.match(r"- \*\*(\w[\w\s]*)\*\*:\s*(.*)", line)
        if field_match:
            field_name = field_match.group(1)
            field_value = field_match.group(2)

            # Rename Evidence -> Code
            if field_name == "Evidence":
                field_name = "Code"

            # Ensure blank line before each field for readability
            if output_lines and output_lines[-1] != "":
                output_lines.append("")
            output_lines.append(f"**{field_name}**: {field_value}")
            i += 1
            continue

        # Pass through everything else (code blocks, etc.)
        output_lines.append(line)
        i += 1

    # Clean up trailing whitespace and excessive blank lines
    result = "\n".join(output_lines).strip()
    result = re.sub(r"\n{3,}", "\n\n", result)
    return result


def is_pebble_env_finding(finding: dict) -> bool:
    """Check if a finding is about non-string Pebble environment values."""
    title_lower = finding["title"].lower()
    body_lower = finding["body"].lower()
    return (
        ("non-string" in title_lower or "non_string" in title_lower)
        and ("pebble" in title_lower or "environment" in title_lower)
    ) or (
        "ap-005" in body_lower
        and "pebble" in body_lower
    )


def get_pebble_env_caveat(finding: dict) -> str:
    """Return the appropriate Pebble env caveat for a finding, or empty string."""
    if not is_pebble_env_finding(finding):
        return ""

    body_lower = finding["body"].lower()

    has_none = "none" in body_lower and (
        "none value" in body_lower
        or "returns none" in body_lower
        or "return none" in body_lower
        or "is none" in body_lower
        or "be none" in body_lower
        or "can be `none`" in body_lower
        or "rejects `none`" in body_lower
        or "rejects none" in body_lower
        or "= none" in body_lower
    )
    has_bytes = "bytes" in body_lower or "b64encode" in body_lower

    if has_none:
        return PEBBLE_ENV_CAVEAT_NONE
    elif has_bytes:
        return PEBBLE_ENV_CAVEAT_BYTES
    else:
        return PEBBLE_ENV_CAVEAT_NON_STRING_ONLY


def generate_writeup(data: dict, github_base: str | None) -> str:
    """Generate the full writeup markdown for a repo."""
    # Filter out security findings
    non_security = [f for f in data["findings"] if not f["is_security"]]

    if not non_security:
        return ""

    # Recalculate counts
    severity_counts = {s: 0 for s in SEVERITY_ORDER}
    for f in non_security:
        if f["severity"] in severity_counts:
            severity_counts[f["severity"]] += 1

    total = sum(severity_counts.values())
    severity_parts = []
    for s in SEVERITY_ORDER:
        if severity_counts[s] > 0:
            severity_parts.append(f"{severity_counts[s]} {s}")
    severity_summary = ", ".join(severity_parts)

    output = REPO_INTRO.format(
        repo_name=data["repo_name"],
        total=total,
        severity_summary=severity_summary,
    )

    # Group findings by severity
    for severity in SEVERITY_ORDER:
        findings_at_level = [
            f for f in non_security if f["severity"] == severity
        ]
        if not findings_at_level:
            continue

        output += f"\n### {severity}\n\n"

        for finding in findings_at_level:
            output += f"#### {finding['bug_id']}: {finding['title']}\n\n"
            transformed = transform_finding_body(finding["body"], github_base)
            output += transformed
            # Add Pebble env caveat if applicable
            caveat = get_pebble_env_caveat(finding)
            if caveat:
                output += caveat
            output += "\n\n---\n\n"

    return output.rstrip("\n-— \n") + "\n"


def generate_email(team: str, repo_summaries: list[tuple[str, int]]) -> str:
    """Generate the draft email for a team."""
    repo_lines = []
    for repo_name, count in repo_summaries:
        repo_lines.append(f"- **{repo_name}** ({count} findings)")

    return EMAIL_TEMPLATE.format(
        total_repos=TOTAL_REPOS,
        repo_list="\n".join(repo_lines),
    )


def main():
    # Build repo-to-team mapping
    repo_to_team = build_repo_to_team_map()

    validation_files = sorted(DATA_DIR.glob("skill_validation_*.md"))
    print(f"Found {len(validation_files)} validation files")

    generated = 0
    skipped_no_findings = 0
    skipped_all_security = 0

    # Track repos per team for email generation
    team_repos: dict[str, list[tuple[str, int]]] = defaultdict(list)

    for vf in validation_files:
        data = parse_validation_file(vf)

        # Find the repo directory
        repo_dir = get_repo_dir_name(data["repo_name"])
        github_base = get_github_url(repo_dir) if repo_dir else None

        # Determine team
        team = repo_to_team.get(repo_dir, "Unknown") if repo_dir else "Unknown"

        if not github_base:
            print(f"  WARNING: No GitHub URL for {data['repo_name']} (dir: {repo_dir})")

        non_security = [f for f in data["findings"] if not f["is_security"]]
        if not non_security:
            if data["findings"]:
                skipped_all_security += 1
                print(f"  SKIP (all security): {data['repo_name']}")
            else:
                skipped_no_findings += 1
                print(f"  SKIP (no findings): {data['repo_name']}")
            continue

        writeup = generate_writeup(data, github_base)
        if not writeup:
            skipped_no_findings += 1
            continue

        # Output to team folder
        team_dir = OUTPUT_DIR / team
        team_dir.mkdir(parents=True, exist_ok=True)

        safe_name = re.sub(r"[^a-zA-Z0-9_-]", "_", data["repo_name"])
        output_path = team_dir / f"{safe_name}.md"
        output_path.write_text(writeup)
        generated += 1

        # Track for email
        team_repos[team].append((data["repo_name"], len(non_security)))

        # Count findings
        sec_count = len(data["findings"]) - len(non_security)
        sec_note = f" ({sec_count} security excluded)" if sec_count else ""
        print(f"  OK: [{team}] {data['repo_name']} -> {output_path.relative_to(OUTPUT_DIR)} ({len(non_security)} findings{sec_note})")

    # Generate draft emails per team
    for team, repos in sorted(team_repos.items()):
        email = generate_email(team, repos)
        email_path = OUTPUT_DIR / team / "_email_draft.md"
        email_path.write_text(email)
        total_findings = sum(count for _, count in repos)
        print(f"  EMAIL: {team} ({len(repos)} repos, {total_findings} findings)")

    print(f"\nDone: {generated} writeups generated, {len(team_repos)} team emails, {skipped_no_findings} skipped (no findings), {skipped_all_security} skipped (all security)")


if __name__ == "__main__":
    main()
