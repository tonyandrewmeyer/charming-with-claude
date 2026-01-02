#!/usr/bin/env python3
"""Generate RSS feed for experiments and READTHEM.md updates."""

import os
import re
import subprocess
from datetime import datetime
from pathlib import Path


def get_git_info(path: str) -> tuple[str, str, str] | None:
    """Get the git commit info (author name, email, date) for a path.
    
    Returns the info for the most recent commit that touched this path.
    """
    try:
        result = subprocess.run(
            [
                "git",
                "log",
                "-1",
                "--format=%an|%ae|%ad",
                "--date=iso-strict",
                "--",
                path,
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        if result.stdout.strip():
            author, email, date = result.stdout.strip().split("|")
            return author, email, date
        return None
    except (subprocess.CalledProcessError, ValueError):
        return None


def get_readthem_updates() -> list[dict]:
    """Get all updates to READTHEM.md from git history."""
    try:
        result = subprocess.run(
            [
                "git",
                "log",
                "--format=%H|%an|%ae|%ad|%s",
                "--date=iso-strict",
                "--",
                "READTHEM.md",
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        
        updates = []
        for line in result.stdout.strip().split("\n"):
            if not line:
                continue
            parts = line.split("|", 4)
            if len(parts) == 5:
                commit_hash, author, email, date, subject = parts
                
                # Get the diff for this commit
                diff_result = subprocess.run(
                    [
                        "git",
                        "show",
                        "--format=",
                        f"{commit_hash}",
                        "--",
                        "READTHEM.md",
                    ],
                    capture_output=True,
                    text=True,
                    check=True,
                )
                
                github_url = f"https://github.com/tonyandrewmeyer/charming-with-claude/commit/{commit_hash}"
                
                updates.append({
                    "commit_hash": commit_hash,
                    "author": author,
                    "email": email,
                    "date": date,
                    "subject": subject,
                    "diff": diff_result.stdout,
                    "github_url": github_url,
                })
        
        return updates
    except subprocess.CalledProcessError:
        return []


def get_experiments() -> list[dict]:
    """Get all experiment directories and their metadata."""
    experiments = []
    experiments_dir = Path("experiments")
    
    if not experiments_dir.exists():
        return experiments
    
    # Pattern for YYYY-MM-DD-name
    pattern = re.compile(r"^(\d{4})-(\d{2})-(\d{2})-(.+)$")
    
    for entry in sorted(experiments_dir.iterdir()):
        if not entry.is_dir():
            continue
        
        match = pattern.match(entry.name)
        if not match:
            continue
        
        year, month, day, name = match.groups()
        date_str = f"{year}-{month}-{day}"
        
        readme_path = entry / "README.md"
        if not readme_path.exists():
            continue
        
        with open(readme_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Get git info for this experiment
        git_info = get_git_info(str(entry))
        if git_info:
            author, email, commit_date = git_info
        else:
            # Fallback to the date from the folder name
            author = "Unknown"
            email = "unknown@example.com"
            commit_date = f"{date_str}T00:00:00+00:00"
        
        experiments.append({
            "date": date_str,
            "name": name,
            "folder": entry.name,
            "content": content,
            "author": author,
            "email": email,
            "commit_date": commit_date,
        })
    
    return experiments


def generate_rss(experiments: list[dict], readthem_updates: list[dict]) -> str:
    """Generate RSS 2.0 feed XML."""
    # Combine all items and sort by date (most recent first)
    all_items = []
    
    # Add experiments
    for exp in experiments:
        all_items.append({
            "title": f"New Experiment: {exp['name'].replace('-', ' ').title()}",
            "link": f"https://github.com/tonyandrewmeyer/charming-with-claude/tree/main/experiments/{exp['folder']}",
            "description": f"New experiment: {exp['name'].replace('-', ' ')}",
            "content": exp["content"],
            "author": exp["author"],
            "email": exp["email"],
            "pubDate": exp["commit_date"],
            "guid": f"experiment-{exp['folder']}",
        })
    
    # Add READTHEM updates
    for update in readthem_updates:
        all_items.append({
            "title": f"Reading List Update: {update['subject']}",
            "link": update["github_url"],
            "description": update["subject"],
            "content": f"<pre>{escape_xml(update['diff'])}</pre>",
            "author": update["author"],
            "email": update["email"],
            "pubDate": update["date"],
            "guid": f"readthem-{update['commit_hash']}",
        })
    
    # Sort by publication date (most recent first)
    all_items.sort(key=lambda x: x["pubDate"], reverse=True)
    
    # Build RSS feed manually to avoid namespace issues
    rss_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom" xmlns:content="http://purl.org/rss/1.0/modules/content/" xmlns:dc="http://purl.org/dc/elements/1.1/">',
        '  <channel>',
        '    <title>Charming with Claude - Updates</title>',
        '    <link>https://github.com/tonyandrewmeyer/charming-with-claude</link>',
        '    <description>Updates from the Charming with Claude repository: new experiments and reading list additions</description>',
        '    <atom:link href="https://tonyandrewmeyer.github.io/charming-with-claude/feed.rss" rel="self" type="application/rss+xml"/>',
    ]
    
    # Add items
    for item_data in all_items:
        rss_lines.append('    <item>')
        rss_lines.append(f'      <title>{escape_xml(item_data["title"])}</title>')
        rss_lines.append(f'      <link>{escape_xml(item_data["link"])}</link>')
        rss_lines.append(f'      <description>{escape_xml(item_data["description"])}</description>')
        rss_lines.append(f'      <content:encoded><![CDATA[{item_data["content"]}]]></content:encoded>')
        rss_lines.append(f'      <dc:creator>{escape_xml(item_data["author"])}</dc:creator>')
        
        # Convert date to RFC 822 format
        try:
            dt = datetime.fromisoformat(item_data["pubDate"])
            rfc822_date = dt.strftime("%a, %d %b %Y %H:%M:%S %z")
            rss_lines.append(f'      <pubDate>{rfc822_date}</pubDate>')
        except ValueError:
            pass
        
        rss_lines.append(f'      <guid isPermaLink="false">{escape_xml(item_data["guid"])}</guid>')
        rss_lines.append('    </item>')
    
    rss_lines.append('  </channel>')
    rss_lines.append('</rss>')
    
    return '\n'.join(rss_lines)


def escape_xml(text: str) -> str:
    """Escape XML special characters."""
    return (text
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&apos;"))


def main():
    """Generate RSS feed and write to file."""
    # Change to repository root
    repo_root = Path(__file__).parent
    os.chdir(repo_root)
    
    experiments = get_experiments()
    readthem_updates = get_readthem_updates()
    
    rss_content = generate_rss(experiments, readthem_updates)
    
    output_file = Path("feed.rss")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(rss_content)
    
    print(f"RSS feed generated: {output_file}")
    print(f"  - {len(experiments)} experiment(s)")
    print(f"  - {len(readthem_updates)} READTHEM.md update(s)")


if __name__ == "__main__":
    main()
