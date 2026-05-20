"""SQLite database initialization and queries."""

from __future__ import annotations
import aiosqlite
import sqlite3
from pathlib import Path
from typing import Optional

from review_tool.config import DB_PATH

SCHEMA = """
CREATE TABLE IF NOT EXISTS findings (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    bug_id          TEXT NOT NULL,
    repo            TEXT NOT NULL,
    charm_name      TEXT NOT NULL,
    round           INTEGER NOT NULL,
    category        TEXT NOT NULL,
    title           TEXT NOT NULL,
    severity        TEXT NOT NULL CHECK(severity IN ('Critical','High','Medium','Low')),
    location        TEXT NOT NULL,
    pattern         TEXT NOT NULL,
    issue           TEXT NOT NULL,
    impact          TEXT NOT NULL,
    evidence        TEXT NOT NULL,
    recommended_fix TEXT NOT NULL,
    historical_precedent TEXT NOT NULL DEFAULT '',
    review_status   TEXT NOT NULL DEFAULT 'pending'
                    CHECK(review_status IN ('pending','reviewed','false_positive')),
    reviewer_notes  TEXT NOT NULL DEFAULT '',
    reviewed_at     TEXT,
    source_file     TEXT,
    created_at      TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at      TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE(repo, bug_id)
);

CREATE TABLE IF NOT EXISTS confirmed_safe (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    repo            TEXT NOT NULL,
    round           INTEGER NOT NULL,
    location        TEXT NOT NULL,
    explanation     TEXT NOT NULL,
    source_file     TEXT,
    created_at      TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS import_log (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    source_file     TEXT NOT NULL UNIQUE,
    imported_at     TEXT NOT NULL DEFAULT (datetime('now')),
    findings_count  INTEGER NOT NULL,
    safe_count      INTEGER NOT NULL DEFAULT 0
);
"""


def init_db_sync(db_path: Path = DB_PATH) -> None:
    """Initialise database synchronously (for CLI use)."""
    conn = sqlite3.connect(str(db_path))
    conn.executescript(SCHEMA)
    conn.close()


async def init_db(db_path: Path = DB_PATH) -> None:
    """Initialise database asynchronously."""
    async with aiosqlite.connect(str(db_path)) as db:
        await db.executescript(SCHEMA)


async def get_db(db_path: Path = DB_PATH) -> aiosqlite.Connection:
    """Get an async database connection."""
    db = await aiosqlite.connect(str(db_path))
    db.row_factory = aiosqlite.Row
    await db.execute("PRAGMA journal_mode=WAL")
    return db


def get_db_sync(db_path: Path = DB_PATH) -> sqlite3.Connection:
    """Get a sync database connection."""
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


async def insert_finding(db: aiosqlite.Connection, data: dict) -> int:
    """Insert a finding, returning its id. Skip if duplicate."""
    cols = list(data.keys())
    placeholders = ", ".join(["?"] * len(cols))
    col_names = ", ".join(cols)
    try:
        cursor = await db.execute(
            f"INSERT INTO findings ({col_names}) VALUES ({placeholders})",
            list(data.values()),
        )
        return cursor.lastrowid or 0
    except aiosqlite.IntegrityError:
        return -1


def insert_finding_sync(conn: sqlite3.Connection, data: dict) -> int:
    """Insert a finding synchronously. Skip if duplicate."""
    cols = list(data.keys())
    placeholders = ", ".join(["?"] * len(cols))
    col_names = ", ".join(cols)
    try:
        cursor = conn.execute(
            f"INSERT INTO findings ({col_names}) VALUES ({placeholders})",
            list(data.values()),
        )
        return cursor.lastrowid or 0
    except sqlite3.IntegrityError:
        return -1


async def insert_safe(db: aiosqlite.Connection, data: dict) -> int:
    """Insert a confirmed-safe entry."""
    cols = list(data.keys())
    placeholders = ", ".join(["?"] * len(cols))
    col_names = ", ".join(cols)
    cursor = await db.execute(
        f"INSERT INTO confirmed_safe ({col_names}) VALUES ({placeholders})",
        list(data.values()),
    )
    return cursor.lastrowid or 0


def insert_safe_sync(conn: sqlite3.Connection, data: dict) -> int:
    """Insert a confirmed-safe entry synchronously."""
    cols = list(data.keys())
    placeholders = ", ".join(["?"] * len(cols))
    col_names = ", ".join(cols)
    cursor = conn.execute(
        f"INSERT INTO confirmed_safe ({col_names}) VALUES ({placeholders})",
        list(data.values()),
    )
    return cursor.lastrowid or 0


def get_findings_sync(
    conn: sqlite3.Connection,
    severity: Optional[str] = None,
    status: Optional[str] = None,
    repo: Optional[str] = None,
    round_num: Optional[int] = None,
    pattern: Optional[str] = None,
) -> list[dict]:
    """Query findings with optional filters (sync)."""
    query = "SELECT * FROM findings WHERE 1=1"
    params: list = []
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
    if pattern:
        query += " AND pattern = ?"
        params.append(pattern)
    query += " ORDER BY round, repo, bug_id"
    cursor = conn.execute(query, params)
    return [dict(row) for row in cursor.fetchall()]


def get_finding_sync(conn: sqlite3.Connection, finding_id: int) -> Optional[dict]:
    """Get a single finding by id (sync)."""
    cursor = conn.execute("SELECT * FROM findings WHERE id = ?", [finding_id])
    row = cursor.fetchone()
    return dict(row) if row else None


def update_finding_sync(
    conn: sqlite3.Connection, finding_id: int, data: dict
) -> Optional[dict]:
    """Update a finding's review_status and/or reviewer_notes (sync)."""
    sets: list[str] = []
    params: list = []
    if "review_status" in data and data["review_status"]:
        sets.append("review_status = ?")
        params.append(data["review_status"])
        if data["review_status"] in ("reviewed", "false_positive"):
            sets.append("reviewed_at = datetime('now')")
    if "reviewer_notes" in data and data["reviewer_notes"] is not None:
        sets.append("reviewer_notes = ?")
        params.append(data["reviewer_notes"])
    if not sets:
        return get_finding_sync(conn, finding_id)
    sets.append("updated_at = datetime('now')")
    params.append(finding_id)
    conn.execute(
        f"UPDATE findings SET {', '.join(sets)} WHERE id = ?",
        params,
    )
    conn.commit()
    return get_finding_sync(conn, finding_id)


def get_stats_sync(conn: sqlite3.Connection) -> dict:
    """Get aggregate statistics (sync)."""
    stats: dict = {
        "total": 0,
        "pending": 0,
        "reviewed": 0,
        "false_positive": 0,
        "by_severity": {},
        "by_repo": {},
        "by_round": {},
    }

    stats["total"] = conn.execute("SELECT COUNT(*) FROM findings").fetchone()[0]
    for st in ("pending", "reviewed", "false_positive"):
        row = conn.execute(
            "SELECT COUNT(*) FROM findings WHERE review_status = ?", [st]
        ).fetchone()
        stats[st] = row[0] if row else 0

    cursor = conn.execute(
        "SELECT severity, COUNT(*) FROM findings GROUP BY severity ORDER BY "
        "CASE severity WHEN 'Critical' THEN 1 WHEN 'High' THEN 2 WHEN 'Medium' THEN 3 ELSE 4 END"
    )
    stats["by_severity"] = {row[0]: row[1] for row in cursor.fetchall()}

    cursor = conn.execute(
        "SELECT repo, COUNT(*) FROM findings GROUP BY repo ORDER BY repo"
    )
    stats["by_repo"] = {row[0]: row[1] for row in cursor.fetchall()}

    cursor = conn.execute(
        "SELECT round, COUNT(*) FROM findings GROUP BY round ORDER BY round"
    )
    stats["by_round"] = {row[0]: row[1] for row in cursor.fetchall()}

    return stats


async def get_findings(
    db: aiosqlite.Connection,
    severity: Optional[str] = None,
    status: Optional[str] = None,
    repo: Optional[str] = None,
    round_num: Optional[int] = None,
    pattern: Optional[str] = None,
) -> list[dict]:
    """Query findings with optional filters."""
    query = "SELECT * FROM findings WHERE 1=1"
    params = []
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
    if pattern:
        query += " AND pattern = ?"
        params.append(pattern)
    query += " ORDER BY round, repo, bug_id"
    cursor = await db.execute(query, params)
    rows = await cursor.fetchall()
    return [dict(row) for row in rows]


async def get_finding(db: aiosqlite.Connection, finding_id: int) -> Optional[dict]:
    """Get a single finding by id."""
    cursor = await db.execute("SELECT * FROM findings WHERE id = ?", [finding_id])
    row = await cursor.fetchone()
    return dict(row) if row else None


async def update_finding(
    db: aiosqlite.Connection, finding_id: int, data: dict
) -> Optional[dict]:
    """Update a finding's review_status and/or reviewer_notes."""
    sets = []
    params = []
    if "review_status" in data and data["review_status"]:
        sets.append("review_status = ?")
        params.append(data["review_status"])
        if data["review_status"] in ("reviewed", "false_positive"):
            sets.append("reviewed_at = datetime('now')")
    if "reviewer_notes" in data and data["reviewer_notes"] is not None:
        sets.append("reviewer_notes = ?")
        params.append(data["reviewer_notes"])
    if not sets:
        return await get_finding(db, finding_id)
    sets.append("updated_at = datetime('now')")
    params.append(finding_id)
    await db.execute(
        f"UPDATE findings SET {', '.join(sets)} WHERE id = ?",
        params,
    )
    await db.commit()
    return await get_finding(db, finding_id)


async def get_stats(db: aiosqlite.Connection) -> dict:
    """Get aggregate statistics."""
    stats = {
        "total": 0,
        "pending": 0,
        "reviewed": 0,
        "false_positive": 0,
        "by_severity": {},
        "by_repo": {},
        "by_round": {},
    }

    cursor = await db.execute("SELECT COUNT(*) FROM findings")
    row = await cursor.fetchone()
    stats["total"] = row[0] if row else 0

    for status in ("pending", "reviewed", "false_positive"):
        cursor = await db.execute(
            "SELECT COUNT(*) FROM findings WHERE review_status = ?", [status]
        )
        row = await cursor.fetchone()
        stats[status] = row[0] if row else 0

    cursor = await db.execute(
        "SELECT severity, COUNT(*) as cnt FROM findings GROUP BY severity ORDER BY "
        "CASE severity WHEN 'Critical' THEN 1 WHEN 'High' THEN 2 WHEN 'Medium' THEN 3 ELSE 4 END"
    )
    stats["by_severity"] = {row[0]: row[1] for row in await cursor.fetchall()}

    cursor = await db.execute(
        "SELECT repo, COUNT(*) as cnt FROM findings GROUP BY repo ORDER BY repo"
    )
    stats["by_repo"] = {row[0]: row[1] for row in await cursor.fetchall()}

    cursor = await db.execute(
        "SELECT round, COUNT(*) as cnt FROM findings GROUP BY round ORDER BY round"
    )
    stats["by_round"] = {row[0]: row[1] for row in await cursor.fetchall()}

    return stats


async def get_next_unreviewed(
    db: aiosqlite.Connection, current_id: int
) -> Optional[int]:
    """Get the next unreviewed finding id after current_id."""
    cursor = await db.execute(
        "SELECT id FROM findings WHERE review_status = 'pending' AND id > ? ORDER BY id LIMIT 1",
        [current_id],
    )
    row = await cursor.fetchone()
    if row:
        return row[0]
    # Wrap around
    cursor = await db.execute(
        "SELECT id FROM findings WHERE review_status = 'pending' ORDER BY id LIMIT 1"
    )
    row = await cursor.fetchone()
    return row[0] if row else None


async def log_import(
    db: aiosqlite.Connection, source_file: str, findings_count: int, safe_count: int
) -> None:
    """Log an import."""
    try:
        await db.execute(
            "INSERT INTO import_log (source_file, findings_count, safe_count) VALUES (?, ?, ?)",
            [source_file, findings_count, safe_count],
        )
    except aiosqlite.IntegrityError:
        await db.execute(
            "UPDATE import_log SET imported_at = datetime('now'), findings_count = ?, safe_count = ? WHERE source_file = ?",
            [findings_count, safe_count, source_file],
        )
