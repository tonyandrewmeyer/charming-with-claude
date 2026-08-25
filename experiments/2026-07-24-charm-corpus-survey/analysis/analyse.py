"""Derive every table in WRITEUP.md from the raw collector output.

The raw JSONL is too large to commit (~90 MB), so this script reads it from a
live results directory and writes the small derived artefacts under `data/`.
Everything here is deterministic: given the same results directory it produces
byte-identical output.

    python3 analysis/analyse.py --results ~/charm-research/results --out data

Two things worth knowing before reading the numbers:

* The static passes stamp rows with the UTC date and blindly append, so a UTC
  day can carry more than one run. Every static table dedupes on
  `(date, repo)` / `(date, charm)` and reports the last complete day.
* `classified.jsonl` only ever covered the repos the classify phase reached
  (303 of 461 with content), so the RQ-6 tables ignore it and re-run the same
  deterministic classifier over every file in `raw/` instead.
"""

from __future__ import annotations

import argparse
import collections
import csv
import datetime
import json
import pathlib
import re
import sys

PLATFORM = (
    "platform-cos",
    "platform-tls",
    "platform-terraform",
    "platform-airgap",
    "platform-backup",
    "platform-arm64",
)

# Repos that hold a charm but are really a web property, a site, or shared
# tooling. They dominate RQ-6 by volume (canonical/ubuntu.com alone is 16% of
# every item fetched) and say nothing about charming, so the headline RQ-6
# numbers exclude them and the full-corpus numbers are reported alongside.
WEB_EXTRA = {
    "vanilla-framework",
    "dashboard",
    "assets",
    "marketplace-analytics",
    "webteam-webbot",
    "open-graph-images-generator",
    "snap-recommendation-service",
    "charming-actions",
}

# canonical/bundle-kubeflow was fetched twice, once under the owner it was
# transferred from. Same issues, near-identical numbering.
ALIASES = {"juju-solutions/bundle-kubeflow": "canonical/bundle-kubeflow"}

# The reference "now" for every age calculation, so reruns stay reproducible.
AS_OF = datetime.datetime(2026, 8, 26, tzinfo=datetime.timezone.utc)


def is_web(repo: str) -> bool:
    """Report whether a repo holds a charm but is really a website or shared tooling."""
    name = repo.split("/", 1)[1]
    return "." in name or name in WEB_EXTRA


def canonical_repo(repo: str) -> str:
    """Fold a repo that was fetched under more than one owner onto one name."""
    return ALIASES.get(repo, repo)


def read_jsonl(path: pathlib.Path):
    """Yield each record of a JSONL file, skipping blank and unparseable lines."""
    with path.open(errors="replace") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    yield json.loads(line)
                except ValueError:
                    continue


def by_day(path: pathlib.Path, key: str) -> dict:
    """Dedupe on (date, key). Returns {date: {key: record}}."""
    days: dict[str, dict] = collections.defaultdict(dict)
    for rec in read_jsonl(path):
        days[rec["date"]][rec[key]] = rec
    return days


def age_days(stamp: str) -> int:
    """Days between an ISO timestamp and the pinned reference date."""
    when = datetime.datetime.fromisoformat(stamp.replace("Z", "+00:00"))
    return (AS_OF - when).days


def write_json(out: pathlib.Path, name: str, payload) -> None:
    """Write one derived artefact, sorted so reruns are byte-identical."""
    out.mkdir(parents=True, exist_ok=True)
    (out / name).write_text(json.dumps(payload, indent=1, sort_keys=True) + "\n")
    print(f"wrote {out / name}")


# --------------------------------------------------------------------------
# churn: the evidence that the static passes stopped paying for themselves
# --------------------------------------------------------------------------


def churn(results: pathlib.Path, out: pathlib.Path) -> None:
    """Count how many rows changed from one day to the next, per static pass."""
    sources = [
        ("rq2", "rq2-supply-chain/posture.jsonl", "repo", ("date", "head_date")),
        ("rq7", "rq7-docs/docs-audit.jsonl", "repo", ("date",)),
        ("rq9", "rq9-config-actions/surface.jsonl", "charm", ("date",)),
        ("rq11", "rq11-substrate/substrate.jsonl", "charm", ("date",)),
    ]
    table: dict[str, dict] = collections.defaultdict(dict)
    for rq, rel, key, ignore in sources:
        days = by_day(results / rel, key)
        previous = None
        for date in sorted(days):
            current = {
                k: {a: b for a, b in v.items() if a not in ignore} for k, v in days[date].items()
            }
            if previous is not None:
                changed = sum(1 for k in current if k in previous and current[k] != previous[k])
                table[date][rq] = (len(current), changed, len(set(current) - set(previous)))
            previous = current
    out.mkdir(parents=True, exist_ok=True)
    with (out / "churn.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["date", "rq", "rows", "changed_vs_previous_day", "new_rows"])
        for date in sorted(table):
            for rq in ("rq2", "rq7", "rq9", "rq11"):
                if rq in table[date]:
                    w.writerow([date, rq, *table[date][rq]])
    print(f"wrote {out / 'churn.csv'}")


# --------------------------------------------------------------------------
# static passes: RQ-2, RQ-7, RQ-9, RQ-11
# --------------------------------------------------------------------------


def ops_bucket(value: str | None) -> str:
    """Group a raw version constraint into the form it takes."""
    if value is None:
        return "not declared"
    if value == "unpinned":
        return "unpinned"
    for prefix, label in (
        ("===", "exact"),
        ("==", "exact"),
        ("~=", "compatible"),
        ("^", "caret"),
        (">=", "lower bound"),
        (">", "lower bound"),
        ("<", "upper bound only"),
    ):
        if value.startswith(prefix):
            return label
    return "other"


def static(results: pathlib.Path, out: pathlib.Path) -> dict:
    """Summarise RQ-2, RQ-7, RQ-9 and RQ-11 from their last complete day."""
    summary: dict = {}

    days = by_day(results / "rq2-supply-chain/posture.jsonl", "repo")
    date = max(days)
    rq2 = days[date]
    summary["rq2"] = {
        "date": date,
        "repos": len(rq2),
        "style": dict(collections.Counter(r["style"] for r in rq2.values())),
        "ops_constraint": dict(
            collections.Counter(ops_bucket(r.get("ops")) for r in rq2.values())
        ),
        "ops_verbatim_top": collections.Counter(
            str(r.get("ops")) for r in rq2.values()
        ).most_common(20),
        "pydantic_declared": sum(1 for r in rq2.values() if r.get("pydantic")),
        "dependabot": sum(1 for r in rq2.values() if r.get("dependabot")),
        "renovate": sum(1 for r in rq2.values() if r.get("renovate")),
        "either_bot": sum(1 for r in rq2.values() if r.get("dependabot") or r.get("renovate")),
        "security_md": sum(1 for r in rq2.values() if r.get("security_md")),
        "scorecard": sum(1 for r in rq2.values() if r.get("scorecard")),
        "multi_charm_repos": sum(1 for r in rq2.values() if (r.get("charms") or 0) > 1),
    }

    days = by_day(results / "rq7-docs/docs-audit.jsonl", "repo")
    date = max(days)
    rq7 = days[date]
    readme = sorted(r["readme_bytes"] for r in rq7.values())
    per_owner = collections.defaultdict(collections.Counter)
    for repo, r in rq7.items():
        per_owner[repo.split("/", 1)[0]][r["rung"]] += 1
    summary["rq7"] = {
        "date": date,
        "repos": len(rq7),
        "rung": dict(collections.Counter(r["rung"] for r in rq7.values())),
        "doc_link": sum(1 for r in rq7.values() if r.get("doc_link")),
        "docs_dir": sum(1 for r in rq7.values() if r.get("docs_dir")),
        "docs_url_in_readme": sum(1 for r in rq7.values() if r.get("docs_url_in_readme")),
        "contributing": sum(1 for r in rq7.values() if r.get("contributing")),
        "readme_bytes_median": readme[len(readme) // 2],
        "readme_empty": sum(1 for b in readme if b == 0),
        "readme_under_500b": sum(1 for b in readme if b < 500),
        "readme_boilerplate": sum(1 for r in rq7.values() if r.get("readme_boilerplate")),
        "has_summary": sum(1 for r in rq7.values() if r.get("has_summary")),
        "no_links_block": sum(1 for r in rq7.values() if not r.get("links")),
        "links_keys": dict(
            collections.Counter(k for r in rq7.values() for k in (r.get("links") or []))
        ),
        "rung_by_owner": {
            o: dict(c)
            for o, c in sorted(per_owner.items(), key=lambda kv: -sum(kv[1].values()))[:8]
        },
    }

    days = by_day(results / "rq9-config-actions/surface.jsonl", "charm")
    date = max(days)
    rq9 = days[date]
    options = sum(r["config_options"] for r in rq9.values())
    actions = sum(r["actions"] for r in rq9.values())
    names = collections.Counter(a for r in rq9.values() for a in (r.get("action_names") or []))
    families = collections.defaultdict(set)
    for a in names:
        families[re.sub(r"[-_]", "", a.lower())].add(a)
    secretish = {k: v["secretish_plain"] for k, v in rq9.items() if v.get("secretish_plain")}
    summary["rq9"] = {
        "date": date,
        "charms": len(rq9),
        "config_options": options,
        "charms_with_no_config": sum(1 for r in rq9.values() if r["config_options"] == 0),
        "config_typed": sum(r["config_typed"] for r in rq9.values()),
        "config_described": sum(r["config_described"] for r in rq9.values()),
        "config_secret_typed": sum(r["config_secret_typed"] for r in rq9.values()),
        "charms_using_secret_type": sum(1 for r in rq9.values() if r["config_secret_typed"]),
        "secretish_plain_keys": sum(len(v) for v in secretish.values()),
        "secretish_plain_charms": len(secretish),
        "secretish_worst": sorted(((len(v), k) for k, v in secretish.items()), reverse=True)[:10],
        "actions": actions,
        "charms_with_no_actions": sum(1 for r in rq9.values() if r["actions"] == 0),
        "actions_described": sum(r["actions_described"] for r in rq9.values()),
        "actions_with_params": sum(r["actions_with_params"] for r in rq9.values()),
        "distinct_action_names": len(names),
        "action_names_used_once": sum(1 for v in names.values() if v == 1),
        "action_names_top": names.most_common(25),
        "action_name_separator_collisions": {
            k: sorted(v) for k, v in families.items() if len(v) > 1
        },
    }

    days = by_day(results / "rq11-substrate/substrate.jsonl", "charm")
    date = max(days)
    rq11 = days[date]

    def base_label(v):
        """Render a base declaration, legacy list form included, as one label."""
        if v is None:
            return "none declared"
        if isinstance(v, list):
            return "bases[] (legacy): " + ",".join(v)
        return v

    def declares_arm64(r) -> bool:
        """Report whether the charm targets arm64, compound platform keys included."""
        # r["arm64"] misses charms whose platforms are shorthand keys, because
        # their build-for values arrive as "ubuntu@24.04:arm64" rather than a
        # bare arch. Recount off the suffix instead.
        for value in (r.get("archs") or []) + (r.get("platforms") or []):
            if value.split(":")[-1] in ("arm64", "aarch64"):
                return True
        return False

    summary["rq11"] = {
        "date": date,
        "charms": len(rq11),
        "base": dict(collections.Counter(base_label(r.get("base")) for r in rq11.values())),
        "has_charmcraft_yaml": sum(1 for r in rq11.values() if r.get("has_charmcraft_yaml")),
        "platforms_declared": sum(1 for r in rq11.values() if r.get("platforms")),
        "arm64_as_recorded": sum(1 for r in rq11.values() if r.get("arm64")),
        "arm64_recounted": sum(1 for r in rq11.values() if declares_arm64(r)),
        "archs": dict(
            collections.Counter(
                a.split(":")[-1] for r in rq11.values() for a in (r.get("archs") or [])
            )
        ),
        "framework_ext": dict(
            collections.Counter(
                r["framework_ext"] for r in rq11.values() if r.get("framework_ext")
            )
        ),
        "plugins": dict(
            collections.Counter(p for r in rq11.values() for p in (r.get("plugins") or []))
        ),
        "type": dict(collections.Counter(str(r.get("type")) for r in rq11.values())),
    }

    write_json(out, "static-summary.json", summary)

    # The final day of each static pass, deduped, as the snapshot of record.
    snapshot = out / f"snapshot-{summary['rq2']['date']}"
    snapshot.mkdir(parents=True, exist_ok=True)
    for rel, key, name in (
        ("rq2-supply-chain/posture.jsonl", "repo", "rq2-posture.jsonl"),
        ("rq7-docs/docs-audit.jsonl", "repo", "rq7-docs-audit.jsonl"),
        ("rq9-config-actions/surface.jsonl", "charm", "rq9-surface.jsonl"),
        ("rq11-substrate/substrate.jsonl", "charm", "rq11-substrate.jsonl"),
    ):
        days = by_day(results / rel, key)
        rows = days[max(days)]
        with (snapshot / name).open("w") as f:
            for k in sorted(rows):
                f.write(json.dumps(rows[k], separators=(",", ":"), sort_keys=True) + "\n")
        print(f"wrote {snapshot / name} ({len(rows)} rows)")
    return summary


# --------------------------------------------------------------------------
# RQ-6
# --------------------------------------------------------------------------


def classify_all(results: pathlib.Path, collectors: pathlib.Path) -> dict:
    """Re-run the shipped heuristic classifier over every raw file."""
    sys.path.insert(0, str(collectors))
    sys.path.insert(0, str(collectors / "lib"))
    import rq6_issues as heuristics

    items = {}
    for path in sorted((results / "rq6-issues/raw").glob("*.jsonl")):
        for rec in read_jsonl(path):
            cats = heuristics.classify(rec.get("title") or "", rec.get("labels") or [])
            rec["categories"] = sorted(cats)
            items[(rec["repo"], rec["number"])] = rec
    return items


def rq6(results: pathlib.Path, collectors: pathlib.Path, out: pathlib.Path) -> dict:
    """Summarise RQ-6 over every fetched item, in both the charm-only and full cuts."""
    raw_dir = results / "rq6-issues/raw"
    items = classify_all(results, collectors)
    overlay = {
        (r["repo"], r["number"]): r
        for r in read_jsonl(results / "rq6-issues/llm-classified.jsonl")
    }

    def merge(keys):
        merged = {}
        for k in keys:
            cats = set(items[k]["categories"]) - {"uncategorised"}
            if k in overlay:
                cats |= set(overlay[k]["categories"])
            merged[k] = cats or {"uncategorised"}
        return merged

    def block(keys) -> dict:
        keys = list(keys)
        chosen = {k: items[k] for k in keys}
        merged = merge(keys)
        open_items = [r for r in chosen.values() if r["state"] == "open"]
        open_ages = sorted(age_days(r["created_at"]) for r in open_items)
        authors = collections.Counter(r["author"] for r in chosen.values())
        bots = {a for a in authors if a and "bot" in a.lower()}
        pr_latency = sorted(
            age_days(r["created_at"]) - age_days(r["closed_at"])
            for r in chosen.values()
            if r["is_pr"] and r["state"] == "closed" and r.get("closed_at")
        )
        issue_latency = sorted(
            age_days(r["created_at"]) - age_days(r["closed_at"])
            for r in chosen.values()
            if not r["is_pr"] and r["state"] == "closed" and r.get("closed_at")
        )
        spread = {}
        for cat in PLATFORM:
            hits = [k for k in keys if cat in merged[k]]
            repos = {canonical_repo(k[0]) for k in hits}
            # Items the title regex missed and the LLM pass put back. The
            # overlay only ever saw the residue of the 303 repos that
            # classified.jsonl reached, so this is a floor, not a total.
            recovered = [k for k in hits if cat not in items[k]["categories"]]
            spread[cat] = {
                "items": len(hits),
                "repos": len(repos),
                "items_per_repo": round(len(hits) / max(len(repos), 1), 1),
                "open": sum(1 for k in hits if items[k]["state"] == "open"),
                "recovered_by_llm": len(recovered),
                "repos_only_via_llm": len(
                    repos - {canonical_repo(k[0]) for k in hits if cat in items[k]["categories"]}
                ),
            }
        return {
            "items": len(keys),
            "repos": len({canonical_repo(k[0]) for k in keys}),
            "prs": sum(1 for r in chosen.values() if r["is_pr"]),
            "issues": sum(1 for r in chosen.values() if not r["is_pr"]),
            "open": len(open_items),
            "open_issues": sum(1 for r in open_items if not r["is_pr"]),
            "open_prs": sum(1 for r in open_items if r["is_pr"]),
            "open_age_median_days": open_ages[len(open_ages) // 2],
            "open_over_1y": sum(1 for a in open_ages if a > 365),
            "open_over_2y": sum(1 for a in open_ages if a > 730),
            "by_year": dict(
                sorted(collections.Counter(r["created_at"][:4] for r in chosen.values()).items())
            ),
            "categories": dict(
                collections.Counter(c for cats in merged.values() for c in cats).most_common()
            ),
            "heuristic_uncategorised": sum(
                1 for r in chosen.values() if r["categories"] == ["uncategorised"]
            ),
            "uncategorised_after_overlay": sum(
                1 for c in merged.values() if c == {"uncategorised"}
            ),
            "cross_cutting": spread,
            "bot_items": sum(authors[a] for a in bots),
            "bot_accounts": len(bots),
            "top_bots": [(a, authors[a]) for a in sorted(bots, key=lambda a: -authors[a])[:8]],
            "distinct_authors": len(authors),
            "unlabelled": sum(1 for r in chosen.values() if not r["labels"]),
            "zero_comment": sum(1 for r in chosen.values() if not (r.get("comments") or 0)),
            "closed_pr_latency_median_days": pr_latency[len(pr_latency) // 2],
            "closed_pr_latency_p90_days": pr_latency[int(0.9 * len(pr_latency))],
            "closed_issue_latency_median_days": issue_latency[len(issue_latency) // 2],
            "closed_issue_latency_p90_days": issue_latency[int(0.9 * len(issue_latency))],
            "top_open_backlogs": collections.Counter(
                canonical_repo(r["repo"]) for r in open_items
            ).most_common(15),
        }

    shipped = {
        (r["repo"], r["number"]) for r in read_jsonl(results / "rq6-issues/classified.jsonl")
    }
    labels = collections.Counter(name for r in items.values() for name in (r["labels"] or []))
    summary = {
        "coverage": {
            "repos_in_corpus_at_snapshot": 529,
            "raw_files": len(list(raw_dir.glob("*.jsonl"))),
            "raw_files_empty": sum(1 for p in raw_dir.glob("*.jsonl") if p.stat().st_size == 0),
            "items_fetched": len(items),
            "items_in_shipped_classified_jsonl": len(shipped),
            "repos_in_shipped_classified_jsonl": len({r for r, _ in shipped}),
            "llm_overlay_items": len(overlay),
        },
        "full_corpus": block(items),
        "charm_only": block(k for k in items if not is_web(k[0])),
        "labels": {
            "distinct": len(labels),
            "top": labels.most_common(20),
            "bug_spellings": sorted(
                (name for name in labels if "bug" in name.lower()), key=lambda name: -labels[name]
            ),
            "doc_spellings": sorted(
                (name for name in labels if "doc" in name.lower()), key=lambda name: -labels[name]
            ),
        },
    }
    write_json(out / "rq6", "rq6-summary.json", summary)

    per_repo = collections.defaultdict(lambda: collections.Counter())
    for (repo, _), rec in items.items():
        row = per_repo[canonical_repo(repo)]
        row["items"] += 1
        row["prs" if rec["is_pr"] else "issues"] += 1
        if rec["state"] == "open":
            row["open"] += 1
        for cat in rec["categories"]:
            row[cat] += 1
    fields = [
        "repo",
        "web_property",
        "items",
        "issues",
        "prs",
        "open",
        "bug",
        "feature",
        "deps",
        "chore",
        "ci",
        "testing",
        "docs",
        "security",
        "uncategorised",
        *PLATFORM,
    ]
    with (out / "rq6" / "rq6-per-repo.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(fields)
        for repo in sorted(per_repo):
            row = per_repo[repo]
            w.writerow([repo, int(is_web(repo))] + [row[c] for c in fields[2:]])
    print(f"wrote {out / 'rq6' / 'rq6-per-repo.csv'} ({len(per_repo)} repos)")
    return summary


def main() -> None:
    """Write every derived artefact under --out."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--results", type=pathlib.Path, default=pathlib.Path.home() / "charm-research/results"
    )
    ap.add_argument(
        "--out", type=pathlib.Path, default=pathlib.Path(__file__).resolve().parent.parent / "data"
    )
    ap.add_argument(
        "--collectors",
        type=pathlib.Path,
        default=pathlib.Path(__file__).resolve().parent.parent / "collectors",
    )
    args = ap.parse_args()

    churn(args.results, args.out)
    static(args.results, args.out)
    rq6(args.results, args.collectors, args.out)


if __name__ == "__main__":
    main()
