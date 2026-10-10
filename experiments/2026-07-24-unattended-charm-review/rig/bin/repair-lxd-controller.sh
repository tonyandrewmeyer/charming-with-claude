#!/bin/bash
# Re-bootstrap an LXD juju controller that is no longer there.
#
# Why this exists (2026-08-12): repair-controller.sh only knows how to repair the *k8s*
# controllers — it deletes controller-0 in the controller namespace and waits for the pod
# to come back. The LXD controllers are containers, and the failure actually observed was
# not a wedged controller but a missing one: after the 2026-08-05 ENOSPC event both
# concierge-lxd and concierge-lxd-4 were gone from LXD's instance table entirely, with
# only their orphaned profiles and storage volumes left behind. No restart fixes that.
#
# Nothing noticed for six days, because reviews 63-74 were all k8s charms. The first
# machine charm after the event (idx 75, cos-proxy, 08-11 20:00) then found no substrate,
# and every slot from there skipped — see defer_charm in run-review.sh for the other half
# of this fix.
#
# Only ever called from run-review.sh's substrate guard, which holds the lock and has
# already waited SUBSTRATE_WAIT_MAX for the controller to answer on its own.
#
#   repair-lxd-controller.sh <controller-name>
. /home/ubuntu/charm-review/bin/lib.sh
set -u

CTL="${1:-$CTL_LXD4}"
COOLDOWN=${LXD_REPAIR_COOLDOWN:-43200}   # 12h — a bootstrap costs ~5min and a whole slot
STAMP="$ROOT/state/repair-$CTL.stamp"

case "$CTL" in
  "$CTL_LXD3") CLIENT=juju_3 ;;   # 3.6 controller needs the 3.6 client to bootstrap
  "$CTL_LXD4") CLIENT=juju ;;
  *) log "repair-lxd: $CTL is not an LXD controller, refusing"; exit 1 ;;
esac

now=$(date +%s)
last=$(cat "$STAMP" 2>/dev/null || echo 0)
if [ $(( now - last )) -lt "$COOLDOWN" ]; then
  log "repair-lxd: $CTL was rebuilt $(( (now-last)/3600 ))h ago, leaving it alone"
  exit 0
fi

# Bootstrapping into a sick LXD would burn a slot and leave more debris than it cleared,
# so establish that the substrate underneath is actually healthy first. These are the
# three things the bootstrap needs: a responding daemon, the bridge, and a default profile
# with a root disk. If LXD itself is the problem this is not the tool for it.
if ! timeout 60 lxc list >/dev/null 2>&1; then
  log "repair-lxd: LXD daemon is not answering — not attempting a bootstrap"
  exit 1
fi
if ! timeout 30 lxc profile show default 2>/dev/null | grep -q 'pool:'; then
  log "repair-lxd: LXD default profile has no root disk — not attempting a bootstrap"
  exit 1
fi
if ! ip -4 addr show lxdbr0 2>/dev/null | grep -q inet; then
  log "repair-lxd: lxdbr0 has no address — not attempting a bootstrap"
  exit 1
fi

# Take the stamp *before* the attempt, not after. A bootstrap that hangs and gets timed
# out must still count as an attempt, or every subsequent slot retries it and the cooldown
# protects nothing — the same shape of bug as the guards that only halted.
echo "$now" > "$STAMP"

# A registered-but-absent controller blocks `bootstrap` on the name being in use, and the
# local record is worthless once the container is gone. Dropping it only touches this
# client's controllers.yaml.
if $CLIENT controllers --format json 2>/dev/null | grep -q "\"$CTL\""; then
  log "repair-lxd: dropping the stale local record for $CTL"
  $CLIENT unregister "$CTL" --no-prompt >/dev/null 2>&1 || true
fi

log "repair-lxd: bootstrapping $CTL with $CLIENT (this takes ~5min)"
if ! timeout "${LXD_BOOTSTRAP_TIMEOUT:-1800}" \
       $CLIENT bootstrap localhost "$CTL" >>"$ROOT/logs/_bootstrap-$CTL.log" 2>&1; then
  log "repair-lxd: WARNING bootstrap of $CTL failed — see logs/_bootstrap-$CTL.log"
  exit 1
fi

# Verify the way the caller will: controller_ready() uses this exact call, so a bootstrap
# that "succeeded" but does not answer it is still a failure here.
if timeout 60 juju status -m "$CTL:controller" >/dev/null 2>&1; then
  log "repair-lxd: $CTL is back and answering"
  exit 0
fi
log "repair-lxd: WARNING $CTL bootstrapped but does not answer juju status"
exit 1
