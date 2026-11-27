"""Shared helpers for charm corpus research scripts.

Corpus: ~/.cache/hyrum/charms/<owner>/<repo> (git clones, mostly shallow).
A "repo" = top-level owner/repo dir (may contain multiple charms).
A "charm root" = a directory containing charmcraft.yaml (fallback metadata.yaml
at repo root only), or a k8s-style charmcraft.yaml at <repo>/charmcraft.yaml.
"""
from __future__ import annotations

import json
import os
import subprocess
import time
from pathlib import Path

CORPUS = Path.home() / ".cache/hyrum/charms"
RESULTS = Path.home() / "charm-research/results"

NON_CHARM_OWNERS = {"bugs.launchpad.net", "git.launchpad.net", "+source",
                    "landscape-bundles", "openstack-bundles", "ubuntu-repository-cache",
                    "bundle-jupyter", "bundle-kubeflow"}

_META_CACHE: dict = {}


def iter_repos(corpus: Path = CORPUS):
    """Yield (owner, name, path) for repo dirs containing at least one charm."""
    for owner_dir in sorted(corpus.iterdir()):
        if not owner_dir.is_dir():
            continue
        owner = owner_dir.name
        if owner in NON_CHARM_OWNERS:
            continue
        for repo_dir in sorted(owner_dir.iterdir()):
            if not repo_dir.is_dir():
                continue
            if find_charm_roots(repo_dir):
                yield owner, repo_dir.name, repo_dir


def find_charm_roots(repo: Path) -> list[Path]:
    roots = []
    if (repo / "charmcraft.yaml").exists() or (repo / "metadata.yaml").exists():
        roots.append(repo)
    else:
        for sub in sorted(repo.iterdir()) if repo.is_dir() else []:
            if sub.is_dir() and not sub.name.startswith(".") and (sub / "charmcraft.yaml").exists():
                roots.append(sub)
    return roots


def _yaml_cache():
    global _META_CACHE
    if not _META_CACHE:
        import yaml
        _META_CACHE["yaml"] = yaml
    return _META_CACHE["yaml"]


def read_yaml(path: Path) -> dict:
    if not path.exists():
        return {}
    yaml = _yaml_cache()
    try:
        data = yaml.safe_load(path.read_text(errors="replace"))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def load_meta(root: Path) -> dict:
    """Merged view: charmcraft.yaml fields take precedence; metadata.yaml fills gaps."""
    cc = read_yaml(root / "charmcraft.yaml")
    md = read_yaml(root / "metadata.yaml")
    meta = dict(md)
    meta.update(cc)
    return meta


def git_head_date(repo: Path) -> str | None:
    """Local fallback for last-commit date (works in shallow clones for the tip)."""
    try:
        out = subprocess.run(
            ["git", "-C", str(repo), "log", "-1", "--format=%cI"],
            capture_output=True, text=True, timeout=15)
        d = out.stdout.strip()
        return d if out.returncode == 0 and d else None
    except Exception:
        return None


def gh_api(path: str, retries: int = 4):
    """Call `gh api` with retry/backoff. Returns parsed JSON or None on failure."""
    delay = 2.0
    for attempt in range(retries):
        try:
            out = subprocess.run(["gh", "api", path], capture_output=True, text=True, timeout=60)
            if out.returncode == 0:
                return json.loads(out.stdout)
            err = out.stderr.lower()
            if "rate limit" in err or "403" in err or "502" in err or "503" in err or "abuse" in err:
                time.sleep(delay)
                delay *= 2
                continue
            return None  # 404 etc: permanent, don't retry
        except Exception:
            time.sleep(delay)
            delay *= 2
    return None


def rate_limits() -> dict:
    try:
        out = subprocess.run(["gh", "api", "rate_limit"], capture_output=True, text=True, timeout=30)
        if out.returncode != 0:
            return {}
        d = json.loads(out.stdout).get("resources", {})
        return {"core": d.get("core", {}).get("remaining", 0),
                "graphql": d.get("graphql", {}).get("remaining", 0),
                "search": d.get("search", {}).get("remaining", 0)}
    except Exception:
        return {}


def load_state(path: Path, default: dict) -> dict:
    try:
        return json.loads(path.read_text())
    except Exception:
        return dict(default)


def save_state(path: Path, state: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(state, indent=1))
    tmp.replace(path)


def append_jsonl(path: Path, record: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a") as f:
        f.write(json.dumps(record, separators=(",", ":")) + "\n")


def parse_ops_constraint(text: str) -> str | None:
    """Extract the version constraint for 'ops' from a requirements/pyproject line."""
    import re
    m = re.search(r"^\s*ops\s*(?:\[[^\]]*\])?\s*\([^)]*?([<>=!~][^)\s]+)[^)]*\)", text)
    if m:
        return m.group(1)
    m = re.search(r"^\s*ops\s*(?:\[[^\]]*\])?\s*([<>=!~]=?|~=)\s*([0-9][^,;\s'\"]*)", text)
    if m:
        return m.group(1) + m.group(2)
    if re.search(r"^\s*ops\s*(?:\[[^\]]*\])?\s*$", text):
        return "unpinned"
    m = re.search(r"ops\s*(?:\[[^\]]*\])?\s*=\s*['\"]([^'\"]+)['\"]", text)  # poetry: ops = "^2.14"
    if m:
        return m.group(1)
    return None


def parse_pydantic_constraint(text: str) -> str | None:
    import re
    m = re.search(r"pydantic\s*(?:\[[^\]]*\])?\s*([<>=!~]=?|~=)\s*([0-9][^,;\s'\"]*)", text)
    if m:
        return m.group(1) + m.group(2)
    if re.search(r"^\s*pydantic\s*$", text):
        return "unpinned"
    return None


def dep_files(root: Path) -> list[Path]:
    """Dependency-declaring files, deduplicated, in priority order."""
    names = ["pylock.toml", "uv.lock", "poetry.lock", "requirements.txt",
             "requirements-dev.txt", "pyproject.toml", "setup.py"]
    out = []
    for n in names:
        p = root / n
        if p.exists():
            out.append(p)
    return out


def extract_constraints(root: Path) -> dict:
    """Scan dependency files for ops/pydantic constraints and overall pinning style."""
    result = {"ops": None, "pydantic": None, "style": None, "decl_files": []}
    files = dep_files(root)
    result["decl_files"] = [f.name for f in files]
    if any(f.name == "pylock.toml" for f in files):
        result["style"] = "pylock"
    elif any(f.name == "uv.lock" for f in files):
        result["style"] = "uv.lock"
    elif any(f.name == "poetry.lock" for f in files):
        result["style"] = "poetry.lock"

    exact = loose = unpinned = 0
    for f in files:
        if f.suffix == ".lock" or f.name == "pylock.toml":
            continue
        try:
            text = f.read_text(errors="replace")
        except Exception:
            continue
        for line in text.splitlines():
            s = line.strip()
            if not s or s.startswith("#"):
                continue
            if result["ops"] is None:
                c = parse_ops_constraint(s)
                if c:
                    result["ops"] = c
            if result["pydantic"] is None:
                c = parse_pydantic_constraint(s)
                if c:
                    result["pydantic"] = c
            # crude pin classification (skip option lines / urls / comments)
            if s.startswith(("-", "git+", "http", ".")):
                continue
            if any(ch.isalpha() for ch in s.split("=")[0]) or s[0].isalnum():
                if "==" in s:
                    exact += 1
                elif any(op in s for op in (">=", "<=", "~=", "!=", ">", "<", "^")):
                    loose += 1
                elif s[0].isalnum():
                    unpinned += 1
    if result["style"] is None:
        total = exact + loose + unpinned
        if total == 0:
            result["style"] = "none-declared"
        elif unpinned == 0 and loose == 0:
            result["style"] = "exact-pins"
        elif unpinned > total / 2:
            result["style"] = "mostly-unpinned"
        else:
            result["style"] = "mixed"
    return result
