"""Markdown parser for skill_validation_*.md files."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Optional


def parse_validation_file(
    filepath: Path,
    round_num: int,
    repo_override: Optional[str] = None,
) -> tuple[list[dict], list[dict]]:
    """Parse a skill validation markdown file.

    Returns (findings, confirmed_safe) where each finding is a dict
    ready for database insertion.
    """
    text = filepath.read_text()
    filename = filepath.name

    # Extract repo from header
    repo: str = repo_override or ""
    if not repo:
        m = re.search(r"## Bug Review:\s*(\S+)", text)
        if m:
            repo = m.group(1).rstrip("/")

    # Extract charm name
    charm_name = ""
    m = re.search(r"\*\*Charm name\*\*:\s*(.+)", text)
    if m:
        charm_name = m.group(1).strip()

    findings = _parse_findings(text, repo, charm_name, round_num, filename)
    safe = _parse_confirmed_safe(text, repo, round_num, filename)

    return findings, safe


def _parse_findings(
    text: str,
    repo: str,
    charm_name: str,
    round_num: int,
    source_file: str,
) -> list[dict]:
    """Extract individual bug findings from the markdown."""
    findings = []

    # Split on #### [BUG- to isolate each finding
    parts = re.split(r"(?=####\s*\[BUG-)", text)

    for part in parts:
        if not part.strip().startswith("#### [BUG-"):
            continue

        finding = _parse_single_finding(part, repo, charm_name, round_num, source_file)
        if finding:
            findings.append(finding)

    return findings


def _parse_single_finding(
    block: str,
    repo: str,
    charm_name: str,
    round_num: int,
    source_file: str,
) -> Optional[dict]:
    """Parse a single finding block."""
    # Header: #### [BUG-001] Category -- Title (Severity)
    header_match = re.match(
        r"####\s*\[(BUG-\d+)\]\s+(.+?)\s+--\s+(.+?)\s+\((\w+)\)",
        block,
    )
    if not header_match:
        return None

    bug_id = header_match.group(1)
    category = header_match.group(2).strip()
    title = header_match.group(3).strip()
    severity = header_match.group(4).strip()

    def extract_field(name: str) -> str:
        pattern = rf"- \*\*{name}\*\*:\s*(.+?)(?=\n- \*\*|\n####|\n###|\Z)"
        m = re.search(pattern, block, re.DOTALL)
        if m:
            return m.group(1).strip()
        return ""

    location = extract_field("Location")
    # Clean backticks from location
    location = location.strip("`")

    pattern = extract_field("Pattern")
    issue = extract_field("Issue")
    impact = extract_field("Impact")
    historical = extract_field("Historical precedent")

    evidence = _extract_code_section(block, "Evidence")
    recommended_fix = _extract_code_section(block, "Recommended fix")

    return {
        "bug_id": bug_id,
        "repo": repo,
        "charm_name": charm_name,
        "round": round_num,
        "category": category,
        "title": title,
        "severity": severity,
        "location": location,
        "pattern": pattern,
        "issue": issue,
        "impact": impact,
        "evidence": evidence,
        "recommended_fix": recommended_fix,
        "historical_precedent": historical,
        "source_file": source_file,
    }


def _extract_code_section(block: str, field_name: str) -> str:
    """Extract content after a field label, including code blocks."""
    # Find the field start
    pattern = rf"- \*\*{field_name}\*\*:\s*"
    m = re.search(pattern, block)
    if not m:
        return ""

    # Get everything from after the label to the next field or section
    rest = block[m.end() :]

    # Find the end: next "- **" field or "###" section header
    end_match = re.search(r"\n- \*\*(?!.*```)", rest)
    if end_match:
        rest = rest[: end_match.start()]

    # Also check for next section
    section_match = re.search(r"\n###\s", rest)
    if section_match:
        if not end_match or section_match.start() < len(rest):
            rest = rest[: section_match.start()]

    return rest.strip()


def _parse_confirmed_safe(
    text: str,
    repo: str,
    round_num: int,
    source_file: str,
) -> list[dict]:
    """Parse the Confirmed Safe section."""
    safe_entries = []

    # Find the Confirmed Safe section
    m = re.search(r"### Confirmed Safe\s*\n(.*)", text, re.DOTALL)
    if not m:
        return safe_entries

    safe_text = m.group(1)

    # Parse bullet points: - **Description** (location): explanation
    bullets = re.findall(
        r"- \*\*(.+?)\*\*\s*(?:\(([^)]+)\))?\s*:\s*(.+?)(?=\n- \*\*|\Z)",
        safe_text,
        re.DOTALL,
    )

    for desc, location, explanation in bullets:
        loc = location.strip() if location else desc.strip()
        safe_entries.append(
            {
                "repo": repo,
                "round": round_num,
                "location": loc,
                "explanation": f"{desc.strip()}: {explanation.strip()}",
                "source_file": source_file,
            }
        )

    return safe_entries
