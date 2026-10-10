"""RQ-2': supply-chain posture & dependency drift across the charm corpus.

Static pass over local clones (no gh API): ops/pydantic version constraints,
pinning style, lockfile presence, python base, hygiene files (dependabot /
renovate / SECURITY.md / scorecard). Appends one JSONL record per repo per day.
"""
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "lib"))
from corpus import (RESULTS, append_jsonl, extract_constraints, git_head_date,
                    iter_repos, find_charm_roots, load_meta)

OUT = RESULTS / "rq2-supply-chain"
TODAY = datetime.now(timezone.utc).strftime("%Y-%m-%d")


def repo_record(owner: str, name: str, path: Path) -> dict:
    roots = find_charm_roots(path)
    rec = {"date": TODAY, "repo": f"{owner}/{name}", "charms": len(roots)}
    # constraints from the primary (first) charm root; note multi-charm repos
    if roots:
        rec.update(extract_constraints(roots[0]))
        meta = load_meta(roots[0])
        base = meta.get("base")
        if base is None and meta.get("platforms"):
            base = "platforms-only"
        rec["base"] = base
        rec["platforms"] = sorted(meta.get("platforms", {}).keys()) or None
        rec["meta_source"] = ("charmcraft.yaml" if (roots[0] / "charmcraft.yaml").exists()
                              else "metadata.yaml")
    else:
        rec.update({"ops": None, "pydantic": None, "style": None, "decl_files": []})
    # repo-level hygiene files
    gh = path / ".github"
    rec["dependabot"] = (gh / "dependabot.yaml").exists() or (gh / "dependabot.yml").exists()
    rec["renovate"] = (path / "renovate.json").exists() or (path / ".renovaterc").exists() \
        or (gh / "renovate.json").exists()
    rec["security_md"] = (path / "SECURITY.md").exists() or (gh / "SECURITY.md").exists()
    rec["scorecard"] = False
    wf = gh / "workflows"
    if wf.is_dir():
        for f in wf.iterdir():
            try:
                if "scorecard" in f.read_text(errors="replace").lower():
                    rec["scorecard"] = True
                    break
            except Exception:
                continue
    rec["head_date"] = git_head_date(path)
    return rec


def main() -> None:
    n = 0
    for owner, name, path in iter_repos():
        append_jsonl(OUT / "posture.jsonl", repo_record(owner, name, path))
        n += 1
    print(f"rq2: scanned {n} repos -> {OUT/'posture.jsonl'}")


if __name__ == "__main__":
    main()
