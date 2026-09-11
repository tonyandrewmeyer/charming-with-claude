#!/bin/bash
# Cron entrypoint. Reviews exactly one charm, then cleans up after itself.
#   run-review.sh            -> next charm in the queue
#   run-review.sh <repo>     -> that specific repo (does not move the cursor)
. /home/ubuntu/charm-review/bin/lib.sh
set -u

exec 9>"$ROOT/state/lock"
# A run that wedges while holding this lock stops the programme outright: every later slot
# lands here, logs the same line and skips, for ever. Nothing else bounds a run's
# wall-clock — the agent is capped by RUN_TIMEOUT and the liveness watchdog, but finish()
# shells out to lxc and juju with no timeout, and a wedged LXD hangs there still holding
# the lock. That is the 2026-08-05 disk stall's failure mode with no recovery path at all:
# the disk at least came back once space was freed from outside, whereas a held lock would
# simply skip until someone logged in. So treat a lock held far longer than any real run as
# a wedge and break it. Real runs take 1.5-5h against a 4h slot, so the threshold has hours
# of daylight under it; a run that legitimately overruns its slot is still just skipped.
if ! flock -n 9; then
  HELD=0
  LOCK_STAMP="$ROOT/state/lock.acquired"
  [ -f "$LOCK_STAMP" ] && HELD=$(( $(date +%s) - $(cat "$LOCK_STAMP" 2>/dev/null || echo 0) ))
  if [ "$HELD" -gt "${STALE_LOCK_SECS:-28800}" ]; then
    log "run: lock held for $((HELD/3600))h — treating the holder as wedged and breaking it"
    # `exec 9>` above already opened this file, so fuser reports *this* process as a holder
    # too. Signalling that would kill the run trying to take over, and a process-group kill
    # would take cron's shell with it — which is exactly what happened the first time this
    # was written. Skip ourselves, and signal PIDs individually rather than process groups.
    for pid in $(fuser "$ROOT/state/lock" 2>/dev/null); do
      [ "$pid" = "$$" ] && continue
      kill -TERM "$pid" 2>/dev/null
    done
    sleep 30
    for pid in $(fuser "$ROOT/state/lock" 2>/dev/null); do
      [ "$pid" = "$$" ] && continue
      kill -KILL "$pid" 2>/dev/null
    done
    # The agent outlives its parent if the parent is killed — observed 2026-08-09 — so reap
    # it by name too, or it keeps its memory and its spend.
    pkill -f "pi -p --no-session" 2>/dev/null
    sleep 5
    if ! flock -n 9; then
      log "run: could not break the stale lock — skipping this slot"
      exit 0
    fi
    log "run: broke the stale lock, continuing"
  else
    log "run: another review is still going (${HELD}s), skipping this slot"
    exit 0
  fi
fi
date +%s > "$ROOT/state/lock.acquired"

QUEUE="$ROOT/queue.tsv"
FORCE_REPO="${1:-}"
DEFERRED="$ROOT/state/deferred.tsv"
# Kinds whose substrate has already failed its probe in *this* slot. Exported across the
# `exec "$0"` below so the fast-forward past the rest of that kind costs one probe per
# kind per slot rather than a fresh 15-minute wait per charm.
DEAD_KINDS="${DEAD_KINDS:-}"
FROM_DEFERRED=0

# ---- pick the charm ----------------------------------------------------
LINE=""
if [ -n "$FORCE_REPO" ]; then
  LINE=$(awk -F'\t' -v r="$FORCE_REPO" 'NR>1 && $2==r' "$QUEUE" | head -1)
  [ -z "$LINE" ] && { log "run: '$FORCE_REPO' is not in the queue"; exit 1; }
else
  # A charm set aside by a dead substrate gets one attempt at the top of every slot,
  # because the substrate it needs may have come back. This is the only thing that takes a
  # charm off the deferred list, so it has to run before the cursor pick — and only once
  # per slot, which is what the empty DEAD_KINDS means. Re-deferred charms are appended to
  # the end of the file, so taking the first line round-robins over them.
  if [ -z "$DEAD_KINDS" ] && [ -s "$DEFERRED" ]; then
    DIDX=$(awk -F'\t' 'NR==1{print $1}' "$DEFERRED")
    LINE=$(awk -F'\t' -v i="${DIDX:-}" 'NR>1 && $1==i' "$QUEUE")
    if [ -n "$LINE" ]; then
      FROM_DEFERRED=1
      log "run: retrying deferred idx=$DIDX ($(wc -l <"$DEFERRED") charm(s) deferred)"
    else
      # No such queue line any more — drop the stale entry rather than retry it for ever.
      awk -F'\t' -v i="${DIDX:-}" '$1!=i' "$DEFERRED" > "$DEFERRED.tmp" && mv "$DEFERRED.tmp" "$DEFERRED"
    fi
  fi
  if [ -z "$LINE" ]; then
    IDX=$(cat "$ROOT/state/cursor" 2>/dev/null || echo 1)
    LINE=$(awk -F'\t' -v i="$IDX" 'NR>1 && $1==i' "$QUEUE")
    if [ -z "$LINE" ]; then
      if [ -s "$DEFERRED" ]; then
        # Not "nothing left to do": the deferred retry above still runs every slot, so the
        # tail comes back on its own if its substrate ever does.
        log "run: queue finished at index $IDX, but $(wc -l <"$DEFERRED") charm(s) are deferred waiting on a substrate — still retrying one per slot"
      else
        log "run: queue finished at index $IDX — nothing left to do"
      fi
      exit 0
    fi
  fi
fi

IFS=$'\t' read -r IDX REPO ORG KIND NAMES DIRS SRC LASTC LINES SCORE <<< "$LINE"
REVIEW_FILE="$ROOT/reviews/$REPO.md"

# Write (or refresh) this charm's row on the deferred list. Split out from defer_charm
# because retry_or_give_up needs the record without the cursor move and the exec.
defer_record() {  # defer_record <reason>
  local now first
  now=$(date +%s)
  first=$(awk -F'\t' -v i="$IDX" '$1==i{print $4; exit}' "$DEFERRED" 2>/dev/null)
  [ -z "$first" ] && first="$now"
  if [ -s "$DEFERRED" ]; then
    awk -F'\t' -v i="$IDX" '$1!=i' "$DEFERRED" > "$DEFERRED.tmp" && mv "$DEFERRED.tmp" "$DEFERRED"
  fi
  printf '%s\t%s\t%s\t%s\t%s\t%s\n' "$IDX" "$REPO" "$KIND" "$first" "$now" "$1" >> "$DEFERRED"
}
defer_undo() {
  [ -s "$DEFERRED" ] || return 0
  awk -F'\t' -v i="$IDX" '$1!=i' "$DEFERRED" > "$DEFERRED.tmp" && mv "$DEFERRED.tmp" "$DEFERRED"
}

# Set this charm aside and carry on with the rest of the queue in the same slot.
#
# Skipping the slot outright — what the substrate guard below used to do — keeps the queue
# intact, but it also pins the cursor on the unrunnable charm, so *nothing* runs until a
# human fixes the substrate. That is not a theoretical cost: the LXD controllers went
# missing during the 2026-08-05 disk event and were not noticed until idx 75 (cos-proxy)
# became the first machine charm since, on 08-11. Five consecutive slots then skipped on a
# queue that still held 39 perfectly runnable k8s charms. The guard behaved exactly as
# designed and the programme still stopped dead, which is the same lesson the disk stall
# taught: a guard that only halts is not enough.
#
# So the charm moves to the deferred list instead of the cursor stopping on it. Nothing is
# lost — a deferred charm is retried at the top of every later slot — and the queue keeps
# moving for the kinds whose substrate is fine.
defer_charm() {  # defer_charm <reason>
  if [ -n "$FORCE_REPO" ]; then
    log "run: $REPO cannot run — $1"
    exit 1
  fi
  defer_record "$1"
  # Only the cursor pick owns the cursor; a deferred retry must not move it.
  [ "$FROM_DEFERRED" = 0 ] && echo $((IDX+1)) > "$ROOT/state/cursor"
  case " $DEAD_KINDS " in
    *" $KIND "*) ;;
    *) DEAD_KINDS="${DEAD_KINDS:+$DEAD_KINDS }$KIND" ;;
  esac
  export DEAD_KINDS
  log "run: deferred idx=$IDX $REPO ($KIND) — $1"
  exec "$0"   # on to the next charm in this same slot
}

# This kind already failed its probe in this slot, so do not pay for another one.
case " $DEAD_KINDS " in
  *" $KIND "*) defer_charm "substrate for kind '$KIND' already failed this slot" ;;
esac

# Skip work already done, so the queue is resumable and forced test runs are not
# redone when the cursor later reaches them. -f forces a redo. "Done" means a review
# that passes review_is_good, not merely a file that exists — see lib.sh.
if [ -z "$FORCE_REPO" ] && review_is_good "$REVIEW_FILE"; then
  log "run: idx=$IDX $REPO already reviewed, advancing past it"
  if [ "$FROM_DEFERRED" = 1 ]; then defer_undo; else echo $((IDX+1)) > "$ROOT/state/cursor"; fi
  exec "$0"   # move straight on to the next charm in this same slot
fi
NOTES_FILE="$ROOT/notes/$REPO.notes.md"
LOGDIR="$ROOT/logs/$REPO"; mkdir -p "$LOGDIR"
# Everything this run writes into LOGDIR lands at or after this instant. provider_budget_block
# uses it to ignore logs left by an *earlier* run of the same charm — see the comment on that
# function in lib.sh for the 2026-08-30 stall that made the filter necessary. Set here rather
# than at the top of the file because LOGDIR is the first point at which anything of this
# run's is written under it.
export BUDGET_LOG_SINCE=$(date +%s)
WS="$ROOT/work/$REPO"

# ---- resource guard ----------------------------------------------------
# A run that cannot deploy anything is a run that wastes budget. Bail out
# loudly rather than producing a code-only review by accident.
# stderr, not stdout, carries cleanup's narration: log() tees to runs.log and copies to
# stderr. Redirecting that copy back into runs.log wrote every pre-flight line there
# twice. Send it to the per-run log, as the other two cleanup calls already do.
"$ROOT/bin/cleanup.sh" >>"$LOGDIR/cleanup.log" 2>&1

# A model that wedges in `destroying` does not just sit there: its dependency
# engine restarts three workers roughly once a minute for ever. Repair the
# controller before starting work, while we hold the lock and nothing is
# deployed. See bin/repair-controller.sh.
for ctl in "$CTL_K8S4" "$CTL_K8S3"; do
  WEDGED=$(CTL="$ctl" python3 -c "
import os, pathlib, time
p = pathlib.Path('$ROOT/state/destroying.tsv')
now, ctl, n = time.time(), os.environ['CTL'], 0
if p.exists():
    for line in p.read_text().splitlines():
        f = line.split('\t')
        if len(f) == 3 and f[0].startswith(ctl + ':') and now - float(f[1]) >= ${REAP_AFTER:-1800}:
            n += 1
print(n)" 2>/dev/null || echo 0)
  if [ "${WEDGED:-0}" -ge 2 ]; then
    log "run: $WEDGED wedged model(s) on $ctl"
    "$ROOT/bin/repair-controller.sh" "$ctl" || true
  fi
done

FREE_G=$(df --output=avail -BG / | tail -1 | tr -dc '0-9')
FREE_M=$(free -g | awk 'NR==2{print $7}')
if [ "${FREE_G:-0}" -lt "${MIN_FREE_DISK_G:-18}" ]; then
  # Skipping without consuming the slot keeps the queue intact, which is right, but on its
  # own it repairs nothing. On 2026-08-05 the disk filled and this branch then ran for
  # every slot until 08-09: 25 consecutive skips, four days, no progress and no recovery.
  #
  # The stall sustained itself. A full disk stops the juju API answering, so the cleanup
  # that would have destroyed the offending model could not list models at all — the one
  # action that would have freed the disk was the one the full disk prevented. Nothing
  # that goes through juju can break that loop, so escalate to the reclaim that does not:
  # bin/logcap.sh is pure filesystem work. Once it has freed space juju answers again and
  # the ordinary cleanup can finish the job, so run that second and re-check before giving
  # up. Only a genuinely unrecoverable box should still skip.
  log "run: only ${FREE_G}G disk free (need ${MIN_FREE_DISK_G:-18}G) — attempting hard reclaim"
  "$ROOT/bin/logcap.sh" --force >>"$LOGDIR/cleanup.log" 2>&1 || true
  "$ROOT/bin/cleanup.sh" >>"$LOGDIR/cleanup.log" 2>&1 || true
  FREE_G=$(df --output=avail -BG / | tail -1 | tr -dc '0-9')
  if [ "${FREE_G:-0}" -lt "${MIN_FREE_DISK_G:-18}" ]; then
    log "run: still only ${FREE_G}G free after reclaim — skipping slot without consuming it"
    exit 0
  fi
  log "run: reclaim recovered space — ${FREE_G}G free, continuing"
fi
if [ "${FREE_M:-0}" -lt "${MIN_FREE_MEM_G:-4}" ]; then
  # Same shape as the disk guard above, and the same lesson: skipping repairs nothing, so
  # this would have repeated every slot for ever too. Here the likely culprit is knowable.
  # We hold the lock, so no legitimate review is in flight — any agent process still alive
  # is an orphan from a run that died without reaping it. That is not hypothetical: on
  # 2026-08-09 killing a run's parent left its `timeout`/`pi` child running and holding its
  # memory. cleanup.sh cannot help here; it frees disk and never kills anything.
  log "run: only ${FREE_M}G memory available (need ${MIN_FREE_MEM_G:-4}G) — reaping orphaned agents"
  pkill -f "pi -p --no-session" 2>/dev/null && log "run: killed orphaned agent process(es)"
  sleep 10
  FREE_M=$(free -g | awk 'NR==2{print $7}')
  if [ "${FREE_M:-0}" -lt "${MIN_FREE_MEM_G:-4}" ]; then
    log "run: still only ${FREE_M}G memory after reaping orphans — skipping slot without consuming it"
    exit 0
  fi
  log "run: reaped orphans — ${FREE_M}G available, continuing"
fi

# Disk and memory say the box is healthy. They say nothing about whether anything can
# actually be *deployed*, and a run that cannot deploy does not fail — it quietly writes
# a code-only review, which clears the 8K/1-finding floor, is recorded as done and is
# never revisited. That is the silent-drift case, so check the substrate too. A host
# reboot is the obvious way in: after the 2026-07-30 boot at 12:14 a run started at
# 12:22 and spent its whole 3h producing a 3.6K review with 0 citations checked.
#
# Skipping is deliberately the only outcome here — there is no "waited long enough,
# proceed anyway" valve. An unspent slot leaves the queue intact and recoverable; a
# queue burned through with code-only reviews is neither, because the cursor has moved
# past every one of them. Halting is the recoverable error, so bias to it.
#
# The expected case is transient (the substrate is mid-boot), so wait it out rather than
# skipping on the first miss. The wait is minutes against a 4h slot and holds the lock
# throughout, so it cannot overlap the next one.
NEED_CTLS=$(controllers_for_kind "$KIND")
WAITED=0
READY_CTLS=$(ready_controllers $NEED_CTLS)
while [ -z "$READY_CTLS" ]; do
  if [ "$WAITED" -ge "${SUBSTRATE_WAIT_MAX:-900}" ]; then
    # Skipping remains the right outcome for this slot — the reasoning above about there
    # being no "proceed anyway" valve is unchanged. What was missing is any attempt to fix
    # the cause before giving up, which is exactly what turned the disk stall into four
    # lost days. repair-controller.sh was written for a wedged controller but was only
    # reachable from the wedged-destroying-models pre-flight, so a controller that had gone
    # unreachable could never trigger it. Try it once before skipping; it carries its own
    # 6h cooldown, so this cannot turn into a restart loop.
    #
    # The two substrates need different repairs. k8s: delete controller-0 in the controller
    # namespace and let it come back. LXD: the controller is a container, and the failure
    # seen on 2026-08-05 was that the container no longer existed at all — which no restart
    # fixes, only a re-bootstrap. That gap is why concierge-lxd stayed dead for six days.
    for ctl in $NEED_CTLS; do
      log "run: $ctl still unreachable — attempting repair before setting the charm aside"
      case "$ctl" in
        "$CTL_K8S4"|"$CTL_K8S3") "$ROOT/bin/repair-controller.sh" "$ctl" >/dev/null 2>&1 || true ;;
        "$CTL_LXD4"|"$CTL_LXD3") "$ROOT/bin/repair-lxd-controller.sh" "$ctl" >/dev/null 2>&1 || true ;;
      esac
    done
    READY_CTLS=$(ready_controllers $NEED_CTLS)
    if [ -n "$READY_CTLS" ]; then
      log "run: repair brought $READY_CTLS back, continuing"
      break
    fi
    # Not `exit 0`. See defer_charm: halting here pins the cursor on a charm that cannot
    # run and stops the whole programme, including the kinds that are perfectly healthy.
    defer_charm "no $KIND controller reachable after $((WAITED/60))min (tried: $NEED_CTLS)"
  fi
  log "run: no $KIND controller reachable yet (tried: $NEED_CTLS), re-probing in ${SUBSTRATE_PROBE_INTERVAL:-60}s"
  sleep "${SUBSTRATE_PROBE_INTERVAL:-60}"
  WAITED=$(( WAITED + ${SUBSTRATE_PROBE_INTERVAL:-60} ))
  READY_CTLS=$(ready_controllers $NEED_CTLS)
done
if [ "$READY_CTLS" != "$NEED_CTLS" ]; then
  # Reviewable, but the cross-version comparison the brief asks for is not available.
  log "run: only $READY_CTLS reachable of '$NEED_CTLS' — proceeding on the reachable one"
fi
if [ "$WAITED" -gt 0 ]; then
  log "run: substrate came up after $((WAITED/60))min, continuing"
fi

# ---- budget ------------------------------------------------------------
SPENT=$(usage_today); LIMIT=$(daily_limit)
if [ -z "$SPENT" ]; then log "run: cannot reach openrouter, aborting (cursor unchanged)"; exit 1; fi
# Ask the provider what is left rather than deriving it from the day's spend — on a key whose
# limit does not reset, those two are different numbers. See budget_remaining in lib.sh.
REMAIN=$(budget_remaining)
[ -z "$REMAIN" ] && REMAIN=$(python3 -c "print(f'{max(0.0,$LIMIT-$SPENT):.2f}')")
REMAIN=$(python3 -c "print(f'{float(\"$REMAIN\"):.2f}')")
# OpenRouter's allowance resets at 00:00 UTC, not local midnight — confirmed on
# 2026-07-25, when spend went back to $0 at 12:00 NZST. Count the slots left in
# the UTC day, or the run at 00:00 local divides what is left of the *afternoon's*
# budget by a full 8 slots and reviews all night on a starvation cap.
# The cron slots are every SLOT_HOURS on the hour, so they land on the same hours in UTC.
SLOTS_LEFT=$(python3 -c "
import datetime
h=datetime.datetime.now(datetime.timezone.utc).hour
print(max(1,len([x for x in range(0,24,int("$SLOT_HOURS")) if x>=h])))")
CAP=$(python3 -c "
cap=min($MAX_RUN_BUDGET, $REMAIN/$SLOTS_LEFT)
print(f'{cap:.2f}')")
# Citation correction is the pass that makes the file:line references trustworthy —
# about half of first-draft citations are wrong without it. If the deep passes are
# allowed to spend the whole cap, that correction gets skipped and the review keeps its
# bad citations. So the exploring passes stop short of the cap and leave this reserve
# behind for it. A pass costs $0.30-0.50 and there can be two, so the reserve must cover
# ~$1.00, not the $0.15 originally assumed — see CITE_RESERVE in lib.sh.
WORK_CAP=$(python3 -c "print(f'{max($CAP-${CITE_RESERVE:-1.00}, $CAP*0.5):.2f}')")
log "run: idx=$IDX repo=$REPO kind=$KIND spent_today=\$$SPENT limit=\$$LIMIT budget_left=\$$REMAIN slots_left=$SLOTS_LEFT cap=\$$CAP (work \$$WORK_CAP)"
if python3 -c "import sys; sys.exit(0 if $REMAIN < $MIN_RUN_BUDGET else 1)"; then
  log "run: only \$$REMAIN of budget left, skipping without consuming the queue slot"; exit 0
fi

# advance the cursor now: a charm that crashes the harness must not wedge the queue.
# A charm taken off the deferred list is not at the cursor, so it clears its deferred row
# instead. Either way the failure paths below (retry_or_give_up) put it back exactly once.
if [ "$FROM_DEFERRED" = 1 ]; then
  defer_undo
  log "run: $REPO came off the deferred list — its substrate is back"
elif [ -z "$FORCE_REPO" ]; then
  echo $((IDX+1)) > "$ROOT/state/cursor"
fi

# ---- always clean up, however we exit ----------------------------------
WATCHDOG_PID=""
# The agent's own exit status, once it has one. `rc=$?` inside the trap is the status of
# whatever ran last before the exit — usually the polish pass — so a run whose agent
# timed out at rc=124 was being written to history as rc=0. Report what the agent did.
AGENT_RC=""
# Set when the slot was refused by the provider before any work could happen (see
# budget_abort). Such a slot did not review the charm and must not be written to
# history.tsv as though it had: a row of rc=1 bytes=0 for a charm that is still queued
# reads as "this charm failed", and 6 of them a day for as long as the budget is out
# would bury the real corpus stats that RESUME.md's numbers are checked against.
SLOT_ABORTED=0
finish() {
  rc=$?
  [ -n "$WATCHDOG_PID" ] && kill "$WATCHDOG_PID" 2>/dev/null
  "$ROOT/bin/cleanup.sh" "$WS" >>"$LOGDIR/cleanup.log" 2>&1
  if [ "$SLOT_ABORTED" = 1 ]; then
    log "run: slot abandoned before reviewing $REPO — not recording it as an attempt"
    return
  fi
  END_SPENT=$(usage_today); [ -z "$END_SPENT" ] && END_SPENT="$SPENT"
  COST=$(python3 -c "print(f'{max(0.0,($END_SPENT)-($SPENT)):.3f}')" 2>/dev/null || echo "?")
  SIZE=$( [ -f "$REVIEW_FILE" ] && wc -c <"$REVIEW_FILE" || echo 0 )
  NFIND=$(review_findings "$REVIEW_FILE")
  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$(date -Is)" "$IDX" "$REPO" "rc=${AGENT_RC:-$rc}" "cost=\$$COST" "bytes=$SIZE" "findings=$NFIND" >> "$ROOT/state/history.tsv"
  log "run: finished $REPO rc=${AGENT_RC:-$rc} cost=\$$COST review=${SIZE}B findings=$NFIND"
  "$ROOT/bin/index.sh" >/dev/null 2>&1
}
trap finish EXIT

"$ROOT/bin/cleanup.sh" >>"$LOGDIR/cleanup.log" 2>&1

# Put the charm back at the head of the queue, once. Both failure paths — prepare failing
# here, and no usable review at the bottom — must apply the same rule, so they share one
# implementation rather than two copies that can drift apart (see lib.sh on review_is_good
# for the same argument). One bad slot must not drop a charm; a charm that fails twice must
# not wedge the queue.
# Put the charm back where the next slot will find it. The cursor advanced before the
# work, so both callers have to undo that; they differ only in whether the attempt counts
# against the charm's one retry.
requeue_charm() {  # requeue_charm <why>
  if [ "$FROM_DEFERRED" = 1 ]; then
    # This charm is behind the cursor, so rewinding the cursor to it would re-walk
    # everything in between. Put it back where it came from instead.
    defer_record "$1"
    log "run: put $REPO back on the deferred list to be retried"
  else
    echo "$IDX" > "$ROOT/state/cursor"
    log "run: rewound the cursor to $IDX so $REPO is retried next slot"
  fi
}

retry_or_give_up() {  # retry_or_give_up
  [ -n "$FORCE_REPO" ] && return 0
  local retries="$ROOT/state/retries.tsv" n
  n=$(awk -F'\t' -v r="$REPO" '$1==r{print $2}' "$retries" 2>/dev/null | tail -1)
  if [ "${n:-0}" -lt 1 ]; then
    printf '%s\t%s\n' "$REPO" "$(( ${n:-0} + 1 ))" >> "$retries"
    requeue_charm "failed on the slot that took it off the deferred list"
  else
    log "run: $REPO has already been retried once, giving up on it"
  fi
}

# The provider refused to bill the account at all — the monthly budget is gone, or the
# credit balance is. Nothing about this charm is wrong and nothing here can fix it, so
# treat it the way the substrate guard treats a dead controller: give the slot back
# untouched and wait. No retry is spent, no history row is written, and the cursor stays
# on this charm, so whenever the budget returns the queue simply carries on from here.
# Every slot until then costs a few seconds and $0.
#
# NOT defer_charm: that execs on to the next charm in the same slot, which is right for a
# substrate that only one *kind* of charm needs and catastrophically wrong here — an
# account with no money left would defer the entire remaining queue in a single slot.
budget_abort() {  # budget_abort <provider message>
  SLOT_ABORTED=1
  log "run: provider refused to bill this account — $1"
  if [ -n "$FORCE_REPO" ]; then
    log "run: forced run, leaving the queue alone"
  else
    requeue_charm "provider budget exhausted"
    log "run: slot given back without consuming it; $REPO stays next in line"
  fi
  exit 0
}

# Check after any turn that could have been refused. Cheap: greps one log.
check_provider_budget() {  # check_provider_budget <logfile>...
  local msg
  msg=$(provider_budget_block "$@") && budget_abort "$msg"
  return 0
}

# ---- prepare -----------------------------------------------------------
rm -rf "$WS"
"$ROOT/bin/prepare.sh" "$REPO" "$SRC" "$WS" >>"$LOGDIR/prepare.log" 2>&1
if [ ! -d "$WS/repo" ]; then
  # The cursor advanced above, and this exit goes straight to the finish trap — which does
  # not rewind it. Without the rewind the charm is written to history with bytes=0 and is
  # never revisited, which is the same silent-loss class as the rc=0 stub and the no-op
  # citation gate. Nothing has been lost to it yet; that is luck, not design.
  log "run: prepare failed for $REPO"
  retry_or_give_up
  exit 1
fi

# ---- the review --------------------------------------------------------
export WS REVIEW_FILE NOTES_FILE
TIME_BUDGET_HUMAN=$(python3 -c "print(f'{$RUN_TIMEOUT//60} minutes')")
TODAY=$(date +%Y-%m-%d)
BRIEF=$(mkdir -p "$WS" && sed -e "s#\$WS#$WS#g" -e "s#\$REVIEW_FILE#$REVIEW_FILE#g" \
        -e "s#\$NOTES_FILE#$NOTES_FILE#g" -e "s#\$TIME_BUDGET_HUMAN#$TIME_BUDGET_HUMAN#g" \
        -e "s#\$TODAY#$TODAY#g" \
        "$ROOT/prompts/review.md" > "$WS/BRIEF.md" && echo "$WS/BRIEF.md")

cat > "$WS/TASK.md" <<EOF
Review the charm repository at $WS/repo — this is "$REPO" from the $ORG org
($KIND charm; declared charms: ${NAMES:-see _context/charms.json}).

Your full brief is in $BRIEF. Read it first, then follow it. Write your review to
$REVIEW_FILE and your working notes to $NOTES_FILE. Start now and keep working
until the review is genuinely thorough.
EOF

# pi has no spend cap of its own, so poll and stop a turn if it runs away.
# The agent writes its review to disk as it goes, so a kill still leaves output.
# Sets WATCHDOG_PID. The turn must be started with `exec setsid` in a background
# subshell so that $! is the process-group leader and the group kill lands on pi
# itself, not just on the timeout wrapper.
WATCHDOG_PID=""
# Watches a turn on two axes, because they fail differently: a runaway turn spends too
# much, and a wedged turn spends nothing at all. Until 2026-08-04 only the first was
# checked — see LIVENESS_STALL in lib.sh for the turn that burned 2h08 for 1s of CPU.
start_spend_watchdog() {  # start_spend_watchdog <pid> <cap> <label> [logfile]
  local pid="$1" cap="$2" label="$3" logf="${4:-}"
  ( stop() {  # stop <why>
      echo "[$(date -Is)] watchdog: $1, stopping $label" >> "$LOGDIR/watchdog.log"
      kill -TERM -- "-$pid" 2>/dev/null; sleep 30
      kill -KILL -- "-$pid" 2>/dev/null
      exit 0
    }
    base_b=-1; base_c=0; base_m=""; base_s=""; base_t=$(date +%s)
    while kill -0 "$pid" 2>/dev/null; do
      sleep "${WATCHDOG_POLL:-90}"
      # --- spend ---
      # A failed usage lookup must not skip the liveness check below: the network being
      # unreachable is itself a decent reason to suspect the turn is going nowhere.
      NOW=$(usage_today)
      if [ -n "$NOW" ] && python3 -c "import sys; sys.exit(0 if ($NOW)-($SPENT) > $cap else 1)"; then
        stop "$label passed \$$cap"
      fi
      # --- liveness ---
      # The clock resets only on *meaningful* progress, not on any change at all, so a
      # turn ticking the odd CPU second while wedged still trips it. Any log growth
      # counts, since the turn only writes when it has something to say.
      #
      # Spend is the primary signal and the only one that cannot go quiet during honest
      # work: a turn talking to the model is alive by definition, and a wedged one bills
      # nothing. It is already fetched just above for the cap check, so it is free. This
      # matters because the other three signals all go flat *together* during a deploy —
      # pi idles in ep_poll waiting on its child, -p mode prints nothing, and notes are
      # not written mid-deploy. On kfp-operators (2026-08-17) that combination read as
      # 34.7min of "no progress" while spend climbed $0.31 -> $1.27 and the turn went on
      # to finish rc=0. An empty lookup is not progress; it leaves the clock running.
      read -r b c marks <<<"$(turn_activity "$pid" "$logf")"
      spent_up=0
      if [ -n "$NOW" ] && [ -n "$base_s" ] && \
         python3 -c "import sys; sys.exit(0 if ($NOW)-($base_s) > 0.0005 else 1)"; then
        spent_up=1
      fi
      if [ "$base_b" -lt 0 ] || [ "$spent_up" -eq 1 ] || [ "$b" -gt "$base_b" ] || \
         [ "$marks" != "$base_m" ] || [ "$(( c - base_c ))" -ge "${LIVENESS_MIN_CPU:-5}" ]; then
        base_b="$b"; base_c="$c"; base_m="$marks"; base_t=$(date +%s)
        [ -n "$NOW" ] && base_s="$NOW"
        continue
      fi
      [ -n "$NOW" ] && base_s="$NOW"
      idle=$(( $(date +%s) - base_t ))
      if [ "$idle" -ge "${LIVENESS_STALL:-3600}" ]; then
        stop "$label made no progress for $((idle/60))min (log +0B, no review/notes write, no spend, CPU +$(( c - base_c ))s)"
      fi
    done ) &
  WATCHDOG_PID=$!
}

START_TS=$(date +%s)
log "run: starting agent on $REPO with $WORK_MODEL (cap \$$CAP, timeout ${RUN_TIMEOUT}s)"
( cd "$WS/repo" && exec setsid timeout --signal=TERM --kill-after=60 "$RUN_TIMEOUT" \
    pi -p --no-session --no-approve --no-context-files \
       --model "$WORK_MODEL" --thinking high \
       --append-system-prompt "$BRIEF" \
       "$(cat "$WS/TASK.md")" </dev/null ) > "$LOGDIR/agent.log" 2>&1 &
AGENT_PID=$!
start_spend_watchdog "$AGENT_PID" "$WORK_CAP" "first pass" "$LOGDIR/agent.log"

wait "$AGENT_PID"; AGENT_RC=$?
kill "$WATCHDOG_PID" 2>/dev/null; WATCHDOG_PID=""
log "run: agent finished rc=$AGENT_RC"
# Checked here as well as at the bottom so a refused account does not go on to pay for
# deploys, depth passes and a citation gate that cannot run either.
check_provider_budget "$LOGDIR/agent.log"

# ---- helper: another pi turn against the same workspace -----------------
# The cap check here is only a pre-flight: it stops a turn starting past the cap but
# said nothing about a turn that starts just under it. Until 2026-07-30 the depth passes
# had no watchdog, so a pass beginning at $4.49 of a $4.50 work cap could run for 40
# minutes and spend straight through the citation reserve behind it. That is how k6 and
# kyuubi ended at $5.77 and $6.52 of a $5.50 cap with their citation correction skipped
# and 9 bad citations each left standing. Every turn is now watchdogged, not just the
# first one — so the reserve survives the work phase.
agent_turn() {  # agent_turn <label> <timeout> <prompt> [cap]
  local label="$1" tmo="$2" prompt="$3" cap="${4:-$CAP}" now pid rc
  now=$(usage_today)
  if [ -n "$now" ] && python3 -c "import sys; sys.exit(0 if ($now)-($SPENT) > $cap else 1)"; then
    log "run: skipping $label, run is already at its \$$cap cap"; return 1
  fi
  log "run: $label"
  ( cd "$WS/repo" && exec setsid timeout --signal=TERM --kill-after=60 "$tmo" \
      pi -p --no-session --no-approve --no-context-files \
         --model "$WORK_MODEL" --thinking high \
         --append-system-prompt "$BRIEF" "$prompt" </dev/null ) >> "$LOGDIR/$label.log" 2>&1 &
  pid=$!
  start_spend_watchdog "$pid" "$cap" "$label" "$LOGDIR/$label.log"
  wait "$pid"; rc=$?
  kill "$WATCHDOG_PID" 2>/dev/null; WATCHDOG_PID=""
  return $rc
}

# ---- depth passes ------------------------------------------------------
# The agent reliably stops early: 10 min of 30, then 15 min of 60 in the two smoke
# tests. Telling it to try harder in the brief moved the needle barely, so the budget
# is enforced structurally instead — keep handing it back until it has used the time.
if [ -s "$REVIEW_FILE" ]; then
  PASS=0
  while [ "$PASS" -lt "${DEPTH_PASSES:-3}" ]; do
    ELAPSED=$(( $(date +%s) - START_TS ))
    if [ "$ELAPSED" -ge $(( RUN_TIMEOUT * ${DEPTH_PCT:-55} / 100 )) ]; then break; fi
    PASS=$((PASS+1))
    LEFT=$(( RUN_TIMEOUT - ELAPSED - 600 ))
    [ "$LEFT" -lt 300 ] && break
    agent_turn "deepen-$PASS" "$LEFT" \
      "$(sed -e "s#\$REVIEW_FILE#$REVIEW_FILE#g" -e "s#\$NOTES_FILE#$NOTES_FILE#g" \
             -e "s#\$USED_MIN#$((ELAPSED/60))#g" -e "s#\$BUDGET_MIN#$((RUN_TIMEOUT/60))#g" \
             "$ROOT/prompts/deepen.md")" "$WORK_CAP" || break
  done
fi

# ---- citation correction ------------------------------------------------
# About half of all cited line numbers were wrong in both smoke tests, including
# citations into files shorter than the line cited. This is checkable, so check it.
# Only worth doing if there is a review at all: on the datahub run these passes
# spent 15 minutes and $0.5 being told the file did not exist.
# The reserve only guarantees anything if these passes are measured from where the work
# phase actually stopped. Gating them at the absolute $CAP meant a work phase that ended
# at the cap left nothing behind for them, which is exactly the case the reserve exists
# to prevent. Measure from here instead, so the correction always gets its $CITE_RESERVE
# however the work phase went, and never less than the original cap allowed.
CITE_NOW=$(usage_today)
if [ -n "$CITE_NOW" ]; then
  CITE_CAP=$(python3 -c "print(f'{max($CAP, ($CITE_NOW)-($SPENT)+${CITE_RESERVE:-1.00}):.2f}')")
else
  CITE_CAP="$CAP"
fi
[ "$CITE_CAP" = "$CAP" ] || log "run: work phase overran, citation cap raised to \$$CITE_CAP"
for attempt in 1 2; do
  [ -s "$REVIEW_FILE" ] || break
  REPORT=$(python3 "$ROOT/bin/verify-citations.py" "$REVIEW_FILE" "$WS/repo" "$WS/deps" 2>&1) && break
  echo "$REPORT" >> "$LOGDIR/citations.log"
  log "run: citation check attempt $attempt — $(echo "$REPORT" | head -1)"
  # build the prompt through files; the report contains quotes and backticks
  printf '%s\n' "$REPORT" > "$WS/citation-report.txt"
  REVIEW_FILE="$REVIEW_FILE" python3 - "$ROOT/prompts/fix-citations.md" \
      "$WS/citation-report.txt" "$WS/fix-prompt.txt" <<'PY'
import os, sys, pathlib
tpl, rep, out = (pathlib.Path(p) for p in sys.argv[1:4])
pathlib.Path(out).write_text(
    tpl.read_text()
       .replace("$REPORT", rep.read_text())
       .replace("$WS", os.environ["WS"])
       .replace("$REVIEW_FILE", os.environ["REVIEW_FILE"]))
PY
  agent_turn "fix-citations-$attempt" 900 "$(cat "$WS/fix-prompt.txt")" "$CITE_CAP" || break
done
if [ -s "$REVIEW_FILE" ]; then
  python3 "$ROOT/bin/verify-citations.py" "$REVIEW_FILE" "$WS/repo" "$WS/deps" > "$LOGDIR/citations-final.log" 2>&1
  log "run: citations final — $(head -1 "$LOGDIR/citations-final.log")"
fi

# ---- polish ------------------------------------------------------------
# A short, cheap pass on a Claude model: tighten the prose and structure of the
# draft. It may not add findings — everything it says has to come from the draft
# and the notes, which is why it is allowed to read them but not the internet.
if [ -s "$REVIEW_FILE" ]; then
  SPENT2=$(usage_today)
  REMAIN2=$(budget_remaining)
  [ -z "$REMAIN2" ] && REMAIN2=$(python3 -c "print(f'{max(0.0,$LIMIT-$SPENT2):.2f}')")
  REMAIN2=$(python3 -c "print(f'{float(\"$REMAIN2\"):.2f}')")
  if python3 -c "import sys; sys.exit(0 if $REMAIN2 > $POLISH_BUDGET else 1)"; then
    cp "$REVIEW_FILE" "$LOGDIR/review.draft.md"
    log "run: polishing with $POLISH_MODEL"
    timeout "$POLISH_TIMEOUT" pi -p --no-session --no-approve --no-context-files \
      --model "$POLISH_MODEL" --thinking low \
      "$(sed -e "s#\$REVIEW_FILE#$REVIEW_FILE#g" -e "s#\$NOTES_FILE#$NOTES_FILE#g" \
             -e "s#\$TODAY#$TODAY#g" \
             -e "s#\$DRAFT#$LOGDIR/review.draft.md#g" "$ROOT/prompts/polish.md")" \
      </dev/null > "$LOGDIR/polish.log" 2>&1
    [ -s "$REVIEW_FILE" ] || cp "$LOGDIR/review.draft.md" "$REVIEW_FILE"
  else
    log "run: skipping polish, only \$$REMAIN2 of budget left"
  fi
fi

# ---- did the slot actually produce a review? ---------------------------
# datahub-k8s-operator (2026-07-25) exited rc=0 in two minutes having written nothing at
# all and not even a line to its own log. kafka-benchmark-operator (2026-07-30) was the
# subtler version of the same thing: it burned the full 3h, timed out, and left a 3.6K
# file whose Findings section was empty — which the old `[ -s ]` test accepted, so the
# charm was recorded as reviewed and silently lost. Test the artifact, not the exit code.
# Either way a charm must not fall out of the queue because of one bad slot: rewind the
# cursor so the next slot picks it up again. Once only — a charm that fails twice is the
# charm's problem, not a flake, and must not wedge the queue.
if ! review_is_good "$REVIEW_FILE"; then
  log "run: $REPO produced no usable review ($( [ -f "$REVIEW_FILE" ] && wc -c <"$REVIEW_FILE" || echo 0 )B, \
$(review_findings "$REVIEW_FILE") findings, agent rc=${AGENT_RC:-?}, \
agent.log $(wc -c <"$LOGDIR/agent.log" 2>/dev/null || echo 0)B)"
  # Keep the rejected attempt for inspection, but move it out of reviews/ so the retry is
  # not skipped as "already reviewed" and INDEX.md does not count it among the reviewed.
  if [ -s "$REVIEW_FILE" ]; then
    REJECTED="$LOGDIR/review.rejected.$(date +%Y%m%dT%H%M%S).md"
    mv "$REVIEW_FILE" "$REJECTED"
    log "run: kept the rejected draft at $REJECTED"
  fi
  # Catch-all: the budget can also run out part way through, in which case the first pass
  # was clean and one of the later logs holds the refusal. An empty review is only the
  # charm's fault if the provider was willing to be paid.
  check_provider_budget "$LOGDIR"/agent.log "$LOGDIR"/*.log
  retry_or_give_up
fi
