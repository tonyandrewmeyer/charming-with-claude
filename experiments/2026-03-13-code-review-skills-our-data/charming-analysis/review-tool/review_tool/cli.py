"""CLI for the review tool."""

from __future__ import annotations

import builtins
import json
import sqlite3
import sys
from pathlib import Path
from typing import Optional

import click
import uvicorn

from review_tool.app import create_app
from review_tool.config import FILE_REPO_MAP
from review_tool.db import (
    get_db_sync,
    init_db_sync,
    insert_finding_sync,
    insert_safe_sync,
)
from review_tool.logging_setup import setup_logging
from review_tool.parser import parse_validation_file


@click.group()
def cli():
    """Charm bug finding review tool."""
    setup_logging()


@cli.command()
@click.option("--port", default=8000, help="Port to serve on.")
@click.option("--host", default="0.0.0.0", help="Host to bind to.")
def serve(port: int, host: str):
    """Start the local web server."""
    app = create_app()
    uvicorn.run(app, host=host, port=port)


@cli.command()
def tui():
    """Start the terminal UI (Textual)."""
    from review_tool.tui import run_tui

    run_tui()


@cli.command(name="import")
@click.argument("file_path", type=click.Path(exists=True))
@click.option(
    "--round", "round_num", type=int, required=True, help="Validation round number."
)
@click.option("--repo", default=None, help="Override repository name.")
def import_file(file_path: str, round_num: int, repo: Optional[str]):
    """Import findings from a markdown validation file."""
    path = Path(file_path)
    init_db_sync()

    if not repo:
        repo = FILE_REPO_MAP.get(path.name)

    findings, safe = parse_validation_file(path, round_num, repo)
    conn = get_db_sync()

    inserted = 0
    skipped = 0
    for f in findings:
        result = insert_finding_sync(conn, f)
        if result > 0:
            inserted += 1
        else:
            skipped += 1

    safe_count = 0
    for s in safe:
        insert_safe_sync(conn, s)
        safe_count += 1

    # Log import
    try:
        conn.execute(
            "INSERT INTO import_log (source_file, findings_count, safe_count) VALUES (?, ?, ?)",
            [str(path), inserted, safe_count],
        )
    except sqlite3.IntegrityError:
        conn.execute(
            "UPDATE import_log SET imported_at = datetime('now'), findings_count = ?, safe_count = ? WHERE source_file = ?",
            [inserted, safe_count, str(path)],
        )

    conn.commit()
    conn.close()

    click.echo(
        f"Imported {inserted} findings, {skipped} skipped (duplicates), {safe_count} confirmed safe entries."
    )


@cli.command(name="import-all")
def import_all():
    """Import all existing validation files."""
    data_dir = Path(__file__).resolve().parent.parent.parent / "data"
    init_db_sync()

    files_rounds = {
        "skill_validation_grafana.md": 1,
        "skill_validation_kafka.md": 1,
        "skill_validation_discourse.md": 2,
        "skill_validation_hydra.md": 2,
        "skill_validation_opensearch.md": 2,
        "skill_validation_sdcore_amf.md": 2,
        "skill_validation_traefik.md": 3,
        "skill_validation_temporal.md": 3,
        "skill_validation_vault.md": 3,
        "skill_validation_mongodb.md": 3,
        "skill_validation_postgresql.md": 4,
        "skill_validation_indico.md": 4,
        "skill_validation_prometheus.md": 4,
        "skill_validation_kratos.md": 4,
        "skill_validation_alertmanager.md": 5,
        "skill_validation_loki.md": 5,
        "skill_validation_oathkeeper.md": 5,
        "skill_validation_pgbouncer.md": 5,
        "skill_validation_redis.md": 5,
        "skill_validation_synapse.md": 5,
        "skill_validation_tempo_coordinator.md": 5,
        "skill_validation_wordpress.md": 5,
        "skill_validation_postgresql_vm.md": 6,
        "skill_validation_grafana_agent.md": 6,
        "skill_validation_zookeeper.md": 6,
        "skill_validation_seldon.md": 6,
        "skill_validation_pgbouncer_vm.md": 7,
        "skill_validation_trino.md": 7,
        "skill_validation_cos_proxy.md": 7,
        "skill_validation_mlflow.md": 7,
        "skill_validation_identity_admin_ui.md": 8,
        "skill_validation_cos_configuration.md": 8,
        "skill_validation_superset.md": 8,
        "skill_validation_sdcore_nms.md": 8,
        "skill_validation_self_signed_certs.md": 9,
        "skill_validation_gunicorn.md": 9,
        "skill_validation_openfga.md": 9,
        "skill_validation_mimir_coordinator.md": 9,
        "skill_validation_hardware_observer.md": 10,
        "skill_validation_kubeflow_profiles.md": 10,
        "skill_validation_nginx_ingress.md": 10,
        "skill_validation_content_cache.md": 10,
    }

    total_inserted = 0
    total_safe = 0
    for filename, round_num in files_rounds.items():
        path = data_dir / filename
        if not path.exists():
            click.echo(f"  Skipping {filename}: not found")
            continue

        repo = FILE_REPO_MAP.get(filename)
        findings, safe = parse_validation_file(path, round_num, repo)
        conn = get_db_sync()

        inserted = 0
        for f in findings:
            result = insert_finding_sync(conn, f)
            if result > 0:
                inserted += 1

        safe_count = 0
        for s in safe:
            insert_safe_sync(conn, s)
            safe_count += 1

        try:
            conn.execute(
                "INSERT INTO import_log (source_file, findings_count, safe_count) VALUES (?, ?, ?)",
                [str(path), inserted, safe_count],
            )
        except sqlite3.IntegrityError:
            conn.execute(
                "UPDATE import_log SET imported_at = datetime('now'), findings_count = ?, safe_count = ? WHERE source_file = ?",
                [inserted, safe_count, str(path)],
            )

        conn.commit()
        conn.close()

        click.echo(f"  {filename}: {inserted} findings, {safe_count} safe")
        total_inserted += inserted
        total_safe += safe_count

    click.echo(
        f"\nTotal: {total_inserted} findings, {total_safe} confirmed safe entries."
    )


@cli.command(name="list")
@click.option("--severity", default=None, help="Filter by severity.")
@click.option("--status", default=None, help="Filter by review status.")
@click.option("--repo", default=None, help="Filter by repository.")
@click.option("--round", "round_num", type=int, default=None, help="Filter by round.")
def list_findings(
    severity: Optional[str],
    status: Optional[str],
    repo: Optional[str],
    round_num: Optional[int],
):
    """List findings in a table."""
    init_db_sync()
    conn = get_db_sync()

    query = "SELECT * FROM findings WHERE 1=1"
    params: builtins.list[str | int] = []
    if severity:
        query += " AND severity = ?"
        params.append(severity)
    if status:
        query += " AND review_status = ?"
        params.append(status)
    if repo:
        query += " AND repo = ?"
        params.append(repo)
    if round_num is not None:
        query += " AND round = ?"
        params.append(round_num)
    query += " ORDER BY round, repo, bug_id"

    cursor = conn.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        click.echo("No findings match the filters.")
        return

    # Print table
    click.echo(
        f"{'ID':>4} {'Sev':>8} {'Bug':>8} {'Repo':<25} {'R':>2} {'Status':<14} Title"
    )
    click.echo("-" * 100)
    for r in rows:
        status_icon = {"pending": ".", "reviewed": "+", "false_positive": "x"}.get(
            r["review_status"], "?"
        )
        click.echo(
            f"{r['id']:>4} {r['severity']:>8} {r['bug_id']:>8} {r['repo']:<25} {r['round']:>2} "
            f"{status_icon} {r['review_status']:<12} {r['title'][:50]}"
        )
    click.echo(f"\n{len(rows)} findings.")


@cli.command()
@click.argument("finding_id", type=int)
def show(finding_id: int):
    """Show a single finding in detail."""
    init_db_sync()
    conn = get_db_sync()
    cursor = conn.execute("SELECT * FROM findings WHERE id = ?", [finding_id])
    row = cursor.fetchone()
    conn.close()

    if not row:
        click.echo(f"Finding {finding_id} not found.")
        sys.exit(1)

    click.echo(
        f"[{row['bug_id']}] {row['category']} -- {row['title']} ({row['severity']})"
    )
    click.echo(
        f"Repo: {row['repo']} | Charm: {row['charm_name']} | Round: {row['round']}"
    )
    click.echo(f"Location: {row['location']}")
    click.echo(f"Pattern: {row['pattern']}")
    click.echo(f"Status: {row['review_status']}")
    if row["reviewer_notes"]:
        click.echo(f"Notes: {row['reviewer_notes']}")
    click.echo(f"\n--- Issue ---\n{row['issue']}")
    click.echo(f"\n--- Impact ---\n{row['impact']}")
    click.echo(f"\n--- Evidence ---\n{row['evidence']}")
    click.echo(f"\n--- Recommended Fix ---\n{row['recommended_fix']}")
    if row["historical_precedent"]:
        click.echo(f"\n--- Historical Precedent ---\n{row['historical_precedent']}")


@cli.command()
@click.argument("finding_id", type=int)
@click.option(
    "--status",
    required=True,
    type=click.Choice(["reviewed", "false_positive", "pending"]),
)
@click.option("--notes", default=None, help="Reviewer notes.")
def review(finding_id: int, status: str, notes: Optional[str]):
    """Update the review status of a finding."""
    init_db_sync()
    conn = get_db_sync()

    cursor = conn.execute("SELECT id FROM findings WHERE id = ?", [finding_id])
    if not cursor.fetchone():
        click.echo(f"Finding {finding_id} not found.")
        sys.exit(1)

    sets = ["review_status = ?", "updated_at = datetime('now')"]
    params: builtins.list[str | int] = [status]
    if status in ("reviewed", "false_positive"):
        sets.append("reviewed_at = datetime('now')")
    if notes is not None:
        sets.append("reviewer_notes = ?")
        params.append(notes)
    params.append(finding_id)

    conn.execute(f"UPDATE findings SET {', '.join(sets)} WHERE id = ?", params)
    conn.commit()
    conn.close()
    click.echo(f"Finding {finding_id} marked as '{status}'.")


@cli.command()
def stats():
    """Show summary statistics."""
    init_db_sync()
    conn = get_db_sync()

    total = conn.execute("SELECT COUNT(*) FROM findings").fetchone()[0]
    if total == 0:
        click.echo("No findings in the database.")
        conn.close()
        return

    pending = conn.execute(
        "SELECT COUNT(*) FROM findings WHERE review_status = 'pending'"
    ).fetchone()[0]
    reviewed = conn.execute(
        "SELECT COUNT(*) FROM findings WHERE review_status = 'reviewed'"
    ).fetchone()[0]
    fp = conn.execute(
        "SELECT COUNT(*) FROM findings WHERE review_status = 'false_positive'"
    ).fetchone()[0]

    click.echo(
        f"Total: {total} | Reviewed: {reviewed} | False Positive: {fp} | Pending: {pending}"
    )
    click.echo(
        f"Progress: {reviewed + fp}/{total} ({100 * (reviewed + fp) / total:.0f}%)"
    )

    click.echo("\nBy Severity:")
    for row in conn.execute(
        "SELECT severity, COUNT(*) FROM findings GROUP BY severity "
        "ORDER BY CASE severity WHEN 'Critical' THEN 1 WHEN 'High' THEN 2 WHEN 'Medium' THEN 3 ELSE 4 END"
    ):
        click.echo(f"  {row[0]}: {row[1]}")

    click.echo("\nBy Repository:")
    for row in conn.execute(
        "SELECT repo, COUNT(*) FROM findings GROUP BY repo ORDER BY repo"
    ):
        click.echo(f"  {row[0]}: {row[1]}")

    click.echo("\nBy Round:")
    for row in conn.execute(
        "SELECT round, COUNT(*) FROM findings GROUP BY round ORDER BY round"
    ):
        click.echo(f"  Round {row[0]}: {row[1]}")

    conn.close()


@cli.command()
@click.option(
    "--output", "-o", default=None, type=click.Path(), help="Output file path."
)
def export(output: Optional[str]):
    """Export all findings as JSON."""
    init_db_sync()
    conn = get_db_sync()

    cursor = conn.execute("SELECT * FROM findings ORDER BY round, repo, bug_id")
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()

    data = json.dumps({"findings": rows, "count": len(rows)}, indent=2)

    if output:
        Path(output).write_text(data)
        click.echo(f"Exported {len(rows)} findings to {output}")
    else:
        click.echo(data)
