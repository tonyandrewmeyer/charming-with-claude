#!/usr/bin/env bash
#
# Round 2 evaluation runner for the ops-upgrade experiment.
#
# Usage:
#   ./scripts/run-evaluation.sh <charm> <feature> <condition>
#
# Example:
#   ./scripts/run-evaluation.sh alertmanager-k8s-operator set-ports C1pf
#
# This script:
#   1. Clones the charm at the pinned commit into a temp directory
#   2. Installs the skill (for C1pf/C1s conditions)
#   3. Generates the appropriate prompt
#   4. Runs GitHub Copilot CLI in non-interactive mode
#   5. Captures output to results/<charm>__<feature>__<condition>/
#
# Prerequisites:
#   - gh copilot extension installed
#   - jq installed
#   - Local charm clones available at ~/charm-clones/

set -euo pipefail

EXPERIMENT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
RESULTS_DIR="${EXPERIMENT_DIR}/results"
SKILLS_DIR="${EXPERIMENT_DIR}/skills"
METADATA="${RESULTS_DIR}/experiment-metadata.json"
CLONE_BASE="${HOME}/charm-clones"
WORKDIR="/tmp/ops-upgrade-experiment"

# Copilot settings
MAX_CONTINUES=25
TIMEOUT_MINUTES=15

# --- Argument parsing ---

if [[ $# -lt 3 ]]; then
    echo "Usage: $0 <charm> <feature> <condition>"
    echo ""
    echo "Charms:  discourse-k8s-operator, alertmanager-k8s-operator, loki-k8s-operator,"
    echo "         indico-operator, traefik-k8s-operator, grafana-k8s-operator,"
    echo "         tempo-k8s-operator, wordpress-k8s-operator, content-cache-k8s-operator,"
    echo "         zinc-k8s-operator"
    echo ""
    echo "Features: set-ports, ops-tracing, pebble-check-events, action-testing,"
    echo "          ops-testing-migration, all"
    echo ""
    echo "Conditions: C1pf, C2, C3, C1s, C4"
    exit 1
fi

CHARM="$1"
FEATURE="$2"
CONDITION="$3"

RUN_NAME="${CHARM}__${FEATURE}__${CONDITION}"
RUN_DIR="${RESULTS_DIR}/${RUN_NAME}"

# --- Helpers ---

get_commit() {
    jq -r ".round_2.charms[\"${CHARM}\"]" "${METADATA}"
}

get_exemplar_charm() {
    local feature="$1"
    # Return the first exemplar for the feature
    case "${feature}" in
        set-ports)
            echo "catalogue-k8s-operator"
            ;;
        ops-tracing)
            echo "sdcore-amf-operator"
            ;;
        pebble-check-events)
            echo "kratos-operator"
            ;;
        *)
            echo ""
            ;;
    esac
}

feature_description() {
    local feature="$1"
    case "${feature}" in
        set-ports)
            echo "ops 2.7.0 added a declarative Unit.set_ports() API that replaces the imperative open_port()/close_port() pattern. Instead of tracking which ports to open and close individually, charms declare the full set of desired ports and ops handles the diff."
            ;;
        ops-tracing)
            echo "ops 2.21.0 introduced ops[tracing] as the first-party charm tracing library, replacing the community charm_tracing / charms.tempo_k8s.v2.tracing library approach. Charms can now add OpenTelemetry tracing with pip install ops[tracing] and a single ops.tracing.setup() or ops.tracing.Tracing() call."
            ;;
        pebble-check-events)
            echo "ops 2.15.0 added pebble-check-failed and pebble-check-recovered events that allow K8s charms to react when Pebble health checks fail or recover, replacing manual check polling patterns."
            ;;
        action-testing)
            echo "ops 2.9.0 introduced Harness.run_action() which returns an ActionOutput object (or raises ActionFailed), replacing the older pattern of manually triggering action events and inspecting results via the backend."
            ;;
        ops-testing-migration)
            echo "ops 2.17.0 introduced ops[testing] extras, exposing Scenario-based testing as ops.testing. This provides a declarative, state-transition-based testing model to replace the deprecated Harness."
            ;;
    esac
}

exemplar_url() {
    local feature="$1"
    case "${feature}" in
        set-ports)
            echo "https://github.com/canonical/catalogue-k8s-operator"
            ;;
        ops-tracing)
            echo "https://github.com/canonical/sdcore-amf-operator"
            ;;
        pebble-check-events)
            echo "https://github.com/canonical/kratos-operator"
            ;;
        *)
            echo ""
            ;;
    esac
}

generate_prompt() {
    local feature="$1"
    local condition="$2"
    local desc
    desc="$(feature_description "${feature}")"

    case "${condition}" in
        C1pf)
            echo "This charm could benefit from ${feature}. There is a skill available for applying this change."
            ;;
        C2)
            echo "${desc} Learn how to use that feature and update this charm to make use of it."
            ;;
        C3)
            local url
            url="$(exemplar_url "${feature}")"
            if [[ -z "${url}" ]]; then
                echo "ERROR: No exemplar available for ${feature}" >&2
                exit 1
            fi
            echo "${desc} The charm at ${url} already uses this feature -- look at how they did it and update this charm similarly."
            ;;
        C1s)
            echo "Upgrade this charm's ops usage. There is a skill available for this."
            ;;
        C4)
            echo "There is a new ops (and ops-tracing, and ops-scenario) release. Carefully read the release notes and analyse how each change (feature, bug fix, deprecation, etc.) impacts this charm. Prepare a branch that upgrades to the new ops version, making use of new features wherever sensible and addressing any other items that arise from your analysis."
            ;;
    esac
}

# --- Pre-flight checks ---

COMMIT="$(get_commit)"
if [[ "${COMMIT}" == "null" || -z "${COMMIT}" ]]; then
    echo "ERROR: No pinned commit for ${CHARM} in experiment-metadata.json" >&2
    exit 1
fi

if [[ -d "${RUN_DIR}" ]]; then
    echo "WARNING: ${RUN_DIR} already exists. Skipping."
    echo "  Delete it to re-run: rm -rf ${RUN_DIR}"
    exit 0
fi

# --- Setup workspace ---

echo "=== ${RUN_NAME} ==="
echo "Charm:     ${CHARM} @ ${COMMIT}"
echo "Feature:   ${FEATURE}"
echo "Condition: ${CONDITION}"
echo ""

WORKSPACE="${WORKDIR}/${RUN_NAME}"
rm -rf "${WORKSPACE}"

# Use local clone if available (cp is faster and avoids network),
# otherwise fall back to GitHub.
if [[ -d "${CLONE_BASE}/${CHARM}/.git" ]]; then
    echo "Copying from local clone: ${CLONE_BASE}/${CHARM}"
    cp -a "${CLONE_BASE}/${CHARM}" "${WORKSPACE}.tmp"
    mv "${WORKSPACE}.tmp" "${WORKSPACE}"
elif [[ -d "${CLONE_BASE}/${CHARM}" ]]; then
    # Bare repo or similar — clone from it
    echo "Cloning from local: ${CLONE_BASE}/${CHARM}"
    git clone --quiet "${CLONE_BASE}/${CHARM}" "${WORKSPACE}"
else
    echo "Local clone not found; cloning from GitHub: canonical/${CHARM}"
    git clone --quiet "https://github.com/canonical/${CHARM}.git" "${WORKSPACE}"
fi

cd "${WORKSPACE}"
git checkout --quiet "${COMMIT}"
# Clean any local modifications from the clone
git reset --hard --quiet "${COMMIT}"
git clean -fdx --quiet
echo "Checked out ${COMMIT}"

# --- Install skill (C1pf or C1s) ---

if [[ "${CONDITION}" == "C1pf" ]]; then
    # Map feature names to skill directory names where they differ
    SKILL_NAME="${FEATURE}"
    case "${FEATURE}" in
        ops-tracing) SKILL_NAME="ops-tracing-adoption" ;;
    esac
    SKILL_SOURCE="${SKILLS_DIR}/${SKILL_NAME}/SKILL.md"
    if [[ ! -f "${SKILL_SOURCE}" ]]; then
        echo "ERROR: Skill not found: ${SKILL_SOURCE}" >&2
        exit 1
    fi
    # For Copilot, the skill goes into .github/copilot-instructions.md
    # (Copilot reads this file as system instructions)
    mkdir -p "${WORKSPACE}/.github"
    cp "${SKILL_SOURCE}" "${WORKSPACE}/.github/copilot-instructions.md"
    echo "Installed per-feature skill: ${FEATURE}"
elif [[ "${CONDITION}" == "C1s" ]]; then
    SKILL_SOURCE="${SKILLS_DIR}/ops-upgrade/SKILL.md"
    mkdir -p "${WORKSPACE}/.github"
    cp "${SKILL_SOURCE}" "${WORKSPACE}/.github/copilot-instructions.md"
    echo "Installed single upgrade skill"
fi

# --- Generate and save prompt ---

mkdir -p "${RUN_DIR}"
PROMPT="$(generate_prompt "${FEATURE}" "${CONDITION}")"
echo "${PROMPT}" > "${RUN_DIR}/prompt.txt"
echo "Prompt: ${PROMPT}"
echo ""

# --- Run Copilot ---

TRANSCRIPT="${RUN_DIR}/transcript.md"

echo "Starting Copilot CLI (max ${MAX_CONTINUES} continues, ${TIMEOUT_MINUTES}min timeout)..."
echo "  Workspace: ${WORKSPACE}"
echo "  Skill installed: $([ -f "${WORKSPACE}/.github/copilot-instructions.md" ] && echo 'yes' || echo 'no')"
echo ""

START_TIME=$(date +%s)

# Run Copilot in non-interactive mode with autopilot continuation.
# --allow-all-tools: no permission prompts (required for non-interactive)
# --autopilot: auto-continue when Copilot wants to keep going
# --max-autopilot-continues: cap to prevent runaway loops
# --share: save transcript to markdown file
# --model: use claude-sonnet-4.6 (same as round 1)
COPILOT_EXIT=0
timeout "${TIMEOUT_MINUTES}m" \
    copilot \
        -p "${PROMPT}" \
        --allow-all-tools \
        --autopilot \
        --max-autopilot-continues "${MAX_CONTINUES}" \
        --model claude-sonnet-4.6 \
        --share "${TRANSCRIPT}" \
    > "${RUN_DIR}/output.txt" 2>&1 \
    || COPILOT_EXIT=$?

END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))
echo "${DURATION}" > "${RUN_DIR}/duration_seconds.txt"

# Record status
if [[ ${COPILOT_EXIT} -eq 0 ]]; then
    echo "COMPLETED" > "${RUN_DIR}/status.txt"
elif [[ ${COPILOT_EXIT} -eq 124 ]]; then
    echo "TIMEOUT" > "${RUN_DIR}/status.txt"
else
    echo "EXIT_CODE_${COPILOT_EXIT}" > "${RUN_DIR}/status.txt"
fi

echo "Copilot finished (exit ${COPILOT_EXIT}, ${DURATION}s)"
echo "Status: $(cat "${RUN_DIR}/status.txt")"

# --- Capture results ---

cd "${WORKSPACE}"

# Diff (compare against pinned commit — Copilot may have committed its changes)
git diff "${COMMIT}"..HEAD > "${RUN_DIR}/diff.patch"
git diff "${COMMIT}"..HEAD --stat > "${RUN_DIR}/diff-stat.txt"

additions=$(git diff "${COMMIT}"..HEAD --numstat | awk '{s+=$1} END {print s+0}')
deletions=$(git diff "${COMMIT}"..HEAD --numstat | awk '{s+=$2} END {print s+0}')
echo "+${additions} -${deletions}" > "${RUN_DIR}/diff-size.txt"

# Changed files
git diff "${COMMIT}"..HEAD --name-only > "${RUN_DIR}/changed-files.txt"

# Mark complete
touch "${RUN_DIR}/completed"

echo ""
echo "Results captured to ${RUN_DIR}"
echo "  Diff: +${additions} -${deletions}"
echo "  Files changed: $(wc -l < "${RUN_DIR}/changed-files.txt")"
echo "  Duration: ${DURATION}s"
echo "  Transcript: ${TRANSCRIPT}"
