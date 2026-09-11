#!/bin/bash
# Cap runaway logging inside LXD containers.
#
# Why this exists, and why it runs on its own short timer rather than inside cleanup.sh:
#
# opentelemetry-collector (queue idx 62) scrapes /var/log/syslog for forwarding *and*
# writes its own progress lines to syslog, so every line it read produced another line
# to read. Measured on 2026-08-09 while it was still running: ~120MB/s. That fills this
# box's 260G disk in about half an hour, and it did so twice.
#
# Half an hour is far shorter than the 4h review cycle, so a check that only runs at slot
# boundaries cannot contain it: by the time the next slot starts the disk is already full.
# And a full disk is self-sustaining, because juju's API stops answering when it cannot
# write — so reap-models.py could not even *list* the model it needed to destroy, and
# cleanup.sh skipped the very containers that were filling the disk. 25 consecutive slots
# skipped, four days lost, every one of them running a cleanup that could not help itself.
#
# So the rule here is: do only filesystem work. No juju, and no LXD API on the common
# path, because those are exactly what stop working when this is needed. Truncation is
# always safe on a multi-gigabyte log and works on an open file — rsyslog appends, so
# writes resume at zero.
#
# Truncating alone only mops up, though: an offender refills within minutes. So a
# container that offends repeatedly gets stopped, which is what actually ends the bleed.
# The review's model is destroyed by the next cleanup anyway, so stopping it early costs
# nothing that was not already being thrown away.
#
# This is not a one-charm patch. cos-proxy (75), parca-agent (106), otel-ebpf-profiler
# (112) and hardware-observer (139) are all still queued and all forward logs the same way.
#
# Run from cron every minute. --force is accepted for symmetry with the caller in
# run-review.sh and simply means "run now"; there is no other mode.
. /home/ubuntu/charm-review/bin/lib.sh

POOL=/var/snap/lxd/common/lxd/storage-pools/default/containers
# A legitimate container log does not reach a gigabyte between two runs of this script.
TRUNCATE_MB=${LOGCAP_TRUNCATE_MB:-1024}
# Truncating the same container this many times means it is not a spike, it is a loop.
STOP_AFTER=${LOGCAP_STOP_AFTER:-3}
OFFENCES="$ROOT/state/logcap.d"
KEEP_LIST="$ROOT/state/keep-containers"

[ -d "$POOL" ] || exit 0
mkdir -p "$OFFENCES"

# The pool directory is root-only, so every path test below has to go through sudo. A
# plain `for cdir in "$POOL"/*` silently expands to nothing as the ubuntu user cron runs
# as, which made the first version of this script a no-op that reported success.
mapfile -t CONTAINERS < <(sudo -n find "$POOL" -maxdepth 1 -mindepth 1 -type d -printf '%f\n' 2>/dev/null)
for c in "${CONTAINERS[@]}"; do
  cdir="$POOL/$c"
  sudo -n test -d "$cdir/rootfs" || continue

  # Only the log trees. Scanning a whole rootfs every minute would be its own problem,
  # and a runaway writer is always writing a log.
  mapfile -t BIG < <(sudo -n find "$cdir/rootfs/var/log" -type f -size +"${TRUNCATE_MB}"M \
                       -printf '%s\t%p\n' 2>/dev/null | sort -nr)
  [ "${#BIG[@]}" -eq 0 ] && continue

  for entry in "${BIG[@]}"; do
    sz=${entry%%	*}
    path=${entry#*	}
    log "logcap: truncating $(awk -v s="$sz" 'BEGIN{printf "%.1fG", s/1073741824}') $path"
    sudo -n truncate -s 0 "$path" 2>/dev/null
  done

  # Record the offence and decide whether mopping up is still worth it.
  echo "$(date -Is)" >> "$OFFENCES/$c"
  n=$(wc -l < "$OFFENCES/$c")
  [ "${n:-0}" -lt "$STOP_AFTER" ] && continue

  # Being a repeat offender is not on its own a reason to stop the container, and stopping
  # one that is under review destroys the deployment the review depends on — which would
  # produce exactly the code-only review this whole exercise exists to prevent. (idx 62 is
  # opentelemetry-collector itself: the charm that caused the stall is also a charm that has
  # to be reviewed, deployed and running.)
  #
  # Truncating once a minute already bounds the worst observed writer to ~7G between passes,
  # which this disk absorbs without noticing. So mopping up is the normal case and is
  # sufficient; stopping is only warranted once truncation is demonstrably *not* keeping up.
  # Gate it on real pressure rather than on offence count alone.
  FREE_G=$(df --output=avail -BG / | tail -1 | tr -dc '0-9')
  if [ "${FREE_G:-0}" -ge "${LOGCAP_STOP_FREE_G:-40}" ]; then
    [ $(( n % 30 )) -eq 0 ] &&
      log "logcap: $c has filled its log $n times but disk is healthy (${FREE_G}G free) — still only truncating"
    continue
  fi

  # --- protections on the stop path only; truncation above is safe for anything ---
  # Never stop a juju controller: that would take down the substrate every review needs,
  # and a busy controller can legitimately produce a large log. Detected from the
  # filesystem rather than by name, so it holds if a controller is ever rebuilt.
  if sudo -n test -d "$cdir/rootfs/var/snap/juju-db" || \
     [ -n "$(sudo -n find "$cdir/rootfs/var/lib/juju/agents" -maxdepth 1 -name 'controller-*' \
               -print -quit 2>/dev/null)" ]; then
    log "logcap: $c looks like a juju controller — truncating only, not stopping"
    continue
  fi
  # The operator's own containers, by explicit list and by predating the harness.
  grep -qxF "$c" "$KEEP_LIST" 2>/dev/null && continue
  EPOCH=$(cat "$ROOT/state/epoch" 2>/dev/null || echo 0)
  born=$(sudo -n lxc info "$c" 2>/dev/null | awk -F': ' '/Created/{print $2}' |
         xargs -I{} date -d "{}" +%s 2>/dev/null)
  if [ -n "$born" ] && [ "$born" -lt "$EPOCH" ]; then
    log "logcap: $c predates the harness — truncating only, not stopping"
    continue
  fi

  log "logcap: $c has filled its log $n times and only ${FREE_G}G is free — stopping it to end the bleed"
  sudo -n lxc stop "$c" --force 2>/dev/null &&
    log "logcap: stopped $c" || log "logcap: could not stop $c (LXD unresponsive?)"
  rm -f "$OFFENCES/$c"
done

# Offence files for containers that no longer exist are noise. Best-effort: this needs the
# LXD API, so it is allowed to fail silently when everything is seized.
LIVE=$(sudo -n lxc list --format csv -c n 2>/dev/null)
if [ -n "$LIVE" ]; then
  for f in "$OFFENCES"/*; do
    [ -e "$f" ] || continue
    echo "$LIVE" | grep -qxF "$(basename "$f")" || rm -f "$f"
  done
fi
