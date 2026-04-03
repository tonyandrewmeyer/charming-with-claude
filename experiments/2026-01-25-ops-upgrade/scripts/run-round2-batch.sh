#!/usr/bin/env bash
#
# Round 2 batch runner — all remaining evaluation runs.
#
# Usage:
#   ./scripts/run-round2-batch.sh [--batch N]
#
# Runs are grouped into batches so you can stop and resume between them.
# Use --batch N to start from batch N (default: 1).
#
# Each run uses ~1 Copilot premium request. Budget: ~58 runs total.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
RUN="${SCRIPT_DIR}/run-evaluation.sh"

START_BATCH="${1:-1}"
if [[ "$START_BATCH" == "--batch" ]]; then
    START_BATCH="${2:-1}"
fi

run() {
    local charm="$1" feature="$2" condition="$3" timeout="${4:-}"
    echo ""
    echo "━━━ ${charm}__${feature}__${condition} ━━━"
    if [[ -n "${timeout}" ]]; then
        TIMEOUT_MINUTES="${timeout}" "${RUN}" "${charm}" "${feature}" "${condition}"
    else
        "${RUN}" "${charm}" "${feature}" "${condition}"
    fi
}

# ============================================================
# BATCH 1: Re-runs — TIMEOUT (ops-tracing on tempo + traefik)
#   8 runs, 25 min timeout each
# ============================================================
if [[ ${START_BATCH} -le 1 ]]; then
    echo "═══════════════════════════════════════════"
    echo "  BATCH 1: Re-run timeouts (8 runs, 25min)"
    echo "═══════════════════════════════════════════"
    run tempo-k8s-operator    ops-tracing C1pf 25
    run tempo-k8s-operator    ops-tracing C2   25
    run tempo-k8s-operator    ops-tracing C3   25
    run tempo-k8s-operator    ops-tracing C4   25
    run traefik-k8s-operator  ops-tracing C1pf 25
    run traefik-k8s-operator  ops-tracing C2   25
    run traefik-k8s-operator  ops-tracing C3   25
    run traefik-k8s-operator  ops-tracing C4   25
    echo ""
    echo "✓ Batch 1 complete"
fi

# ============================================================
# BATCH 2: Re-runs — EXITED_1 (all-features on alertmanager + discourse)
#   + incomplete discourse pebble-check-events
#   5 runs
# ============================================================
if [[ ${START_BATCH} -le 2 ]]; then
    echo "═══════════════════════════════════════════"
    echo "  BATCH 2: Re-run failures (5 runs)"
    echo "═══════════════════════════════════════════"
    run alertmanager-k8s-operator  all C1s
    run alertmanager-k8s-operator  all C4
    run discourse-k8s-operator     all C1s
    run discourse-k8s-operator     all C4
    run discourse-k8s-operator     pebble-check-events C1pf
    echo ""
    echo "✓ Batch 2 complete"
fi

# ============================================================
# BATCH 3: pebble-check-events — remaining runs
#   15 runs (discourse C2/C3/C4, indico ×4, wordpress ×4, content-cache ×4)
# ============================================================
if [[ ${START_BATCH} -le 3 ]]; then
    echo "═══════════════════════════════════════════"
    echo "  BATCH 3: pebble-check-events (15 runs)"
    echo "═══════════════════════════════════════════"
    run discourse-k8s-operator      pebble-check-events C2
    run discourse-k8s-operator      pebble-check-events C3
    run discourse-k8s-operator      pebble-check-events C4
    run indico-operator             pebble-check-events C1pf
    run indico-operator             pebble-check-events C2
    run indico-operator             pebble-check-events C3
    run indico-operator             pebble-check-events C4
    run wordpress-k8s-operator      pebble-check-events C1pf
    run wordpress-k8s-operator      pebble-check-events C2
    run wordpress-k8s-operator      pebble-check-events C3
    run wordpress-k8s-operator      pebble-check-events C4
    run content-cache-k8s-operator  pebble-check-events C1pf
    run content-cache-k8s-operator  pebble-check-events C2
    run content-cache-k8s-operator  pebble-check-events C3
    run content-cache-k8s-operator  pebble-check-events C4
    echo ""
    echo "✓ Batch 3 complete"
fi

# ============================================================
# BATCH 4: set-ports — all runs
#   12 runs (alertmanager ×4, grafana ×4, zinc ×4)
# ============================================================
if [[ ${START_BATCH} -le 4 ]]; then
    echo "═══════════════════════════════════════════"
    echo "  BATCH 4: set-ports (12 runs)"
    echo "═══════════════════════════════════════════"
    run alertmanager-k8s-operator  set-ports C1pf
    run alertmanager-k8s-operator  set-ports C2
    run alertmanager-k8s-operator  set-ports C3
    run alertmanager-k8s-operator  set-ports C4
    run grafana-k8s-operator       set-ports C1pf
    run grafana-k8s-operator       set-ports C2
    run grafana-k8s-operator       set-ports C3
    run grafana-k8s-operator       set-ports C4
    run zinc-k8s-operator          set-ports C1pf
    run zinc-k8s-operator          set-ports C2
    run zinc-k8s-operator          set-ports C3
    run zinc-k8s-operator          set-ports C4
    echo ""
    echo "✓ Batch 4 complete"
fi

# ============================================================
# BATCH 5: action-testing + ops-testing-migration (secondary/exploratory)
#   8 runs
# ============================================================
if [[ ${START_BATCH} -le 5 ]]; then
    echo "═══════════════════════════════════════════"
    echo "  BATCH 5: action-testing + ops-testing-migration (8 runs)"
    echo "═══════════════════════════════════════════"
    run indico-operator             action-testing C1pf
    run indico-operator             action-testing C2
    run wordpress-k8s-operator      action-testing C1pf
    run wordpress-k8s-operator      action-testing C2
    run wordpress-k8s-operator      ops-testing-migration C1pf
    run wordpress-k8s-operator      ops-testing-migration C2
    run content-cache-k8s-operator  ops-testing-migration C1pf
    run content-cache-k8s-operator  ops-testing-migration C2
    echo ""
    echo "✓ Batch 5 complete"
fi

# ============================================================
# BATCH 6: C1s + C4 (all-features) — remaining runs
#   9 runs
# ============================================================
if [[ ${START_BATCH} -le 6 ]]; then
    echo "═══════════════════════════════════════════"
    echo "  BATCH 6: all-features C1s + C4 (9 runs)"
    echo "═══════════════════════════════════════════"
    run wordpress-k8s-operator      all C1s
    run content-cache-k8s-operator  all C1s
    run loki-k8s-operator           all C4
    run traefik-k8s-operator        all C4
    run grafana-k8s-operator        all C4
    run tempo-k8s-operator          all C4
    run wordpress-k8s-operator      all C4
    run content-cache-k8s-operator  all C4
    run zinc-k8s-operator           all C4
    echo ""
    echo "✓ Batch 6 complete"
fi

echo ""
echo "═══════════════════════════════════════════"
echo "  ALL BATCHES COMPLETE"
echo "═══════════════════════════════════════════"
