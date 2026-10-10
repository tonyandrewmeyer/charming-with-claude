#!/bin/bash
# Shared config + helpers for the charm review harness.

export ROOT=/home/ubuntu/charm-review
export PATH="/home/ubuntu/.local/share/pi-node/node-v22.23.1-linux-x64/bin:/snap/bin:/usr/local/bin:/usr/bin:/bin:/home/ubuntu/.local/bin"

# --- transport ----------------------------------------------------------
# 2026-08-30: the whole programme stopped for 2.5 days and every turn died in ~16s with
# `Request timed out.` in agent.log, while curl against the same endpoint returned 200 and
# billed normally. The provider was fine; node could not open the socket.
#
# pi runs on node 22, whose Happy Eyeballs implementation gives each address it tries only
# `autoSelectFamilyAttemptTimeout` ms to complete the TCP handshake, default **250**.
# Connect latency from this box to openrouter.ai had drifted to 287-383ms — measured with
# `curl -w %{time_connect}`, five samples, all of them over the line — so node aborted every
# attempt and reported `connect ETIMEDOUT`, which the openai SDK surfaces as a timeout after
# its retries. Nothing in the rig or the account had changed; the network path to Cloudflare
# got slower and crossed a threshold nobody knew was there.
#
# openrouter.ai also publishes AAAA records only (`getent hosts`) and this host has no IPv6
# route, so the v6 attempts fail ENETUNREACH and the v4 attempts are all that is left — the
# 250ms budget is the entire connection story here, with no second chance behind it.
#
# 2000ms leaves ~5x headroom over the worst sample. Verified by running the real thing: pi
# against WORK_MODEL answers in 3.1s with the variable set and times out at 16.6s without it.
# NODE_OPTIONS is used rather than a wrapper because pi is invoked from several places here
# (run-review.sh, themes.sh) and the flag has to reach every one of them.
export NODE_OPTIONS="${NODE_OPTIONS:+$NODE_OPTIONS }--network-family-autoselection-attempt-timeout=2000"

# --- models -------------------------------------------------------------
# WORK_MODEL does the deploy/explore/analyse loop; POLISH_MODEL writes the
# final report from the working notes. Set by bin/models.env (benchmark output).
[ -f "$ROOT/bin/models.env" ] && . "$ROOT/bin/models.env"
: "${WORK_MODEL:=z-ai/glm-4.7}"
: "${POLISH_MODEL:=anthropic/claude-sonnet-5}"

# --- cadence -------------------------------------------------------------
# Hours between cron slots. MUST match the crontab (`0 */N * * *`) — the per-slot
# budget maths counts the remaining slots in the UTC day using this figure, so the
# two drifting apart silently mis-sizes every cap.
: "${SLOT_HOURS:=4}"
: "${RUNS_PER_DAY:=$((24 / SLOT_HOURS))}"

# --- budget -------------------------------------------------------------
: "${MIN_RUN_BUDGET:=1.50}"   # skip the run if less than this is left today
: "${MAX_RUN_BUDGET:=5.50}"
: "${POLISH_BUDGET:=0.60}"
# Held back from the cap for the citation-correction passes; see run-review.sh. Raised
# from $0.35 on 2026-07-28 because it was not covering even one pass, let alone two:
# reviews had grown (32K -> 38K, $3.17 -> $4.51 mean) until the depth loop ate the whole
# cap, and 3 of the previous 12 runs skipped a correction pass on "already at its cap".
# Residual bad citations had gone from ~1 per review to 5-8 (postgresql 8 of 25, blackbox
# 6 of 28, alertmanager 17 of 51). MAX_RUN_BUDGET went $5.00 -> $5.50 at the same time so
# the reserve comes out of new headroom rather than out of depth: the work cap stays at
# ~$4.50. Worst case is 6 x $5.50 = $33 of the $35/day key limit, against $26-28/day
# observed, and the per-slot `min(MAX, REMAIN/SLOTS_LEFT)` squeezes the late slots rather
# than overrunning if a day does run hot.
: "${CITE_RESERVE:=1.00}"
# 3h cap on the agent phase, and the agent is *told* this figure in its brief, so it
# paces itself against it. Depth passes keep starting until 60% of it is used, the last
# one can overrun to ~170min, and citations + polish add up to ~45min worst case — so a
# slot stays inside the 4h cron gap with roughly 25min to spare.
# Every run so far stopped on these ceilings rather than because the agent had run out
# of work, which is why they were raised from 2h/55%/3-passes on 2026-07-25.
: "${RUN_TIMEOUT:=10800}"
: "${DEPTH_PCT:=60}"
: "${DEPTH_PASSES:=4}"
: "${POLISH_TIMEOUT:=900}"

# --- turn liveness -------------------------------------------------------
# The spend watchdog cannot see a turn that has stopped working. A pi turn blocked on a
# provider call that never returns spends nothing, so the cap is never approached and
# only the wall-clock timeout stops it — at the full length of the turn.
# hook-service-operator's deepen-2 (2026-08-04) burned **1 second of CPU in 2h08** with a
# 0-byte log and no write to the review or the notes, then died on its 7816s timeout
# having contributed nothing, taking the rest of the slot's depth with it. Progress is
# checkable, so check it.
# 2026-08-17: raised 1800 -> 3600. Deploy-and-wait phases are legitimately long — the
# kfp-operators first pass went 34.7min between notes writes and finished rc=0 — and now
# that spend carries the liveness signal (see below), a false positive needs the turn to
# make no API call at all for an hour. A genuinely wedged turn still dies well inside its
# 3h wall-clock timeout, so the cost of being generous here is bounded and small.
: "${LIVENESS_STALL:=3600}"    # no progress for this long -> stop the turn
: "${LIVENESS_MIN_CPU:=5}"     # CPU seconds in a window that count as "still working"

# A turn's progress signature: bytes written to its log, and CPU seconds burned by the
# turn and every process descended from it. Echoes "<bytes> <cpu> <marks>".
#
# This summed over the process *group* until 2026-08-17, on the assumption that "pi shells
# out to juju and kubectl, so the group is the unit of work". That assumption is false for
# pi 0.81.1: it starts each shell tool-call in a **new process group**, so the group sum
# saw only `timeout` and `pi` itself and was structurally blind to every juju, kubectl and
# tox the agent ran. Caught live on the kfp-operators run, where the group read 1s of CPU
# while `/bin/bash -c sleep 90 && juju status -m rv-kfp-ops-3` (pgid 1833653, its own
# group) was doing the work. Walk the ppid tree instead: children stay descendants even
# when they leave the group. Twelve of the fourteen slots before this were killed by that
# blindness, three charms permanently.
#
# All components are needed. A turn can legitimately go many minutes without logging
# while it waits on a deploy, so log growth alone would kill working turns; and a wedged
# client can tick the odd CPU second, so CPU alone can be fooled. If ps cannot report
# (no cputimes), cpu reads 0 and the log becomes the only signal — that fails towards
# *not* killing, which is the right way for this to be wrong.
turn_activity() {  # turn_activity <root-pid> [logfile]
  local pgid="$1" logf="${2:-}" bytes=0 cpu marks
  if [ -n "$logf" ] && [ -f "$logf" ]; then
    bytes=$(wc -c <"$logf" 2>/dev/null || echo 0)
  fi
  cpu=$(ps -eo pid=,ppid=,cputimes= 2>/dev/null | python3 -c "
import sys, collections
kids = collections.defaultdict(list); cpu = {}
for line in sys.stdin:
    f = line.split()
    if len(f) < 3: continue
    try: p, pp, c = int(f[0]), int(f[1]), int(f[2])
    except ValueError: continue
    kids[pp].append(p); cpu[p] = c
seen = set(); stack = [$pgid]; tot = 0
while stack:
    p = stack.pop()
    if p in seen: continue
    seen.add(p); tot += cpu.get(p, 0); stack += kids.get(p, [])
print(tot)
" 2>/dev/null || echo 0)
  # The artifacts the turn exists to produce. Log growth is a weaker signal than it
  # looks: 53 of the 247 pass logs across the first 57 runs are 0 bytes (21%), on runs
  # that finished perfectly well — writing nothing to stdout for half an hour is normal
  # pi behaviour. These two files are where a working turn actually shows itself, so
  # they carry the signal that log bytes do not.
  marks=$(stat -c %Y "${REVIEW_FILE:-/nonexistent}" "${NOTES_FILE:-/nonexistent}" \
          2>/dev/null | tr '\n' ',')
  echo "$bytes ${cpu:-0} ${marks:-none}"
}

# --- what counts as a review --------------------------------------------
# A file is not a review. kafka-benchmark-operator (2026-07-30) hit the 3h timeout with
# an empty agent log, left a 3.6K file with zero findings, and was still recorded rc=0:
# the trap reports the exit status at trap time, not the agent's, and the file cleared
# the old 2000-byte "already reviewed" bar, so the cursor moved past it and nothing ever
# went back. Judge the artifact instead of the exit code. The smallest review that has
# ever been worth keeping is 19.6K (self-signed-certificates, 9 findings), so 8K is a
# floor with a lot of daylight under it rather than a target to tune.
# A genuinely spotless charm would trip MIN_FINDINGS and be re-reviewed once before the
# harness gives up on it. None of the first 36 was; one wasted slot is the cheaper error.
: "${MIN_REVIEW_BYTES:=8000}"
: "${MIN_FINDINGS:=1}"

# Findings = "### " headings inside the "## Findings" section, and nowhere else. Counting
# every "### " sweeps up the per-deployment subsections of the deployment log and reports
# 38 findings for a review that has 12. bin/index.sh counts by the same rule.
review_findings() {  # review_findings <review.md>
  python3 - "$1" <<'PY' 2>/dev/null || echo 0
import re, sys, pathlib
p = pathlib.Path(sys.argv[1])
if not p.exists():
    print(0); raise SystemExit
m = re.search(r"^## Findings\s*$(.*?)(?=^## |\Z)", p.read_text(errors="replace"), re.M | re.S)
print(len(re.findall(r"^### ", m.group(1), re.M)) if m else 0)
PY
}

# Used in two places that must agree: whether to retry a run, and whether the queue may
# skip past a charm. If they disagree, a rewound cursor just skips the charm again.
review_is_good() {  # review_is_good <review.md>
  local f="$1"
  [ -s "$f" ] || return 1
  [ "$(wc -c <"$f")" -ge "${MIN_REVIEW_BYTES:-8000}" ] || return 1
  [ "$(review_findings "$f")" -ge "${MIN_FINDINGS:-1}" ] || return 1
}

OR_KEY=$(python3 -c "import json;print(json.load(open('/home/ubuntu/.pi/agent/auth.json'))['openrouter']['key'])" 2>/dev/null)
export OR_KEY

# usage_today -> dollars spent against today's cap
usage_today() {
  curl -sS --max-time 20 -H "Authorization: Bearer $OR_KEY" \
    https://openrouter.ai/api/v1/key 2>/dev/null |
    python3 -c "import json,sys;d=json.load(sys.stdin)['data'];print(f\"{d.get('usage_daily') or 0:.4f}\")" 2>/dev/null || echo ""
}

daily_limit() {
  curl -sS --max-time 20 -H "Authorization: Bearer $OR_KEY" \
    https://openrouter.ai/api/v1/key 2>/dev/null |
    python3 -c "import json,sys;d=json.load(sys.stdin)['data'];print(d.get('limit') or 0)" 2>/dev/null || echo 0
}

# What is actually left to spend, in dollars.
#
# Do NOT go back to computing this as `limit - usage_daily`. That was correct for the $35/day
# key the rig grew up on, where the limit reset with the day, and it is wrong for a key whose
# limit does not reset: `usage_daily` returns to 0 at 00:00 UTC while the pot does not refill,
# so a spent-down key reads as full every morning and the rig only learns the truth by being
# refused mid-run. Hit on 2026-08-26, when a colleague's key ($150 total, `limit_reset: null`)
# replaced the daily one for the last week of the month and the run log cheerfully printed
# `remaining=$150.00` on a key that had already spent some of it.
#
# `limit_remaining` is the provider's own answer and is right for both shapes of key, so ask
# for that and keep the old arithmetic only as the fallback for a key that reports no
# limit_remaining at all. A key with no limit is unlimited, not broke — hence the big number
# rather than 0, which would skip every slot for ever.
#
# This is NOT a substitute for provider_budget_block below: it is the *key's* counter and
# still cannot see the org-member budget. It stops the rig walking into a wall it can see;
# the 403 path is what catches the wall it cannot.
budget_remaining() {
  curl -sS --max-time 20 -H "Authorization: Bearer $OR_KEY" \
    https://openrouter.ai/api/v1/key 2>/dev/null |
    python3 -c "
import json,sys
d=json.load(sys.stdin)['data']
r=d.get('limit_remaining')
if r is None:
    lim=d.get('limit')
    r=1e9 if lim is None else max(0.0, lim-(d.get('usage_daily') or 0))
print(f'{r:.4f}')" 2>/dev/null || echo ""
}

# Did this turn die because the *account* is out of money, rather than because the charm
# or the harness went wrong?
#
# This is not the same failure as the daily cap, and not the same as openrouter being
# unreachable, and the rig was blind to it until 2026-08-26 — when the $500/month org
# member budget ran out and three slots died in under a second each with
#   403: {"message":"Org member budget limit exceeded (monthly limit)...","code":403}
# An empty review with a non-zero rc looks exactly like a bad charm, so retry_or_give_up
# spent one retry and then abandoned the charm for good: idx 134 was permanently lost and
# 135 was one slot from the same fate, with nothing in deferred.tsv to show for it.
#
# It cannot be pre-empted by asking the API. /api/v1/key answered 200 throughout, with
# limit_remaining $28.94 and usage_monthly $36.86 — that key's own counters know nothing
# about the org budget enforced above it. Same trap as the pgid CPU sum and as
# last-connection: the guard was reading a field the failing path never writes. So the
# only honest signal is what the provider actually said when a real request was billed,
# which means classifying the turn's log after the fact.
#
# Matches on message text, never on a bare status code: a 403 is also what moderation
# returns, and that IS the charm's problem. Erring towards matching is safe here — a false
# positive skips a slot without consuming it, a false negative loses a charm.
#
# Only logs written by the CURRENT run are eligible, which is what BUDGET_LOG_SINCE is for
# (an epoch, set by run-review.sh once it knows the repo; unset means no filtering, which is
# only right for a caller passing files it just wrote itself).
#
# 2026-08-30: without that filter this classifier froze the whole programme for 2.5 days.
# `logs/<repo>/` is per-repo and never cleared, so a *re-run* of a charm greps the leftovers
# of its previous run. landscape-server-operator's 08-25 run had hit the genuine org-budget
# wall on its depth passes, leaving three 104-byte `403 ... budget limit exceeded` logs
# behind; the review itself passed the floor, so the charm was accepted and later requeued
# for quality. From 08-28 every retry of it re-read those five-day-old files, called
# budget_abort, and exited the slot — and because a deferred charm is picked at the *top* of
# every slot, the main queue behind it never ran at all. The account was solvent throughout.
# So: match on message text, and only on text this run actually produced. A stale hit is not
# a cheap false positive like a live one — it never clears, because nothing rewrites the file
# it is reading.
provider_budget_block() {  # provider_budget_block <logfile>... -> prints the line, rc 0 if blocked
  local f hit mtime
  for f in "$@"; do
    [ -s "$f" ] || continue
    if [ -n "${BUDGET_LOG_SINCE:-}" ]; then
      mtime=$(stat -c %Y "$f" 2>/dev/null) || continue
      [ "$mtime" -ge "$BUDGET_LOG_SINCE" ] || continue
    fi
    hit=$(grep -aiEm1 'budget limit exceeded|key limit exceeded|insufficient credits|(requires|require) more credits|negative credit balance|out of credits' "$f") || continue
    echo "${hit:0:200}"
    return 0
  done
  return 1
}

log() { echo "[$(date -Is)] $*" | tee -a "$ROOT/state/runs.log" >&2; }

# juju controllers available on this box, by (juju major, substrate)
export CTL_K8S4=concierge-k8s-4
export CTL_K8S3=concierge-k8s-3
export CTL_LXD3=concierge-lxd
export CTL_LXD4=concierge-lxd-4

# --- substrate readiness -------------------------------------------------
# How long run-review.sh waits for a substrate to come up before skipping the slot,
# and how often it re-probes while waiting. Sized for a host reboot: minutes against
# a 4h slot. See the substrate guard in run-review.sh for why skipping is the chosen
# failure mode.
: "${SUBSTRATE_WAIT_MAX:=900}"
: "${SUBSTRATE_PROBE_INTERVAL:=60}"
: "${SUBSTRATE_PROBE_TIMEOUT:=60}"

# The controllers a charm of this kind can actually be deployed to. Either juju version
# will do — the run wants both so it can compare them, but one is enough to review on.
controllers_for_kind() {  # controllers_for_kind <kind>
  case "$1" in
    k8s) echo "$CTL_K8S4 $CTL_K8S3" ;;
    *)   echo "$CTL_LXD4 $CTL_LXD3" ;;
  esac
}

# One API call per controller covers both layers: the k8s controllers are pods and the
# LXD ones are containers, so a controller that answers proves the substrate under it is
# up. Probing kubectl/lxc as well would only add ways to get a false negative, and a
# false negative here costs a whole slot.
# `juju status` against a controller that is missing or unreachable exits non-zero
# (rc=2, confirmed 2026-08-04) rather than hanging, but it is wrapped in a timeout
# anyway — a half-booted API server is exactly the case where it might not return.
controller_ready() {  # controller_ready <controller>
  timeout "${SUBSTRATE_PROBE_TIMEOUT:-60}" juju status -m "$1:controller" \
    --format json >/dev/null 2>&1
}

# Echoes the subset of the given controllers that answered, in the order given.
ready_controllers() {  # ready_controllers <controller>...
  local c out=""
  for c in "$@"; do
    controller_ready "$c" && out="${out:+$out }$c"
  done
  echo "$out"
}
