#!/usr/bin/env bash
#
# Capture results from a completed Copilot run.
#
# Usage:
#   cd /tmp/ops-upgrade-experiment/<run-name>
#   ./scripts/capture-results.sh <results-dir>
#
# Or source it:
#   source scripts/capture-results.sh /path/to/results/run-dir

set -euo pipefail

RUN_DIR="${1:?Usage: capture-results.sh <results-dir>}"
mkdir -p "${RUN_DIR}"

# Diff
git diff > "${RUN_DIR}/diff.patch"
git diff --stat > "${RUN_DIR}/diff-stat.txt"

additions=$(git diff --numstat | awk '{s+=$1} END {print s+0}')
deletions=$(git diff --numstat | awk '{s+=$2} END {print s+0}')
echo "+${additions} -${deletions}" > "${RUN_DIR}/diff-size.txt"

# Changed files
git diff --name-only > "${RUN_DIR}/changed-files.txt"

# Mark complete
touch "${RUN_DIR}/completed"

echo "Results captured to ${RUN_DIR}"
echo "  Diff: +${additions} -${deletions}"
echo "  Files changed: $(wc -l < "${RUN_DIR}/changed-files.txt")"
echo ""
echo "Remaining manual steps:"
echo "  1. Copy the Copilot transcript to ${RUN_DIR}/transcript.md"
echo "  2. Copy the Copilot output summary to ${RUN_DIR}/output.txt"
echo "  3. Record the run status in ${RUN_DIR}/status.txt"
echo "     (COMPLETED, API_ERROR_AFTER_COMPLETION, TIMEOUT, LOOP, etc.)"
