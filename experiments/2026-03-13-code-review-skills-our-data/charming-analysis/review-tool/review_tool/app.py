"""FastAPI application setup."""

from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

import markdown as md
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from jinja2 import Environment, FileSystemLoader
from markupsafe import Markup

from review_tool import db
from review_tool.config import DB_PATH
from review_tool.routes.api import router as api_router
from review_tool.routes.pages import router as pages_router

TEMPLATE_DIR = Path(__file__).parent / "templates"
STATIC_DIR = Path(__file__).parent / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialise the database on startup."""
    await db.init_db(DB_PATH)
    yield


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(title="Charm Bug Review Tool", lifespan=lifespan)

    # Templates
    env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)), autoescape=True)
    env.filters["markdown"] = lambda text: (
        # Findings are authored locally by the reviewer, not untrusted input.
        Markup(md.markdown(text, extensions=["fenced_code", "tables"]))  # noqa: S704
        if text
        else ""
    )
    app.state.templates = _TemplateAdapter(env)

    # Static files
    if STATIC_DIR.exists():
        app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

    # Routes
    app.include_router(pages_router)
    app.include_router(api_router)

    return app


class _TemplateAdapter:
    """Adapt Jinja2 Environment to work like Starlette's Jinja2Templates."""

    def __init__(self, env: Environment):
        self.env = env

    def TemplateResponse(  # noqa: N802  # Mirrors Starlette's Jinja2Templates API.
        self, name: str, context: dict, status_code: int = 200
    ):
        from starlette.responses import HTMLResponse

        template = self.env.get_template(name)
        html = template.render(**context)
        return HTMLResponse(html, status_code=status_code)
