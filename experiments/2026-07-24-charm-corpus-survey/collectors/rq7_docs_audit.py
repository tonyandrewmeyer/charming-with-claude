"""RQ-7: docs & listing-quality audit across the charm corpus.

Static pass (no gh API): records the *rung* of the documentation ladder each
repo reaches, plus listing metadata signals:
  1  links.documentation in charmcraft.yaml / metadata.yaml
  2  docs/ (or doc/) directory in repo
  3  docs-ish URL in README (discourse / readthedocs / charmhub docs page)
  4  nothing found
Also: README length + charmcraft-init boilerplate match, CONTRIBUTING.md
presence/size, description/summary quality, links coverage, and charmhub
name match for later listing checks.
"""
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "lib"))
from corpus import RESULTS, append_jsonl, iter_repos, find_charm_roots, load_meta

OUT = RESULTS / "rq7-docs"
TODAY = datetime.now(timezone.utc).strftime("%Y-%m-%d")

DOCS_URL = re.compile(
    r"(discourse\.charmhub\.io|charmhub\.io/[^\s)'\"]+/docs|readthedocs|documentation\.ubuntu\.com)",
    re.IGNORECASE)
INIT_BOILERPLATE = [
    "charmcraft init",
    "this is a template",
    "TODO: fill out the following",
    "create a new charm",
]


def read_text(p: Path, limit: int = 400_000) -> str:
    try:
        return p.read_text(errors="replace")[:limit]
    except Exception:
        return ""


def readme(path: Path) -> tuple[Path | None, str]:
    for name in ("README.md", "README.rst", "README.txt", "README"):
        p = path / name
        if p.exists():
            return p, read_text(p)
    return None, ""


def main() -> None:
    n = 0
    for owner, repo, path in iter_repos():
        roots = find_charm_roots(path)
        meta = load_meta(roots[0]) if roots else {}
        links = meta.get("links") or {}
        doc_link = links.get("documentation") or meta.get("docs")  # legacy metadata.yaml 'docs'

        docs_dir = next((d for d in ("docs", "doc") if (path / d).is_dir()), None)
        rpath, rtext = readme(path)
        docs_url_in_readme = bool(DOCS_URL.search(rtext)) if rtext else False

        if doc_link:
            rung = 1
        elif docs_dir:
            rung = 2
        elif docs_url_in_readme:
            rung = 3
        else:
            rung = 4

        lower = rtext.lower()
        boiler = any(b in lower for b in INIT_BOILERPLATE)
        contrib = next((c for c in ("CONTRIBUTING.md", "CONTRIBUTING.rst", "CONTRIBUTING")
                        if (path / c).exists()), None)
        contrib_size = (path / contrib).stat().st_size if contrib else 0

        desc = meta.get("description") or ""
        summary = meta.get("summary") or ""
        rec = {
            "date": TODAY, "repo": f"{owner}/{repo}",
            "rung": rung,
            "doc_link": doc_link or None,
            "docs_dir": docs_dir,
            "docs_url_in_readme": docs_url_in_readme,
            "readme_bytes": len(rtext),
            "readme_boilerplate": boiler,
            "contributing": contrib,
            "contributing_bytes": contrib_size,
            "has_description": bool(desc.strip()),
            "has_summary": bool(summary.strip()),
            "desc_is_templated": bool(re.search(r"(^|\b)(a juju charm|charm for)\b\.?$", desc.strip().lower())) or None,
            "links": sorted(links.keys()) or None,
            "charm_name": meta.get("name"),
        }
        append_jsonl(OUT / "docs-audit.jsonl", rec)
        n += 1
    print(f"rq7: audited {n} repos -> {OUT/'docs-audit.jsonl'}")


if __name__ == "__main__":
    main()
