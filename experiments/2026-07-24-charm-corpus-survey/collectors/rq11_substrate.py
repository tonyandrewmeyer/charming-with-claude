"""RQ-11: charmcraft substrate adoption across the charm corpus.

Static pass (no gh API): base / platforms (incl. arm64) / plugin / framework
extension usage per charm. Appends one JSONL record per charm per day —
the time series builds the migration curves.
"""
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "lib"))
from corpus import RESULTS, append_jsonl, iter_repos, find_charm_roots, load_meta

OUT = RESULTS / "rq11-substrate"
TODAY = datetime.now(timezone.utc).strftime("%Y-%m-%d")

FRAMEWORK_EXTS = ("flask-framework", "django-framework", "fastapi-framework",
                  "go-framework", "expressjs-framework", "spring-boot-framework")


KNOWN_ARCHES = {"amd64", "arm64", "armhf", "ppc64el", "s390x", "riscv64", "aarch64"}


def extract_archs(platforms: dict) -> set:
    archs = set()
    for key, pdata in platforms.items():
        # compound key form: "ubuntu@24.04:amd64" with null value
        if ":" in key:
            suffix = key.split(":")[-1]
            if suffix in KNOWN_ARCHES:
                archs.add(suffix)
        if isinstance(pdata, dict):
            for k in ("build-on", "build-for"):
                v = pdata.get(k)
                if isinstance(v, str):
                    archs.add(v)
                elif isinstance(v, list):
                    for item in v:
                        archs.add(item.get("name") if isinstance(item, dict) else item)
        elif isinstance(pdata, str):
            archs.add(pdata)
        elif isinstance(pdata, list):
            archs.update(x for x in pdata if isinstance(x, str))
    return archs


def base_value(meta: dict):
    base = meta.get("base")
    if base is None and meta.get("bases"):
        vals = []
        for b in meta["bases"]:
            if not isinstance(b, dict):
                continue
            if "name" in b:
                vals.append(f"{b.get('name','?')}@{b.get('channel','?')}")
            else:  # old style: - build-on: [{name, channel}] / run-on: [...]
                for phase in ("run-on", "build-on"):
                    for tgt in b.get(phase) or []:
                        if isinstance(tgt, dict) and tgt.get("name"):
                            vals.append(f"{tgt['name']}@{tgt.get('channel','?')}")
        base = sorted(set(vals)) or None
    if base is None and meta.get("platforms"):
        base = "platforms-only"
    return base


def charm_record(owner: str, repo: str, root: Path) -> dict:
    rel = str(root.relative_to(root.parents[1])) if root.name != root.parents[1].name else root.name
    meta = load_meta(root)
    platforms = meta.get("platforms") or {}
    exts = meta.get("extensions") or []
    parts = meta.get("parts") or {}
    plugins = sorted({p.get("plugin") for p in parts.values()
                      if isinstance(p, dict) and p.get("plugin")})
    archs = extract_archs(platforms)
    return {"date": TODAY, "charm": f"{owner}/{repo}:{rel}",
            "base": base_value(meta),
            "has_charmcraft_yaml": (root / "charmcraft.yaml").exists(),
            "platforms": sorted(platforms.keys()) or None,
            "archs": sorted(archs) or None,
            "arm64": bool(archs & {"arm64", "aarch64"}) or None,
            "plugins": plugins or None,
            "framework_ext": next((e for e in exts if e in FRAMEWORK_EXTS), None),
            "other_exts": [e for e in exts if e not in FRAMEWORK_EXTS] or None,
            "type": meta.get("type")}


def main() -> None:
    n = 0
    for owner, repo, path in iter_repos():
        for root in find_charm_roots(path):
            append_jsonl(OUT / "substrate.jsonl", charm_record(owner, repo, root))
            n += 1
    print(f"rq11: scanned {n} charms -> {OUT/'substrate.jsonl'}")


if __name__ == "__main__":
    main()
