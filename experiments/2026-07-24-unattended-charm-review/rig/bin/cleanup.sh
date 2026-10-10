#!/bin/bash
# Return the machine to a clean baseline. Safe to run before and after every
# review, and by hand. Only touches things this harness creates:
#   * juju models named rv-*
#   * kubernetes namespaces named rv-* that no juju model claims any more
#   * charmcraft build containers
#   * the per-run workspace
# plus generic cache pruning that costs nothing to redo.
. /home/ubuntu/charm-review/bin/lib.sh

WORKSPACE="${1:-}"

log "cleanup: start"

# Model teardown is fire-and-forget: `juju destroy-model` waits for the model to
# actually go however you ask it not to, and never returns at all for a model
# whose undertaker has died. Blocking on it cost ~40min of a 3h slot before this
# was split out. reap-models.py issues the destroys detached and rips out the
# namespace of anything that has clearly wedged. See its docstring.
#
# Since 2026-08-27 it also sweeps the other way round — cluster namespaces minus
# what juju knows — because everything above enumerates juju *models*, so a
# namespace whose model has already gone was invisible to cleanup whatever it was
# called. That sweep is the only thing here that deletes something juju never told
# us about, so it abstains unless both k8s controllers and kubectl have answered;
# its guards are documented on sweep_orphans().
timeout 300 python3 "$ROOT/bin/reap-models.py" 2>&1 | while IFS= read -r line; do
  log "cleanup: $line"
done

# charmcraft and rockcraft leave build containers behind when they are killed mid-pack,
# and they are 1.3-2.8G each.
#
# These live in their own LXD *projects* (`charmcraft`, `rockcraft`), and a bare
# `lxc list` only ever shows the `default` project — so the original version of this loop
# matched nothing and had never deleted a single one. They were accumulating at ~5G a day,
# which would have filled the disk around the middle of the programme.
#
# Two things are deliberately spared:
#   * `base-instance-*` — the cached buildd base each tool clones from. Reusable, and
#     rebuilding it costs minutes on the next pack. Same reasoning as the LXD images below.
#   * anything created before EPOCH — this box had the operator's own charmcraft work on it
#     before the harness existed, and that is not ours to delete. (Those were cleared by
#     hand on 2026-07-25 at the operator's request, so EPOCH currently spares nothing; it
#     stays as a floor in case older work reappears.)
#   * anything named in state/keep-containers, one name per line. Use that if you do your
#     own charmcraft work while the harness is running — otherwise this loop will delete
#     your build container within the hour. Killed-mid-pack leftovers are often still
#     RUNNING, so "skip running instances" is not a safe substitute for this list.
EPOCH=$(cat "$ROOT/state/epoch" 2>/dev/null || echo 0)
KEEP_LIST="$ROOT/state/keep-containers"
for proj in charmcraft rockcraft; do
  sudo -n lxc list --project "$proj" --format csv -c n 2>/dev/null | while read -r c; do
    [ -z "$c" ] && continue
    case "$c" in base-instance-*) continue ;; esac
    grep -qxF "$c" "$KEEP_LIST" 2>/dev/null && continue
    born=$(sudo -n lxc info "$c" --project "$proj" 2>/dev/null |
           awk -F': ' '/Created/{print $2}' | xargs -I{} date -d "{}" +%s 2>/dev/null)
    [ -z "$born" ] && continue
    [ "$born" -lt "$EPOCH" ] && continue     # predates the harness — leave it alone
    log "cleanup: deleting build container $proj:$c"
    sudo -n lxc delete "$c" --project "$proj" --force 2>/dev/null
  done
done

# k8s: drop workload images that no running pod references any more. Keep the
# cluster's own images (cilium, coredns, metrics-server, juju controller) — those
# get pulled straight back and cost minutes each time.
CTR=/snap/k8s/current/bin/ctr
if [ -x "$CTR" ]; then
  KEEP=$(kubectl get pods -A -o jsonpath='{range .items[*]}{range .status.containerStatuses[*]}{.image}{"\n"}{end}{end}' 2>/dev/null | sort -u)
  sudo -n "$CTR" --address /run/containerd/containerd.sock -n k8s.io images ls -q 2>/dev/null |
    grep -vE '@sha256:' | while read -r img; do
      case "$img" in
        *cilium*|*coredns*|*metrics-server*|*rawfile*|*metallb*|*pause*|*jujusolutions*|*juju*) continue ;;
      esac
      echo "$KEEP" | grep -qxF "$img" && continue
      sudo -n "$CTR" --address /run/containerd/containerd.sock -n k8s.io images rm "$img" >/dev/null 2>&1 &&
        log "cleanup: removed image $img"
    done
  sudo -n "$CTR" --address /run/containerd/containerd.sock -n k8s.io content prune references >/dev/null 2>&1
fi

# LXD base images are deliberately NOT pruned: juju and charmcraft reuse the same
# handful of ubuntu images on every run, and re-downloading them costs more time
# than the ~2G they occupy.

rm -rf /home/ubuntu/.cache/charmcraft/* 2>/dev/null
rm -rf /home/ubuntu/.local/state/charmcraft/log/* 2>/dev/null
[ -n "$WORKSPACE" ] && [ -d "$WORKSPACE" ] && rm -rf "$WORKSPACE"
rm -rf "$ROOT"/work/* 2>/dev/null

sudo -n journalctl --vacuum-size=200M >/dev/null 2>&1

# The juju controllers' k8s volumes are sparse files behind a loopback ext4. Deleting
# data inside them (juju pruning its own logs) never shrinks the backing file, so they
# ratchet upward for ever. The k8s-4 controller reached 8.7G of backing file for 877M of
# live data — 7.9G of pure ratchet, driven by the log volume from the wedged-model worker
# churn. fstrim punches those freed blocks back out of the sparse file; it reclaimed
# 7.7G the first time it was run and costs about a second.
sudo -n sh -c 'findmnt -rno TARGET | grep "kubernetes.io~csi" | while read -r m; do fstrim "$m"; done' >/dev/null 2>&1

log "cleanup: done — disk $(df -h / | awk 'NR==2{print $4}') free, mem $(free -g | awk 'NR==2{print $7}')G available"
# Per-component sizes, so disk growth is attributable from the log rather than guessed at.
log "cleanup: usage — containerd $(sudo -n du -sm /var/lib/containerd 2>/dev/null | awk '{printf "%.1fG",$1/1024}') lxd $(sudo -n du -sm /var/snap/lxd/common/lxd 2>/dev/null | awk '{printf "%.1fG",$1/1024}') k8s-volumes $(sudo -n du -sm /var/snap/k8s/common/rawfile-storage 2>/dev/null | awk '{printf "%.1fG",$1/1024}')"
