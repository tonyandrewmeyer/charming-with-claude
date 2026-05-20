"""HTML page routes for the web UI."""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from pygments import highlight
from pygments.formatters import HtmlFormatter  # type: ignore[attr-defined]
from pygments.lexers import PythonLexer  # type: ignore[attr-defined]

from review_tool import db
from review_tool.config import DB_PATH

router = APIRouter(tags=["pages"])

_python_lexer = PythonLexer()
_html_formatter = HtmlFormatter(nowrap=False, cssclass="highlight")


def highlight_python(code: str) -> str:
    """Syntax-highlight Python code."""
    return highlight(code, _python_lexer, _html_formatter)


@router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    conn = await db.get_db(DB_PATH)
    try:
        stats = await db.get_stats(conn)
        return request.app.state.templates.TemplateResponse(
            "index.html",
            {"request": request, "stats": stats},
        )
    finally:
        await conn.close()


@router.get("/findings", response_class=HTMLResponse)
async def findings_page(
    request: Request,
    severity: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    repo: Optional[str] = Query(None),
    round: Optional[str] = Query(None),
):
    # Treat empty strings from form selects as None
    severity = severity or None
    status = status or None
    repo = repo or None
    round_int = int(round) if round else None

    conn = await db.get_db(DB_PATH)
    try:
        findings = await db.get_findings(conn, severity, status, repo, round_int)
        stats = await db.get_stats(conn)

        # Get unique repos and rounds for filter dropdowns
        all_findings = await db.get_findings(conn)
        repos = sorted({f["repo"] for f in all_findings})
        rounds = sorted({f["round"] for f in all_findings})

        # If htmx request for just the list partial
        if request.headers.get("HX-Target") == "findings-list":
            return request.app.state.templates.TemplateResponse(
                "partials/findings_list.html",
                {"request": request, "findings": findings},
            )

        return request.app.state.templates.TemplateResponse(
            "findings.html",
            {
                "request": request,
                "findings": findings,
                "stats": stats,
                "repos": repos,
                "rounds": rounds,
                "current_severity": severity or "",
                "current_status": status or "",
                "current_repo": repo or "",
                "current_round": round_int or "",
            },
        )
    finally:
        await conn.close()


@router.get("/findings/{finding_id}", response_class=HTMLResponse)
async def finding_detail(request: Request, finding_id: int):
    conn = await db.get_db(DB_PATH)
    try:
        finding = await db.get_finding(conn, finding_id)
        if not finding:
            return HTMLResponse("<p>Finding not found</p>", status_code=404)

        # Highlight code blocks
        evidence_html = (
            highlight_python(finding["evidence"]) if finding["evidence"] else ""
        )
        fix_html = (
            highlight_python(finding["recommended_fix"])
            if finding["recommended_fix"]
            else ""
        )

        return request.app.state.templates.TemplateResponse(
            "partials/finding_detail.html",
            {
                "request": request,
                "finding": finding,
                "evidence_html": evidence_html,
                "fix_html": fix_html,
            },
        )
    finally:
        await conn.close()


@router.patch("/findings/{finding_id}", response_class=HTMLResponse)
async def update_finding_html(request: Request, finding_id: int):
    conn = await db.get_db(DB_PATH)
    try:
        form = await request.form()
        update_data = {}
        if "review_status" in form:
            update_data["review_status"] = form["review_status"]
        if "reviewer_notes" in form:
            update_data["reviewer_notes"] = form["reviewer_notes"]

        finding = await db.update_finding(conn, finding_id, update_data)
        if not finding:
            return HTMLResponse("<p>Finding not found</p>", status_code=404)

        # Return updated row partial (template uses `f` as the loop variable)
        return request.app.state.templates.TemplateResponse(
            "partials/finding_row.html",
            {"request": request, "f": finding},
        )
    finally:
        await conn.close()


@router.get("/findings/{finding_id}/next-unreviewed")
async def next_unreviewed(finding_id: int):
    conn = await db.get_db(DB_PATH)
    try:
        next_id = await db.get_next_unreviewed(conn, finding_id)
        if next_id:
            return RedirectResponse(url=f"/findings/{next_id}", status_code=303)
        return HTMLResponse("<p>All findings have been reviewed!</p>")
    finally:
        await conn.close()
