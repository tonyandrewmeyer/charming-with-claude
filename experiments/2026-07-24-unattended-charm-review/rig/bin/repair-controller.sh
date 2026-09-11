#!/bin/bash
# Restart a k8s juju controller whose model workers are crash-looping.
#
# Why this exists (2026-07-25): force-destroying a k8s model on juju 4.0.5
# sometimes tears down the model's modeloperator before its units are removed.
# The model can then never finish destroying, because the agents that would
# report the removal are already gone. That would be survivable on its own —
# except the dying model's dependency engine keeps trying to start
# valid-credential-flag / migration-master / migration-inactive-flag, each of
# which fails instantly with "watcher registry closed", about 60 times an hour
# per wedged model, for ever. Three wedged models were costing ~180 restarts an
# hour. Left alone over a two-week programme that compounds until the controller
# is unusable.
#
# Restarting the controller pod clears the wedged in-memory engines and lets the
# undertaker finish the models off. Only ever called from run-review.sh's
# pre-flight, where we hold the lock and nothing is deployed.
#
#   repair-controller.sh <controller-name>
. /home/ubuntu/charm-review/bin/lib.sh
set -u

CTL="${1:-$CTL_K8S4}"
NS="controller-$CTL"
COOLDOWN=${REPAIR_COOLDOWN:-21600}   # 6h — a restart is cheap but not free
STAMP="$ROOT/state/repair-$CTL.stamp"

now=$(date +%s)
last=$(cat "$STAMP" 2>/dev/null || echo 0)
if [ $(( now - last )) -lt "$COOLDOWN" ]; then
  log "repair: $CTL was repaired $(( (now-last)/60 ))m ago, leaving it alone"
  exit 0
fi

if ! kubectl get ns "$NS" >/dev/null 2>&1; then
  log "repair: no namespace $NS, nothing to repair"
  exit 0
fi

log "repair: restarting $CTL controller pod to clear wedged model workers"
echo "$now" > "$STAMP"
kubectl -n "$NS" delete pod controller-0 --wait=false >/dev/null 2>&1

# Wait for it to come back. If it does not, say so loudly — every k8s review
# after this point depends on it.
for _ in $(seq 1 60); do
  sleep 10
  if kubectl -n "$NS" get pod controller-0 \
       -o jsonpath='{.status.containerStatuses[*].ready}' 2>/dev/null | grep -qv false; then
    if timeout 60 juju models -c "$CTL" >/dev/null 2>&1; then
      log "repair: $CTL is back and answering"
      exit 0
    fi
  fi
done

log "repair: WARNING $CTL did not come back within 10 minutes"
exit 1
