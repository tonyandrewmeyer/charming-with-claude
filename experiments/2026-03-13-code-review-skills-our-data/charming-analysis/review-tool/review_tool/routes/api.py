"""JSON API routes."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from review_tool import db
from review_tool.config import DB_PATH
from review_tool.models import FindingUpdate
from review_tool.parser import parse_validation_file

router = APIRouter(prefix="/api", tags=["api"])


@router.get("/findings")
async def list_findings(
    severity: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    repo: Optional[str] = Query(None),
    round: Optional[int] = Query(None),
    pattern: Optional[str] = Query(None),
) -> list[dict]:
    conn = await db.get_db(DB_PATH)
    try:
        return await db.get_findings(conn, severity, status, repo, round, pattern)
    finally:
        await conn.close()


@router.get("/findings/{finding_id}")
async def get_finding(finding_id: int) -> dict:
    conn = await db.get_db(DB_PATH)
    try:
        finding = await db.get_finding(conn, finding_id)
        if not finding:
            raise HTTPException(status_code=404, detail="Finding not found")
        return finding
    finally:
        await conn.close()


@router.patch("/findings/{finding_id}")
async def update_finding(finding_id: int, data: FindingUpdate) -> dict:
    conn = await db.get_db(DB_PATH)
    try:
        existing = await db.get_finding(conn, finding_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Finding not found")

        update_data = data.model_dump(exclude_none=True)
        if "review_status" in update_data:
            valid = ("pending", "reviewed", "false_positive")
            if update_data["review_status"] not in valid:
                raise HTTPException(
                    status_code=400, detail=f"Invalid status. Must be one of: {valid}"
                )

        result = await db.update_finding(conn, finding_id, update_data)
        if not result:
            raise HTTPException(status_code=404, detail="Finding not found")
        return result
    finally:
        await conn.close()


@router.post("/import")
async def import_file(
    file_path: str,
    round: int,
    repo: Optional[str] = None,
) -> dict:
    path = Path(file_path)
    if not path.exists():
        raise HTTPException(status_code=400, detail=f"File not found: {file_path}")

    findings, safe = parse_validation_file(path, round, repo)
    conn = await db.get_db(DB_PATH)
    try:
        inserted = 0
        skipped = 0
        for f in findings:
            result = await db.insert_finding(conn, f)
            if result > 0:
                inserted += 1
            else:
                skipped += 1

        safe_count = 0
        for s in safe:
            await db.insert_safe(conn, s)
            safe_count += 1

        await db.log_import(conn, str(path), inserted, safe_count)
        await conn.commit()

        return {
            "inserted": inserted,
            "skipped": skipped,
            "safe_entries": safe_count,
            "source": str(path),
        }
    finally:
        await conn.close()


@router.get("/stats")
async def get_stats() -> dict:
    conn = await db.get_db(DB_PATH)
    try:
        return await db.get_stats(conn)
    finally:
        await conn.close()


@router.get("/export")
async def export_all() -> dict:
    conn = await db.get_db(DB_PATH)
    try:
        findings = await db.get_findings(conn)
        stats = await db.get_stats(conn)
        return {"findings": findings, "stats": stats}
    finally:
        await conn.close()
