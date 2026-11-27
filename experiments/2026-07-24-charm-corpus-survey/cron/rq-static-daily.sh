#!/usr/bin/env bash
# Daily static research passes over the local charm corpus (no gh API, fast).
#
# Step 2 refreshes the clones. Without it the passes only re-derive whatever is
# already on disk: the corpus sat frozen at 2026-07-10 while this job ran for 24
# consecutive nights, producing byte-identical rows every time.
set -u

RESEARCH="$HOME/charm-research"
# The live checkout. Note $HOME/multipass-mounts/hyrum is a SEPARATE, stale tree
# (stuck at 2026-07-04); using it silently pulls an old charm list and an older
# get-charms whose CLI rejects --workers. Fail loudly rather than fall back to it.
HYRUM="${HYRUM_DIR:-/w/hyrum}"
CORPUS="${HYRUM_CHARMS:-$HOME/.cache/hyrum/charms}"
RESULTS="$RESEARCH/results"
UV=/snap/bin/uv
GIT=/usr/bin/git
PY=/usr/bin/python3
TODAY="$($PY -c 'import datetime;print(datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d"))')"

WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

# --- 1. drop hyrum patcher leftovers -------------------------------------
# hyrum's ops patcher rewrites dependency files in place and does not always
# revert them. Those are the exact files RQ-2 reads, so leftovers get recorded
# as if they were the charm's own declaration (canonical/charm-ubuntu was logged
# as ops==3.7.1 / exact-pins for 25 days; upstream declares ops>=1.0,<2.0). They
# also block `git pull`. Restore only dependency files, and only when no hyrum
# run is in flight, so we never fight a live patch.
if pgrep -f 'hyrum|run_pilot' >/dev/null 2>&1; then
  echo "rq-static: hyrum run in flight, skipping worktree cleanup"
else
  while IFS= read -r repo; do
    dirty=$("$GIT" -C "$repo" diff --name-only -- \
      'pyproject.toml' 'uv.lock' 'poetry.lock' 'pylock.toml' \
      'requirements*.txt' 'setup.py' 2>/dev/null)
    [ -n "$dirty" ] || continue
    # shellcheck disable=SC2086
    "$GIT" -C "$repo" checkout -- $dirty 2>/dev/null \
      && echo "rq-static: reverted patcher leftovers in ${repo#"$CORPUS"/}: $(echo $dirty | tr '\n' ' ')"
  done < <(find "$CORPUS" -mindepth 3 -maxdepth 3 -name .git -printf '%h\n' 2>/dev/null)
fi

# --- 2. refresh the corpus ------------------------------------------------
# Probe each distinct host once and drop rows for hosts that do not answer.
# git.launchpad.net has been unreachable from this machine since at least
# 2026-08-17; each dead connection hangs ~270s and, because get-charms shares one
# worker pool across all rows, 119 launchpad rows starve the ~520 reachable ones
# (10 minutes in, only a third of the GitHub repos had even started). Probing
# rather than hardcoding an exclusion means those rows come back automatically if
# the host does. Everything reachable refreshes in ~90s.
if [ -f "$HYRUM/charm-list/charms.csv" ]; then
  "$PY" - "$HYRUM/charm-list/charms.csv" "$WORK/charms-reachable.csv" <<'PYEOF'
import csv, subprocess, sys, urllib.parse
src, dest = sys.argv[1], sys.argv[2]
rows = list(csv.DictReader(open(src)))
hosts = {urllib.parse.urlparse(r["Repository"]).netloc
         for r in rows if r.get("Repository")}
ok = set()
for h in sorted(h for h in hosts if h):
    probe = subprocess.run(["curl", "-sSI", "--max-time", "10", f"https://{h}/"],
                           capture_output=True)
    if probe.returncode == 0:
        ok.add(h)
    else:
        print(f"rq-static: host unreachable, skipping its rows: {h}", file=sys.stderr)
keep = [r for r in rows
        if urllib.parse.urlparse(r.get("Repository") or "").netloc in ok]
with open(dest, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=rows[0].keys())
    w.writeheader()
    w.writerows(keep)
print(f"rq-static: refreshing {len(keep)}/{len(rows)} repos "
      f"({len(rows) - len(keep)} on unreachable hosts)", file=sys.stderr)
PYEOF
  if [ -s "$WORK/charms-reachable.csv" ]; then
    # `uv run` rebuilds the project whenever the hyrum source tree has changed,
    # and an invocation that races that rebuild sees a half-installed entry
    # point (observed as a bogus "unrecognized arguments: --workers"). Sync
    # first so the rebuild is done, then retry once for network flakiness.
    (cd "$HYRUM" && /usr/bin/timeout 300 "$UV" sync --quiet) \
      || echo "rq-static: uv sync failed, trying get-charms anyway"
    for attempt in 1 2; do
      if (cd "$HYRUM" && /usr/bin/timeout 900 "$UV" run hyrum get-charms \
          --source "$WORK/charms-reachable.csv" --dest "$CORPUS" --workers 24); then
        break
      fi
      echo "rq-static: get-charms attempt $attempt failed"
      [ "$attempt" = 2 ] && echo "FAILED: get-charms (continuing with corpus as-is)"
      sleep 10
    done
  fi
else
  echo "FAILED: no charm list at $HYRUM/charm-list/charms.csv (skipping refresh)"
fi

# --- 3. static passes -----------------------------------------------------
# Each script stamps rows with the UTC date and blindly appends, so a second run
# landing on the same UTC date duplicates that day (this is what made 2026-07-23
# five times too wide). The 05:00 NZ schedule sits at 17:00 UTC the day before,
# so a manual run and the next cron fire collide easily. Skip any pass already
# recorded for today; delete the day's rows first if you want a genuine redo.
cd "$RESEARCH" || exit 1
declare -A OUTPUT=(
  [rq2_supply_chain]="$RESULTS/rq2-supply-chain/posture.jsonl"
  [rq9_config_actions]="$RESULTS/rq9-config-actions/surface.jsonl"
  [rq11_substrate]="$RESULTS/rq11-substrate/substrate.jsonl"
  [rq7_docs_audit]="$RESULTS/rq7-docs/docs-audit.jsonl"
)
for s in rq2_supply_chain rq9_config_actions rq11_substrate rq7_docs_audit; do
  out="${OUTPUT[$s]}"
  if [ -f "$out" ] && LC_ALL=C grep -qF "\"date\":\"$TODAY\"" "$out"; then
    echo "rq-static: $s already has rows for $TODAY, skipping"
    continue
  fi
  /usr/bin/timeout 600 "$PY" "$s.py" || echo "FAILED: $s"
done
