#!/usr/bin/env bash
#
# Generate the full run schedule for round 2.
#
# Usage:
#   ./scripts/run-all.sh          # Print the schedule (dry run)
#   ./scripts/run-all.sh --run    # Execute all runs sequentially
#
# Sequencing: feature-first, then charm-by-charm within each feature.
# This makes scoring easier — you compare across conditions while the
# feature is fresh.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
RUN_SCRIPT="${SCRIPT_DIR}/run-evaluation.sh"

MODE="${1:-}"

run_or_print() {
    local charm="$1" feature="$2" condition="$3"
    if [[ "${MODE}" == "--run" ]]; then
        "${RUN_SCRIPT}" "${charm}" "${feature}" "${condition}"
        echo ""
        echo "---"
        echo ""
    else
        echo "  ${charm}  ${feature}  ${condition}"
    fi
}

echo "=== ROUND 2 RUN SCHEDULE ==="
echo "=== 67 runs total ==="
echo ""

# -------------------------------------------------------
# Phase 1: Primary features (C1pf, C2, C3, C4 per charm)
# -------------------------------------------------------

echo "--- Phase 1: ops-tracing (16 runs) ---"
for charm in alertmanager-k8s-operator loki-k8s-operator traefik-k8s-operator tempo-k8s-operator; do
    for cond in C1pf C2 C3 C4; do
        run_or_print "${charm}" "ops-tracing" "${cond}"
    done
done
echo ""

echo "--- Phase 2: pebble-check-events (16 runs) ---"
for charm in discourse-k8s-operator indico-operator wordpress-k8s-operator content-cache-k8s-operator; do
    for cond in C1pf C2 C3 C4; do
        run_or_print "${charm}" "pebble-check-events" "${cond}"
    done
done
echo ""

echo "--- Phase 3: set-ports (12 runs) ---"
for charm in alertmanager-k8s-operator grafana-k8s-operator zinc-k8s-operator; do
    for cond in C1pf C2 C3 C4; do
        run_or_print "${charm}" "set-ports" "${cond}"
    done
done
echo ""

# -------------------------------------------------------
# Phase 2: Secondary features (C1pf, C2 only)
# -------------------------------------------------------

echo "--- Phase 4: action-testing (4 runs) ---"
for charm in indico-operator wordpress-k8s-operator; do
    for cond in C1pf C2; do
        run_or_print "${charm}" "action-testing" "${cond}"
    done
done
echo ""

# -------------------------------------------------------
# Phase 3: Exploratory (C1pf, C2 only)
# -------------------------------------------------------

echo "--- Phase 5: ops-testing-migration (4 runs) ---"
for charm in wordpress-k8s-operator content-cache-k8s-operator; do
    for cond in C1pf C2; do
        run_or_print "${charm}" "ops-testing-migration" "${cond}"
    done
done
echo ""

# -------------------------------------------------------
# Phase 4: All-features runs
# -------------------------------------------------------

echo "--- Phase 6: C1s single upgrade skill (5 runs) ---"
for charm in alertmanager-k8s-operator discourse-k8s-operator indico-operator wordpress-k8s-operator content-cache-k8s-operator; do
    run_or_print "${charm}" "all" "C1s"
done
echo ""

echo "--- Phase 7: C4 generic prompt (10 runs) ---"
for charm in discourse-k8s-operator alertmanager-k8s-operator loki-k8s-operator indico-operator traefik-k8s-operator grafana-k8s-operator tempo-k8s-operator wordpress-k8s-operator content-cache-k8s-operator zinc-k8s-operator; do
    run_or_print "${charm}" "all" "C4"
done
echo ""

echo "=== END ==="
