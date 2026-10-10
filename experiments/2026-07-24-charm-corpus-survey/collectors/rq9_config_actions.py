"""RQ-9: config & action surface ergonomics across the charm corpus.

Static pass (no gh API): config option counts/types/descriptions, should-be-secret
heuristics, action counts/descriptions/params, and action-name frequency for the
naming-inconsistency table. Appends one JSONL record per charm per day; also writes
action-names.json (cumulative) for cross-charm name analysis.
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "lib"))
from corpus import RESULTS, append_jsonl, iter_repos, find_charm_roots, read_yaml

OUT = RESULTS / "rq9-config-actions"
TODAY = datetime.now(timezone.utc).strftime("%Y-%m-%d")

SECRETISH = ("password", "passwd", "secret", "token", "apikey", "api-key",
             "private-key", "privatekey", "credential", "passphrase")


def charm_record(owner: str, repo: str, root: Path) -> dict:
    rel = str(root.relative_to(root.parents[1])) if root.name != root.parents[1].name else root.name
    cfg = read_yaml(root / "config.yaml").get("options", {}) or {}
    cc = read_yaml(root / "charmcraft.yaml")
    cfg = cc.get("config", {}).get("options", cfg) or cfg  # new-style inline config
    actions = read_yaml(root / "actions.yaml") or {}
    actions = cc.get("actions", actions) or actions  # new-style inline actions

    n_opts = len(cfg)
    typed = sum(1 for o in cfg.values() if isinstance(o, dict) and o.get("type"))
    described = sum(1 for o in cfg.values() if isinstance(o, dict) and o.get("description"))
    secretish_plain = [k for k, o in cfg.items()
                       if isinstance(o, dict)
                       and any(s in k.lower() for s in SECRETISH)
                       and o.get("type") not in ("secret", None)]
    secret_typed = sum(1 for o in cfg.values() if isinstance(o, dict) and o.get("type") == "secret")

    n_acts = len(actions)
    act_described = sum(1 for a in actions.values() if isinstance(a, dict) and a.get("description"))
    act_with_params = sum(1 for a in actions.values() if isinstance(a, dict) and a.get("params"))

    return {"date": TODAY, "charm": f"{owner}/{repo}:{rel}",
            "config_options": n_opts, "config_typed": typed, "config_described": described,
            "config_secret_typed": secret_typed, "secretish_plain": secretish_plain or None,
            "actions": n_acts, "actions_described": act_described,
            "actions_with_params": act_with_params,
            "action_names": sorted(actions.keys()) or None}


def main() -> None:
    names_path = OUT / "action-names.json"
    try:
        names = json.loads(names_path.read_text())
    except Exception:
        names = {}
    n = 0
    for owner, repo, path in iter_repos():
        for root in find_charm_roots(path):
            rec = charm_record(owner, repo, root)
            append_jsonl(OUT / "surface.jsonl", rec)
            for a in rec["action_names"] or []:
                entry = names.setdefault(a.lower(), {"count": 0, "variants": [], "users": []})
                if isinstance(entry.get("variants"), list) is False:
                    entry["variants"] = []
                entry["count"] += 1
                if a not in entry["variants"]:
                    entry["variants"].append(a)
                if len(entry["users"]) < 200:
                    entry["users"].append(rec["charm"])
            n += 1
    for v in names.values():
        v["variants"] = sorted(set(v["variants"]))
    names_path.write_text(json.dumps(names, indent=1, sort_keys=True))
    print(f"rq9: scanned {n} charms -> {OUT/'surface.jsonl'}; {len(names)} distinct action names")


if __name__ == "__main__":
    main()
