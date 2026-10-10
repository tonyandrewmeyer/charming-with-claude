#!/bin/bash
# Bootstrap the Juju 3.6 Kubernetes controller, so the rig has 3.x and 4.x on both
# substrates. This failed on 2026-07-24 with:
#
#   ProvisioningFailed  failed to provision volume with StorageClass
#   "csi-rawfile-default": rpc error: code = ResourceExhausted
#   desc = Not enough disk space
#
# The juju controller asks for a fixed 20Gi PVC and the rawfile CSI would not carve
# it out of the 24G that was free. Run this again once the root disk has been grown.
. /home/ubuntu/charm-review/bin/lib.sh
set -u

FREE_G=$(df --output=avail -BG / | tail -1 | tr -dc '0-9')
if [ "${FREE_G:-0}" -lt 45 ]; then
  echo "only ${FREE_G}G free; the controller wants a 20Gi PVC and the rawfile CSI"
  echo "keeps a margin. Grow the root disk first — 45G+ free is comfortable."
  exit 1
fi

juju_3 bootstrap k8s "$CTL_K8S3" --config controller-service-type=cluster "$@"
juju controllers
