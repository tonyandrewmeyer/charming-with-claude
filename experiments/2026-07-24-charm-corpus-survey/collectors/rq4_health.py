"""RQ-4: maintenance-health time series.

Daily: walks the repo universe round-robin (~100 repos/run), fetching per-repo
signals via gh REST + one GraphQL batch (issues by age bucket, PR counts/ages,
CI rollup). One JSONL record per repo per day — the longitudinal series.
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "lib"))
from corpus import RESULTS, append_jsonl, gh_api, iter_repos, load_state, rate_limits, save_state

OUT = RESULTS / "rq4-health"
STATE = OUT / "state.json"
TODAY = datetime.now(timezone.utc).strftime("%Y-%m-%d")
BATCH = 60
MIN_REMAINING = 250

GQL = """
query($owner:String!, $name:String!) {
  repository(owner:$owner, name:$name) {
    isArchived
    issues_open: issues(states:OPEN) { totalCount }
    issues_old: issues(states:OPEN, filterBy:{since:"SINCE_OLD"}) { totalCount }
    issues_mid: issues(states:OPEN, filterBy:{since:"SINCE_MID"}) { totalCount }
    prs: pullRequests(states:OPEN) { totalCount }
    defaultBranchRef {
      target {
        ... on Commit {
          committedDate
          history(first:1) { totalCount }
        }
      }
    }
  }
}
"""


def graphql_batch(repos: list[tuple[str, str]], chunk: int = 20) -> dict:
    """GraphQL in chunks of `chunk` repos per call (large aliased queries 502)."""
    since_old = _days_ago(180)
    since_mid = _days_ago(90)
    result = {}
    import subprocess
    for off in range(0, len(repos), chunk):
        part = repos[off:off + chunk]
        q = "query {\n"
        for i, (owner, name) in enumerate(part):
            q += (f'  r{i}: repository(owner:"{_esc(owner)}", name:"{_esc(name)}") {{\n'
                  f'    isArchived\n'
                  f'    issuesOpen: issues(states:OPEN) {{ totalCount }}\n'
                  f'    issuesOld: issues(states:OPEN, filterBy:{{since:"{since_old}"}}) {{ totalCount }}\n'
                  f'    issuesMid: issues(states:OPEN, filterBy:{{since:"{since_mid}"}}) {{ totalCount }}\n'
                  f'    prsOpen: pullRequests(states:OPEN) {{ totalCount }}\n'
                  f'    defaultBranchRef {{ target {{ ... on Commit {{ committedDate }} }} }}\n'
                  f'  }}\n')
        q += "}"
        out = subprocess.run(["gh", "api", "graphql", "-f", f"query={q}"],
                             capture_output=True, text=True, timeout=120)
        if out.returncode != 0:
            print(f"rq4: graphql chunk @{off} failed: {out.stderr[:200]}", file=sys.stderr)
            continue
        try:
            data = json.loads(out.stdout).get("data", {})
        except Exception:
            continue
        for i, (owner, name) in enumerate(part):
            r = data.get(f"r{i}")
            if r:
                result[f"{owner}/{name}"] = r
    return result


def _days_ago(n: int) -> str:
    from datetime import timedelta
    return (datetime.now(timezone.utc) - timedelta(days=n)).strftime("%Y-%m-%dT%H:%M:%SZ")


def _esc(s: str) -> str:
    return s.replace('"', '\\"')


def repo_signals(owner: str, name: str) -> dict:
    """Cheap REST signals (2 calls) + CI rollup folded in."""
    repo = gh_api(f"repos/{owner}/{name}") or {}
    contributors = gh_api(f"repos/{owner}/{name}/contributors?per_page=100&anon=true")
    # count of contributors in the returned page; 100 means "100 or more"
    # (good enough for bus-factor: we care about 1 vs 2 vs few vs many)
    n_contrib = len(contributors) if isinstance(contributors, list) else None
    ci = None
    branch = (repo.get("default_branch") or "main")
    runs = gh_api(f"repos/{owner}/{name}/actions/runs?per_page=1&branch={branch}")
    if isinstance(runs, dict) and runs.get("workflow_runs"):
        ci = runs["workflow_runs"][0].get("conclusion") or runs["workflow_runs"][0].get("status")
    return {"pushed_at": repo.get("pushed_at"),
            "archived": repo.get("archived"),
            "stars": repo.get("stargazers_count"),
            "contributors_sample": n_contrib,
            "ci_default": ci}


def main() -> None:
    universe = [f"{o}/{n}" for o, n, _ in iter_repos()]
    state = load_state(STATE, {"cursor": 0, "sweep": 0})
    rl = rate_limits()
    if rl.get("core", 0) < MIN_REMAINING or rl.get("graphql", 0) < MIN_REMAINING:
        print(f"rq4: rate limit low ({rl}); skipping run")
        return

    start = state["cursor"] % len(universe)
    batch = [universe[(start + i) % len(universe)] for i in range(min(BATCH, len(universe)))]
    state["cursor"] = (start + len(batch)) % len(universe)
    if state["cursor"] <= start:
        state["sweep"] = state.get("sweep", 0) + 1

    gql = graphql_batch([tuple(r.split("/", 1)) for r in batch])
    ok = 0
    for full in batch:
        owner, name = full.split("/", 1)
        sig = repo_signals(owner, name)
        g = gql.get(full, {})
        branch = g.get("defaultBranchRef") or {}
        target = (branch.get("target") or {}) if isinstance(branch, dict) else {}
        rec = {"date": TODAY, "repo": full, **sig,
               "issues_open": (g.get("issuesOpen") or {}).get("totalCount"),
               "issues_90d": (g.get("issuesMid") or {}).get("totalCount"),
               "issues_180d": (g.get("issuesOld") or {}).get("totalCount"),
               "prs_open": (g.get("prsOpen") or {}).get("totalCount"),
               "last_commit": target.get("committedDate")}
        if rec["pushed_at"] is None and rec["last_commit"] is None:
            continue  # repo lookup failed (private/deleted); don't record junk
        append_jsonl(OUT / "health.jsonl", rec)
        ok += 1
    save_state(STATE, state)
    print(f"rq4: sweep {state.get('sweep',0)} cursor {state['cursor']}/{len(universe)}; "
          f"recorded {ok}/{len(batch)} repos; rate {rate_limits()}")


if __name__ == "__main__":
    main()
